#!/usr/bin/env python3
"""SessionStart hook.

Injects live repository state into the conversation before the first prompt.

Write the text as factual statements, not commands. Phrasing that reads like
an out-of-band system instruction trips Claude's prompt-injection defences,
and the text gets surfaced to the user instead of used as context.
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _hookio import hook_output  # noqa: E402


def git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args], capture_output=True, text=True, timeout=5
        )
        return out.stdout.strip()
    except Exception:
        return ""


def main() -> None:
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    dirty = len([ln for ln in git("status", "--porcelain").splitlines() if ln])
    db = "built" if Path("data/telemetry.db").exists() else "not built yet"

    hook_output(
        "SessionStart",
        additionalContext=(
            f"Repository state: branch {branch}, {dirty} uncommitted file(s). "
            f"The SQLite database data/telemetry.db is {db}; it is rebuilt with "
            f"python scripts/seed_db.py. "
            f"Tests run with: python -m pytest -q. "
            f"Lint and format run with: ruff check . and ruff format . "
            f"The data/ and solutions/ directories are write-protected by a "
            f"PreToolUse hook."
        ),
    )


if __name__ == "__main__":
    main()
