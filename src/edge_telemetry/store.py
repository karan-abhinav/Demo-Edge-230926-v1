"""SQLite persistence for telemetry runs."""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from .config import DB_PATH
from .ingest import iter_runs

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id      TEXT PRIMARY KEY,
    timestamp   TEXT NOT NULL,
    device_id   TEXT NOT NULL,
    temp_c      REAL NOT NULL,
    vibration_g REAL NOT NULL,
    current_a   REAL NOT NULL,
    rpm         INTEGER NOT NULL,
    label       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_device ON runs(device_id);
"""


def connect(path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def build(path: Path = DB_PATH) -> int:
    """(Re)build the SQLite database from the CSV. Returns the row count."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = connect(path)
    with conn:
        conn.executescript(SCHEMA)
        conn.execute("DELETE FROM runs")
        conn.executemany(
            "INSERT INTO runs VALUES (:run_id, :timestamp, :device_id, "
            ":temp_c, :vibration_g, :current_a, :rpm, :label)",
            list(iter_runs()),
        )
    count = conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
    conn.close()
    return count


def query(
    sql: str, params: tuple = (), path: Path = DB_PATH
) -> List[Dict[str, Any]]:
    """Run a SELECT and return rows as dictionaries."""
    conn = connect(path)
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
