# Hossain, Chinnappa & Blanco — An Analysis of Negation in NLU Corpora

- Primary: https://aclanthology.org/2022.acl-short.81/ (ACL 2022 main, short paper).
- Reading S2: §3 Q1–Q3, Tables 1–4 and discussion; not an empirical reproduction.

## Facts and experimental object

The paper measures negation prevalence, manually judges whether removing a negation changes task gold, and compares model performance by this distinction. All negations in its inspected WiC validation subset are classified as unimportant for that task. This is a claim about that subset, not every possible lexical example.

## Idea genesis — INFERENCE

The useful move is to ask whether an operator *should* influence the task before evaluating whether a model responds to it. Negation sensitivity is neither universally desirable nor universally a failure: word identity, proposition truth conditions and sentiment impose different requirements.

## Our critique and nearest-work distance

Performance differences between naturally occurring subsets also reflect difficulty and composition; they do not isolate negation causally. Removing a cue can change grammaticality or a lexical construction, so invariance needs local semantic review.

Our [scope follow-up](../notes/SCOPE_FOLLOWUP_2026-10-13.md) makes negation relevant or irrelevant by changing only the annotated target extent. It therefore tests whether models respect the requested semantic unit, rather than rediscovering that negation is difficult. Authored binary domains keep proposition labels determinate but limit naturalistic generality. The paper gives a reason to preserve lexical gold under negation; it does not independently validate our Chinese translations or every authored item.
