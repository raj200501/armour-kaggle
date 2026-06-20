#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PYTHONDONTWRITEBYTECODE=1

python3 -m adapter.armour_trace_compliance.main \
  --output-dir benchmark \
  --check
python3 tests/test_dataset.py
python3 tests/test_handoff_bundle.py
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

for required_doc in \
  docs/KAGGLE_FDE_HANDOFF_PACKET.md \
  docs/HARBOR_OUTPUT_CONTRACT.md \
  docs/AUTOMATION_BENCH_REVIEW.md; do
  if [[ ! -f "$required_doc" ]]; then
    echo "Missing handoff document: $required_doc" >&2
    exit 1
  fi
done

python3 scripts/export_handoff_bundle.py
python3 - <<'PY'
import json
from pathlib import Path

manifest_path = Path("dist/armour_kaggle_handoff/MANIFEST.json")
if not manifest_path.is_file():
    raise SystemExit("Missing handoff MANIFEST.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
if manifest.get("file_count", 0) < 10:
    raise SystemExit("Handoff manifest must contain at least 10 files")
PY

echo "Verified the handoff bundle, example, and all $task_count benchmark tasks."
