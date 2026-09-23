#!/usr/bin/env python3
"""Read-only query runner for data/telemetry.db, used by the fleet-query skill."""

import argparse
import sqlite3
import statistics
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "telemetry.db"
COLUMNS = {"temp_c", "vibration_g", "current_a", "rpm"}


def connect() -> sqlite3.Connection:
    """Open the telemetry database in read-only mode."""
    if not DB_PATH.exists():
        sys.exit(f"{DB_PATH} not found; run `python scripts/seed_db.py` first")
    return sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)


def print_table(headers: list, rows: list) -> None:
    """Print rows as a Markdown table."""
    print("| " + " | ".join(headers) + " |")
    print("|" + "---|" * len(headers))
    for row in rows:
        print("| " + " | ".join(str(v) for v in row) + " |")


def main() -> int:
    """Run one SELECT, or compute per-device medians."""
    parser = argparse.ArgumentParser()
    parser.add_argument("sql", nargs="?")
    parser.add_argument("--median", choices=sorted(COLUMNS))
    args = parser.parse_args()

    conn = connect()
    if args.median:
        by_device: dict = {}
        for device, value in conn.execute(f"SELECT device_id, {args.median} FROM runs"):
            by_device.setdefault(device, []).append(value)
        rows = sorted(
            ((d, round(statistics.median(v), 2)) for d, v in by_device.items()),
            key=lambda r: r[1],
            reverse=True,
        )
        print_table(["device_id", f"median_{args.median}"], rows)
        return 0

    if not args.sql:
        parser.error("provide a SQL query or --median")
    sql = args.sql.strip().rstrip(";")
    if ";" in sql or not sql.lower().startswith(("select", "with")):
        sys.exit("only a single SELECT/WITH statement is allowed")
    cur = conn.execute(sql)
    print_table([d[0] for d in cur.description], cur.fetchall())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
