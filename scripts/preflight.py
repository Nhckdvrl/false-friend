#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from false_friend_lab.io import read_jsonl


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
    p = argparse.ArgumentParser(description="Fail-fast scientific/data validation before allocating GPUs")
    p.add_argument("--data", default="data/processed/en_de")
    p.add_argument("--min-words-per-relation", type=int, default=10)
    p.add_argument("--min-contexts-per-cell", type=int, default=10)
    p.add_argument("--max-mean-oov", type=float, default=0.05)
    p.add_argument("--skip-hash-check", action="store_true")
    a = p.parse_args()
    d = Path(a.data)
    required = [
        "metadata.json", "targets.csv", "contexts.jsonl", "train_en.npy", "train_de.npy",
        "train_en_lexical_mask.npy", "train_de_lexical_mask.npy", "base_to_compact.npy",
        "compact_to_base.npy", "holdout_pair_ids.npy",
    ]
    problems = [f"missing {x}" for x in required if not (d / x).exists()]
    if problems:
        raise SystemExit("PRECHECK FAIL: " + "; ".join(problems))

    meta = json.load(open(d / "metadata.json", encoding="utf-8"))
    targets = pd.read_csv(d / "targets.csv")
    contexts = read_jsonl(d / "contexts.jsonl")
    V = int(meta["compact_vocab_size"])
    target_ids = set(map(int, targets.compact_token_id))

    if int(meta.get("schema_version", 0)) < 3:
        problems.append("schema_version < 3; data are not from audited preparation")
    if not meta.get("parallel_pair_level_holdout", False):
        problems.append("pair-level holdout not asserted")
    if not meta.get("strict_exact_lexical_mask", False):
        problems.append("strict exact-lexical masking not asserted")
    if not meta.get("true_friend_source_is_common_config", False):
        problems.append("true-friend controls were not sourced from Stingray common config")

    if not a.skip_hash_check:
        for name, expected in meta.get("component_sha256", {}).items():
            path = d / name
            if not path.exists() or sha256_file(path) != expected:
                problems.append(f"component hash mismatch: {name}")

    for relation in ["false_friend", "true_friend"]:
        n = int((targets.relation == relation).sum())
        if n < a.min_words_per_relation:
            problems.append(f"only {n} lexical items for {relation} (<{a.min_words_per_relation})")
    if targets.compact_token_id.duplicated().any():
        problems.append("duplicate compact target id")
    if not ((targets.compact_token_id >= 0) & (targets.compact_token_id < V)).all():
        problems.append("target compact id outside base vocabulary")
    if "source_file" in targets.columns:
        tc_sources = " ".join(targets.loc[targets.relation == "true_friend", "source_file"].astype(str).unique()).lower()
        if "common" not in tc_sources:
            problems.append("true-friend source filename does not look like Stingray common config")

    cells = Counter((r["relation"], r["lang"]) for r in contexts)
    for relation in ["false_friend", "true_friend"]:
        for lang in ["en", "de"]:
            if cells[(relation, lang)] < a.min_contexts_per_cell:
                problems.append(f"only {cells[(relation, lang)]} contexts for {relation}/{lang}")

    word_lang = Counter((r["word"], r["lang"]) for r in contexts)
    for word in targets.word.astype(str):
        for lang in ["en", "de"]:
            if word_lang[(word, lang)] < 1:
                problems.append(f"retained target lacks held-out {lang} context: {word}")

    if contexts and float(np.mean([r.get("oov_fraction", 0.0) for r in contexts])) > a.max_mean_oov:
        problems.append("evaluation mean OOV fraction too high")

    holdout_ids = set(map(int, np.load(d / "holdout_pair_ids.npy")))
    seen_context_ids = set()
    for r in contexts:
        if r["context_id"] in seen_context_ids:
            problems.append(f"duplicate context_id {r['context_id']}")
        seen_context_ids.add(r["context_id"])
        if int(r["pair_id"]) not in holdout_ids:
            problems.append(f"context pair missing from holdout_pair_ids: {r['context_id']}")
        ids = list(map(int, r["compact_ids"]))
        target = int(r["compact_target_id"])
        if target not in target_ids:
            problems.append(f"unknown target in {r['context_id']}")
        for pos in r["positions"]:
            if pos < 0 or pos >= len(ids) or ids[pos] != target:
                problems.append(f"bad target position in {r['context_id']}")

    target_lookup = targets.set_index("compact_token_id")
    for lang in ["en", "de"]:
        ids = np.load(d / f"train_{lang}.npy", mmap_mode="r")
        mask = np.load(d / f"train_{lang}_lexical_mask.npy", mmap_mode="r")
        if len(ids) != len(mask):
            problems.append(f"{lang} ids/mask length mismatch")
            continue
        if len(ids) < 1000:
            problems.append(f"{lang} stream unexpectedly small")
        if len(ids) and (int(ids.min()) < 0 or int(ids.max()) >= V):
            problems.append(f"{lang} id outside base vocabulary")
        marked = ids[np.asarray(mask, dtype=bool)]
        if len(marked) and not np.isin(marked, np.asarray(sorted(target_ids), dtype=ids.dtype)).all():
            problems.append(f"{lang} lexical mask marks a non-retained target token")
        observed = Counter(map(int, marked.tolist()))
        count_col = f"train_count_{lang}"
        for tid, row in target_lookup.iterrows():
            if observed[int(tid)] != int(row[count_col]):
                problems.append(
                    f"{lang} exact-mask count mismatch for {row['word']}: "
                    f"stream={observed[int(tid)]}, table={int(row[count_col])}"
                )

    report = {
        "status": "FAIL" if problems else "PASS",
        "schema_version": meta.get("schema_version"),
        "data_fingerprint": meta.get("data_fingerprint"),
        "compact_vocab_size": V,
        "relation_counts": targets.relation.value_counts().to_dict(),
        "context_cells": {f"{k[0]}/{k[1]}": v for k, v in cells.items()},
        "mean_oov_fraction": float(np.mean([r.get("oov_fraction", 0.0) for r in contexts])) if contexts else None,
        "problems": problems,
    }
    print(json.dumps(report, indent=2, default=str))
    if problems:
        raise SystemExit("PRECHECK FAIL: do not allocate GPUs until fixed")


if __name__ == "__main__":
    main()
