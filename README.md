# false-friend

Controlled validation of:

> **When does lexical sharing turn from transfer into interference?**

The project is organized as kill gates. We do **not** move to dynamics, path dependence, or mechanisms unless the preceding causal behavioral result survives.

## Canonical documents

- [`RESEARCH_MAINLINE.md`](RESEARCH_MAINLINE.md): research question, estimands, gates, kill lines, execution order.
- [`docs/LITERATURE_AUDIT.md`](docs/LITERATURE_AUDIT.md): literature/open-source audit.
- [`docs/SERVER_AGENT_HANDOFF.md`](docs/SERVER_AGENT_HANDOFF.md): server-agent handoff with scientific intent and runtime rules.
- [`docs/AUDIT_2026-08-21.md`](docs/AUDIT_2026-08-21.md): two-pass code/scientific audit and hardening changes.

## Gate 1

For the same real EN-DE false-friend / true-friend targets and the same natural OPUS-100 data, compare:

- **shared**: EN and DE exact lexical occurrences train one token row;
- **split**: DE exact lexical occurrences use a language-specific alias row.

Model shape, parameter count, seed, initial tensors, data, batch sequence, optimizer configuration, and update count are matched.

Primary measurements:

- `surface_nll`: probability of the observed surface string, summing base+alias mass;
- `lexical_nll`: probability of the condition-specific lexical row (diagnostic);
- `post_nll`: next-k natural-token NLL after the target;
- `pre_nll`: previous-k NLL negative control;
- `local_surface = surface_nll - pre_nll`;
- `local_post = post_nll - pre_nll`.

The strong result requires shared FFs to be easier at the surface level **and** worse after the target, both raw and localized, with an FF-vs-true-friend interaction that survives frequency adjustment and paired-seed robustness.

## No Slurm

There is no Slurm workflow. One scientific run uses **one explicitly selected idle GPU**.

Candidate hosts:

`fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21`

Only GPUs confirmed idle with `nvidia-smi` may be used. Never assume an entire node is free and never kill other users' processes.

```bash
bash scripts/check_candidate_gpus.sh
```

## Environment

Prefer an existing local environment. Only create a new virtual environment if the existing environment is missing/conflicting dependencies.

```bash
python -c "import torch, transformers, datasets, pandas, numpy; print(torch.__version__, torch.version.cuda)"
```

If a new environment is actually required:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Data preparation and hard preflight

```bash
python scripts/prepare.py --output data/processed/en_de --max-pairs 1000000 --min-target-occurrences 20
PYTHONPATH=src pytest -q
python scripts/preflight.py --data data/processed/en_de
```

Do **not** allocate scientific GPUs if preflight fails.

The hardened data pipeline uses strict exact lexical occurrences, not arbitrary matching subword IDs, and holds out complete OPUS parallel pairs.

## Runtime smoke

Choose one confirmed-idle GPU index, e.g. `2`:

```bash
bash scripts/run_one_gpu.sh 2 configs/smoke.yaml shared 11 joint
bash scripts/run_one_gpu.sh 2 configs/smoke.yaml split 11 joint
```

Then evaluate both final smoke checkpoints and verify paired initialization fingerprints, checkpoint reload, non-empty evaluation, and exact context matching.

## Gate 1 fast grid

Five paired seeds: `11 22 33 44 55`, conditions `shared/split`.

Each run is independent and should be placed on any **confirmed-idle** GPU among the candidate nodes. Pair shared/split of the same seed on the same GPU model whenever possible.

```bash
bash scripts/run_one_gpu.sh 1 configs/gate1_fast.yaml shared 11 joint
```

Evaluation:

```bash
CUDA_VISIBLE_DEVICES=1 python scripts/evaluate.py --checkpoint runs/gate1_fast/shared/seed_11/joint/checkpoint-0008000 --data data/processed/en_de
```

Final Gate-1 analysis must use the same update for every paired run:

```bash
python scripts/analyze.py --inputs 'runs/gate1_fast/*/seed_*/joint/checkpoint-0008000/eval_contexts.csv' --output-dir results/gate1
```

`summary.json` contains the machine-readable verdict.

## Important causal invariants

1. exact lexical occurrences only;
2. pair-level holdout;
3. same vocabulary size / parameter count;
4. alias rows copied from base rows at step 0 in both conditions;
5. same per-language sampled chunk sequences for paired seeds;
6. optimizer **updates**, not microsteps, define training time;
7. surface-form probability sums base+alias mass, avoiding a one-class-vs-two-class artifact;
8. contexts are averaged within word×seed×language, then EN/DE are equal-weighted;
9. inference uses crossed bootstrap over lexical items and seeds;
10. paired shared/split runs must match init fingerprint, effective batch, code commit, data schema, and GPU model.

## Current status

**ACTIVE — hardened Gate 1 implementation committed; scientific result not yet claimed.**
