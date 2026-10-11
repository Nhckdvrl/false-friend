# First CPU LLM instrument tests (2026-10-12)

**Exploratory only. No claim about internal language gating, no reproduction of Tanwar paper's 70/34 correction rates.** Raw published source and model revisions are pinned in JSONL run artifacts.

## Run 1 — Qwen2.5-0.5B original/order/meaning only

[CI and full six-output artifact](https://github.com/Nhckdvrl/false-friend/actions/runs/38158541047). One exact FF source item 180: `brand` EN and DE, two opposite-host sentences × three question orders. Original Q1 language→Q2 meaning→Q3 coherence; variants Q2 first and only Q2. The 0.5B model sometimes answered about German `Holz` instead of the target `brand`. German common noun `Brand` normally needs capitalization, so exact lowercase `brand` creates a grammar confound. **Result: this is not a valid semantic effect, only a program/stimulus smoke.**

## Run 2 — Qwen2.5-1.5B, 36 full-vocabulary label scores

[CI and complete 36-trial/18-pair JSON artifacts](https://github.com/Nhckdvrl/false-friend/actions/runs/38159224806). Three source ADJ items preselected AFTER the invalid brand smoke (not preregistered scientific sample): `genial` ID261, `blank` ID264, `stark` ID272. English/German high semantic-constraint host sentences, English candidate glosses from author's `en_de_dataset.csv`, both A/B orderings, and three externally set Q1-language cues: none, host, other.

Mean log p(intended host-language gloss label) minus log p(competing other-language gloss label), after swapping A/B order (positive = within-this-task host-gloss preference):

| Form | Host | None | Q1 claims host language | Q1 claims other language |
|---|---|---:|---:|---:|
| genial | EN | 5.826 | 4.361 | 3.988 |
| genial | DE | 5.348 | 4.921 | 4.943 |
| blank | EN | 6.730 | 5.669 | 5.676 |
| blank | DE | 1.308 | 1.628 | 0.654 |
| stark | EN | 3.256 | 2.595 | 0.949 |
| stark | DE | 0.597 | 5.618 | 0.994 |

No model sampling or automatic gold annotations occurred; word meanings/naturalness not independently re-reviewed. All 18 two-order mean margins were positive, but source meaning gloss lengths/phrases differ and there is **no inference from 3 words**.

**Measurement warning:** 7/18 conditions reversed the correct-versus-foil sign when correct option moved from A to B. 14/18 had absolute difference over 2 nats; mean absolute order gap = 3.905 nats (max 6.134). A fixed label prior can be cancelled by order averaging, so this is NOT proof the balanced estimator is invalid. However, variable large order effects make single-order "correct semantics" accuracy untrustworthy. Source glosses are context proxies, not a latent sense posterior.

Example: German `stark` shifted from mean +0.597 (no cue) to +5.618 with externally supplied language=German. This **does not establish** that natural model Q1 language attribution caused internal word-meaning change. It is one item, with new question format and unreviewed verbalizer controls.

## Why this is high-information even though null on mechanism

This stage distinguished:
- *semantic selection* from *generative question-following failure* in a tiny model;
- *grammatically valid source* from the artificial exact-form constraint;
- *apparent sense choice* from response-label-position bias;
- externally supplied answer conditioning from an unmodified network's internal selection.

One good data anomaly is not yet a paper. We should qualify measurement BEFORE invoking an internal gate, just as Cho did not equate constructive filtering with ICL's naturally used mechanism.

## Follow-on discriminating experiment

1. Independently review more source lexemes/senses, including adjective morphology and native sentence naturalness; retain ordinary WSD controls.
2. Compare semantic scoring under A/B, 1/2, yes/no entailment and independent paraphrases. Use source item × prompt order as nested unit; don't interpret prompt rows as independent words.
3. Reproduce the original Tanwar Q1→Q2→Q3 generation and human scoring on a capable multilingual model, with clean/source-observable items; compare Q2-only, Q1-first, Q2-first, and externally fixed Q1. No inferred lexical language gate unless a residual is stable and predicted in unseen words.
4. If apparent source bias vanishes when output self-conditioning / unidentifiable labels are addressed, stop that mechanism story. Do not rescue with more patching.
