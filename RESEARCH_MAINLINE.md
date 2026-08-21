# Research Mainline — When Does Lexical Sharing Turn from Transfer into Interference?

_Last audited: 2026-08-21_

This is the canonical research record. The project is a sequence of falsifiable gates. A later gate must not be used to rescue failure of an earlier one.

## 1. Core question

> When two languages reuse the same exact lexical form, does forcing them through one shared lexical representation improve prediction of that form while making language-specific contextual use harder when the meanings conflict? If so, when does that transfer become interference, and can early learning history leave a persistent bias?

The paper is **not** about the already-established main effect “false friends are difficult.” The causal object is **lexical sharing itself**.

## 2. Literature tension that motivates the question

Existing work measures different outcomes:

- StingrayBench / related false-friend benchmarks: local language-specific semantic disambiguation can fail.
- Kallini et al. (Findings EMNLP 2025): vocabulary overlap, including low-semantic-similarity overlap, can improve global cross-lingual transfer.
- CMCL 2026 Dutch-English controlled models: shared false friends can show surprisal facilitation, much of it frequency-related.

These results need not conflict. The same sharing operation may help form prediction while making conflicting language-specific use harder. This project tests that possibility causally rather than comparing unrelated pretrained models.

## 3. Gate 1 causal estimand

For the same real lexical targets and same natural EN-DE training corpus:

### Shared

`EN exact target -> base row`

`DE exact target -> base row`

### Split

`EN exact target -> base row`

`DE exact target -> reserved alias row`

Everything else should be held fixed.

The estimand is `effect of lexical sharing = shared - split`, not simply `false_friend - ordinary_word`.

### Step-0 identity

Every alias row exists in both conditions and is copied exactly from its paired base row before training. For a paired seed, every model tensor at checkpoint 0 must be bit-identical. If that invariant fails, no scientific run is valid.

### Equal softmax normalization

Merely allocating the same vocabulary size is insufficient because unused alias rows could still steal probability mass.

At every prediction position exactly `base_vocab_size` output rows are active:

- shared: all aliases masked;
- split ordinary position: all aliases masked;
- split exact-DE target label: the correct alias is activated and its paired base row is masked.

This is strict one-in/one-out normalization. The intervention is therefore the identity of the lexical row that receives DE gradients, not a change in softmax cardinality.

## 4. Lexical target definition

Primary language pair: EN-DE.

Targets come from two actual Stingray sources:

- false friends: EN-DE false-friend file/config;
- true-cognate controls: EN-DE `common` file/config.

Do **not** infer true friends by looking for a `Both` answer in the false-friend file.

Primary targets must satisfy all of:

1. exactly the same written form across EN and DE;
2. one identical tokenizer id sentence-initially and after whitespace;
3. unique tokenizer id among retained target types;
4. sufficient exact standalone occurrences in both languages;
5. at least one natural held-out context in both languages.

The tokenizer is an implementation device, not the scientific object. If strict filtering leaves too few lexical items, the result is inconclusive and the tokenizer/language pair must be reconsidered before training; thresholds must not be relaxed post hoc merely to obtain power.

## 5. Exact lexical occurrence intervention

A token id alone is not enough. The same SentencePiece id may occur as part of a compound or derivative.

During corpus preparation, fast-tokenizer offsets are used to mark only occurrences whose character span equals the target surface and whose left/right boundaries are standalone word boundaries.

Only those marked German positions are aliased in split. Non-exact subword reuse remains unchanged.

After evidence filtering, masks for dropped candidate targets are explicitly cleared. Preflight recomputes masked occurrence counts and requires exact agreement with `targets.csv`.

## 6. Natural data and leakage control

Training corpus: `Helsinki-NLP/opus-100`, `de-en`, up to 1,000,000 parallel pairs.

Evaluation contexts are natural OPUS sentences. No new Gate-1 sentences are generated.

Holdout is deterministic at the **parallel-pair level**. If a target-containing pair is assigned to evaluation, neither EN nor DE side enters training. This prevents the translation counterpart of an evaluation sentence from remaining in the training stream.

