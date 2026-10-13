#!/usr/bin/env python3
"""Analyze source-label agreement at the lexical-family level, not prompt level."""
from __future__ import annotations

import argparse
from collections import defaultdict, Counter
import json
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def minimum(values: list[float]) -> int:
    return min(range(len(values)), key=values.__getitem__)


def candidate_mean(score: dict) -> float:
    part = score["parts"]["candidate"]
    return part["nll_sum"] / part["tokens"]


def predictions(record: dict) -> dict[str, int]:
    scores, null = record["scores"], record["null_input_scores"]
    return {
        "source_full_mean": minimum([s["full_nll_mean"] for s in scores]),
        "candidate_mean": minimum([candidate_mean(s) for s in scores]),
        "candidate_sum": minimum([s["parts"]["candidate"]["nll_sum"] for s in scores]),
        "null_candidate_mean": minimum([candidate_mean(s) for s in null]),
        "evidence_mean": minimum([candidate_mean(s) - candidate_mean(n) for s, n in zip(scores, null)]),
    }


def bootstrap(values: dict[str, list[float]], repetitions: int = 4000) -> dict:
    """Equal weight per family; paired differences supplied before resampling."""
    import numpy as np
    arr = np.array([sum(v) / len(v) for _, v in sorted(values.items())])
    if not len(arr):
        return {"n_families": 0, "mean": None, "ci95": None}
    rng = np.random.default_rng(20261013)
    means = arr[rng.integers(len(arr), size=(repetitions, len(arr)))].mean(axis=1)
    return {"n_families": len(arr), "mean": float(arr.mean()),
            "ci95": [float(x) for x in np.quantile(means, [0.025, 0.975])]}


def summarize_chat(records: list[dict]) -> dict[str, dict]:
    grouped = defaultdict(list)
    for r in records:
        grouped[r["item_id"]].append(r)
    result = {}
    for key, rows in grouped.items():
        if {r["rotation"] for r in rows} != {0, 1, 2, 3} or len(rows) != 4:
            raise ValueError(f"Incomplete or duplicate rotations: {key}")
        scores = [0.0] * 4
        choices = []
        for r in rows:
            choices.append(r["content_order"][max(range(4), key=r["label_logps"].__getitem__)])
            for label_idx, content_idx in enumerate(r["content_order"]):
                scores[content_idx] += r["label_logps"][label_idx] / 4
        result[key] = {
            "prediction": max(range(4), key=scores.__getitem__), "content_logps": scores,
            "rotation_choices": choices, "stable": len(set(choices)) == 1,
            "all_rotations_correct": all(c == 0 for c in choices),
            "unrestricted_label_fraction": sum(r["unrestricted_argmax_token"] in r["label_token_ids"] for r in rows) / 4,
        }
    return result


