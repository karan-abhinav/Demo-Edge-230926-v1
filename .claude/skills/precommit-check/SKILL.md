---
name: precommit-check
description: Run the edge-telemetry pre-commit checklist (tests, ruff, docstrings/type hints on public functions, data/ untouched, secret scan) before committing. Use when the user asks to commit, asks "is this ready", or wants a final check of their changes.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(python -m pytest:*), Bash(ruff:*), Read, Grep, Glob
---

# Pre-commit check

Run every check, then report a pass/fail table. This skill only reports: don't fix,
stage or commit anything unless the user asks.

## Checks

1. **Tests.** `python -m pytest -q` must pass. Quote any failures.
2. **Lint.** `ruff check .` must be clean. Run `ruff format --check .` and list the
   files it would reformat.
3. **Fixture data untouched.** `git status --porcelain data/` must print nothing. If any
   file under `data/` changed, that's a hard FAIL, because the directory is the class
   fixture set.
4. **Conventions on changed code.** For each changed `.py` file under `src/`
   (`git diff --name-only`), every public function (no leading `_`) needs type hints and
   a docstring. List any that don't have them.
5. **New behaviour has tests.** If `src/` has changed but `tests/` hasn't, flag it as a
   WARNING.
6. **Secrets.** Grep the diff and `src/` for tokens, keys and passwords. A pattern like
   `(?i)(token|secret|api_key|password)\s*=\s*["'][^"']+` is a reasonable start. Report
   each hit with its file and line. Don't rewrite it; CLAUDE.md says to report secrets,
   not silently fix them.
   - Known: `FLEET_API_TOKEN` in `src/edge_telemetry/config.py` is hard-coded. Always
     report it until it's removed.
7. **Solutions folder.** Warn if the diff touches `solutions/`.

## Output

| check | result | detail |
|---|---|---|

End with **READY** or **NOT READY** and the blocking items.
