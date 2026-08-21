#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import pandas as pd

METRICS = ["form_nll", "post_nll", "pre_nll"]
IDX = ["context_id", "base_context_id", "word", "relation", "lang", "seed", "schedule", "step"]


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--inputs", nargs="+", required=True); p.add_argument("--output", default="results/gate2_trajectory.csv"); a = p.parse_args()
    paths=[]
    for q in a.inputs: paths.extend(glob.glob(q) or [q])
    frames=[pd.read_csv(q) for q in paths if Path(q).exists()]
    if not frames: raise SystemExit("no input CSVs")
    d=pd.concat(frames,ignore_index=True)
    for col in ["data_fingerprint","config_hash","effective_batch_size","git_commit"]:
        if d[col].nunique()!=1: raise ValueError(f"trajectory mixes {col}")
    if d[IDX+["condition"]].duplicated().any(): raise ValueError("trajectory contains duplicate occurrence rows")
    sh=d[d.condition=="shared"].set_index(IDX).sort_index(); sp=d[d.condition=="split"].set_index(IDX).sort_index()
    if not sh.index.equals(sp.index): raise ValueError("trajectory shared/split checkpoint coverage is not exactly paired")
    x=sh[METRICS].add_suffix("_shared").join(sp[METRICS].add_suffix("_split")).reset_index()
    for m in METRICS: x[f"delta_{m}"]=x[f"{m}_shared"]-x[f"{m}_split"]
    x["delta_form_local"]=x.delta_form_nll-x.delta_pre_nll; x["delta_post_local"]=x.delta_post_nll-x.delta_pre_nll
    vals=["delta_form_nll","delta_post_nll","delta_pre_nll","delta_form_local","delta_post_local"]
    ctx=x.groupby(["schedule","step","seed","relation","word","lang","base_context_id"],as_index=False)[vals].mean()
    lang=ctx.groupby(["schedule","step","seed","relation","word","lang"],as_index=False)[vals].mean()
    ws=lang.groupby(["schedule","step","seed","relation","word"],as_index=False)[vals].mean()
    out=ws.groupby(["schedule","step","relation"],as_index=False)[vals].agg(["mean","std","count"])
    out.columns=["_".join(c).strip("_") if isinstance(c,tuple) else c for c in out.columns]; out=out.reset_index()
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); out.to_csv(a.output,index=False); print(out.to_string(index=False))


if __name__=="__main__": main()
