#!/usr/bin/env bash
set -u
NODES=(fvcrc10 fvcrc11 fvcrc12 fvcrc13 fvcrc15 fvcrc20 fvcrc21)
for node in "${NODES[@]}"; do
  echo "===== $node ====="
  ssh -o BatchMode=yes -o ConnectTimeout=4 "$node" 'hostname; nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits; echo "-- processes --"; nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory,process_name --format=csv,noheader,nounits 2>/dev/null || true' || echo "UNREACHABLE"
done
