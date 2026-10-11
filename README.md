# False Friend Lab — Explanatory Research on Multilingual Word Sense

> **2026-10-12 ACTIVE EXPLORATION. Two small CPU model instrument probes completed; **no confirmed scientific effect or reproduced baseline**.** The prior A/B/C idea queue and old E0–E5 promise have been discontinued, not preserved as parallel plans.

**Scientific question:** When a word form suggests competing language-specific senses, can the decision be explained by learned lexical familiarity plus independently measured language and contextual-semantic evidence, or does combining those cues reveal a distinct, reproducible phenomenon that simpler explanations cannot predict?

We learn from Hakaze Cho's method: use the simplest important counterexample to an existing explanation, force competitors to predict DIFFERENT results, separate constructive/observational/causal evidence, and study informative negative boundary conditions. We **do not** require an untouched field or insist on a hidden gating mechanism.

## Research status and start here

1. [RESEARCH_MAINLINE.md](RESEARCH_MAINLINE.md) — the **only active question**, competing explanations, conditional discovery experiments and kill conditions.
2. [experiments/FIRST_PASS.md](experiments/FIRST_PASS.md) — reproducible source-data preflight and concrete baseline-reproduction protocol. Actual LLM baseline experiments are **not yet run**.
3. [knowledge/README.md](knowledge/README.md) + [PAPERS_INDEX.md](knowledge/PAPERS_INDEX.md) — structured paper-centered knowledge including idea genesis, nearest related work, experimental chain, actual reading levels and falsifiers.
4. [Cho 2026 full-paper reconstruction](knowledge/notes/CHO_FULL_PAPER_RECONSTRUCTION_2026.md) — detailed methods, controlled evidence sequence and limitations after reading the actual 87-page paper.
5. [Data atlas](knowledge/data/DATASET_ATLAS.md) — semantic labels and whether they identify our actual experiment object.
6. [Retired research hypotheses](knowledge/ideas/RETIRED_HYPOTHESES.md) — why the previous late-revision, wrong-anchor topology and training-order theories are no longer active.

## Sharpened first mechanism candidate

A source-code reread of [Tanwar et al. Task3](knowledge/notes/TANWAR_IDENTIFIABILITY_AUDIT.md) identified **two high-information rival explanations** for a published ~70% vs ~34% directional "correction" result: (i) strictly identical homograph surfaces cannot reveal a hidden inserted-word source-language index; (ii) the generation prompt asks Q1 word language before Q2 meaning, so model's Q1 text conditions Q2. These are scientific identification/measurement questions, **not newly observed LLM behavior**. We now prioritize original-prompt reproduction plus Q2-only/order controls before any activation patching.

## Verified data-source discovery, not a model discovery

Using source TSVs from [Abuín et al., ACL 2026](https://github.com/mrtva/false-friends-vs-cognates), checked 704 contextual word-pair records; 332 identical lemma forms; 189 same-lemma contextually different-sense pairs; only 69 of those contain the exact same case-sensitive whole form in BOTH contexts (58 distinct language-pair+form units). No linguistic reannotation has been performed, and these are not 69 independent semantic experiment cases. Tanwar original EN-DE/FR/ES low/high constraint CSVs also exist and will be the nearest baseline before any new manipulated contrast.

## Executable source checks

~~~bash
python -m pip install -e '.[dev]'
python -m pytest -q
python scripts/check_knowledge.py
# After fetching the external data sources as explained in experiments/FIRST_PASS.md:
python scripts/audit_romance_wic.py --source-dir false-friends-vs-cognates --output outputs/romance.json
python scripts/audit_tanwar_baseline.py --source-dir Bilingual_processing_LLMs/data --output outputs/tanwar.json
~~~

Open-weight Qwen 0.5B/1.5B CPU pilots were executed via optional GitHub Actions. No user GPU was used; these are **instrument smoke tests**, not paper-baseline replications. See [actual observations and warnings](experiments/PILOT_FINDINGS_2026-10-12.md).

## Newly executed experiments (still exploratory)

[Raw pilot interpretations, model revision and A/B measurement-instability audit](experiments/PILOT_FINDINGS_2026-10-12.md). First 0.5B generated answers often failed to identify even the target word. In the larger 1.5B balanced-label pilot, 7/18 experimental cells flipped raw semantic-preference direction under option order; candidate scoring needs validation before mechanism claims.

## Legacy science

The 2026-08 lexical-sharing training project ended in **conceptual identification failure**, not a hypothesis rejection; its old ten-run verdict was scientifically invalid. Full source lives at [archive/lexical-sharing-2026-08](https://github.com/Nhckdvrl/false-friend/tree/archive/lexical-sharing-2026-08). Original idea triage survives in Git history for reproducibility, but is NOT an active plan.

**Agent rules:** read [AGENTS.md](AGENTS.md) and [knowledge/RESEARCH_AGENT_PROTOCOL.md](knowledge/RESEARCH_AGENT_PROTOCOL.md) before modifying or extending experiments.
