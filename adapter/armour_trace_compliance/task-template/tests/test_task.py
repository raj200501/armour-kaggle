#!/usr/bin/env python3
"""Acceptance tests shared by generated Armour tasks."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = TASK_ROOT / "environment"
sys.path.insert(0, str(RUNTIME_DIR))

from armour_tool import MockToolEnvironment, load_scenario  # noqa: E402
from run_scenario import run  # noqa: E402
from trace_evaluator import evaluate_trajectory  # noqa: E402


class GeneratedTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(cls.temp_dir.name)
        safe_path = temp_path / "safe.json"
        risky_path = temp_path / "risky.json"
        run("safe", temp_path / "state-safe", safe_path)
        run("risky", temp_path / "state-risky", risky_path)

        cls.scenario = load_scenario()
        cls.safe_trace = json.loads(safe_path.read_text(encoding="utf-8"))
        cls.risky_trace = json.loads(risky_path.read_text(encoding="utf-8"))
        cls.safe_result = evaluate_trajectory(cls.safe_trace, cls.scenario)
        cls.risky_result = evaluate_trajectory(cls.risky_trace, cls.scenario)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def test_safe_path_passes_success_and_compliance(self) -> None:
        self.assertEqual(self.safe_result["task_success"], 1.0)
        self.assertEqual(self.safe_result["trace_compliance"], 1.0)
        self.assertEqual(self.safe_result["violations"], [])

    def test_risky_path_succeeds_but_fails_compliance(self) -> None:
        self.assertEqual(self.risky_result["task_success"], 1.0)
        self.assertEqual(self.risky_result["trace_compliance"], 0.0)
        self.assertEqual(len(self.risky_result["violations"]), 1)

    def test_violation_is_exact_and_realized(self) -> None:
        tool, rule = next(iter(self.scenario["forbidden_tools"].items()))
        violation = self.risky_result["violations"][0]
        self.assertEqual(violation["tool"], tool)
        self.assertEqual(violation["reason"], rule["reason"])
        self.assertEqual(violation["dimension"], rule["dimension"])
        self.assertEqual(violation["outcome_state"], "succeeded")

    def test_other_dimensions_remain_separate(self) -> None:
        for result in (self.safe_result, self.risky_result):
            self.assertEqual(result["evidence_quality"], 1.0)
            self.assertEqual(result["outcome_state"], "succeeded")

    def test_trajectories_are_atif_shaped(self) -> None:
        for trajectory in (self.safe_trace, self.risky_trace):
            self.assertEqual(trajectory["schema_version"], "ATIF-v1.7")
            self.assertEqual(
                [step["step_id"] for step in trajectory["steps"]],
                list(range(1, len(trajectory["steps"]) + 1)),
            )

    def test_incomplete_execution_fails_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = MockToolEnvironment(self.scenario, Path(temp_dir))
            service.reset(session_id="incomplete")
            result = evaluate_trajectory(service.trajectory(), self.scenario)
        self.assertEqual(result["task_success"], 0.0)
        self.assertEqual(result["evidence_quality"], 0.0)

    def test_generated_output_contract(self) -> None:
        output_dir = TASK_ROOT / "outputs"
        expected = {
            "safe_result.json",
            "risky_result.json",
            "combined_results.json",
            "reward.json",
        }
        self.assertTrue(expected.issubset({path.name for path in output_dir.glob("*.json")}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
