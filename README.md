# false-friend

Controlled validation of a multilingual lexical-learning question:

> **When does lexical sharing turn from transfer into interference?**

The first experiment asks whether sharing the *same lexical representation* across English and German can make a real false-friend surface form easier to predict while making the natural language-specific continuation harder to predict.

This repository is intentionally designed as a sequence of kill gates. We do not proceed to training dynamics, curriculum/path dependence, or mechanisms unless the preceding behavioral causal result survives.

## Canonical research document

Read **[`RESEARCH_MAINLINE.md`](RESEARCH_MAINLINE.md)** first. It contains:

- the core question and subquestions;
- exact shared-vs-split intervention;
- preregistered metrics and kill lines;
- Gate 1 → dynamics → path-dependence order;
- multi-node execution strategy;
- failure/confound checklist.

Literature/open-source audit: [`docs/LITERATURE_AUDIT.md`](docs/LITERATURE_AUDIT.md).

## Experiment in one diagram

```text
Stingray EN-DE targets
        |
        v
single-token + natural-frequency filter
        |
        +-------------------------------+
        |                               |
        v                               v
 SHARED target row                SPLIT target row
 EN word -> t                     EN word -> t
 DE word -> t                     DE word -> alias(t)
        |                               |
        +---------------+---------------+
                        |
              same OPUS-100 corpus
              same model / vocab size
              same seed / training steps
                        |
                        v
         held-out natural target contexts
                        |
           +------------+------------+
           |                         |
           v                         v
 target form surprisal      post-target continuation NLL
           |                         |
           +------------+------------+
                        v
     false-friend vs true-friend interaction
```

## Quick start

Use an existing local environment if it already contains the dependencies. Otherwise:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Prepare data once on shared storage:

```bash
python scripts/prepare.py \
  --output data/processed/en_de \
  --max-pairs 1000000 \
  --min-target-occurrences 20
```

Run tests:

```bash
PYTHONPATH=src pytest -q
```

Run one 4-GPU node:

```bash
bash scripts/run_local_one.sh configs/gate1_fast.yaml shared 11 joint
bash scripts/run_local_one.sh configs/gate1_fast.yaml split 11 joint
```

Submit the full fast matrix on Slurm (one node per condition/seed, no cross-node DDP):

```bash
bash scripts/submit_gate1.sh configs/gate1_fast.yaml configs/gate1_matrix.tsv
```

Evaluate matched checkpoints:

```bash
python scripts/evaluate.py \
  --checkpoint runs/gate1_fast/shared/seed_11/joint/checkpoint-0008000 \
  --data data/processed/en_de
```

After all paired runs at the same step:

```bash
python scripts/analyze.py \
  --inputs 'runs/gate1_fast/*/seed_*/joint/checkpoint-0008000/eval_contexts.csv' \
  --output-dir results/gate1
```

The analysis emits a machine-readable verdict in `results/gate1/summary.json` and a short `summary.md`.

## Repository layout

```text
RESEARCH_MAINLINE.md              canonical research question + gates + decisions
configs/
  gate1_fast.yaml                fast kill experiment
  gate1_full.yaml                confirmation scale, only after fast pass
  path_fast.yaml                 equal-count + common-tail curriculum test
  gate1_matrix.tsv               2 conditions x 5 paired seeds
  path_matrix.tsv                later path-dependence grid
docs/
  LITERATURE_AUDIT.md            papers, datasets, repositories, novelty boundary
  IMPLEMENTATION_NOTES.md        run/debug checklist
scripts/
  prepare.py                     Stingray targets + OPUS natural corpus + vocab compaction
  train.py                       controlled bilingual causal LM training
  evaluate.py                    form/post/pre natural-context metrics
  analyze.py                     paired item-cluster bootstrap + Gate-1 verdict
  analyze_trajectory.py          checkpoint dynamics
  analyze_path.py                persistent order effect after common tail
  run_local_one.sh               one 4-GPU node
  submit_gate1.sh                Slurm array submission
slurm/train_one.sbatch           exactly one node per run
src/false_friend_lab/remap.py    fixed-vocab target sharing intervention
tests/test_remap.py              core intervention invariants
```

## Primary causal controls

- same natural corpus;
- same tokenizer base;
- same compact background vocabulary;
- same model architecture;
- same total vocabulary size and parameter count;
- paired random seeds;
- target-only sharing manipulation;
- exact natural-context pairing at evaluation;
- lexical item, not sentence, is the bootstrap unit;
- pre-target NLL is a negative control for global run divergence.

## Current status

**Gate 1 code ready; no result has been claimed yet.**
