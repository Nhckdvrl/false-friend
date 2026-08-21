#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd


def paired_bootstrap(delta: np.ndarray, n: int, seed: int):
    delta = np.asarray(delta, dtype=float)
    delta = delta[np.isfinite(delta)]
    if len(delta) < 2:
        return float(np.nanmean(delta)), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    vals = np.empty(n)
    for i in range(n):
        vals[i] = rng.choice(delta, len(delta), replace=True).mean()
    return float(delta.mean()), float(np.quantile(vals, .025)), float(np.quantile(vals, .975))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", nargs="+", required=True)
    p.add_argument("--output", default="results/path_dependence.json")
    p.add_argument("--bootstrap", type=int, default=10000)
    args = p.parse_args()
    paths=[]
    for x in args.inputs:
        m=glob.glob(x); paths.extend(m if m else [x])
    frames=[pd.read_csv(x) for x in paths if Path(x).exists()]
    if not frames:
        raise SystemExit("no rows")
    df=pd.concat(frames, ignore_index=True)
    # Use only the latest checkpoint available for each schedule/condition/seed.
    max_steps=df.groupby(["schedule","condition","seed"])["step"].transform("max")
    df=df[df.step==max_steps].copy()
    # Path dependence is assessed only after the identical balanced tail.
    # Pair by lexical item and seed before bootstrapping words. This prevents
    # unequal item coverage or seed averaging from becoming an apparent path effect.
    out={}
    for condition in sorted(df.condition.unique()):
        d=df[df.condition==condition]
        for relation in ["false_friend","true_friend"]:
            for lang in ["en","de"]:
                sub=d[(d.relation==relation)&(d.lang==lang)]
                per_word_seed=(sub.groupby(["schedule","seed","word"], as_index=False)["post_nll"].mean())
                a=(per_word_seed[per_word_seed.schedule=="en_then_de"]
                   .set_index(["seed","word"])["post_nll"])
                b=(per_word_seed[per_word_seed.schedule=="de_then_en"]
                   .set_index(["seed","word"])["post_nll"])
                common=a.index.intersection(b.index)
                key=f"{condition}:{relation}:{lang}:post_nll_en_then_de_minus_de_then_en"
                if len(common) >= 2:
                    paired=(a.loc[common]-b.loc[common]).rename("delta").reset_index()
                    # Lexical item is the inferential unit; average paired seed effects within word.
                    word_delta=paired.groupby("word")["delta"].mean().to_numpy()
                    if len(word_delta) >= 2:
                        mean,lo,hi=paired_bootstrap(word_delta,args.bootstrap,1234+len(out))
                        out[key]={
                            "mean":mean,"ci95_low":lo,"ci95_high":hi,
                            "n_words":int(len(word_delta)),
                            "n_paired_word_seed":int(len(common)),
                        }
    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__ == "__main__":
    main()
