# Decision record

## 2026-10-09 — Mainline reset

**Decision:** Replace the failed shared/split lexical-row experiment with a sense-selection/revision question. Keep full prior snapshot as branch archive/lexical-sharing-2026-08. Clean old execution scripts/configs from main; create only a lightweight validated pilot and research documents.

**Rationale:**
- Old natural semantic-aligned control was unidentifiable; invalid ten-run results must not be rescued.
- Nearest papers already occupy vocabulary overlap benefit, false-friend benchmark errors, concept-language representation separation, and homograph-copy corrections.
- A possible gap remains in **separating post-evidence sense revision from output-only lexicalization and generic ambiguity** through matched controls and out-of-sample predictions.
- Cho's transferable feature is a chain of distinguishable predictions and interventions, not quantity of analyses.

**Non-decisions:** no claim of established novelty, no experimental result, no choice of final language pair, no approved human-labeled corpus, no training, no patching architecture, no predetermined main conclusion.

**Re-evaluate after E0:** if no reproducible and matched sense-specific anomaly survives, this direction should be stopped or reframed, even though a polished pipeline exists.

**Engineering caveat:** source code is a pilot. GitHub CI tests deterministic logic only; model-dependent tokenizer and inference behavior requires a real smoke run on chosen open weights.
