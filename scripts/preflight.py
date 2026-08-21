#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from false_friend_lab.io import read_jsonl

def main():
    p=argparse.ArgumentParser(description="Fail-fast scientific invariant checks before allocating GPUs"); p.add_argument("--data",default="data/processed/en_de"); p.add_argument("--min-words-per-relation",type=int,default=10); p.add_argument("--max-eval-unk-fraction",type=float,default=0.05); args=p.parse_args(); d=Path(args.data)
    req=["metadata.json","targets.csv","contexts.jsonl","train_en.npy","train_de.npy","train_en_exact_mask.npy","train_de_exact_mask.npy","base_to_compact.npy","compact_to_base.npy"]; missing=[x for x in req if not (d/x).exists()]
    if missing: raise SystemExit(f"PRECHECK FAIL missing files: {missing}")
    meta=json.load(open(d/"metadata.json",encoding="utf-8")); targets=pd.read_csv(d/"targets.csv"); contexts=read_jsonl(d/"contexts.jsonl"); problems=[]
    if int(meta.get("schema_version",0))<2: problems.append("old data schema; rerun prepare.py")
    if not meta.get("pair_level_holdout"): problems.append("holdout is not parallel-pair level")
    if not meta.get("strict_exact_lexical_mask"): problems.append("strict lexical occurrence mask missing")
    if float(meta.get("eval_unk_fraction",1.0))>args.max_eval_unk_fraction: problems.append(f"eval unk fraction too high: {meta.get('eval_unk_fraction')}")
    V=int(meta["compact_vocab_size"])
    if targets.compact_token_id.duplicated().any(): problems.append("target compact ids are not unique")
    if not ((targets.compact_token_id>=0)&(targets.compact_token_id<V)).all(): problems.append("target id outside compact vocab")
    target_ids=set(map(int,targets.compact_token_id.tolist()))
    for relation in ["false_friend","true_friend"]:
        n=int((targets.relation==relation).sum())
        if n<args.min_words_per_relation: problems.append(f"only {n} {relation} words")
    observed={"en":Counter(),"de":Counter()}
    for lang in ("en","de"):
        arr=np.load(d/f"train_{lang}.npy",mmap_mode="r"); m=np.load(d/f"train_{lang}_exact_mask.npy",mmap_mode="r")
        if len(arr)!=len(m): problems.append(f"{lang} stream/mask length mismatch"); continue
        if len(arr)<1000: problems.append(f"{lang} stream unexpectedly small")
        marked=np.asarray(arr[np.asarray(m,dtype=bool)],dtype=int)
        for tid in marked:
            if int(tid) in target_ids: observed[lang][int(tid)]+=1
        if int(arr.max())>=V or int(arr.min())<0: problems.append(f"{lang} token id out of range")
    for row in targets.itertuples(index=False):
        tid=int(row.compact_token_id)
        if observed["en"][tid]!=int(row.train_count_en): problems.append(f"EN exact count mismatch for {row.word}")
        if observed["de"][tid]!=int(row.train_count_de): problems.append(f"DE exact count mismatch for {row.word}")
    clean=[]
    for r in contexts:
        ids=list(map(int,r["compact_ids"])); mask=list(map(int,r["exact_mask"])); pos=int(r["target_position"]); ok=len(ids)==len(mask) and sum(mask)==1 and 0<=pos<len(ids) and mask[pos]==1 and ids[pos]==int(r["compact_target_id"])
        if not ok: problems.append(f"invalid eval context {r.get('context_id')}")
        else: clean.append(r)
    cells=Counter((r["relation"],r["lang"]) for r in clean); word_lang={(r["relation"],r["word"],r["lang"]) for r in clean}; both=Counter()
    for relation in ["false_friend","true_friend"]:
        words=set(targets[targets.relation==relation].word); both[relation]=sum((relation,w,"en") in word_lang and (relation,w,"de") in word_lang for w in words)
        if both[relation]<args.min_words_per_relation: problems.append(f"only {both[relation]} {relation} words have held-out contexts in BOTH languages")
    report={"status":"FAIL" if problems else "PASS","metadata":meta,"relation_counts":targets.relation.value_counts().to_dict(),"context_cells":{f"{a}/{b}":n for (a,b),n in cells.items()},"both_language_words":dict(both),"problems":problems}; print(json.dumps(report,indent=2,default=str))
    if problems: raise SystemExit("PRECHECK FAIL: do not allocate scientific GPUs until fixed")
if __name__=="__main__": main()
