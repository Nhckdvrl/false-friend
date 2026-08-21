#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json
from pathlib import Path
import numpy as np
import pandas as pd

def boot(vals,n=10000,seed=1234):
    vals=np.asarray(vals,float); vals=vals[np.isfinite(vals)]
    if len(vals)<2:return {"mean":float(np.nanmean(vals)),"ci95_low":float("nan"),"ci95_high":float("nan"),"n_words":int(len(vals))}
    rng=np.random.default_rng(seed); z=np.array([rng.choice(vals,len(vals),replace=True).mean() for _ in range(n)]); return {"mean":float(vals.mean()),"ci95_low":float(np.quantile(z,.025)),"ci95_high":float(np.quantile(z,.975)),"n_words":int(len(vals))}
def main():
    p=argparse.ArgumentParser(); p.add_argument("--inputs",nargs="+",required=True); p.add_argument("--output",default="results/path_dependence.json"); args=p.parse_args(); paths=[]
    for x in args.inputs:
        m=glob.glob(x); paths.extend(m if m else [x])
    frames=[pd.read_csv(x) for x in paths if Path(x).exists()]
    if not frames: raise SystemExit("no rows")
    df=pd.concat(frames,ignore_index=True); mx=df.groupby(["schedule","condition","seed"])["update"].transform("max"); df=df[df["update"]==mx]; x=df.groupby(["condition","schedule","seed","relation","word","lang"],as_index=False)["local_post"].mean(); nlang=x.groupby(["condition","schedule","seed","relation","word"])["lang"].nunique().rename("n_lang").reset_index(); x=x.merge(nlang,on=["condition","schedule","seed","relation","word"]); x=x[x.n_lang==2]; x=x.groupby(["condition","schedule","seed","relation","word"],as_index=False)["local_post"].mean(); out={}; effects={}
    for cond in ["shared","split"]:
        for rel in ["false_friend","true_friend"]:
            a=x[(x.condition==cond)&(x.relation==rel)&(x.schedule=="en_then_de")].set_index(["seed","word"]).local_post; b=x[(x.condition==cond)&(x.relation==rel)&(x.schedule=="de_then_en")].set_index(["seed","word"]).local_post; common=a.index.intersection(b.index); d=(a.loc[common]-b.loc[common]).rename("delta").reset_index(); wd=d.groupby("word").delta.mean(); effects[(cond,rel)]=wd; out[f"order_effect:{cond}:{rel}"]=boot(wd.to_numpy(),seed=1300+len(out))
    for rel in ["false_friend","true_friend"]:
        a=effects.get(("shared",rel),pd.Series(dtype=float)); b=effects.get(("split",rel),pd.Series(dtype=float)); common=a.index.intersection(b.index); out[f"sharing_specific_order_effect:{rel}"]=boot((a.loc[common]-b.loc[common]).to_numpy(),seed=1500+len(out))
    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2),encoding="utf-8"); print(json.dumps(out,indent=2))
if __name__=="__main__": main()
