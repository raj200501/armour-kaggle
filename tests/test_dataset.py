#!/usr/bin/env python3
"""Repository-level checks for the generated Armour dataset."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmark"
sys.path.insert(0, str(ROOT))

from adapter.armour_trace_compliance.adapter import CATALOG_PATH  # noqa: E402


def _load_metric_module():
    spec = importlib.util.spec_from_file_location("armour_metric", BENCHMARK / "metric.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load benchmark metric")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.scenarios = cls.catalog["scenarios"]

    def test_catalog_contains_ten_unique_tasks(self) -> None:
        task_ids = [scenario["task_id"] for scenario in self.scenarios]
        self.assertEqual(len(task_ids), 10)
        self.assertEqual(len(set(task_ids)), 10)

    def test_failure_reasons_cover_distinct_boundaries(self) -> None:
        reasons = {
            rule["reason"]
            for scenario in self.scenarios
            for rule in scenario["forbidden_tools"].values()
        }
        self.assertEqual(len(reasons), 10)

    def test_every_generated_task_is_self_contained(self) -> None:
        required = {
            "task.toml",
            "instruction.md",
            "environment/Dockerfile",
            "environment/scenario.json",
            "environment/armour_tool.py",
            "environment/trace_evaluator.py",
            "solution/solve.sh",
            "tests/test.sh",
            "tests/test_task.py",
        }
        for scenario in self.scenarios:
            task_dir = BENCHMARK / scenario["task_id"]
            present = {
                path.relative_to(task_dir).as_posix()
                for path in task_dir.rglob("*")
                if path.is_file()
            }
            self.assertTrue(required.issubset(present), scenario["task_id"])

    def test_dataset_manifest_lists_every_task(self) -> None:
        manifest = (BENCHMARK / "dataset.toml").read_text(encoding="utf-8")
        task_section = manifest.split("[[tasks]]", 1)[1]
        names = re.findall(
            r'^name = "raj200501/armour-([^\"]+)"$',
            task_section,
            re.MULTILINE,
        )
        self.assertEqual(set(names), {scenario["task_id"] for scenario in self.scenarios})

    def test_metric_reports_outcome_compliance_gap(self) -> None:
        metric = _load_metric_module()
        lines = [
            json.dumps({
                "reward": 1.0,
                "task_success": 1.0,
                "trace_compliance": 1.0,
                "policy_compliance": 1.0,
                "scope_adherence": 1.0,
                "evidence_quality": 1.0,
                "audit_integrity": 1.0,
            }),
            json.dumps({
                "reward": 0.0,
                "task_success": 1.0,
                "trace_compliance": 0.0,
                "policy_compliance": 0.0,
                "scope_adherence": 0.0,
                "evidence_quality": 1.0,
                "audit_integrity": 1.0,
            }),
        ]
        result = metric.aggregate(lines)
        self.assertEqual(result["mean_reward"], 0.5)
        self.assertEqual(result["mean_task_success"], 1.0)
        self.assertEqual(result["outcome_compliance_gap"], 0.5)

    def test_validation_summary_is_labeled_as_controls(self) -> None:
        summary = json.loads(
            (ROOT / "results" / "validation_summary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(summary["validation_kind"], "deterministic_controls")
        self.assertEqual(summary["task_count"], 10)
        self.assertIn("not agent or model performance", summary["disclaimer"])
        self.assertEqual(set(summary["runs"]), {
            "compliant_oracle",
            "successful_risky_control",
            "incomplete_noop_control",
        })
        for run in summary["runs"].values():
            self.assertEqual(run["completed_trials"], 10)
            self.assertEqual(run["errored_trials"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
