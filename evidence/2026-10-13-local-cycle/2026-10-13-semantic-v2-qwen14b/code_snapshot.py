#!/usr/bin/env python3
"""Paired original/paraphrase/masked semantic applications; exploratory new labels."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import time

try:
    from scripts.run_doppelganger_diagnostics import score_labels, digest
    from scripts.analyze_doppelganger_diagnostics import bootstrap
except ModuleNotFoundError:
    from run_doppelganger_diagnostics import score_labels, digest
    from analyze_doppelganger_diagnostics import bootstrap


def build_trials(items: list[dict]) -> list[dict]:
    trials = []
    for item in items:
        if len(item["options"]) != 2 or item["correct_index"] not in (0, 1, None):
            raise ValueError("Two options and an explicit label or null ambiguity are required")
        for variant in item.get("variants", ("original", "paraphrase", "masked")):
            gold = item.get("variant_correct_indices", {}).get(variant, item["correct_index"])
            if gold not in (0, 1, None):
                raise ValueError("Invalid variant label")
            for rotation, order in enumerate(([0, 1], [1, 0])):
                instruction = ("正解の選択肢の記号（A、B）のみを答えてください。" if item["source_language"] == "jp"
                               else "只回答正确选项的字母（A、B）。")
                prompt = item["variant_prompts"][variant] + "\n" + "\n".join(
                    f"{label}) {item['options'][idx]}" for label, idx in zip("AB", order)) + "\n" + instruction
                trials.append({**item, "variant": variant, "correct_index": gold,
                               "rotation": rotation, "content_order": order,
                               "label_names": "AB", "prompt": prompt})
    return trials


def summarize(trials: list[dict]) -> dict:
    import math
    grouped = defaultdict(list)
    for row in trials:
        grouped[(row["item_id"], row["variant"])].append(row)
    decisions = []
    for (item, variant), rows in grouped.items():
        if len(rows) != 2 or {r["rotation"] for r in rows} != {0, 1}:
            raise ValueError("Incomplete/duplicated option rotations")
        scores = [0.0, 0.0]
        choices = []
        for r in rows:
            choices.append(r["content_order"][max(range(2), key=r["label_logps"].__getitem__)])
            for j, index in enumerate(r["content_order"]):
                scores[index] += r["label_logps"][j] / 2
        r = rows[0]
        gold = r["correct_index"]
        pred = max(range(2), key=scores.__getitem__)
        decisions.append({"item_id": item, "lexeme_family_id": r["lexeme_family_id"],
                          "source_language": r["source_language"], "context_revision": r["context_revision"],
                          "variant": variant, "correct_index": gold, "prediction": pred,
                          "correct": pred == gold if gold is not None else None,
                          "rotation_stable": len(set(choices)) == 1,
                          "rotation_choices": choices,
                          "option0_minus_option1_logp": scores[0] - scores[1],
                          "correct_minus_foil_logp": scores[gold] - scores[1 - gold] if gold is not None else None,
                          "mean_label_probability_mass": sum(sum(math.exp(x) for x in t["label_logps"]) for t in rows) / 2})
    grouped_stats = defaultdict(list)
    for d in decisions:
        grouped_stats[(d["context_revision"], d["variant"])].append(d)
    stats = []
    for (context, variant), rows in grouped_stats.items():
        vals = defaultdict(list)
        for r in rows:
            if r["correct"] is not None:
                vals[r["lexeme_family_id"]].append(float(r["correct"]))
        stats.append({"context_revision": context, "variant": variant, "n_instances": len(rows),
                      "n_labeled": sum(r["correct"] is not None for r in rows),
                      "n_correct": sum(r["correct"] is True for r in rows), "family_agreement": bootstrap(vals),
                      "rotation_stable": sum(r["rotation_stable"] for r in rows)})
    return {"decisions": decisions, "groups": stats,
            "interpretation": "Exploratory agent-reviewed labels. Masked agreement measures residual cues, not knowledge. Paraphrase repair is constructive sufficiency, not a natural internal mechanism."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--items", type=Path, required=True)
    ap.add_argument("--model-path", type=Path, required=True)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    items = [json.loads(line) for line in args.items.read_text().splitlines() if line.strip()]
    trials = build_trials(items)
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
                "model_id": args.model_id, "model_revision": args.model_path.name,
                "tokenizer_revision": args.model_path.name, "items_sha256": digest(args.items.read_bytes()),
                "code_sha256": digest(Path(__file__).read_bytes()), "n_items": len(items),
                "n_families": len({r["lexeme_family_id"] for r in items}), "n_trials": len(trials),
                "protocol": sorted({r.get("schema_version", "unspecified") for r in items}), "seed": 20261013,
                "sampling_status": "Exploratory: 24 families preselected; v1/v2 material reviewers blind to corresponding outputs. Root selected v2 contrast after seeing v1 aggregate limitation; not held-out confirmation.",
                "cuda_visible_devices": os.getenv("CUDA_VISIBLE_DEVICES"), "host": platform.node(),
                "dtype": "bfloat16", "attention": "sdpa", "batch_size": 16,
                "dependent_code_sha256": digest(Path(score_labels.__code__.co_filename).read_bytes())}
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    (args.output / "code_snapshot.py").write_bytes(Path(__file__).read_bytes())
    (args.output / "scorer_snapshot.py").write_bytes(Path(score_labels.__code__.co_filename).read_bytes())
    (args.output / "items.jsonl").write_bytes(args.items.read_bytes())
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    start = time.monotonic()
    torch.set_num_threads(4)
    torch.manual_seed(20261013)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True, trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model_path, torch_dtype=torch.bfloat16,
                                               local_files_only=True, trust_remote_code=False,
                                               device_map={"": "cuda:0"}, attn_implementation="sdpa").eval()
    result = score_labels(model, tokenizer, trials, 16)
    (args.output / "trials.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in result))
    summary = summarize(result)
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    manifest.update({"status": "COMPLETE", "elapsed_seconds": time.monotonic() - start,
                     "environment": {"python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__},
                     "peak_allocated_gb": torch.cuda.max_memory_allocated() / 1e9,
                     "gpu": torch.cuda.get_device_name(), "chat_template_sha256": digest(tokenizer.chat_template or ""),
                     "finished_utc": datetime.now(timezone.utc).isoformat()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(json.dumps(summary["groups"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
