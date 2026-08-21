# Research Mainline — When Does Lexical Sharing Turn from Transfer into Interference?

_Last updated: 2026-08-21_  
_Final status: **ARCHIVED — CONCEPTUAL_IDENTIFICATION_FAILURE**_

This file is the canonical research record. The full postmortem is in [`docs/FINAL_ARCHIVE_ZH.md`](docs/FINAL_ARCHIVE_ZH.md).

---

## 1. Original core question

> When two languages reuse the same exact lexical form, does forcing them through one shared lexical representation improve prediction of that form while making language-specific contextual use harder when the meanings conflict? If so, when does transfer become interference, and can early learning history leave a persistent bias?

The intended contribution was not the already-established observation that false friends can be difficult. The intended causal object was **lexical sharing itself**.

The motivating literature tension was real:

- false-friend / cross-lingual homograph benchmarks show local semantic-disambiguation failures;
- vocabulary-overlap work shows that lexical sharing can improve global cross-lingual transfer;
- controlled bilingual-model work shows shared forms can have lower surprisal, often strongly affected by frequency.

The project therefore asked whether the same sharing operation could simultaneously produce:

1. a **form benefit**, and
2. a **conflict-specific contextual/semantic cost**.

---

## 2. Intended Gate-1 causal intervention

For the same target lexical form and same natural EN-DE corpus:

### Shared

`EN exact target -> base row`

`DE exact target -> base row`

### Split

`EN exact target -> base row`

`DE exact target -> reserved language-specific alias row`

The primary causal estimand was:

`effect of lexical sharing = shared - split`

rather than a simple observational `false_friend - ordinary_word` comparison.

The final audit-v2 implementation hardened the intervention so that paired shared/split runs had:

- identical model architecture;
- identical parameter count and vocabulary size;
- identical step-0 model tensors;
- alias rows copied exactly from paired base rows;
- identical natural training data;
- identical deterministic per-language sample streams;
- optimizer time defined by optimizer updates, not microsteps;
- pair-level held-out parallel data;
- exact standalone lexical-occurrence masks rather than raw token-id replacement;
- strict one-in/one-out output masking so reserved aliases did not change active softmax cardinality;
- frozen data/config/code/init provenance;
- paired lexical-item × seed inference.

The final audited implementation was frozen at:

`d055f1e0976b0b5cc2ef3bf681cdd197c5317c97`

Algorithmic audit before server execution:

- 8/8 core unit tests passed;
- all Python files compiled;
- synthetic end-to-end analysis recovered a known injected positive Gate-1 pattern.

So the final project failure should not be described as “we could not implement the intervention cleanly.”

---

## 3. What Gate 1 actually needed to identify

A positive paper-level claim required more than a shared/split effect among false friends.

The central specificity claim was:

> **semantic conflict changes the consequence of lexical sharing.**

Therefore Gate 1 needed two naturally identifiable lexical populations:

### Conflict group

`same exact written form + different cross-lingual meanings`

### Non-conflict control

`same exact written form + sufficiently aligned cross-lingual meanings`

The planned strong result was roughly:

- FF: sharing improves form prediction but worsens localized continuation;
- true-friend control: sharing improves form prediction without the same continuation cost;
- therefore FF-minus-control interaction isolates conflict-specific interference.

This design only works if the control category is a valid approximation to:

`same exact form + no relevant semantic conflict in natural usage`.

That assumption ultimately failed.

---

## 4. Frozen preflight result

Using the final frozen implementation without modifying scientific code:

```text
strict Stingray targets before corpus filters:
  false_friend = 65
  true_friend  = 5

targets after natural-corpus evidence gate:
  false_friend = 24
  true_friend  = 3
```

The preregistered support requirement was at least 10 lexical types in each relation.

Preflight therefore correctly returned:

```text
FAIL: only 3 lexical items for true_friend (<10)
PRECHECK FAIL: do not allocate GPUs until fixed
```

No GPU scientific training was launched under the final frozen implementation.

The three surviving nominal true-friend controls were:

| Surface | Approximate resource gloss | Assessment for this project |
|---|---|---|
| `bar` | bar / in cash | semantically conflicting in natural EN/DE usage |
| `Rock` | rock / skirt | semantically conflicting in natural EN/DE usage |
| `intelligent` | intelligent | clean aligned control |

Thus the support problem was actually worse than “3 < 10”: only about one surviving item clearly matched the intended semantic-aligned control object.

---

## 5. Why this is not ordinary insufficient sample size

If the issue were merely that a valid control category had 7 or 8 items instead of 10, the natural response might be to obtain a larger corpus or expand a resource.

That is not what happened.

The deeper issue is that the available category label does not identify the variable required by the causal claim.

StingrayBench is designed for sentence-level cross-lingual semantic / cognate evaluation. For EN-DE it permits orthographic variation such as capitalization differences. That is appropriate for its benchmark task.

Our intervention, however, required the **exact same surface form / token row** in both languages.

For example, a benchmark pair such as:

`English arm` ↔ `German Arm`

