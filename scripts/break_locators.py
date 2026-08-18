#!/usr/bin/env python3
"""
Locator decay simulator for the self-heal demo.

Targets two locators in pages/task_list_page.js that are exercised by
tests/ui/task-list-regression.spec.js.  Supports break and restore.

Usage:
  python scripts/break_locators.py --break-locators
  python scripts/break_locators.py --restore
"""
import argparse
import os
import sys

PAGE_FILE = os.path.join("pages", "task_list_page.js")

# ── Locator pairs: (real, broken) ──────────────────────────────────────────
LOCATORS = [
    (
        'page.locator(".arw-grid-table__row")',
        'page.locator(".arw-broken-grid-table__row")',
    ),
    (
        'page.locator(".arw-grid-table__cell")',
        'page.locator(".arw-broken-grid-table__cell")',
    ),
]


def _read() -> str:
    if not os.path.exists(PAGE_FILE):
        print(f"[break_locators] ERROR: {PAGE_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    with open(PAGE_FILE, encoding="utf-8") as f:
        return f.read()


def _write(content: str) -> None:
    with open(PAGE_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def break_locators() -> None:
    content = _read()
    changed = 0
    for real, broken in LOCATORS:
        if real in content:
            content = content.replace(real, broken, 1)
            changed += 1
            print(f"[break_locators] ✗ Broken: {real.split('(')[1][:40]}…")
        elif broken in content:
            print(f"[break_locators] Already broken, skipping.")
        else:
            print(f"[break_locators] WARNING: locator not matched — {real[:60]}", file=sys.stderr)
    _write(content)
    print(f"[break_locators] {changed} locator(s) broken in {PAGE_FILE}")


def restore_locators() -> None:
    content = _read()
    changed = 0
    for real, broken in LOCATORS:
        if broken in content:
            content = content.replace(broken, real, 1)
            changed += 1
            print(f"[break_locators] ✓ Healed: {real.split('(')[1][:40]}…")
        elif real in content:
            print(f"[break_locators] Already restored, skipping.")
        else:
            print(f"[break_locators] WARNING: locator not matched — {broken[:60]}", file=sys.stderr)
    _write(content)
    print(f"[break_locators] ✓ {changed} locator(s) restored in {PAGE_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate locator decay for the self-heal demo.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--break-locators", action="store_true", help="Inject broken selectors")
    group.add_argument("--restore", action="store_true", help="Restore from backup")
    args = parser.parse_args()

    if args.break_locators:
        break_locators()
    else:
        restore_locators()
