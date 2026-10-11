#!/usr/bin/env python3
"""Descriptive diagnostics for two-order A/B source-gloss LLM pilots; NOT a semantic test."""
from __future__ import annotations
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path


def audit_scores(rows: list[dict], threshold: float=2.0) -> dict:
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    grouped=defaultdict(list)
    for r in rows:
        keys=("source_id","host_language","context_strength","cue","correct_as_a",
              "correct_minus_foil_margin")
        for key in keys:
            if key not in r:
                raise ValueError(f"missing {key}")
        score=float(r["correct_minus_foil_margin"])
        if not math.isfinite(score):
            raise ValueError("nonfinite margin")
        grouped[tuple(r[k] for k in keys[:4])].append(r)
    if not grouped:
        raise ValueError("empty input")
    pairs=[]
    for key, recs in sorted(grouped.items()):
        if len(recs)!=2 or {x["correct_as_a"] for x in recs}!={True,False}:
            raise ValueError(f"incomplete A/B pair for {key}")
        ma=float(next(x for x in recs if x["correct_as_a"])["correct_minus_foil_margin"])
        mb=float(next(x for x in recs if not x["correct_as_a"])["correct_minus_foil_margin"])
        pairs.append(dict(source_id=key[0],host_language=key[1],strength=key[2],cue=key[3],
                          form=recs[0].get("form"),as_A_margin=ma,as_B_margin=mb,
                          mean_margin=(ma+mb)/2,absolute_order_gap=abs(ma-mb),
                          sign_reversal=(ma*mb<0)))
    return {
        "status":"EXPLORATORY_ORDER_INSTRUMENT_NOT_SCIENCE",
        "n_trials":len(rows),"n_pairs":len(pairs),
        "n_sign_reversals":sum(x["sign_reversal"] for x in pairs),
        "order_gap_threshold_nats":threshold,
        "n_order_gaps_above_threshold":sum(x["absolute_order_gap"]>threshold for x in pairs),
        "mean_abs_order_gap_nats":sum(x["absolute_order_gap"] for x in pairs)/len(pairs),
        "max_abs_order_gap_nats":max(x["absolute_order_gap"] for x in pairs),
        "pair_details":pairs,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    data=[json.loads(v) for v in a.input.read_text(encoding="utf-8").splitlines() if v.strip()]
    res=audit_scores(data)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in res.items() if k!="pair_details"},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
