#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
from datasets import load_dataset
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer


def stable_holdout(text: str, modulo: int, bucket: int) -> bool:
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return int(h[:12], 16) % modulo == bucket


def extract_word(raw: str) -> str:
    return str(raw).split("(")[0].strip()


def discover_semantic_column(columns: Iterable[str]) -> str:
    candidates = [c for c in columns if "Which sentence is more semantically appropriate?" in str(c)]
    if len(candidates) != 1:
        raise RuntimeError(f"could not uniquely identify Stingray semantic label column: {candidates}")
    return candidates[0]


def single_surface_token(tokenizer, word: str) -> Tuple[int | None, str | None]:
    # Mid-sentence surface form is the relevant intervention. XLM-R/SentencePiece
    # usually encodes the leading word-boundary marker from the prefixed space.
    variants = [" " + word, word]
    for variant in variants:
        ids = tokenizer.encode(variant, add_special_tokens=False)
        if len(ids) == 1:
            return int(ids[0]), variant
    return None, None


def load_stingray_targets(tokenizer_name: str, language_pair: str) -> pd.DataFrame:
    if language_pair != "en_de":
        raise NotImplementedError("v0.1 causal gate is intentionally restricted to en_de")
    csv_path = hf_hub_download(
        repo_id="StingrayBench/StingrayBench",
        repo_type="dataset",
        filename="data/en_de.csv",
    )
    raw = pd.read_csv(csv_path)
    semantic_col = discover_semantic_column(raw.columns)
    tok = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)

    rows = []
    for _, row in raw.iterrows():
        word = extract_word(row["Cognates"])
        token_id, variant = single_surface_token(tok, word)
        if token_id is None:
            continue
        flag = str(row[semantic_col]).strip()
        relation = "true_friend" if flag.lower() == "both" else "false_friend"
        rows.append(
            {
                "word": word,
                "relation": relation,
                "base_token_id": token_id,
                "tokenized_variant": variant,
                "meaning_en": str(row.get("Meaning in L1", "")).strip(),
                "meaning_de": str(row.get("Meaning in L2", "")).strip(),
                "stingray_flag": flag,
            }
        )

    targets = pd.DataFrame(rows).drop_duplicates(subset=["word", "base_token_id"]).reset_index(drop=True)
    # A token-level intervention cannot distinguish two lexical entries that map
    # to the exact same SentencePiece id. Keep one entry and make collisions visible.
    dup_ids = targets[targets.duplicated("base_token_id", keep=False)]
    if len(dup_ids):
        print("WARNING: dropping target token-id collisions:")
        print(dup_ids[["word", "base_token_id", "relation"]].to_string(index=False))
        targets = targets.drop_duplicates("base_token_id", keep="first").reset_index(drop=True)
    return targets


def append_sentence(stream: List[int], ids: List[int], eos_id: int) -> None:
    stream.extend(ids)
    stream.append(eos_id)


def tokenize_batches(tokenizer, texts: List[str], batch_size: int = 512) -> Iterable[List[List[int]]]:
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        enc = tokenizer(batch, add_special_tokens=False, padding=False, truncation=False)
        yield [list(map(int, ids)) for ids in enc["input_ids"]]


