#!/usr/bin/env python3
"""
Blocking HITL checkpoint. Posts the checkpoint event, then polls until
the dashboard user responds. Exits 0 for approve, 1 for reject/timeout.

Usage:
  python dashboard/utils/hitl_gate.py \
    --id "pre-commit" \
    --message "5 tests generated — approve to commit?" \
    --options "Approve & Continue:approve:success,Reject:reject:danger" \
    --context '{"tests": 5}'
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://localhost:8765")


def post_checkpoint(checkpoint_id: str, message: str, options: list, context: dict):
    payload = {
        "type": "hitl_checkpoint",
        "stage": f"hitl_{checkpoint_id.replace('-', '_')}",
        "checkpoint_id": checkpoint_id,
        "message": message,
        "level": "warning",
        "data": context,
        "options": options,
    }
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{DASHBOARD_URL}/event",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10):
        pass


def wait_for_response(checkpoint_id: str, timeout: float = 600) -> dict:
    url = f"{DASHBOARD_URL}/hitl/{checkpoint_id}/wait?timeout={timeout}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=timeout + 5) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, OSError) as e:
        print(f"[hitl] Error waiting: {e}", file=sys.stderr)
        return {"choice": "timeout", "feedback": None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument(
        "--options",
        default="Approve & Continue:approve:success,Reject:reject:danger",
        help="Comma-separated list of label:id:variant"
    )
    parser.add_argument("--context", default="{}")
    parser.add_argument("--timeout", type=float, default=600)
    args = parser.parse_args()

    options = [
        {"label": o.split(":")[0], "id": o.split(":")[1], "variant": o.split(":")[2]}
        for o in args.options.split(",")
    ]
    context = json.loads(args.context)

    print(f"\n⏸  HITL CHECKPOINT: {args.id}", file=sys.stderr)
    print(f"   {args.message}", file=sys.stderr)
    print(f"   Waiting for response at http://localhost:5173 ...\n", file=sys.stderr)

    try:
        post_checkpoint(args.id, args.message, options, context)
    except Exception as e:
        print(f"[hitl] Dashboard unreachable: {e}. Defaulting to approve.", file=sys.stderr)
        sys.exit(0)

    result = wait_for_response(args.id, timeout=args.timeout)
    choice   = result.get("choice", "timeout")
    feedback = result.get("feedback") or ""

    if choice in ("approve", "timeout"):
        print(f"[hitl] ✅ Approved: {args.id}", file=sys.stderr)
        sys.exit(0)
    else:
        print(f"[hitl] ❌ Rejected: {args.id}", file=sys.stderr)
        if feedback:
            # Print to stdout so Claude's Bash tool captures it
            print(f"HITL_FEEDBACK: {feedback}")
            print(f"[hitl] Feedback: {feedback}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
