# Research Mainline: When Does Lexical Sharing Turn from Transfer into Interference?

_Last updated: 2026-08-21_

This file is the canonical research record. Keep the core question, preregistered gates, decisions, and post-run conclusions here. Do **not** promote a later mechanism experiment if an earlier behavioral gate fails.

## 1. Core research question

> When a model learns two languages that reuse the same lexical form, does sharing the lexical representation improve prediction of that form while making language-specific semantic use harder when the meanings conflict? If so, when does this transfer benefit turn into interference, and can training history leave a persistent semantic bias?

The project deliberately does **not** ask whether false friends are simply difficult. That result is already established by StingrayBench, Doppelganger-JC, SemCog Bench, and ACL 2026 work on Romance-language false friends. The new causal object is **lexical sharing itself**.

### Central causal contrast

For the *same* real lexical targets and *same* natural bilingual corpus:

- **shared**: English and German occurrences of a target use one token/embedding/output row;
- **split**: English uses the base row, German uses a reserved language-specific alias row.

The model vocabulary has the **same size in both conditions**. Alias rows are allocated in both conditions, so parameter count and output-softmax cardinality are held fixed. All non-target tokens are mapped identically.

The first causal estimand is therefore:

`effect of target-level lexical sharing = shared - split`

rather than `false friend - ordinary word`.

## 2. Why EN-DE first

EN-DE is the first language pair because it gives the cleanest intersection of existing resources:

- StingrayBench contains 98 EN-DE true cognates and 98 false friends with sense-oriented annotations.
- Kallini et al. (EMNLP Findings 2025) already train controlled EN-DE bilingual autoregressive models with vocabulary-overlap manipulations.
- OPUS-100 contains 1,000,000 DE-EN training sentence pairs, sufficient for from-scratch causal training without inventing sentences.
- The CMCL 2026 Dutch-English paper supplies the closest psycholinguistic/computational precedent for shared-vs-language-specific lexical embeddings.

Japanese-Chinese and Arabic-Hebrew are important replication targets, but they are intentionally postponed until the EN-DE causal gate survives.

## 3. Main hypotheses and subquestions

### Q1 / Gate 1 — Does a causal form–meaning dissociation exist?

For each real target word in held-out natural corpus contexts, measure two quantities in the *same sentence*:

1. **Form predictability**: target-token surprisal / NLL.
2. **Meaning-sensitive continuation**: mean NLL of the next `k` natural tokens after the target.

The second measure does not require a prompt or artificial sense-label sentence. If a shared target state is semantically less appropriate for the current language, it should make the actual downstream continuation harder to predict.

We also measure **pre-target NLL** over the previous `k` tokens as a negative control. A target-local causal story is suspect if shared/split models already differ similarly before the target occurs.

For false friends, the strong pattern is:

- `Δ_form = NLL_shared - NLL_split < 0` (shared form is easier to predict)
- `Δ_post = NLL_shared - NLL_split > 0` (shared target harms the natural continuation)

For true friends, sharing should not produce the same semantic cost. The key specificity statistic is therefore the relation interaction:

`(Δ_post_false_friend - Δ_post_true_friend) > 0`.

This is a **dissociation** claim first. We only call it a **tradeoff** if the magnitude of the form benefit and semantic cost co-vary systematically across frequency/checkpoints.

### Q2 / Gate 2 — When does the dissociation emerge during learning?

Only if Gate 1 passes, inspect saved checkpoints.

Track, separately by language and relation:

- target form NLL;
- post-target continuation NLL;
- pre-target negative-control NLL;
- shared-minus-split deltas.

Competing trajectories include:

- early transfer → later interference → later separation/recovery;
- immediate interference with no transfer benefit;
- persistent facilitation with no semantic cost;
- no target-specific effect.

The paper-worthy version is not “embeddings separate over time.” It is a behavioral learning trajectory in which the same sharing intervention has changing consequences for form and language-specific continuation.

### Q3 / Gate 3 — Does learning order leave persistent path dependence?

Only if Gates 1–2 survive.

A naive `L1 -> L2` vs `L2 -> L1` comparison is confounded by recency. We therefore use curricula with **identical cumulative token counts** and an **identical long balanced tail**:

- `EN -> DE -> balanced tail`
- `DE -> EN -> balanced tail`

Each first phase and second phase has the same number of optimizer steps and all balanced batches contain exactly half EN and half DE on every process. Thus both paths see the same total EN/DE token budget. The final balanced tail is long enough to ask whether early order leaves a residual state after recency has been washed out.

Path dependence is supported only if final false-friend semantic behavior remains detectably different after that common tail. An immediate post-switch language bias is **not** enough and must be described as recency/forgetting instead.

### Q4 / Specificity gate — Is this cross-lingual lexical collision special?

This is a later low-cost gate, not the first experiment.

Compare matched:

- true friend;
- false friend;
- language-unique word;
- monolingual homonym (prefer homonym over related polysemy).

