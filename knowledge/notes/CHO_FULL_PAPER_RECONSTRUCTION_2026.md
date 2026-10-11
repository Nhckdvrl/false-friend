# Cho 2026 detailed method and test-chain reconstruction (87-page paper)

**Reading evidence:** local user-provided file 4191_Mechanism_of_Task_oriente (1).pdf, 87 pages. Full main §§1–5, Appendix A (methods), B (covariance), E/F (causal controls), G/H (entropy and generation), I figure catalog inspected 2026-10-12. **This is independent reading, not rerunning author code.** [Author conference record](https://proceedings.iclr.cc/paper_files/paper/2026/hash/105112d52254f86d5854f3da734a52b4-Abstract-Conference.html).

## Before any experiment: which alternative explanations disagree?

Unseen-label ICL is a local counterexample to **exclusive induction-head exact label copying**. However, even if another computation exists, it might be query classification learned during pretraining, an instruction prompt effect, or a general output-bias mechanism. Constructive low-rank projection merely tests if **selecting already-encoded task attributes** can replace label demonstrations.

- Zero-shot has plausible competing tokens for same query; Fig.2 visually ranks "President", "Human", "Male". This suggests entangled latent task facts, not necessarily literally orthogonal true subspaces.
- Trained WencWdec filter on zero-shot hidden state, no model updates; output is unrestricted full vocabulary. Very important: a fixed list of candidate labels could make otherwise arbitrary logits appear successful by construction.
- Covariance excluded by rank-r filter and cosine alignment to leading PCs checks that filter is actually removing information.
- Changing labels while freezing one low-rank factor distinguishes *task selection* from *label verbalization* (Table1), without claiming unique biological modules.

## Why not stop at constructive success?

The filter was trained with target labels. Ordinary ICL does not run this optimization for each prompt. The authors measure covariance geometry across natural k-shot query states, then explicitly compare instructions, random-label demos and unseen-label demos (Figs.4–6; Appendix Table6). If geometry changes as information removal predicts, that is consistent but not causal. Worse, more information concentration can accompany reduced accuracy, so the correct independent hypothesis involves **task-relevant** removal, not a monotonic variance–accuracy mapping.

## Why not stop at observational geometry?

The metrics are corpus-level state cloud statistics, not operators one can directly toggle. Authors identify heads whose ablation reduces covariance flux and separately test output accuracy with these heads ablated. DH random controls, induction-head correlation, attention visualization, multiple models, cross-task overlaps. Different failure patterns and stronger effect when true label absent connect mechanism to the **original counterexample**, closing the narrative loop.

Specific results from Table2: Llama3.2-1B unseen-label average 14.54 vs 1.06 when removing DH, vs 10.65 randomly removing equal-count RH; many models have positive causal importance, instruction-tuned Qwen effects weaker on ordinary-label conditions. Head removal still disrupts more than one local operation, so the mechanism is not completely identifiable.

## Most valuable extra section: §5 boundaries

Classification many-to-one encourages compression of irrelevant features; one-to-one country–capital factual recall needs detailed entity mapping and resists coarse low-rank removal; people–profession mapping is easier for selected bottlenecks. On unconstrained generation/translation, authors observe some geometry and expressly stop short of claiming fully measurable correct low-rank TVS. Not a blanket "all ICL = compression" theory.

**Experimental lesson:** state the model of the failure mode first, then predict which task structures make a proposed mechanism appropriate. Test the **absence** of effect as intentionally as the presence. Strong narrative science can come from explaining a known task with correct boundaries.

## Application: multilingual competing evidence

Our own current hypothesis is a low-level predictive question (what cue weights determine a meaning choice?), not an a priori latent routing head. Treat form prediction, semantic choice and free translation as distinct endpoints, measure with authors' baseline tasks, test additive vs interaction predictions on unseen word types, and select the next intervention based on what a simpler explanation cannot cover. If additive cues explain results, report a boundary rather than manufacturing a new mechanism.

**Still separate**: ICLR 2025 previous circuit has been reviewed at official-summary level, not independently reread in the full ~19MB paper. It is not required to claim that ICLR 2026's full experimental design was examined.
