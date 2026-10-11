# Three-route reassessment — 2026-10-11

**State: conditional research choices, not established gaps.** Value is defined by a new causal explanation or out-of-sample prediction, not novelty from changing language pair, model size or metrics.

## Executive correction

A was first because behavioral datasets are easy. Its **novelty risk is high**: Tanwar studies semantic constraints; Doppelganger-JC separates meaning/context/translation; Körner has patch-based word copying and polysemy corrections; Amouyal/Good-Enough already studies late misinterpretation. An ordinary high-vs-low-context evaluation would be derivative.

B might offer more theory if the result from Kallini that low-semantic-similarity token overlap helps global transfer survives clean frequency/capacity controls and has an unexpected local semantic boundary. But the apparent contrast with Škrjanec is not a logical contradiction: global task transfer and target-form surprisal have different dependent variables.

C has a natural question but EN-first/DE-first bias is expected from continual learning and needs far better specificity to be interesting.

**Operational decision:** A0 (small, source-derived behavior audit) and B0 (analytic/synthetic identification preflight) compete. Neither gets full implementation or GPU by default. C parked.

## Route A: cross-language sense commitment and revision

**Question:** Does identical-form cross-language competition cause residual *downstream semantic use* after clear corrective evidence, beyond ordinary same-language polysemy and generic late-context difficulty?

**Closest studies:** Tanwar 2026 (sense, high/low constraint), Doppelganger-JC 2025 (word/context/translation), Körner 2026 (polysemy/copy patch), Amouyal 2025/26 and Christianson (garden-path residual interpretation).

**At least four rival hypotheses:**
- A-K: target sense isn't known; explicit language + strong natural context still fails.
- A-P: sense known but dominant language prior wins; label/target-language cue and relative usage frequency determine error.
- A-G: generic ambiguous sentence reanalysis; identical residual is found in within-language polysemy or garden-path controls.
- A-O: output copying/answer token priors; semantic inference correct but translation wrong, and answer label swaps change performance.
- A-R: genuine persistent wrong *semantic commitment*; corrected final context still gives excess, cross-language-specific wrong-sense downstream inference beyond these controls.

**Minimal falsifier:** source-audited 10–20 cross-language type examples and similar generic ambiguity controls. Crossed factors (same-form collision yes/no) × (misleading prior context yes/no), with balanced early and late cues **holding final sense fixed**. Primary outcome is non-copy downstream semantic consequences (at least two independent formulations); also inspect gloss-choice and translation as diagnostic outcomes. Lexical type is sampling unit; pre-register number of contexts and model.

**Not enough:** comparison of two completed prompts differing in token order, grammaticality or recency. Standard causal Transformer states for prior token positions are not retroactively changed when later tokens arrive. Later tokens compute new interpretations. A late-vs-early effect is not uniquely a revision failure; require a cross-language-specific **difference-in-differences**, sensible length/position controls, and ordinary ambiguity baseline.

**Abort if:** semantics can't be independently validated, target meaning not reliably available even in disambiguated contexts, no cross-language interaction, or anomaly appears only in free translation and collapses in semantic inference. If meaning works but translation copies, switch to output artifact and assess novelty against Körner instead of calling the model confused.

**If positive:** first account for source-language prior, then use one targeted activation interchange with reciprocal controls and a donor of *same answer label but unrelated semantic content* (Ravisankar precedent). Demand preservation of unrelated meaning and output behaviors. Freeze predictions on held-out words; no success story from hand-picked heads.

**Scientific leverage:** medium–high IF interaction/prediction exists. Practical first step cheap, full causal identification hard. Very high overlap risk with previous research.

## Route B: why can incorrect lexical anchors be beneficial?

**Question:** What exactly provides transfer benefits when shared token identities connect different language meanings: correct semantic bridge, pooled counts, smaller effective parameterization, or graph connectivity?