can express the same “arm” sense in the intended benchmark sentence. But converting this into an exact-surface natural-corpus target `arm` changes the German lexical object: lower-case German `arm` is an adjective meaning “poor”.

Therefore orthographic normalization can transform a benchmark true cognate into the exact kind of semantic collision that was supposed to define the treatment group.

The problem is conceptual, not a parser bug.

---

## 6. Resource-semantic mismatch

The frozen execution also inspected `en_de_common_words.csv` and found that its meaning fields cannot be used as independent semantic-distribution labels for our purpose.

Observed facts recorded in [`docs/GATE1_STATUS_ZH.md`](docs/GATE1_STATUS_ZH.md):

- all 98 rows have identical `Meaning in L1` and `Meaning in L2` strings;
- several rows contain union-like glosses such as `arm, poor`, `rock, skirt`, `bar, in cash`, `log, lied`, `costs, taste`.

This is compatible with a benchmark designed around common/cognate word usage, but it does not certify:

`P(sense | word, EN) ≈ P(sense | word, DE)`

in natural corpora.

That distinction is decisive because our model is trained on all natural occurrences of a form, not on one selected benchmark sense.

A resource can validly mark that two languages share a sense in a controlled sentence while still failing to provide the **matched full lexical-semantic distribution** needed for a no-conflict training control.

Hence:

> **benchmark category ≠ causal control.**

---

## 7. Why the earlier 10-run result is invalid

Before the final frozen preflight, an earlier branch ran 5 paired seeds × shared/split and produced:

`KILL_CORE_FORM_ONLY`

That verdict is permanently invalid for two independent reasons.

### 7.1 Wrong implementation version

The runs used:

`d8d1b18cf2aa0d2718218775b780adc84f9470a1`

This branch diverged from an earlier base and did not contain the final audit-v2 one-in/one-out causal output normalization.

The old split condition let base and alias rows coexist as softmax competitors, introducing an extra repulsive training signal between the two lexical rows.

This contaminates the intended sharing intervention.

### 7.2 Runtime modification of the control definition

The first strict preparation had too few true-friend controls. The runtime execution then widened the target extraction by treating capitalization variants as independent surface candidates.

This changed the scientific object and admitted semantically conflicting forms into the nominal control group.

Therefore the old FF-vs-TF interaction cannot be interpreted.

### 7.3 Old FF-only diagnostic

The invalid implementation produced, among 24 FFs:

- `Δpost = -0.011`, CI `[-0.049, +0.025]`, expected direction in 0/5 seeds;
- `Δlocal_post = -0.014`, CI `[-0.064, +0.033]`, expected direction in 1/5 seeds.

These numbers lower confidence in the hypothesis but remain **diagnostic only**. They are not a valid negative scientific finding.

---

## 8. Why we do not build a new matched control dataset

A technically possible rescue is to manually construct a semantic-aligned exact-form control set.

To make that control credible, we would need to inspect or match at least:

- exact orthography;
- tokenizer identity;
- part of speech;
- dominant sense;
- secondary senses / polysemy;
- sense-frequency distribution by language;
- total lexical frequency;
- EN/DE frequency imbalance;
- contextual diversity;
- potentially semantic distance and morphology.

At that point the project is no longer a fast natural causal experiment. It becomes a bespoke bilingual lexical-semantic dataset-construction project.

This is precisely the warning sign identified in earlier failed topics:

> When the gate and kill-line structure keeps expanding because every claimed effect must first be distinguished from many neighboring explanations, the underlying research question may not be naturally identifiable.

The controls here are not growing because of ordinary rigor around a clean object. They are growing because the supposedly simple “non-conflicting shared form” is not directly available as a stable natural category.

Therefore we do not rescue the topic by manual control construction.

---

## 9. Why we do not run FF-only Gate 1

The 24 strict false friends are themselves a viable treatment set.

One could run only:

`shared vs split on FF`

and ask whether `Δpost^FF > 0`.

This can falsify a necessary condition. But if positive, it cannot establish the intended claim that **semantic conflict specifically** causes interference, because there is no matched non-conflict sharing baseline.

The possible result would therefore be asymmetric:

- negative: potentially informative kill signal;
- positive: insufficient to support the paper story.

Given that the main causal specificity contrast has already failed identification, and the invalid older run already provided an unfavorable diagnostic signal, this one-sided experiment is not worth further GPU budget.

---

## 10. Why we do not immediately change language pair

A language pair with more exact orthographic overlap, such as Indonesian-Malay, may improve the form side of the problem.

But exact orthographic overlap does not automatically solve the deeper requirement:

`same form + sufficiently matched natural sense distribution`.

Changing language pair would require a new corpus, new lexical inventory, new semantic-control audit, new tokenization study, new frequency analysis and a new preregistration.

That should be evaluated as a separate future candidate topic, not treated as a patch to this project.

Current project: stop.

---

## 11. Final failure classification

### Correct classification

`ARCHIVED — CONCEPTUAL_IDENTIFICATION_FAILURE`

### Incorrect classifications

Not `HYPOTHESIS_REJECTED`:

