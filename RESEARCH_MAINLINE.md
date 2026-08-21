# Research Mainline: When Does Lexical Sharing Turn from Transfer into Interference?

_Last updated: 2026-08-21_

This is the canonical research record. Do not promote later experiments if an earlier causal gate fails.

## 1. Core research question

> When two languages reuse the same lexical form, does sharing the lexical representation improve prediction of that form while harming language-specific contextual/semantic use when the meanings conflict? If so, when does transfer turn into interference, and can early learning history leave a persistent lexical-semantic bias?

This project does **not** ask whether false friends are merely difficult. The causal object is **lexical sharing itself**.

## 2. Central intervention

For the same real EN-DE lexical target and the same natural bilingual corpus:

- **shared**: exact English and German lexical occurrences use the same base token row;
- **split**: English uses the base row; exact German lexical occurrences use a reserved alias row.

Both conditions have the same model shape, vocabulary size, parameter count, seed, initialization tensors, training data, sampled chunks, optimizer settings, and optimizer update count.

Alias rows are copied from their base rows at initialization in both conditions, so paired shared/split models are tensor-identical at update 0.

Crucially, split remapping is driven by an **exact lexical-occurrence mask** derived from tokenizer offsets. A matching subword id inside a compound/derivative is not remapped.

## 3. Why EN-DE first

EN-DE is the first causal gate because it combines StingrayBench false-friend/common resources, Kallini et al.'s controlled EN-DE overlap precedent, OPUS-100 natural parallel data, and the closest shared-vs-language-specific lexical-representation precedent from CMCL 2026.

Japanese-Chinese and Arabic-Hebrew are replication candidates only after EN-DE survives.

## 4. Q1 / Gate 1 — causal form-context dissociation

For each strict held-out natural target context measure:

1. **surface_nll**: `-log(P(base target row) + P(alias row))` at the target position. This measures the observed surface probability and avoids a mechanical one-class-vs-two-class artifact.
2. **lexical_nll**: NLL of the condition-specific lexical row. Diagnostic only.
3. **post_nll**: mean NLL of the next `k` natural tokens.
4. **pre_nll**: mean NLL of the preceding `k` tokens; negative control.
5. **local_surface = surface_nll - pre_nll**.
6. **local_post = post_nll - pre_nll**.

Default `k=8`.

Strong FF pattern:

- `Δ_surface = shared - split < 0`;
- `Δ_post > 0`;
- `Δ_local_surface < 0`;
- `Δ_local_post > 0`.

Specificity:

`Δ_local_post_false_friend - Δ_local_post_true_friend > 0`.

Frequency-adjusted specificity controls total lexical frequency and EN/DE frequency imbalance.

This is initially a **form-context dissociation** claim. It becomes a semantic-fidelity claim only after explicit sense-disambiguation confirmation.

## 5. Gate 1 data rules

Training corpus: `Helsinki-NLP/opus-100`, `de-en`, up to 1M pairs.

Target source: StingrayBench `en_de` false friends and `en_de_common` controls.

Automatic filtering:

1. require one shared orthographic surface string;
2. require exactly one stable XLM-R token sentence-initial and mid-sentence;
3. find natural corpus occurrences using tokenizer character offsets and exact standalone boundaries;
4. require minimum exact occurrence count in **both** languages;
5. deterministic **parallel-pair-level** holdout: if a selected pair is held out, neither side enters training;
6. evaluation contexts must contain exactly one manipulated target occurrence;
7. compact the observed training vocabulary;
8. save aligned exact-occurrence masks for EN/DE training streams.

No new experimental sentences are generated.

## 6. Gate 1 inference

Sentence occurrences are not independent evidence.

Pipeline:

`context -> word × seed × language -> equal-weight EN/DE -> word × seed -> crossed bootstrap(words × seeds)`.

Primary support requires at least 5 paired seeds, 10 FF lexical items with held-out evidence in both languages, and 10 true-friend lexical items with held-out evidence in both languages.

Paired shared/split runs must match initialization SHA256, effective batch size, GPU model, git commit, data schema version, and final update. Any mismatch makes the gate inconclusive.

## 7. Preregistered Gate 1 PASS

