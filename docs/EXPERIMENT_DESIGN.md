# Experimental protocol v0.1 — from behavioral anomaly to falsifiable mechanism

This protocol defines **what must be observed before more expensive work**, not a commitment to find a particular effect.

## Measurement before theorizing

### Units

- Lexeme type: primary sampling unit; distinguish capitalization, morphology, exact surface identity, frequency and POS.
- Context family: shared semantic proposition / target sense across deliberately paired manipulations; retain all variants with family_id.
- Model and tokenizer revision: fixed before testing; record both exact commits.
- Prompt: answer label order is **always swapped**, and scores are reported within family.

### Current pilot measure

Paired correct-minus-foil log-likelihood margin over *A/B answers*. Positive indicates correct-gloss preference under this task. It is not calibrated sense probability or evidence of information "inside a neuron". Score both labels with the same proper unconditional next-token vocabulary; reject tokenizer prefix resegmentation.

Potential problems: English gloss comprehension; translation competence; prompt-induced label bias; option ordering; distractor plausibility; lengths; binary forced choice; model's instruction-following. Required controls: independent alternative gloss paraphrases, explicit versus implicit language, foil balance, multiple prompt families and free-answer check on a held-out subset.

### Item gates

- Lexical sense pair and language identity independently checked by two reviewers; provenance and permitted data license retained.
- Exact same target form required for the main stress test; orthographic near-matches analyzed separately, not silently normalized.
- Sentence naturalness, POS and morphology independently reviewed.
- No source corpus training/evaluation leakage if later training; no translation-pair leakage.
- Within-language polysemy and non-homographic paraphrase controls must be credible before claiming cross-lingual specificity.
- Frequency/sense dominance documented when possible; never infer dominant sense from resource class alone.
- Sample items rejected on **semantic** grounds before choosing favorable models or prompts.

## E0 → E1: establish a discriminating phenomenon

Construct pilot item families (not an inflated sentence benchmark). Required per-family comparisons:
- Ambiguous cross-lingual surface in natural context.
- Same intended proposition rendered without cross-lingual surface collision; document lexical-substitution costs. Ensure §target_form§ is absent from the **entire paraphrase prompt**, not only the sentence; use §focus_form§ to identify the replacement.
- Analogous within-language ambiguous word matched in syntax / sense frequency where feasible.
- Free-form translation compared with binary meaning selection; count copying separately.

**Decision:** if only free translation is affected while meaning selection is robust, switch explanation to lexicalization/copy and assess novelty against Körner 2026; do not claim semantic-interference persistence.

## E2: competition and evidence arrival (requires positive E1)

Two orthogonal factors:
1. Language prior: explicit language cue vs implicit, keeping target proposition stable; code switching as pre-registered separate condition.
2. Disambiguating evidence: semantic strength and timing. Separate *pre-target prefix*, *immediately post-target*, *later post-target*, and *completed sentence* contexts using a controlled incremental prefix construction.

Do not treat a fully supplied post-evidence sentence as a measure of revision through time. E2 tests require time-ordered prefixes, matched length/punctuation where possible, and an additional **downstream consequence** (e.g. inference about selected referent) not reducible to choosing the just-seen surface string.

Predictions:
- Prior dominance: language cue moves the initial sense preference with stable semantic evidence.
- Incomplete revision: after an identical final disambiguating cue, the earlier misleading condition leaves a residual difference in downstream semantic behavior (beyond generic late-cue controls).
- Copy-only: free translation changes, but meaning tasks consistently reflect correct revised sense.
- Knowledge deficit: failure persists under multiple clear target-language contexts and paraphrases.

A single nonzero group effect is insufficient; test a **difference-in-differences against ordinary polysemy and matched paraphrase controls**. Report sign, item variation, confidence intervals, plausible alternatives and every failed manipulation.

## E3: inferential constraint, not cherry-picked probing

For selected items, separately verify (a) target sense can be recovered under unambiguous conditions; (b) competitor sense is behaviorally dominant before disambiguation; (c) downstream inference is sensitive to corrected sense. Only then perform decoding/geometry diagnostics. A linearly decodable feature is *not* proof of use or the mechanism of revision.

## E4: conditional, selective causal tests

Use source/target prompts matched for:
- token boundaries, target position, grammar, language and semantic role (except manipulated factor);
- answer verbalizers, task and target semantic reference;
- overall model competence.

Swap language-related vs semantic-evidence-related activations separately in both directions. Include shuffled patch, irrelevant positions, baseline replay and no-ambiguity word. Report both intended effect and collateral behavior changes. Pre-specify what observation would reject each mechanism. Avoid declaring modules from single-layer or broad residual-stream patching alone.

## E5: holdout prediction

Freeze:
- lexical holdout set; no word-type leakage,
- model families and tokenizer revisions,
- primary contrasts, candidate predictor definitions and rejection criterion,
- analysis script/seed and annotation adjudication.

Evaluate conditional prediction and calibration of which cases show residual erroneous sense after correction. An explanation without predictions on untouched words is downgraded to exploratory.

## Statistical constraints

Word-level resampling, context-family pairing, prompt-order pairing, crossed model replication where appropriate. Do not flatten repeated contexts into thousands of independent samples. Report model-specific estimates plus cross-model variation; never report exploratory bootstrap as a decisive p-value. Demo items are never allowed into scientific claims.

## Stopping rules

1. Invalid object or independent semantic annotation fails: stop and revise dataset.
2. Balanced meaning test fails to reproduce the effect: drop semantic-interference claim.
3. All apparent effects are explained by ordinary ambiguity/context difficulty: drop cross-lingual specificity.
4. Only global patching fixes performance and controls fail: no localized mechanism claim.
5. No held-out generalization: stop strong explanatory story.

The strongest experiment is the one whose outcome would **force us to abandon our preferred explanation**.
