# Zhou et al. — How Language Models Process Negation

- Primary v2: https://arxiv.org/html/2605.03052v2 (2026-05-29).
- Author code: https://github.com/Ja1Zhou/LM_Negation.
- Venue: authors report ICML 2026 in arXiv and their repository. OpenReview's verification page prevented independent acceptance verification; retain this qualification.
- Reading S2: §§3–5.4, selected §5.5/Limitations, Appendix A.2–A.3; not all plots or a reproduction.

## Experimental reasoning

The paper distinguishes negation-sensitive logit changes from correct final candidate ranking. It uses attention interventions and patching to study opposing contributions, then examines whether intermediate outputs promote negated concepts. Patching uses an expanded answer set. Models are base models; this differs from our instruction-following generations.

## Idea genesis — INFERENCE

The opening is a mismatch between directional sensitivity and final accuracy. The next experiment asks whether useful computation is counteracted, rather than concluding that negation was never represented. Suppression versus construction then provides predictions about the information carried to later positions.

## Critical assessment

A logit shift in the expected direction shows a response to the operator, not complete negation understanding. Attention sinking also removes unrelated information pathways and changes normalization; a beneficial ablation does not uniquely establish the proposed semantic shortcut. Selecting the best layer on the same evaluation data needs separate validation before being called a general remedy. LogitLens and semantic annotation of promoted tokens depend on the readout and candidate inventory; they do not prove a unique internal algorithm.

Expanding acceptable answers for patching can improve measurement, but it changes the outcome relative to the original single-answer test. These objects must be distinguished. A small set of interpretable SAE examples is a mechanism clue, not prevalence evidence for every negated construction.

## Distance to our work

Our question is which semantic unit a task uses when lexical content and a larger expression differ. The [fourth-cycle results](../notes/ROMANCE_SCOPE_CYCLE_RESULTS_2026-10-13.md) are behavioral; no layer, head or suppression/construction mechanism has been tested locally. Before adopting this paper's interventions, we need independent target-level meanings and a held-out prediction that distinguishes scope selection, relation criterion and response mapping. It would be scientifically weak to transplant an attention ablation onto a YES/NO failure without establishing what the failure means.
