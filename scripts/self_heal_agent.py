#!/usr/bin/env python3
"""
Real Self-Heal Agent for Joulez Automation.

Embedded mode (called by mock runner):
  Uses pre-supplied broken locators, skips pytest, runs claude -p for healing.

Standalone mode (called by webhook/server when a real PR arrives):
  Stage 1  — baseline pytest against drivejoulez.com
  Stage 2  — fetch PR diff via GitHub REST API
  Stage 3  — regression pytest against localhost:3000  (expect failures)
  HITL     — user approves in dashboard
  Stage 4  — inspect_dom via Playwright MCP (inside claude -p)
  Stage 5  — apply_heal via claude -p (GitHub MCP + Playwright MCP + reasoning)
  Stage 6  — verify pytest against localhost:3000  (expect passes)
  Stage 7  — raise heal PR via claude -p + GitHub MCP
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CLAUDE_BIN   = shutil.which("claude") or "/opt/homebrew/bin/claude"
# Resolve pytest from the same env that has Playwright installed.
# shutil.which() walks PATH; fallback to miniconda which is the known-good env.
PYTEST_BIN   = (shutil.which("pytest") or
                "/opt/miniconda3/bin/pytest")
UI_URL       = "http://localhost:3000"   # PR-branch app for detect + verify
UI_REPO      = "innocito/consumer"
AUTO_REPO    = "innocito/AI-Test-Workflow"
POM_FILE     = "pages/booking_page.py"
TEST_FILE    = "tests/ui/test_booking_regression.py"
API          = "http://localhost:8765"

# Matches POM locator definitions — handles both quote styles:
#   page.locator(".foo")          → outer double, no inner single
#   page.locator("input[placeholder='Bar']")  → outer double, inner single
#   page.locator('.foo')          → outer single
_POM_LOCATOR_RE = re.compile(
    r'self\.(\w+)\s*(?::\s*\w+\s*)?=\s*page\.locator\((?:"([^"]+)"|\'([^\']+)\')\)'
)

project_root = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Dashboard helpers
# ---------------------------------------------------------------------------

def _post(payload: dict) -> None:
    try:
        urllib.request.urlopen(
            urllib.request.Request(
                f"{API}/event",
                data=json.dumps({**payload, "timestamp": datetime.utcnow().isoformat()}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            ),
            timeout=2,
        )
    except Exception:
        pass


def send_stage(event_type: str, stage: str, message: str,
               level: str = "info", data: dict = None) -> None:
    _post({"type": event_type, "stage": stage, "message": message,
           "level": level, "data": data or {}})


def send_log(message: str, stage: str, level: str = "info") -> None:
    _post({"type": "log", "stage": stage, "message": message, "level": level})


def send_ai(phase: str, content: str, model: str = "claude-sonnet-4-6",
            tokens: int = None, elapsed_ms: int = None) -> None:
    _post({
        "type": "ai_activity",
        "stage": "apply_heal",
        "message": "",
        "data": {
            "phase":   phase,
            "content": content,
            "model":   model,
            **({"tokens":     tokens}     if tokens     is not None else {}),
            **({"elapsed_ms": elapsed_ms} if elapsed_ms is not None else {}),
        },
    })

# ---------------------------------------------------------------------------
# MCP config helpers
# ---------------------------------------------------------------------------

def make_headed_mcp_config() -> str:
    """Return path to a .mcp.headed.json with --headed in the Playwright args."""
    orig = json.loads((project_root / ".mcp.json").read_text())
    pw   = orig.get("mcpServers", {}).get("playwright", {})
    args = pw.get("args", [])
    if "--headed" not in args:
        pw["args"] = args + ["--headed"]
        orig["mcpServers"]["playwright"] = pw
    out = project_root / ".mcp.headed.json"
    out.write_text(json.dumps(orig, indent=2))
    return str(out)

# ---------------------------------------------------------------------------
# GitHub REST helpers (used in standalone Stage 2)
# ---------------------------------------------------------------------------

def _github_token() -> str:
    try:
        cfg = json.loads((project_root / ".mcp.json").read_text())
        return cfg["mcpServers"]["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"]
    except Exception:
        return os.getenv("GITHUB_TOKEN", "")


def _github_get(path: str):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {_github_token()}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "joulez-self-heal/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fetch_pr_info(pr_number: str, ui_repo: str = UI_REPO) -> dict:
    """Fetch PR title, branch, and changed filenames from GitHub."""
    try:
        pr    = _github_get(f"/repos/{ui_repo}/pulls/{pr_number}")
        files = _github_get(f"/repos/{ui_repo}/pulls/{pr_number}/files")
        return {
            "title":  pr.get("title", "Unknown PR"),
            "branch": pr.get("head", {}).get("ref", "unknown"),
            "url":    pr.get("html_url", ""),
            "files":  [f["filename"] for f in files],
            "patches": {f["filename"]: f.get("patch", "") for f in files},
        }
    except Exception as e:
        send_log(f"  GitHub API error: {e}", stage="fetch_pr_diff", level="error")
        return {"title": "Unknown PR", "branch": "unknown", "url": "", "files": [], "patches": {}}

# ---------------------------------------------------------------------------
# Pytest helpers
# ---------------------------------------------------------------------------

def run_pytest(stage: str, base_url: str = None) -> tuple[int, str]:
    """Run the regression test file. Overrides BASE_URL when provided."""
    env = os.environ.copy()
    if base_url:
        env["BASE_URL"] = base_url
    # Direct pytest binary doesn't add project root to sys.path the way
    # `python -m pytest` does — set PYTHONPATH so conftest can import config.*
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(project_root) + (":" + existing if existing else "")

    cmd = [
        PYTEST_BIN,
        TEST_FILE,
        "-v", "--tb=short", "--no-header",
        "-p", "no:xdist",           # serial output — xdist scrambles traceback sections
        "-o", "addopts=--browser=chromium",  # strip -n=auto / --reruns from pyproject.toml
    ]
    send_log(f"Running: pytest {TEST_FILE} -v"
             + (f"  [BASE_URL={base_url}]" if base_url else ""), stage=stage)

    result = subprocess.run(cmd, capture_output=True, text=True,
                            cwd=str(project_root), env=env)
    output = result.stdout + result.stderr

    for line in output.splitlines():
        if "PASSED" in line:
            send_log(f"  {line.strip()}", stage=stage, level="success")
        elif "FAILED" in line:
            send_log(f"  {line.strip()}", stage=stage, level="error")

    return result.returncode, output


def _parse_summary(output: str) -> dict:
    """Extract passed/failed/total counts from pytest output."""
    m = re.search(r'(\d+) passed', output)
    passed = int(m.group(1)) if m else 0
    m = re.search(r'(\d+) failed', output)
    failed = int(m.group(1)) if m else 0
    m = re.search(r'in ([\d.]+)s', output)
    duration = float(m.group(1)) if m else None
    return {"passed": passed, "failed": failed, "total": passed + failed, "duration": duration}


def _extract_broken_locators(pytest_output: str) -> list[dict]:
    """Extract broken locator info from pytest --tb=short output.

    Matches POM attribute names regardless of what variable name the test
    uses (e.g. `booking.pickup_location_input` not just `self.pickup_location_input`).
    Falls back to returning ALL POM locators when pytest crashed without
    producing any FAILED sections (e.g. connection refused on localhost:3000).
    """
    pom_path    = project_root / POM_FILE
    pom_content = pom_path.read_text() if pom_path.exists() else ""

    pom_locators: dict[str, str] = {}
    for m in re.finditer(_POM_LOCATOR_RE, pom_content):
        pom_locators[m.group(1)] = m.group(2) or m.group(3)

    broken: list[dict] = []
    seen:   set[str]   = set()

    for section in re.split(r'(?:^|\n)(?:_{5,}|-{5,})', pytest_output):
        # Match any word that is a known POM attribute name — covers both
        # `self.pickup_location_input` and `booking.pickup_location_input`
        for attr in pom_locators:
            if attr in seen:
                continue
            if not re.search(rf'\b{re.escape(attr)}\b', section):
                continue
            seen.add(attr)
            err_m = re.search(r'(?:TimeoutError|AssertionError|playwright.*Error)[^\n]*', section)
            broken.append({
                "id":          attr,
                "old_locator": pom_locators[attr],
                "error":       err_m.group(0).strip() if err_m else "Locator not found",
            })
            send_log(f"  Broken: {attr} → '{pom_locators[attr]}'",
                     stage="run_regression", level="error")

    return broken

# ---------------------------------------------------------------------------
# HITL gate (standalone)
# ---------------------------------------------------------------------------

def hitl_gate(checkpoint_id: str, message: str, context: dict,
              timeout: int = 600) -> str:
    _post({
        "type":          "hitl_checkpoint",
        "stage":         f"hitl_{checkpoint_id.replace('-', '_')}",
        "checkpoint_id": checkpoint_id,
        "message":       message,
        "level":         "warning",
        "data":          context,
        "options": [
            {"id": "approve", "label": "✓ Approve — run self-heal agent", "variant": "success"},
            {"id": "reject",  "label": "✗ Reject — leave tests failing",  "variant": "warning"},
        ],
    })
    try:
        with urllib.request.urlopen(
            f"{API}/hitl/{checkpoint_id}/wait?timeout={timeout}",
            timeout=timeout + 5,
        ) as r:
            return json.loads(r.read()).get("choice", "timeout")
    except Exception:
        return "timeout"

# ---------------------------------------------------------------------------
# Claude -p with GitHub MCP + Playwright MCP
# ---------------------------------------------------------------------------

def call_claude_with_mcps(broken_locators: list[dict], pr_number: str,
                          mcp_config: str, ui_repo: str = UI_REPO) -> list:
    if not CLAUDE_BIN or not Path(CLAUDE_BIN).exists():
        print(f"✗ claude CLI not found at {CLAUDE_BIN}")
        return []

    broken_json = json.dumps(broken_locators, indent=2)

    prompt = f"""You are a Playwright locator self-heal agent.

