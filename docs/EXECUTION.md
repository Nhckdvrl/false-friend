# Execution and preflight (2026 reset)

## Dependency policy

Scientific dry-run validation needs Python >= 3.10 and pytest only. The actual open-weight model pilot uses optional PyTorch + Transformers and must run only on properly approved/local resources.

```bash
python -m pip install -e '.[dev]'
pytest -q
python scripts/preflight.py --data data/examples/illustrative.jsonl --allow-illustrative
```

This preflight should report 3 rows, 1 lexical type and scientific_claims_permitted=false. **Passing does not make the example scientifically valid.**

## First verified pilot

Create your own human-audited data/verified/items.jsonl following DATA_SCHEMA.md, with independent provenance. Do not change flags to circumvent reviewer checks.

```bash
python scripts/preflight.py --data data/verified/items.jsonl
python -m pip install -e '.[pilot]'
python scripts/run_behavior.py --data data/verified/items.jsonl \
  --model /path/to/open-weight-causal-lm \
  --revision PINNED_MODEL_COMMIT --device cuda:0 \
  --output outputs/pilot.jsonl
python scripts/summarize.py --input outputs/pilot.jsonl \
  --output outputs/pilot_summary.json --bootstrap 2000
```

The runner scores **both A/B candidate orders**. It explicitly refuses cases where adding an answer changes tokenizer prefix segmentation or either answer-label continuation uses more than one token. For unsupported tokenizers, modify the format transparently with new tests; do not silently force a score.

The summary first averages within lexical types then provides a lexeme-level exploratory bootstrap and descriptive *family-paired* differences from baseline. **It is not a confirmatory statistical test**: heterogeneous model / prompt effects and joint uncertainty have not been modeled.

### Failure triage

- DataError: revise the scientific item, never weaken the semantic rule to make a gate pass.
- TokenBoundaryError: revise prompt delimiter/verbalizers or choose another model, then rerun all conditions.
- OOM: choose a feasible local model/device, not reduced conditions selected after seeing outputs.
- Meaning-task near chance: check data quality and instruction following before interpreting semantic mechanism.
- Output-copy mismatch: record as separate mode; do not label it internal sense confusion.

### What's deliberately absent

No old Gate 1 training code, no remote GPU inventory scripts, no automatic corpus scraping, no patching/probing before a behavior anomaly, no claims from a handful of template examples, and no fixed target performance numbers. Reintroduce tools only for an experiment with a causal estimand and failure criterion.
