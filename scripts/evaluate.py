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
from false_friend_lab.remap import TargetLexicalRemapper


def token_nlls(model, ids: torch.Tensor) -> torch.Tensor:
    with torch.no_grad():
        logits = model(input_ids=ids.unsqueeze(0), use_cache=False).logits[0]
    lprobs = F.log_softmax(logits[:-1].float(), dim=-1)
    labels = ids[1:]
    nll = -lprobs.gather(1, labels.unsqueeze(1)).squeeze(1)
    out = torch.full((ids.numel(),), float("nan"), device=ids.device)
    out[1:] = nll
    return out


def window_for_position(ids: List[int], pos: int, max_len: int, post_k: int) -> tuple[list[int], int]:
    if len(ids) <= max_len:
        return ids, pos
    suffix_budget = min(post_k + 8, max_len // 3)
    start = max(0, pos - (max_len - suffix_budget - 1))
    end = min(len(ids), start + max_len)
    if end - start < max_len:
        start = max(0, end - max_len)
    return ids[start:end], pos - start


def safe_mean(x: torch.Tensor) -> float:
    if x.numel() == 0:
        return float("nan")
    x = x[~torch.isnan(x)]
    return float(x.mean().item()) if x.numel() else float("nan")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--data", default="data/processed/en_de")
    p.add_argument("--post-k", type=int, default=8)
    p.add_argument("--pre-k", type=int, default=8)
    p.add_argument("--output", default=None)
    args = p.parse_args()
    ckpt = Path(args.checkpoint)
    data_dir = Path(args.data)
    run_meta = json.load(open(ckpt / "run_meta.json", "r", encoding="utf-8"))
    condition = run_meta["condition"]
    seed = int(run_meta["seed"])
    schedule = run_meta["schedule"]
    data_meta = json.load(open(data_dir / "metadata.json", "r", encoding="utf-8"))
    targets = pd.read_csv(data_dir / "targets.csv")
    target_ids = sorted(set(map(int, targets["compact_token_id"].tolist())))
    target_meta = targets.set_index("word").to_dict(orient="index")
    remapper = TargetLexicalRemapper(int(data_meta["compact_vocab_size"]), target_ids, condition, split_lang="de")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = GPT2LMHeadModel.from_pretrained(ckpt).to(device)
    model.eval()
    max_len = int(model.config.n_positions)
    rows = []
    for row in read_jsonl(data_dir / "contexts.jsonl"):
        ids_base = list(map(int, row["compact_ids"]))
        target_base = int(row["compact_target_id"])
        positions = [i for i, x in enumerate(ids_base) if x == target_base]
        for occ_idx, pos in enumerate(positions):
            if pos == 0 or pos >= len(ids_base) - 1:
                continue
            ids_mapped = remapper.map_ids(ids_base, row["lang"])
            target_mapped = remapper.map_ids([target_base], row["lang"])[0]
            if ids_mapped[pos] != target_mapped:
                raise AssertionError("target remapping mismatch")
            win, win_pos = window_for_position(ids_mapped, pos, max_len, args.post_k)
            if win_pos == 0 or win_pos >= len(win) - 1:
                continue
            ids = torch.tensor(win, dtype=torch.long, device=device)
            nlls = token_nlls(model, ids)
            post_start = win_pos + 1
            post_end = min(len(win), post_start + args.post_k)
            pre_start = max(1, win_pos - args.pre_k)
            pre_end = win_pos
            rows.append({
                "context_id": f"{row['context_id']}-occ{occ_idx}",
                "base_context_id": row["context_id"], "word": row["word"], "relation": row["relation"],
                "lang": row["lang"], "condition": condition, "seed": seed, "schedule": schedule,
                "step": int(run_meta.get("step", -1)), "form_nll": float(nlls[win_pos].item()),
                "post_nll": safe_mean(nlls[post_start:post_end]), "pre_nll": safe_mean(nlls[pre_start:pre_end]),
                "position": pos, "sentence_tokens": len(ids_base),
                "train_count_en": int(target_meta[row["word"]]["train_count_en"]),
                "train_count_de": int(target_meta[row["word"]]["train_count_de"]), "text": row["text"],
            })
    df = pd.DataFrame(rows)
    output = Path(args.output or (ckpt / "eval_contexts.csv"))
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    print(f"wrote {len(df)} context-occurrence rows to {output}")
    if len(df):
        print(df.groupby(["relation", "lang"])[["form_nll", "post_nll", "pre_nll"]].mean())


if __name__ == "__main__":
    main()
