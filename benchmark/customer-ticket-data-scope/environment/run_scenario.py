#!/usr/bin/env python3
"""Execute the catalog's safe or risky strategy against mocked tools."""

from __future__ import annotations

import argparse
from pathlib import Path

from armour_tool import MockToolEnvironment, load_scenario


def run(mode: str, state_dir: Path, output: Path) -> None:
    scenario = load_scenario()
    service = MockToolEnvironment(scenario, state_dir)
    service.reset(session_id=f"{mode}-{scenario['task_id']}")
    for call in scenario[f"{mode}_calls"]:
        service.call(call["tool"], call["arguments"])
    service.finalize(scenario["final_answer"])
    service.write_trajectory(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("safe", "risky"), required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.mode, args.state_dir, args.output)


if __name__ == "__main__":
    main()
