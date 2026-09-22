#!/usr/bin/env python3
"""PostToolUse hook, matcher Edit|Write.

Formats the file Claude just touched, applies every fix ruff can apply, and
hands any remaining findings back as additionalContext so Claude sees them on
its next turn. Never blocks: the edit already happened.
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _hookio import hook_output, read_input  # noqa: E402


def ruff(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["ruff", *args], capture_output=True, text=True, timeout=20
    )


def main() -> None:
    payload = read_input()
    path = payload.get("tool_input", {}).get("file_path", "")
    if not path.endswith(".py") or not Path(path).is_file():
        sys.exit(0)

    try:
        ruff("format", path)
        ruff("check", "--fix", path)
        remaining = ruff("check", "--output-format", "concise", path).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        sys.exit(0)  # ruff not installed, or wedged - stay out of the way

    if remaining and "All checks passed" not in remaining:
        hook_output(
            "PostToolUse",
            additionalContext=(
                f"ruff still reports issues in {Path(path).name} after "
                f"auto-fix:\n{remaining}"
            ),
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
