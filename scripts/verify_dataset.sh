#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PYTHONDONTWRITEBYTECODE=1

python3 -m adapter.armour_trace_compliance.main \
  --output-dir benchmark \
  --check
python3 tests/test_dataset.py
bash examples/harbor_trace_compliance/tests/test.sh >/tmp/armour-example-test.log

task_count=0
for task_toml in benchmark/*/task.toml; do
  task_dir="${task_toml%/task.toml}"
  bash "$task_dir/tests/test.sh" >/tmp/armour-benchmark-task.log
  task_count=$((task_count + 1))
done

if [[ "$task_count" -ne 10 ]]; then
  echo "Expected 10 generated tasks, found $task_count" >&2
  exit 1
fi

echo "Verified the example and all $task_count benchmark tasks."
