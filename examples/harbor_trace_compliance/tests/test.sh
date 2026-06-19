#!/usr/bin/env bash
set -euo pipefail

TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="$TASK_ROOT/outputs"
EVALUATOR="$TASK_ROOT/metrics/per_dimension.py"
CONFIG="$TASK_ROOT/config.yaml"

mkdir -p "$OUTPUT_DIR"

python3 "$EVALUATOR" \
  --config "$CONFIG" \
  --trace "$TASK_ROOT/data/safe_trace.json" \
  --output "$OUTPUT_DIR/safe_result.json" \
  --trajectory-output "$OUTPUT_DIR/safe_trajectory.json"

python3 "$EVALUATOR" \
  --config "$CONFIG" \
  --trace "$TASK_ROOT/data/risky_trace.json" \
  --output "$OUTPUT_DIR/risky_result.json" \
  --trajectory-output "$OUTPUT_DIR/risky_trajectory.json"

python3 "$EVALUATOR" \
  --combine "$OUTPUT_DIR/safe_result.json" "$OUTPUT_DIR/risky_result.json" \
  --output "$OUTPUT_DIR/combined_results.json" \
  --reward-output "$OUTPUT_DIR/reward.json"

python3 "$TASK_ROOT/tests/test_trace_compliance.py"

if [[ -n "${LOGS_DIR:-}" ]]; then
  mkdir -p "$LOGS_DIR/verifier"
  cp "$OUTPUT_DIR/reward.json" "$LOGS_DIR/verifier/reward.json"
fi

echo "Wrote trace-compliance artifacts to $OUTPUT_DIR"