A held-out evaluation sentence may contain multiple occurrences of one retained target, but not multiple retained target types. Multiple occurrences in one sentence are averaged at context level so the sentence does not gain extra statistical weight.

## 7. Gate 1 measurements

For target token position `j`, with fixed primary windows `k_pre = k_post = 8`:

- `form_nll = -log P(x_j | x_<j)`
- `post_nll = mean NLL(x_{j+1:j+k})`
- `pre_nll = mean NLL(x_{j-k:j-1})`

Evaluation keeps only occurrences with the complete pre and post window available.

Paired causal deltas are shared minus split: `delta_form`, `delta_post`, `delta_pre`.

To localize continuation effects against general run divergence:

`delta_post_local = delta_post - delta_pre`

`delta_form_local = delta_form - delta_pre` is diagnostic; the primary form-prediction quantity remains raw `delta_form`.

Interpretation:

- `delta_form < 0`: shared lexical row improves form prediction.
- `delta_post_local > 0`: after removing pre-target divergence, sharing makes the natural continuation harder.

Post-target continuation is **meaning-sensitive contextual integration**, not direct proof that the model selected the wrong dictionary sense. Explicit Stingray sense likelihood is confirmatory only after this causal behavioral gate survives.

## 8. Statistical unit and bootstrap

Raw sentence rows are not independent evidence.

Aggregation order:

1. exact shared/split occurrence pairing;
2. multiple occurrences -> base sentence/context;
3. contexts -> word × seed × language;
4. EN and DE are equal-weighted -> word × seed;
5. inference uses a crossed bootstrap over lexical words and random seeds.

This prevents a high-frequency word or a word with many contexts from dominating the result.

Frequency is a prespecified confound/moderator because CMCL 2026 shows it explains much of form facilitation. FF-vs-true-cognate specificity is reported both unadjusted and after lexical-level adjustment for `log1p(total EN+DE frequency)` and absolute EN/DE log-frequency ratio.

## 9. Gate 1 preregistered decision

Fast grid: 2 conditions × 5 paired seeds (`11,22,33,44,55`).

A strong PASS requires all of:

1. at least 10 false-friend lexical types and 10 true-cognate lexical types survive;
2. all five paired seeds are complete;
3. FF `delta_form` 95% crossed-bootstrap CI is entirely below 0;
4. FF raw `delta_post` CI is entirely above 0;
5. FF `delta_post_local` CI is entirely above 0;
6. FF-minus-true-cognate `delta_post_local` interaction CI is entirely above 0;
7. the frequency-adjusted FF coefficient CI is entirely above 0;
8. at least 80% of paired seeds show the expected FF form and localized-post directions;
9. absolute FF pre-target divergence is no more than half the raw post-target effect;
10. each same-seed shared/split pair used the same GPU model;
11. one data fingerprint, one config hash, one Git commit, one effective batch, one terminal update, identical paired initialization fingerprint, and exact evaluation-row coverage are used throughout.

Machine verdicts include:

- `PASS_CAUSAL_FORM_CONTEXT_DISSOCIATION`
- `KILL_CORE_FORM_ONLY`
- `WEAK_INTERFERENCE_ONLY`
- `KILL_NO_SPECIFIC_CAUSAL_DISSOCIATION`
- `INCONCLUSIVE_INSUFFICIENT_LEXICAL_OR_SEED_SUPPORT`
- `INCONCLUSIVE_PAIRED_HARDWARE_MISMATCH`
- `INCONCLUSIVE_GLOBAL_DIVERGENCE_NEGATIVE_CONTROL_FAILED`

A failed Gate 1 must not be rescued by hidden-state probes, steering, language tags, or checkpoint cherry-picking.

## 10. Fast and confirmation scales

`configs/smoke.yaml`: 2L/128D, 50 optimizer updates. Engineering only.

`configs/gate1_fast.yaml`: 6L/384D, context 256, 8,000 optimizer updates. Primary kill experiment.

