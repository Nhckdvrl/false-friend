#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from datasets import load_dataset
from transformers import AutoTokenizer


def stable_holdout(key: str, modulo: int, bucket: int) -> bool:
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return int(h[:12], 16) % modulo == bucket


def _parse_common_word(raw: object) -> str | None:
    text = str(raw).strip()
    if not text:
        return None
    parts = [x.strip() for x in text.split(",")]
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2 and parts[0] == parts[1]:
        return parts[0]
    return None


def single_shared_token(tokenizer, word: str) -> int | None:
    a = tokenizer.encode(word, add_special_tokens=False)
    b = tokenizer.encode(" " + word, add_special_tokens=False)
    if len(a) == len(b) == 1 and int(a[0]) == int(b[0]):
        return int(a[0])
    return None


def load_stingray_targets(tokenizer_name: str) -> pd.DataFrame:
    tok = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    rows: List[dict] = []
    for config_name, relation in [("en_de", "false_friend"), ("en_de_common", "true_friend")]:
        ds = load_dataset("StingrayBench/StingrayBench", config_name, split="test", trust_remote_code=True)
        for ex in ds:
            raw_word = ex.get("word", "")
            if relation == "true_friend":
                word = _parse_common_word(raw_word)
            else:
                word = str(raw_word).strip()
                if "," in word:
                    parts = [x.strip() for x in word.split(",")]
                    word = parts[0] if len(parts) == 2 and parts[0] == parts[1] else None
            if not word:
                continue
            tid = single_shared_token(tok, word)
            if tid is None:
                continue
            rows.append({"word": word, "relation": relation, "base_token_id": tid,
                         "meaning_en": str(ex.get("meaning_l1", "")), "meaning_de": str(ex.get("meaning_l2", "")),
                         "source_config": config_name})
    targets = pd.DataFrame(rows).drop_duplicates(["relation", "word", "base_token_id"]).reset_index(drop=True)
    if targets.empty:
        raise RuntimeError("no strict single-token Stingray EN-DE targets survived")
    dup = targets[targets.duplicated("base_token_id", keep=False)]
    if len(dup):
        print("WARNING: dropping token-id collisions across lexical targets:")
        print(dup[["word", "relation", "base_token_id"]].to_string(index=False))
        bad = set(map(int, dup.base_token_id.tolist()))
        targets = targets[~targets.base_token_id.isin(bad)].reset_index(drop=True)
    return targets


def is_word_char(ch: str) -> bool:
    return bool(ch) and (ch.isalnum() or ch == "_")


def exact_target_mask(text: str, ids: List[int], offsets: List[Tuple[int, int]], target_by_id: Dict[int, str]) -> np.ndarray:
    mask = np.zeros(len(ids), dtype=np.uint8)
    for i, (tid, (s, e)) in enumerate(zip(ids, offsets)):
        word = target_by_id.get(int(tid))
        if word is None or s < 0 or e <= s:
            continue
        if text[s:e] != word:
            continue
        left_ok = s == 0 or not is_word_char(text[s - 1])
        right_ok = e == len(text) or not is_word_char(text[e])
        if left_ok and right_ok:
            mask[i] = 1
    return mask


def append_sentence(stream: List[int], masks: List[int], ids: List[int], exact_mask: np.ndarray, eos_id: int) -> None:
    stream.extend(map(int, ids)); masks.extend(map(int, exact_mask.tolist()))
    stream.append(int(eos_id)); masks.append(0)


