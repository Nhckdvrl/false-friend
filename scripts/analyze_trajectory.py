#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import pandas as pd


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", nargs="+", required=True)
    p.add_argument("--output", default="results/trajectory.csv")
    args = p.parse_args()
    paths = []
    for x in args.inputs:
        m = glob.glob(x)
        paths.extend(m if m else [x])
    frames = [pd.read_csv(x) for x in paths if Path(x).exists()]
    if not frames:
        raise SystemExit("no input CSVs")
    df = pd.concat(frames, ignore_index=True)

    idx = ["context_id", "word", "relation", "lang", "seed", "schedule", "step"]
    shared = df[df.condition == "shared"].set_index(idx)
    split = df[df.condition == "split"].set_index(idx)
    common = shared.index.intersection(split.index)
    metrics = ["form_nll", "post_nll", "pre_nll"]
    paired = shared.loc[common, metrics].add_suffix("_shared").join(
        split.loc[common, metrics].add_suffix("_split")
    ).reset_index()
    for metric in metrics:
        paired[f"delta_{metric}"] = paired[f"{metric}_shared"] - paired[f"{metric}_split"]

    # First average contexts within lexical items so frequent words cannot dominate.
    per_word = paired.groupby(["schedule", "step", "seed", "relation", "lang", "word"], as_index=False)[
        [f"delta_{m}" for m in metrics]
    ].mean()
    traj = per_word.groupby(["schedule", "step", "relation", "lang"], as_index=False)[
        [f"delta_{m}" for m in metrics]
    ].agg(["mean", "std", "count"])
    traj.columns = ["_".join([c for c in col if c]) if isinstance(col, tuple) else col for col in traj.columns]
    traj = traj.reset_index(drop=True)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    traj.to_csv(out, index=False)
    print(traj.to_string(index=False))


if __name__ == "__main__":
    main()