The purpose is to distinguish a specifically cross-lingual lexical-separation problem from generic lexical ambiguity. Do not build a large hand-crafted dataset for this gate. If a clean matched public resource is unavailable, keep the comparison small or drop it.

## 4. Gate 1 experimental design

### Data

**Training corpus:** `Helsinki-NLP/opus-100`, config `de-en`, up to 1,000,000 natural parallel sentence pairs.

**Lexical target source:** StingrayBench EN-DE. We use it as a curated lexicon/annotation source, not as the training corpus.

### Automatic target filtering

`python scripts/prepare.py`:

1. downloads `data/en_de.csv` from StingrayBench;
2. extracts the surface word;
3. labels `Both` items as true friends and the remaining items as false friends;
4. keeps only targets that are a single whole-word-compatible token under `xlm-roberta-base`;
5. counts natural occurrences in EN and DE OPUS text;
6. keeps only words with at least the configured minimum occurrence count in **both** languages;
7. reserves a deterministic subset of target-containing natural sentences as evaluation contexts;
8. removes those contexts from the training token streams;
9. compacts the XLM-R vocabulary to token ids actually observed in the corpus;
10. saves target metadata, compact vocab mappings, EN/DE training streams, and held-out contexts.

No new target sentences are generated.

### Why compact the vocabulary

XLM-R has a large multilingual vocabulary. Kallini et al. likewise remap used token ids into a smaller training vocabulary. We compact observed token ids before model training so the controlled models spend compute on transformer capacity rather than hundreds of thousands of unused embedding rows.

### Shared-vs-split intervention

Suppose compact target id `t` is one of the retained false friends or true friends and base compact vocabulary size is `V`.

Both model conditions have vocabulary size `V + N_targets`.

- Shared condition: EN `t -> t`, DE `t -> t`.
- Split condition: EN `t -> t`, DE `t -> V + alias_index(t)`.

Reserved aliases exist in both conditions. No global vocabulary-size confound is introduced.

### Model

Two predefined scales:

- `configs/gate1_fast.yaml`: 6 layers, 384 hidden, 6 heads, 256 context, 8k steps.
- `configs/gate1_full.yaml`: 12 layers, 768 hidden, 12 heads, 512 context, 30k steps.

The fast grid is the kill experiment. The full grid is justified only when the fast experiment is directionally convincing.

### Seeds

Default Gate-1 matrix uses five paired seeds:

`11, 22, 33, 44, 55`

Each seed has both shared and split runs. Never compare unpaired seed sets.

### Metrics

For a target at token position `j`:

- `form_nll`: `-log P(x_j | x_<j)`
- `post_nll`: average token NLL over `j+1 ... j+k`
- `pre_nll`: average token NLL over the preceding `k` tokens

Default `k=8`; later robustness may use `4/8/16` **only after** the primary analysis is fixed.

### Statistical unit

Sentence occurrences are not independent evidence if they contain the same lexical item. The analysis therefore:

1. pairs shared/split rows by exact natural context and seed;
2. computes `shared - split` within those pairs;
3. averages contexts/seeds within lexical items;
4. bootstraps **lexical items (words)**, not raw sentences.

The default script uses 10,000 item-cluster bootstrap replicates.

## 5. Preregistered Gate 1 verdict

`PASS_CAUSAL_FORM_MEANING_DISSOCIATION` requires all of:

1. FF form effect CI entirely below zero;
2. FF post-target effect CI entirely above zero;
3. FF-vs-true-friend post-target interaction CI entirely above zero;
4. the desired FF form and post directions occur in at least 80% of paired seeds;
5. absolute FF pre-target effect is no more than half of the post-target effect.

Interpret alternatives as follows:

- `KILL_CORE_FORM_ONLY`: sharing helps target prediction but no semantic-continuation cost. The central form→meaning dissociation is not supported.
- `WEAK_INTERFERENCE_ONLY`: semantic cost without form benefit. This is closer to ordinary interference and is a weaker story.
- `KILL_NO_SPECIFIC_CAUSAL_DISSOCIATION`: no relation-specific causal pattern.
- `INCONCLUSIVE_GLOBAL_DIVERGENCE_NEGATIVE_CONTROL_FAILED`: models differ before the target too strongly; do not interpret the post-target difference as local lexical collision.

Do **not** rescue a failed Gate 1 by immediately adding probes, steering, extra language tags, or elaborate controls.

## 6. Gate 2: learning dynamics

If Gate 1 passes, evaluate every saved checkpoint using the same held-out contexts and run:

```bash
bash scripts/eval_matrix.sh runs/gate1_fast data/processed/en_de
python scripts/analyze_trajectory.py \
  --inputs 'runs/gate1_fast/*/seed_*/*/checkpoint-*/eval_contexts.csv' \
  --output results/gate2_trajectory.csv
```

Primary questions:

- Does the form benefit appear before the semantic cost?
- Does false-friend post-target interference peak and then recover?
- Does true-friend sharing stay beneficial/non-harmful throughout?
- Are trajectory differences robust across seeds and both languages?

