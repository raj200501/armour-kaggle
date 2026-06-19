#!/usr/bin/env bash
set -euo pipefail

TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESTINATION="${TRACE_OUTPUT_PATH:-$TASK_ROOT/outputs/oracle_trajectory.json}"

mkdir -p "$(dirname "$DESTINATION")"
cp "$TASK_ROOT/data/safe_trace.json" "$DESTINATION"

echo "Wrote the compliant reference trajectory to $DESTINATION"
