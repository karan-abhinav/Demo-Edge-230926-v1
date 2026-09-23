from statistics import median

from edge_telemetry.features import p95_vibration, summarize, zscores
from edge_telemetry.ingest import load_runs


def test_zscores_centre_on_zero():
    scores = zscores([1.0, 2.0, 3.0, 4.0])
    assert abs(sum(scores)) < 1e-9


def test_zscores_handle_constant_input():
    assert zscores([5.0, 5.0, 5.0]) == [0.0, 0.0, 0.0]


def test_summarize_reports_counts():
    stats = summarize(load_runs(), "temp_c")
    assert stats["count"] == 240
    assert stats["min"] < stats["mean"] < stats["max"]


def test_p95_vibration_interpolates_between_samples():
    runs = [{"vibration_g": 1.0}, {"vibration_g": 3.0}]
    assert abs(p95_vibration(runs) - 2.9) < 1e-9


def test_p95_vibration_single_run_returns_its_value():
    assert p95_vibration([{"vibration_g": 0.4}]) == 0.4


def test_p95_vibration_empty_returns_zero():
    assert p95_vibration([]) == 0.0


def test_p95_vibration_on_fixture_sits_between_median_and_max():
    runs = load_runs()
    values = [float(r["vibration_g"]) for r in runs]
    assert median(values) < p95_vibration(runs) <= max(values)
