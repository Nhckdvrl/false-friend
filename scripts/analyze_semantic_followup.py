#!/usr/bin/env python3
"""Analyze explicit sense pairs, ambiguous conditions and full-vocabulary label mass."""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

try:
    from scripts.run_semantic_followup import summarize
except ModuleNotFoundError:
    from run_semantic_followup import summarize


def analyze(run):
    trials = [json.loads(line) for line in (run / "trials.jsonl").read_text().splitlines()]
    summary = summarize(trials)
    grouped = defaultdict(dict)
    for row in summary["decisions"]:
        grouped[row["item_id"]][row["variant"]] = row
    pairs = []
    for item, variants in grouped.items():
        if "foil_paraphrase" not in variants:
            continue
        first, second = variants["paraphrase"], variants["foil_paraphrase"]
        assert {first["correct_index"], second["correct_index"]} == {0, 1}
        correct = first["correct"] and second["correct"]
        pairs.append({"item_id": item, "lexeme_family_id": first["lexeme_family_id"],
                      "both_correct": correct,
                      "both_correct_all_orders": correct and first["rotation_stable"] and second["rotation_stable"],
                      "option0_response_logp_difference": first["option0_minus_option1_logp"] - second["option0_minus_option1_logp"]})
    masses = [sum(math.exp(lp) for lp in row["label_logps"]) for row in trials]
    pair_summary = {"n_pairs": len(pairs), "n_families": len({r["lexeme_family_id"] for r in pairs}),
                    "n_both_correct": sum(r["both_correct"] for r in pairs),
                    "n_both_correct_all_orders": sum(r["both_correct_all_orders"] for r in pairs), "pairs": pairs,
                    "format_audit": {"n_trials": len(trials), "min_label_probability_mass": min(masses),
                                     "mean_label_probability_mass": sum(masses) / len(masses),
                                     "off_label_argmax_count": sum(r["unrestricted_argmax_token"] not in r["label_token_ids"] for r in trials)},
                    "interpretation": "Explicit input sense substitutions, exploratory items. Ambiguous/null-gold conditions excluded from agreement. No natural internal mechanism inferred."}
    (run / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    (run / "pair_summary.json").write_text(json.dumps(pair_summary, ensure_ascii=False, indent=2))
    print(run, "pairs", len(pairs), "both-correct", pair_summary["n_both_correct_all_orders"], pair_summary["format_audit"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path)
    for run in parser.parse_args().runs:
        analyze(run)
