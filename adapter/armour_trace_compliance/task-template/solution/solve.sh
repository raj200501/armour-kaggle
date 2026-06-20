#!/usr/bin/env bash
set -euo pipefail

MODE="${ARMOUR_SCENARIO_MODE:-safe}"
if [[ "$MODE" != "safe" && "$MODE" != "risky" ]]; then
  echo "ARMOUR_SCENARIO_MODE must be safe or risky" >&2
  exit 2
fi

python3 /opt/armour-task/run_scenario.py \
  --mode "$MODE" \
  --state-dir "${ARMOUR_STATE_DIR:-/var/lib/armour}" \
  --output /tmp/armour-oracle-trajectory.json

echo "Completed the task through the $MODE mocked-tool path."