def main() -> None:
    p = argparse.ArgumentParser(description="Prepare EN-DE controlled lexical-sharing experiment")
    p.add_argument("--output", default="data/processed/en_de")
    p.add_argument("--tokenizer", default="xlm-roberta-base")
    p.add_argument("--max-pairs", type=int, default=1_000_000)
    p.add_argument("--min-target-occurrences", type=int, default=20)
    p.add_argument("--holdout-modulo", type=int, default=10)
    p.add_argument("--holdout-bucket", type=int, default=0)
    p.add_argument("--max-contexts-per-word-lang", type=int, default=200)
    args = p.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(args.tokenizer, use_fast=True)
    if tok.eos_token_id is None:
        raise RuntimeError("tokenizer must expose eos_token_id")

    targets = load_stingray_targets(args.tokenizer, "en_de")
    target_ids = set(map(int, targets["base_token_id"].tolist()))
    target_by_id = {int(r.base_token_id): r for r in targets.itertuples(index=False)}

    print(f"Stingray single-token targets before corpus-frequency filter: {len(targets)}")
    dataset = load_dataset("Helsinki-NLP/opus-100", "de-en", split="train")
    if args.max_pairs and args.max_pairs < len(dataset):
        dataset = dataset.select(range(args.max_pairs))

    streams: Dict[str, List[int]] = {"en": [], "de": []}
    used_ids = {int(tok.unk_token_id), int(tok.eos_token_id)}
    train_counts = {"en": Counter(), "de": Counter()}
    heldout_counts = {"en": Counter(), "de": Counter()}
    heldout_raw: List[dict] = []
    context_cap = defaultdict(int)

    # Process modest batches to keep memory controlled while still using fast-tokenizer batching.
    batch_rows = 512
    for start in range(0, len(dataset), batch_rows):
        block = dataset[start : start + batch_rows]["translation"]
        texts_en = [str(x["en"]) for x in block]
        texts_de = [str(x["de"]) for x in block]
        enc_en = tok(texts_en, add_special_tokens=False, padding=False, truncation=False)["input_ids"]
        enc_de = tok(texts_de, add_special_tokens=False, padding=False, truncation=False)["input_ids"]

        for pair_offset, (text_en, text_de, ids_en, ids_de) in enumerate(zip(texts_en, texts_de, enc_en, enc_de)):
            pair_id = start + pair_offset
            for lang, text, ids in (("en", text_en, ids_en), ("de", text_de, ids_de)):
                ids = list(map(int, ids))
                present = sorted(target_ids.intersection(ids))
                is_heldout = bool(present) and stable_holdout(
                    f"{pair_id}\t{lang}\t{text}", args.holdout_modulo, args.holdout_bucket
                )
                if is_heldout:
                    for tid in present:
                        meta = target_by_id[tid]
                        key = (meta.word, lang)
                        if context_cap[key] < args.max_contexts_per_word_lang:
                            positions = [i for i, x in enumerate(ids) if x == tid]
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
                                }
                            )
                            context_cap[key] += 1
                        heldout_counts[lang][tid] += ids.count(tid)
                    continue

                append_sentence(streams[lang], ids, int(tok.eos_token_id))
                used_ids.update(ids)
                for tid in present:
                    train_counts[lang][tid] += ids.count(tid)

        if start and start % 50_000 == 0:
            print(f"processed {start:,}/{len(dataset):,} sentence pairs")

    # Filter targets to lexical items with enough evidence in BOTH languages.
    keep_base_ids = []
    freq_rows = []
    for row in targets.itertuples(index=False):
        tid = int(row.base_token_id)
        en_n = int(train_counts["en"][tid])
        de_n = int(train_counts["de"][tid])
        keep = en_n >= args.min_target_occurrences and de_n >= args.min_target_occurrences
        freq_rows.append((en_n, de_n, keep))
        if keep:
            keep_base_ids.append(tid)
            used_ids.add(tid)
    targets["train_count_en"] = [x[0] for x in freq_rows]
    targets["train_count_de"] = [x[1] for x in freq_rows]
    targets["passes_frequency_gate"] = [x[2] for x in freq_rows]
    targets = targets[targets["passes_frequency_gate"]].copy().reset_index(drop=True)
    keep_set = set(keep_base_ids)
    print(f"targets after >= {args.min_target_occurrences} occurrences in each language: {len(targets)}")
    print(targets["relation"].value_counts().to_dict())

    # Compact the XLM-R vocabulary to ids actually observed in the training streams,
    # following the core efficiency idea in Kallini et al. while keeping our target-only intervention explicit.
    sorted_used = np.array(sorted(used_ids), dtype=np.int64)
    base_to_compact = np.full(tok.vocab_size, -1, dtype=np.int32)
    base_to_compact[sorted_used] = np.arange(len(sorted_used), dtype=np.int32)
    compact_to_base = sorted_used.astype(np.int32)
    unk_compact = int(base_to_compact[int(tok.unk_token_id)])

    np.save(out / "base_to_compact.npy", base_to_compact)
    np.save(out / "compact_to_base.npy", compact_to_base)

    for lang in ("en", "de"):
        arr = np.asarray(streams[lang], dtype=np.int64)
        compact = base_to_compact[arr]
        if np.any(compact < 0):
            raise AssertionError("training stream contains token missing from compact vocabulary")
        np.save(out / f"train_{lang}.npy", compact.astype(np.int32))

    targets["compact_token_id"] = targets["base_token_id"].map(lambda x: int(base_to_compact[int(x)]))
    targets.to_csv(out / "targets.csv", index=False)

    # Convert held-out contexts after compact vocabulary is known.
    final_contexts = []
    valid_words = set(targets["word"].tolist())
    for row in heldout_raw:
        if row["word"] not in valid_words or int(row["base_target_id"]) not in keep_set:
            continue
        base_ids = np.asarray(row.pop("base_ids"), dtype=np.int64)
        compact = base_to_compact[base_ids]
        compact[compact < 0] = unk_compact
        row["compact_ids"] = compact.astype(int).tolist()
        row["compact_target_id"] = int(base_to_compact[int(row["base_target_id"])])
        final_contexts.append(row)

    with open(out / "contexts.jsonl", "w", encoding="utf-8") as f:
        for row in final_contexts:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    metadata = {
        "tokenizer": args.tokenizer,
        "source_dataset": "Helsinki-NLP/opus-100:de-en",
        "pairs_seen": len(dataset),
        "base_tokenizer_vocab_size": int(tok.vocab_size),
        "compact_vocab_size": int(len(sorted_used)),
        "eos_base_id": int(tok.eos_token_id),
        "eos_compact_id": int(base_to_compact[int(tok.eos_token_id)]),
        "unk_compact_id": unk_compact,
        "n_targets": int(len(targets)),
        "n_false_friends": int((targets.relation == "false_friend").sum()),
        "n_true_friends": int((targets.relation == "true_friend").sum()),
        "n_eval_contexts": len(final_contexts),
        "holdout_rule": {
            "modulo": args.holdout_modulo,
            "bucket": args.holdout_bucket,
            "max_contexts_per_word_lang": args.max_contexts_per_word_lang,
        },
        "min_target_occurrences": args.min_target_occurrences,
    }
    with open(out / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
