#!/usr/bin/env bash
#SBATCH --job-name=ff-gate
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gres=gpu:4
#SBATCH --cpus-per-task=32
#SBATCH --mem=200G
#SBATCH --output=logs/%x-%A_%a.out
#SBATCH --error=logs/%x-%A_%a.err

set -euo pipefail
CONFIG=${1:?config yaml required}
MATRIX=${2:?matrix tsv required}
mkdir -p logs
LINE=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$MATRIX")
IFS=$'\t' read -r CONDITION SEED SCHEDULE <<< "$LINE"

echo "node=$(hostname) condition=$CONDITION seed=$SEED schedule=$SCHEDULE"
# Exactly one node is used per array task. There is intentionally no multi-node NCCL.
accelerate launch --num_processes 4 --num_machines 1 scripts/train.py \
  --config "$CONFIG" \
  --condition "$CONDITION" \
  --seed "$SEED" \
  --schedule "$SCHEDULE"
