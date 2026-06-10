#!/usr/bin/env python3
"""
Post an ai_activity event to the dashboard (used by Claude Code skills).

Content is read from a positional argument or stdin (pipe / heredoc).

Usage:
  # From argument
  python dashboard/utils/ai_event.py --phase thinking "Analysing broken locators..."

  # From heredoc (multi-line)
  python dashboard/utils/ai_event.py --phase prompt << 'EOF'
  Broken locators: ...
  PR diff: ...
  EOF

  # With metadata
  python dashboard/utils/ai_event.py --phase response --tokens 312 --elapsed-ms 1840 "Healed selectors: ..."
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import os
from datetime import datetime

DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://localhost:8765")


def post(phase: str, content: str, stage: str, model: str,
         tokens: int | None, elapsed_ms: int | None) -> bool:
    payload = {
        "type":      "ai_activity",
        "timestamp": datetime.utcnow().isoformat(),
        "stage":     stage,
        "message":   "",
        "data": {
            "phase":      phase,
            "content":    content,
            "model":      model,
            **({"tokens":     tokens}     if tokens     is not None else {}),
            **({"elapsed_ms": elapsed_ms} if elapsed_ms is not None else {}),
        },
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{DASHBOARD_URL}/event",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5):
            return True
    except (urllib.error.URLError, OSError):
        return False


def main():
    p = argparse.ArgumentParser(description="Post an ai_activity event to the dashboard")
    p.add_argument("--phase", required=True,
                   choices=["prompt", "thinking", "response", "patch", "tool_call"],
                   help="Activity phase")
    p.add_argument("--stage", default="apply_heal",
                   help="Stage ID (default: apply_heal)")
    p.add_argument("--model", default="claude-sonnet-4-6",
                   help="Model name shown in ClaudePane")
    p.add_argument("--tokens", type=int, default=None,
                   help="Token count to display")
    p.add_argument("--elapsed-ms", type=int, default=None,
                   help="Elapsed time in ms to display")
    p.add_argument("content", nargs="?", default=None,
                   help="Content string. Omit to read from stdin.")
    args = p.parse_args()

    content = args.content if args.content is not None else sys.stdin.read().rstrip("\n")
    if not content:
        print("[ai_event] Warning: empty content — skipping", file=sys.stderr)
        sys.exit(0)

    ok = post(args.phase, content, args.stage, args.model, args.tokens, args.elapsed_ms)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
