#!/usr/bin/env python3
"""Check Type-1 adapter against original source runners without model inference."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import nullcontext
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

try:
    from scripts.run_doppelganger_diagnostics import records, digest
except ModuleNotFoundError:
    from run_doppelganger_diagnostics import records, digest


def audit(source: Path) -> dict:
    source = source.resolve()
    items = records(source)
    captured = []

    class Inputs(dict):
        def to(self, device):
            return self

    class Tokenizer:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()

        def __call__(self, text, **kwargs):
            captured.append(text)
            return Inputs(input_ids=[0])

    class Model:
        device = "mock"

        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()

        def __call__(self, **kwargs):
            return SimpleNamespace(loss=SimpleNamespace(item=lambda: 0.0))

    real_open = open

    def safe_open(path, mode="r", *args, **kwargs):
        if str(path).startswith("ppl/"):
            return io.StringIO()
        return real_open(path, mode, *args, **kwargs)

    comparisons = []
    original_cwd = Path.cwd()
    sys.path.insert(0, str(source))
    old_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        os.chdir(source)
        for task, name in [("meaning", "calc_ppl_meaning.py"), ("context", "calc_ppl_meaning_context.py"),
                           ("translation", "calc_ppl_translation.py")]:
            spec = importlib.util.spec_from_file_location("audited_source", source / name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            original_loader = getattr(module, "loadQADataset", None)
            if task == "meaning":
                def repaired_loader(path, cognate_type, lang):
                    data = original_loader(path, cognate_type, lang)
                    for key, entry in data.items():
                        own_field = "word_ja" if lang == "jp" else "word_zh"
                        assert own_field not in entry
                        entry[own_field] = key
                    return data
                module.loadQADataset = repaired_loader
            for lang in ("jp", "zh"):
                captured.clear()
                with patch.dict(sys.modules, {
                    "transformers": SimpleNamespace(AutoTokenizer=Tokenizer, AutoModelForCausalLM=Model),
                    "torch": SimpleNamespace(bfloat16="mock", no_grad=nullcontext),
                }), patch("builtins.open", safe_open), patch("os.makedirs", lambda *a, **k: None):
                    if task == "translation":
                        module.calculatePerplexity("mock/model", lang, "zh" if lang == "jp" else "jp", "homographs")
                    else:
                        module.calculatePerplexity("mock/model", lang, "homographs")
                expected = [text for r in items if r["task"] == task and r["source_language"] == lang for text in r["texts"]]
                if captured != expected:
                    mismatch = next((i for i, (a, b) in enumerate(zip(captured, expected)) if a != b), None)
                    raise AssertionError(f"Source prompt mismatch {task}/{lang}: {mismatch}, counts {len(captured)}/{len(expected)}")
                comparisons.append({"task": task, "source_language": lang, "n_candidate_texts": len(expected),
                                    "exact_match": True, "texts_sha256": digest(json.dumps(expected, ensure_ascii=False))})
    finally:
        os.chdir(original_cwd)
        sys.path.remove(str(source))
        sys.dont_write_bytecode = old_bytecode
    copy_rule = []
    for lang in ("jp", "zh"):
        rows = [r for r in items if r["source_language"] == lang and r["task"] == "translation"]
        copy_rule.append({"source_language": lang, "n": len(rows),
                          "correct_contains_target": [r["item_id"] for r in rows if r["source_key"] in r["candidates"][0]],
                          "wrong1_lacks_target": [r["item_id"] for r in rows if r["source_key"] not in r["candidates"][1]]})
    return {"source_prompt_comparisons": comparisons, "copy_rule_checks": copy_rule,
            "n_lexical_families": len({r["lexeme_family_id"] for r in items}),
            "checks_only": "Exact source text equivalence with disclosed WM key repair; no model or semantic validation."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = audit(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result["source_prompt_comparisons"], indent=2))
    print("Copy checks", [(r["source_language"], len(r["correct_contains_target"]), r["n"]) for r in result["copy_rule_checks"]])


if __name__ == "__main__":
    main()
