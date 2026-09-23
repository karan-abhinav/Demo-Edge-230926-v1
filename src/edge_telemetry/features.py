"""Windowed feature extraction over a run sequence."""

from statistics import mean, median, pstdev, quantiles
from typing import Dict, List, Sequence


def rolling_mean(values: Sequence[float], window: int) -> List[float]:
    """Rolling mean over `window` samples.

    KNOWN BUG (Lab A2 target): the slice start is off by one, so each window
    contains window-1 samples. Ask the debugger subagent to find it.
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    out: List[float] = []
    for i in range(len(values)):
        start = max(0, i - window + 2)
        out.append(mean(values[start : i + 1]))
    return out


def zscores(values: Sequence[float]) -> List[float]:
    """Population z-score for every sample."""
    if not values:
        return []
    mu = mean(values)
    sigma = pstdev(values)
    if sigma == 0:
        return [0.0] * len(values)
    return [(v - mu) / sigma for v in values]


def summarize(runs: List[Dict[str, object]], field: str) -> Dict[str, float]:
    """Min/max/mean/stdev for one numeric field across a set of runs."""
    values = [float(r[field]) for r in runs]
    if not values:
        return {"count": 0, "min": 0.0, "max": 0.0, "mean": 0.0, "stdev": 0.0}
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "stdev": pstdev(values),
    }


def median_temp(runs: List[Dict[str, object]]) -> float:
    """Median `temp_c` across a set of runs, or 0.0 when there are none."""
    temps = [float(r["temp_c"]) for r in runs]
    if not temps:
        return 0.0
    return median(temps)


def p95_vibration(runs: List[Dict[str, object]]) -> float:
    """95th-percentile `vibration_g` (linear interpolation), or 0.0 when there are no runs."""
    values = [float(r["vibration_g"]) for r in runs]
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    return quantiles(values, n=100, method="inclusive")[94]


def peak_current(runs: List[Dict[str, object]]) -> float:
    """Maximum `current_a` across a set of runs, or 0.0 when there are none."""
    return max((float(r["current_a"]) for r in runs), default=0.0)
