#!/usr/bin/env python3
"""Aggregate Armour's multi-dimensional Harbor rewards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METRICS = (
    "reward",
    "task_success",
    "trace_compliance",
    "policy_compliance",
    "scope_adherence",
    "evidence_quality",
    "audit_integrity",
)


def aggregate(lines: list[str]) -> dict[str, float]:
    values = {metric: [] for metric in METRICS}
    for line in lines:
        if not line.strip():
            continue
        payload = _unwrap(json.loads(line))
        if payload is None:
            values["reward"].append(0.0)
            continue
        if isinstance(payload, (int, float)):
            values["reward"].append(float(payload))
            continue
        if not isinstance(payload, dict):
            raise ValueError(f"Unsupported reward payload: {payload!r}")
        for metric in METRICS:
            value = payload.get(metric)
            if isinstance(value, (int, float)):
                values[metric].append(float(value))

    means = {
        f"mean_{metric}": _mean(metric_values)
        for metric, metric_values in values.items()
    }
    means["outcome_compliance_gap"] = max(
        0.0,
        means["mean_task_success"] - means["mean_reward"],
    )
    return means


def _unwrap(value: Any) -> Any:
    if isinstance(value, dict) and len(value) == 1:
        nested = next(iter(value.values()))
        if isinstance(nested, dict):
            return nested
    return value


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main(input_path: Path, output_path: Path) -> None:
    result = aggregate(input_path.read_text(encoding="utf-8").splitlines())
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input-path", type=Path, required=True)
    parser.add_argument("-o", "--output-path", type=Path, required=True)
    args = parser.parse_args()
    main(args.input_path, args.output_path)
