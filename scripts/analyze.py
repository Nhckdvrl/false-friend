#!/usr/bin/env python3
from __future__ import annotations

import argparse, glob, json
from pathlib import Path
from typing import Dict
import numpy as np
import pandas as pd

PRIMARY=["surface_nll","lexical_nll","post_nll","pre_nll","local_surface","local_post"]

def pair_rows(df):
    idx=["context_id","word","relation","lang","seed","schedule","update"]
    s=df[df.condition=="shared"].set_index(idx); p=df[df.condition=="split"].set_index(idx); common=s.index.intersection(p.index)
    if not len(common): raise ValueError("no paired shared/split rows")
    out=s.loc[common,PRIMARY].add_suffix("_shared").join(p.loc[common,PRIMARY].add_suffix("_split")).reset_index()
    for m in PRIMARY: out[f"delta_{m}"]=out[f"{m}_shared"]-out[f"{m}_split"]
    freq=df[["word","train_count_en","train_count_de"]].drop_duplicates("word"); return out.merge(freq,on="word",how="left")

def primary_word_seed(paired):
    dcols=[f"delta_{m}" for m in PRIMARY]
    x=paired.groupby(["seed","relation","word","lang"],as_index=False)[dcols].mean(); counts=x.groupby(["seed","relation","word"])["lang"].nunique().rename("n_lang").reset_index(); x=x.merge(counts,on=["seed","relation","word"]); x=x[x.n_lang==2]
    return x.groupby(["seed","relation","word"],as_index=False)[dcols].mean()

def crossed_bootstrap(frame,relation,metric,n,seed)->Dict[str,float]:
    sub=frame[frame.relation==relation].pivot(index="word",columns="seed",values=f"delta_{metric}").dropna()
    if sub.shape[0]<2 or sub.shape[1]<2: return {"mean":float("nan"),"ci95_low":float("nan"),"ci95_high":float("nan"),"n_words":int(sub.shape[0]),"n_seeds":int(sub.shape[1])}
    arr=sub.to_numpy(float); rng=np.random.default_rng(seed); vals=np.empty(n)
    for i in range(n):
        wi=rng.integers(0,arr.shape[0],arr.shape[0]); si=rng.integers(0,arr.shape[1],arr.shape[1]); vals[i]=arr[np.ix_(wi,si)].mean()
    return {"mean":float(arr.mean()),"ci95_low":float(np.quantile(vals,.025)),"ci95_high":float(np.quantile(vals,.975)),"n_words":int(arr.shape[0]),"n_seeds":int(arr.shape[1])}

def crossed_interaction(frame,metric,n,seed):
    piv={r:frame[frame.relation==r].pivot(index="word",columns="seed",values=f"delta_{metric}") for r in ["false_friend","true_friend"]}; seeds=sorted(set(piv["false_friend"].columns).intersection(piv["true_friend"].columns)); ff=piv["false_friend"][seeds].dropna().to_numpy(float); tf=piv["true_friend"][seeds].dropna().to_numpy(float)
    if ff.shape[0]<2 or tf.shape[0]<2 or len(seeds)<2: return {"mean":float("nan"),"ci95_low":float("nan"),"ci95_high":float("nan")}
    rng=np.random.default_rng(seed); vals=np.empty(n)
    for i in range(n):
        si=rng.integers(0,len(seeds),len(seeds)); fi=rng.integers(0,len(ff),len(ff)); ti=rng.integers(0,len(tf),len(tf)); vals[i]=ff[np.ix_(fi,si)].mean()-tf[np.ix_(ti,si)].mean()
    return {"mean":float(ff.mean()-tf.mean()),"ci95_low":float(np.quantile(vals,.025)),"ci95_high":float(np.quantile(vals,.975)),"n_false_friend":int(len(ff)),"n_true_friend":int(len(tf)),"n_seeds":int(len(seeds))}

def ols_beta(frame):
    y=frame.delta.to_numpy(float); ff=(frame.relation.to_numpy()=="false_friend").astype(float); total=np.log1p(frame.train_count_en.to_numpy(float)+frame.train_count_de.to_numpy(float)); ratio=np.abs(np.log((frame.train_count_en.to_numpy(float)+1)/(frame.train_count_de.to_numpy(float)+1))); X=np.column_stack([np.ones(len(frame)),ff,total,ratio]); return float(np.linalg.lstsq(X,y,rcond=None)[0][1])

