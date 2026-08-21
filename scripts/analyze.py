#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Callable, Dict, Tuple

import numpy as np
import pandas as pd


def cluster_bootstrap(word_effects: pd.Series, n_boot: int, seed: int) -> Tuple[float, float, float]:
    vals = word_effects.dropna().to_numpy(dtype=float)
    if len(vals) < 2:
        return float(np.nanmean(vals)), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        means[i] = rng.choice(vals, size=len(vals), replace=True).mean()
    return float(vals.mean()), float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def effect_by_word(paired: pd.DataFrame, metric: str, relation: str) -> pd.Series:
    sub = paired[paired["relation"] == relation].copy()
    # Shared - split. Negative form delta = sharing improves predictability.
    # Positive post delta = sharing harms post-target continuation.
    sub[f"delta_{metric}"] = sub[f"{metric}_shared"] - sub[f"{metric}_split"]
    return sub.groupby("word")[f"delta_{metric}"].mean()


def seed_consistency(paired: pd.DataFrame, metric: str, relation: str, desired_sign: int) -> float:
    sub = paired[paired["relation"] == relation].copy()
    sub["delta"] = sub[f"{metric}_shared"] - sub[f"{metric}_split"]
    per_seed = sub.groupby("seed")["delta"].mean()
    if not len(per_seed):
        return float("nan")
    if desired_sign < 0:
        return float((per_seed < 0).mean())
    return float((per_seed > 0).mean())


def summarize(paired: pd.DataFrame, metric: str, relation: str, n_boot: int, seed: int) -> Dict[str, float]:
    s = effect_by_word(paired, metric, relation)
    mean, lo, hi = cluster_bootstrap(s, n_boot, seed)
    return {"mean": mean, "ci95_low": lo, "ci95_high": hi, "n_words": int(s.shape[0])}


def interaction_by_word(paired: pd.DataFrame, metric: str) -> pd.Series:
    tmp = paired.copy()
    tmp["delta"] = tmp[f"{metric}_shared"] - tmp[f"{metric}_split"]
    per_word = tmp.groupby(["relation", "word"])["delta"].mean().reset_index()
    ff = per_word[per_word.relation == "false_friend"].set_index("word")["delta"]
    tf = per_word[per_word.relation == "true_friend"].set_index("word")["delta"]
    # Relations contain different lexical items, so bootstrap the difference of relation means below.
    # This function returns a sentinel concatenation; actual bootstrap is in bootstrap_interaction.
    return pd.concat({"false_friend": ff, "true_friend": tf})


