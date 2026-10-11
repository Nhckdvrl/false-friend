#!/usr/bin/env python3
"""Inspect published high-/low-semantic-constraint stimuli without model inference.

Source: EshaanT/Bilingual_processing_LLMs data/task3_en_{de,fr,es}.csv.
The script checks schema and preflights contrasts, NOT stimulus semantics.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

COLS = {"ID", "en", "type", "lexical_category", "low_en", "high_en"}


def audit(path: Path, language: str) -> dict:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = COLS | {language, f"low_{language}", f"high_{language}"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"{path}: missing {sorted(required - set(reader.fieldnames or []))}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path}: empty")
    counts = Counter()
    malformed = []
    for i, row in enumerate(rows, 2):
        counts[str(row["type"]).strip().upper()] += 1
        problems = []
        for col in [f"low_{language}", f"high_{language}", "low_en", "high_en"]:
            if "<MASK>" not in row[col]:
                problems.append(col)
        if problems:
            malformed.append({"row": i, "mask_missing_in": problems})
    return {
        "file": path.name,
        "rows": len(rows),
        "type_counts": dict(sorted(counts.items())),
        "missing_mask_rows": len(malformed),
        "missing_mask_details_first10": malformed[:10],
        "note": "Task 3 is context-before-masked-word semantic-constraint, not late reanalysis; semantics not human re-annotated here."
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    langs = ["de", "fr", "es"]
    results = [audit(args.source_dir / f"task3_en_{lang}.csv", lang) for lang in langs]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for row in results:
        print(row["file"], row["rows"], row["type_counts"], "missing masks", row["missing_mask_rows"])


if __name__ == "__main__":
    main()
