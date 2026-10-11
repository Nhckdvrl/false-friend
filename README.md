# False Friend Lab — Explanatory Research on Multilingual Word Sense

> **2026-10-12 ACTIVE EXPLORATION. No new scientific-model results.** The prior A/B/C idea queue and old E0–E5 promise have been discontinued, not preserved as parallel plans.

**Scientific question:** When a word form suggests competing language-specific senses, can the decision be explained by learned lexical familiarity plus independently measured language and contextual-semantic evidence, or does combining those cues reveal a distinct, reproducible phenomenon that simpler explanations cannot predict?

We learn from Hakaze Cho's method: use the simplest important counterexample to an existing explanation, force competitors to predict DIFFERENT results, separate constructive/observational/causal evidence, and study informative negative boundary conditions. We **do not** require an untouched field or insist on a hidden gating mechanism.

## Research status and start here

1. [RESEARCH_MAINLINE.md](RESEARCH_MAINLINE.md) — the **only active question**, competing explanations, conditional discovery experiments and kill conditions.
2. [experiments/FIRST_PASS.md](experiments/FIRST_PASS.md) — reproducible source-data preflight and concrete baseline-reproduction protocol. Actual LLM baseline experiments are **not yet run**.
3. [knowledge/README.md](knowledge/README.md) + [PAPERS_INDEX.md](knowledge/PAPERS_INDEX.md) — structured paper-centered knowledge including idea genesis, nearest related work, experimental chain, actual reading levels and falsifiers.
4. [Cho 2026 full-paper reconstruction](knowledge/notes/CHO_FULL_PAPER_RECONSTRUCTION_2026.md) — detailed methods, controlled evidence sequence and limitations after reading the actual 87-page paper.
5. [Data atlas](knowledge/data/DATASET_ATLAS.md) — semantic labels and whether they identify our actual experiment object.
6. [Retired research hypotheses](knowledge/ideas/RETIRED_HYPOTHESES.md) — why the previous late-revision, wrong-anchor topology and training-order theories are no longer active.

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

No model weights downloaded or GPU work performed by the new scripts; CI only validates tests and synthetic examples. A previous optional binary-gloss model runner remains exploratory and must not be misrepresented as an author's published baseline.

## Legacy science

The 2026-08 lexical-sharing training project ended in **conceptual identification failure**, not a hypothesis rejection; its old ten-run verdict was scientifically invalid. Full source lives at [archive/lexical-sharing-2026-08](https://github.com/Nhckdvrl/false-friend/tree/archive/lexical-sharing-2026-08). Original idea triage survives in Git history for reproducibility, but is NOT an active plan.

**Agent rules:** read [AGENTS.md](AGENTS.md) and [knowledge/RESEARCH_AGENT_PROTOCOL.md](knowledge/RESEARCH_AGENT_PROTOCOL.md) before modifying or extending experiments.
