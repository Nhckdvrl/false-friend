# Research Agent Protocol — question-first science

**Current only active topic:** competing language identity versus contextual evidence in multilingual lexical sense choice. Read RESEARCH_MAINLINE.md, knowledge/ideas/ACTIVE_QUESTION.md and experiments/FIRST_PASS.md. Retired A/B/C should not be suggested as live branches without new observations.

## Deep-reading process

For each paper, use knowledge/PAPER_NOTE_TEMPLATE.md. Record author question and its background, key prior explanation, smallest novelty over nearest work, datasets and controls, reconstructed **inferred** idea genesis, experimental step-by-step *why*, limitations and most valuable next falsifier. FACT and INFERENCE must be separate. Register citations and note S1/S2/S3 honestly; do not claim a 19MB PDF was read if only its abstract was accessible.

Compare studies using exact dependent variables: token surprisal, contextual meaning recognition, word translation/copying, multilingual transfer, hidden-feature decoding, mechanistic patch. These cannot be identified with each other.

## Before scientific experiments

- Reproduce original Tanwar/Doppelganger metrics/prompt as baseline when appropriate. Our binary gloss runner is a different metric.
- Validate language side explicitly; filename language pair is insufficient. Check lexical surface, inflection, POS, naturally correct usage, error-injection, relation label scope, source copyright.
- Require word-level holdout and meaningful ordinary WSD / unambiguous controls; label-order swapping and multi-phrase semantics.
- Predetermine which rival accounts make different predictions, which variables are fixed, and what outcome would change the theory. A merely nonzero main effect is not mechanistic evidence.
- No gold-dependent softmax, no interpreting probe decodability as information use, no unselective patch interpreted as a special module.
- Do not automatically progress from baseline to probing or training. Only a strong residual from a simple account justifies additional complexity.

## Required research handoff

1. What naturally important problem are we explaining?
2. Which nearest paper almost already answers it, and what claim is occupied?
3. Which two simplest distinct explanations predict different behavior, in what unit?
4. What source data and task can distinguish them without manufacturing an object?
5. Exact stop/failure criterion and output that would be surprising.
6. Is this a **code preflight**, a reproduced existing finding, a new observed result, or a causal proof? Never conflate.

## Reset discipline

When evidence is inconsistent with the old picture, rewrite the picture rather than rescue it through more metrics, custom data or unconstrained interaction terms. A clear negative or simple explanation can be a scientifically useful endpoint. If there is no valid data contrast, stop before allocating GPUs.