def analyze(run: Path) -> dict:
    manifest = json.loads((run / "manifest.json").read_text())
    items = read_jsonl(run / "trials.jsonl")
    chat = summarize_chat(read_jsonl(run / "chat_trials.jsonl")) if (run / "chat_trials.jsonl").exists() else {}
    grouped = defaultdict(list)
    paired = []
    for r in items:
        pred = predictions(r)
        pred_chat = chat.get(r["item_id"])
        compact = {k: r[k] for k in ["item_id", "lexeme_family_id", "source_language", "target_language", "task", "word_jp", "word_zh"]}
        compact.update({"predictions": pred, "chat": pred_chat})
        paired.append(compact)
        grouped[(r["source_language"], r["task"])].append((r, pred, pred_chat))
    summaries = []
    for (lang, task), rows in grouped.items():
        metrics = {}
        for metric in rows[0][1]:
            vals = defaultdict(list)
            for r, pred, _ in rows:
                vals[r["lexeme_family_id"]].append(float(pred[metric] == 0))
            metrics[metric] = {**bootstrap(vals), "choices": dict(Counter(p[metric] for _, p, _ in rows))}
        for metric in ("candidate_mean", "candidate_sum", "null_candidate_mean", "evidence_mean"):
            vals = defaultdict(list)
            for r, pred, _ in rows:
                vals[r["lexeme_family_id"]].append(float(pred[metric] == 0) - float(pred["source_full_mean"] == 0))
            metrics[metric + "_minus_source"] = bootstrap(vals)
        vals = defaultdict(list)
        for r, pred, _ in rows:
            vals[r["lexeme_family_id"]].append(float(pred["candidate_mean"] == 0) - float(pred["null_candidate_mean"] == 0))
        metrics["conditional_minus_null"] = bootstrap(vals)
        selected = [(r, p, c) for r, p, c in rows if c is not None]
        if selected:
            for metric in ["chat", "chat_all_correct", "chat_stable", "chat_minus_source", "source_on_chat_subset"]:
                vals = defaultdict(list)
                for r, pred, c in selected:
                    value = {"chat": float(c["prediction"] == 0),
                             "chat_all_correct": float(c["all_rotations_correct"]),
                             "chat_stable": float(c["stable"]),
                             "chat_minus_source": float(c["prediction"] == 0) - float(pred["source_full_mean"] == 0),
                             "source_on_chat_subset": float(pred["source_full_mean"] == 0)}[metric]
                    vals[r["lexeme_family_id"]].append(value)
                metrics[metric] = bootstrap(vals)
        summaries.append({"source_language": lang, "task": task, "n_rows": len(rows), "metrics": metrics,
                          "source_vs_conditional_choice_disagreements": sum(p["source_full_mean"] != p["candidate_mean"] for _, p, _ in rows),
                          "source_vs_null_choice_agreement": sum(p["source_full_mean"] == p["null_candidate_mean"] for _, p, _ in rows)})
    transitions = []
    by_family = defaultdict(dict)
    for r in paired:
        if r["chat"]:
            by_family[(r["lexeme_family_id"], r["source_language"])][r["task"]] = r["chat"]
    for lang in ("jp", "zh"):
        for first, second in [("meaning", "context"), ("context", "translation"), ("meaning", "translation")]:
            counts = Counter()
            stable_counts = Counter()
            for (_, l), tasks in by_family.items():
                if l == lang and first in tasks and second in tasks:
                    key = f"{int(tasks[first]['prediction'] == 0)}->{int(tasks[second]['prediction'] == 0)}"
                    counts[key] += 1
                    if tasks[first]["stable"] and tasks[second]["stable"]:
                        stable_counts[key] += 1
            transitions.append({"source_language": lang, "first": first, "second": second,
                                "counts": dict(counts), "both_tasks_rotation_stable": dict(stable_counts)})
    result = {"model_id": manifest["model_id"], "model_revision": manifest["model_revision"],
              "run_status": manifest["status"], "n_rows": len(items),
              "n_families": len({r["lexeme_family_id"] for r in items}), "groups": summaries,
              "transitions": transitions,
              "interpretation": "All accuracy measures are published source-label agreement. Bootstrap unit is lexical family; new readouts are not original scores or causal evidence."}
    (run / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    (run / "paired_predictions.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in paired))
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("runs", nargs="+", type=Path)
    args = ap.parse_args()
    for run in args.runs:
        result = analyze(run)
        print(run, result["run_status"])
        print("lang task n source conditional null evidence chat source-subset stable-chat")
        for row in result["groups"]:
            m = row["metrics"]
            keys = ["source_full_mean", "candidate_mean", "null_candidate_mean", "evidence_mean",
                    "chat", "source_on_chat_subset", "chat_all_correct"]
            print(row["source_language"], row["task"], row["n_rows"],
                  *[f"{100 * m[k]['mean']:.1f}" if k in m else "pending" for k in keys])
        print("paired transitions", json.dumps(result["transitions"]))


if __name__ == "__main__":
    main()
