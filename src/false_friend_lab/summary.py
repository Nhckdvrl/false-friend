"""Descriptive, lexeme-clustered pilot summaries; never automated paper-level claims."""
from __future__ import annotations

import math
import random
from collections import defaultdict
from statistics import mean


def summarize(rows: list[dict], *, bootstrap: int = 2000, seed: int = 42) -> dict:
    if not rows:
        raise ValueError("no evaluation rows")
    seen = set()
    cells = defaultdict(list)
    families = defaultdict(list)
    for r in rows:
        key = (r["item_id"], r.get("model", ""))
        if key in seen:
            raise ValueError(f"duplicate item/model: {key}")
        seen.add(key)
        value = float(r["mean_correct_minus_foil_logp"])
        if not math.isfinite(value):
            raise ValueError("non-finite margin")
        cells[(r["condition"], r["lexeme_id"])].append(value)
        families[(r["family_id"], r["condition"])].append(value)
    condition_to_lexemes = defaultdict(list)
    for (condition, lexeme), vals in cells.items():
        condition_to_lexemes[condition].append(mean(vals))

    rng = random.Random(seed)
    summary = {}
    for condition, values in sorted(condition_to_lexemes.items()):
        values = sorted(values)
        bs = [mean(rng.choices(values, k=len(values))) for _ in range(bootstrap)] if bootstrap else []
        bs.sort()
        ci = [bs[int((len(bs)-1)*.025)], bs[int((len(bs)-1)*.975)]] if bs else None
        summary[condition] = {
            "n_lexemes": len(values), "mean_logp_margin": mean(values),
            "lexeme_bootstrap_ci95_exploratory": ci
        }
    pair_groups = defaultdict(dict)
    for (family, condition), vals in families.items():
        pair_groups[family][condition] = mean(vals)
    paired = defaultdict(list)
    for family, values in pair_groups.items():
        for condition in values:
            if condition == "baseline" or "baseline" not in values:
                continue
            paired[condition].append(values[condition] - values["baseline"])
    return {
        "status": "DESCRIPTIVE_ONLY_NOT_A_HYPOTHESIS_TEST",
        "conditions": summary,
        "paired_vs_baseline_by_family": {
            k: {"n_families": len(v), "mean_delta_logp_margin": mean(v)}
            for k, v in sorted(paired.items())
        },
        "warning": "Bootstraps are exploratory; multi-model dependence, item review, "
                   "prompt effects and confirmatory uncertainty are not handled.",
    }
