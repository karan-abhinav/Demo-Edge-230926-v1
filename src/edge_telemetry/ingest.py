"""Load raw sensor runs from CSV into plain dictionaries."""

import csv
from pathlib import Path
from typing import Dict, Iterator, List

from .config import CSV_PATH

NUMERIC_FIELDS = ("temp_c", "vibration_g", "current_a", "rpm")


def _coerce(row: Dict[str, str]) -> Dict[str, object]:
    """Copy a CSV row with numeric fields cast to float, using 0.0 for unparseable values."""
    out: Dict[str, object] = dict(row)
    for field in NUMERIC_FIELDS:
        try:
            out[field] = float(row[field])
        except (KeyError, TypeError, ValueError):
            out[field] = 0.0
    return out


def iter_runs(path: Path = CSV_PATH) -> Iterator[Dict[str, object]]:
    """Yield one coerced record per row of the sensor CSV."""
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            yield _coerce(row)


def load_runs(path: Path = CSV_PATH, device_id: str = None) -> List[Dict[str, object]]:
    """Return all runs, optionally filtered to a single device."""
    runs = list(iter_runs(path))
    if device_id:
        runs = [r for r in runs if r["device_id"] == device_id]
    return runs


def device_ids(path: Path = CSV_PATH) -> List[str]:
    """Return the sorted set of device identifiers present in the file."""
    return sorted({r["device_id"] for r in iter_runs(path)})
