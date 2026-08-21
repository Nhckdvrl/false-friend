# false-friend

Controlled validation of one causal multilingual lexical-learning question:

> **When does lexical sharing turn from transfer into interference?**

The first experiment asks whether forcing the *same exact lexical form* in English and German through one shared lexical row can make that form easier to predict while making language-conditioned continuation harder when the two meanings conflict.

This repository is organized as kill gates. Do **not** proceed to training dynamics, path dependence, or mechanisms unless the preceding behavioral causal gate survives.

## Canonical documents

- [`RESEARCH_MAINLINE.md`](RESEARCH_MAINLINE.md): research question, causal estimand, gates, decision rules.
- [`docs/LITERATURE_AUDIT.md`](docs/LITERATURE_AUDIT.md): literature/open-source boundary.
- [`docs/SERVER_AGENT_HANDOFF.md`](docs/SERVER_AGENT_HANDOFF.md): server execution handoff with scientific intent and GPU policy.
- [`docs/IMPLEMENTATION_NOTES.md`](docs/IMPLEMENTATION_NOTES.md): engineering/scientific validation checklist.
- [`docs/AUDIT_2026-08-21.md`](docs/AUDIT_2026-08-21.md): two-pass algorithm/scientific audit.

## Gate 1 in one diagram

```text
Stingray EN-DE false-friend targets + EN-DE common/true-cognate controls
                              |
             exact same surface + exact single token
                              |
                              v
                       natural OPUS-100
                              |
                exact standalone occurrence mask
                              |
          +-------------------+-------------------+
          |                                       |
          v                                       v
       SHARED                                  SPLIT
 EN exact form -> base row              EN exact form -> base row
 DE exact form -> base row              DE exact form -> alias row
          |                                       |
          +-------------------+-------------------+
                              |
        same seed / same step-0 tensors / same sampled batches
        same model size / same active softmax cardinality
                              |
                              v
          held-out natural parallel pairs, never seen in training
                              |
                  form NLL / pre NLL / post NLL
                              |
                              v
       false-friend effect vs true-cognate sharing control
```

## Critical causal invariants

1. True-cognate controls come from Stingray's `en_de_common*` source, not by guessing from the false-friend file.
2. Only **standalone exact lexical occurrences** are remapped. A target token reused as a compound/subword is not manipulated.
3. A held-out OPUS parallel pair is removed on **both** sides.
4. Same-seed shared/split step-0 model tensors are exactly identical; every alias row starts as an exact copy of its base row.
5. Reserved aliases do not change softmax denominator size: shared masks all aliases; split uses strict **one-in/one-out** masking only when the label is an exact German target alias.
6. `max_updates` means optimizer updates, not microsteps.
7. Gate-1 training is one GPU per independent run. Cross-node bandwidth is irrelevant.
8. Inference is paired on the exact same occurrence; inference unit is lexical item × seed, not sentence row.
9. The primary continuation claim uses `delta_post_local = delta_post - delta_pre`; explicit sense understanding is a later confirmatory test.
10. Every run records data fingerprint, config hash, Git commit, initialization fingerprint, effective batch and GPU model; the primary analysis refuses mixed provenance.

## Environment

Prefer an existing local virtual/conda environment. Do not create a new environment unless dependencies are missing or conflicting.

The scripts work after either an editable install:

```bash
pip install -e .
```

or explicit local package path:

```bash
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
```

## Data preparation and preflight

```bash
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
python scripts/prepare.py \
  --output data/processed/en_de \
  --max-pairs 1000000 \
  --min-target-occurrences 20 \
  --min-eval-contexts-per-word-lang 1

python scripts/preflight.py --data data/processed/en_de
PYTHONPATH=src pytest -q
```

A preflight failure is a stop signal. Do not weaken thresholds merely to make the experiment run.

## No Slurm: GPU policy

Candidate hosts are only:

`fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21`

Not every GPU is free. Inspect first:

```bash
bash scripts/check_candidate_gpus.sh
```

Use **only actually idle cards**. Never kill or interfere with another process. One scientific run uses one exposed GPU:

```bash
bash scripts/run_one_gpu.sh configs/smoke.yaml shared 11 joint 0
bash scripts/run_one_gpu.sh configs/smoke.yaml split  11 joint 0
```

The last argument is the physical GPU index on the current host. Across hosts, dispatch independent `(condition, seed)` jobs to whichever listed cards are genuinely idle. Same-seed shared/split runs should use the same GPU model.

## Mandatory smoke before Gate 1

Run both 50-update smoke conditions, then verify exact step-0 identity:

```bash
python scripts/verify_step0_identity.py \
  runs/smoke/shared/seed_11/joint/checkpoint-0000000 \
  runs/smoke/split/seed_11/joint/checkpoint-0000000

python scripts/evaluate.py --checkpoint runs/smoke/shared/seed_11/joint/checkpoint-0000050 --data data/processed/en_de
python scripts/evaluate.py --checkpoint runs/smoke/split/seed_11/joint/checkpoint-0000050  --data data/processed/en_de
```

Smoke is engineering validation only; one seed cannot pass the scientific gate.

## Gate-1 scientific grid

Five paired seeds: `11, 22, 33, 44, 55`.

For every seed run `shared` and `split` at the same config. Example:

```bash
bash scripts/run_one_gpu.sh configs/gate1_fast.yaml shared 11 joint 0
bash scripts/run_one_gpu.sh configs/gate1_fast.yaml split  11 joint 0
```

After all ten terminal checkpoints are evaluated:

```bash
python scripts/analyze.py \
  --inputs 'runs/gate1_fast/*/seed_*/joint/checkpoint-0008000/eval_contexts.csv' \
  --output-dir results/gate1
```

The analysis refuses mixed steps/configs/data fingerprints/Git commits/effective batches, refuses imperfect shared/split occurrence coverage, and will not PASS if paired hardware types differ.

## Repository layout

```text
RESEARCH_MAINLINE.md
configs/
  smoke.yaml
  gate1_fast.yaml
  gate1_full.yaml
  path_fast.yaml
  gate1_matrix.tsv
  path_matrix.tsv
docs/
  LITERATURE_AUDIT.md
  IMPLEMENTATION_NOTES.md
  SERVER_AGENT_HANDOFF.md
  AUDIT_2026-08-21.md
scripts/
  prepare.py
  preflight.py
  train.py
  evaluate.py
  analyze.py
  analyze_trajectory.py
  analyze_path.py
  verify_step0_identity.py
  check_candidate_gpus.sh
  run_one_gpu.sh
src/false_friend_lab/
  remap.py
  sampling.py
tests/
  test_remap.py
```

## Current status

**ACTIVE — audited Gate-1 implementation prepared; no scientific result has been claimed.**
