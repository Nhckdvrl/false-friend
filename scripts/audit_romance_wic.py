#!/usr/bin/env python3
"""Audit the source annotation object in Abuín et al. ACL 2026 TSV data.

Pure-data preflight, NO model results, NO downloaded dataset redistribution.
Source: https://github.com/mrtva/false-friends-vs-cognates
A lemma pair can be identical while the actual contextual *inflected forms* differ.
Case-sensitive whole-form detection is intentional; it does not substitute POS,
language direction, semantic validity or native-speaker checking.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DATA_FILES = (
    "auto-es-pt.tsv", "auto-gl-es.tsv", "auto-gl-pt.tsv",
    "human-es-pt.tsv", "human-gl-es.tsv", "human-gl-pt.tsv",
)
NEEDED = {"W1", "C1", "P1", "W2", "C2", "P2", "R", "POS"}


class InputError(ValueError):
    pass


def is_whole_form(form: str, context: str) -> bool:
    # \w is Unicode-aware in Python. Preserves case, accent, diacritics.
    if not form or not context:
        return False
    return re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", context) is not None


def load_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        missing = NEEDED - set(reader.fieldnames or ())
        if missing:
            raise InputError(f"{path}: missing columns {sorted(missing)}")
        rows = list(reader)
    for n, row in enumerate(rows, 2):
        if row["R"] not in ("0", "1"):
            raise InputError(f"{path}:{n}: R must be 0/1, got {row['R']!r}")
        if not all(row.get(k) for k in ("W1", "W2", "C1", "C2")):
            raise InputError(f"{path}:{n}: blank essential word/context")
    return rows


def audit_files(paths: list[Path]) -> dict:
    if not paths:
        raise InputError("No TSV files")
    total = Counter()
    groups: dict[str, dict] = {}
    repeated = defaultdict(list)
    candidates = []
    per_file = {}
    for path in paths:
        local = Counter()
        file_id = path.name
        if file_id.startswith("auto-"):
            language_pair = file_id[len("auto-"):-len(".tsv")]
        elif file_id.startswith("human-"):
            language_pair = file_id[len("human-"):-len(".tsv")]
        else:
            language_pair = file_id.removesuffix(".tsv")
        for ordinal, row in enumerate(load_tsv(path), 2):
            for counter in (local, total):
                counter["rows"] += 1
            exact = row["W1"] == row["W2"]
            present = is_whole_form(row["W1"], row["C1"]) and is_whole_form(row["W2"], row["C2"])
            relation = row["R"]
            if exact:
                local["exact_lemma"] += 1
                total["exact_lemma"] += 1
                target = "exact_lemma_ff" if relation == "0" else "exact_lemma_same_sense_context"
                local[target] += 1
                total[target] += 1
                group = (language_pair, row["W1"], relation)
                repeated[group].append(f"{file_id}:{ordinal}")
            if exact and present:
                local["exact_form_in_both_contexts"] += 1
                total["exact_form_in_both_contexts"] += 1
                kind = "context_ff" if relation == "0" else "context_same_sense"
                local[kind] += 1
                total[kind] += 1
                if relation == "0":
                    same_pos_flag = "/" not in row.get("POS", "")
                    if same_pos_flag:
                        local["context_ff_without_slash_pos"] += 1
                        total["context_ff_without_slash_pos"] += 1
                    candidates.append({
                        "source_file": file_id,
                        "source_row": ordinal,
                        "language_pair_file_hint_only": language_pair,
                        "form": row["W1"], "POS_source": row["POS"],
                        "surface_match_case_sensitive": True,
                        "contextual_different_sense_R0": True,
                        "language_direction_verified": False,
                        "annotation_verified_for_new_experiment": False,
                    })
        per_file[file_id] = dict(sorted(local.items()))
    distinct = {(c["language_pair_file_hint_only"], c["form"]) for c in candidates}
    cross_subset_duplicates = {
        " / ".join(key): where for key, where in repeated.items() if len(where) > 1
    }
    return {
        "status": "SOURCE_DATA_PREFLIGHT_NOT_SCIENTIFIC_RESULT",
        "source_reference": "Abuín et al., ACL 2026; mrtva/false-friends-vs-cognates",
        "file_summaries": per_file,
        "totals": dict(sorted(total.items())),
        "unique_candidate_language_pair_form": len(distinct),
        "same_pair_form_label_duplicate_groups": len(cross_subset_duplicates),
        "candidate_manifest": candidates,
        "limitations": [
            "W1==W2 is the source lemma spelling, not full sense-distribution alignment.",
            "R labels equality or difference for THESE TWO SENTENCES only.",
            "Exact whole-form matching excludes inflections; compound/text segmentation requires review.",
            "Filename language pair does not certify which sentence side is which language.",
            "POS lacking a slash is not independent grammatical validity.",
            "Repeated auto/human and other lexeme instances are correlated, not independent evidence.",
            "No independent native-speaker or response-candidate validation performed.",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", type=Path, required=True, help="directory with six original publisher TSVs")
    ap.add_argument("--output", type=Path, required=True, help="write machine-readable audit, not training data")
    args = ap.parse_args()
    paths = [args.source_dir / name for name in DATA_FILES]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        ap.error("Missing source files:\n  " + "\n  ".join(missing))
    result = audit_files(paths)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Source rows:", result["totals"]["rows"])
    print("Strict exact-context FF records:", result["totals"].get("context_ff", 0))
    print("Unique language-pair / form candidate units:", result["unique_candidate_language_pair_form"])
    print("Output:", args.output)


if __name__ == "__main__":
    main()