def frequency_adjusted(frame,paired,n,seed):
    freq=paired[["word","relation","train_count_en","train_count_de"]].drop_duplicates(["word","relation"]); piv={r:frame[frame.relation==r].pivot(index="word",columns="seed",values="delta_local_post") for r in ["false_friend","true_friend"]}; seeds=sorted(set(piv["false_friend"].columns).intersection(piv["true_friend"].columns)); ff=piv["false_friend"][seeds].dropna(); tf=piv["true_friend"][seeds].dropna()
    def make(ff_df,tf_df,seed_idx=None):
        a=ff_df.mean(axis=1) if seed_idx is None else pd.Series(ff_df.to_numpy()[:,seed_idx].mean(axis=1),index=ff_df.index); b=tf_df.mean(axis=1) if seed_idx is None else pd.Series(tf_df.to_numpy()[:,seed_idx].mean(axis=1),index=tf_df.index); z=pd.concat([a.rename("delta").reset_index().assign(relation="false_friend"),b.rename("delta").reset_index().assign(relation="true_friend")]); return z.merge(freq,on=["word","relation"],how="left")
    if len(ff)<4 or len(tf)<4 or len(seeds)<2: return {"mean":float("nan"),"ci95_low":float("nan"),"ci95_high":float("nan")}
    estimate=ols_beta(make(ff,tf)); rng=np.random.default_rng(seed); vals=np.empty(n)
    for i in range(n):
        si=rng.integers(0,len(seeds),len(seeds)); fi=rng.integers(0,len(ff),len(ff)); ti=rng.integers(0,len(tf),len(tf)); vals[i]=ols_beta(make(ff.iloc[fi],tf.iloc[ti],si))
    return {"mean":estimate,"ci95_low":float(np.quantile(vals,.025)),"ci95_high":float(np.quantile(vals,.975)),"covariates":"log1p(total_frequency),abs(log((en+1)/(de+1)))"}

def seed_consistency(frame,relation,metric,sign):
    x=frame[frame.relation==relation].groupby("seed")[f"delta_{metric}"].mean(); return float("nan") if not len(x) else float((x<0).mean() if sign<0 else (x>0).mean())

def check_invariants(df):
    problems=[]
    if df["update"].nunique()!=1: problems.append(f"mixed checkpoint updates: {sorted(df['update'].unique())}")
    for seed in sorted(df.seed.unique()):
        d=df[df.seed==seed]
        if set(d.condition.unique())!={"shared","split"}: problems.append(f"seed {seed} missing paired condition"); continue
        for field in ["init_sha256","effective_batch_size","gpu_name","git_commit","data_schema_version"]:
            vals=set(map(str,d[field].dropna().unique()))
            if len(vals)!=1: problems.append(f"seed {seed} shared/split mismatch in {field}: {vals}")
    return problems

