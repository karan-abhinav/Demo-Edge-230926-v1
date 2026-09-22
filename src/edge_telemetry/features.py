"""Windowed feature extraction over a run sequence."""

from statistics import mean, pstdev
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
