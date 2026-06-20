#!/usr/bin/env python3
"""Scenario-driven mocked tools with a structured execution record."""

from __future__ import annotations

import argparse
import copy
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SCENARIO_PATH = Path(__file__).resolve().with_name("scenario.json")
DEFAULT_STATE_DIR = Path(os.environ.get("ARMOUR_STATE_DIR", "/tmp/armour-state"))
BASE_TIME = datetime(2026, 6, 19, 14, 0, tzinfo=timezone.utc)


def load_scenario() -> dict[str, Any]:
    return json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))


class MockToolEnvironment:
    def __init__(self, scenario: dict[str, Any], state_dir: Path = DEFAULT_STATE_DIR) -> None:
        self.scenario = scenario
        self.state_dir = state_dir
        self.events_path = state_dir / "events.jsonl"
        self.final_answer_path = state_dir / "final_answer.txt"
        self.session_path = state_dir / "session.json"

    def reset(self, *, session_id: str) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.events_path.write_text("", encoding="utf-8")
        self.final_answer_path.unlink(missing_ok=True)
        self.session_path.write_text(
            json.dumps({"session_id": session_id}, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        outputs = self.scenario["tool_outputs"]
        if tool not in outputs:
            raise ValueError(f"Unknown tool: {tool}")
        observation = copy.deepcopy(outputs[tool])
        event = {
            "sequence": len(self.events()) + 1,
            "tool": tool,
            "arguments": arguments,
            "outcome_state": "succeeded",
            "observation": observation,
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        return observation

    def finalize(self, final_answer: str) -> None:
        if not final_answer.strip():
            raise ValueError("Final answer must not be empty")
        self.final_answer_path.write_text(final_answer.strip() + "\n", encoding="utf-8")

    def events(self) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []
        return [
            json.loads(line)
            for line in self.events_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def trajectory(self) -> dict[str, Any]:
        session = json.loads(self.session_path.read_text(encoding="utf-8"))
        events = self.events()
        steps: list[dict[str, Any]] = [
            {
                "step_id": 1,
                "timestamp": _timestamp(0),
                "source": "user",
                "message": self.scenario["instruction_summary"],
            }
        ]
        for index, event in enumerate(events, start=2):
            call_id = f"call-{index - 1}"
            steps.append(
                {
                    "step_id": index,
                    "timestamp": _timestamp(index - 1),
                    "source": "agent",
                    "message": f"Calling {event['tool']}.",
                    "tool_calls": [
                        {
                            "tool_call_id": call_id,
                            "function_name": event["tool"],
                            "arguments": event["arguments"],
                            "extra": {"outcome_state": event["outcome_state"]},
                        }
                    ],
                    "observation": {
                        "results": [
                            {
                                "source_call_id": call_id,
                                "content": json.dumps(event["observation"], sort_keys=True),
                            }
                        ]
                    },
                }
            )

        if self.final_answer_path.exists():
            steps.append(
                {
                    "step_id": len(steps) + 1,
                    "timestamp": _timestamp(len(steps)),
                    "source": "agent",
                    "message": self.final_answer_path.read_text(encoding="utf-8").strip(),
                }
            )
        return {
            "schema_version": "ATIF-v1.7",
            "session_id": session["session_id"],
            "agent": {
                "name": "harbor-or-mocked-agent",
                "version": "0.3",
                "model_name": "agent-selected",
            },
            "steps": steps,
            "final_metrics": {"total_steps": len(steps)},
            "extra": {
                "task_id": self.scenario["task_id"],
                "domain": self.scenario["domain"],
                "trajectory_source": "mock-tool-audit-log",
            },
        }

    def write_trajectory(self, output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
        temporary.write_text(
            json.dumps(self.trajectory(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output)


def _timestamp(offset_seconds: int) -> str:
    return (BASE_TIME + timedelta(seconds=offset_seconds)).isoformat().replace("+00:00", "Z")


def _arguments(value: str) -> dict[str, Any]:
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("Tool arguments must be a JSON object")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    subparsers = parser.add_subparsers(dest="command", required=True)

    call = subparsers.add_parser("call")
    call.add_argument("--tool", required=True)
    call.add_argument("--arguments", type=_arguments, required=True)

    finalize = subparsers.add_parser("finalize")
    finalize.add_argument("--final-answer", required=True)

    emit = subparsers.add_parser("emit-trajectory")
    emit.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    service = MockToolEnvironment(load_scenario(), args.state_dir)
    if args.command == "call":
        print(json.dumps(service.call(args.tool, args.arguments), sort_keys=True))
    elif args.command == "finalize":
        service.finalize(args.final_answer)
    else:
        service.write_trajectory(args.output)


if __name__ == "__main__":
    main()
