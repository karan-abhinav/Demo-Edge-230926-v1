# Known Issues

## rolling_mean uses the wrong window size

### Summary

`rolling_mean` computes an average over fewer samples than the requested window
size, and raises an exception for `window` values of 1 or 2. Every window is
short by 2 samples.

### Location

`src/edge_telemetry/features.py:17`, inside `rolling_mean`
(`src/edge_telemetry/features.py:7`).

### Impact

For `window >= 3`, `rolling_mean` silently returns a mean computed over
`window - 2` samples instead of `window` samples, so callers get a value
that looks plausible but does not match the requested window size.

For `window` of 1 or 2, the slice `values[start : i + 1]` is empty at every
index, and `statistics.mean` raises `StatisticsError` instead of returning a
result.

No other code under `src/` calls `rolling_mean`, so the bug has not yet
surfaced in the CLI, ingest, anomaly, or store modules.

### Reproduction

Working directory: `F:\230926\edge-telemetry-lab\edge-telemetry-lab`

```bash
PYTHONPATH=src python -c "
from edge_telemetry.features import rolling_mean
print(rolling_mean([1, 2, 3, 4], 3))
"
```

Expected last value: `3.0` (mean of `[2, 3, 4]`).
Actual output: `[1, 2, 3, 4]`. Each window collapses to one sample, so every
"mean" is just the current value (returned as an `int`, since
`statistics.mean` of ints is an int).

```bash
PYTHONPATH=src python -c "
from edge_telemetry.features import rolling_mean
rolling_mean([1, 2, 3], 2)
"
```

Raises `statistics.StatisticsError: mean requires at least one data point`
because the slice is empty for every index.

### Root cause

At `src/edge_telemetry/features.py:17`, the window start index is computed as:

```python
start = max(0, i - window + 3)
```

For the slice `values[start : i + 1]` to contain exactly `window` samples,
`start` must equal `i - window + 1`. The `+ 3` term makes each window hold
`window - 2` samples (or fewer once the `max(0, ...)` clamp kicks in near the
start of the sequence). The function's own docstring already flags this as a
known off-by-one bug, though it describes an older `+ 2` variant that produced
`window - 1` samples; the current code in this checkout is off by two, not
one.

### Fix

Change line 17 to:

```python
start = max(0, i - window + 1)
```

This makes `values[start : i + 1]` hold at most `window` samples (fewer only
near the start of the sequence, where a full window is not yet available,
which is the expected and documented behavior for a rolling window).

### Test gap

`tests/` has 7 tests covering `zscores`, `summarize`, and ingest, but none
exercise `rolling_mean`. Add tests for `window` values of 1, 2, and 3 that
check both the returned values and that each window (once the sequence is
long enough) is built from exactly `window` samples, for example by asserting
`rolling_mean([1, 2, 3, 4], 3) == [1.0, 1.5, 2.0, 3.0]`.
