#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from transformers import GPT2LMHeadModel


def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("shared"); p.add_argument("split"); a=p.parse_args()
    sdir,qdir=Path(a.shared),Path(a.split); sm=json.load(open(sdir/"run_meta.json",encoding="utf-8")); qm=json.load(open(qdir/"run_meta.json",encoding="utf-8"))
    for key in ["seed","schedule","config_hash","data_fingerprint","effective_batch_size","git_commit","init_sha256"]:
        if sm[key]!=qm[key]: raise SystemExit(f"STEP0 META FAIL: {key}: {sm[key]} != {qm[key]}")
    if sm["condition"]!="shared" or qm["condition"]!="split": raise SystemExit("STEP0 META FAIL: expected shared then split checkpoint")
    m1=GPT2LMHeadModel.from_pretrained(sdir,map_location="cpu"); m2=GPT2LMHeadModel.from_pretrained(qdir,map_location="cpu"); s1,s2=m1.state_dict(),m2.state_dict(); bad=[]
    for key in s1:
        if key not in s2 or not torch.equal(s1[key],s2[key]): bad.append(key)
    if bad: raise SystemExit(f"STEP0 IDENTITY FAIL: {bad[:20]} ({len(bad)} tensors)")
    print(f"PASS: metadata matched and {len(s1)} tensors are exactly identical")


if __name__=="__main__": main()
