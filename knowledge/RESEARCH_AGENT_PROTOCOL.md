# Local Agent Research Protocol — mandatory for this repository

The knowledge base is a **research instrument**, not a memory dump. Current repo is hypothesis development without empirical discovery. A polished figure cannot make a weak question strong.

## Before touching code

1. Read RESEARCH_MAINLINE.md and knowledge/README.md, then select relevant branches in knowledge/PAPERS_INDEX.md.
2. Open **full relevant core paper notes and source URLs**, especially the nearest two works; S3 references remain *unread for mechanism claims*. Any assertion of novelty needs a 2026-aware re-search.
3. Separate FACT, INFERENCE and PROPOSAL. Authors' motivations not stated explicitly can only be reconstructed and labeled INFERENCE.
4. Read knowledge/CONCEPT_MAP.md to catch metric category mistakes, theories for human analogy, and knowledge/ideas/EXPERIMENT_KILL_TABLE.md before proposing a new experiment.
5. Write, *before implementation*, the rival-generating mechanism, mutually differentiating predictions, operational data definition, required control, exact result that would change the conclusion, and the nearest literature's coverage.

## When reading a new paper

Create knowledge/papers/<slug>.md using PAPER_NOTE_TEMPLATE.md. Register it in PAPERS_INDEX.md, CITATION_LEDGER.md (for strong claims), concept map and idea-genesis graph as appropriate. Mark S0/S1/S2/S3 honestly based on accessed content; never promote reading level merely due to a paper's fame. Include page/figure references and specific unresolved verification tasks.

**What matters most:** explicitly reconstruct plausible idea sources and *scale*. Was it a new question, a new error isolation, a causal manipulation, a hidden-variable control, a stronger baseline, a predictive theory, or merely additional examples? Which existing paper does it most resemble, and what is the shortest nontrivial step forward? Avoid irrelevant dense summaries.

## During experiment construction

- The data label must operationalize the exact causal variable, not a similarly named resource category.
- Validate source license, semantic object, sentence naturalness, POS, case, morphological identity, tokenizer segmentation; do not use surname/category as a shortcut.
- Never use target-label-conditioned softmax normalization to compare alternative outputs. If two candidates change the output probability denominator by their ground truth, probability design is invalid.
- Do not collapse form surprisal, selected sense, downstream semantic consequence, free translation, global transfer, and activation decodability into one metric.
- Never infer causal *use* of information from a linear probe. Never claim a unique module from indiscriminate patching.
- For each analysis report cross-item variation, model/prompt dependence, uncertainty and failures; avoid sentence pseudo-replication.
- Record precise data revision, sample IDs, model/tokenizer commit and prompt text.
- Do not run GPU until cheaply verifying sample/control identifiability. Reuse the archival branch only for historical lessons; not its old Gate 1 as new scientific evidence.

## Direction change

A failed clean test can be an important fact; record it without rescuing the story. Failed data identification is not evidence for or against the hypothesis. If a strong new paper already makes the same claim, **downgrade novelty and update docs**, don't invent artificial conditions to make the original wording novel.

## Required research handoff format

- Current strongest question and why important independent of machinery.
- Exact strongest neighboring paper and what it has **already** proven.
- Up to three live rival hypotheses with different predictions.
- Minimal valid discriminating experiment and stop condition.
- What remains unknown after a result in either direction.
- Source and degree of verification for every empirical assertion.

## Review cadence

Update paper notes when experiments reveal new confounds. Reopen the novelty audit before writing an abstract and after a major new result; do not treat 2026-10-11 index as permanent coverage.
