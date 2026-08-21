#!/usr/bin/env bash
set -euo pipefail
CONFIG=${1:-configs/gate1_fast.yaml}
MATRIX=${2:-configs/gate1_matrix.tsv}
N=$(grep -cv '^\s*$' "$MATRIX")
mkdir -p logs
sbatch --array="0-$((N-1))" slurm/train_one.sbatch "$CONFIG" "$MATRIX"
