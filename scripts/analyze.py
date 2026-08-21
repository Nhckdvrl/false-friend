#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd

METRICS = ["form_nll", "post_nll", "pre_nll"]
PAIR_INDEX = ["context_id", "base_context_id", "word", "relation", "lang", "seed", "schedule", "step"]


def load_inputs(items):
    paths = []
    for item in items:
        paths.extend(glob.glob(item) or [item])
    frames = [pd.read_csv(p) for p in paths if Path(p).exists()]
    if not frames:
        raise SystemExit("no evaluation CSVs")
    return pd.concat(frames, ignore_index=True)


def validate_run_set(df: pd.DataFrame) -> None:
    required = {
        *PAIR_INDEX, "condition", "train_count_en", "train_count_de", "data_fingerprint",
        "config_hash", "effective_batch_size", "training_gpu_name", "git_commit", "init_sha256", *METRICS,
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    if df[PAIR_INDEX + ["condition"]].duplicated().any():
        raise ValueError("duplicate evaluation rows for the same paired occurrence")
    if df.step.nunique() != 1:
        raise ValueError(f"Gate-1 verdict requires exactly one matched step, got {sorted(df.step.unique())}")
    if df.schedule.nunique() != 1 or str(df.schedule.iloc[0]) != "joint":
        raise ValueError("Gate-1 verdict must use only the joint schedule")
    for col in ["data_fingerprint", "config_hash", "effective_batch_size", "git_commit"]:
        if df[col].nunique() != 1:
            raise ValueError(f"mixed {col} across Gate-1 runs")
    conditions = set(df.condition.unique())
    if conditions != {"shared", "split"}:
        raise ValueError(f"expected shared+split, got {conditions}")
    per_seed = df.groupby("seed").condition.nunique()
    if not (per_seed == 2).all():
        raise ValueError("every seed must contain both shared and split runs")


def paired_contexts(df: pd.DataFrame) -> pd.DataFrame:
    meta = ["data_fingerprint", "config_hash", "effective_batch_size", "training_gpu_name", "git_commit", "init_sha256"]
    sh = df[df.condition == "shared"].set_index(PAIR_INDEX).sort_index()
    sp = df[df.condition == "split"].set_index(PAIR_INDEX).sort_index()
    if not sh.index.equals(sp.index):
        raise ValueError(
            f"shared/split evaluation coverage differs: missing_in_split={len(sh.index.difference(sp.index))}, "
            f"missing_in_shared={len(sp.index.difference(sh.index))}"
        )
    p = sh[METRICS + meta].add_suffix("_shared").join(sp[METRICS + meta].add_suffix("_split")).reset_index()
    for key in ["data_fingerprint", "config_hash", "effective_batch_size", "git_commit", "init_sha256"]:
        if not (p[f"{key}_shared"] == p[f"{key}_split"]).all():
            raise ValueError(f"paired {key} mismatch")
    for m in METRICS:
        p[f"delta_{m}"] = p[f"{m}_shared"] - p[f"{m}_split"]
    p["delta_form_local"] = p["delta_form_nll"] - p["delta_pre_nll"]
    p["delta_post_local"] = p["delta_post_nll"] - p["delta_pre_nll"]
    return p


def word_seed_table(p: pd.DataFrame) -> pd.DataFrame:
    vals = ["delta_form_nll", "delta_post_nll", "delta_pre_nll", "delta_form_local", "delta_post_local"]
    ctx = p.groupby(["relation", "word", "seed", "lang", "base_context_id"], as_index=False)[vals].mean()
    lang = ctx.groupby(["relation", "word", "seed", "lang"], as_index=False)[vals].mean()
    counts = lang.groupby(["relation", "word", "seed"]).lang.nunique()
    if not (counts == 2).all():
        raise ValueError(f"word/seed missing one language after evaluation: {counts[counts != 2].head().to_dict()}")
    return lang.groupby(["relation", "word", "seed"], as_index=False)[vals].mean()


def complete_matrix(x: pd.DataFrame, metric: str, relation: str) -> np.ndarray:
    d = x[x.relation == relation].pivot(index="word", columns="seed", values=metric)
    if d.empty or d.isna().any().any():
        raise ValueError(f"incomplete word×seed matrix for {relation}/{metric}")
    return d.to_numpy(float)


def crossed_ci(x, metric, relation, n, seed):
    arr = complete_matrix(x, metric, relation)
    point = float(arr.mean())
    rng = np.random.default_rng(seed)
    vals = np.empty(n)
    for i in range(n):
        wi = rng.integers(0, arr.shape[0], arr.shape[0])
        si = rng.integers(0, arr.shape[1], arr.shape[1])
        vals[i] = arr[np.ix_(wi, si)].mean()
    return {"mean": point, "ci95_low": float(np.quantile(vals, .025)), "ci95_high": float(np.quantile(vals, .975)), "n_words": int(arr.shape[0]), "n_seeds": int(arr.shape[1])}


def interaction_ci(x, metric, n, seed):
    ff = x[x.relation == "false_friend"].pivot(index="word", columns="seed", values=metric)
    tf = x[x.relation == "true_friend"].pivot(index="word", columns="seed", values=metric)
    seeds = sorted(set(ff.columns).intersection(tf.columns)); ff, tf = ff[seeds], tf[seeds]
    if ff.isna().any().any() or tf.isna().any().any():
        raise ValueError(f"incomplete matrices for interaction {metric}")
    fa, ta = ff.to_numpy(float), tf.to_numpy(float); point = float(fa.mean() - ta.mean())
    rng = np.random.default_rng(seed); vals = np.empty(n)
    for i in range(n):
        si = rng.integers(0, len(seeds), len(seeds)); fi = rng.integers(0, fa.shape[0], fa.shape[0]); ti = rng.integers(0, ta.shape[0], ta.shape[0])
        vals[i] = fa[np.ix_(fi, si)].mean() - ta[np.ix_(ti, si)].mean()
    return {"mean": point, "ci95_low": float(np.quantile(vals, .025)), "ci95_high": float(np.quantile(vals, .975)), "n_false_friend": int(fa.shape[0]), "n_true_friend": int(ta.shape[0]), "n_seeds": len(seeds)}


def _beta_from_arrays(y, ff, total, ratio):
    X = np.column_stack([np.ones(len(y)), ff, total, ratio])
    return float(np.linalg.lstsq(X.T @ X, X.T @ y, rcond=None)[0][1])


def frequency_adjusted(p, metric, n, seed):
    x = word_seed_table(p)
    freq = p[["word", "train_count_en", "train_count_de"]].drop_duplicates("word")
    z = x.merge(freq, on="word", how="left"); seeds = sorted(z.seed.unique()); rel_arrays = {}
    for rel in ["false_friend", "true_friend"]:
        sub = z[z.relation == rel]; pv = sub.pivot(index="word", columns="seed", values=metric)[seeds]
        if pv.empty or pv.isna().any().any():
            raise ValueError(f"incomplete frequency-adjusted matrix for {rel}")
        meta = sub.drop_duplicates("word").set_index("word").loc[pv.index]
        total = np.log1p(meta.train_count_en.to_numpy(float) + meta.train_count_de.to_numpy(float))
        ratio = np.abs(np.log((meta.train_count_en.to_numpy(float)+1.0)/(meta.train_count_de.to_numpy(float)+1.0)))
        rel_arrays[rel] = (pv.to_numpy(float), total, ratio)

    def build(ff_w=None, tf_w=None, seed_idx=None):
        parts=[]
        for rel, word_idx in [("false_friend", ff_w), ("true_friend", tf_w)]:
            vals,total,ratio=rel_arrays[rel]
            if word_idx is None: word_idx=np.arange(vals.shape[0])
            if seed_idx is None: seed_idx=np.arange(vals.shape[1])
            yy=vals[np.ix_(word_idx,seed_idx)].reshape(-1)
            tt=np.repeat(total[word_idx], len(seed_idx)); rr=np.repeat(ratio[word_idx], len(seed_idx))
            indicator=np.full(len(yy), 1.0 if rel=="false_friend" else 0.0); parts.append((yy,indicator,tt,rr))
        return [np.concatenate([q[i] for q in parts]) for i in range(4)]

    y,ff,total,ratio=build(); point=_beta_from_arrays(y,ff,total,ratio)
    rng=np.random.default_rng(seed); vals=np.empty(n); nff=rel_arrays["false_friend"][0].shape[0]; ntf=rel_arrays["true_friend"][0].shape[0]; ns=len(seeds)
    for i in range(n):
        fi=rng.integers(0,nff,nff); ti=rng.integers(0,ntf,ntf); si=rng.integers(0,ns,ns)
        yb,ffb,tb,rb=build(fi,ti,si); vals[i]=_beta_from_arrays(yb,ffb,tb,rb)
    return {"mean":point,"ci95_low":float(np.quantile(vals,.025)),"ci95_high":float(np.quantile(vals,.975)),"covariates":"log1p(total_frequency), abs(log((en+1)/(de+1)))"}


def seed_consistency(x, metric, relation, sign):
    d = x[x.relation == relation].groupby("seed")[metric].mean()
    return float((d < 0).mean() if sign < 0 else (d > 0).mean())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--inputs", nargs="+", required=True); ap.add_argument("--output-dir", default="results/gate1"); ap.add_argument("--bootstrap", type=int, default=10000); ap.add_argument("--seed", type=int, default=1234); a = ap.parse_args()
    df = load_inputs(a.inputs); validate_run_set(df); p = paired_contexts(df)
    freq = df[["word", "train_count_en", "train_count_de"]].drop_duplicates("word"); p = p.merge(freq, on="word", how="left"); x = word_seed_table(p)
    summary = {"n_paired_occurrence_rows": int(len(p)), "n_base_contexts": int(p.base_context_id.nunique()), "n_seeds": int(x.seed.nunique()), "step": int(df.step.iloc[0]), "data_fingerprint": str(df.data_fingerprint.iloc[0]), "config_hash": str(df.config_hash.iloc[0]), "effective_batch_size": int(df.effective_batch_size.iloc[0]), "git_commit": str(df.git_commit.iloc[0])}
    primary_metrics = ["delta_form_nll", "delta_post_nll", "delta_pre_nll", "delta_form_local", "delta_post_local"]
    for rel in ["false_friend", "true_friend"]:
        for m in primary_metrics:
            summary[f"{rel}:{m}"] = crossed_ci(x, m, rel, a.bootstrap, a.seed + len(summary) * 7)
    summary["interaction_false_minus_true:delta_post_local"] = interaction_ci(x, "delta_post_local", a.bootstrap, a.seed + 701)
    summary["interaction_false_minus_true:delta_form_nll"] = interaction_ci(x, "delta_form_nll", a.bootstrap, a.seed + 702)
    summary["frequency_adjusted_false_minus_true:delta_post_local"] = frequency_adjusted(p, "delta_post_local", a.bootstrap, a.seed + 703)
    summary["seed_consistency_ff_form_benefit"] = seed_consistency(x, "delta_form_nll", "false_friend", -1)
    summary["seed_consistency_ff_post_local_cost"] = seed_consistency(x, "delta_post_local", "false_friend", 1)
    summary["paired_hardware_match_fraction"] = float((p.training_gpu_name_shared == p.training_gpu_name_split).mean())

    ff_form=summary["false_friend:delta_form_nll"]; ff_post=summary["false_friend:delta_post_nll"]; ff_local=summary["false_friend:delta_post_local"]; ff_pre=summary["false_friend:delta_pre_nll"]; inter=summary["interaction_false_minus_true:delta_post_local"]; adjusted=summary["frequency_adjusted_false_minus_true:delta_post_local"]
    support = x.seed.nunique() >= 5 and ff_form["n_words"] >= 10 and summary["true_friend:delta_form_nll"]["n_words"] >= 10
    form_pass = ff_form["ci95_high"] < 0 and summary["seed_consistency_ff_form_benefit"] >= .8
    post_raw_pass = ff_post["ci95_low"] > 0
    post_local_pass = ff_local["ci95_low"] > 0 and summary["seed_consistency_ff_post_local_cost"] >= .8
    specificity_pass = inter["ci95_low"] > 0 and adjusted["ci95_low"] > 0
    negative_control_pass = abs(ff_pre["mean"]) <= .5 * max(abs(ff_post["mean"]), 1e-12)
    hardware_pass = summary["paired_hardware_match_fraction"] == 1.0
    components = {"support":bool(support),"form_benefit":bool(form_pass),"post_raw_cost":bool(post_raw_pass),"post_local_cost":bool(post_local_pass),"ff_specificity":bool(specificity_pass),"negative_control":bool(negative_control_pass),"paired_hardware_match":bool(hardware_pass)}; summary["gate_components"] = components
    if not support: verdict="INCONCLUSIVE_INSUFFICIENT_LEXICAL_OR_SEED_SUPPORT"
    elif not hardware_pass: verdict="INCONCLUSIVE_PAIRED_HARDWARE_MISMATCH"
    elif form_pass and post_raw_pass and post_local_pass and specificity_pass and negative_control_pass: verdict="PASS_CAUSAL_FORM_CONTEXT_DISSOCIATION"
    elif form_pass and not post_local_pass: verdict="KILL_CORE_FORM_ONLY"
    elif post_local_pass and not form_pass: verdict="WEAK_INTERFERENCE_ONLY"
    elif not negative_control_pass: verdict="INCONCLUSIVE_GLOBAL_DIVERGENCE_NEGATIVE_CONTROL_FAILED"
    else: verdict="KILL_NO_SPECIFIC_CAUSAL_DISSOCIATION"
    summary["verdict"] = verdict
    out=Path(a.output_dir); out.mkdir(parents=True, exist_ok=True); (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8"); p.to_csv(out/"paired_context_effects.csv",index=False)
    (out/"summary.md").write_text("\n".join(["# Gate 1 result","",f"**Verdict: `{verdict}`**","","Primary deltas are shared - split. Form < 0 is benefit; post-local > 0 is target-local continuation cost.","","```json",json.dumps(components,indent=2),"```"]),encoding="utf-8")
    print(verdict); print(json.dumps(components,indent=2))


if __name__ == "__main__": main()
