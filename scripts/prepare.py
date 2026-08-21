#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from array import array
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
from datasets import load_dataset
from huggingface_hub import hf_hub_download
from huggingface_hub.utils import EntryNotFoundError
from transformers import AutoTokenizer


def stable_holdout(key: str, modulo: int, bucket: int) -> bool:
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()
    return int(h[:12], 16) % modulo == bucket


def clean_surface(raw: object) -> str:
    return str(raw).split("(")[0].strip()


def strict_single_shared_token(tokenizer, word: str) -> int | None:
    """Require one identical SentencePiece id initially and after whitespace."""
    if not word or any(ch.isspace() for ch in word):
        return None
    a = tokenizer.encode(word, add_special_tokens=False)
    b = tokenizer.encode(" " + word, add_special_tokens=False)
    if len(a) != 1 or len(b) != 1 or int(a[0]) != int(b[0]):
        return None
    return int(a[0])


def is_word_char(ch: str) -> bool:
    return bool(ch) and (ch.isalnum() or ch == "_")


def exact_lexical_mask(
    text: str,
    ids: List[int],
    offsets: List[Tuple[int, int]],
    token_to_word: Dict[int, str],
) -> List[bool]:
    """Mark only standalone exact target-word occurrences, never subword reuse."""
    if len(ids) != len(offsets):
        raise ValueError("offset/id length mismatch")
    mask = [False] * len(ids)
    for i, (tid, (start, end)) in enumerate(zip(ids, offsets)):
        word = token_to_word.get(int(tid))
        if word is None or start == end:
            continue
        if text[start:end] != word:
            continue
        left_ok = start == 0 or not is_word_char(text[start - 1])
        right_ok = end == len(text) or not is_word_char(text[end])
        if left_ok and right_ok:
            mask[i] = True
    return mask


def download_first(candidates: Iterable[str]) -> str:
    errors = []
    for filename in candidates:
        try:
            return hf_hub_download(
                repo_id="StingrayBench/StingrayBench",
                repo_type="dataset",
                filename=filename,
            )
        except EntryNotFoundError as e:
            errors.append(f"{filename}: {e}")
    raise FileNotFoundError("none of the Stingray files exist: " + " | ".join(errors))


def row_surface(row: pd.Series) -> str | None:
    """Return only an exactly shared written form across the two languages."""
    if "Cognates" in row.index and pd.notna(row["Cognates"]):
        return clean_surface(row["Cognates"])
    if {"Cognates_L1", "Cognates_L2"}.issubset(row.index):
        a, b = clean_surface(row["Cognates_L1"]), clean_surface(row["Cognates_L2"])
        return a if a == b else None
    return None


def relation_rows(raw: pd.DataFrame, relation: str, tokenizer, source_file: str) -> List[dict]:
    rows = []
    for _, row in raw.iterrows():
        word = row_surface(row)
        if word is None:
            continue
        tid = strict_single_shared_token(tokenizer, word)
        if tid is None:
            continue
        m1 = str(row.get("Meaning in L1", "")).strip()
        m2 = str(row.get("Meaning in L2", "")).strip()
        if relation == "false_friend" and m1 and m2 and m1.casefold() == m2.casefold():
            continue
        rows.append(
            {
                "word": word,
                "relation": relation,
                "base_token_id": tid,
                "meaning_en": m1,
                "meaning_de": m2,
                "source_file": source_file,
            }
        )
    return rows


def load_stingray_targets(tokenizer_name: str) -> pd.DataFrame:
    """Load FF and true-cognate controls from their actual Stingray sources."""
    tok = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    if not tok.is_fast:
        raise RuntimeError("a fast tokenizer is required for exact offset masks")

    ff_path = download_first(["data/en_de.csv", "data/en_de_false_friends.csv"])
    tc_path = download_first(["data/en_de_common_words.csv", "data/en_de_common.csv"])
    ff = pd.read_csv(ff_path)
    tc = pd.read_csv(tc_path)
    rows = relation_rows(ff, "false_friend", tok, Path(ff_path).name)
    rows += relation_rows(tc, "true_friend", tok, Path(tc_path).name)
    targets = pd.DataFrame(rows)
    if targets.empty:
        raise RuntimeError("no strict Stingray targets survived source/token filtering")

    targets = targets.drop_duplicates(["word", "base_token_id", "relation"]).reset_index(drop=True)
    dup = targets[targets.duplicated("base_token_id", keep=False)]
    if len(dup):
        print("WARNING: dropping tokenizer-id collisions across lexical targets:")
        print(dup[["word", "base_token_id", "relation"]].to_string(index=False))
        bad = set(map(int, dup.base_token_id.tolist()))
        targets = targets[~targets.base_token_id.isin(bad)].reset_index(drop=True)
    return targets


def append_sentence(stream, mask_stream, ids: List[int], mask: List[bool], eos: int) -> None:
    if len(ids) != len(mask):
        raise ValueError("ids/mask mismatch")
    stream.extend(map(int, ids))
    stream.append(int(eos))
    mask_stream.extend(1 if x else 0 for x in mask)
    mask_stream.append(0)


