#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob
from pathlib import Path
import pandas as pd
METRICS=["surface_nll","lexical_nll","post_nll","pre_nll","local_surface","local_post"]
def main():
    p=argparse.ArgumentParser(); p.add_argument("--inputs",nargs="+",required=True); p.add_argument("--output",default="results/gate2_trajectory.csv"); args=p.parse_args(); paths=[]
    for x in args.inputs:
        m=glob.glob(x); paths.extend(m if m else [x])
    frames=[pd.read_csv(x) for x in paths if Path(x).exists()]
    if not frames: raise SystemExit("no input CSVs")
    df=pd.concat(frames,ignore_index=True); idx=["context_id","word","relation","lang","seed","schedule","update"]; s=df[df.condition=="shared"].set_index(idx); q=df[df.condition=="split"].set_index(idx); common=s.index.intersection(q.index); paired=s.loc[common,METRICS].add_suffix("_shared").join(q.loc[common,METRICS].add_suffix("_split")).reset_index()
    for m in METRICS: paired[f"delta_{m}"]=paired[f"{m}_shared"]-paired[f"{m}_split"]
    dcols=[f"delta_{m}" for m in METRICS]; x=paired.groupby(["schedule","update","seed","relation","word","lang"],as_index=False)[dcols].mean(); counts=x.groupby(["schedule","update","seed","relation","word"])["lang"].nunique().rename("n_lang").reset_index(); x=x.merge(counts,on=["schedule","update","seed","relation","word"]); x=x[x.n_lang==2]; x=x.groupby(["schedule","update","seed","relation","word"],as_index=False)[dcols].mean(); traj=x.groupby(["schedule","update","relation"],as_index=False)[dcols].agg(["mean","std","count"]).reset_index(); traj.columns=["_".join([str(c) for c in col if str(c)]) if isinstance(col,tuple) else col for col in traj.columns]; out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); traj.to_csv(out,index=False); print(traj.to_string(index=False))
if __name__=="__main__": main()
