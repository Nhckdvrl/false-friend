#!/usr/bin/env python3
"""Separate semantic content, rule mapping, option stability and language conditions."""
from collections import defaultdict
import argparse
import json
import math
from pathlib import Path
import re
try:
    from scripts.analyze_doppelganger_diagnostics import bootstrap
except ModuleNotFoundError:
    from analyze_doppelganger_diagnostics import bootstrap


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def key(row):
    return tuple(row[k] for k in ("item_id", "representation", "task", "mapping", "explanation_language"))


def analyze(run):
    raw = rows(run / "trials.jsonl")
    grouped = defaultdict(list)
    for row in raw:
        grouped[key(row)].append(row)
    decisions = []
    for k, rr in grouped.items():
        assert len(rr) == 2 and {r["rotation"] for r in rr} == {0, 1}
        scores = [0.0, 0.0]
        choices = []
        for row in rr:
            choices.append(row["content_order"][max(range(2), key=row["label_logps"].__getitem__)])
            for j, content in enumerate(row["content_order"]):
                scores[content] += row["label_logps"][j] / 2
        r = rr[0]
        pred = max(range(2), key=scores.__getitem__)
        gold = r["correct_index"]
        d = {f:r[f] for f in ("item_id", "lexeme_family_id", "lexeme", "group", "source_language", "sense_index", "representation", "task", "mapping", "explanation_language", "correct_index", "original_label_index")}
        d.update({"prediction": pred, "predicted_sense": pred ^ (r["mapping"] if r["task"] == "rule" else 0),
                  "correct": pred == gold if gold is not None else None,
                  "original_label_agreement": pred == r["original_label_index"],
                  "rotation_choices": choices, "stable": len(set(choices)) == 1,
                  "all_orders_correct": all(p == gold for p in choices) if gold is not None else None,
                  "exact_score_tie": scores[0] == scores[1],
                  "content_logps": scores, "original_label_margin": scores[r["original_label_index"]] - scores[1-r["original_label_index"]]})
        decisions.append(d)
    groups = defaultdict(list)
    for r in decisions:
        groups[(r["group"], r["representation"], r["task"], r["explanation_language"])].append(r)
    summaries = []
    for (group, representation, task, language), rr in groups.items():
        metrics = {}
        for metric in ("correct", "all_orders_correct", "original_label_agreement", "stable", "original_label_margin"):
            vals = defaultdict(list)
            for r in rr:
                if r[metric] is not None:
                    vals[r["lexeme_family_id"]].append(float(r[metric]))
            metrics[metric] = bootstrap(vals)
        summaries.append({"group": group, "representation": representation, "task": task,
                          "explanation_language": language, "n_decisions": len(rr), "metrics": metrics})
    lookup = {key(r):r for r in decisions}
    pairs = defaultdict(lambda: defaultdict(list))
    flips = []
    for r in decisions:
        if r["explanation_language"] != "English":
            continue
        other = lookup[key(r)[:-1] + ("German",)]
        vals = pairs[(r["group"], r["representation"], r["task"])]
        if r["correct"] is not None:
            vals[r["lexeme_family_id"]].append(float(other["correct"]) - float(r["correct"]))
        if r["prediction"] != other["prediction"]:
            flips.append({"English": r, "German": other})
    contrasts = [{"group":k[0], "representation":k[1], "task":k[2], "German_minus_English":bootstrap(v)} for k,v in pairs.items()]
    mappings = []
    for r in decisions:
        if r["task"] != "rule" or r["mapping"] != 0:
            continue
        other = lookup[(r["item_id"],r["representation"],"rule",1,r["explanation_language"])]
        sense = lookup[(r["item_id"],r["representation"],"sense",0,r["explanation_language"])]
        mappings.append({"item_id":r["item_id"], "lexeme_family_id":r["lexeme_family_id"], "group":r["group"],
                         "representation":r["representation"], "explanation_language":r["explanation_language"],
                         "sense_prediction":sense["prediction"], "sense_all_orders_correct":sense["all_orders_correct"],
                         "rule_implied_senses":[r["predicted_sense"],other["predicted_sense"]],
                         "rule_same_sense_under_both_mappings":r["predicted_sense"] == other["predicted_sense"],
                         "rule_both_mappings_all_orders_correct":r["all_orders_correct"] and other["all_orders_correct"]})
    generation_checks = []
    if (run / "generations.jsonl").exists():
        for r in rows(run / "generations.jsonl"):
            if r["generation_task"] != "rule_explanation":
                continue
            match = re.match(r'^\s*[\*"\']*([AB])(?:\b|[).:\s])',r["generated"])
            letter = match.group(1) if match else None
            choice = r["content_order"]["AB".index(letter)] if letter else None
            generation_checks.append({"item_id":r["item_id"], "lexeme_family_id":r["lexeme_family_id"],
                                      "representation":r["representation"], "explanation_language":r["explanation_language"],
                                      "mapping":r["mapping"], "letter":letter, "choice":choice,
                                      "correct":choice == r["correct_index"] if choice is not None else None,
                                      "hit_token_limit":r["hit_token_limit"], "explanation_language_status":"UNREVIEWED",
                                      "explanation_semantics":"UNREVIEWED"})
    masses = [sum(math.exp(lp) for lp in r["label_logps"]) for r in raw]
    summary = {"manifest_status":json.loads((run/'manifest.json').read_text())["status"],
               "n_trials":len(raw), "n_families":len({r['lexeme_family_id'] for r in raw}), "groups":summaries,
               "contrasts":contrasts, "n_language_choice_flips":len(flips),
               "format_audit":{"mean_label_mass":sum(masses)/len(masses), "min_label_mass":min(masses),
                               "off_label_argmax":sum(r['unrestricted_argmax_token'] not in r['label_token_ids'] for r in raw)},
               "interpretation":"Family-level exploratory comparisons. Masked agreement is recoverability of original labels, not semantic correctness. Conditional answer scores are not hidden-state posteriors."}
    for name,data in [("decisions.jsonl",decisions),("language_flips.jsonl",flips),("mapping_checks.jsonl",mappings),("generation_checks.jsonl",generation_checks)]:
        (run/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in data))
    (run/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(run,summary['manifest_status'],summary['format_audit'],'language flips',len(flips))
    for row in summaries:
        if row['representation']=='original':
            m=row['metrics'];print(row['group'],row['task'],row['explanation_language'],
                                  'correct',round(m['correct']['mean'],3),'all-orders',round(m['all_orders_correct']['mean'],3))
    return summary


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('runs',nargs='+',type=Path)
    for run in ap.parse_args().runs: analyze(run)
