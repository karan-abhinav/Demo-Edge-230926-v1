#!/usr/bin/env python3
"""PreToolUse (matcher: Edit|Write|NotebookEdit).

Denies writes to the class fixture data, the solutions directory, and any
dotenv file. Returns a structured permissionDecision instead of exiting 2 so
Claude receives a readable reason.
"""

import fnmatch
import json
import os
import sys

PROTECTED = [
    "data/*",
    "solutions/*",
    ".env",
    "*.env",
    "*.db",
]


def deny(reason: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # never block on a parse failure

    path = payload.get("tool_input", {}).get("file_path") or ""
    if not path:
        sys.exit(0)

    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        rel = os.path.relpath(path, project)
    except ValueError:
        rel = path
    rel = rel.replace(os.sep, "/")
    base = os.path.basename(rel)

    for pattern in PROTECTED:
        if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(base, pattern):
            deny(
                f"'{rel}' is protected by the project guardrail hook "
                f"(pattern '{pattern}'). Fixture data and reference solutions "
                f"are read-only. Ask the user if you believe this is wrong."
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