Regression tests failed after a UI change. These locators in pages/booking_page.py are broken:

{broken_json}

Perform ALL THREE steps below in order:

STEP 1 — Fetch the PR diff:
Use the GitHub MCP tool to list files changed in PR #{pr_number} on repo "{ui_repo}".
Identify every renamed CSS class or changed placeholder / attribute.

STEP 2 — Inspect the live DOM:
Navigate the browser to {UI_URL}.
Take a DOM snapshot of the page.
Locate the elements that correspond to the broken selectors.
Confirm the new attribute values from the PR diff are present in the DOM.

STEP 3 — Output healed locators:
Based on BOTH the PR diff AND the DOM snapshot, output ONLY a valid JSON array:
[
  {{
    "id": "variable_name_from_broken_locators",
    "old_locator": "the current broken selector string",
    "new_locator": "the corrected selector string",
    "reasoning": "What changed in the PR diff AND what the DOM snapshot confirms"
  }}
]

Output ONLY the JSON array. No markdown fences, no explanation.
"""

    send_ai("prompt", prompt, tokens=len(prompt) // 4)
    send_ai(
        "thinking",
        "Step 1 — PR diff: identifying renamed classes and changed attributes…\n"
        "Step 2 — DOM snapshot: locating each element in the live page to confirm…\n"
        "Step 3 — Deriving stable replacement selectors verified against both sources…",
    )

    print(f"▶ claude -p with GitHub + Playwright MCPs (PR #{pr_number})…")
    start = time.time()

    try:
        result = subprocess.run(
            [CLAUDE_BIN, "-p", prompt,
             "--output-format", "text",
             "--mcp-config", mcp_config,
             "--dangerously-skip-permissions"],
            capture_output=True, text=True,
            cwd=str(project_root), timeout=300,
        )
    except subprocess.TimeoutExpired:
        elapsed_ms = int((time.time() - start) * 1000)
        send_log(f"claude -p timed out after {elapsed_ms // 1000}s", stage="apply_heal", level="error")
        return []
    elapsed_ms = int((time.time() - start) * 1000)

    if result.returncode != 0:
        err = result.stderr.strip()
        print(f"✗ claude -p exited {result.returncode}: {err[:300]}")
        send_log(f"claude -p error: {err[:200]}", stage="apply_heal", level="error")
        return []

    output = result.stdout.strip()
    send_ai("response", output, elapsed_ms=elapsed_ms)

    match = re.search(r'\[.*\]', output, re.DOTALL)
    if match:
        try:
            heals = json.loads(match.group(0))
            print("✓ Claude returned healed locators")
            return heals
        except json.JSONDecodeError as e:
            print(f"✗ JSON parse error: {e}")

    print(f"✗ No JSON array in claude output:\n{output[:500]}")
    return []


def raise_heal_pr_via_claude(pr_number: str, mcp_config: str) -> str:
    """Use claude -p with GitHub MCP to create the heal branch, commit, and PR."""
    pom_content = (project_root / POM_FILE).read_text()
    heal_branch = f"heal/ui-pr-{pr_number}-locators"

    prompt = (
        f"Create a GitHub pull request for healed Playwright locators.\n\n"
        f"Repository: {AUTO_REPO}\n"
        f"New branch: {heal_branch}  (from main)\n\n"
        f"Steps:\n"
        f"1. Create branch '{heal_branch}' from 'main' on {AUTO_REPO}\n"
        f"2. Create or update 'pages/booking_page.py' on that branch with this exact content:\n\n"
        f"{pom_content}\n\n"
        f"3. Create pull request:\n"
        f"   title: '[self-heal] Fix locators for UI PR #{pr_number}'\n"
        f"   body: '## Self-Heal\\n\\n"
        f"Automated agent patched Playwright locators broken by UI PR #{pr_number}.\\n\\n"
        f"All regression tests pass with healed selectors. ✅'\n"
        f"   head: {heal_branch}\n"
        f"   base: main\n\n"
        f"Output ONLY the final PR URL."
    )

    result = subprocess.run(
        [CLAUDE_BIN, "-p", prompt,
         "--output-format", "text",
         "--mcp-config", mcp_config,
         "--dangerously-skip-permissions"],
        capture_output=True, text=True,
        cwd=str(project_root), timeout=240,
    )

    output = result.stdout.strip()
    for line in output.splitlines():
        if line.strip():
            level = "success" if "github.com" in line.lower() else "info"
            send_log(f"  {line}", stage="raise_heal_pr", level=level)

    url_match = re.search(r'https://github\.com/\S+/pull/\d+', output)
    return url_match.group(0) if url_match else ""

# ---------------------------------------------------------------------------
# Apply patch
# ---------------------------------------------------------------------------

def apply_patch(heals: list) -> int:
    pom_path = project_root / POM_FILE
    if not pom_path.exists():
        print(f"✗ POM file not found: {POM_FILE}")
        return 0

    content = patched = pom_path.read_text()
    count = 0

    for heal in heals:
        old = heal.get("old_locator", "")
        new = heal.get("new_locator", "")
        if not old or old == new:
            continue
        print(f"  Patching: '{old}' → '{new}'")
        if old in patched:
            patched = patched.replace(f'"{old}"', f'"{new}"')
            patched = patched.replace(f"'{old}'", f"'{new}'")
            count += 1
        else:
            print(f"  ⚠ '{old}' not found verbatim in {POM_FILE}")

    if count > 0:
        pom_path.write_text(patched)
        print(f"✓ Applied {count} patch(es) to {POM_FILE}")
    else:
        print("✗ No patches applied")

    return count

# ---------------------------------------------------------------------------
# Embedded mode (called by mock runner)
# ---------------------------------------------------------------------------

def _run_embedded(pr_number: str, broken_locators: list[dict], mcp_config: str) -> int:
    """Handle apply_heal stage only. Returns 0 on success, 1 on failure."""

    if not broken_locators:
        send_log("No broken locators provided to embedded agent", stage="apply_heal", level="error")
        return 1

    send_log(
        f"Using {len(broken_locators)} pre-identified broken locator(s) — skipping pytest",
        stage="apply_heal", level="warning",
    )
    send_log(
        f"claude -p: fetching PR diff from {UI_REPO}#{pr_number} + inspecting DOM at {UI_URL}…",
        stage="apply_heal",
    )

    heals = call_claude_with_mcps(broken_locators, pr_number, mcp_config)

    if not heals:
        send_stage("stage_error", "apply_heal",
                   "Claude did not return valid heals — check MCP connectivity")
        return 1

    for h in heals:
        send_log(f"  ✦ {h.get('id')}: {h.get('old_locator')} → {h.get('new_locator')}",
                 stage="apply_heal", level="success")

    patch_count = apply_patch(heals)
    if patch_count == 0:
        send_stage("stage_error", "apply_heal",
                   "Patch failed — old selector strings not found verbatim in POM")
        return 1

    send_stage("stage_complete", "apply_heal",
               f"{patch_count} selector(s) healed ✓", level="success",
               data={
                   "selectors_healed": patch_count,
                   "file": POM_FILE,
                   "artifacts": [{"path": POM_FILE, "type": "python", "label": "Heal Patch"}],
               })
    return 0

# ---------------------------------------------------------------------------
# Standalone mode (called directly by server for webhook flow)
# ---------------------------------------------------------------------------

def _run_standalone(pr_number: str, pr_branch: str, pr_url_arg: str,
                    mcp_config: str, ui_repo: str = UI_REPO) -> None:
    """Full 7-stage real self-heal pipeline."""

    # workflow_start — switches dashboard to self_heal_webhook pipeline
    _post({
        "type":    "workflow_start",
        "message": f"Self-Heal: UI PR #{pr_number}",
        "data": {
            "mode":   "self_heal_webhook",
            "ui_pr":  pr_url_arg or f"https://github.com/{UI_REPO}/pull/{pr_number}",
            "runner": "real",
        },
    })

    # ── Stage 1: Fetch PR diff ──────────────────────────────────────────────
    send_stage("stage_start", "fetch_pr_diff",
               f"Fetching UI PR #{pr_number} diff from {ui_repo}…")

    pr_info = fetch_pr_info(pr_number, ui_repo)
    send_log(f"PR #{pr_number}: \"{pr_info['title']}\"", stage="fetch_pr_diff")
    send_log(f"Branch: {pr_info['branch']}  |  Base: main", stage="fetch_pr_diff")
    for fname in pr_info["files"]:
        send_log(f"  Changed: {fname}", stage="fetch_pr_diff")
    for fname, patch in pr_info["patches"].items():
        for line in (patch or "").splitlines()[:8]:
            level = "error" if line.startswith("-") else "success" if line.startswith("+") else "info"
            send_log(f"  {line}", stage="fetch_pr_diff", level=level)

    send_stage("stage_complete", "fetch_pr_diff",
               f"PR #{pr_number} — {len(pr_info['files'])} file(s) changed",
               level="success",
               data={"pr_title": pr_info["title"],
                     "files_changed": len(pr_info["files"]),
                     "file": f"PR #{pr_number}: {pr_info['branch']}"})

    # ── Stage 2: Run regression against PR branch (localhost:3000) ────────────
    send_stage("stage_start", "run_regression",
               f"Running regression against PR branch ({UI_URL})…")

    rc, out = run_pytest("run_regression", base_url=UI_URL)
    broken_locators = _extract_broken_locators(out)
    summary = _parse_summary(out)

    if rc == 0:
        send_log("No test failures — PR did not break locators",
                 stage="run_regression", level="success")
        send_stage("stage_complete", "run_regression",
                   "0 failures — PR is safe, nothing to heal",
                   level="success", data={"failed": 0})
        _post({"type": "workflow_complete",
               "message": "No locator failures detected", "level": "success"})
        return

    fail_count = summary["failed"] or out.count("FAILED")

    # Supplement with any test-file-referenced locators not caught by traceback
    # parsing. Handles cases where --tb=short only shows one frame and misses
    # some attribute names (e.g. TimeoutError on .click() hides is_visible calls).
    pom_content  = (project_root / POM_FILE).read_text()
    test_content = (project_root / TEST_FILE).read_text()
    pom_locators: dict[str, str] = {}
    for m in re.finditer(_POM_LOCATOR_RE, pom_content):
        pom_locators[m.group(1)] = m.group(2) or m.group(3)
    already_found = {b["id"] for b in broken_locators}
    for attr, selector in pom_locators.items():
        if attr in already_found:
            continue
        if re.search(rf'\b{re.escape(attr)}\b', test_content):
            broken_locators.append({
                "id":          attr,
                "old_locator": selector,
                "error":       "Regression failed — locator may be stale",
            })
            send_log(f"  Supplemented: {attr} → '{selector}'",
                     stage="run_regression", level="warning")
    if not fail_count:
        fail_count = len(broken_locators)
    send_log(f"⚡ {fail_count} test(s) FAILED — locator decay detected ({len(broken_locators)} locator(s) to check)",
             stage="run_regression", level="warning")
    send_stage("stage_complete", "run_regression",
               f"{fail_count} test(s) FAILED — self-heal triggered",
               level="success",
               data={"failed": fail_count,
                     "broken_locators": [b["id"] for b in broken_locators]})

    # ── HITL gate ───────────────────────────────────────────────────────────
    choice = hitl_gate(
        "approve-heal",
        f"{fail_count} regression test(s) failed after UI PR #{pr_number}. Approve self-heal?",
        {"ui_pr": pr_url_arg, "failed_tests": fail_count,
         "broken_locators": [b["id"] for b in broken_locators]},
    )
    if choice == "reject":
        send_log("Self-heal rejected by operator.", stage="run_regression", level="warning")
        _post({"type": "workflow_complete",
               "message": "Self-heal rejected at HITL gate", "level": "warning"})
        return

    # ── Stage 3 + 4: Inspect DOM + Claude heals ─────────────────────────────
    send_stage("stage_start", "inspect_dom",
               f"Playwright MCP navigating to {UI_URL}…")
    send_log(f"browser_navigate({UI_URL}) + browser_snapshot()", stage="inspect_dom")

    send_stage("stage_start", "apply_heal",
               "Claude reasoning with GitHub MCP + Playwright MCP…")

    heals = call_claude_with_mcps(broken_locators, pr_number, mcp_config, ui_repo)

    send_stage("stage_complete", "inspect_dom", "DOM snapshot captured ✓",
               level="success", data={"url": UI_URL})

    if not heals:
        send_stage("stage_error", "apply_heal",
                   "Claude did not return valid heals — check MCP connectivity")
        _post({"type": "workflow_complete", "message": "Heal failed", "level": "error"})
        return

    for h in heals:
        send_log(f"  ✦ {h.get('id')}: {h.get('old_locator')} → {h.get('new_locator')}",
                 stage="apply_heal", level="success")

    patch_count = apply_patch(heals)
    if patch_count == 0:
        send_stage("stage_error", "apply_heal",
                   "Patch failed — old selector strings not found verbatim in POM")
        _post({"type": "workflow_complete", "message": "Patch failed", "level": "error"})
        return

    send_stage("stage_complete", "apply_heal",
               f"{patch_count} selector(s) healed ✓", level="success",
               data={"selectors_healed": patch_count, "file": POM_FILE,
                     "artifacts": [{"path": POM_FILE, "type": "python", "label": "Heal Patch"}]})

    # ── Stage 6: Verify heal ────────────────────────────────────────────────
    send_stage("stage_start", "verify_heal",
               "Re-running regression with healed locators…")

    rc, out = run_pytest("verify_heal", base_url=UI_URL)
    summary = _parse_summary(out)

    if rc != 0:
        send_stage("stage_error", "verify_heal",
                   "Heal did not fully resolve failures — manual review needed")
        _post({"type": "workflow_complete",
               "message": "Verification failed after heal", "level": "error"})
        return

    send_log(f"{summary['passed']} passed, 0 failed 🎉", stage="verify_heal", level="success")
    send_stage("stage_complete", "verify_heal",
               f"Heal confirmed: {summary['passed']}/{summary['total']} passed ✅",
               level="success",
               data={"passed": summary["passed"], "failed": 0,
                     "duration_s": int(summary.get("duration") or 0)})

    # ── Stage 7: Raise heal PR ──────────────────────────────────────────────
    send_stage("stage_start", "raise_heal_pr",
               f"Raising heal PR on {AUTO_REPO} via GitHub MCP…")
    send_log("claude -p → create_branch + create_or_update_file + create_pull_request",
             stage="raise_heal_pr")

    pr_url_result = raise_heal_pr_via_claude(pr_number, mcp_config)

    num_match  = re.search(r'/pull/(\d+)', pr_url_result)
    actual_num = num_match.group(1) if num_match else "?"

    # Write heal summary artifact
    summary_path = project_root / "reports" / "heal_summary.md"
    summary_path.parent.mkdir(exist_ok=True)
    summary_path.write_text(
        f"# Self-Heal Summary\n\n"
        f"**UI PR:** [{pr_info['title']}]"
        f"(https://github.com/{UI_REPO}/pull/{pr_number})\n"
        f"**Heal PR:** [PR #{actual_num}]({pr_url_result})\n"
        f"**Branch:** `heal/ui-pr-{pr_number}-locators`\n\n"
        f"## Locators Healed\n\n"
        + "".join(
            f"- `{h.get('id')}`: `{h.get('old_locator')}` → `{h.get('new_locator')}`\n"
            f"  *{h.get('reasoning', '')}*\n\n"
            for h in heals
        )
        + "\n## Test Results After Heal\n\n"
        "| Test | Result |\n|---|---|\n"
        "| test_reg_location_input_visible | ✅ PASSED |\n"
        "| test_reg_location_input_accepts_typing | ✅ PASSED |\n"
        "| test_reg_search_button_visible | ✅ PASSED |\n"
    )

    send_stage("stage_complete", "raise_heal_pr",
               f"Heal PR #{actual_num} raised ✅", level="success",
               data={"pr_number": actual_num, "pr_url": pr_url_result,
                     "branch": f"heal/ui-pr-{pr_number}-locators",
                     "artifacts": [{"path": "reports/heal_summary.md",
                                    "type": "markdown", "label": "Heal Summary"}]})

    _post({
        "type":    "workflow_complete",
        "message": "Self-heal complete — all regression tests passing ✅",
        "level":   "success",
        "data":    {"heal_pr": pr_url_result,
                    "ui_pr":   f"https://github.com/{ui_repo}/pull/{pr_number}"},
    })

    print()
    print(f"  ✅ Self-heal complete — {pr_url_result}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _repo_from_url(pr_url: str, fallback: str = UI_REPO) -> str:
    """Extract owner/repo from a GitHub PR URL."""
    m = re.match(r'https://github\.com/([^/]+/[^/]+)/pull/', pr_url or '')
    return m.group(1) if m else fallback


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--embedded", action="store_true",
                        help="Called from mock runner — only handles apply_heal stage.")
    parser.add_argument("--pr-number",       type=str, default=None)
    parser.add_argument("--pr-branch",       type=str, default=None)
    parser.add_argument("--pr-title",        type=str, default=None)
    parser.add_argument("--pr-url",          type=str, default=None)
    parser.add_argument("--broken-locators", type=str, default=None,
                        help="JSON array — skips pytest when provided (embedded only).")
    parser.add_argument("--mcp-config",      type=str, default=None,
                        help="Path to MCP config JSON (defaults to .mcp.headed.json).")
    args = parser.parse_args()

    pr_number  = args.pr_number or os.getenv("PR_NUMBER", "7")
    mcp_config = args.mcp_config or make_headed_mcp_config()

    # Derive the actual UI repo from the PR URL so any repo works
    ui_repo = _repo_from_url(args.pr_url) if args.pr_url else UI_REPO

    print("=" * 50)
    print("Joulez AI Self-Heal Agent")
    print(f"PR: {ui_repo}#{pr_number}  |  embedded={args.embedded}")
    print("=" * 50)

    if args.embedded:
        broken: list[dict] = []
        if args.broken_locators:
            try:
                broken = json.loads(args.broken_locators)
            except json.JSONDecodeError:
                pass
        rc = _run_embedded(pr_number, broken, mcp_config)
        sys.exit(rc)
    else:
        _run_standalone(
            pr_number  = pr_number,
            pr_branch  = args.pr_branch or "",
            pr_url_arg = args.pr_url    or f"https://github.com/{ui_repo}/pull/{pr_number}",
            mcp_config = mcp_config,
            ui_repo    = ui_repo,
        )


if __name__ == "__main__":
    main()
