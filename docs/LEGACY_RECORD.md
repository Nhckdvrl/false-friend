# Historical record — the archived EN–DE lexical-sharing experiment

**Repository state preserved in branch [archive/lexical-sharing-2026-08](https://github.com/Nhckdvrl/false-friend/tree/archive/lexical-sharing-2026-08)**. The 2026-08-21 archive commit is `9f19b0a1d47818811733fb766b8772d427e2a9fb`.

## What was attempted

Given identical written EN/DE forms, compare shared embedding row versus separate same-initialization alias rows; measure potential surface benefit and post-target semantic-context cost with a false-friend vs aligned-control interaction.

## Why it did not reach a scientific answer

- Strict single-token exact-form candidates: 65 FF, 5 nominal aligned controls.
- Passing the natural-corpus evidence gate: 24 FF, 3 nominal aligned controls.
- Two of the three nominal controls (bar, Rock) were semantically conflicting, so only ~1 was plausibly a valid semantic-aligned natural-form control.
- StingrayBench common/cognate **sentence-level** class did not imply matching natural whole-distribution P(sense | form, language). Capitalization transformations changed the object (arm / Arm).
- Final audited preflight therefore correctly blocked GPU science; no valid Gate 1 result was obtained.

A pre-audit ten-run batch cannot be cited as a negative outcome: an output softmax competition issue and runtime alteration of control definitions invalidated it. Gate 2/3 were never scientifically completed.

## New independent code-audit concern (not a claimed historical experimental finding)

In archived remap.py `apply_causal_vocab_mask` the active output alternatives are altered based on the **gold next-token label**. One-in/one-out equalizes the *number* of active classes but generally makes the denominator depend on the target being scored. Probabilities of alternative candidate next tokens no longer share a single well-defined predictive distribution; this particularly matters for comparing sense alternatives or claiming a proper next-token NLL. This is a theoretical audit issue and would require an independent reproducing test before precise claims about its quantitative effects.

The new pilot has *no gold-dependent output softmax masking*; each answer is scored against the model's unmodified autoregressive vocabulary, with both gloss orders counterbalanced.

## Reuse policy

Do not resurrect the old `train.py`/`prepare.py`/`analyze.py` scripts or the old FF-vs-TF Gate 1. Inspect the archived branch when historical algorithm design is useful. Git history provides every source and record. Future training requires a **new** hypothesis, independently validated controls and a sound common probability definition.
