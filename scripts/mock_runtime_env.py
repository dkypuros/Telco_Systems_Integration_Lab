#!/usr/bin/env python3
"""Runtime environment helper for copied mock services.

This module intentionally does not edit copied source files. It only builds the
PYTHONPATH needed for byte-identical copied sources that still import their
original package names (`config`, `core_network`, `oran`, top-level E2SM files).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

LAB_ROOT = Path(__file__).resolve().parents[1]
PYTHONPATH_ENTRIES: List[Path] = [
    LAB_ROOT / "services" / "mock_5g_core",
    LAB_ROOT / "adapters" / "mock_ran",
    LAB_ROOT / "adapters" / "mock_ran" / "ran" / "ric",
    LAB_ROOT / "adapters" / "mock_oran",
]


def runtime_pythonpath() -> str:
    existing = os.environ.get("PYTHONPATH", "")
    entries = [str(p) for p in PYTHONPATH_ENTRIES]
    if existing:
        entries.append(existing)
    return os.pathsep.join(entries)


def runtime_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = runtime_pythonpath()
    return env


if __name__ == "__main__":
    print(runtime_pythonpath())