`configs/gate1_full.yaml`: 12L/768D, context 512, 30,000 optimizer updates. Confirmation only after fast evidence is convincing.

Configuration uses **optimizer updates**, never ambiguous microsteps. Effective batch = `micro_batch_size × gradient_accumulation_steps` because one scientific run is one GPU.

## 11. Compute strategy — no Slurm

There is no Slurm.

Candidate hosts: `fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21`.

Not every GPU on these hosts is available. Always inspect live state first with `scripts/check_candidate_gpus.sh` / `nvidia-smi` and use only cards that are genuinely idle. Never kill or displace another process.

One independent `(condition, seed, schedule)` run uses one exposed GPU. Parallelism is across independent runs, not DDP. This both avoids cross-node communication and maximizes useful parallelism when only some cards are free.

Same-seed shared/split should use the same GPU model. If not, Gate-1 analysis refuses PASS.

## 12. Environment policy

Prefer an existing local virtual/conda environment.

First inspect Python, PyTorch, CUDA, Transformers and datasets versions. Reuse an environment if compatible. Only create a new project environment if dependencies are absent/conflicting or the existing environment cannot safely be modified.

Expose the local package with either editable install or `export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"`.

## 13. Mandatory execution order

1. Pull and record frozen commit SHA.
2. Select/reuse compatible existing environment.
3. Prepare data with `scripts/prepare.py`.
4. Run `scripts/preflight.py`. Any failure stops GPU allocation.
5. Run unit tests.
6. Inventory actual free GPUs on the seven candidate hosts.
7. Run shared and split smoke seed 11 on a free GPU.
8. Run `verify_step0_identity.py` on the two checkpoint-0 directories.
9. Reload/evaluate both final smoke checkpoints and confirm exact shared/split row pairing.
10. Dispatch ten Gate-1 fast jobs to available idle cards; queue the rest rather than changing batch size.
11. Evaluate the exact same terminal update for all ten runs.
12. Run `scripts/analyze.py` exactly once on the frozen primary data.
13. Record all results/deviations here before any new experiment.

## 14. Gate 2 — learning dynamics

Only if Gate 1 survives. Use the same held-out contexts at saved checkpoints and track `delta_form(t)`, `delta_post_local(t)`, and true-cognate controls.

Competing trajectories include early transfer -> interference -> recovery/separation; immediate interference; persistent facilitation without contextual cost; or no target-specific effect. The desired contribution is behavioral acquisition dynamics, not merely embedding similarity over time.

## 15. Gate 3 — path dependence

Only after Gates 1–2 justify it.

Compare EN -> DE -> identical balanced tail vs DE -> EN -> identical balanced tail.

The two paths must consume the same deterministic per-language sample sequences. This is enforced with independent EN and DE RNGs. After equal first/second phases, both RNG states are identical before the tail; the balanced-tail language plan also starts from the same RNG state.

Path config additionally uses constant learning rate, zero warmup, and optimizer reset at the common-tail boundary. These controls remove LR-stage and Adam-momentum explanations.

The claim is not simply “training order matters.” The core later estimand is:

`(EN->DE - DE->EN)_shared - (EN->DE - DE->EN)_split`

measured after the common tail. A generic order effect in both conditions is ordinary sequential-learning/forgetting, not lexical-sharing hysteresis.

## 16. Specificity gate

If needed after the causal effect exists, compare false friends against public matched monolingual homonyms / language-unique controls. Do not build a large hand-crafted dataset merely to save the story.

## 17. Results log

- 2026-08-21: literature audit and initial implementation created.
- 2026-08-21: two-pass code/scientific audit hardened target sources, exact occurrence masks, pair-level holdout, step-0 identity, one-in/one-out softmax, optimizer-update semantics, crossed word×seed inference, frozen code/data/config provenance, and path-dependence controls. No scientific result yet.

**Current status: ACTIVE — Gate 1 audited implementation ready for server runtime smoke; no positive claim has been made.**
