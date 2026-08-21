# false-friend

> **Status: ARCHIVED — CONCEPTUAL_IDENTIFICATION_FAILURE (2026-08-21)**

This repository investigated one causal multilingual lexical-learning question:

> **When does lexical sharing turn from transfer into interference?**

The intended experiment asked whether forcing the same exact lexical form in English and German through one shared lexical representation would improve form prediction while harming language-specific contextual/semantic use when the two languages assign conflicting meanings.

The project is now **archived**. The reason is not a valid negative experimental result. The core causal control — an adequate set of **exactly shared bilingual forms with genuinely aligned semantic distributions in natural corpora** — could not be identified from the available public resource without introducing substantial new manual semantic construction and increasingly elaborate matching gates.

## Read this first

- [`docs/FINAL_ARCHIVE_ZH.md`](docs/FINAL_ARCHIVE_ZH.md) — **final archive decision, complete failure analysis, and lessons**.
- [`RESEARCH_MAINLINE.md`](RESEARCH_MAINLINE.md) — canonical research history and final stop decision.
- [`docs/GATE1_STATUS_ZH.md`](docs/GATE1_STATUS_ZH.md) — last frozen-implementation preflight before the final archive decision; historical execution record.
- [`docs/AUDIT_2026-08-21.md`](docs/AUDIT_2026-08-21.md) — two-pass code/scientific audit of the causal implementation.
- [`docs/LITERATURE_AUDIT.md`](docs/LITERATURE_AUDIT.md) — literature and open-source audit that motivated the original question.

## Final outcome in one paragraph

The audited implementation itself reached a clean causal intervention: shared/split models could be matched in architecture, parameter count, step-0 tensors, data, sampling, optimizer updates and effective softmax cardinality. The project failed one level earlier: Gate 1 required a false-friend treatment group and a semantic-aligned exact-form control group. Under the frozen pipeline, 24 false friends survived but only 3 nominal true-friend controls survived the exact-form/evidence gate; two of those three (`bar`, `Rock`) are themselves semantically conflicting across English and German. The underlying `en_de_common` resource is suitable for its original sentence-level cognate benchmark, but it does not identify the natural-corpus object required here: `same exact form + matched cross-lingual sense distribution`. Therefore the causal specificity claim is not identifiable with this resource.

## Important result-status distinction

There are three different events in the history of this repository:

1. **Old 10-run result — INVALID.** An earlier 5-seed shared/split run used commit `d8d1b18`, which predated the final one-in/one-out softmax hardening, and its true-friend extraction was changed at runtime. Its `KILL_CORE_FORM_ONLY` verdict must not be cited as a scientific result.
2. **Frozen audit-v2 preflight — VALID STOP.** Commit `d055f1e0976b0b5cc2ef3bf681cdd197c5317c97` passed the algorithmic audit, but strict data preparation returned 24 FF / 3 TF and preflight correctly refused GPU allocation.
3. **Final project decision — ARCHIVED.** Further work would require constructing and validating a bespoke bilingual semantic-control dataset. That would change the character of the project from a fast natural causal test into a data-construction project and was judged not worth pursuing.

So the project did **not** establish either:

- “lexical sharing causes semantic interference”, or
- “lexical sharing does not cause semantic interference”.

It established that the proposed experiment, as naturally formulated with the available EN-DE resource, lacks an identifiable semantic-aligned control.

## What remains useful

The repository preserves reusable infrastructure for future controlled lexical-sharing experiments:

- exact standalone lexical-occurrence masking;
- pair-level parallel holdout;
- shared/split step-0 tensor identity;
- alias/base one-in-one-out softmax normalization;
- optimizer-update semantics;
- deterministic paired sampling;
- word × seed crossed bootstrap;
- frozen data/config/code/init provenance;
- fail-fast preflight design;
- no-Slurm, one-idle-GPU-per-independent-run execution.

The code is retained as a historical research artifact. **Do not resume Gate 1 / Gate 2 / Gate 3 from the existing plan unless the project is explicitly reopened under the conditions in `docs/FINAL_ARCHIVE_ZH.md`.**

## Final decision

```text
ARCHIVED — CONCEPTUAL_IDENTIFICATION_FAILURE
Gate 1: no valid scientific adjudication; stopped at causal-control preflight
Gate 2: cancelled
Gate 3: cancelled
Mechanism/probe work: cancelled
Further GPU budget: 0
```
