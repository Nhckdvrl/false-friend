# Research agent operating rules (2026-10)

You are maintaining an **active hypothesis-development repo**, not optimizing a benchmark or rescuing a rejected result.

1. Read RESEARCH_MAINLINE.md, knowledge/README.md, knowledge/PAPERS_INDEX.md, knowledge/RESEARCH_AGENT_PROTOCOL.md and docs/LEGACY_RECORD.md first. The knowledge base is the authoritative research context.
2. **No claims that the hypothesis is confirmed.** Keep observations, prior literature, hypotheses and guesses separate.
3. Preserve the old full state via archive/lexical-sharing-2026-08; never copy old Gate 1 scripts back without explicit new scientific protocol.
4. Data review before GPU: proper language/sense/POS, verified independent reviewers, provenance, matched controls and no capitalization-normalized fake cognates.
5. Illustrative data never become published evidence. Do not bypass preflight or silently relabel illustrative -> verified.
6. Do not equate surprisal or continuation NLL with sense comprehension; do not equate probing with causal use.
7. For every proposed experiment, list competing hypotheses, differing predictions, necessary invariant, negative control, decisive failure result and incremental knowledge gained.
8. Do not use gold-dependent softmax masks or change answer alternatives as a function of the label being evaluated.
9. Verify nearest paper novelty, especially Körner EACL 2026 and Dumas ACL 2025, before patching.
10. No GPU allocation, model downloads, publishing, or large-data collection by default; perform only after explicit user request and verified resources.
11. Test pure logic with pytest and run scripts/preflight.py before new work; record code and model/tokenizer hashes for actual experiments.
12. Prefer deleting obsolete code rather than leaving confusing inactive executables on main. Git history is the archive.

13. New papers require a structured knowledge/papers note recording exact sources and reading depth, FACT vs INFERENCE, possible idea genesis, innovation scale, nearest-paper distance, experiment chain and falsifiers.
14. Before adopting an idea, read knowledge/ideas/ROUTE_REASSESSMENT.md and EXPERIMENT_KILL_TABLE.md. E0–E5 is conditional; A0/B0 may fail; do not default to A.
15. Keep knowledge/PAPERS_INDEX.md and CITATION_LEDGER.md in sync. A source checked at abstract level cannot be promoted to deep-read in order to justify novelty.