- no valid final Gate-1 scientific run occurred.

Not `ENGINEERING_FAILURE`:

- the audited intervention and analysis pipeline passed local algorithmic checks;
- the frozen preflight stopped before scientific GPU allocation exactly as designed.

Not merely `INSUFFICIENT_SAMPLE_SIZE`:

- the nominal control category itself does not reliably correspond to the required semantic-aligned causal object.

The central failure is:

> The intervention was identifiable, but the semantic specificity contrast was not.

---

## 12. Lessons for future topic selection

### 12.1 Run an identifiability preflight before implementation

Before writing training code, ask:

1. Does the treatment object actually exist in the data?
2. Does the control object actually exist in the data?
3. Does the public label operationalize the variable required by the claim?
4. Can 10–20 randomly selected examples survive manual inspection under the exact causal definition?

If not, kill before coding.

This project should likely have ended after inspecting examples such as `bar`, `Rock`, and `arm/Arm`.

### 12.2 Separate paper labels from causal variables

For every reused benchmark category, explicitly write:

`literature label -> operational definition -> causal variable`

and verify all arrows.

“True cognate” sounded close enough to “semantic-aligned exact-form control” that the distinction was initially skipped. That was the key mistake.

### 12.3 Audit the control arm before the treatment arm

A visually compelling treatment phenomenon is easy to find. A causal paper is often limited by whether the counterfactual/control is clean.

Future candidate topics should inspect the control resource first.

### 12.4 Treat increasing gate complexity as a topic-quality alarm

Additional controls are justified when they isolate a well-defined causal object.

They are a bad sign when they are needed to manufacture the object itself.

If a simple claim requires custom annotation of POS, polysemy, sense frequency, orthography, context, morphology and frequency before the basic comparison exists, reconsider the question rather than continuing to harden it.

### 12.5 Distinguish three failure types

- **Valid negative**: a valid experiment rejects the hypothesis.
- **Invalid experiment**: an implementation/data deviation makes results uninterpretable.
- **Identification failure**: the experiment cannot naturally instantiate the causal comparison required by the claim.

This project ended in the third category. The old 10-run result belongs to the second.

### 12.6 Preflight was successful even though the project failed

The final preflight did exactly what a good kill system should do:

- stopped before GPU allocation;
- exposed insufficient control support;
- triggered semantic inspection;
- prevented another misleading “result”.

So the methodological takeaway is not “preflight failed”.

It is:

> **preflight successfully killed an invalid research path before additional compute was spent.**

---

## 13. Reusable engineering assets

The following remain technically useful:

- exact lexical occurrence masking;
- pair-level parallel holdout;
- step-0 paired initialization identity;
- one-in/one-out softmax normalization;
- optimizer-update semantics;
- deterministic per-language sampling;
- paired occurrence coverage checks;
- word × seed crossed bootstrap;
- frequency-adjusted specificity analysis;
- frozen data/config/code/init provenance;
- single-idle-GPU independent-run orchestration without Slurm;
- fail-fast preflight structure.

They are retained as historical infrastructure, not as an active experiment plan.

---

## 14. Reopen conditions

Default: **do not reopen**.

Reconsider only if a future public resource provides, without substantial bespoke annotation:

1. enough exact same-surface bilingual lexical controls;
2. independently verified semantic alignment appropriate to natural-corpus training;
3. sufficient natural frequency in both languages;
4. a small manual audit that confirms the causal category before implementation;
5. new evidence that materially increases the prior probability of conflict-specific sharing interference.

Otherwise this project remains closed.

---

## 15. Final results log

- 2026-08-21: literature audit identified a possible form-benefit / semantic-cost tension.
- 2026-08-21: initial EN-DE shared/split causal pipeline implemented.
- 2026-08-21: two-pass algorithm/scientific audit fixed exact-occurrence masking, pair-level holdout, step-0 identity, one-in/one-out output normalization, optimizer-update semantics, deterministic sampling and crossed lexical-item × seed inference.
- 2026-08-21: an earlier 10-run `KILL_CORE_FORM_ONLY` result was invalidated because it used pre-final code and a runtime-modified control definition.
- 2026-08-21: final frozen implementation `d055f1e...` was executed through data preparation and preflight only. Result: 24 FF / 3 nominal TF; preflight FAIL; no scientific GPU run launched.
- 2026-08-21: semantic audit showed the nominal true-friend resource does not identify the required exact-form matched semantic-distribution control. Two of three surviving nominal controls were themselves semantically conflicting.
- 2026-08-21: project archived as `CONCEPTUAL_IDENTIFICATION_FAILURE`.

## Final decision

```text
ARCHIVED — CONCEPTUAL_IDENTIFICATION_FAILURE
Gate 1: no valid scientific adjudication; stopped at causal-control preflight
Gate 2: CANCELLED
Gate 3: CANCELLED
Mechanism / hidden-state probes: CANCELLED
Full-scale confirmation: CANCELLED
Further GPU allocation: 0
Old KILL_CORE_FORM_ONLY: INVALID, DO NOT CITE
```
