#!/usr/bin/env python3
"""Cross requested explanation language with semantic selection and rule application."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import time

try:
    from scripts.run_doppelganger_diagnostics import score_labels, generate_records, digest
except ModuleNotFoundError:
    from run_doppelganger_diagnostics import score_labels, generate_records, digest


def selected_generation_families(items):
    chosen = []
    for group in sorted({r["group"] for r in items}):
        families = {r["lexeme_family_id"] for r in items if r["group"] == group}
        chosen += sorted(families, key=lambda x: digest("output-cycle-20261013:" + x))[:4]
    return chosen


def build_trials(items, template_kwargs=None):
    trials = []
    for item in items:
        for representation, context in item["contexts"].items():
            for task in ("sense", "rule"):
                for mapping in ([0] if task == "sense" else [0, 1]):
                    codes = ["Cedar", "Maple"] if mapping == 0 else ["Maple", "Cedar"]
                    gold = item["sense_index"] if task == "sense" else (item["sense_index"] ^ mapping)
                    choices = item["definitions"] if task == "sense" else ["Cedar", "Maple"]
                    for explanation_language in ("none", "English", "German"):
                        for rotation, order in enumerate(([0, 1], [1, 0])):
                            language = {"de": "German", "en": "English"}[item["source_language"]]
                            prefix = f"The quoted sentence is in {language}. Interpret the meaning conveyed by its bracketed expression. Use the local literal reading, not every property the referent might have.\nText: {context}\n"
                            if task == "sense":
                                question = "Which meaning is conveyed by the bracketed expression?"
                            else:
                                question = ("Apply this logging rule to the meaning conveyed by the bracketed expression:\n"
                                            f"If it means {item['definitions'][0]}, record code {codes[0]}.\n"
                                            f"If it means {item['definitions'][1]}, record code {codes[1]}.\n"
                                            "Which code must be recorded?")
                            options = "\n".join(f"{label}) {choices[index]}" for label, index in zip("AB", order))
                            instruction = ("Reply with only the correct option letter (A or B)." if explanation_language == "none" else
                                           f"Start with the correct option letter (A or B), then explain your choice in one sentence in {explanation_language}.")
                            trials.append({**item, "representation": representation, "task": task,
                                           "mapping": mapping, "explanation_language": explanation_language,
                                           "rotation": rotation, "content_order": order, "label_names": "AB",
                                           "correct_index": gold if representation != "masked" else None,
                                           "original_label_index": gold, "chat_template_kwargs": template_kwargs or {},
                                           "prompt": prefix + question + "\n" + options + "\n" + instruction})
    return trials


def generation_specs(items, trials):
    families = selected_generation_families(items)
    specs = []
    for r in trials:
        # Fixed, pre-output, balanced mapping assignment; generations are a subset
        # of already specified prompts, not selected on label errors.
        assigned = int(digest(r["item_id"])[0], 16) % 2
        if (r["lexeme_family_id"] in families and r["task"] == "rule" and r["representation"] != "masked"
                and r["explanation_language"] != "none" and r["mapping"] == assigned and r["rotation"] == 0):
            specs.append({**r, "generation_task": "rule_explanation"})
    for item in items:
        language = {"de": "German", "en": "English"}[item["source_language"]]
        specs.append({**item, "generation_task": "independent_gloss", "representation": "original", "explanation_language": "English",
                      "chat_template_kwargs": trials[0]["chat_template_kwargs"],
                      "prompt": f"The following sentence is in {language}. Explain the meaning of its bracketed expression in one short English sentence.\n{item['contexts']['original']}"})
    return specs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--items", type=Path, required=True)
    ap.add_argument("--model-path", type=Path, required=True)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--generation-batch-size", type=int, default=8)
    ap.add_argument("--disable-thinking", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    items = [json.loads(line) for line in args.items.read_text().splitlines()]
    kwargs = {"enable_thinking": False} if args.disable_thinking else {}
    trials = build_trials(items, kwargs)
    generations = generation_specs(items, trials)
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = {"status": "PREPARED" if args.dry_run else "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
                "protocol": "output-language-cycle-v1", "host": platform.node(),
                "model_id": args.model_id, "model_path": str(args.model_path), "model_revision": args.model_path.name,
                "tokenizer_revision": args.model_path.name, "chat_template_kwargs": kwargs,
                "items_sha256": digest(args.items.read_bytes()), "code_sha256": digest(Path(__file__).read_bytes()),
                "scorer_sha256": digest(Path(score_labels.__code__.co_filename).read_bytes()),
                "n_items": len(items), "n_families": len({r['lexeme_family_id'] for r in items}),
                "n_trials": len(trials), "n_generations": len(generations),
                "generation_families": selected_generation_families(items), "seed": 20261013,
                "batch_size": args.batch_size, "generation_batch_size": args.generation_batch_size,
                "dtype": "bfloat16", "attention": "sdpa", "max_new_tokens": 96,
                "cuda_visible_devices": os.getenv("CUDA_VISIBLE_DEVICES"),
                "interpretation": "New exploratory locally authored materials; no human gold. Masked has no unique semantic gold; original-label agreement may be described separately. Language instruction contrast does not alone separate priming from production planning."}
    def save_manifest():
        (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    save_manifest()
    (args.output / "items.jsonl").write_bytes(args.items.read_bytes())
    (args.output / "code_snapshot.py").write_bytes(Path(__file__).read_bytes())
    (args.output / "scorer_snapshot.py").write_bytes(Path(score_labels.__code__.co_filename).read_bytes())
    (args.output / "trial_specs.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in trials))
    if args.dry_run:
        print(json.dumps(manifest, indent=2)); return
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    start = time.monotonic()
    torch.set_num_threads(4)
    torch.manual_seed(20261013)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, local_files_only=True, trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model_path, torch_dtype=torch.bfloat16, local_files_only=True,
                                               trust_remote_code=False, device_map={"": "cuda:0"}, attn_implementation="sdpa").eval()
    manifest["environment"] = {"python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__}
    manifest["gpu"] = torch.cuda.get_device_name()
    manifest["chat_template_sha256"] = digest(tokenizer.chat_template or "")
    save_manifest()
    labels = score_labels(model, tokenizer, trials, args.batch_size)
    (args.output / "trials.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in labels))
    outputs = generate_records(model, tokenizer, generations, args.generation_batch_size, 96)
    (args.output / "generations.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in outputs))
    manifest.update({"status": "COMPLETE", "finished_utc": datetime.now(timezone.utc).isoformat(),
                     "elapsed_seconds": time.monotonic() - start, "peak_allocated_gb": torch.cuda.max_memory_allocated() / 1e9})
    save_manifest()
    print(f"Completed {args.output} in {manifest['elapsed_seconds']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
