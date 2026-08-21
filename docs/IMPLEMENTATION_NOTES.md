# Implementation / validation checklist

## Before any GPU is allocated

- [ ] Pull and record the exact frozen commit SHA.
- [ ] Prefer an existing local venv/conda environment; only create a new environment if necessary.
- [ ] `export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"` or `pip install -e .`.
- [ ] `PYTHONPATH=src pytest -q` passes.
- [ ] `scripts/prepare.py` finishes with schema v3.
- [ ] `scripts/preflight.py` returns PASS.
- [ ] Inspect retained false-friend/true-cognate word counts and EN/DE context cells.
- [ ] Inspect compact vocabulary size before estimating runtime.

## Scientific invariants checked by code

- [ ] True controls come from Stingray common/true-cognate source.
- [ ] Exact same surface and exact single-token target only.
- [ ] Split remaps only exact standalone German lexical occurrences.
- [ ] Masks for targets dropped by evidence filtering are cleared.
- [ ] Pair-level holdout removes both sides of selected OPUS pairs.
- [ ] Training exact-mask counts reproduce `targets.csv` counts.
- [ ] Alias rows are copied exactly from base rows at step 0.
- [ ] Shared/split active softmax cardinality is equal via one-in/one-out masking.
- [ ] Same-seed data RNGs are identical across conditions.
- [ ] `max_updates` counts optimizer updates.
- [ ] Data fingerprint, config hash, Git commit and initialization fingerprint are recorded.

## GPU inventory

Candidate hosts only: `fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21`.

- [ ] Run `bash scripts/check_candidate_gpus.sh`.
- [ ] Use only cards that are actually idle at dispatch time.
- [ ] Never kill or displace other users' processes.
- [ ] One run = one GPU.
- [ ] Same-seed shared/split use the same GPU model whenever possible.

## Smoke

- [ ] shared seed11 50-update smoke completes.
- [ ] split seed11 50-update smoke completes.
- [ ] step-0 checkpoints pass `verify_step0_identity.py` exactly, including frozen provenance.
- [ ] loss finite; checkpoint reload works.
- [ ] evaluation writes non-empty rows.
- [ ] shared/split evaluation occurrence sets are identical.

## Gate 1

- [ ] seeds 11,22,33,44,55 each complete in both conditions.
- [ ] all use the exact same data fingerprint/config hash/Git commit/effective batch/terminal update.
- [ ] evaluate only the same terminal update.
- [ ] run `scripts/analyze.py`; do not manually cherry-pick rows/checkpoints.
- [ ] record effects, CIs, verdict, hardware and deviations in `RESEARCH_MAINLINE.md`.

## If Gate 1 passes

- [ ] confirm at larger model/training scale.
- [ ] inspect checkpoint trajectory.
- [ ] explicitly confirm sense behavior with Stingray likelihood evaluation before claiming semantic fidelity.
- [ ] only then consider path dependence/mechanism work.

## If Gate 1 fails

Do not rescue the story with probes, steering, language tags, checkpoint cherry-picking, or new metrics unless a concrete implementation/data failure is independently established.
