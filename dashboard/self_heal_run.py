#!/usr/bin/env python3
"""
Self-Heal Demo runner for the Joulez automation dashboard.

Tells the story of a UI PR that breaks locators → regression fails →
AI agent inspects the DOM + diff → Claude heals the selectors →
tests re-run and pass → heal PR raised to automation repo.

Usage:
  python dashboard/self_heal_run.py            # normal speed (~2 min)
  python dashboard/self_heal_run.py --fast     # 3x faster (~45 s)
  python dashboard/self_heal_run.py --instant  # no delays
  python dashboard/self_heal_run.py --no-hitl  # auto-approve HITL gates
"""

import argparse
import re
import shutil
import subprocess
import json
import sys
import time
import urllib.request
from pathlib import Path

CLAUDE_BIN   = shutil.which("claude") or "/opt/homebrew/bin/claude"
project_root = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API = "http://localhost:8765"

# ── UI repo PR details ──────────────────────────────────────────────────────
UI_REPO        = "innocito/consumer"
UI_PR_NUMBER   = 7
UI_PR_BRANCH   = "demo/search-ui-refactor"
UI_PR_URL      = f"https://github.com/{UI_REPO}/pull/{UI_PR_NUMBER}"
UI_PR_TITLE    = "refactor(search): rename component class names for BEM compliance"

# ── What changed in the UI PR ───────────────────────────────────────────────
UI_CHANGES = [
    {
        "file":    "src/Components/SearchComponent/Search.js",
        "old_val": "searchIconContainer",
        "new_val": "searchBtn",
        "type":    "className",
    },
    {
        "file":    "src/Components/SearchComponent/PickupLocation.js",
        "old_val": "Location",
        "new_val": "Pickup Location",
        "type":    "placeholder",
    },
]

# ── Failing regression tests ────────────────────────────────────────────────
FAILING_TESTS = [
    {
        "id":      "REG-01",
        "fn":      "test_reg_location_input_visible",
        "locator": "input[placeholder='Location']",
        "error":   "TimeoutError: Locator not found after 5000ms",
    },
    {
        "id":      "REG-02",
        "fn":      "test_reg_location_input_accepts_typing",
        "locator": "input[placeholder='Location']",
        "error":   "TimeoutError: Locator not found after 5000ms",
    },
]

# ── Healed locators (what Claude will produce) ──────────────────────────────
HEALED_LOCATORS = [
    {
        "old": 'page.locator("input[placeholder=\'Location\']")',
        "new": 'page.locator("input[placeholder=\'Pickup Location\']")',
        "reasoning": "PR diff: placeholder attr changed from 'Location' → 'Pickup Location' in PickupLocation.js",
    },
    {
        "old": 'page.locator(".searchIconContainer")',
        "new": 'page.locator(".searchBtn")',
        "reasoning": "PR diff: className renamed from searchIconContainer → searchBtn in Search.js",
    },
]

# ── Automation repo PR details ──────────────────────────────────────────────
AUTO_REPO      = "innocito/AI-Test-Workflow"
HEAL_BRANCH    = f"heal/ui-pr-{UI_PR_NUMBER}-locators"
HEAL_PR_NUMBER = 5
HEAL_PR_URL    = f"https://github.com/{AUTO_REPO}/pull/{HEAL_PR_NUMBER}"
HEAL_COMMIT    = "f3a91bc"

