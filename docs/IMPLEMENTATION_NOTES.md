# Implementation Notes and Validation Checklist

## Before GPU training

- [ ] `pip install -e .` succeeds in the chosen existing/local environment.
- [ ] `PYTHONPATH=src pytest -q` passes.
- [ ] `scripts/prepare.py` finishes without token-map assertions.
- [ ] Inspect `data/processed/en_de/metadata.json`.
- [ ] Inspect `targets.csv`: enough false friends and true friends survive the single-token + frequency gate.
- [ ] Check EN/DE occurrence-count histograms; flag extreme imbalance.
- [ ] Check `contexts.jsonl` has multiple lexical items in both relations and both languages.
- [ ] Verify held-out context ids are not present in training construction by design (prepare script removes deterministic target-containing holdouts before appending to streams).

## Smoke test

Use a copied config with 20–50 steps.

- [ ] shared run loss is finite and falls.
- [ ] split run loss is finite and falls.
- [ ] both report identical `effective_vocab_size`.
- [ ] checkpoint has `config.json`, `model.safetensors`, `run_meta.json`.
- [ ] `scripts/evaluate.py` reloads both checkpoints.
- [ ] exact context/seed pairing works in `scripts/analyze.py`.

## Primary grid

- [ ] five shared seeds complete.
- [ ] same five split seeds complete.
- [ ] compare one identical checkpoint step across all ten runs.
- [ ] no failed/partial run is silently included.
- [ ] record Gate 1 summary in `RESEARCH_MAINLINE.md`.

## Positive-result robustness (only after Gate 1 pass)

- [ ] reproduce on `gate1_full.yaml` with at least three paired seeds.
- [ ] evaluate post windows k=4 and k=16 without changing the primary k=8 decision.
- [ ] inspect effect versus EN/DE frequency ratio.
- [ ] repeat with larger natural corpus / CCMatrix-style corpus.
- [ ] confirm explicit sense behavior on Stingray prompts or a direct semantic-choice protocol.
- [ ] then run checkpoint trajectory.

## Negative-result discipline

If Gate 1 fails:

- do not add hidden-state probes;
- do not change five controls simultaneously;
- do not call a frequency main effect a rescue;
- archive the exact result and reason.

Only revise the setup if a concrete implementation failure is found (e.g. too few target occurrences, tokenization accidentally split most items, eval pairing bug, or training instability).