`PASS_CAUSAL_FORM_CONTEXT_DISSOCIATION` requires all of:

1. FF raw `surface_nll` effect CI entirely below 0;
2. FF raw `post_nll` effect CI entirely above 0;
3. FF `local_surface` effect CI entirely below 0;
4. FF `local_post` effect CI entirely above 0;
5. FF-vs-TF `local_post` interaction CI entirely above 0;
6. frequency-adjusted FF-vs-TF `local_post` coefficient CI entirely above 0;
7. all four target directions occur in at least 80% of paired seeds;
8. absolute FF pre-target effect is no more than half the raw post-target effect;
9. support/invariant checks pass.

Alternative verdicts include `KILL_CORE_FORM_ONLY`, `WEAK_INTERFERENCE_ONLY`, `KILL_NO_SPECIFIC_CAUSAL_DISSOCIATION`, and `INCONCLUSIVE_*`.

Do not rescue a failed Gate 1 with probes, steering, extra language tags, metric fishing, or cherry-picked checkpoints.

## 8. Q2 / Gate 2 — learning dynamics

Only after Gate 1 PASS. Evaluate matched saved checkpoints and track `Δ_surface(t)`, `Δ_local_surface(t)`, `Δ_post(t)`, and `Δ_local_post(t)` by relation.

Competing trajectories include early transfer -> interference -> recovery/separation; persistent transfer with no context cost; immediate interference; or no relation-specific trajectory.

Do not make embedding-similarity dynamics the paper before a behavioral trajectory exists.

## 9. Q3 / Gate 3 — persistent path dependence

Only after Gates 1-2 justify it.

Compare `EN -> DE -> balanced common tail` and `DE -> EN -> balanced common tail`.

Hard controls:

1. independent deterministic EN/DE RNG streams ensure both curricula consume the same language-specific sample sequences, only reordered;
2. sequential curricula use **constant LR**;
3. after equal EN/DE exposure, the balanced tail begins;
4. Adam optimizer state resets at common-tail start;
5. common-tail data sequence is identical across paths.

A generic order effect is not enough. The key quantity is `OrderEffect_shared - OrderEffect_split`. A lexical-sharing path-dependence claim requires a persistent FF sharing-specific order interaction after the common tail.

## 10. Q4 / monolingual ambiguity specificity

Later low-cost gate only. Prefer monolingual homonyms over related polysemy and avoid constructing a large new dataset. Drop this gate if clean matching becomes more complex than the question warrants.

## 11. Compute strategy: no Slurm

Candidate nodes:

`fvcrc10, fvcrc11, fvcrc12, fvcrc13, fvcrc15, fvcrc20, fvcrc21`.

Not every GPU is available. **Only confirmed-idle GPUs may be used.** Never assume a whole node is free and never terminate other users' jobs.

One scientific run = one GPU. Gate 1 has 10 independent jobs (`2 conditions × 5 seeds`). Run as many concurrently as there are confirmed-idle GPUs; queue the rest. Pair shared/split of the same seed on the same GPU model whenever possible.

## 12. Environment rule

Prefer a compatible existing server environment first. Only create a new virtual environment if dependencies are missing/conflicting. Do not overwrite shared environments.

## 13. Execution order

1. pull the frozen `main` commit;
2. inspect existing Python/torch/CUDA environment;
3. inspect candidate GPUs and choose only idle devices;
4. prepare data once;
5. run `pytest` and `scripts/preflight.py`;
6. if preflight fails, stop scientific GPU allocation and diagnose data/design;
7. run 50-update shared/split smoke on one idle GPU;
8. verify checkpoint reload, non-empty eval, and identical paired initialization SHA;
9. launch the 10 Gate-1 independent runs across idle GPUs;
10. evaluate the same final update for every pair;
11. run `scripts/analyze.py` and record the machine verdict here;
12. only then decide whether Gate 2 is justified.

## 14. Results log

- 2026-08-21: project initialized.
- 2026-08-21: two-pass code/scientific audit completed; strict lexical masks, pair-level holdout, identical alias initialization, optimizer-update semantics, surface-probability metric, crossed word×seed bootstrap, and no-Slurm single-GPU workflow introduced. No scientific result yet.
