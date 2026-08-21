#!/usr/bin/env bash
set -euo pipefail
CONFIG=${1:-configs/gate1_fast.yaml}
CONDITION=${2:-shared}
SEED=${3:-11}
SCHEDULE=${4:-joint}
GPU=${5:-0}
export CUDA_VISIBLE_DEVICES="$GPU"
export PYTHONPATH="${PWD}/src${PYTHONPATH:+:${PYTHONPATH}}"
exec python scripts/train.py --config "$CONFIG" --condition "$CONDITION" --seed "$SEED" --schedule "$SCHEDULE"
