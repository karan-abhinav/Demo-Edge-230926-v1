from edge_telemetry.ingest import device_ids, load_runs


def test_load_runs_returns_records():
    runs = load_runs()
    assert len(runs) == 240
    assert set(runs[0]) >= {"run_id", "device_id", "temp_c", "label"}


def test_numeric_fields_are_floats():
    run = load_runs()[0]
    for field in ("temp_c", "vibration_g", "current_a", "rpm"):
        assert isinstance(run[field], float)


def test_device_filter():
    runs = load_runs(device_id="uno-q-01")
    assert runs
    assert {r["device_id"] for r in runs} == {"uno-q-01"}


def test_device_ids_are_sorted_and_unique():
    ids = device_ids()
    assert ids == sorted(set(ids))
