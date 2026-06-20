#!/usr/bin/env python3
"""Tests for the deterministic Kaggle/FDE handoff export."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.export_handoff_bundle import build_bundle, validate_bundle


class HandoffBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output = Path(self.temp_dir.name) / "handoff"
        self.manifest = build_bundle(self.output)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_required_review_files_are_present(self) -> None:
        expected = {
            "README.md",
            "docs/KAGGLE_FDE_HANDOFF_PACKET.md",
            "docs/HARBOR_OUTPUT_CONTRACT.md",
            "docs/AUTOMATION_BENCH_REVIEW.md",
            "benchmark/dataset.toml",
            "results/validation_summary.json",
            "benchmark/customer-ticket-data-scope/task.toml",
        }
        paths = {entry["path"] for entry in self.manifest["files"]}
        self.assertTrue(expected.issubset(paths))
        self.assertGreaterEqual(self.manifest["file_count"], 10)

    def test_manifest_covers_exact_files_and_hashes(self) -> None:
        validate_bundle(self.output, minimum_files=10)
        parsed = json.loads(
            (self.output / "MANIFEST.json").read_text(encoding="utf-8")
        )
        self.assertEqual(parsed, self.manifest)

    def test_runtime_outputs_and_bytecode_are_excluded(self) -> None:
        paths = [entry["path"] for entry in self.manifest["files"]]
        self.assertFalse(any("/outputs/" in path for path in paths))
        self.assertFalse(any("__pycache__" in path for path in paths))
        self.assertFalse(any(path.endswith(".pyc") for path in paths))


if __name__ == "__main__":
    unittest.main(verbosity=2)
