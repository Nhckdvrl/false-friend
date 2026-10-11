# Hakaze Cho et al. 2025/2026 — Experimental design from a small ICL counterexample

- ICLR 2025: [Revisiting In-context Learning Inference Circuit](https://proceedings.iclr.cc/paper_files/paper/2025/hash/22d4f952efa13970f0b1ffb22170d416-Abstract-Conference.html). Reading: S3 official abstract and relevant citations in the 2026 full paper; the 2025 complete PDF is too large for the current public tool, so **do not claim its every experiment has been independently verified**.
- ICLR 2026: [Mechanism of Task-oriented Information Removal in ICL](https://proceedings.iclr.cc/paper_files/paper/2026/hash/105112d52254f86d5854f3da734a52b4-Abstract-Conference.html), official [code](https://github.com/hc495/Verb_subspace). **Reading S1: full 87-page manuscript recovered from previous user-provided Library file, read complete main text, appendix methods, critical tables and all figure captions; individual supplemental plot traces are not all independently replotted.** Not an empirical reproduction.
- Additional detailed experiment-chain and boundary note: [CHO_FULL_PAPER_RECONSTRUCTION_2026.md](../notes/CHO_FULL_PAPER_RECONSTRUCTION_2026.md).

## Important problem (fact)

The dominant induction/label-copy account of ICL predicts failure if demonstration labels never contain the correct output token. But in a real unseen-label condition, some nonzero ICL performance survives. A good mechanism paper asks **what extra operation is needed** rather than declaring all induction work wrong.

## Idea genesis — our INFERENCE, not an author autobiographical claim

Notice zero-shot last-query vector contains several plausible task attributes, e.g. Donald Trump can be encoded with President, Human, Male; arbitrary plausible completion may emerge without specifying which task. The interesting intervention is not adding evidence but **removing all dimensions not useful for the selected task**. A trained low-rank task-verbalization subspace (TVS) can prove such filtering is constructively sufficient. But this *cannot* prove ordinary model ICL does it. Hence novel measurements of spontaneous few-shot state ensembles; those are observational, so proceed to selective targeted ablation. Then examine cases where low-rank information removal should be insufficient.

This inference chain is what we should emulate, not attention head hunts or making every experiment complex.

## Actual experimental design and role of each step

**Step 1: Explicit filtering, Fig.1–3, §3, §4.2.** Freeze backbone, insert trained WencWdec low-rank filter into query's zero-shot residual state at a selected layer; optimize filter to output target label, mask preceding-token dependencies beyond that point; evaluate **full vocabulary open-end greedy output**, not an artificially restricted pair of labels. Appendix documents approx. 2048 training and 512 validation examples, multiple ranks and layers. Fig.3 successful even with small rank. Check covariance retained outside top-r to address rival "filter doesn't actually remove information."

**Factor perturbation, Table 1.** Recombine/freeze encoder/decoder factors under symbolic replacement labels; differing results show the task-feature orientation and output verbalization are not identical effects. The decomposition of a *fitted filter* still does not imply native unique modularity.

**Step 2: Natural observational analog, Fig.4–6, §4.3.** Eccentricity = variance fraction along first PC of query-hidden-state ensemble; covariance flux = fraction through identified TVS. Vary number of demonstrations, instructions, random demonstration labels, missing true label. Few-shot representations exhibit selective information concentration in mid-to-late layers. **Crucial subtlety**: missing-label condition can display stronger compression while having worse accuracy; therefore neither compression nor anisotropy is an unconditional proxy for correct ICL. Random labels differ from missing labels. Spontaneous geometry resembling the constructive filter remains correlation, not proof of same algorithm.

**Step 3: Targeted disruption, Figs.7–11, Table 2 / Appendix Table 7.** Head-by-head covariance-flux ablations identify Denoising Heads (DH); compare their joint ablation to count-matched random heads; examine induction strength vs flux effects, attention maps, and DH overlap between tasks. Many DH effects differ from induction heads; some cross-task heads are common, many task-specific. On Llama3.2-1B six-task average, 8-shot unseen-label approx. 14.54% → 1.06% when DH ablated; matched random-head control 10.65%. This supports causal relevance **under these tasks and models**, not uniqueness of an information-removal circuit.

**Boundary/failure, §5, Figs.12–13, Appendix H.** A learned low-rank filter aids many classification and some many-to-one fact mapping (people-profession), but is not a general solution for one-to-one country–capital mapping or complex generative translation. Eccentricity may change even in generative cases without a valid linear TVS/covariance flux explanation. This **negative boundary** makes the mechanism scientifically sharper: not a general theory that every ICL step is dimensionality reduction.

## The nearest-work distance

ICLR 2025 explains Encode → Merge → Retrieve-Copy and admits bypass paths; ICLR 2026 responds to a concrete missing-label counterexample with **task-oriented information removal**. This is a complementary and broader hypothesis with constructive, observational and ablation evidence, not "nobody studied ICL". Its strength depends on keeping the cases where it fails.

The 2026 authors still rely on a task-specific trained linear filter/metric and attention-head ablation with collateral effects. The resulting evidence is substantial but should not be paraphrased as discovering a uniquely identifiable natural low-rank filter in every Transformer.

## Transferring to our false-friend question

Old measurements (Stingray FF error, Škrjanec word surprisal, Kallini transfer) are not in logical conflict because they have different outcomes. We have NOT yet found a Cho-style sharp counterexample. A plausible search is: a word whose target sense is reliably known, whose language cue alone and semantic cue alone favor intended interpretation, but whose combination unexpectedly favors an unrelated-language sense. This would challenge a calibrated additive model, IF task and lexicalization confounds are excluded. Then use predictive held-out contrast, targeted intervention only if warranted.

We must **permit the simple additive model to win**, just as Cho reports boundary cases where low-rank filtering fails. The scientific work is discriminating existing explanations, not forcing a headline.

## No fake reading completeness

ICLR 2026 was examined through main text, appendices and figure catalog. ICLR 2025 remains referenced for the already confirmed high-level operations and bypass, not misrepresented as a full-paper line-by-line independent replication. Full 2025 pdf inaccessible via current web (about 19 MB exceeds tool cap). This is a bounded background source, not an excuse to invent more experiments.