**Closest studies:** Conneau 2020 transfer without overlap; Winther 2021 pooled frequency; Kallini 2025 high/low overlap; Škrjanec 2026 frequency and form surprisal; Limisiewicz 2023 task-specific vocab effects.

**Mechanisms with divergent predictions:**
- B-F frequency: effective pooled counts alone; at fixed counts and positions wrong anchors offer no special benefit.
- B-C capacity/regularization: any parameter tying helps, irrespective of semantic matching, with effect governed by number of free degrees of freedom.
- B-S semantic bridge: correct anchors uniquely improve transfer at equal effective capacity and frequency.
- B-T structural connection: even wrong anchors may align otherwise separated distributional manifolds; benefit follows connectivity/coverage, not individual sense agreement.

**Minimal causal preflight:** synthetic two-language, shared latent semantic micro-world with controlled vocabulary/permutation mapping. Conditions semantic-correct anchor vs semantic-wrong permutation vs random anchor vs disjoint; freeze same corpus, grammar, latent concept distribution, number of anchor tokens, counts and active prediction options. Use several permutations and seeds to avoid accidental correct mapping. Evaluate global compositional held-out transfer, local sense decisions, and form surprisal **separately**.

**Hard identification warning:** exact parameter count is not equivalent to exact effective model capacity. Gold-target-conditioned output masks do not define a shared proper next-token distribution (legacy bug). Rebuild a valid probability model before believing any result. Synthetic token systems do not establish natural-language FF behavior; a later natural replication is needed.

**Abort if:** apparent benefit vanishes with capacity/frequency control, only copies tokens, or mapping variants make target data distribution incomparable. Do not use old natural EN–DE true-cognate extraction as a rescue.

**If positive:** derive simple measurable predictor (e.g., graph coverage/anchor connectivity) and test held-out remappings, then ask if it transfers to realistic language pairs. Novelty would be *predictive causal condition*, not another global leaderboard.

**Scientific leverage:** potentially high; compute medium, methodological risk high; theory might be deeper than A if the intervention exists cleanly.

## Route C: lasting learning-history effects

**Question:** Can different exposure orders lead to durable, meaning-specific lexical policies under **matched final bilingual experience**, and can this be predicted independently of generic forgetting?

**Closest studies:** Elhady/Agirre/Artetxe continued pretraining and forgetting, Arnett bilingual ordering and priming, Inaba representation dynamics.

**Rivals:** C-R recency/forgetting (effect vanishes after balanced tail); C-O optimizer path effects (different states because nonconvex training, but no semantic specificity); C-S conflict-specific hysteresis (language×order×conflict interaction survives balanced tail and predicts held-out ambiguous terms).

**Design, if reopened:** EN→DE, DE→EN and interleaved schedules, matched sample counts and random seeds, same stable LR, optimizer reset before identical balanced tail, report both short/long tail behavior and global L1/L2 competence. Distinguish persistent *semantic decision* from differences in embedding geometry. Use non-conflicting words and generic L2 tasks as negative controls.

**Abort if:** just generic L2 forgetting, recency, small model capacity or idiosyncratic random seed. Learning trajectories differing is **not** a novel result by itself.

**Decision:** parked. No C GPU budget without an A/B-driven, identifiable mechanism question.

## Relative comparison (qualitative)

| Trait | A | B | C |
|---|---|---|---|
| Existing data for E0 | High | Synthetic needed | Corpora/training needed |
| Novelty overlap | Very high | High but explanatory uncertainty | High with learning-order work |
| Critical confound | Generic ambiguity, copying, cue timing | Frequency, active softmax, capacity, artificial world | Recency/global forgetting |
| Most valuable possible result | Predictive cross-language-specific semantic revision condition | Causal reason wrong anchors help/hurt | Meaning-specific, nonrecency hysteresis |
| Cheapest next step | Small factorial item audit | Formal estimand/preflight | Literature review |
| Current action | A0 only | B0 only | Park |

**Stop rule for all:** if no controlled observation requires a new explanation, stop. The existence of a repository or sophisticated harness is not an argument for continuing.
