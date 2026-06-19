#!/usr/bin/env python3
"""Local entry point for the evaluator packaged with the Harbor environment."""

from __future__ import annotations

import sys
from pathlib import Path


ENVIRONMENT_DIR = Path(__file__).resolve().parents[1] / "environment"
sys.path.insert(0, str(ENVIRONMENT_DIR))

from trace_evaluator import *  # noqa: F401,F403,E402
from trace_evaluator import main  # noqa: E402


if __name__ == "__main__":
    main()
