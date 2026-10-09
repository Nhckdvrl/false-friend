# Research Mainline — Cross-Lingual Sense Selection and Revision

*Reset: 2026-10-09. State: candidate mechanism problem / behavior preflight, not established scientific result.*

## 0. The one question

**How does an LLM choose among competing language-specific meanings of a shared form, and when does subsequent context revise that choice rather than merely changing a final output string?**

False friends are a *stress test* of this question, not necessarily its cause. The project must survive the possibility that a model has no enduring semantic conflict at all.

### Why this is not already answered

StingrayBench establishes cross-lingual sense-disambiguation failures. Kallini et al. establish that vocabulary overlap usually aids **global** transfer, and Škrjanec et al. find form-level surprisal facilitation, strongly related to frequency. Dumas and Körner et al. show that multilingual concepts/output language can be causally manipulated, and Körner et al. already find homograph copying and polysemy artifacts in apparent patching gains. These findings measure different dependent variables. None alone identifies the causal locus of *a specific contextual correction after an initially misleading cross-lingual reading*. But this is a **candidate explanatory gap**, not a claim of proven novelty.

## 1. Competing hypotheses (non-exclusive)

| H | Mechanism | Distinctive prediction | What would count against it |
|---|---|---|---|
| K — Knowledge deficit | No sufficiently reliable representation of the intended sense | Explicit target-language sense identification fails even in strong unambiguous contexts | The model robustly identifies the intended sense under matched explicit-language prompts |
| P — Prior competition | Both senses available; dominant language/lexeme prior overwhelms local cue | A language cue changes meaning selection even with near-fixed sentence semantics; lexical frequency moderates | Controlled language cues leave sense decisions unchanged once competence is matched |
| R — Incomplete revision | An initially preferred sense persists after decisive late evidence | Position-matched late evidence leaves a residual competitor-sense effect in a downstream *meaning* test, not only in free translation | Once final semantic evidence is matched, any apparent residual vanishes in meaning-only and matched controls |
| O — Output/copy artifact | Sense selection is adequate; generation lexicalizes/copies a misleading form | Controlled sense-choice succeeds while free-form translation fails; output-sensitive interventions change strings without changing sense judgments | Stable sense-decision failures survive label swaps and no-copy controls |

H1–H4 are **diagnostic possibilities**; avoid introducing a separate experiment family for each before establishing an anomaly. Multiple mechanisms can coexist.

## 2. Sequential experiment logic — each link answers a missing inference

### E0. Item validity and phenomenon existence — cheap, before GPU

Independently inspect language, exact form, lexical senses, POS, naturalness, morphology, sense dominance and source license. First compare a few existing open models under a balanced gloss-choice task. Include (i) genuine cross-language false friends, (ii) ordinary within-language polysemy, (iii) unambiguous/paraphrase controls. Primary unit is lexical type, not repeated templates.

**Stop** if high-quality matched items or reproducible excess error do not exist. Do not manufacture true-friend controls simply to fill sample quotas.

### E1. Is the apparent mistake actually semantic?

On the same context/lexeme, compare (a) counterbalanced forced-choice sense judgment, (b) optional paraphrase/inference consistency, (c) free translation / copying behavior. Difference between (a) and (c) diagnoses an output confound; it is not itself causal proof of distinct modules.

**Stop** if order/template sensitivity alone explains the supposed semantic mistakes.

### E2. Competing evidence: language cue × context strength × evidence position

Build *human-audited* minimal pairs, factorial when feasible. Crucially hold the final interpretation constant while varying whether decisive information is present before or only after the ambiguity. For post-target revision, evaluate prefixes and final sequences as separate tasks; Transformer layer index is **not** psycholinguistic time.

Counterbalance item direction, answer order, prompt framing, semantic plausibility, lengths and language proficiency. Compare equivalent non-homographic replacement, ordinary polysemy, and translation vs sense-choice tasks.

**Key contrast:** a late-evidence residual competitor effect that exceeds corresponding generic revision effects, not merely lower accuracy on late cues.

