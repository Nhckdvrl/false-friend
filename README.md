# False Friend Lab — Cross-Lingual Sense Selection & Revision

> **Status: ACTIVE / HYPOTHESIS DEVELOPMENT — no confirmed experimental findings.**
> 2026-10-09 research reset. The old lexical-sharing Gate 1 is retired, not resumed.

这个仓库现在研究一个清晰、可证伪的问题：

**当相同或高度相似的词形指向不同语言里的不同意义时，多语言语言模型如何利用语言线索与上下文证据选择意义？新的证据到来后，它是否真正修订解释，还是只修饰最终输出？**

We study *sense selection and revision*, not merely benchmark accuracy, and do not presuppose that lexical sharing is harmful. The immediate deliverable is a *reliable behavioral phenomenon*, not a mechanistic story.

## Research knowledge base — read before experiments

The original document-level literature matrix was NOT a true research knowledge base. It has been replaced by a curated [knowledge/](knowledge/) system:

1. [Paper index and reading depth](knowledge/PAPERS_INDEX.md) — all relevant papers with honest S1/S2/S3 coverage markers.
2. [Deep paper notes](knowledge/papers/) — source claim versus reconstructed idea origin, nearest-work distance, experimental chain, explanatory limits and distinguishing new predictions.
3. [Idea genealogy](knowledge/ideas/IDEA_GENESIS_GRAPH.md) and [concept map](knowledge/CONCEPT_MAP.md) — how normal research questions develop into strong mechanism tests.
4. [Route reassessment](knowledge/ideas/ROUTE_REASSESSMENT.md) and [kill table](knowledge/ideas/EXPERIMENT_KILL_TABLE.md) — conditional A0/B0 preflights, C parked.
5. [Theory cards](knowledge/theories/) and [research agent protocol](knowledge/RESEARCH_AGENT_PROTOCOL.md).

**2026-10-11 update:** sense revision is NOT assumed the final paper topic. Tanwar/Körner/Amouyal already occupy major portions of it. A0 (small, controlled behavior audit) and B0 (wrong-anchor causal identifiability audit) compete for investment; neither has scientific results. [Decision record](docs/DECISION_LOG.md).

## Read in this order

1. [RESEARCH_MAINLINE.md](RESEARCH_MAINLINE.md) — one core question, competing explanations, research decisions and gates.
2. [docs/CHO_DESIGN_PATTERNS.md](docs/CHO_DESIGN_PATTERNS.md) — how to design indispensable experiments rather than accumulate controls.
3. [docs/LITERATURE_MATRIX.md](docs/LITERATURE_MATRIX.md) — closest studies, covered claims, remaining uncertainty and verification.
4. [docs/EXPERIMENT_DESIGN.md](docs/EXPERIMENT_DESIGN.md) — staged experimental logic, causal claims and falsifiers.
5. [docs/DATA_SCHEMA.md](docs/DATA_SCHEMA.md) — data contract and annotation/provenance requirements.
6. [docs/EXECUTION.md](docs/EXECUTION.md) — reproduce the **non-scientific illustrative dry run**.
7. [docs/LEGACY_RECORD.md](docs/LEGACY_RECORD.md) — previous archived study and invalid-result warning.

## What is implemented

- Strict JSONL data validator and fail-fast preflight; unverified examples are **blocked by default**.
- Local Hugging Face causal-LM pilot that evaluates **both A/B gloss orders**, computing a signed correct-minus-competitor conditional log-likelihood margin.
- Defensive tokenization boundary check and one-token answer-label requirement; no gold-label-dependent candidate masking.
- Descriptive lexeme-clustered summaries with optional exploratory bootstrap, not confirmatory significance tests.
- Unit tests and GitHub Actions CI.

Not implemented: corpus construction, native-speaker annotation, approved scientific dataset, training, representation probes, causal activation patching, cross-model generalization, or scientific results. Those depend on behavioral identification.

## Quick start

```bash
python -m pip install -e '.[dev]'
pytest -q
python scripts/preflight.py --data data/examples/illustrative.jsonl --allow-illustrative
# For a *real* verified dataset and an available open-weight causal LM:
python -m pip install -e '.[pilot]'
python scripts/preflight.py --data data/verified/items.jsonl
python scripts/run_behavior.py --data data/verified/items.jsonl \
  --model PATH_OR_HF_ID --revision COMMIT_SHA --device cuda:0 \
  --output outputs/pilot.jsonl
python scripts/summarize.py --input outputs/pilot.jsonl --output outputs/pilot_summary.json
```

**IMPORTANT:** The example file is illustrative and unverified. The opt-in flag is for smoke-testing software only. The model commands are *not* part of CI; no model or GPU has been run as a result of this reset.

## Legacy

The August 2026 EN–DE from-scratch shared-vs-split project terminated for **conceptual identification failure** (24 false-friend items, 3 nominal controls, only ~1 plausibly aligned). Earlier 10-run results were scientifically invalid and must never be cited as negative results. Its complete final state is preserved on [archive/lexical-sharing-2026-08](https://github.com/Nhckdvrl/false-friend/tree/archive/lexical-sharing-2026-08) and in Git history. The default branch contains only the new active direction.

License and data-sharing rules for future corpora must be independently verified; no scraped or automatically produced annotation is treated as ground truth.
