#!/usr/bin/env bash
set -euo pipefail
CONFIG=${1:-configs/gate1_fast.yaml}
CONDITION=${2:-shared}
SEED=${3:-11}
SCHEDULE=${4:-joint}
accelerate launch --num_processes 4 --num_machines 1 scripts/train.py \
  --config "$CONFIG" --condition "$CONDITION" --seed "$SEED" --schedule "$SCHEDULE"
