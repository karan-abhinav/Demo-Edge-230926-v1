# edge-telemetry

A small sensor-telemetry pipeline used as the sandbox for the Claude Code
extension-layer training. Nothing here ships to production; break it freely.

## Layout

- `src/edge_telemetry/` — the package (ingest, features, anomaly, store, cli)
- `tests/` — pytest suite
- `data/sensor_runs.csv` — 240 sensor runs, the only real input
- `data/telemetry.db` — SQLite build of the CSV, produced by `scripts/seed_db.py`
- `mcp_servers/` — the custom MCP server built in Lab B2
- `solutions/` — reference answers; do not read these while a lab is in progress

## Commands

```bash
python -m pytest -q                     # tests
ruff check . && ruff format .           # lint and format
python scripts/seed_db.py               # rebuild data/telemetry.db
PYTHONPATH=src python -m edge_telemetry.cli detect
```

## Conventions

- Python 3.10+, 100-column lines, type hints on public functions.
- Every public function gets a one-line docstring.
- New behaviour needs a test in `tests/` before it is considered done.
- Never edit anything under `data/` — it is the fixture set for the whole class.
- Never commit secrets. If you find one, report it; do not silently rewrite it.
