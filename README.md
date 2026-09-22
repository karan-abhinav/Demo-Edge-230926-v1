# edge-telemetry — Claude Code extension-layer lab

Sandbox repository for the training **"Claude Code: Extending the Agent —
Subagents, MCP, Hooks and Plugins."**

It is a small, real, working Python project: a sensor-telemetry pipeline with
240 rows of fixture data, a passing test suite, and two deliberately planted
defects for the labs to find.

## Contents

| Path | What it is |
|---|---|
| `TOPICS.md` | The full topic list for the day |
| `LABS.md` | Nine hands-on labs with checkpoints |
| `INSTRUCTOR_NOTES.md` | Timings, planted defects, demo cues, failure modes |
| `src/edge_telemetry/` | The package under test |
| `tests/` | pytest suite — 7 tests, all green at the start |
| `data/sensor_runs.csv` | 240 sensor runs; write-protected during the labs |
| `mcp_servers/telemetry_mcp.py` | The MCP server built in Lab B2 |
| `.claude/` | Where participants build their own agents and hooks |
| `solutions/` | Reference answers — keep closed until each lab is done |

## Setup (10 minutes, do this before the session)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install "mcp[cli]>=1.2"        # only needed for Lab B2

python -m pytest -q                # expect: 7 passed
python scripts/seed_db.py          # expect: inserted 240 rows
ruff check --output-format concise .   # expect: exactly 2 findings
```

Then start a session in this directory:

```bash
claude
```

## Verify your environment

| Check | Expected |
|---|---|
| `claude --version` | 2.1.x or later |
| `python --version` | 3.10 or later |
| `python -m pytest -q` | `7 passed` |
| `ruff check .` | 2 errors, both in `src/edge_telemetry/ingest.py` |
| `python scripts/seed_db.py` | `inserted 240 rows` |
| `sqlite3 data/telemetry.db "SELECT COUNT(*) FROM runs"` | `240` |

If `sqlite3` is missing, the MCP server still works — it uses Python's
built-in `sqlite3` module. Only the `db-reader` lab needs the CLI.

## House rules for the day

- Do not edit anything under `data/`. Lab C2 makes that a hard guarantee.
- Do not open `solutions/` until you have finished the lab it answers.
- Break things. The repository is disposable; `git checkout .` resets it.