def main():
    p=argparse.ArgumentParser(); p.add_argument("--inputs",nargs="+",required=True); p.add_argument("--output-dir",default="results/gate1"); p.add_argument("--bootstrap",type=int,default=10000); p.add_argument("--seed",type=int,default=1234); args=p.parse_args(); paths=[]
    for x in args.inputs:
        m=glob.glob(x); paths.extend(m if m else [x])
    frames=[pd.read_csv(x) for x in paths if Path(x).exists()]
    if not frames: raise SystemExit("no evaluation CSVs")
    df=pd.concat(frames,ignore_index=True); required={"context_id","word","relation","lang","condition","seed","schedule","update","surface_nll","lexical_nll","post_nll","pre_nll","local_surface","local_post","train_count_en","train_count_de","gpu_name","init_sha256","effective_batch_size","git_commit","data_schema_version"}; missing=required-set(df.columns)
    if missing: raise ValueError(f"missing columns {sorted(missing)}")
    invariant_problems=check_invariants(df); paired=pair_rows(df); ws=primary_word_seed(paired); summary={"n_paired_context_rows":int(len(paired)),"n_seeds":int(ws.seed.nunique()),"invariant_problems":invariant_problems}
    for rel in ["false_friend","true_friend"]:
        for i,m in enumerate(PRIMARY): summary[f"{rel}:{m}"]=crossed_bootstrap(ws,rel,m,args.bootstrap,args.seed+100*i+(0 if rel=="false_friend" else 50))
    for i,m in enumerate(PRIMARY): summary[f"interaction_false_minus_true:{m}"]=crossed_interaction(ws,m,args.bootstrap,args.seed+700+i)
    summary["frequency_adjusted_false_minus_true:local_post"]=frequency_adjusted(ws,paired,args.bootstrap,args.seed+900); summary["seed_consistency_ff_surface_benefit"]=seed_consistency(ws,"false_friend","surface_nll",-1); summary["seed_consistency_ff_post_cost"]=seed_consistency(ws,"false_friend","post_nll",1); summary["seed_consistency_ff_local_surface_benefit"]=seed_consistency(ws,"false_friend","local_surface",-1); summary["seed_consistency_ff_local_post_cost"]=seed_consistency(ws,"false_friend","local_post",1)
    ff_s,ff_p=summary["false_friend:surface_nll"],summary["false_friend:post_nll"]; ff_ls,ff_lp=summary["false_friend:local_surface"],summary["false_friend:local_post"]; ff_pre=summary["false_friend:pre_nll"]; inter=summary["interaction_false_minus_true:local_post"]; adj=summary["frequency_adjusted_false_minus_true:local_post"]
    support=summary["n_seeds"]>=5 and ff_lp["n_words"]>=10 and summary["true_friend:local_post"]["n_words"]>=10; seed_ok=min(summary["seed_consistency_ff_surface_benefit"],summary["seed_consistency_ff_post_cost"],summary["seed_consistency_ff_local_surface_benefit"],summary["seed_consistency_ff_local_post_cost"])>=.8; raw_ok=ff_s["ci95_high"]<0 and ff_p["ci95_low"]>0; local_ok=ff_ls["ci95_high"]<0 and ff_lp["ci95_low"]>0; specificity=inter["ci95_low"]>0 and adj["ci95_low"]>0; neg_ok=np.isfinite(ff_pre["mean"]) and abs(ff_pre["mean"])<=.5*max(abs(ff_p["mean"]),1e-12)
    if invariant_problems: verdict="INCONCLUSIVE_INVARIANT_MISMATCH"
    elif not support: verdict="INCONCLUSIVE_INSUFFICIENT_LEXICAL_OR_SEED_SUPPORT"
    elif raw_ok and local_ok and specificity and seed_ok and neg_ok: verdict="PASS_CAUSAL_FORM_CONTEXT_DISSOCIATION"
    elif ff_s["ci95_high"]<0 and not (ff_p["ci95_low"]>0 and ff_lp["ci95_low"]>0): verdict="KILL_CORE_FORM_ONLY"
    elif ff_p["ci95_low"]>0 and not ff_s["ci95_high"]<0: verdict="WEAK_INTERFERENCE_ONLY"
    elif not neg_ok: verdict="INCONCLUSIVE_GLOBAL_DIVERGENCE_NEGATIVE_CONTROL_FAILED"
    else: verdict="KILL_NO_SPECIFIC_CAUSAL_DISSOCIATION"
    summary["gate_components"]={"support":bool(support),"raw_form_and_post":bool(raw_ok),"localized_form_and_post":bool(local_ok),"specificity":bool(specificity),"seed_robustness":bool(seed_ok),"negative_control":bool(neg_ok)}; summary["verdict"]=verdict
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True); json.dump(summary,open(out/"summary.json","w",encoding="utf-8"),indent=2); paired.to_csv(out/"paired_context_effects.csv",index=False); ws.to_csv(out/"primary_word_seed_effects.csv",index=False)
    lines=["# Gate 1 result","",f"**Verdict: `{verdict}`**","",f"Invariant problems: {invariant_problems or 'none'}",""]
    for k,v in summary.items():
        if isinstance(v,dict) and "mean" in v: lines.append(f"- `{k}` mean={v['mean']:.6f}, 95% CI=[{v['ci95_low']:.6f}, {v['ci95_high']:.6f}]")
    lines += ["","Primary deltas are shared - split. Surface < 0 is benefit; post/local_post > 0 is cost.","Surface probability is base+alias probability mass, avoiding a one-class-vs-two-class artifact.","Primary inference uses contexts -> equal language weighting -> lexical item x seed, then crossed bootstrap over words and seeds."]; (out/"summary.md").write_text("\n".join(lines),encoding="utf-8"); print("\n".join(lines[:6])); print(json.dumps(summary["gate_components"],indent=2))
if __name__=="__main__": main()
