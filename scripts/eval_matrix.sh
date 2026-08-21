#!/usr/bin/env bash
set -euo pipefail
ROOT=${1:-runs/gate1_fast}
DATA=${2:-data/processed/en_de}
for ckpt in "$ROOT"/*/seed_*/*/checkpoint-*; do
  [[ -d "$ckpt" ]] || continue
  if [[ ! -f "$ckpt/eval_contexts.csv" ]]; then
    echo "[eval] $ckpt"
    python scripts/evaluate.py --checkpoint "$ckpt" --data "$DATA"
  fi
done
# All checkpoints are a trajectory, not a single Gate-1 estimate. Keep step
# separate here; run scripts/analyze.py on one matched step for the gate verdict.
python scripts/analyze_trajectory.py \
  --inputs "$ROOT"/*/seed_*/*/checkpoint-*/eval_contexts.csv \
  --output results/gate1_trajectory.csv
