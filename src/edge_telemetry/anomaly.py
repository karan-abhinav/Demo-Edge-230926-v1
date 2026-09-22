"""Threshold and z-score anomaly detection."""

from typing import Dict, List

from .config import DEFAULT_THRESHOLDS, Thresholds
from .features import zscores


def threshold_flags(run: Dict[str, object], th: Thresholds = DEFAULT_THRESHOLDS) -> List[str]:
    """Return the names of every threshold this run breaches."""
    flags = []
    if float(run["temp_c"]) > th.temp_c:
        flags.append("temp_c")
    if float(run["vibration_g"]) > th.vibration_g:
        flags.append("vibration_g")
    if float(run["current_a"]) > th.current_a:
        flags.append("current_a")
    return flags


def detect(
    runs: List[Dict[str, object]], th: Thresholds = DEFAULT_THRESHOLDS
) -> List[Dict[str, object]]:
    """Score every run and return the ones that look anomalous."""
    temps = [float(r["temp_c"]) for r in runs]
    vibs = [float(r["vibration_g"]) for r in runs]
    temp_z = zscores(temps)
    vib_z = zscores(vibs)

    findings = []
    for i, run in enumerate(runs):
        flags = threshold_flags(run, th)
        score = max(abs(temp_z[i]), abs(vib_z[i]))
        if flags or score >= th.zscore:
            findings.append(
                {
                    "run_id": run["run_id"],
                    "device_id": run["device_id"],
                    "timestamp": run["timestamp"],
                    "flags": flags,
                    "zscore": round(score, 3),
                }
            )
    return findings
