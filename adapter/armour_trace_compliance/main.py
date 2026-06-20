"""CLI for generating the Armour Harbor dataset."""

from __future__ import annotations

import argparse
import filecmp
import tempfile
from pathlib import Path

from .adapter import ArmourTraceComplianceAdapter


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "benchmark"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--task-ids", nargs="+", default=None)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify checked-in generated tasks match the adapter output.",
    )
    args = parser.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory() as temp_dir:
            expected = Path(temp_dir) / "benchmark"
            generated = ArmourTraceComplianceAdapter(
                expected,
                limit=args.limit,
                overwrite=True,
                task_ids=args.task_ids,
            ).run()
            for expected_task in generated:
                actual_task = args.output_dir / expected_task.name
                if not actual_task.is_dir() or not _same_tree(expected_task, actual_task):
                    raise SystemExit(f"Generated task is stale: {actual_task}")
        print(f"Generated tasks match {args.output_dir}")
        return

    generated = ArmourTraceComplianceAdapter(
        args.output_dir,
        limit=args.limit,
        overwrite=args.overwrite,
        task_ids=args.task_ids,
    ).run()
    print(f"Generated {len(generated)} tasks in {args.output_dir}")


def _same_tree(expected: Path, actual: Path) -> bool:
    comparison = filecmp.dircmp(expected, actual, ignore=["outputs", "__pycache__"])
    if comparison.left_only or comparison.right_only or comparison.diff_files or comparison.funny_files:
        return False
    return all(
        _same_tree(expected / name, actual / name)
        for name in comparison.common_dirs
    )


if __name__ == "__main__":
    main()
