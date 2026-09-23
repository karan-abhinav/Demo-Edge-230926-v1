"""Tiny helper shared by the lab hooks.

Claude Code sends hook input as JSON on stdin and reads your decision from
stdout. That is the whole contract; this module just wraps it so the hook
scripts stay readable.
"""

import json
import sys
from typing import Any, Dict


def read_input() -> Dict[str, Any]:
    """Parse the event JSON from stdin. Never raise - a broken hook must not
    break the session, so a parse failure exits quietly with no decision."""
    try:
        return json.load(sys.stdin)
    except Exception:
        sys.exit(0)


def emit(payload: Dict[str, Any]) -> None:
    """Write one JSON object to stdout and exit 0.

    Stdout must contain nothing but this object. If your shell profile prints
    a banner, the JSON is ignored.
    """
    json.dump(payload, sys.stdout)
    sys.exit(0)


def hook_output(event: str, **fields: Any) -> None:
    """Emit a hookSpecificOutput object for `event`."""
    emit({"hookSpecificOutput": {"hookEventName": event, **fields}})
