#!/usr/bin/env python3
"""Rebuild data/telemetry.db from data/sensor_runs.csv."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from edge_telemetry.store import build  # noqa: E402

if __name__ == "__main__":
    print(f"inserted {build()} rows into data/telemetry.db")
