#!/usr/bin/env python3
"""Persist numerical observations without republishing the source benchmark corpus."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil


def digest(value):
    if isinstance(value, str):
        value = value.encode()
    return hashlib.sha256(value).hexdigest()


def package(run: Path, destination: Path):
    out = destination / run.name
    out.mkdir(parents=True, exist_ok=False)
    files = {}
    for path in sorted(run.iterdir()):
        if path.is_file():
            files[path.name] = {"sha256": digest(path.read_bytes()), "bytes": path.stat().st_size}
    common = ("item_id", "lexeme_family_id", "sense_pair_id", "context_family_id", "source_language",
              "target_language", "task", "type", "source_index", "source_label", "status")
    per_file = {
        "trials.jsonl": ("scores", "null_input_scores", "variant", "context_revision", "correct_index",
                         "rotation", "content_order", "label_names", "label_token_ids", "label_logps",
                         "unrestricted_argmax_token", "rendered_prompt_sha256", "input_tokens"),
        "chat_trials.jsonl": ("rotation", "content_order", "label_token_ids", "label_logps",
                              "unrestricted_argmax_token", "rendered_prompt_sha256", "input_tokens"),
        "generations.jsonl": ("generated", "generated_token_ids", "generated_tokens", "hit_token_limit",
                              "rendered_prompt_sha256"),
    }
    for name, extras in per_file.items():
        path = run / name
        if not path.exists():
            continue
        rows = []
        for line in path.read_text().splitlines():
            row = json.loads(line)
            compact = {key: row[key] for key in common + extras if key in row}
            for key in ("sentence", "prompt", "context_original", "context_paraphrase", "context_masked", "question"):
                if key in row:
                    compact[key + "_sha256"] = digest(row[key])
            for key in ("candidates", "texts", "options"):
                if key in row:
                    compact[key + "_sha256"] = [digest(text) for text in row[key]]
            rows.append(compact)
        (out / name).write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
    for name in ("manifest.json", "summary.json", "pair_summary.json", "paired_predictions.jsonl", "measurement_audit.json",
                 "translation_agent_review.jsonl", "numerical_audit.json", "code_snapshot.py", "scorer_snapshot.py"):
        if (run / name).exists():
            shutil.copyfile(run / name, out / name)
    provenance = {"local_raw_run": str(run.resolve()), "original_files": files,
                  "policy": "Raw source sentences/options/prompts remain in local run. This bundle keeps hashes, numerical scores, model outputs, code snapshots and non-human review. It is not an independent semantic annotation."}
    (out / "raw_provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2))
    print(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("runs", type=Path, nargs="+")
    args = parser.parse_args()
    for run in args.runs:
        package(run, args.destination)
