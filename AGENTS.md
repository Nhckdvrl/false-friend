# Research agent operating rules (2026-10)

You are maintaining an **active hypothesis-development repo**, not optimizing a benchmark or rescuing a rejected result.

1. Read RESEARCH_MAINLINE.md, docs/CHO_DESIGN_PATTERNS.md and docs/LEGACY_RECORD.md first.
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
