# Direction triage — why one mainline, not three projects at once

Updated 2026-10-09. A topic is not publishable merely because no one used exactly its terminology.

## A. Current active: semantic selection and genuine revision

The known contradiction: local sense-disambiguation errors (Stingray), form predictability gain (Škrjanec), overall transfer gain (Kallini), and concept/output manipulation (Dumas / Körner) do not by themselves locate **the specific failure when late evidence ought to revise the wrong reading**.

A strong end result: distinguish initial language-prior bias, failure to revise meaning, and surface-copy errors, then predict which holdout items are affected. A weak end result: another false-friend prompt-accuracy leaderboard, or patching homographs to fix translations.

Minimum next investment: native-speaker item audit, one open-weight pilot and explicit matched within-language polysemy baselines.

## B. Reserve only: paradox of helpful false anchors

Why can low-similarity token overlap still help global multilingual transfer? Requires controlled synthetic bilingual mapping with fixed token count / capacity / frequency and independently evaluated global alignment vs local sense success. The original natural same-form matched-sense control was invalid. Do not enter B until A motivates its importance, or B is scoped as a separately preregistered topic.

## C. Parked: historical order dependence

EN-first vs DE-first curriculum and persistent path bias are close to extensive continual pretraining/curriculum work. Needs matched final exposure, stronger novelty and a direct sense-selection account; not a default extra gate.

## Anti-patterns

- Building a bespoke control resource solely to obtain a hoped-for significant interaction.
- Reporting post-target LM NLL as if it directly measured which meaning was understood.
- Calling A/B classification a latent sense posterior.
- Using large-scale activation patching as the first experiment.
- Calling any successful intervention a novel mechanism without nearest-paper comparison.
- Diluting a single research question into model training, benchmark construction and metric design at the same time.
