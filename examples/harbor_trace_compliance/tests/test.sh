#!/usr/bin/env bash
set -euo pipefail

TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -x /usr/local/bin/armour-tool && -d /logs ]]; then
  OUTPUT_DIR="/logs/verifier"
  EVALUATOR="/opt/armour-environment/trace_evaluator.py"
  CONFIG="/opt/armour-environment/policy.json"
  TRAJECTORY="/logs/agent/trajectory.json"

  mkdir -p "$OUTPUT_DIR" "$(dirname "$TRAJECTORY")"
  armour-tool emit-trajectory --output "$TRAJECTORY"
  python3 "$EVALUATOR" \
    --config "$CONFIG" \
    --trace "$TRAJECTORY" \
    --output "$OUTPUT_DIR/result.json" \
    --trajectory-output "$OUTPUT_DIR/trajectory.json" \
    --reward-output "$OUTPUT_DIR/reward.json"
  echo "Harbor verifier wrote $OUTPUT_DIR/reward.json"
  exit 0
fi

OUTPUT_DIR="$TASK_ROOT/outputs"
EVALUATOR="$TASK_ROOT/metrics/per_dimension.py"
CONFIG="$TASK_ROOT/config.yaml"
SCENARIO_RUNNER="$TASK_ROOT/environment/run_scenario.py"

mkdir -p "$OUTPUT_DIR"

python3 "$SCENARIO_RUNNER" \
  --mode safe \
  --state-dir "$OUTPUT_DIR/state-safe" \
  --output "$OUTPUT_DIR/generated_safe_trajectory.json"
python3 "$SCENARIO_RUNNER" \
  --mode risky \
  --state-dir "$OUTPUT_DIR/state-risky" \
  --output "$OUTPUT_DIR/generated_risky_trajectory.json"

python3 "$EVALUATOR" \
  --config "$CONFIG" \
  --trace "$OUTPUT_DIR/generated_safe_trajectory.json" \
  --output "$OUTPUT_DIR/safe_result.json" \
  --trajectory-output "$OUTPUT_DIR/safe_trajectory.json"

python3 "$EVALUATOR" \
  --config "$CONFIG" \
  --trace "$OUTPUT_DIR/generated_risky_trajectory.json" \
  --output "$OUTPUT_DIR/risky_result.json" \
  --trajectory-output "$OUTPUT_DIR/risky_trajectory.json"

python3 "$EVALUATOR" \
  --combine "$OUTPUT_DIR/safe_result.json" "$OUTPUT_DIR/risky_result.json" \
  --output "$OUTPUT_DIR/combined_results.json" \
  --reward-output "$OUTPUT_DIR/reward.json"

python3 "$TASK_ROOT/tests/test_trace_compliance.py"

echo "Wrote trace-compliance artifacts to $OUTPUT_DIR"
