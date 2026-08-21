#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from false_friend_lab.io import read_jsonl

def main() -> None:
    p=argparse.ArgumentParser(description="Fail-fast validation before allocating GPUs")
    p.add_argument("--data",default="data/processed/en_de"); p.add_argument("--min-words-per-relation",type=int,default=10); p.add_argument("--min-contexts-per-cell",type=int,default=10); args=p.parse_args()
    d=Path(args.data); required=["metadata.json","targets.csv","contexts.jsonl","train_en.npy","train_de.npy","base_to_compact.npy","compact_to_base.npy"]
    missing=[x for x in required if not (d/x).exists()]
    if missing: raise SystemExit(f"PRECHECK FAIL: missing files: {missing}")
    meta=json.load(open(d/"metadata.json",encoding="utf-8")); targets=pd.read_csv(d/"targets.csv"); contexts=read_jsonl(d/"contexts.jsonl"); problems=[]
    for relation in ["false_friend","true_friend"]:
        n=int((targets.relation==relation).sum())
        if n<args.min_words_per_relation: problems.append(f"only {n} lexical items for {relation} (<{args.min_words_per_relation})")
    if targets["compact_token_id"].duplicated().any(): problems.append("target compact token ids are not unique")
    V=int(meta["compact_vocab_size"])
    if not ((targets.compact_token_id>=0)&(targets.compact_token_id<V)).all(): problems.append("target compact token id outside base vocabulary")
    cells=Counter((r["relation"],r["lang"]) for r in contexts)
    for relation in ["false_friend","true_friend"]:
        for lang in ["en","de"]:
            if cells[(relation,lang)]<args.min_contexts_per_cell: problems.append(f"only {cells[(relation,lang)]} held-out contexts for {relation}/{lang}")
    for lang in ["en","de"]:
        arr=np.load(d/f"train_{lang}.npy",mmap_mode="r")
        if len(arr)<1000: problems.append(f"{lang} training stream unexpectedly small: {len(arr)} tokens")
        if int(arr.max())>=V or int(arr.min())<0: problems.append(f"{lang} stream contains id outside compact vocabulary")
    report={"status":"FAIL" if problems else "PASS","metadata":meta,"relation_counts":targets.relation.value_counts().to_dict(),"context_cells":{f"{k[0]}/{k[1]}":v for k,v in cells.items()},"frequency_summary":targets.groupby("relation")[["train_count_en","train_count_de"]].describe().to_dict(),"problems":problems}
    print(json.dumps(report,indent=2,default=str))
    if problems: raise SystemExit("PRECHECK FAIL: do not allocate GPUs until fixed")
if __name__=="__main__": main()
