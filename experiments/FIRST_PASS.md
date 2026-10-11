# First Pass — a study with decisions, not a preset mechanism story

**Status (2026-10-12): source-data inspection completed; no inference/model training results.** The primary value of this project is its explanation of previously studied behavior, not the construction of another false-friend benchmark.

## An actual prioritized decision, not an open-ended benchmark

**P-FIRST:** Tanwar Task3 was designed with **Q1 word language, Q2 word meaning, Q3 coherence** in a single generation. Published report has roughly 70% nonEnglish-word/English-context correction vs 34% the reverse, but this is a **joint answer-label annotation**. First replicate it and test *same-item answer-order/self-conditioning* and *whether the target word's source language can be known from the exact sentence surface*. This is a sharper question than another generic context-strength bar plot. [Audit note](../knowledge/notes/TANWAR_IDENTIFIABILITY_AUDIT.md).

A second closest neighboring paper, [Östling & Kurfalı 2026](../knowledge/papers/ostling-kurfali-2026-conflicting-language.md), already demonstrates language bias in conflicting facts under swapped evidence languages; don't claim language-conditioned conflict is new.

## Closest published baselines to reproduce

1. [Tanwar et al. bilingual word processing](https://github.com/EshaanT/Bilingual_processing_LLMs) contains task1 word-sense discrimination, task2 semantic judgement, and task3 high/low semantic constraint for EN-DE/ES/FR. Reuse their original prompts, targets and code for a true baseline. Task3 is masked-word prediction in **prior context**, NOT late-evidence revision.
2. [Doppelganger-JC](https://github.com/0017-alt/Doppelganger-JC) contains isolated meaning, contextual meaning and translation of Chinese/Japanese same/near form. Its word/context/translation task contrast is already a substantial contribution; a naive reproduction is not new.
3. [Abuín et al., Romance WiC](https://github.com/mrtva/false-friends-vs-cognates) commit a87b73e387a6ef86d0cef7ffe703150905e75d7a: six original TSVs with contextual same/different meaning labels. Use only as source inventory and task-level semantic relationship measurement; no causal whole-distribution aligned-control claims.

Our existing run_behavior.py (label-order-balanced two-gloss score) is **different from the original published metrics**. Keep original and additional results separate. A positive forced-choice score is not the posterior of latent sense.

## Executable source-only preflights (no GPU or network inside scripts)

Clone the two published data repositories locally, or supply previously downloaded originals:

~~~bash
git clone https://github.com/mrtva/false-friends-vs-cognates.git
python scripts/audit_romance_wic.py \
  --source-dir false-friends-vs-cognates \
  --output outputs/romance_audit.json

git clone https://github.com/EshaanT/Bilingual_processing_LLMs.git
python scripts/audit_tanwar_baseline.py \
  --source-dir Bilingual_processing_LLMs/data \
  --output outputs/tanwar_audit.json

python -m pytest -q
~~~

Rome data strict **case-sensitive whole word** filter (actual checked from GitHub source):
- 704 total word-pair rows; 332 word-pairs have identical W1/W2 strings.
- 189 exactly identical word-pairs with R=0 contextual different-meaning; 143 with R=1 contextual same-meaning.
- Of these, **69 R=0 and 64 R=1** have that identical lexical form appearing exactly as a standalone whole word in both C1 and C2.
- The 69 R=0 records cover **58 unique (language pair, lexical form)** candidate types.
- 52 R=0 rows lack a POS slash; this does not mean a valid POS match.
- Some items use inflection in actual contexts even if W1==W2; many human and auto subsets share lexemes. Neither row number nor form count equals independent scientific lexical observations.
- The language pair from a filename does not guarantee W1/C1 corresponds to the first named language for every row; audit orientation independently.

Output status is SOURCE_DATA_PREFLIGHT_NOT_SCIENTIFIC_RESULT, with manifest annotation_verified_for_new_experiment=false. **Do not publish numerical claims about LLM performance from these counts.**

## Proposed initial scientific experiments — NOT YET EXECUTED

**T1 — published baseline fidelity first:** run original Tanwar Task 3 with fixed model and authors' metric and original prompts, record exact base model/tokenizer SHAs, per-word and per-language result distribution, available source vs target language usage. Do the same for Doppelganger-JC three tasks. Avoid treating paper's isolated word meaning item as an automatically valid contextual sense judgment.

**T2 — do apparent errors survive a meaning-only task?** Compare the same lexical senses on context judgement, independent referent/entailment questions and translation/copy outcome, using native-verified gold. If semantic reasoning is correct but translation copies the form, no evidence for hidden sense competition.

**T3 — independent cue calibration and conflict:** for prequalified words, separately rate contextual evidence and model prior under language-only, semantic-only, congruent and conflicting evidence. Freeze simple additive predictions from nonconflict cue cells and test on lexeme-disjoint held-out conflict cells, compare with an interaction/routing predictor and an ordinary same-language ambiguity baseline. Avoid arbitrary code-mixing that yields unnatural sentences.

**T4 — conditional causal intervention only on diagnostic residuals:** if T3 shows reproducible, held-out non-additivity in non-copy semantic inference, identify one precise contradiction; compare selective semantic- and language-cue patches with wrong-semantic/same-answer-label controls. If broad patching merely supplies answer strings, stop.

## What is a negative result?

- No lexical competence even in clear target-language sentence: knowledge-deficit, no competition claim.
- Wrong outputs only in translation strings: copying/output artifact, no sense-selection mechanism claim.
- Generic within-language ambiguity fully predicts differences: no false-friend-specific effect.
- Additive model predicts held-out cases and interacts no worse than complexity-penalized models: no fancy internal gating story necessary.
- Unable to create grammatical, matched and independently valid cross-cue cases: invalid contrast; stop, don't handcraft favorable data.

## Baseline implementation boundary

No model weights or user GPU server are mounted through this conversation. Source audits and Python unit tests have been implemented; actual LLM baseline running is a future separate execution on an accessible machine. GitHub CI only validates code / synthetic fixture behavior, not experimental results.


## Pinned-source GitHub Actions replay (2026-10-12, VERIFIED source-only)

The external published-source audit job cloned and checked out:
- Tanwar: 281a67eac6ddbe5445e1c10277e5833d40d72125; Task3 EN-DE/EN-FR/EN-ES each **280** rows (140 COGNATE + 140 FALSE COGNATE) and 0 rows with missing <MASK> across the four low/high language context fields.
- Abuín Romance: a87b73e387a6ef86d0cef7ffe703150905e75d7a; 704 paired records, 69 R0 strict-context rows covering 58 language-pair+form units.

[Source-data audit logs](https://github.com/Nhckdvrl/false-friend/actions/runs/38155507571) · [JSON output artifact](https://github.com/Nhckdvrl/false-friend/actions/runs/38155507571/artifacts/11707823643).

These are validated **data structures and case-sensitive surface filters only**, not model-performance findings or independent reannotation of semantic labels. Baseline language-model runs and original paper metrics are pending access to a suitable model environment.
