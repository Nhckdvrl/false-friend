# Ok & Lee (Findings ACL 2026) — Lost in the Prompt Order

- Official PDF: https://aclanthology.org/2026.findings-acl.1921.pdf
- Reading depth: **S1**, main text §§1–5, Figs.1–6, Tables 1–2, intervention descriptions; appendix theoretical details noted, not rerun.
- Family: general causal prompt organization / attention mechanism. **Not** specifically multilingual lexical sense.
- Closest predecessor: prompt/order sensitivity, lost-in-the-middle, option/order MCQA effects.

## Natural science problem and idea scale

Changing prompt component order in a decoder should leave the evidence content intact, yet context–question–option (CQO) outperforms question–option–context (QOC) by **14.72 percentage points** on average across 21 decoder-only models and 4 RC datasets. Previous work documented formatting sensitivity but not why. The innovation is **mechanistic exclusion of rival explanations**, not another prompt technique.

## Where the idea probably came from (INFERENCE)

Authors notice a reliable surprising task outcome and immediately ask *which of three causal stories is compatible*:
1. Training distribution favors CQO → matched base/instruct gap and 0–5 shot QOC examples should repair if true.
2. Options are "lost in the middle" → direct option-recall test should fail if true.
3. **Causal attention**: in QOC option tokens are encoded BEFORE the context; thus their representations are context-blind, putting comparison burden on final decoding position.

They test #1 and #2 first, then the #3 mechanism; this structure resembles Cho's **counterexample→rivals→targeted intervention→boundary** more than a simple ablation table.

## Main experimental chain (FACT)

- Figs.1/3: CQO-vs-QOC 14.72 pp average; matched base/instruct and in-context examples do not remove the gap.
- Fig.4: option recall remains high under QOC; rejects ordinary middle-position forgetting as the leading explanation.
- Fig.5: encoder and encoder-decoder architectures have much smaller CQO–QOC gap; QOC is approximately as bad as QO without the context.
- Fig.6: relative option attention and gradient attribution reveal reduced use of context evidence when options were encoded before it.
- Table2: directly prune option-to-context attention in CQO → ~26.8 pp decline; patch context-aware CQO option states into QOC → ~6.0 pp improvement; repeat options AFTER context in QOCO → ~8.2 pp improvement; CoT reduces gap to 7.47 pp.
- Explicit scope: authors' information-theoretic argument establishes **option state independence of future context** in a causal decoder, not a complete theorem about all QA task decisions or hidden "semantic gate" mechanisms.

## Decisive lesson

An experiment is strong because **rejected rivals make the final mechanism necessary** to explain the controlled observation; targeted attention pruning and rescue demonstrate both effect directions. The simplest observation alone was known. A recent high-quality paper need not invent an unseen problem.

## Important difference from our Tanwar prompt-order control

Our issue is **Q1 answer is generated before Q2**: Q2 can causally attend to generated Q1, regardless of context presentation order. Ok & Lee examine **where question/options occur relative to evidence before decoding**. They are NOT the same manipulation. But their paper proves prompt-order and architecture can confound accuracy, and suggests testing which representations become context-conditioned under altered question order rather than interpreting output correlations as latent word-sense mechanisms.

## Next falsifier for us

If isolated Q2, Q1-first and externally fixed Q1 produce the same host-sense preference on human-validated items, then prompt self-conditioning is not a sufficient explanation for Tanwar direction effects. If scores vary, must next rule out generic question-order sensitivity with non-homographic synonyms and unrelated semantic tasks, rather than immediately publish a multilingual mechanism.
