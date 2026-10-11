# False Friend Lab — Lexical Sense Resolution Under Competing Evidence

**Active question (2026-10-12):** How do multilingual language models combine lexical familiarity, language identity and contextual semantic evidence when they suggest different interpretations of the same word form?

Status: exploration only. **No model experiment or mechanism discovered in this reset.** This supersedes the old A/B/C research queues and the predetermined E0–E5 mechanistic pipeline.

## Why this is a natural, important, nonempty question

- Stingray and Tanwar establish word-meaning failures and language/context effects.
- Doppelganger-JC shows word meaning, contextual meaning and translation/copy are different behaviors.
- Kallini and Škrjanec analyze global lexical transfer and target-form predictability, which are NOT measures of conditional sense selection.
- Dumas, Körner and Ravisankar demonstrate causal interchange of concept/language/task representations, including misleading answer-copy confounds.
- Human BIA+ and Good-Enough theories motivate competing explanations; they are not proofs of LLM mechanisms.

We do **not** claim cue conflict has never been studied. Tanwar already tests high/low semantic constraints; merely testing a new factorial matrix has weak novelty. We seek **an explanatory account that predicts new conflicting-cue cases**, including a result that might be explained by ordinary frequency and skill.

## Competing explanations

**M0: Predictable evidence integration.** Lexical sense familiarity, the actual language of the sentence, task/output language and independently calibrated semantic evidence combine approximately additively. A simple model predicts the result on unseen word types.

**M1: Conditional cue selection/routing.** One cue changes how strongly another cue is used; a robust interaction makes M0 fail on held-out words, after ordinary WSD, lexical frequency, syntax, cue strength and response format are controlled. This describes a behavioral hypothesis, NOT a discovered internal language-gating module.

**M2: Output copying or verbalizer artifact.** Internal/behavioral semantics are adequate; translation string or answer tokens are wrong. Must compare with independent, non-copy semantic entailment questions.

**M3: Missing lexical knowledge or ordinary ambiguity.** Model doesn't know target sense in explicit-language unambiguous context, or same-language polysemy matches the entire effect.

## High-information, adaptable discovery program

1. **Source and instrument preflight.** Reuse published Tanwar word meaning and high/low semantic-constraint sentences, Doppelganger-JC word/context/translation tasks, and source-filtered Romance WiC. Audit exact surface form vs lemma, linguistic provenance and held-out lexical families. Audit scripts and source counts are in [experiments/FIRST_PASS.md](experiments/FIRST_PASS.md). No forced new benchmark or large annotation campaign.
2. **Reproduce nearest existing baselines first**, with authors' prompts and scores rather than our separate pilot instrument. Record model and tokenizer revisions; one fixed accessible multilingual model first.
3. **Make new, independently testable predictions.** On validated items, independently calibrate language and semantic cues, compare each alone versus aligned/conflicting combinations. Freeze a simple M0 prediction on training lexemes, test unseen word types; compare M1 only with held-out generalization and meaningful effect size. Include same-language polysemy, unambiguous paraphrase, free translation and independent semantic consequence tasks.
4. **Only if M0/M2/M3 fail predictively**, follow the observation: isolate source-language versus semantic positions; conduct paired reciprocal activation patches including Ravisankar-style same-answer-label different-content donors and unrelated-task checks. If a broad patch can trivially rewrite answers, that is not a mechanism claim.
5. **Generalize or stop.** Freeze the smallest explanation on new lexemes, model families or languages. A simple sufficient account closes the question; a surprising interaction demands discriminating follow-up, not instant neuron hunting.

At each stage, specify two models that make **different predictions**, decide what would falsify them, and let data choose the next experiment. Avoid treating the figure order as a mandatory pipeline.

## Immediate verified data result

The ACL 2026 Romance WiC source has 704 word-pair rows; 332 identical lemma spellings, 189 of which are context-level different-meaning pairs. Only 69 different-meaning rows contain the identical case-sensitive word form as a whole word in **both** contexts (58 distinct language-pair/form keys). These are candidate objects only; orientation/POS/meaning still require human review, and the source's same-sense labels do NOT certify matched full lexical sense distributions.

The author's Tanwar Task 3 EN-DE/ES/FR high/low cue CSV files are public; no reason to reinvent a context-strength benchmark to claim novelty.

## Discontinued hypothesis programs

The predetermined lasting late-context semantic trace, incorrect-anchor graph/topology training and language-order hysteresis plans are **removed from the active research program**, not parked as work queues. Why they were rejected and when their historical motivation remains relevant: [knowledge/ideas/RETIRED_HYPOTHESES.md](knowledge/ideas/RETIRED_HYPOTHESES.md). Old source papers remain in the scientific knowledge base.

Start at [knowledge/README.md](knowledge/README.md), [knowledge/ideas/ACTIVE_QUESTION.md](knowledge/ideas/ACTIVE_QUESTION.md), and [experiments/FIRST_PASS.md](experiments/FIRST_PASS.md). The [AGENTS.md](AGENTS.md) protocol is compulsory for local agents.
