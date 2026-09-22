---
name: lab-report
description: Produce a markdown lab report summarising what changed in this session - files touched, tests run, findings raised. Use at the end of a working session or when the user asks for a report or handover note.
disable-model-invocation: true
---

# Lab report

Produce a handover note for the work done in this session.

## Gather

1. `git status --porcelain` and `git diff --stat` for the changed files.
2. `python -m pytest -q` for the current test state.
3. `ruff check --output-format concise .` for outstanding lint findings.

## Write

Create `reports/session-<YYYY-MM-DD-HHMM>.md` with these sections, in order:

| Section | Contents |
|---|---|
| Objective | One sentence: what the session set out to do. |
| Changes | Table of file, lines added/removed, one-line rationale. |
| Verification | Test count and result, lint findings that remain. |
| Open items | Anything deliberately left undone, with a reason. |

Keep it under 400 words. Do not restate diffs the reader can run `git diff`
for. If `$ARGUMENTS` is non-empty, use it as the objective line verbatim.
