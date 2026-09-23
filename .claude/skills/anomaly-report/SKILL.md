---
name: anomaly-report
description: Run the edge-telemetry anomaly detector and explain which runs were flagged and why (threshold breaches vs z-score outliers), optionally for one device. Use when asked about anomalies, faults, flagged runs, or detector accuracy.
argument-hint: "[device_id]"
---

# Anomaly report

## 1. Run the detector

From the repo root (on Windows PowerShell, set `$env:PYTHONPATH="src"` first):

```bash
PYTHONPATH=src python -m edge_telemetry.cli detect            # whole fleet
PYTHONPATH=src python -m edge_telemetry.cli detect --device $ARGUMENTS
```

Each finding contains `run_id`, `device_id`, `timestamp`, `flags` and `zscore`.

## 2. Explain each finding

The thresholds live in `src/edge_telemetry/config.py` (`Thresholds`). Read the current
values there rather than assuming them. At the time of writing they are:

| field | limit |
|---|---|
| temp_c | > 58.0 |
| vibration_g | > 0.95 |
| current_a | > 2.6 |
| zscore | >= 3.0 (max of \|z\| for temp and vibration, computed over the loaded set) |

A run is flagged if it breaches any threshold or reaches the z-score limit. The z-scores
are computed over whatever set was loaded, so a single-device run gives different scores
from a fleet-wide run. Mention this whenever you compare the two.

## 3. Check against ground truth

The fixture labels every run `ok` or `fault`. Compare the flagged runs with the labels
(use the `fleet-query` skill, or `load_runs()`) and report:

- true positives: faults that were flagged
- false positives: `ok` runs that were flagged
- missed faults: faults that were not flagged

## 4. Output

Give a table of the findings (run_id, device, flags, zscore, label), the TP/FP/missed
counts, and one sentence on whether the thresholds look too loose or too tight. Don't
change the thresholds unless the user asks you to.
