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

## 2026-10-11 — Literature KB and route correction

**Decision:** Build a real paper-centered knowledge base with per-paper idea-origin reconstruction, reading confidence, nearest-neighbor distance, experiment logic and cross-paper concept/causal graphs. Historical literature matrix is kept but superseded.

**Scientific course correction:** Tanwar's context tests, Doppelganger's three tasks, Körner's polysemy/copy patching, and Amouyal's garden paths directly threaten A novelty. A now means only A0 cheap identification. B is independently assessed through a formal/synthetic B0 intervention preflight; C remains parked. Neither A nor B has experimental evidence in this repository. Reference: knowledge/ideas/ROUTE_REASSESSMENT.md.

**Verification discipline:** mark unread paper/appendix and inferred author ideation accurately; a bibliographic catalog is not equivalent to full deep reading. All current paper records have traceable source URLs and separate fact/inference claims.


## 2026-10-12 — Retire old A/B/C and switch to data-led sense arbitration

**Decision:** There are no three standing candidate research tracks. Discontinue mandatory late-sense-revision experiments (too close to Good-Enough, Tanwar and Amouyal; contextual copying confound), discontinue wrong-anchor graph-topology training (Kallini covers overlap, global/form endpoints not a strict contradiction, invalid old controls), discontinue early-language-order training hysteresis (ordinary forgetting and recency plausible). Remove them from active docs; preserve historical reasoning as a rejection record only.

**Open question:** how do lexical familiarity, language identity and contextual meaning evidence combine to determine a word's selected sense? Do not assume a literal gating circuit. Compare additivity, conditional routing, output copying, and ordinary WSD/lexical knowledge accounts; first reproduce the relevant Tanwar/Doppelganger original experiments and audit released lexical objects.

**Exploratory verified evidence:** source-level audit of 704 ACL2026 Romance WiC records found 69 exact-context different-sense rows, 58 distinct pair/form types. Source audit is NOT a model result. Two data preflight scripts and synthetic tests added to repo; actual model inference not run.

**Cho source:** recovered and read 87-page 2026 ICLR original from user's previous uploaded PDF and updated detailed experimental genesis/limitations, including low-rank constructive success, natural covariance evidence, selective ablation, and negative task boundaries. Earlier ICLR2025 complete work remains bibliographic background, not essential for immediate experiment identification.

**Policy:** Before paper writing, recheck nearest works and frozen predictive tests; do not protect retired routes as sunk-cost stories.


## 2026-10-12 follow-up — sharpen test from published asymmetry and source-code observation

Read Tanwar §4.3, original Task3 prompt creation and generation, and Östling–Kurfalı 2026 language-swapped conflicting-fact method. First priority is to test whether the published 70/34 direction difference reflects independently elicited semantic interpretation or **output-cascade effects/hidden source-label conventions**. Created strict-source identifiability audit, its unit tests, and an upstream pinned-source CI replay. This is a methodological finding about task **design**, not a model score. Maintain one explanatory sense-arbitration problem, no return to old A/B/C.


## 2026-10-12 — CPU pilot correctly downgrades evidence

After pinned source audit, executed Qwen2.5-0.5B free-response program test and Qwen2.5-1.5B two-order 3-word gloss scoring. Raw archived GitHub Actions artifacts and descriptive data are documented at experiments/PILOT_FINDINGS_2026-10-12.md. The first stimulus had German noun capitalization risk and target-extraction failures; second had 7/18 raw option-order preference flips. **Decision:** instrument not yet qualified, no latent-gating or correction-asymmetry paper claim, no general GPU scale-up. Do alternative verbalizer/semantic inference validation before testing network mechanisms.
