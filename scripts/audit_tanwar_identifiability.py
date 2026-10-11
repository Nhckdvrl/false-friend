#!/usr/bin/env python3
"""Test observability of source-word language in Tanwar et al. Task3.

Source: https://github.com/EshaanT/Bilingual_processing_LLMs
Commit audited by CI: 281a67eac6ddbe5445e1c10277e5833d40d72125

This checks a measurement issue: when EN and L2 forms are *identical strings*,
cross-condition insertion of the "other-language" word into the host context
produces exactly the same visible sentence as a normal within-language word.
The source row index is hidden; it is not inferable from the sentence alone.
The ORIGINAL cross-condition instruction explicitly mentions code-mixing,
so the complete prompts are NOT observationally identical. This analysis
makes no claim that authors' free-text labels are scientifically invalid
in general, nor that the model's interpretation is wrong.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


TYPES = ("COGNATE", "FALSE COGNATE", "NON COGNATE")


def insert(sentence: str, word: str) -> str:
    if sentence.count("<MASK>") != 1:
        raise ValueError("Each context must contain exactly one <MASK> for a matched comparison")
    return sentence.replace("<MASK>", '"' + word + '"')


def audit_one(path: Path, l2: str) -> dict:
    fields = {"ID", "en", l2, "type", "lexical_category",
              "low_en", "high_en", f"low_{l2}", f"high_{l2}"}
    with path.open(encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        if not fields.issubset(set(reader.fieldnames or ())):
            raise ValueError(f"missing fields in {path.name}: {fields-set(reader.fieldnames or ())}")
        rows = list(reader)
    counter = Counter()
    examples = []
    for r in rows:
        label = r["type"].strip().upper()
        if label not in TYPES:
            raise ValueError(f"unknown source type {label!r}")
        en, other = r["en"].strip(), r[l2].strip()
        if not en or not other:
            raise ValueError("blank word")
        exact = en == other
        casefold_same = en.casefold() == other.casefold()
        counter["items"] += 1
        counter["type_"+label] += 1
        if exact:
            counter["exact_forms"] += 1
            counter["exact_type_"+label] += 1
        elif casefold_same:
            counter["case_only_forms"] += 1
            counter["case_only_type_"+label] += 1
        # Same host context, same surface, but different *source-language* row label.
        # Constructed as in Task3.get_test_prompts, with instruction excluded.
        for host in ("en", l2):
            cross_word = other if host == "en" else en
            ordinary_word = en if host == "en" else other
            for strength in ("low", "high"):
                sentence = r[f"{strength}_{host}"]
                ordinary = insert(sentence, ordinary_word)
                cross = insert(sentence, cross_word)
                counter["host_and_strength_comparisons"] += 1
                if ordinary == cross:
                    counter["sentence_observational_equivalences"] += 1
                    if len(examples) < 8 and label == "FALSE COGNATE":
                        examples.append({
                            "ID": r["ID"],
                            "type": label,
                            "host": host,
                            "strength": strength,
                            "form": ordinary_word,
                            "sentence": ordinary,
                            "source_language_is_not_distinguishable_from_sentence": True
                        })
    return {
        "file": path.name,
        "language_pair": "en-"+l2,
        "status": "SOURCE_ONLY_NOT_A_MODEL_EVALUATION",
        "counts": dict(sorted(counter.items())),
        "example_equivalences": examples,
        "interpretation": (
            "For identical orthographies, the source-language identity label does not follow "
            "from the sentence string alone. The original cross-condition TASK INSTRUCTION "
            "is different and explicitly indicates code mixing; that pragmatic difference "
            "can influence the model. This is a stimulus-identifiability warning, not "
            "an assertion about model correctness."
        )
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    a = ap.parse_args()
    report = [audit_one(a.source_dir/f"task3_en_{l2}.csv", l2) for l2 in ("de", "fr", "es")]
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    for r in report:
        c = r["counts"]
        print(r["file"], "items", c["items"],
              "strictly identical false cognates", c.get("exact_type_FALSE COGNATE", 0),
              "matched same-sentence source ambiguities", c["sentence_observational_equivalences"])
    print("Output", a.output)


if __name__ == "__main__":
    main()
