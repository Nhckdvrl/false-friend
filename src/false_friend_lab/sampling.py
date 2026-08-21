from __future__ import annotations

import random
from typing import Dict

import numpy as np


def make_language_rngs(seed: int) -> Dict[str, np.random.Generator]:
    # Separate streams ensure EN-first and DE-first consume the exact same
    # per-language sample sequences; only temporal order differs.
    return {
        "en": np.random.default_rng(seed * 100_003 + 17),
        "de": np.random.default_rng(seed * 100_003 + 29),
    }


def make_plan_rng(seed: int) -> random.Random:
    return random.Random(seed * 100_003 + 41)


def language_plan(schedule: str, update: int, phase_updates: int, micro_batch: int, rng: random.Random) -> list[str]:
    def balanced() -> list[str]:
        if micro_batch % 2:
            raise ValueError("balanced micro_batch_size must be even")
        x = ["en"] * (micro_batch // 2) + ["de"] * (micro_batch // 2)
        rng.shuffle(x)
        return x

    if schedule == "joint":
        return balanced()
    if schedule == "en_only":
        return ["en"] * micro_batch
    if schedule == "de_only":
        return ["de"] * micro_batch
    if schedule in {"en_then_de", "de_then_en"}:
        if phase_updates <= 0:
            raise ValueError("phase_updates must be positive")
        first, second = ("en", "de") if schedule == "en_then_de" else ("de", "en")
        if update < phase_updates:
            return [first] * micro_batch
        if update < 2 * phase_updates:
            return [second] * micro_batch
        return balanced()
    raise ValueError(f"unknown schedule: {schedule}")


def sample_chunk(ids: np.ndarray, lexical_mask: np.ndarray, block: int, rng: np.random.Generator):
    if len(ids) != len(lexical_mask) or len(ids) <= block:
        raise ValueError("stream/mask invalid for block size")
    start = int(rng.integers(0, len(ids) - block + 1))
    return (
        np.asarray(ids[start : start + block], dtype=np.int64),
        np.asarray(lexical_mask[start : start + block], dtype=np.bool_),
    )