### E3. Is the competing sense represented, selected, or output-only?

First use intervention-free diagnostics on matched correct/error trials. Separate information *decodability* from *causal use*. If no robust E2 effect, E3 is forbidden. Probe results alone do not justify representation mechanism claims.

### E4. Targeted causal intervention: necessity, specificity, mediation

Only after E2/E3 produce discriminating predictions: paired activation patching of language cues vs sense evidence vs output context, with reciprocal directions, unrelated-position and random-vector controls, semantic invariance checks, prompt-token alignment, and no global linguistic collapse. Avoid claiming localization from broad residual-stream patching.

A strong outcome is **double dissociation** of meaning judgments and output form; a simpler full-activation correction is already close to Körner et al. 2026 and has weak novelty.

### E5. Out-of-sample prediction

Freeze theory, predictors, thresholds and control set. Predict which *held-out lexical types/context families* will show (i) correction, (ii) persistent competition, (iii) copy-only errors. Evaluate on different models and ideally another language pair. A theory that only describes hand-picked patched examples fails.

## 3. Metrics — no substitution

Primary pilot: within-item, label-order-balanced log probability margin

  m_i = 1/2 [(log p(A | prompt[A=correct]) - log p(B | prompt[A=correct])) +
             (log p(B | prompt[B=correct]) - log p(A | prompt[B=correct]))].

Positive m means greater *conditional model preference* for the intended gloss, not a calibrated sense probability and not a hidden-state measurement.

For revision, define an independently audited final-context contrast, e.g. m_late - m_early, only where the semantic gold remains unchanged and matched controls exist. An uncorrected direction-specific effect is not sufficient. Keep task-conditional margins distinct from generation string accuracy and form surprisal.

Cluster at lexical type (and context family/model where relevant). No sentence-level pseudo-replication. Preregister effect thresholds based on reliability, not post hoc significance. The current scripts produce **descriptive** summaries only.

## 4. Why not reuse the old shared/split training pipeline?

Archived Gate 1 was *not* a negative scientific result. Its semantic-aligned natural control could not be identified; the 10 older runs were invalid. There is also a separate unresolved likelihood-design concern: the final one-in/one-out mask switches the candidate normalization according to the **gold next token**, which does not define a standard common next-token distribution for comparing alternative candidate outcomes. See docs/LEGACY_RECORD.md.

From-scratch training returns only if natural behavior reveals a specific causal question for which controlled training changes a prediction. Synthetic form–meaning mapping experiments may help internal validity, but must be distinguished from natural-language evidence.

## 5. No predetermined success story

- If most errors are **copy-only**, write that, then ask whether the output mechanism offers a nontrivial new explanation beyond Körner.
- If language cue solves everything, a failure of context-free language identification may be the simple explanation.
- If semantic competition is no greater than ordinary polysemy, the cross-lingual-specific hypothesis dies.
- If the discrepancy is not robust to choices of task and lexical items, stop.
- If E4 patching corrects everything indiscriminately, it does **not** demonstrate selective mechanism.
- If E5 cannot predict held-out cases, claims stay descriptive.

Novelty is measured by *excluded rival explanations and successful novel predictions*, not the number of experiments, model sizes or probes.

## 6. Research assets and next real actions

- Complete an independent literature novelty audit, prioritizing Körner 2026 and Dumas 2025, plus explicit late-evidence/revision works. See docs/LITERATURE_MATRIX.md.
- Create ~50–100 **candidate** lexical items (not a target quota to force), then check 10–20 randomly drawn entries and two independent annotators. Existing resources are discovery aids; their category tags are not gold causal objects.
- Pilot one open multilingual causal LM only after E0 review. Keep held-out lexical families sealed.
- Commit only empirical results with model SHA, tokenizer SHA, prompts, code hash, raw scores and failures. No claim before rerun.

**Decision:** Active question = sense selection and revision. Alternative hypothesis = false anchors/global transfer as a later independently scoped project. Training-order path dependence = parked. Do not conflate them.
