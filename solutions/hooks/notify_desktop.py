#!/usr/bin/env python3
"""Notification hook.

Hooks run without a controlling terminal, so writing an escape sequence to
/dev/tty does nothing. Return it in terminalSequence and Claude Code emits it
through its own terminal write path - race-free, and it works under tmux and
on Windows.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _hookio import emit, read_input  # noqa: E402


def main() -> None:
    payload = read_input()
    body = payload.get("message") or "Claude Code needs your attention"
    # OSC 777 desktop notification; OSC 0/1/2/9/99/777 and BEL are allowed.
    emit({"terminalSequence": f"\033]777;notify;edge-telemetry;{body}\007"})


if __name__ == "__main__":
    main()
