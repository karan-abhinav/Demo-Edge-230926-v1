from edge_telemetry.features import summarize, zscores
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