def bootstrap_interaction(paired: pd.DataFrame, metric: str, n_boot: int, seed: int) -> Dict[str, float]:
    tmp = paired.copy()
    tmp["delta"] = tmp[f"{metric}_shared"] - tmp[f"{metric}_split"]
    ff = tmp[tmp.relation == "false_friend"].groupby("word")["delta"].mean().dropna().to_numpy()
    tf = tmp[tmp.relation == "true_friend"].groupby("word")["delta"].mean().dropna().to_numpy()
    if len(ff) < 2 or len(tf) < 2:
        return {"mean": float("nan"), "ci95_low": float("nan"), "ci95_high": float("nan")}
    rng = np.random.default_rng(seed)
    vals = np.empty(n_boot)
    for i in range(n_boot):
        vals[i] = rng.choice(ff, len(ff), replace=True).mean() - rng.choice(tf, len(tf), replace=True).mean()
    return {
        "mean": float(ff.mean() - tf.mean()),
        "ci95_low": float(np.quantile(vals, 0.025)),
        "ci95_high": float(np.quantile(vals, 0.975)),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", nargs="+", required=True, help="CSV paths or glob patterns")
    p.add_argument("--output-dir", default="results/gate1")
    p.add_argument("--bootstrap", type=int, default=10000)
    p.add_argument("--seed", type=int, default=1234)
    args = p.parse_args()

    paths = []
    for item in args.inputs:
        matches = glob.glob(item)
        paths.extend(matches if matches else [item])
    frames = [pd.read_csv(p) for p in paths if Path(p).exists()]
    if not frames:
        raise SystemExit("no evaluation CSVs found")
    df = pd.concat(frames, ignore_index=True)

    required = {"context_id", "word", "relation", "lang", "condition", "seed", "form_nll", "post_nll", "pre_nll"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    # Compare conditions within the same seed and exact natural context occurrence.
    idx = ["context_id", "word", "relation", "lang", "seed", "schedule", "step"]
    shared = df[df.condition == "shared"].set_index(idx)
    split = df[df.condition == "split"].set_index(idx)
    common = shared.index.intersection(split.index)
    if len(common) == 0:
        raise ValueError("no paired shared/split evaluation rows; verify seeds/schedules/checkpoints")
    metrics = ["form_nll", "post_nll", "pre_nll"]
    paired = shared.loc[common, metrics].add_suffix("_shared").join(
        split.loc[common, metrics].add_suffix("_split")
    ).reset_index()

    summary: Dict[str, object] = {"n_paired_rows": int(len(paired)), "n_seeds": int(paired.seed.nunique())}
    seed_offsets = {
        ("false_friend", "form_nll"): 101,
        ("false_friend", "post_nll"): 102,
        ("false_friend", "pre_nll"): 103,
        ("true_friend", "form_nll"): 201,
        ("true_friend", "post_nll"): 202,
        ("true_friend", "pre_nll"): 203,
    }
    metric_offsets = {"form_nll": 301, "post_nll": 302, "pre_nll": 303}
    for relation in ["false_friend", "true_friend"]:
        for metric in metrics:
            summary[f"{relation}:{metric}"] = summarize(
                paired, metric, relation, args.bootstrap, args.seed + seed_offsets[(relation, metric)]
            )
    for metric in metrics:
        summary[f"interaction_false_minus_true:{metric}"] = bootstrap_interaction(
            paired, metric, args.bootstrap, args.seed + metric_offsets[metric]
        )

    ff_form = summary["false_friend:form_nll"]
    ff_post = summary["false_friend:post_nll"]
    ff_pre = summary["false_friend:pre_nll"]
    post_inter = summary["interaction_false_minus_true:post_nll"]
    form_consistency = seed_consistency(paired, "form_nll", "false_friend", -1)
    post_consistency = seed_consistency(paired, "post_nll", "false_friend", +1)
    summary["seed_consistency_ff_form_benefit"] = form_consistency
    summary["seed_consistency_ff_post_cost"] = post_consistency

    form_pass = ff_form["ci95_high"] < 0 and form_consistency >= 0.8
    post_pass = ff_post["ci95_low"] > 0 and post_consistency >= 0.8
    specificity_pass = post_inter["ci95_low"] > 0
    neg_control_pass = (
        np.isfinite(ff_pre["mean"])
        and np.isfinite(ff_post["mean"])
        and abs(ff_pre["mean"]) <= 0.5 * max(abs(ff_post["mean"]), 1e-12)
    )

    if form_pass and post_pass and specificity_pass and neg_control_pass:
        verdict = "PASS_CAUSAL_FORM_MEANING_DISSOCIATION"
    elif form_pass and not post_pass:
        verdict = "KILL_CORE_FORM_ONLY"
    elif post_pass and not form_pass:
        verdict = "WEAK_INTERFERENCE_ONLY"
    elif not neg_control_pass:
        verdict = "INCONCLUSIVE_GLOBAL_DIVERGENCE_NEGATIVE_CONTROL_FAILED"
    else:
        verdict = "KILL_NO_SPECIFIC_CAUSAL_DISSOCIATION"
    summary["verdict"] = verdict
    summary["gate_components"] = {
        "form_pass": bool(form_pass),
        "post_pass": bool(post_pass),
        "specificity_pass": bool(specificity_pass),
        "negative_control_pass": bool(neg_control_pass),
    }

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    paired.to_csv(out / "paired_context_effects.csv", index=False)

    lines = ["# Gate 1 result", "", f"**Verdict: `{verdict}`**", ""]
    for key, value in summary.items():
        if isinstance(value, dict) and "mean" in value:
            lines.append(
                f"- `{key}`: mean={value['mean']:.5f}, 95% CI=[{value['ci95_low']:.5f}, {value['ci95_high']:.5f}]"
            )
    lines += [
        "",
        "Interpretation of deltas: shared - split. Form < 0 is a sharing benefit; post-target > 0 is a continuation cost.",
        "Bootstrap unit is lexical item (word), after averaging contexts and seeds within each item.",
    ]
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:4]))
    print(json.dumps(summary["gate_components"], indent=2))


if __name__ == "__main__":
    main()
