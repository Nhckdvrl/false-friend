#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import pandas as pd
import torch
import torch.nn.functional as F
from transformers import GPT2LMHeadModel

from false_friend_lab.io import read_jsonl
from false_friend_lab.remap import TargetLexicalRemapper, apply_causal_vocab_mask


def token_nlls(model, ids: torch.Tensor, remapper: TargetLexicalRemapper) -> torch.Tensor:
    with torch.no_grad():
        logits = model(input_ids=ids.unsqueeze(0), use_cache=False).logits[0]
    labels = ids[1:]
    masked = apply_causal_vocab_mask(logits[:-1], labels, remapper).float()
    lp = F.log_softmax(masked, dim=-1)
    nll = -lp.gather(1, labels[:, None]).squeeze(1)
    out = torch.full((ids.numel(),), float("nan"), device=ids.device)
    out[1:] = nll
    return out


def safe_mean(x: torch.Tensor) -> float:
    x = x[~torch.isnan(x)]
    return float(x.mean()) if x.numel() else float("nan")


def window(ids: List[int], pos: int, max_len: int, pre_k: int, post_k: int):
    """Return a model-sized window preserving the full primary pre/post span."""
    if pos < pre_k or len(ids) - pos - 1 < post_k:
        return None
    if len(ids) <= max_len:
        return ids, pos
    if pre_k + post_k + 1 > max_len:
        raise ValueError("pre_k + post_k + 1 exceeds model context length")
    min_start = pos + post_k + 1 - max_len
    max_start = pos - pre_k
    start = max(0, min_start)
    start = min(start, max_start)
    end = min(len(ids), start + max_len)
    if pos + post_k >= end:
        start = pos + post_k + 1 - max_len
        end = start + max_len
    wp = pos - start
    if wp < pre_k or end - (wp + start) - 1 < post_k:
        raise AssertionError("window failed to preserve full metric spans")
    return ids[start:end], wp


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--data", default="data/processed/en_de")
    p.add_argument("--post-k", type=int, default=8)
    p.add_argument("--pre-k", type=int, default=8)
    p.add_argument("--output", default=None)
    a = p.parse_args()

    ck = Path(a.checkpoint)
    d = Path(a.data)
    rm = json.load(open(ck / "run_meta.json", encoding="utf-8"))
    dm = json.load(open(d / "metadata.json", encoding="utf-8"))
    if int(dm.get("schema_version", 0)) < 3:
        raise RuntimeError("evaluation requires audited data schema v3")
    if rm["data_fingerprint"] != dm["data_fingerprint"]:
        raise RuntimeError("checkpoint/data fingerprint mismatch")

    targets = pd.read_csv(d / "targets.csv")
    tids = sorted(set(map(int, targets.compact_token_id)))
    tm = targets.set_index("word").to_dict("index")
    remap = TargetLexicalRemapper(int(dm["compact_vocab_size"]), tids, rm["condition"], "de")

    dev = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = GPT2LMHeadModel.from_pretrained(ck).to(dev).eval()
    max_len = int(model.config.n_positions)
    rows = []
    skipped_short = 0

    for r in read_jsonl(d / "contexts.jsonl"):
        base = list(map(int, r["compact_ids"]))
        target = int(r["compact_target_id"])
        positions = list(map(int, r["positions"]))
        exact = [False] * len(base)
        for pos in positions:
            if pos < 0 or pos >= len(base) or base[pos] != target:
                raise AssertionError("saved exact target position mismatch")
            exact[pos] = True
        mapped = remap.map_ids(base, r["lang"], exact)

        for occ, pos in enumerate(positions):
            pack = window(mapped, pos, max_len, a.pre_k, a.post_k)
            if pack is None:
                skipped_short += 1
                continue
            w, wp = pack
            ids = torch.tensor(w, dtype=torch.long, device=dev)
            n = token_nlls(model, ids, remap)
            ps, pe = wp + 1, wp + 1 + a.post_k
            qs, qe = wp - a.pre_k, wp
            if qs < 0 or pe > len(w):
                raise AssertionError("metric span escaped evaluation window")
            rows.append(
                {
                    "context_id": f"{r['context_id']}-occ{occ}",
                    "base_context_id": r["context_id"],
                    "word": r["word"],
                    "relation": r["relation"],
                    "lang": r["lang"],
                    "condition": rm["condition"],
                    "seed": int(rm["seed"]),
                    "schedule": rm["schedule"],
                    "step": int(rm.get("update", rm.get("step", -1))),
                    "form_nll": float(n[wp]),
                    "post_nll": safe_mean(n[ps:pe]),
                    "pre_nll": safe_mean(n[qs:qe]),
                    "n_pre": a.pre_k,
                    "n_post": a.post_k,
                    "position": pos,
                    "sentence_tokens": len(base),
                    "oov_fraction": float(r.get("oov_fraction", 0.0)),
                    "train_count_en": int(tm[r["word"]]["train_count_en"]),
                    "train_count_de": int(tm[r["word"]]["train_count_de"]),
                    "data_fingerprint": rm["data_fingerprint"],
                    "config_hash": rm["config_hash"],
                    "effective_batch_size": int(rm["effective_batch_size"]),
                    "training_gpu_name": rm["training_gpu_name"],
                    "git_commit": rm.get("git_commit", "unknown"),
                    "init_sha256": rm.get("init_sha256", "unknown"),
                    "text": r["text"],
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("evaluation produced zero full-window target occurrences")
    output = Path(a.output or ck / "eval_contexts.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    print(f"wrote {len(df)} rows to {output}; skipped_short_window={skipped_short}")


if __name__ == "__main__":
    main()
