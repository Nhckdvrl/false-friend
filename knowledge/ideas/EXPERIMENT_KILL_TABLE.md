# Claim-first experiment design: what observation would change our mind?

Each row is a **possible decision**, not a mandatory experiment or published preregistration. Do not build code before verifying stimulus identity, data provenance and controls.

| Candidate | Strong claim | Best rival explanation | Decisive contrast | Failure / downgrade | Incremental knowledge |
|---|---|---|---|---|---|
| A0 | False-friend collision creates **additional** lingering wrong semantic belief | ordinary polysemy + late cue cost | (cross-lingual collision vs ordinary ambiguity) × (misleading vs neutral history), hold target final meaning, ask non-copy semantic consequence | zero interaction / only task verbalizers differ | specific boundary of generic revision |
| A1 | Correct sense learned but not used after correction | sense never known to model | separately verify target sense in clear native context, then infer consequence of identical final meaning | target sense unknown even in unambiguous context | availability vs conditional use |
| A2 | Wrong sense remains in semantics, not just output string | homograph copying / answer-word prior | compare paraphrase, downstream inference, translation, balanced A/B glosses and independent prompts | inferred meaning correct, only translation copies | output-artifact boundary, probably already close to Körner |
| A3 | Language and semantic signals have selectively different causal roles | broad patch copies answer label / is off-distribution | reciprocal aligned patches, same-answer-different-semantics donor, unrelated positions/meanings | randomized or answer-label-only donor works equally | selective causal influence conditional on controls |
| A4 | Explanation predicts other lexical items | token frequency, template memorization | lock predictor on training lexemes then test unseen word families and different tasks/languages | not better than frequency/majority baseline | predictive generalizable mechanism |
| B0 | Wrong shared anchor's benefit is identifiable | unequal vocabulary/optimizer normalization | hand-verify formal conditional next-token probability, shared vs split active class and effective capacity; paired data | gold-dependent denominator or unmatched capacity remains | validity of causal object |
| B1 | Semantic correctness differs from structural connectivity | pooled token frequency/capacity | correct vs wrong vs random anchors at matched frequency/number/size, vary graph connectivity independently | all effects follow total token count or parameter tying | topology vs frequency vs semantic bridge |
| B2 | Global transfer gain coexists with local *meaning* loss | perplexity task mismatch | same model/task family: semantic inference, form surprisal, global compositional transfer | loss only seen in token-copy tasks | validated multiscale tradeoff |
| C0 | Learning history creates meaning-specific hysteresis | recency and catastrophic forgetting | EN-first / DE-first / interleaved, equal data, Adam reset, same balanced long tail, conflict vs nonconflict | disappears with tail or follows overall proficiency | order × conflict specificity |
| C1 | Hysteresis can be predicted | random seed / trivial nonconvexity | word-level held-out order effect predictions and matched global skill | no transferable prediction | mechanism, not raw trajectory |

## Evidence distinctions to preserve

- Form surprisal is not the posterior of a latent word meaning. Forced-choice candidate logits are also not such a posterior.
- Multiple prompts for one lexeme are **nested**, not separate independent words; keep word and family-level pairing in analysis.
- A late-evidence test cannot claim to have retroactively rewritten preceding hidden states in a standard causal Transformer; measure the new end-position computation.
- A broad activation patch that helps answers is only sufficiency under one intervention; it does not identify unique natural processing route.
- If a simple rival predicts all observations, stop the elaborate story instead of adding a probe, new model or larger Appendix.
- Valid negative, invalid implementation and *unidentifiable contrast* are different outcomes: see legacy record.

## Smallest next two experiments (not yet executed)

**A0 preflight:** draw candidate lexemes from reviewed Doppelganger/Abuín/Tanwar/Stingray resources; sample blind human review, identify a small four-cell matched set with clean semantic consequence judgments; run one instruction-capable open-weight model as an exploratory diagnostic only if preflight succeeds. There is no finished revision corpus yet.

**B0 preflight:** specify a synthetic probabilistic bilingual environment where same-base vs alias rows permit a **single gold-independent predictive softmax** across all candidate outputs and compare effective capacity; provide mathematical invariance checks before any GPU training. If this cannot be made meaningful, don't code the model.

### A/B fork decision

A0 supported unique interaction but B0 unidentifiable → A. A0 null, B0 clean and genuinely discriminating → B. Both unidentifiable/null → return to paper review; no new experiments. Both feasible → choose by expected explanatory gain and nearest-work distance, not programming sunk costs.
