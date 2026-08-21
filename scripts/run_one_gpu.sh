#!/usr/bin/env bash
set -euo pipefail
GPU=${1:?GPU index required; use only a confirmed-idle GPU}
CONFIG=${2:-configs/gate1_fast.yaml}
CONDITION=${3:-shared}
SEED=${4:-11}
SCHEDULE=${5:-joint}
export CUDA_VISIBLE_DEVICES="$GPU"
python scripts/train.py --config "$CONFIG" --condition "$CONDITION" --seed "$SEED" --schedule "$SCHEDULE"
