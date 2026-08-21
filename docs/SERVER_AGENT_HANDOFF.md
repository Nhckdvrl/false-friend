# Server-agent handoff — false-friend causal validation

Repository: `https://github.com/Nhckdvrl/false-friend`

You are not a command runner. You are taking over a causal research validation. Understand the estimand before changing code.

## Scientific objective

The question is whether **sharing one exact lexical row across EN and DE** can simultaneously:

1. improve prediction of the shared form; and
2. harm language-conditioned contextual integration specifically when the meanings conflict.

This is not a benchmark asking whether false friends are hard.

For an exact retained target:

- shared: EN and DE exact lexical occurrences use the base row;
- split: EN uses base; exact standalone DE occurrences use an initially-identical alias row.

Same-seed shared/split checkpoint 0 must be bit-identical.

Reserved alias rows must not alter softmax normalization. Shared masks every alias. Split normally masks every alias; only when the gold next token is an exact DE target alias does it activate that alias and mask the paired base row. Thus exactly one row is exchanged.

Primary paired effects (shared - split):

- `delta_form = form_nll_shared - form_nll_split`
- `delta_post = post_nll_shared - post_nll_split`
- `delta_pre = pre_nll_shared - pre_nll_split`
- `delta_post_local = delta_post - delta_pre`

Strong Gate-1 pattern:

- FF `delta_form < 0`;
- FF `delta_post_local > 0`;
- FF localized cost > true-cognate localized cost;
- survives frequency adjustment and crossed word×seed bootstrap.

Post-target NLL is meaning-sensitive contextual integration, not by itself proof of wrong dictionary-sense selection. Explicit Stingray sense likelihood is confirmatory only after Gate 1 survives.

## Data logic you must preserve

- False friends come from Stingray EN-DE false-friend source.
- True controls come from Stingray EN-DE `common`/true-cognate source.
- Require exact same written form and exact single-token identity.
- Split only exact standalone German occurrences using tokenizer offsets; subword/compound reuse is not manipulated.
- A selected OPUS evaluation parallel pair is removed on both EN and DE sides.
- Retained words require training evidence and natural held-out evidence in both languages.
- Preflight recomputes lexical-mask counts and must exactly match target frequency metadata.

If any of these fail, do not run the scientific grid.

## Environment policy

**Prefer existing local virtual/conda environments.** First inspect:

- `which python`
- `python --version`
- PyTorch/CUDA availability
- `transformers`, `datasets`, `pandas`, `numpy`, `sentencepiece`, `safetensors`

Reuse a compatible existing environment. Only create a new environment if dependencies are missing/conflicting or modifying the existing one is unsafe.

Expose this repository's package either with `pip install -e .` or:

```bash
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
```

Do not overwrite shared environments casually.

## GPU policy — absolutely no Slurm

Candidate hosts only:

`fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21`

Not every card is free. Before dispatch, run:

```bash
bash scripts/check_candidate_gpus.sh
```

or equivalent `ssh HOST nvidia-smi`.

Use **only GPUs that are actually idle at that moment**. Do not kill, preempt, or interfere with another user's process.

One scientific run = one GPU. Parallelize by independent `(condition, seed)` jobs. If six cards are free, run six jobs and queue four. Do not change batch size simply to use a different card.

For the same seed, shared and split should use the same GPU model whenever possible; final Gate-1 analysis refuses a PASS when paired GPU names differ.

## Required execution order

1. Pull the frozen audited `main` and record commit SHA.
2. Reuse an existing compatible environment if possible.
3. `export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"`.
4. Prepare data once:

```bash
python scripts/prepare.py --output data/processed/en_de --max-pairs 1000000 --min-target-occurrences 20 --min-eval-contexts-per-word-lang 1
```

5. Run:

```bash
python scripts/preflight.py --data data/processed/en_de
PYTHONPATH=src pytest -q
```

A preflight failure is a stop signal. Diagnose whether it is an engineering bug, insufficient data, or a failed design assumption. Do not weaken thresholds just to proceed.

6. Inventory free GPUs on the seven allowed nodes.
7. Run 50-update smoke shared+split seed 11 on one actually free GPU (sequentially is fine):

```bash
bash scripts/run_one_gpu.sh configs/smoke.yaml shared 11 joint GPU_INDEX
bash scripts/run_one_gpu.sh configs/smoke.yaml split  11 joint GPU_INDEX
```

8. Verify checkpoint-0 identity:

```bash
python scripts/verify_step0_identity.py \
  runs/smoke/shared/seed_11/joint/checkpoint-0000000 \
  runs/smoke/split/seed_11/joint/checkpoint-0000000
```

This also checks seed, schedule, config hash, data fingerprint, effective batch, frozen Git commit and initialization fingerprint. If it fails, stop. Do not interpret any dynamics.

9. Evaluate both 50-update smoke checkpoints and confirm non-empty, exactly paired rows.
10. Only then dispatch Gate 1: seeds `11,22,33,44,55`, each shared+split, using idle cards.
11. Evaluate exactly checkpoint `0008000` for every Gate-1 fast run.
12. Run `scripts/analyze.py` on all ten CSVs.
13. Update `RESEARCH_MAINLINE.md` with commit, environment, data counts, GPU assignments, deviations, effects/CIs and machine verdict.

## Runtime bug triage

### Engineering bug — fix if estimand is unchanged

Examples: import/path issue, CUDA/PyTorch compatibility, checkpoint I/O, OOM caused by an implementation mistake.

### Scientific-logic bug — affected runs are invalid

Examples: different sampled data across a paired run, lexical-mask misalignment, wrong true-control source, alias-init mismatch, output-softmax cardinality mismatch, pair leakage, unequal effective batch, evaluation pairing loss, mixed checkpoint steps/config hashes/data fingerprints/Git commits.

Fix and rerun affected experiments. A run that did not crash can still be scientifically invalid.

### Negative scientific result — not a bug

Examples: no form benefit; no localized continuation cost; true friends show the same cost; effect disappears after frequency adjustment.

Do not modify code to obtain a positive result. Apply the preregistered kill verdict.

## Gate 1 meaning

A PASS requires the complete conjunction in `RESEARCH_MAINLINE.md`; one significant p-value is insufficient. The analysis bootstraps lexical words and random seeds, gives EN/DE equal weight, and rejects missing paired coverage.

If Gate 1 fails, do not immediately add hidden-state probes, steering, tags or cherry-picked checkpoints.

## Later path gate

Only if Gate 1/2 survive. `en_then_de` and `de_then_en` use independent deterministic EN and DE RNGs, constant LR, zero warmup, and reset Adam at the identical balanced tail. The later claim requires a **sharing-specific order effect** after that tail, not a generic curriculum/forgetting effect.

## Deliverables back to the user

Report:

- frozen commit SHA;
- environment and Python/PyTorch/CUDA/Transformers versions;
- live GPU inventory for `fvcrc10/11/12/13/15/20/21` and exact cards used;
- retained FF/true-cognate counts, compact vocab size, context cells, preflight result;
- smoke logs and exact checkpoint-0 identity result;
- host/GPU/model/seed/condition/status for every Gate-1 run;
- Gate-1 form, pre, post, localized-post effects, FF-vs-control interactions, frequency-adjusted effect, crossed bootstrap CIs, seed consistency, final verdict;
- every runtime/scientific bug found, fix commit, and which runs were invalidated/repeated;
- recommendation PASS / FAIL / INCONCLUSIVE without story rescue.
