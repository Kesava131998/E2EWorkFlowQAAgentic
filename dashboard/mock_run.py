#!/usr/bin/env python3
"""
Mock run of the RevFlow E2E Workflow — KAN-2: Task 2 (Payment Schedule Icon).

Streams realistic events to the dashboard server using real KAN-2 data.
No Jira, GitHub, or test execution touches — purely for UI demo purposes.

Usage:
  python dashboard/mock_run.py            # normal speed (~3 min total)
  python dashboard/mock_run.py --fast     # 3x faster (~1 min)
  python dashboard/mock_run.py --instant  # no delays (server stress test)
  python dashboard/mock_run.py --no-hitl  # skip HITL gates (unattended demo)
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API = "http://localhost:8765"

# Real KAN-2 data
TICKET = "KAN-2"
SUMMARY = "Task 2 — Payment Schedule Icon"
BRANCH = "kan-2-task-2"
PR_URL = "https://github.com/innocito/AI-Test-Workflow/pull/24"
COMMIT = "b7e21f4"
JIRA_URL = "https://vikeshwiki9.atlassian.net/browse/KAN-2"

# No Swagger/OpenAPI spec is configured for RevFlow yet — Swagger Discovery is skipped.

TEST_CASES = [
    {"tc": "TC1", "ac": "AC1", "type": "Happy Path", "fn": "test_pos_calendar_icon_appears_when_schedule_exists", "scenario": "Calendar icon appears when payer schedule exists"},
    {"tc": "TC2", "ac": "AC2", "type": "Negative",    "fn": "test_err_no_calendar_icon_when_no_schedule",         "scenario": "No icon appears when no payer schedule exists"},
    {"tc": "TC3", "ac": "AC3", "type": "Edge Case",   "fn": "test_err_icon_hidden_without_payer_grouping",        "scenario": "Icon hidden when grouping has no payer level above resident"},
    {"tc": "TC4", "ac": "AC4", "type": "Negative",    "fn": "test_err_icon_not_clickable",                        "scenario": "Icon is not clickable and has no hover state beyond tooltip"},
    {"tc": "TC5", "ac": "AC5", "type": "Happy Path",  "fn": "test_pos_tooltip_shows_schedule_details",            "scenario": "Tooltip displays schedule details on hover"},
    {"tc": "TC6", "ac": "AC5", "type": "Edge Case",   "fn": "test_pos_tooltip_ordinal_schedule_format",           "scenario": "Tooltip displays alternate schedule format correctly"},
    {"tc": "TC7", "ac": "AC6", "type": "Regression",  "fn": "test_pos_resident_hyperlink_unaffected_by_icon",     "scenario": "Icon does not interfere with resident name hyperlink"},
]

# Tests run in the demo (all 7 KAN-2 cases — TODO stubs pending icon shipping)
TEST_RESULTS = {
    "test_pos_calendar_icon_appears_when_schedule_exists": "skip",
    "test_err_no_calendar_icon_when_no_schedule":          "skip",
    "test_err_icon_hidden_without_payer_grouping":         "skip",
    "test_err_icon_not_clickable":                         "skip",
    "test_pos_tooltip_shows_schedule_details":             "skip",
    "test_pos_tooltip_ordinal_schedule_format":            "skip",
    "test_pos_resident_hyperlink_unaffected_by_icon":      "skip",
}


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


class Runner:
    def __init__(self, speed: float, no_hitl: bool):
        self.speed = speed          # 1.0 = normal, 3.0 = fast, 0 = instant
        self.no_hitl = no_hitl

    def sleep(self, seconds: float):
        if self.speed > 0:
            time.sleep(seconds / self.speed)

    def log(self, msg, level="info", stage=None):
        send({"type": "log", "stage": stage, "message": msg, "level": level})
        self.sleep(0.18)

    def ai(self, phase: str, content: str, stage: str = None,
           model: str = "claude-sonnet-4-5", tokens: int = None, elapsed_ms: int = None):
        """Emit an ai_activity event visible in the Claude pane."""
        send({
            "type": "ai_activity",
            "stage": stage,
            "data": {
                "phase":      phase,
                "content":    content,
                "model":      model,
                "tokens":     tokens,
                "elapsed_ms": elapsed_ms,
            },
        })
        self.sleep(0.1)

    def stage_start(self, stage_id: str, message: str, data: dict = None):
        send({"type": "stage_start", "stage": stage_id, "message": message, "level": "info", "data": data or {}})
        print(f"\n  ▶ {message}")

    def stage_done(self, stage_id: str, message: str, data: dict = None):
        send({"type": "stage_complete", "stage": stage_id, "message": message, "level": "success", "data": data or {}})
        print(f"  ✓ {message}")

    def hitl(self, checkpoint_id: str, message: str, options: list, context: dict = None) -> str:
        if self.no_hitl:
            print(f"\n  ⏸  [HITL skipped] {checkpoint_id} → auto-approve")
            send({
                "type": "hitl_checkpoint",
                "stage": f"hitl_{checkpoint_id.replace('-','_')}",
                "checkpoint_id": checkpoint_id,
                "message": message,
                "level": "warning",
                "data": context or {},
                "options": options,
            })
            self.sleep(0.5)
            # auto-respond
            body = json.dumps({"choice": "approve"}).encode()
            urllib.request.urlopen(
                urllib.request.Request(f"{API}/hitl/{checkpoint_id}/respond",
                                       data=body, headers={"Content-Type": "application/json"}, method="POST"),
                timeout=5,
            )
            return "approve"

        send({
            "type": "hitl_checkpoint",
            "stage": f"hitl_{checkpoint_id.replace('-','_')}",
            "checkpoint_id": checkpoint_id,
            "message": message,
            "level": "warning",
            "data": context or {},
            "options": options,
        })
        print(f"\n  ⏸  HITL: {message}")
        print(f"     → Waiting for response at http://localhost:5173 ...")
        choice = wait_hitl(checkpoint_id)
        symbol = "✓ Approved" if choice in ("approve", "timeout") else "✗ Rejected"
        print(f"     {symbol}")
        return choice

    # -----------------------------------------------------------------------
    # Stages
    # -----------------------------------------------------------------------

    def run_stage1_jira(self):
        self.stage_start("jira_fetch", f"Fetching {TICKET} from Jira...")
        self.log("Connecting to Jira Cloud (vikeshwiki9.atlassian.net)...", stage="jira_fetch")
        self.sleep(1.2)
        self.log(f"Issue found: {TICKET} — {SUMMARY}", "success", stage="jira_fetch")
        self.sleep(0.5)
        self.log("Extracting acceptance criteria (6 ACs found)...", stage="jira_fetch")
        self.sleep(0.8)
        self.log("Status: In Progress  |  Priority: Unset  |  Assignee: Unassigned", stage="jira_fetch")
        self.sleep(0.4)
        self.stage_done("jira_fetch", f"{TICKET}: {SUMMARY}", {
            "ticket": TICKET,
            "summary": SUMMARY,
            "status": "In Progress",
            "priority": "Unset",
            "assignee": "Unassigned",
            "acs_found": 6,
            "jira_url": JIRA_URL,
        })

    def run_stage2_branch(self):
        self.stage_start("branch_create", "Creating feature branch...")
        self.log("git checkout main && git pull origin main", stage="branch_create")
        self.sleep(1.0)
        self.log(f"git checkout -b {BRANCH}", stage="branch_create")
        self.sleep(0.8)
        self.log(f"Branch ready: {BRANCH}", "success", stage="branch_create")
        self.sleep(0.3)
        self.log("Jira already In Progress — skipping transition", stage="branch_create")
        self.stage_done("branch_create", f"Branch: {BRANCH}", {"branch": BRANCH, "base": "main"})

    def run_stage3_test_cases(self):
        self.stage_start("test_cases", "Deriving test cases from ACs...")
        acs = ["AC1: Icon appears when schedule exists", "AC2: No icon when no schedule",
               "AC3: Icon requires payer grouping above resident", "AC4: Icon not clickable",
               "AC5: Tooltip shows label/value/method", "AC6: Icon doesn't block resident hyperlink"]
        for ac in acs:
            self.log(f"Analysing {ac}...", stage="test_cases")
            self.sleep(0.7)
        self.sleep(0.5)

        # Claude pane — show the derivation prompt
        self.ai("prompt",
            "You are a QA engineer. Given the following acceptance criteria for\n"
            "KAN-2 (Payment Schedule Icon), derive a comprehensive test case\n"
            "matrix covering Happy Path, Negative, and Edge Case scenarios.\n\n"
            "AC1: Calendar icon appears when a payer schedule exists\n"
            "AC2: No icon appears when no payer schedule is configured\n"
            "AC3: Icon only renders when grouping includes a payer level above resident\n"
            "AC4: Icon is not clickable, no hover state beyond tooltip\n"
            "AC5: Tooltip shows label, schedule value, and payment method\n"
            "AC6: Icon does not interfere with the resident name hyperlink\n\n"
            "Output a test case table with columns: ID, AC, Type, Function Name, Scenario.",
            stage="test_cases", tokens=240
        )
        self.sleep(0.3)
        self.ai("thinking", "Mapping ACs to test types…\nIdentifying edge cases for schedule format variations…",
                stage="test_cases")
        self.sleep(1.5)
        self.ai("response",
            f"Derived {len(TEST_CASES)} test cases across 6 ACs:\n"
            "• 3 Happy Path  · 3 Negative  · 1 Regression\n\n"
            "Sample:\n"
            "  TC1  test_pos_calendar_icon_appears_when_schedule_exists\n"
            "  TC2  test_err_no_calendar_icon_when_no_schedule\n"
            "  TC3  test_err_icon_hidden_without_payer_grouping\n"
            "  TC5  test_pos_tooltip_shows_schedule_details",
            stage="test_cases", tokens=170, elapsed_ms=1480
        )

        self.log("Generating Happy Path, Negative, Edge cases...", stage="test_cases")
        self.sleep(1.0)
        self.log(f"Derived {len(TEST_CASES)} test cases", "success", stage="test_cases")
        self.log("Saved to plans/manual_tests_kan-2_2026-07-14.md", stage="test_cases")
        self.log("Saved to plans/manual_tests_kan-2_2026-07-14.csv", stage="test_cases")
        self.stage_done("test_cases", f"{len(TEST_CASES)} test cases derived", {
            "cases_total": len(TEST_CASES),
            "ui_cases": len(TEST_CASES),
            "api_cases": 0,
            "acs_covered": 6,
            "plan_file": "plans/manual_tests_kan-2_2026-07-14.md",
            "artifacts": [
                {"path": "plans/manual_tests_kan-2_2026-07-14.csv", "type": "csv",      "label": "Test Cases CSV"},
                {"path": "plans/manual_tests_kan-2_2026-07-14.md",  "type": "markdown", "label": "Test Cases MD"},
            ],
        })

    def run_hitl1_review(self) -> str:
        tc_summary = "\n".join(
            f"  {t['tc']:4s}  {t['ac']}  [{t['type']:10s}]  {t['fn']}"
            for t in TEST_CASES
        )

        return self.hitl(
            checkpoint_id="test-case-review",
            message=f"I derived {len(TEST_CASES)} test cases from KAN-2: {SUMMARY}.\n\nWould you like to add, remove, or modify any cases before I proceed to generation?",
            options=[
                {"id": "approve", "label": "Looks good — proceed to generate", "variant": "success"},
                {"id": "reject",  "label": "I want to make changes",           "variant": "warning"},
            ],
            context={
                "ticket": TICKET,
                "total_cases": len(TEST_CASES),
                "ui_cases": len(TEST_CASES),
                "api_cases": 0,
                "acs_covered": "AC1–AC6",
                "plan_file": "plans/manual_tests_kan-2_2026-07-14.md",
                "artifacts": [
                    {"csvPath": "plans/manual_tests_kan-2_2026-07-14.csv", "mdPath": "plans/manual_tests_kan-2_2026-07-14.md", "type": "testcases", "label": "Test Cases"},
                ],
            },
        )

    def run_hitl_api_scope(self) -> str:
        return self.hitl(
            checkpoint_id="api-test-scope",
            message="This is a UI flow ticket, but no Swagger/OpenAPI spec is configured for RevFlow yet, so API test generation isn't available.\n\nProceed with UI tests only?",
            options=[
                {"id": "approve", "label": "No — UI tests only",  "variant": "default"},
                {"id": "reject",  "label": "Cancel",               "variant": "warning"},
            ],
            context={
                "ticket": TICKET,
                "swagger_endpoints": 0,
                "note": "No OpenAPI spec configured for RevFlow — API test generation skipped",
            },
        )

    def run_hitl_naming_preview(self) -> str:
        ui_fns = [t["fn"] for t in TEST_CASES]
        return self.hitl(
            checkpoint_id="test-naming-preview",
            message=f"Here are the {len(ui_fns)} UI test function names I'll generate. Approve to proceed, or request renames via the feedback field.",
            options=[
                {"id": "approve", "label": "Looks good — proceed",   "variant": "success"},
                {"id": "reject",  "label": "Request renames",         "variant": "feedback"},
            ],
            context={
                "ticket": TICKET,
                "functions_count": len(TEST_CASES),
                "ui_functions": ui_fns,
                "api_functions": [],
            },
        )

    def run_hitl1b_scope(self) -> str:
        fn_list = [t["fn"] for t in TEST_CASES]
        return self.hitl(
            checkpoint_id="test-execution-scope",
            message=f"I generated {len(TEST_CASES)} test functions in tests/test_kan2_payment_schedule.py.\n\nThe payment schedule icon feature hasn't shipped yet, so steps are TODO stubs. How would you like to proceed?",
            options=[
                {"id": "reject",  "label": "Skip — go straight to commit", "variant": "warning"},
                {"id": "all",     "label": "Run collection check only",     "variant": "default"},
            ],
            context={
                "total_functions": len(TEST_CASES),
                "ui_functions": len(TEST_CASES),
                "api_functions": 0,
                "sample_tests": fn_list,
                "artifacts": [
                    {"path": "tests/test_kan2_payment_schedule.py", "type": "python", "label": "UI Tests"},
                ],
            },
        )

    def run_stage4_generate(self):
        self.stage_start("generate_tests", "Generating Playwright test scripts...")
        self.log("Creating tests/test_kan2_payment_schedule.py...", stage="generate_tests")
        self.sleep(0.8)

        # Claude pane — code generation prompt
        self.ai("prompt",
            "Generate a Playwright (Python) test file for the following test cases.\n"
            "Use the TaskListPage page object model. Follow these conventions:\n"
            "  · @allure.story / @allure.title decorators on each test\n"
            "  · Prefix: test_pos_ (happy), test_err_ (negative)\n"
            "  · Use settings.TIMEOUT, never raw integers\n\n"
            "Test cases (7 tests):\n"
            "  TC1  test_pos_calendar_icon_appears_when_schedule_exists\n"
            "  TC2  test_err_no_calendar_icon_when_no_schedule\n"
            "  TC3  test_err_icon_hidden_without_payer_grouping\n"
            "  TC4  test_err_icon_not_clickable\n"
            "  TC5  test_pos_tooltip_shows_schedule_details",
            stage="generate_tests", tokens=232
        )
        self.sleep(0.3)
        self.ai("thinking", "Mapping test cases to TaskListPage methods…\nInferring assertions from acceptance criteria…",
                stage="generate_tests")

        for t in TEST_CASES:
            self.log(f"  + {t['fn']}  [{t['type']}]", stage="generate_tests")
            self.sleep(0.25)

        self.sleep(0.4)
        self.ai("response",
            f"Generated {len(TEST_CASES)} UI test functions in tests/test_kan2_payment_schedule.py\n"
            "Steps marked # TODO: Implement — payment schedule icon feature not yet shipped\n"
            "All functions follow naming convention and @allure.step pattern ✓",
            stage="generate_tests", tokens=58, elapsed_ms=2980
        )

        self.sleep(0.5)
        self.log("Verifying test collection: pytest --collect-only...", stage="generate_tests")
        self.sleep(1.2)
        self.log(f"{len(TEST_CASES)} tests collected in 0.17s ✓", "success", stage="generate_tests")
        self.stage_done("generate_tests", f"{len(TEST_CASES)} test functions generated", {
            "ui_file": "tests/test_kan2_payment_schedule.py",
            "api_file": None,
            "total_functions": len(TEST_CASES),
            "collected": f"{len(TEST_CASES)} items",
            "artifacts": [
                {"path": "tests/test_kan2_payment_schedule.py", "type": "python", "label": "UI Tests"},
            ],
        })

    def run_stage6_commit(self):
        self.stage_start("commit_push", "Committing and pushing...")
        self.log(f"Branch guard: current = {BRANCH} ✓", stage="commit_push")
        self.sleep(0.6)
        self.log("Pre-commit checks:", stage="commit_push")
        checks = [
            "No print() statements ✓",
            "No raw integer timeouts ✓",
            "All page methods have @allure.step ✓",
            "Naming convention (test_pos_/test_err_/test_perm_) ✓",
            "No hardcoded credentials ✓",
        ]
        for c in checks:
            self.log(f"  {c}", "success", stage="commit_push")
            self.sleep(0.2)
        self.sleep(0.4)
        self.log("git add tests/test_kan2_payment_schedule.py plans/...", stage="commit_push")
        self.sleep(0.8)
        self.log('git commit -m "test(payment_schedule): add automation tests for KAN-2"', stage="commit_push")
        self.sleep(1.0)
        self.log(f"Committed: {COMMIT}", "success", stage="commit_push")
        self.sleep(0.5)
        self.log(f"git push -u origin {BRANCH}", stage="commit_push")
        self.sleep(1.2)
        self.log("Pushed ✓", "success", stage="commit_push")
        self.stage_done("commit_push", f"Committed {COMMIT} and pushed", {
            "commit": COMMIT,
            "branch": BRANCH,
            "files_staged": 3,
        })

    def run_stage7_pr(self):
        self.stage_start("raise_pr", "Creating GitHub pull request...")
        self.log("mcp__github__create_pull_request(owner=innocito, repo=AI-Test-Workflow, ...)", stage="raise_pr")
        self.sleep(2.0)
        self.log(f"PR #24 created: [{TICKET}] test(payment_schedule): add automation tests", "success", stage="raise_pr")
        self.log(f"URL: {PR_URL}", "success", stage="raise_pr")
        self.log("Draft: true  |  Base: main  |  Coverage delta: 10 → 17 tests (+7)", stage="raise_pr")
        self.stage_done("raise_pr", f"PR #24 raised (draft) — {PR_URL}", {
            "pr_number": 24,
            "pr_url": PR_URL,
            "title": f"[{TICKET}] test(payment_schedule): add automation tests",
            "draft": True,
            "tests_added": len(TEST_CASES),
            "coverage_before": 10,
            "coverage_after": 10 + len(TEST_CASES),
            "artifacts": [
                {"path": "plans/run_summary_kan-2_2026-07-14.md", "type": "markdown", "label": "Run Summary"},
            ],
        })

    def run_stage8_jira(self):
        self.stage_start("update_jira", "Updating Jira ticket...")
        self.log("jira_add_comment(issue_key=KAN-2, body=...)", stage="update_jira")
        self.sleep(1.5)
        self.log("Comment posted with test scaffold summary and PR link ✓", "success", stage="update_jira")
        self.sleep(0.5)
        self.log("jira_transition_issue(KAN-2 → In Review)...", stage="update_jira")
        self.sleep(0.8)
        self.log("KAN-2 transitioned → In Review ✓", "success", stage="update_jira")
        self.stage_done("update_jira", "KAN-2 updated and transitioned → In Review", {
            "ticket": TICKET,
            "transition": "In Review",
            "pr_url": PR_URL,
        })

    def run_stage9_review(self):
        self.stage_start("pr_review", "Spawning PR review agent...")
        self.log("Initialising review agent for PR #24...", stage="pr_review")
        self.sleep(1.2)
        self.log("Fetching PR diff: 3 files changed, +198 −0 lines", stage="pr_review")
        self.sleep(1.0)
        self.log("Checking: @allure.step on all public page methods...", stage="pr_review")
        self.sleep(0.8)
        self.log("  ✓ task_list_page.py — all 8 methods decorated", "success", stage="pr_review")
        self.log("Checking: no raw integer timeouts...", stage="pr_review")
        self.sleep(0.6)
        self.log("  ✓ settings.TIMEOUT used throughout", "success", stage="pr_review")
        self.log("Checking: test naming convention...", stage="pr_review")
        self.sleep(0.6)
        self.log("  ✓ test_pos_*/test_err_* — all 7 pass", "success", stage="pr_review")
        self.log("Checking: no hardcoded credentials or URLs...", stage="pr_review")
        self.sleep(0.5)
        self.log("  ✓ BASE_URL/AUTH_* from settings, no inline secrets", "success", stage="pr_review")
        self.sleep(0.8)
        self.log("Review decision: COMMENT (draft — steps pending real feature) ✓", "success", stage="pr_review")
        self.log("Review posted to GitHub PR #24", "success", stage="pr_review")
        self.stage_done("pr_review", "Review: COMMENT — posted to PR #24", {
            "decision": "COMMENT",
            "pr_url": PR_URL,
            "issues_found": 0,
            "suggestions": 1,
        })

    # -----------------------------------------------------------------------
    # Main
    # -----------------------------------------------------------------------

    def run(self):
        print()
        print("  ╔══════════════════════════════════════════════╗")
        print("  ║  RevFlow · E2E Workflow Mock Run             ║")
        print("  ║  KAN-2: Task 2 — Payment Schedule Icon       ║")
        print("  ╚══════════════════════════════════════════════╝")
        print()

        # Check server
        try:
            urllib.request.urlopen(f"{API}/health", timeout=3)
        except Exception:
            print("  ✗ Dashboard server not reachable at http://localhost:8765")
            print("    Start it first: python dashboard/server/main.py")
            sys.exit(1)

        print("  ✓ Dashboard server connected")
        print("  ✓ Opening http://localhost:5173")
        print()
        if self.no_hitl:
            print("  ℹ  --no-hitl: HITL checkpoints will auto-approve")
        print()

        send({"type": "workflow_start", "message": f"KAN-2 — {SUMMARY}", "data": {
            "ticket": TICKET,
            "summary": SUMMARY,
            "branch": BRANCH,
            "runner": "mock",
        }})

        self.run_stage1_jira()
        self.sleep(1.0)

        self.run_stage2_branch()
        self.sleep(0.8)

        self.run_stage3_test_cases()
        self.sleep(1.0)

        choice1 = self.run_hitl1_review()
        if choice1 == "reject":
            self.log("Workflow paused — user wants to revise test cases.", "warning")
            send({"type": "workflow_complete", "message": "Workflow paused at HITL checkpoint 1"})
            print("\n  Workflow paused at HITL-1. Re-run after revision.")
            return

        self.sleep(0.8)
        self.run_hitl_api_scope()
        self.sleep(0.8)

        self.run_hitl_naming_preview()
        self.sleep(0.8)

        self.run_stage4_generate()
        self.sleep(1.0)

        self.run_hitl1b_scope()
        self.sleep(0.8)

        self.run_stage6_commit()
        self.sleep(0.8)

        self.run_stage7_pr()
        self.sleep(0.8)

        self.run_stage8_jira()
        self.sleep(0.8)

        self.run_stage9_review()

        send({"type": "workflow_complete", "message": "All stages complete — KAN-2 ✓", "level": "success", "data": {
            "ticket": TICKET,
            "pr_url": PR_URL,
            "tests_added": len(TEST_CASES),
            "verdict": "COMMENT",
        }})

        print()
        print("  ═══════════════════════════════════════════════")
        print(f"  ✓ Workflow complete — {PR_URL}")
        print("  ═══════════════════════════════════════════════")
        print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock e2e workflow run for KAN-2")
    speed_group = parser.add_mutually_exclusive_group()
    speed_group.add_argument("--fast",    action="store_true", help="3× faster")
    speed_group.add_argument("--instant", action="store_true", help="No delays")
    parser.add_argument("--no-hitl", action="store_true", help="Auto-approve all HITL checkpoints")
    args = parser.parse_args()

    speed = 0 if args.instant else (3.0 if args.fast else 1.0)
    Runner(speed=speed, no_hitl=args.no_hitl).run()