def main() -> None:
    p = argparse.ArgumentParser(description="Prepare strict EN-DE lexical-sharing causal experiment")
    p.add_argument("--output", default="data/processed/en_de")
    p.add_argument("--tokenizer", default="xlm-roberta-base")
    p.add_argument("--max-pairs", type=int, default=1_000_000)
    p.add_argument("--min-target-occurrences", type=int, default=20)
    p.add_argument("--holdout-modulo", type=int, default=10)
    p.add_argument("--holdout-bucket", type=int, default=0)
    p.add_argument("--max-contexts-per-word-lang", type=int, default=100)
    args = p.parse_args()

    out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(args.tokenizer, use_fast=True)
    if not tok.is_fast or tok.eos_token_id is None or tok.unk_token_id is None:
        raise RuntimeError("a fast tokenizer with eos/unk ids is required")

    targets = load_stingray_targets(args.tokenizer)
    target_by_id = {int(r.base_token_id): str(r.word) for r in targets.itertuples(index=False)}
    target_meta = {int(r.base_token_id): r for r in targets.itertuples(index=False)}
    print("strict Stingray targets before corpus-frequency filter:", targets.relation.value_counts().to_dict())

    dataset = load_dataset("Helsinki-NLP/opus-100", "de-en", split="train")
    if args.max_pairs and args.max_pairs < len(dataset):
        dataset = dataset.select(range(args.max_pairs))

    streams: Dict[str, List[int]] = {"en": [], "de": []}
    masks: Dict[str, List[int]] = {"en": [], "de": []}
    used_ids = {int(tok.unk_token_id), int(tok.eos_token_id)}
    train_counts = {"en": Counter(), "de": Counter()}
    heldout_raw: List[dict] = []; context_cap = defaultdict(int); n_heldout_pairs = 0

    batch_rows = 512
    for start in range(0, len(dataset), batch_rows):
        block = dataset[start:start + batch_rows]["translation"]
        texts_en = [str(x["en"]) for x in block]; texts_de = [str(x["de"]) for x in block]
        enc_en = tok(texts_en, add_special_tokens=False, padding=False, truncation=False, return_offsets_mapping=True)
        enc_de = tok(texts_de, add_special_tokens=False, padding=False, truncation=False, return_offsets_mapping=True)
        for off in range(len(block)):
            pair_id = start + off; per_lang = {}; has_target = False
            for lang, text, enc in (("en", texts_en[off], enc_en), ("de", texts_de[off], enc_de)):
                ids = list(map(int, enc["input_ids"][off]))
                offsets = [(int(a), int(b)) for a, b in enc["offset_mapping"][off]]
                exact = exact_target_mask(text, ids, offsets, target_by_id)
                has_target = has_target or bool(exact.sum()); per_lang[lang] = (text, ids, exact)
            pair_holdout = has_target and stable_holdout(str(pair_id), args.holdout_modulo, args.holdout_bucket)
            if pair_holdout:
                n_heldout_pairs += 1
                for lang in ("en", "de"):
                    text, ids, exact = per_lang[lang]; positions = np.flatnonzero(exact)
                    if len(positions) != 1:
                        continue
                    pos = int(positions[0]); tid = int(ids[pos]); meta = target_meta[tid]; key = (str(meta.word), lang)
                    if context_cap[key] >= args.max_contexts_per_word_lang:
                        continue
                    heldout_raw.append({"context_id": f"opus-{pair_id}-{lang}-{tid}", "pair_id": pair_id,
                                        "lang": lang, "word": str(meta.word), "relation": str(meta.relation),
                                        "base_target_id": tid, "target_position": pos, "text": text,
                                        "base_ids": ids, "exact_mask": exact.astype(int).tolist()})
                    context_cap[key] += 1
                continue
            for lang in ("en", "de"):
                _, ids, exact = per_lang[lang]
                append_sentence(streams[lang], masks[lang], ids, exact, int(tok.eos_token_id)); used_ids.update(ids)
                for pos in np.flatnonzero(exact): train_counts[lang][int(ids[int(pos)])] += 1
        if start and start % 50_000 == 0: print(f"processed {start:,}/{len(dataset):,} sentence pairs")

    keep_ids = []; freq_rows = []
    for row in targets.itertuples(index=False):
        tid = int(row.base_token_id); en_n = int(train_counts["en"][tid]); de_n = int(train_counts["de"][tid])
        keep = en_n >= args.min_target_occurrences and de_n >= args.min_target_occurrences
        freq_rows.append((en_n, de_n, keep))
        if keep: keep_ids.append(tid); used_ids.add(tid)
    targets["train_count_en"] = [x[0] for x in freq_rows]; targets["train_count_de"] = [x[1] for x in freq_rows]; targets["passes_frequency_gate"] = [x[2] for x in freq_rows]
    targets = targets[targets.passes_frequency_gate].copy().reset_index(drop=True); keep_set = set(keep_ids)
    print("targets after frequency gate:", targets.relation.value_counts().to_dict())

    sorted_used = np.array(sorted(used_ids), dtype=np.int64); base_to_compact = np.full(tok.vocab_size, -1, dtype=np.int32)
    base_to_compact[sorted_used] = np.arange(len(sorted_used), dtype=np.int32); compact_to_base = sorted_used.astype(np.int32)
    unk_compact = int(base_to_compact[int(tok.unk_token_id)])
    np.save(out / "base_to_compact.npy", base_to_compact); np.save(out / "compact_to_base.npy", compact_to_base)
    for lang in ("en", "de"):
        arr = np.asarray(streams[lang], dtype=np.int64); m = np.asarray(masks[lang], dtype=np.uint8)
        if len(arr) != len(m): raise AssertionError("stream/mask length mismatch")
        compact = base_to_compact[arr]
        if np.any(compact < 0): raise AssertionError("training stream contains token missing from compact vocabulary")
        np.save(out / f"train_{lang}.npy", compact.astype(np.int32)); np.save(out / f"train_{lang}_exact_mask.npy", m)

    targets["compact_token_id"] = targets.base_token_id.map(lambda x: int(base_to_compact[int(x)])); targets.to_csv(out / "targets.csv", index=False)
    final_contexts = []; n_eval_unk = 0; n_eval_tokens = 0
    for row in heldout_raw:
        tid = int(row["base_target_id"])
        if tid not in keep_set: continue
        base_ids = np.asarray(row.pop("base_ids"), dtype=np.int64); compact = base_to_compact[base_ids]
        n_eval_unk += int((compact < 0).sum()); n_eval_tokens += int(len(compact)); compact[compact < 0] = unk_compact
        row["compact_ids"] = compact.astype(int).tolist(); row["compact_target_id"] = int(base_to_compact[tid]); final_contexts.append(row)
    with open(out / "contexts.jsonl", "w", encoding="utf-8") as f:
        for row in final_contexts: f.write(json.dumps(row, ensure_ascii=False) + "\n")

    metadata = {"schema_version": 2, "tokenizer": args.tokenizer, "source_dataset": "Helsinki-NLP/opus-100:de-en",
                "pairs_seen": int(len(dataset)), "heldout_parallel_pairs": int(n_heldout_pairs), "pair_level_holdout": True,
                "strict_exact_lexical_mask": True, "base_tokenizer_vocab_size": int(tok.vocab_size), "compact_vocab_size": int(len(sorted_used)),
                "eos_compact_id": int(base_to_compact[int(tok.eos_token_id)]), "unk_compact_id": unk_compact,
                "n_targets": int(len(targets)), "n_false_friends": int((targets.relation == "false_friend").sum()),
                "n_true_friends": int((targets.relation == "true_friend").sum()), "n_eval_contexts": int(len(final_contexts)),
                "eval_unk_fraction": float(n_eval_unk / max(n_eval_tokens, 1)),
                "holdout_rule": {"modulo": args.holdout_modulo, "bucket": args.holdout_bucket},
                "min_target_occurrences": int(args.min_target_occurrences)}
    with open(out / "metadata.json", "w", encoding="utf-8") as f: json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__": main()
