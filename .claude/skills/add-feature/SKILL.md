---
name: add-feature
description: Add a new feature/statistic function to src/edge_telemetry/features.py (e.g. p95_vibration, max_current, rolling stats) following the project's test-first conventions. Use when asked to add a metric, feature, or summary function to the package.
---

# Add a feature function

Follow these steps in order. The CLAUDE.md conventions apply, and a feature does not
count as done until it has a passing test.

## 1. Write the test first

Add the test to `tests/test_features.py`, matching the tests already there: plain
`assert`, no classes, names like `test_<feature>_<behaviour>`. Cover at least:

- a small hand-computed input, such as `[{"temp_c": 1.0}, {"temp_c": 3.0}]`
- the empty-input case (existing functions return `0.0` or an empty structure; they don't raise)
- one sanity check against the real fixture through `load_runs()` (240 runs)

Run `python -m pytest -q tests/test_features.py` and confirm the new test fails.

## 2. Implement

In `src/edge_telemetry/features.py`:

- Type-hint the signature. Runs are `List[Dict[str, object]]`, and values are read
  with `float(r["<field>"])`.
- Write a one-line docstring that says what comes back and what empty input gives.
- Prefer the `statistics` stdlib. The package has no numpy dependency.
- Keep lines at or under 100 columns.
- Don't touch `rolling_mean`. Its `KNOWN BUG` is a deliberate lab target.

## 3. Expose it (optional)

If the user wants it on the CLI, add a subcommand or flag in `src/edge_telemetry/cli.py`
next to `summary`, and have it print JSON the way the other commands do.

## 4. Verify

```bash
python -m pytest -q
ruff check . && ruff format .
```

Report the new function signature, the tests added and the pytest result.
