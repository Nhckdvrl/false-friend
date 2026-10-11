# Östling & Kurfalı 2026 — Language Bias under Conflicting Information in Multilingual LLMs

- Source: https://arxiv.org/html/2604.07123v2
- Read level: S1 — methods ``3–5, tables, discussions and key appendices inspected; no claim every supplemental table verified.
- Closest predecessors: Kurfalı & Östling 2025 conflicting-needles; earlier long-context retrieval and repetition/recency bias.

## Scientific question and idea origin (INFERENCE)

Existing conflicting-needles tests found models often report just one of two incompatible facts, biased by position, repetition and **name string**. An elegant next variable is evidence language: exchange the language containing the exact same conflicting fact, hold identifiers and placements constant, and test whether the selected answer follows the language rather than the name. This extends an old problem with a discriminating intervention; not a “completely new research area.”

## Actual design (FACT)

Five languages EN/DE/ZH/RU/TR; naturalistic news haystacks with two conflicting pseudofacts, pseudo-random article positions and language assignments, 900 haystack settings × five query languages per model, 12 models, short and long context. Language-swap contrasts ask whether output follows evidence language; hierarchical Bayesian log-odds summarize biases across models/prompts. Added reduced-format-prompt and monolingual nonconflicting retrieval controls.

## Evidence, limitation, and idea scale

Models mostly deliver one answer, rarely explicitly mention contradictions. They show bias against Russian and in some long-context cases for Chinese; prompt-language often preferred. However, the authors report that **language was the decisive factor in only a minority of contrastive pairs**; surface/name and other factors dominate many cases. Their main contribution is *an experimental separation of the signal of language from alternative conflict-selection cues*, not a general internal gating mechanism. They explicitly leave mechanism identification future work.

Critical confounds: 25k-word contexts, translated articles, factual retrieval and model/prompt dependencies. These are not the same variables as the lexical sense of an **identical form** in one local sentence. Their two conflicting facts have distinguishable language sources, whereas a literal same-form word can have an **underdetermined source label**.

## Our nearest-work distance / discriminating prediction

We cannot publish “conflicting bilingual evidence shows language bias.” Already known. Instead exploit the *observable source language* gap between two-fact retrieval and lexical homographs. If word-source identity is not identifiable from the stimulus, a model cannot recover the dataset's hidden source-language index except from instructions. The first experiment must establish this measurement identifiability and remove answer-format self-conditioning, before trying to locate a lexical cue-selection mechanism.
