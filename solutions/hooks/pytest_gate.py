#!/usr/bin/env python3
"""Stop hook.

Refuses to end the turn while the suite is red, using the top-level
decision/reason shape that Stop and SubagentStop understand.

The stop_hook_active guard is not optional: without it a blocked Stop fires
this hook again on the next attempt and you get an infinite loop.
"""

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _hookio import emit, read_input  # noqa: E402


def main() -> None:
    payload = read_input()
    if payload.get("stop_hook_active"):
        sys.exit(0)

    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if not (Path(project) / "tests").is_dir():
        sys.exit(0)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=110,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        sys.exit(0)

    if result.returncode == 0:
        sys.exit(0)

    tail = "\n".join((result.stdout + result.stderr).splitlines()[-25:])
    emit(
        {
            "decision": "block",
            "reason": (
                "The test suite is failing, so this task is not finished. "
                f"Fix these before stopping:\n{tail}"
            ),
        }
    )


if __name__ == "__main__":
    main()
