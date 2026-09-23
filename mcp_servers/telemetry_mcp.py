#!/usr/bin/env python3
"""A read-only MCP server over data/telemetry.db.

Built in Lab B2. Run it directly to smoke-test it:

    pip install "mcp[cli]>=1.2,<2"
    python3 mcp_servers/telemetry_mcp.py

Register it with Claude Code:

    claude mcp add --scope project telemetry \
      -- python3 "$PWD/mcp_servers/telemetry_mcp.py"

Tool descriptions are the whole interface Claude sees. Write them the way you
would write an API doc: what it returns, in what shape, and when to reach for it.
"""

import os
import sqlite3
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

DB_PATH = Path(
    os.environ.get(
        "TELEMETRY_DB",
        Path(__file__).resolve().parents[1] / "data" / "telemetry.db",
    )
)

mcp = FastMCP("telemetry")

ALLOWED_ORDER = {"timestamp", "temp_c", "vibration_g", "current_a", "rpm"}


def _rows(sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"{DB_PATH} is missing. Run: python scripts/seed_db.py"
        )
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


@mcp.tool()
def schema() -> str:
    """Return the CREATE statement for every table in the telemetry database.

    Call this first when you do not yet know the column names.
    """
    rows = _rows("SELECT sql FROM sqlite_master WHERE type='table'")
    return "\n\n".join(r["sql"] for r in rows if r["sql"])


@mcp.tool()
def list_devices() -> list[dict[str, Any]]:
    """List every device in the fleet with its run count and mean temperature.

    Returns one object per device: device_id, runs, mean_temp_c, fault_runs.
    Use this to decide which device is worth drilling into.
    """
    return _rows(
        """
        SELECT device_id,
               COUNT(*)                                   AS runs,
               ROUND(AVG(temp_c), 2)                      AS mean_temp_c,
               SUM(CASE WHEN label='fault' THEN 1 ELSE 0 END) AS fault_runs
        FROM runs GROUP BY device_id ORDER BY device_id
        """
    )


@mcp.tool()
def query_runs(
    device_id: Optional[str] = None,
    label: Optional[str] = None,
    order_by: str = "timestamp",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Fetch individual telemetry runs, newest first by default.

    Args:
        device_id: restrict to one device, e.g. "uno-q-01". Omit for all devices.
        label: restrict to "ok" or "fault". Omit for both.
        order_by: one of timestamp, temp_c, vibration_g, current_a, rpm.
        limit: maximum rows to return, 1-200.

    Returns one object per run with every column of the runs table.
    """
    if order_by not in ALLOWED_ORDER:
        raise ValueError(f"order_by must be one of {sorted(ALLOWED_ORDER)}")
    limit = max(1, min(int(limit), 200))

    clauses, params = [], []
    if device_id:
        clauses.append("device_id = ?")
        params.append(device_id)
    if label:
        clauses.append("label = ?")
        params.append(label)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    return _rows(
        f"SELECT * FROM runs {where} ORDER BY {order_by} DESC LIMIT ?",
        (*params, limit),
    )


@mcp.tool()
def anomaly_summary(temp_threshold: float = 58.0) -> dict[str, Any]:
    """
    Summary.
    """
    total = _rows("SELECT COUNT(*) AS n FROM runs")[0]["n"]
    per_device = _rows(
        """
        SELECT device_id, COUNT(*) AS breaching, ROUND(MAX(temp_c), 2) AS peak_temp_c
        FROM runs WHERE temp_c > ? GROUP BY device_id ORDER BY breaching DESC
        """,
        (temp_threshold,),
    )
    return {
        "temp_threshold": temp_threshold,
        "total_runs": total,
        "breaching_runs": sum(d["breaching"] for d in per_device),
        "per_device": per_device,
    }


if __name__ == "__main__":
    mcp.run()
