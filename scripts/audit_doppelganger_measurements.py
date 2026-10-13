#!/usr/bin/env python3
"""CPU-only audit of saved Type-1 scores; does not mutate inference artifacts."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path

try:
    from scripts.run_doppelganger_diagnostics import null_prefix
except ModuleNotFoundError:
    from run_doppelganger_diagnostics import null_prefix


def rows(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def audit(run: Path) -> dict:
    from transformers import AutoTokenizer

    manifest = json.loads((run / "manifest.json").read_text())
    items = rows(run / "inputs.jsonl")
    tokenizer = AutoTokenizer.from_pretrained(manifest["model_path"], local_files_only=True)
    if len({r["item_id"] for r in items}) != len(items):
        raise ValueError("Duplicate item identifiers")
    duplicate_options = []
    token_boundaries = defaultdict(Counter)
    token_stream_mismatches = []
    for r in items:
        if len(set(r["candidates"])) != 4:
            groups = defaultdict(list)
            for i, candidate in enumerate(r["candidates"]):
                groups[candidate].append(i)
            duplicate_options.append({"item_id": r["item_id"], "source_key": r["source_key"],
                                      "duplicate_index_groups": [v for v in groups.values() if len(v) > 1]})
        null_p, null_s = null_prefix(r["target_language"], r["task"])
        for candidate_idx, candidate in enumerate(r["candidates"]):
            streams = []
            for kind, p, s in [("source", r["prefix"], r["suffix"]), ("null", null_p, null_s)]:
                encoded = tokenizer(p + candidate + s, return_offsets_mapping=True)
                start, end = len(p), len(p + candidate)
                offsets = encoded["offset_mapping"]
                key = ":".join((kind, r["source_language"], r["task"]))
                token_boundaries[key].update({"candidate_sequences": 1,
                    "prefix_crossing_sequences": int(any(a < start < b for a, b in offsets)),
                    "suffix_crossing_sequences": int(any(a < end < b for a, b in offsets))})
                streams.append([token for token, (a, b) in zip(encoded["input_ids"][1:], offsets[1:])
                                if b > start and a < end])
            if streams[0] != streams[1]:
                token_stream_mismatches.append({"item_id": r["item_id"], "candidate_index": candidate_idx})
    meaning = {(r["source_language"], r["lexeme_family_id"]): r for r in items if r["task"] == "meaning"}
    changed_context_candidates = [r["item_id"] for r in items if r["task"] == "context"
                                  and r["candidates"] != meaning[r["source_language"], r["lexeme_family_id"]]["candidates"]]
    chat = defaultdict(list)
    if (run / "chat_trials.jsonl").exists():
        for r in rows(run / "chat_trials.jsonl"):
            chat[r["source_language"] + ":" + r["task"]].append(r)
    chat_audit = {}
    for key, group in chat.items():
        masses = [sum(math.exp(lp) for lp in r["label_logps"]) for r in group]
        if not all(0 < mass < 1 + 1e-6 for mass in masses):
            raise ValueError("Invalid full-vocabulary probability mass")
        off = [r for r in group if r["unrestricted_argmax_token"] not in r["label_token_ids"]]
        chat_audit[key] = {"n_rotations": len(group), "mean_label_probability_mass": sum(masses) / len(masses),
            "min_label_probability_mass": min(masses), "off_label_argmax_count": len(off),
            "off_label_argmax_tokens": dict(Counter(tokenizer.decode([r["unrestricted_argmax_token"]]) for r in off)),
            "restricted_position_choices": dict(Counter("ABCD"[max(range(4), key=r["label_logps"].__getitem__)] for r in group))}
    generations = rows(run / "generations.jsonl") if (run / "generations.jsonl").exists() else []
    config = json.loads((Path(manifest["model_path"]) / "generation_config.json").read_text())
    eos = config["eos_token_id"]
    eos = [eos] if isinstance(eos, int) else eos
    inconsistent_stops = [r["item_id"] for r in generations if not r["hit_token_limit"]
                          and (not r["generated_token_ids"] or r["generated_token_ids"][-1] not in eos)]
    result = {"model_id": manifest["model_id"], "run_status_at_audit": manifest["status"],
              "duplicate_candidate_rows": duplicate_options, "token_boundaries": dict(token_boundaries),
              "source_null_candidate_token_stream_mismatches": token_stream_mismatches,
              "meaning_context_distractor_changes": changed_context_candidates,
              "chat_full_vocabulary_audit": chat_audit,
              "generation": {"n": len(generations), "eos_ids": eos,
                  "hit_token_limit": [r["item_id"] for r in generations if r["hit_token_limit"]],
                  "inconsistent_stops": inconsistent_stops},
              "interpretation": "Token/format audit only; no new semantic labels or causal conclusions. PMA uses full-vocabulary label log probabilities without ABCD renormalization."}
    (run / "measurement_audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path)
    for run in parser.parse_args().runs:
        result = audit(run)
        print(run, result["run_status_at_audit"], "duplicate rows", len(result["duplicate_candidate_rows"]),
              "source-null token mismatches", len(result["source_null_candidate_token_stream_mismatches"]))
        for key, value in result["chat_full_vocabulary_audit"].items():
            print(key, "PMA", value["mean_label_probability_mass"], "off-label", value["off_label_argmax_count"])


if __name__ == "__main__":
    main()
