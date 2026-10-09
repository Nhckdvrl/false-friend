# What we actually borrow from Hakaze Cho: an indispensable experimental chain

**Not**: more experiments, more probes, more training, longer appendix, or an attractive causal diagram.

**Yes**: build a sequence where each observation has a well-defined rival interpretation, and the next experiment is the minimum intervention needed to distinguish them.

## Two reference papers

- Hakaze Cho et al., [Revisiting In-context Learning Inference Circuit in Large Language Models](https://proceedings.iclr.cc/paper_files/paper/2025/hash/22d4f952efa13970f0b1ffb22170d416-Abstract-Conference.html), ICLR 2025.
- Hakaze Cho et al., [Mechanism of Task-oriented Information Removal in In-context Learning](https://proceedings.iclr.cc/paper_files/paper/2026/hash/105112d52254f86d5854f3da734a52b4-Abstract-Conference.html), ICLR 2026.

The 2025 paper offers a multi-operation inference account, specific quantitative measurement and ablation, plus bypass mechanisms. The 2026 paper starts with a meaningful contradiction (ICL can work without the correct label in demonstrations), explores a *constructive* low-rank filtering intervention, measures whether natural few-shot ICL has analogous informational changes, then tests causal importance by removing implicated computations. It does **not** infer natural mechanisms from the synthetic filtering success alone.

## The translation into our problem

| Stage | Question | Experiment | New uncertainty exposed |
|---|---|---|---|
| 1. Counterexample | A model predicts shared forms well; does it understand both meanings? | Form vs order-balanced sense discrimination vs free translation | A bad answer may still be output copying |
| 2. Rival decomposition | Does the model know the target sense under unambiguous conditions? | Explicit-language / non-homographic meaning controls | Recoverable knowledge does not prove its causal use |
| 3. Discriminating manipulation | What turns an early incorrect preference into a correct interpretation? | Semantic evidence strength and pre-/post-position, language cue and matched polysemy | Prompt response is not a causal internal story |
| 4. Causal prediction | Do language and semantic signals play different necessary roles? | Factorial activation interchange with reciprocal negative controls | Off-manifold patching can perturb many variables |
| 5. Novel prediction | Can one account predict untested failure/recovery conditions? | Held-out words, contexts and model families | Failure means no explanatory generalization |

## Constructive vs observational vs causal evidence

1. A *constructive* replacement (e.g., unambiguous paraphrase or information-limiting context) shows a mechanism is **possible**, not that the unmodified model uses it.
2. An *observational* measure (gloss log-likelihood, probe, trajectories) shows association, not necessity.
3. A *causal* patch requires specificity and counterfactual invariants: what changed, what should not change, and a reciprocal/null intervention.
4. **Predictive** validity is the harder final test: can our account predict new words rather than narrate existing plots?

## Pre-experiment worksheet (required)

Before accepting each figure, write:
- Observation being explained (with its independent ground-truth definition).
- Two rival hypotheses that predict **different results**.
- Intervention and what must stay invariant.
- Measurement and a negative control that could make the claim collapse.
- A threshold or failure observation chosen *before* inspecting results.
- Why the previous experiment cannot already answer this question.

If these cannot be filled, don't add the experiment. Never use a probe or a complicated framework as a substitute for causal identification.

## Specific overlap with existing work

Körner et al. (EACL 2026) already use cross-language concept patching over checkpoints and manually identify *homograph copying* and *polysemy sense shifts* as misleading apparent improvements. Dumas et al. (ACL 2025) already separate concept and output language with activation patching. Therefore a new paper cannot merely say “semantics and output form are separable” or “patching changes homograph translation.” New evidence must distinguish **sense selection vs revision vs output-only** under matched counterfactuals and predict new observations.

The lesson is methodological, not about copying a particular component-level attribution story from Cho.
