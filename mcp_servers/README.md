# mcp_servers

`telemetry_mcp.py` is the custom MCP server built in Lab B2. It exposes four
read-only tools over `data/telemetry.db`.

## Setup

```bash
pip install "mcp[cli]>=1.2"
python scripts/seed_db.py          # the server needs the database to exist
```

## Register with Claude Code

Project scope, so it lands in a committable `.mcp.json`:

```bash
claude mcp add --scope project telemetry \
  -- python3 "$PWD/mcp_servers/telemetry_mcp.py"
```

Then inside a session:

```
/mcp                 # connection status per server
/context all         # how many tokens each loaded tool costs
```

Tools arrive as `mcp__telemetry__schema`, `mcp__telemetry__list_devices`,
`mcp__telemetry__query_runs`, `mcp__telemetry__anomaly_summary`.

## Why the tool docstrings are long

The docstring is the entire interface Claude sees when choosing a tool. "Runs
a query" loses to fifty other tools; "fetch individual telemetry runs, newest
first, filtered by device and label" wins. Treat the docstring as the product.
