#!/usr/bin/env bash
set -euo pipefail
echo "run_local_one.sh delegates to one-GPU causal runs; pass GPU index as arg5." >&2
exec "$(dirname "$0")/run_one_gpu.sh" "$@"
