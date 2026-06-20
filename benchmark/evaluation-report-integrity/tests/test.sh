#!/usr/bin/env bash
set -euo pipefail

TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -x /usr/local/bin/armour-tool && -d /logs ]]; then
  OUTPUT_DIR="/logs/verifier"
  RUNTIME_DIR="/opt/armour-task"
  TRAJECTORY="/logs/agent/trajectory.json"

  mkdir -p "$OUTPUT_DIR" "$(dirname "$TRAJECTORY")"
  armour-tool emit-trajectory --output "$TRAJECTORY"
  python3 "$RUNTIME_DIR/trace_evaluator.py" \
    --scenario "$RUNTIME_DIR/scenario.json" \
    --trace "$TRAJECTORY" \
    --output "$OUTPUT_DIR/result.json" \
    --trajectory-output "$OUTPUT_DIR/trajectory.json" \
    --reward-output "$OUTPUT_DIR/reward.json"
  echo "Harbor verifier wrote $OUTPUT_DIR/reward.json"
  exit 0
fi

OUTPUT_DIR="$TASK_ROOT/outputs"
RUNTIME_DIR="$TASK_ROOT/environment"
STATE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/armour-task.XXXXXX")"
trap 'rm -rf "$STATE_ROOT"' EXIT
mkdir -p "$OUTPUT_DIR"

python3 "$RUNTIME_DIR/run_scenario.py" \
  --mode safe \
  --state-dir "$STATE_ROOT/safe" \
  --output "$OUTPUT_DIR/generated_safe_trajectory.json"
python3 "$RUNTIME_DIR/run_scenario.py" \
  --mode risky \
  --state-dir "$STATE_ROOT/risky" \
  --output "$OUTPUT_DIR/generated_risky_trajectory.json"

python3 "$RUNTIME_DIR/trace_evaluator.py" \
  --scenario "$RUNTIME_DIR/scenario.json" \
  --trace "$OUTPUT_DIR/generated_safe_trajectory.json" \
  --output "$OUTPUT_DIR/safe_result.json" \
  --trajectory-output "$OUTPUT_DIR/safe_trajectory.json"
python3 "$RUNTIME_DIR/trace_evaluator.py" \
  --scenario "$RUNTIME_DIR/scenario.json" \
  --trace "$OUTPUT_DIR/generated_risky_trajectory.json" \
  --output "$OUTPUT_DIR/risky_result.json" \
  --trajectory-output "$OUTPUT_DIR/risky_trajectory.json"
python3 "$RUNTIME_DIR/trace_evaluator.py" \
  --combine "$OUTPUT_DIR/safe_result.json" "$OUTPUT_DIR/risky_result.json" \
  --output "$OUTPUT_DIR/combined_results.json" \
  --reward-output "$OUTPUT_DIR/reward.json"

python3 "$TASK_ROOT/tests/test_task.py"
echo "Wrote trace-compliance artifacts to $OUTPUT_DIR"
