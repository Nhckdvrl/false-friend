# Server Agent Handoff

Repository: `https://github.com/Nhckdvrl/false-friend`

You are not a shell-script executor. Preserve the **causal meaning** of the experiment while making it run correctly on the real server.

## Goal

Not “are false friends hard?” The question is:

> Does sharing one lexical representation across languages causally make the shared surface easier to predict while making language-specific continuation/meaning harder when the meanings conflict?

Shared vs split is the causal intervention. Everything else should be matched.

Desired strong FF result:

- shared improves total surface-form probability;
- shared worsens natural continuation after the target;
- both remain after subtracting a pre-target baseline;
- continuation cost is larger for false friends than true friends;
- FF-specific effect survives frequency controls and seed resampling.

If this pattern does not occur, do not rescue it by changing metrics or adding probes.

## Why each invariant exists

### Exact lexical mask
Split changes only the standalone target word in German. A matching SentencePiece id inside a compound/derivative is not the experimental object.

### Pair-level holdout
If an OPUS pair is selected for evaluation, neither language side may remain in training.

### Identical update-0 model
Every alias row is copied from its base row in both conditions. Same-seed shared/split `init_sha256` must match.

### Surface probability
In split, the same visible word can correspond to base/alias lexical rows. `surface_nll` therefore sums both probability masses. `lexical_nll` is only diagnostic.

### Pre-target control
`pre_nll` estimates global drift. `local_surface` and `local_post` subtract it. A PASS still requires raw directions.

### Optimizer updates
`max_updates` means real optimizer updates, not accumulation microsteps.

### Path dependence
For Gate 3, EN/DE use independent deterministic sample RNGs; paths consume the same per-language samples, only reordered. Path runs use constant LR and reset optimizer state at common-tail start.

## Environment

**First preference: reuse an existing compatible virtual/conda environment.**

```bash
which python
python --version
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
python -c "import transformers, datasets, pandas, numpy, sentencepiece; print('deps ok')"
```

Only create a new environment if the existing one is missing/conflicting dependencies or cannot be safely modified:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Do not damage shared environments.

## GPU resources

Candidate nodes only:

`fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21`

Not all cards are free. Inspect `nvidia-smi` before use. Use only GPUs with no meaningful memory/process occupancy. Never kill another user's process. Never assume all cards on a node are available.

```bash
bash scripts/check_candidate_gpus.sh
```

One scientific run uses exactly one visible GPU:

```bash
CUDA_VISIBLE_DEVICES=<idle-index> python scripts/train.py ...
```

The trainer intentionally refuses multiple visible GPUs.

Run as many of the 10 Gate-1 jobs concurrently as there are truly idle GPUs, then queue the rest. Pair shared/split of the same seed on the same GPU model whenever possible.

## Before scientific GPU work

```bash
python scripts/prepare.py --output data/processed/en_de --max-pairs 1000000 --min-target-occurrences 20
PYTHONPATH=src pytest -q
python scripts/preflight.py --data data/processed/en_de
```

Understand the report. If strict filtering leaves too few words, that is a data/design outcome. Do not silently relax exact-surface/token rules.

## Smoke

Use one confirmed-idle GPU:

```bash
bash scripts/run_one_gpu.sh <gpu> configs/smoke.yaml shared 11 joint
bash scripts/run_one_gpu.sh <gpu> configs/smoke.yaml split 11 joint
```

Evaluate both final checkpoints. Confirm same `init_sha256`, same effective batch/code/data schema, checkpoint reload, non-empty exactly paired evaluation, and no remapping assertions.

## Gate 1 jobs

Seeds: `11 22 33 44 55`; each has `shared` and `split`, `configs/gate1_fast.yaml`, `joint`.

```bash
bash scripts/run_one_gpu.sh <idle-gpu> configs/gate1_fast.yaml shared 11 joint
```

Do not change batch size across jobs to fit different GPUs. If a GPU cannot fit the frozen config, use another GPU or report it.

## Evaluation and decision

Evaluate identical final updates and run:

```bash
python scripts/analyze.py --inputs 'runs/gate1_fast/*/seed_*/joint/checkpoint-0008000/eval_contexts.csv' --output-dir results/gate1
```

A positive result is allowed only when the code returns `PASS_CAUSAL_FORM_CONTEXT_DISSOCIATION` with all gate components true.

If KILL, treat it as a scientific outcome unless an actual invariant failed.

## Classify failures

**Engineering bug**: import/version, OOM, path, serialization. Fix without changing causal design; rerun affected jobs.

**Scientific logic bug**: different data batches, alias init mismatch, bad exact mask, leakage, mixed updates, unmatched config/hardware. Fix first; invalidate affected runs.

**Negative scientific result**: surface benefit absent, continuation cost absent, FF/TF interaction absent, frequency adjustment removes effect. Do not rewrite the experiment to force positive results.

## Recordkeeping

Update `RESEARCH_MAINLINE.md` after each gate with date/git commit, environment, retained FF/TF counts, nodes/GPU indices/models actually used, exact config/seeds, invalidated runs, estimates/CIs/verdict, and continue/kill/inconclusive decision.

Commit any scientific code change before mixing its outputs with other runs.