def sha256_file(path: Path, chunk: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(description="Prepare strict EN-DE lexical-sharing causal data")
    p.add_argument("--output", default="data/processed/en_de")
    p.add_argument("--tokenizer", default="xlm-roberta-base")
    p.add_argument("--max-pairs", type=int, default=1_000_000)
    p.add_argument("--min-target-occurrences", type=int, default=20)
    p.add_argument("--min-eval-contexts-per-word-lang", type=int, default=1)
    p.add_argument("--holdout-modulo", type=int, default=10)
    p.add_argument("--holdout-bucket", type=int, default=0)
    p.add_argument("--max-contexts-per-word-lang", type=int, default=200)
    args = p.parse_args()

    if args.holdout_modulo <= 1 or not (0 <= args.holdout_bucket < args.holdout_modulo):
        raise ValueError("invalid holdout modulo/bucket")

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(args.tokenizer, use_fast=True)
    if not tok.is_fast or tok.eos_token_id is None or tok.unk_token_id is None:
        raise RuntimeError("fast tokenizer with eos/unk ids required")

    targets = load_stingray_targets(args.tokenizer)
    token_to_word = {int(r.base_token_id): str(r.word) for r in targets.itertuples(index=False)}
    target_by_id = {int(r.base_token_id): r for r in targets.itertuples(index=False)}
    print("strict Stingray targets before corpus filters:", targets.relation.value_counts().to_dict())

    ds = load_dataset("Helsinki-NLP/opus-100", "de-en", split="train")
    if args.max_pairs and args.max_pairs < len(ds):
        ds = ds.select(range(args.max_pairs))

    streams = {"en": array("I"), "de": array("I")}
    masks = {"en": bytearray(), "de": bytearray()}
    used_ids = {int(tok.unk_token_id), int(tok.eos_token_id)}
    train_counts = {"en": Counter(), "de": Counter()}
    heldout_counts = {"en": Counter(), "de": Counter()}
    heldout_raw: List[dict] = []
    context_cap = defaultdict(int)
    holdout_pair_ids: List[int] = []

    batch_rows = 512
    for start in range(0, len(ds), batch_rows):
        block = ds[start : start + batch_rows]["translation"]
        texts = {"en": [str(x["en"]) for x in block], "de": [str(x["de"]) for x in block]}
        enc = {
            lang: tok(
                texts[lang], add_special_tokens=False, padding=False, truncation=False,
                return_offsets_mapping=True,
            )
            for lang in ("en", "de")
        }

        for off in range(len(block)):
            pair_id = start + off
            pair = {}
            pair_has_exact_target = False
            for lang in ("en", "de"):
                text = texts[lang][off]
                ids = list(map(int, enc[lang]["input_ids"][off]))
                offsets = [(int(a), int(b)) for a, b in enc[lang]["offset_mapping"][off]]
                exact = exact_lexical_mask(text, ids, offsets, token_to_word)
                pair[lang] = (text, ids, exact)
                pair_has_exact_target |= any(exact)

            holdout = pair_has_exact_target and stable_holdout(
                f"opus-pair-{pair_id}", args.holdout_modulo, args.holdout_bucket
            )
            if holdout:
                holdout_pair_ids.append(pair_id)
                for lang in ("en", "de"):
                    text, ids, exact = pair[lang]
                    by_tid = defaultdict(list)
                    for pos, (tid, hit) in enumerate(zip(ids, exact)):
                        if hit:
                            by_tid[int(tid)].append(pos)
                    all_tids = sorted(by_tid)
                    for tid, positions in by_tid.items():
                        meta = target_by_id[tid]
                        heldout_counts[lang][tid] += len(positions)
                        key = (meta.word, lang)
                        if context_cap[key] >= args.max_contexts_per_word_lang:
                            continue
                        heldout_raw.append(
                            {
                                "context_id": f"opus-{pair_id}-{lang}-{tid}",
                                "pair_id": pair_id,
                                "lang": lang,
                                "word": meta.word,
                                "relation": meta.relation,
                                "base_target_id": tid,
                                "text": text,
                                "base_ids": ids,
                                "positions": positions,
                                "all_exact_target_ids": all_tids,
                            }
                        )
                        context_cap[key] += 1
                continue

            for lang in ("en", "de"):
                _, ids, exact = pair[lang]
                append_sentence(streams[lang], masks[lang], ids, exact, int(tok.eos_token_id))
                used_ids.update(ids)
                for tid, hit in zip(ids, exact):
                    if hit:
                        train_counts[lang][int(tid)] += 1

        if start and start % 50_000 == 0:
            print(f"processed {start:,}/{len(ds):,} parallel pairs")

    keep_ids = []
    stats = []
    for r in targets.itertuples(index=False):
        tid = int(r.base_token_id)
        en_n, de_n = int(train_counts["en"][tid]), int(train_counts["de"][tid])
        en_e, de_e = int(heldout_counts["en"][tid]), int(heldout_counts["de"][tid])
        keep = (
            en_n >= args.min_target_occurrences and de_n >= args.min_target_occurrences
            and en_e >= args.min_eval_contexts_per_word_lang
            and de_e >= args.min_eval_contexts_per_word_lang
        )
        stats.append((en_n, de_n, en_e, de_e, keep))
        if keep:
            keep_ids.append(tid)
            used_ids.add(tid)
    targets["train_count_en"] = [x[0] for x in stats]
    targets["train_count_de"] = [x[1] for x in stats]
    targets["heldout_count_en"] = [x[2] for x in stats]
    targets["heldout_count_de"] = [x[3] for x in stats]
    targets["passes_evidence_gate"] = [x[4] for x in stats]
    targets = targets[targets.passes_evidence_gate].copy().reset_index(drop=True)
    keep_set = set(keep_ids)
    print("targets after evidence gate:", targets.relation.value_counts().to_dict())

    sorted_used = np.asarray(sorted(used_ids), dtype=np.int64)
    base_to_compact = np.full(tok.vocab_size, -1, dtype=np.int32)
    base_to_compact[sorted_used] = np.arange(len(sorted_used), dtype=np.int32)
    compact_to_base = sorted_used.astype(np.int32)
    unk_compact = int(base_to_compact[int(tok.unk_token_id)])
    np.save(out / "base_to_compact.npy", base_to_compact)
    np.save(out / "compact_to_base.npy", compact_to_base)
    np.save(out / "holdout_pair_ids.npy", np.asarray(sorted(set(holdout_pair_ids)), dtype=np.int64))

    keep_arr = np.asarray(sorted(keep_set), dtype=np.int64)
    for lang in ("en", "de"):
        arr = np.asarray(streams[lang], dtype=np.int64)
        raw_mask = np.frombuffer(masks[lang], dtype=np.uint8).astype(np.bool_)
        if len(raw_mask) != len(arr):
            raise AssertionError("training lexical mask misaligned")
        raw_mask &= np.isin(arr, keep_arr)
        compact = base_to_compact[arr]
        if np.any(compact < 0):
            raise AssertionError("training stream token missing from compact vocabulary")
        np.save(out / f"train_{lang}.npy", compact.astype(np.int32))
        np.save(out / f"train_{lang}_lexical_mask.npy", raw_mask)

    targets["compact_token_id"] = targets.base_token_id.map(lambda x: int(base_to_compact[int(x)]))
    targets.to_csv(out / "targets.csv", index=False)

    final_contexts = []
    for row in heldout_raw:
        tid = int(row["base_target_id"])
        if tid not in keep_set:
            continue
        surviving_types = set(map(int, row.pop("all_exact_target_ids"))).intersection(keep_set)
        if surviving_types != {tid}:
            continue
        base_ids = np.asarray(row.pop("base_ids"), dtype=np.int64)
        compact = base_to_compact[base_ids]
        oov = compact < 0
        compact[oov] = unk_compact
        row["compact_ids"] = compact.astype(int).tolist()
        row["compact_target_id"] = int(base_to_compact[tid])
        row["oov_fraction"] = float(oov.mean()) if len(oov) else 0.0
        final_contexts.append(row)

    contexts_path = out / "contexts.jsonl"
    with open(contexts_path, "w", encoding="utf-8") as f:
        for row in final_contexts:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    component_files = [
        "targets.csv", "contexts.jsonl", "train_en.npy", "train_de.npy",
        "train_en_lexical_mask.npy", "train_de_lexical_mask.npy",
        "compact_to_base.npy", "holdout_pair_ids.npy",
    ]
    component_hashes = {name: sha256_file(out / name) for name in component_files}
    fingerprint = hashlib.sha256(json.dumps(component_hashes, sort_keys=True).encode("utf-8")).hexdigest()
    metadata = {
        "schema_version": 3,
        "data_fingerprint": fingerprint,
        "component_sha256": component_hashes,
        "tokenizer": args.tokenizer,
        "source_dataset": "Helsinki-NLP/opus-100:de-en",
        "pairs_seen": len(ds),
        "parallel_pair_level_holdout": True,
        "strict_exact_lexical_mask": True,
        "true_friend_source_is_common_config": True,
        "base_tokenizer_vocab_size": int(tok.vocab_size),
        "compact_vocab_size": int(len(sorted_used)),
        "eos_compact_id": int(base_to_compact[int(tok.eos_token_id)]),
        "unk_compact_id": unk_compact,
        "n_targets": int(len(targets)),
        "n_false_friends": int((targets.relation == "false_friend").sum()),
        "n_true_friends": int((targets.relation == "true_friend").sum()),
        "n_eval_contexts": len(final_contexts),
        "n_holdout_pairs": len(set(holdout_pair_ids)),
        "min_target_occurrences": args.min_target_occurrences,
        "min_eval_contexts_per_word_lang": args.min_eval_contexts_per_word_lang,
        "holdout_rule": {
            "modulo": args.holdout_modulo,
            "bucket": args.holdout_bucket,
            "max_contexts_per_word_lang": args.max_contexts_per_word_lang,
        },
    }
    with open(out / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
