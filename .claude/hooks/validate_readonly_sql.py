#!/usr/bin/env python3
"""PreToolUse hook registered in the db-reader subagent's frontmatter.

Demonstrates the other half of the decision API: exit code 2 blocks the tool
call and shows stderr to the agent, with no JSON involved. Compare with
protect_paths.py, which returns a structured permissionDecision instead.
"""

import json
import re
import sys

WRITE_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|ATTACH|PRAGMA)\b",
    re.IGNORECASE,
)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    command = payload.get("tool_input", {}).get("command", "")
    if command and WRITE_SQL.search(command):
        print(
            "Blocked: db-reader may only run SELECT statements against "
            "telemetry.db.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
