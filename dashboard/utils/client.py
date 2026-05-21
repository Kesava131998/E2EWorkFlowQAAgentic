#!/usr/bin/env python3
"""
Thin client for sending events to the dashboard server.

Usage (CLI):
  python dashboard/utils/client.py event --type stage_start --stage jira_fetch --message "Fetching JP-1..."
  python dashboard/utils/client.py event --type stage_complete --stage jira_fetch --message "JP-1 fetched" --data '{"ticket":"JP-1","summary":"..."}'

Usage (Python import):
  from dashboard.utils.client import send_event
  send_event("stage_complete", stage="jira_fetch", message="Done", data={"ticket": "JP-1"})
"""

import argparse
import json
import os
import urllib.request
import urllib.error
from datetime import datetime

DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://localhost:8765")


def send_event(
    event_type: str,
    stage: str | None = None,
    message: str = "",
    level: str = "info",
    data: dict | None = None,
    checkpoint_id: str | None = None,
    options: list | None = None,
    silent: bool = False,
) -> bool:
    payload = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "stage": stage,
        "message": message,
        "level": level,
        "data": data or {},
        "checkpoint_id": checkpoint_id,
        "options": options,
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
    except (urllib.error.URLError, OSError) as e:
        if not silent:
            print(f"[dashboard] Could not reach server: {e}")
        return False


def check_server() -> bool:
    """Returns True if the dashboard server is reachable."""
    try:
        with urllib.request.urlopen(f"{DASHBOARD_URL}/health", timeout=3):
            return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    ev = sub.add_parser("event")
    ev.add_argument("--type", required=True)
    ev.add_argument("--stage")
    ev.add_argument("--message", default="")
    ev.add_argument("--level", default="info")
    ev.add_argument("--data", default="{}")

    sub.add_parser("check")   # exits 0 if server up, 1 if down

    args = parser.parse_args()

    if args.cmd == "event":
        ok = send_event(args.type, stage=args.stage, message=args.message, level=args.level, data=json.loads(args.data))
        raise SystemExit(0 if ok else 1)

    if args.cmd == "check":
        if check_server():
            print("✓ Dashboard server is running at", DASHBOARD_URL)
            raise SystemExit(0)
        else:
            print("✗ Dashboard server is NOT running at", DASHBOARD_URL)
            print("  Start it first:  cd dashboard && ./start.sh")
            raise SystemExit(1)


if __name__ == "__main__":
    main()