Only after a real behavioral trajectory exists should hidden-state/embedding analysis be considered.

## 7. Gate 3: path dependence

Use `configs/path_fast.yaml` and `configs/path_matrix.tsv` only after Gate 2 is worth pursuing.

Each run has:

- first 4k steps language A only;
- next 4k steps language B only;
- final 8k steps exactly balanced.

The reverse curriculum swaps A/B but preserves total token counts. Submit with the same one-node-per-run Slurm infrastructure.

At the final checkpoint run:

```bash
python scripts/analyze_path.py \
  --inputs 'runs/path_fast/*/seed_*/*/checkpoint-*/eval_contexts.csv' \
  --output results/path_dependence.json
```

A path-dependence claim requires a residual false-friend semantic difference **after the common balanced tail**. If the difference disappears, path dependence is killed even if intermediate checkpoints show recency effects.

## 8. Compute strategy

The experiment is deliberately embarrassingly parallel across nodes.

- One run = one physical node.
- Up to 4 GPUs on that node are used through `accelerate` data parallelism.
- Different nodes run different `(condition, seed, schedule)` jobs.
- No run uses multi-node DDP/NCCL.
- Cross-node network bandwidth therefore does not affect gradient synchronization.

Default Slurm matrix contains 10 Gate-1 fast jobs (2 conditions × 5 seeds). If ten nodes are free, run all ten concurrently. If fewer are free, the array queues naturally.

## 9. Execution order

### Environment

Prefer an existing local Python environment if it already satisfies dependencies. Otherwise:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
accelerate config default
```

### Data preparation (one CPU job; shared filesystem preferred)

```bash
python scripts/prepare.py \
  --output data/processed/en_de \
  --tokenizer xlm-roberta-base \
  --max-pairs 1000000 \
  --min-target-occurrences 20
```

Before any GPU training, inspect:

- number of surviving FF/true-friend words;
- EN/DE target frequency distributions;
- number of held-out contexts by relation/language;
- compact vocabulary size.

If one relation collapses to a tiny number of lexical items after token/frequency filtering, stop and revise the language pair/tokenizer rather than pretending thousands of sentence rows give enough power.

### Unit test

```bash
PYTHONPATH=src pytest -q
```

### One-run smoke test

Temporarily reduce `max_steps` to 20–50 or pass a copied smoke config, then:

```bash
bash scripts/run_local_one.sh configs/gate1_fast.yaml shared 11 joint
```

Verify loss decreases, checkpoint reload works, and `scripts/evaluate.py` writes non-empty metrics.

### Full fast causal grid

```bash
bash scripts/submit_gate1.sh configs/gate1_fast.yaml configs/gate1_matrix.tsv
```

or manually on separate nodes:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 accelerate launch --num_processes 4 --num_machines 1 \
  scripts/train.py --config configs/gate1_fast.yaml --condition shared --seed 11 --schedule joint
```

### Evaluation and decision

Evaluate the **same checkpoint step** for all paired seeds/conditions. Do not mix 7k shared with 8k split checkpoints.

```bash
python scripts/evaluate.py --checkpoint <checkpoint-dir> --data data/processed/en_de
python scripts/analyze.py \
  --inputs <all-matched-eval-contexts.csv> \
  --output-dir results/gate1
```

Read `results/gate1/summary.md` and `summary.json`. Record the decision in this file before adding experiments.

## 10. Failure modes to check before interpreting a positive result

1. **Vocabulary-size confound:** handled by fixed alias rows in both conditions.
2. **Different corpus exposure:** shared/split read the same compact streams and use paired seed schedules.
3. **Target-frequency imbalance:** report EN and DE target frequencies; frequency is a moderator, not the main claim.
4. **Subword ambiguity:** primary target set is restricted to single-token surface forms.
5. **Sentence leakage:** deterministic target-containing held-out contexts are excluded from training streams.
6. **Pseudo-replication:** bootstrap words, not sentence rows.
7. **Global optimization divergence:** pre-target NLL is a negative control.
8. **Recency masquerading as path dependence:** use equal counts plus a long identical balanced tail.
9. **Metric overclaim:** post-target NLL is a meaning-sensitive behavioral consequence, not a perfect direct sense label. Confirm any strong result on explicit sense-disambiguation resources before the final paper claim.
10. **Prompt artifacts:** the primary causal gate is prompt-free.

## 11. External confirmation if Gate 1 passes

After the prompt-free causal effect is established, use explicit semantic resources as confirmation:

- StingrayBench EN-DE likelihood/generation tasks;
- SemCog Bench as a later Arabic-Hebrew replication;
- Doppelganger-JC as a later Japanese-Chinese replication.

These are **confirmatory** datasets, not excuses to create another benchmark.

## 12. Current project status

**Status: ACTIVE — Gate 1 implementation ready.**

Current decision rule: run the EN-DE fast causal grid before mechanism work or cross-language expansion.

### Results log

_Add dated entries here after each completed gate._

- 2026-08-21: project initialized; literature audit and causal validation code added; no experimental result yet.
