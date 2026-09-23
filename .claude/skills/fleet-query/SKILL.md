---
name: fleet-query
description: Answer questions about the sensor fleet (per-device temperature, vibration, current, rpm, fault counts, hottest/noisiest device, trends) by running read-only SQL against data/telemetry.db. Use for any data question about runs or devices.
allowed-tools: Bash(python .claude/skills/fleet-query/query.py:*)
---

# Fleet query

Answer data questions from `data/telemetry.db` without ever writing to it.

## Schema

Table `runs` (240 rows, 4 devices × 60 runs):

| column | type | notes |
|---|---|---|
| run_id | TEXT PK | `R0001`… |
| timestamp | TEXT | ISO 8601 |
| device_id | TEXT | `rpi5-01`, `uno-q-01`, `uno-q-02`, `uno-q-03` |
| temp_c | REAL | °C |
| vibration_g | REAL | g |
| current_a | REAL | A |
| rpm | INTEGER | |
| label | TEXT | `'ok'` or `'fault'` (not `'normal'`) |

## How to run a query

Use the bundled read-only runner. It opens the DB with `mode=ro` and rejects anything
that is not a single `SELECT` / `WITH` statement:

```bash
python .claude/skills/fleet-query/query.py "SELECT device_id, ROUND(AVG(temp_c),2) FROM runs GROUP BY device_id"
```

Add `--median <column>` to get a per-device median (SQLite has no `MEDIAN`):

```bash
python .claude/skills/fleet-query/query.py --median temp_c
```

If `data/telemetry.db` is missing, tell the user to run `python scripts/seed_db.py`. Do not
run it yourself, and never modify anything under `data/`.

## Answering

1. Say which columns answer the question.
2. Show the SQL you ran.
3. Give a small Markdown table, then a one-line answer in bold.
4. For "which device is most X", report mean, median and max, and repeat with
   `label = 'ok'` only. Faults dominate the extremes, so a max-only ranking is misleading.
5. Point out when the gap between devices is too small to matter (for example, means
   within 0.5 °C).
