#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd


def boot_matrix(frame, value, n=10000, seed=1234):
    pv=frame.pivot(index="word",columns="seed",values=value)
    if pv.empty or pv.isna().any().any(): raise ValueError(f"incomplete word×seed matrix for {value}")
    arr=pv.to_numpy(float); rng=np.random.default_rng(seed); vals=np.empty(n)
    for i in range(n):
        wi=rng.integers(0,arr.shape[0],arr.shape[0]); si=rng.integers(0,arr.shape[1],arr.shape[1]); vals[i]=arr[np.ix_(wi,si)].mean()
    return {"mean":float(arr.mean()),"ci95_low":float(np.quantile(vals,.025)),"ci95_high":float(np.quantile(vals,.975)),"n_words":int(arr.shape[0]),"n_seeds":int(arr.shape[1])}


def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--inputs",nargs="+",required=True); p.add_argument("--output",default="results/path_dependence.json"); p.add_argument("--bootstrap",type=int,default=10000); a=p.parse_args()
    paths=[]
    for q in a.inputs: paths.extend(glob.glob(q) or [q])
    frames=[pd.read_csv(q) for q in paths if Path(q).exists()]
    if not frames: raise SystemExit("no path-evaluation rows")
    d=pd.concat(frames,ignore_index=True)
    required_schedules={"en_then_de","de_then_en"}
    if set(d.schedule.unique())!=required_schedules: raise ValueError(f"path analysis requires exactly {required_schedules}")
    for col in ["data_fingerprint","config_hash","effective_batch_size","git_commit"]:
        if d[col].nunique()!=1: raise ValueError(f"path runs mix {col}")
    terminal=d.groupby(["schedule","condition","seed"])["step"].max()
    if terminal.nunique()!=1: raise ValueError(f"path runs have unequal terminal updates: {sorted(terminal.unique())}")
    final_step=int(terminal.iloc[0]); d=d[d.step==final_step].copy()
    if set(d.condition.unique())!={"shared","split"}: raise ValueError("path analysis requires shared and split")
    if d.training_gpu_name.nunique()!=1: raise ValueError("path gate mixes GPU models; rerun on one hardware type")
    d["local"]=d.post_nll-d.pre_nll
    ctx=d.groupby(["condition","schedule","seed","relation","word","lang","base_context_id"],as_index=False)["local"].mean()
    lang=ctx.groupby(["condition","schedule","seed","relation","word","lang"],as_index=False)["local"].mean()
    ws=lang.groupby(["condition","schedule","seed","relation","word"],as_index=False)["local"].mean()
    orders=[]
    for cond in ["shared","split"]:
        z=ws[ws.condition==cond]; aa=z[z.schedule=="en_then_de"].set_index(["relation","word","seed"]).local.sort_index(); bb=z[z.schedule=="de_then_en"].set_index(["relation","word","seed"]).local.sort_index()
        if not aa.index.equals(bb.index): raise ValueError(f"path schedule coverage differs inside {cond}")
        q=(aa-bb).rename("order_effect").reset_index(); q["condition"]=cond; orders.append(q)
    order=pd.concat(orders,ignore_index=True); sh=order[order.condition=="shared"].set_index(["relation","word","seed"]).order_effect.sort_index(); sp=order[order.condition=="split"].set_index(["relation","word","seed"]).order_effect.sort_index()
    if not sh.index.equals(sp.index): raise ValueError("shared/split path coverage differs")
    inter=(sh-sp).rename("sharing_specific_order_effect").reset_index(); out={"terminal_step":final_step}
    for rel in ["false_friend","true_friend"]: out[rel]=boot_matrix(inter[inter.relation==rel],"sharing_specific_order_effect",a.bootstrap,1234+len(out))
    out["interpretation"]="(EN→DE - DE→EN)_shared minus (EN→DE - DE→EN)_split final local-continuation effect after the identical balanced tail"
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(out,indent=2),encoding="utf-8"); print(json.dumps(out,indent=2))


if __name__=="__main__": main()
