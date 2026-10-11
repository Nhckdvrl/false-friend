# Discontinued, not parked: original A/B/C proposal

Decision 2026-10-12. These old tracks are removed from the active research program; preserve original reasoning in Git history and paper notes only.

**A: persistent wrong interpretation after late evidence.** Not sufficiently motivated as a default mechanism: Good-Enough/Christianson and Amouyal already study persistent/garden-path interpretations; Tanwar studies semantic contextual constraints; Doppelganger/Körner show answer-copy/polysemy pitfalls. A late prompt cannot retroactively rewrite a prior token's state in a causal Transformer. No independently verified paired misleading→correction corpus is yet available. Do not build this benchmark by assumption. Follow it *only* if a novel, reproduced anomaly specifically requires reanalysis.

**B: false semantic anchors / global transfer topology.** Kallini already analyzes lexical-overlap semantics; Škrjanec measures *form surprisal*, which is not contradicted by global transfer, while new graph topology assumptions require artificial languages, matched effective capacity and valid softmax normalization. The old EN-DE matched natural controls failed identification. Do not train another tied-vocab model based on this presumed paradox. Keep the prior research as background, not a work queue.

**C: EN-first/DE-first training hysteresis.** Ordinary forgetting, recency, nonconvex optimizer trajectory and language proficiency are strong existing explanations. No demonstrated extra meaning-specific phenomenon makes costly from-scratch training informative. Do not study it without new direct evidence.

**Other nonstarters:** “false friends confuse LLMs,” “strong context helps,” “word form prediction differs from semantic comprehension,” “concept can be patched independently of output language,” “homograph copying fixed by patch,” “late evidence sometimes leaves a wrong interpretation.” All have direct earlier scientific precedents.

## Replacement

See [ACTIVE_QUESTION.md](ACTIVE_QUESTION.md) and [../../RESEARCH_MAINLINE.md](../../RESEARCH_MAINLINE.md). Test calibrated competition between language and contextual evidence; allow simple additive/competence/copy accounts to win; only do mechanistic follow-up on genuine held-out residuals. This is the current hypothesis, not a claim of a unique untouched literature gap.
