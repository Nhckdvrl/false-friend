#!/usr/bin/env bash
set -euo pipefail
GPU=${1:?GPU index required}
CONFIG=${2:-configs/gate1_fast.yaml}
CONDITION=${3:-shared}
SEED=${4:-11}
SCHEDULE=${5:-joint}
exec bash scripts/run_one_gpu.sh "$GPU" "$CONFIG" "$CONDITION" "$SEED" "$SCHEDULE"