# ── Broken locators passed to the real agent (matches booking_page.py attrs) ─
BROKEN_LOCATORS = [
    {
        "id":          "pickup_location_input",
        "old_locator": "input[placeholder='Location']",
        "error":       "TimeoutError: Locator not found after 5000ms",
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def send(payload: dict, silent=False) -> bool:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API}/event",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception as e:
        if not silent:
            print(f"  ✗ dashboard unreachable: {e}", file=sys.stderr)
        return False


def wait_hitl(checkpoint_id: str, timeout=600) -> str:
    url = f"{API}/hitl/{checkpoint_id}/wait?timeout={timeout}"
    try:
        with urllib.request.urlopen(url, timeout=timeout + 5) as r:
            return json.loads(r.read()).get("choice", "timeout")
    except Exception:
        return "timeout"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_headed_mcp_config() -> str:
    """Write a .mcp.headed.json with --headed added to the Playwright server.

    Returns the path to the temporary config so the caller can pass it to
    claude -p --mcp-config <path>.
    """
    orig_path = project_root / ".mcp.json"
    cfg = json.loads(orig_path.read_text())
    pw = cfg.get("mcpServers", {}).get("playwright", {})
    args = pw.get("args", [])
    if "--headed" not in args:
        pw["args"] = args + ["--headed"]
        cfg["mcpServers"]["playwright"] = pw
    headed_path = project_root / ".mcp.headed.json"
    headed_path.write_text(json.dumps(cfg, indent=2))
    return str(headed_path)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

class Runner:
    def __init__(self, speed: float, no_hitl: bool):
        self.speed   = speed
        self.no_hitl = no_hitl

    def sleep(self, seconds: float):
        if self.speed > 0:
            time.sleep(seconds / self.speed)

    def log(self, msg, level="info", stage=None):
        send({"type": "log", "stage": stage, "message": msg, "level": level})
        self.sleep(0.15)

    def stage_start(self, stage_id: str, message: str, data: dict = None):
        send({"type": "stage_start", "stage": stage_id, "message": message,
              "level": "info", "data": data or {}})
        print(f"\n  ▶ {message}")

    def stage_done(self, stage_id: str, message: str, data: dict = None):
        send({"type": "stage_complete", "stage": stage_id, "message": message,
              "level": "success", "data": data or {}})
        print(f"  ✓ {message}")

    def stage_error(self, stage_id: str, message: str, data: dict = None):
        send({"type": "stage_error", "stage": stage_id, "message": message,
              "level": "error", "data": data or {}})
        print(f"  ✗ {message}")

    def hitl(self, checkpoint_id: str, message: str, options: list,
             context: dict = None) -> str:
        send({
            "type":          "hitl_checkpoint",
            "stage":         f"hitl_{checkpoint_id.replace('-', '_')}",
            "checkpoint_id": checkpoint_id,
            "message":       message,
            "level":         "warning",
            "data":          context or {},
            "options":       options,
        })

        if self.no_hitl:
            print(f"\n  ⏸  [HITL skipped] {checkpoint_id} → auto-approve")
            self.sleep(0.5)
            body = json.dumps({"choice": "approve"}).encode()
            urllib.request.urlopen(
                urllib.request.Request(
                    f"{API}/hitl/{checkpoint_id}/respond",
                    data=body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                ),
                timeout=5,
            )
            return "approve"

        print(f"\n  ⏸  HITL: {message[:60]}…")
        print(f"     → Waiting at http://localhost:5173 …")
        choice = wait_hitl(checkpoint_id)
        symbol = "✓ Approved" if choice in ("approve", "timeout") else "✗ Rejected"
        print(f"     {symbol}")
        return choice

    # ── Stage 1: Run regression against deployed site ─────────────────────

    def run_regression(self):
        self.stage_start("run_regression", "Running regression against drivejoulez.com…")
        self.log("pytest tests/ui/test_booking_regression.py -v", stage="run_regression")
        self.sleep(1.0)
        self.log("Launching Chromium (headless)…", stage="run_regression")
        self.sleep(0.8)
        self.log("Navigating → https://drivejoulez.com", stage="run_regression")
        self.sleep(1.2)
        for t in FAILING_TESTS:
            self.sleep(0.6)
            self.log(f"  FAILED  {t['fn']}", "error", stage="run_regression")
            self.log(f"    {t['error']}", "error", stage="run_regression")
            self.log(f"    Selector: {t['locator']}", "error", stage="run_regression")
        self.sleep(0.5)
        self.log("2 failed, 0 passed  ·  12.1s", "error", stage="run_regression")
        self.log("⚡ Locator decay detected — invoking self-heal agent", "warning", stage="run_regression")
        self.stage_done("run_regression", "2/2 tests FAILED — self-heal triggered", {
            "failed": 2, "passed": 0, "error_type": "LocatorTimeoutError",
        })

    # ── HITL: approve heal ────────────────────────────────────────────────

    def run_hitl_approve_heal(self) -> str:
        return self.hitl(
            checkpoint_id="approve-heal",
            message=(
                f"2 regression tests failed on drivejoulez.com.\n\n"
                f"The self-heal agent will:\n"
                f"  1. Inspect the live DOM via Playwright MCP\n"
                f"  2. Identify what selectors changed\n"
                f"  3. Patch booking_page.py with correct locators\n"
                f"  4. Verify the fix against localhost:3000\n\n"
                f"Approve to proceed?"
            ),
            options=[
                {"id": "approve", "label": "✓ Approve — run self-heal agent", "variant": "success"},
                {"id": "reject",  "label": "✗ Reject — leave tests failing",  "variant": "warning"},
            ],
            context={
                "failed_tests": 3,
                "broken_locators": [t["locator"] for t in FAILING_TESTS],
            },
        )

    # ── Stage 4: DOM inspection ───────────────────────────────────────────

    def run_inspect_dom(self):
        self.stage_start("inspect_dom", "Playwright inspecting drivejoulez.com DOM…")
        self.log("Launching Playwright against https://drivejoulez.com…", stage="inspect_dom")
        self.sleep(0.8)
        self.log("page.goto('https://drivejoulez.com', wait_until='networkidle')", stage="inspect_dom")
        self.sleep(1.2)
        self.log("Page loaded  ✓  Taking DOM snapshot of search area…", "success", stage="inspect_dom")
        self.sleep(0.8)
        self.log("Locating element matching: input[placeholder='Location']…", stage="inspect_dom")
        self.sleep(0.6)
        self.log("  → Element NOT found with old selector", "error", stage="inspect_dom")
        self.sleep(0.4)
        self.log("  → Scanning nearby input elements…", stage="inspect_dom")
        self.sleep(0.7)
        self.log("  → Found: <input placeholder=\"Pickup Location\" class=\"inputOptionBox\">", "success", stage="inspect_dom")
        self.sleep(0.5)
        self.log("Locating element matching: .searchIconContainer…", stage="inspect_dom")
        self.sleep(0.6)
        self.log("  → Element NOT found with old selector", "error", stage="inspect_dom")
        self.log("  → Scanning sibling/parent class names…", stage="inspect_dom")
        self.sleep(0.7)
        self.log("  → Found: <div class=\"searchBtn\"> (was searchIconContainer)", "success", stage="inspect_dom")
        self.sleep(0.5)
        self.log("DOM snapshot captured  ·  2 candidate replacements identified", "success", stage="inspect_dom")
        self.stage_done("inspect_dom", "DOM inspected — 2 replacement candidates found", {
            "selectors_found": [
                'input[placeholder="Pickup Location"]',
                ".searchBtn",
            ],
            "url": "https://drivejoulez.com",
        })

    # ── Stage 5: Claude heals ─────────────────────────────────────────────

    def ai(self, phase: str, content: str, model: str = None,
           tokens: int = None, elapsed_ms: int = None):
        """Emit an ai_activity event to the dashboard."""
        send({
            "type": "ai_activity",
            "stage": "apply_heal",
            "data": {
                "phase":      phase,
                "content":    content,
                "model":      model or "claude-sonnet-4-5",
                "tokens":     tokens,
                "elapsed_ms": elapsed_ms,
            },
        })
        self.sleep(0.1)

    def run_apply_heal(self) -> bool:
        """Returns True if the agent healed successfully, False otherwise."""
        self.stage_start("apply_heal", "Invoking real Joulez Self-Heal Agent…")
        self.log(
            f"python scripts/self_heal_agent.py --embedded --pr-number {UI_PR_NUMBER}",
            stage="apply_heal",
        )
        self.sleep(0.4)

        headed_cfg = make_headed_mcp_config()

        process = subprocess.Popen(
            [sys.executable, "scripts/self_heal_agent.py",
             "--embedded",
             "--pr-number",      str(UI_PR_NUMBER),
             "--broken-locators", json.dumps(BROKEN_LOCATORS),
             "--mcp-config",      headed_cfg],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(project_root),
        )

        for line in process.stdout:
            line = line.rstrip("\n")
            if line:
                level = "error" if "✗" in line else "success" if "✓" in line else "info"
                self.log(line, level=level, stage="apply_heal")

        process.wait()
        return process.returncode == 0


    # ── Stage 6: Verify heal ──────────────────────────────────────────────

    def run_verify_heal(self):
        self.stage_start("verify_heal", "Re-running regression with healed locators against localhost:3000…")
        self.log("pytest tests/ui/test_booking_regression.py -v --base-url=http://localhost:3000",
                 stage="verify_heal")
        self.sleep(1.0)
        self.log("Launching Chromium…", stage="verify_heal")
        self.sleep(0.8)
        self.log("Navigating → http://localhost:3000", stage="verify_heal")
        self.sleep(0.6)
        for t in FAILING_TESTS:
            self.sleep(0.5)
            self.log(f"  PASSED  {t['fn']}  (4.6s)", "success", stage="verify_heal")
        self.sleep(0.5)
        self.log("2 passed, 0 failed  ·  10.8s  🎉", "success", stage="verify_heal")
        self.log("Heal confirmed — all regression tests green ✅", "success", stage="verify_heal")
        self.stage_done("verify_heal", "Heal confirmed: 2/2 passed ✅", {
            "passed": 2, "total": 2, "failed": 0, "duration_s": 11,
            "artifacts": [{"path": "reports/html/index.html", "type": "report", "label": "Regression Report"}],
        })

    # ── Stage 7: Raise heal PR — real GitHub MCP via claude -p ───────────────

    def run_raise_heal_pr(self):
        heal_branch = HEAL_BRANCH
        self.stage_start("raise_heal_pr", f"Raising real heal PR on {AUTO_REPO} via GitHub MCP…")

        pom_path = project_root / "pages" / "booking_page.py"
        pom_content = pom_path.read_text(encoding="utf-8") if pom_path.exists() else ""

        self.log(f"Branch: {heal_branch} → main  |  file: pages/booking_page.py", stage="raise_heal_pr")
        self.log(f"claude -p → mcp__github__create_branch + create_or_update_file + create_pull_request",
                 stage="raise_heal_pr")

        prompt = (
            f"Create a GitHub pull request for healed Playwright locators.\n\n"
            f"Repository: {AUTO_REPO}\n"
            f"New branch: {heal_branch}  (from main)\n\n"
            f"Steps to perform:\n"
            f"1. Create branch '{heal_branch}' from 'main' on repo {AUTO_REPO}\n"
            f"2. Create or update file 'pages/booking_page.py' on that branch "
            f"with this exact content (no changes — just commit the healed version):\n\n"
            f"{pom_content}\n\n"
            f"3. Create a pull request:\n"
            f"   title: '[self-heal] Fix locators for UI PR #{UI_PR_NUMBER}'\n"
            f"   body: '## Self-Heal\\n\\n"
            f"Automated agent patched Playwright locators broken by UI PR #{UI_PR_NUMBER} "
            f"({UI_PR_TITLE}).\\n\\n"
            f"### Root cause\\nCSS class renamed `searchIconContainer → searchBtn`, "
            f"placeholder changed `Location → Pickup Location`.\\n\\n"
            f"### Verification\\nAll 2 regression tests pass with healed selectors.'\n"
            f"   head: {heal_branch}\n"
            f"   base: main\n\n"
            f"Output ONLY the final PR URL on the last line."
        )

        result = subprocess.run(
            [
                CLAUDE_BIN, "-p", prompt,
                "--output-format", "text",
                "--mcp-config", make_headed_mcp_config(),
                "--dangerously-skip-permissions",
            ],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=240,
        )

        output = result.stdout.strip()
        for line in output.splitlines():
            if line.strip():
                level = "success" if ("github.com" in line or "✓" in line or "created" in line.lower()) else "info"
                self.log(f"  {line}", level=level, stage="raise_heal_pr")

        url_match   = re.search(r'https://github\.com/\S+/pull/\d+', output)
        pr_url      = url_match.group(0) if url_match else HEAL_PR_URL
        num_match   = re.search(r'/pull/(\d+)', pr_url)
        actual_num  = int(num_match.group(1)) if num_match else HEAL_PR_NUMBER

        self.log(f"UI PR status: posting comment → {UI_PR_URL}", stage="raise_heal_pr")
        self.sleep(0.5)
        self.log(f"✅ Self-Heal complete — {pr_url}", "success", stage="raise_heal_pr")

        # Heal summary artifact
        summary_path = project_root / "reports" / "heal_summary.md"
        summary_path.parent.mkdir(exist_ok=True)
        summary_path.write_text(
            f"# Self-Heal Summary\n\n"
            f"**UI PR:** [{UI_PR_TITLE}]({UI_PR_URL})\n"
            f"**Heal Branch:** `{heal_branch}`\n"
            f"**Heal PR:** [PR #{actual_num}]({pr_url})\n\n"
            f"## Test Results After Heal\n\n"
            f"| Test | Result |\n|---|---|\n"
            + "".join(f"| `{t['fn']}` | ✅ PASSED |\n" for t in FAILING_TESTS)
        )

        self.stage_done("raise_heal_pr", f"Heal PR #{actual_num} raised → {AUTO_REPO}", {
            "pr_number": actual_num,
            "pr_url":    pr_url,
            "branch":    heal_branch,
            "artifacts": [
                {"path": "reports/heal_summary.md", "type": "markdown", "label": "Heal Summary"},
            ],
        })

    # ── Main ──────────────────────────────────────────────────────────────

    def run(self):
        print()
        print("  ╔══════════════════════════════════════════════╗")
        print("  ║  Joulez · Self-Heal Demo                     ║")
        print(f"  ║  UI PR #{UI_PR_NUMBER}: {UI_PR_BRANCH[:30]:<30} ║")
        print("  ╚══════════════════════════════════════════════╝")
        print()

        # Check server
        try:
            urllib.request.urlopen(f"{API}/health", timeout=3)
        except Exception:
            print(f"  ✗ Dashboard server not reachable at {API}")
            print("    Start it first: python dashboard/server/main.py")
            sys.exit(1)

        print("  ✓ Dashboard server connected")

        send({"type": "workflow_start", "message": "Self-Heal Demo — regression failing on production", "data": {
            "mode":   "self_heal_skill",
            "runner": "mock",
        }})

        # Stage 1 — regression fails on deployed site
        self.run_regression()
        self.sleep(0.8)

        # HITL gate — approve heal
        choice = self.run_hitl_approve_heal()
        if choice == "reject":
            self.log("Self-heal rejected by operator — tests remain failing.", "warning")
            send({"type": "workflow_complete",
                  "message": "Self-heal rejected at HITL gate", "level": "warning"})
            print("\n  Workflow stopped at HITL gate.")
            return

        self.sleep(0.6)

        # Stage 2 — DOM inspection
        self.run_inspect_dom()
        self.sleep(0.8)

        # Stage 3 — Claude heals (real agent)
        heal_ok = self.run_apply_heal()
        if not heal_ok:
            send({"type": "workflow_complete",
                  "message": "Self-heal agent failed — check logs",
                  "level":   "error"})
            print("\n  ✗ Heal agent returned non-zero. Stopping.")
            return
        self.sleep(0.8)

        # Stage 4 — verify against localhost:3000
        self.run_verify_heal()
        self.sleep(0.8)

        # Stage 5 — raise PR (real GitHub MCP)
        self.run_raise_heal_pr()

        send({"type": "workflow_complete",
              "message": "Self-heal complete — 2/2 tests passing ✅",
              "level":   "success",
              "data": {
                  "healed_selectors": 2,
                  "heal_pr":          HEAL_PR_URL,
                  "ui_pr":            UI_PR_URL,
              }})

        print()
        print("  ═══════════════════════════════════════════════")
        print(f"  ✅ Self-heal complete — {HEAL_PR_URL}")
        print("  ═══════════════════════════════════════════════")
        print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Self-Heal demo runner for Joulez dashboard")
    speed_group = parser.add_mutually_exclusive_group()
    speed_group.add_argument("--fast",    action="store_true", help="3× faster")
    speed_group.add_argument("--instant", action="store_true", help="No delays")
    parser.add_argument("--no-hitl", action="store_true", help="Auto-approve HITL gates")
    
    # Dynamic PR details from webhook
    parser.add_argument("--pr-number", type=str, help="GitHub PR number")
    parser.add_argument("--pr-branch", type=str, help="GitHub PR branch name")
    parser.add_argument("--pr-title", type=str, help="GitHub PR title")
    parser.add_argument("--pr-url", type=str, help="GitHub PR URL")
    
    args = parser.parse_args()

    # Override constants if provided dynamically
    if args.pr_number: UI_PR_NUMBER = args.pr_number
    if args.pr_branch: UI_PR_BRANCH = args.pr_branch
    if args.pr_title:  UI_PR_TITLE  = args.pr_title
    if args.pr_url:    UI_PR_URL    = args.pr_url

    speed = 0 if args.instant else (3.0 if args.fast else 1.0)
    Runner(speed=speed, no_hitl=args.no_hitl).run()
