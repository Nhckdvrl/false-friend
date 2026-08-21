#!/usr/bin/env bash
set -euo pipefail
GPU=${1:?GPU index required for evaluation}
ROOT=${2:-runs/gate1_fast}
DATA=${3:-data/processed/en_de}
export CUDA_VISIBLE_DEVICES="$GPU"
for ckpt in "$ROOT"/*/seed_*/*/checkpoint-*; do
  [[ -d "$ckpt" ]] || continue
  if [[ ! -f "$ckpt/eval_contexts.csv" ]]; then
    echo "[eval] $ckpt"
    python scripts/evaluate.py --checkpoint "$ckpt" --data "$DATA"
  fi
done
python scripts/analyze_trajectory.py --inputs "$ROOT"/*/seed_*/*/checkpoint-*/eval_contexts.csv --output results/gate2_trajectory.csv
