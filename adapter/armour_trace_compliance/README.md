# Armour Trace Compliance to Harbor Adapter

This dependency-free adapter converts Armour's reviewed scenario catalog into
ten self-contained Harbor tasks. It exists so the benchmark definition remains
compact and reviewable while each generated task can be packaged, run, and
published independently.

## Source

- Source concept and prototype: [`raj200501/armour`](https://github.com/raj200501/armour)
- Adapter catalog: [`catalog.json`](catalog.json)
- Generated dataset: [`../../benchmark`](../../benchmark)
- License: MIT

The catalog is a selected pilot slice, not an automatic conversion of every
case in the broader Armour prototype.

## Generate

From the repository root:

```bash
python3 -m adapter.armour_trace_compliance.main \
  --output-dir benchmark \
  --overwrite
```

Standard subset flags are supported:

```bash
python3 -m adapter.armour_trace_compliance.main --limit 3 --output-dir /tmp/armour
python3 -m adapter.armour_trace_compliance.main \
  --task-ids customer-ticket-data-scope browser-session-boundary \
  --output-dir /tmp/armour
```

Verify checked-in tasks against fresh adapter output:

```bash
python3 -m adapter.armour_trace_compliance.main \
  --output-dir benchmark \
  --check
```

## Generated Task Structure

```text
{task_id}/
├── README.md
├── instruction.md
├── task.toml
├── environment/
│   ├── Dockerfile
│   ├── scenario.json
│   ├── armour_tool.py
│   ├── run_scenario.py
│   └── trace_evaluator.py
├── solution/
│   └── solve.sh
└── tests/
    ├── test.sh
    └── test_task.py
```

## Fidelity

The same catalog entry generates the instruction, mocked tool outputs, safe
path, risky path, policy rule, and expected violation. Repository tests require
both paths to complete the task while assigning compliance only to the safe
path. Model parity is intentionally not claimed; the Kaggle pilot model matrix
remains an external launch decision.
