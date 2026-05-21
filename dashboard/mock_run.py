#!/usr/bin/env python3
"""
Mock run of the Joulez E2E Workflow — JP-1: Pre Payment Booking Flow.

Streams realistic events to the dashboard server using real JP-1 data.
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

# Real JP-1 data
TICKET = "JP-1"
SUMMARY = "Pre Payment Booking Flow"
BRANCH = "jp-1-pre-payment-booking-flow-v17"
PR_URL = "https://github.com/innocito/AI-Test-Workflow/pull/17"
COMMIT = "a3cca2a"
JIRA_URL = "https://innocito.atlassian.net/browse/JP-1"

SWAGGER_ENDPOINTS = [
    "POST   /joulez-service/booking/create-booking",
    "GET    /joulez-service/cars/get-available-cars-details",
    "POST   /joulez-service/cars/get-available-cars-details",
    "GET    /joulez-service/location/get-available-locations",
    "POST   /joulez-service/booking/estimated-price",
    "GET    /joulez-service/cars/get-car-filter",
    "GET    /joulez-service/booking/get-booking-details-by-id/{id}",
    "POST   /joulez-service/user/create-authn-token",
    "GET    /joulez-service/payment/make-payment-intent",
    "GET    /joulez-service/cars/get-protection-plans",
    "GET    /joulez-service/cars/get-all-extras",
    "GET    /joulez-service/booking/check-booking-eligibility",
]

TEST_CASES = [
    # AC1 — Location Selection
    {"tc": "TC1",  "ac": "AC1", "type": "Happy Path",  "fn": "test_pos_select_serviceable_pickup_location",  "scenario": "Select Bronx, NY as pickup location"},
    {"tc": "TC2",  "ac": "AC1", "type": "Happy Path",  "fn": "test_pos_select_different_dropoff_location",   "scenario": "Set different drop-off (Brooklyn, NY)"},
    {"tc": "TC3",  "ac": "AC1", "type": "Happy Path",  "fn": "test_pos_delivery_option_available",           "scenario": "Delivery option visible for metro area"},
    {"tc": "TC4",  "ac": "AC1", "type": "Negative",    "fn": "test_err_unserviceable_location_no_results",   "scenario": "Seattle, WA returns no vehicles"},
    {"tc": "TC5",  "ac": "AC1", "type": "Edge Case",   "fn": "test_edge_same_pickup_dropoff_location",       "scenario": "Same pickup and drop-off location"},
    # AC2 — Date & Time
    {"tc": "TC6",  "ac": "AC2", "type": "Happy Path",  "fn": "test_pos_select_pickup_date_from_calendar",    "scenario": "Pick future date from calendar"},
    {"tc": "TC7",  "ac": "AC2", "type": "Happy Path",  "fn": "test_pos_duration_auto_calculated",            "scenario": "Rental duration auto-calculates"},
    {"tc": "TC8",  "ac": "AC2", "type": "Happy Path",  "fn": "test_pos_default_values_prepopulated",         "scenario": "Default date/time pre-populated"},
    {"tc": "TC9",  "ac": "AC2", "type": "Negative",    "fn": "test_err_past_dates_disabled_in_calendar",     "scenario": "Past dates are disabled in picker"},
    # AC3 — Vehicle Search
    {"tc": "TC10", "ac": "AC3", "type": "Happy Path",  "fn": "test_pos_vehicle_search_returns_results",      "scenario": "Search returns EV list for Bronx, NY"},
    {"tc": "TC11", "ac": "AC3", "type": "Happy Path",  "fn": "test_pos_vehicle_card_displays_required_fields","scenario": "Each card shows name, rate, range, seats"},
    {"tc": "TC12", "ac": "AC3", "type": "Happy Path",  "fn": "test_pos_filter_buttons_available",            "scenario": "Filter controls visible (Type/Brand/Price)"},
    {"tc": "TC13", "ac": "AC3", "type": "Negative",    "fn": "test_err_no_vehicles_for_unserviceable_location","scenario": "No results for Denver, CO"},
    # AC4 — Vehicle Selection
    {"tc": "TC14", "ac": "AC4", "type": "Happy Path",  "fn": "test_pos_view_vehicle_detail_page",            "scenario": "Click card → detail page loads"},
    {"tc": "TC15", "ac": "AC4", "type": "Happy Path",  "fn": "test_pos_vehicle_detail_shows_pickup_dropoff", "scenario": "Pickup/drop-off shown on detail page"},
    # AC5 — Pricing
    {"tc": "TC16", "ac": "AC5", "type": "Happy Path",  "fn": "test_pos_pricing_breakdown_displayed",         "scenario": "Base rate, taxes, total all visible"},
    {"tc": "TC17", "ac": "AC5", "type": "Happy Path",  "fn": "test_pos_grand_total_prominently_displayed",   "scenario": "Grand total is highlighted"},
    {"tc": "TC18", "ac": "AC5", "type": "Happy Path",  "fn": "test_pos_base_rate_visible",                   "scenario": "Per-day and per-trip rates shown"},
    # AC6 — Booking/Auth
    {"tc": "TC19", "ac": "AC6", "type": "RBAC",        "fn": "test_perm_guest_sees_auth_gate",               "scenario": "Guest user sees login prompt"},
    {"tc": "TC20", "ac": "AC6", "type": "RBAC",        "fn": "test_perm_guest_can_initiate_signup",          "scenario": "Guest can reach signup via 'Join Us'"},
    {"tc": "TC21", "ac": "AC6", "type": "Negative",    "fn": "test_err_guest_cannot_see_pay_now",            "scenario": "Pay Now hidden from unauthenticated user"},
    # API Tests
    {"tc": "API1", "ac": "AC3", "type": "API",         "fn": "test_api_pos_get_available_locations",         "scenario": "GET /location returns 6 serviceable locations"},
    {"tc": "API2", "ac": "AC3", "type": "API",         "fn": "test_api_pos_get_available_cars",              "scenario": "POST /cars returns vehicles for Bronx, NY"},
    {"tc": "API3", "ac": "AC5", "type": "API",         "fn": "test_api_pos_estimated_price",                 "scenario": "POST /estimated-price returns valid total"},
    {"tc": "API4", "ac": "AC3", "type": "API",         "fn": "test_api_err_cars_no_location",                "scenario": "POST /cars without location returns 400"},
    {"tc": "API5", "ac": "AC4", "type": "API",         "fn": "test_api_pos_car_detail",                      "scenario": "GET /car-detail/{id} returns full schema"},
    {"tc": "API6", "ac": "AC6", "type": "API",         "fn": "test_api_pos_authenticate",                    "scenario": "POST /authn-token returns valid JWT"},
]

# Tests run in the demo (AC1 scope — matches real PR #17 run)
TEST_RESULTS = {
    "test_pos_select_serviceable_pickup_location": "pass",
    "test_pos_select_different_dropoff_location":  "pass",
    "test_pos_delivery_option_available":          "xpass",
    "test_err_unserviceable_location_no_results":  "pass",
    "test_edge_same_pickup_dropoff_location":      "pass",
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
        self.log("Connecting to Jira Cloud (innocito.atlassian.net)...", stage="jira_fetch")
        self.sleep(1.2)
        self.log(f"Issue found: {TICKET} — {SUMMARY}", "success", stage="jira_fetch")
        self.sleep(0.5)
        self.log("Extracting acceptance criteria (6 ACs found)...", stage="jira_fetch")
        self.sleep(0.8)
        self.log("Status: In Progress  |  Priority: Medium  |  Assignee: Eswar Prasad Kona", stage="jira_fetch")
        self.sleep(0.4)
        self.stage_done("jira_fetch", f"{TICKET}: {SUMMARY}", {
            "ticket": TICKET,
            "summary": SUMMARY,
            "status": "In Progress",
            "priority": "Medium",
            "assignee": "Eswar Prasad Kona",
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
        self.log("Jira → transitioned to In Progress ✓", "success", stage="branch_create")
        self.stage_done("branch_create", f"Branch: {BRANCH}", {"branch": BRANCH, "base": "main"})

    def run_stage3a_swagger(self):
        self.stage_start("swagger_discovery", "Discovering relevant API endpoints...")
        self.log("Fetching spec: https://beta.drivejoulez.com:8443/joulez-service/v2/api-docs", stage="swagger_discovery")
        self.sleep(2.0)
        self.log(f"Parsed {len(SWAGGER_ENDPOINTS)} relevant endpoints:", stage="swagger_discovery")
        self.sleep(0.3)
        for ep in SWAGGER_ENDPOINTS[:6]:
            self.log(f"  {ep}", stage="swagger_discovery")
        self.log(f"  ... and {len(SWAGGER_ENDPOINTS) - 6} more", stage="swagger_discovery")
        self.stage_done("swagger_discovery", f"{len(SWAGGER_ENDPOINTS)} endpoints discovered", {
            "endpoints_found": len(SWAGGER_ENDPOINTS),
            "base_url": "https://beta.drivejoulez.com:8443",
        })

    def run_stage3_test_cases(self):
        self.stage_start("test_cases", "Deriving test cases from ACs...")
        acs = ["AC1: Location Selection", "AC2: Date & Time", "AC3: Vehicle Search",
               "AC4: Vehicle Selection", "AC5: Pricing Details", "AC6: Booking/Auth"]
        for ac in acs:
            self.log(f"Analysing {ac}...", stage="test_cases")
            self.sleep(0.7)
        self.sleep(0.5)
        self.log("Generating Happy Path, Negative, Edge, RBAC cases...", stage="test_cases")
        self.sleep(1.0)
        self.log(f"Derived {len(TEST_CASES)} test cases (21 UI + 6 API)", "success", stage="test_cases")
        self.log("Saved to plans/manual_tests_jp-1_2026-05-21.md", stage="test_cases")
        self.log("Saved to plans/manual_tests_jp-1_2026-05-21.csv", stage="test_cases")
        self.stage_done("test_cases", f"{len(TEST_CASES)} test cases derived", {
            "cases_total": len(TEST_CASES),
            "ui_cases": 21,
            "api_cases": 6,
            "acs_covered": 6,
            "plan_file": "plans/manual_tests_jp-1_2026-05-20.md",
            "artifacts": [
                {"path": "plans/manual_tests_jp-1_2026-05-20.csv",  "type": "csv",      "label": "Test Cases CSV"},
                {"path": "plans/manual_tests_jp-1_2026-05-20.md",   "type": "markdown", "label": "Test Cases MD"},
            ],
        })

    def run_hitl1_review(self) -> str:
        tc_summary = "\n".join(
            f"  {t['tc']:4s}  {t['ac']}  [{t['type']:10s}]  {t['fn']}"
            for t in TEST_CASES[:8]
        ) + f"\n  ... and {len(TEST_CASES) - 8} more"

        return self.hitl(
            checkpoint_id="test-case-review",
            message=f"I derived {len(TEST_CASES)} test cases from JP-1: Pre Payment Booking Flow.\n\nWould you like to add, remove, or modify any cases before I proceed to generation?",
            options=[
                {"id": "approve", "label": "Looks good — proceed to generate", "variant": "success"},
                {"id": "reject",  "label": "I want to make changes",           "variant": "warning"},
            ],
            context={
                "ticket": TICKET,
                "total_cases": len(TEST_CASES),
                "ui_cases": 21,
                "api_cases": 6,
                "acs_covered": "AC1–AC6",
                "plan_file": "plans/manual_tests_jp-1_2026-05-20.md",
                "artifacts": [
                    {"csvPath": "plans/manual_tests_jp-1_2026-05-20.csv", "mdPath": "plans/manual_tests_jp-1_2026-05-20.md", "type": "testcases", "label": "Test Cases"},
                ],
            },
        )

    def run_hitl_api_scope(self) -> str:
        return self.hitl(
            checkpoint_id="api-test-scope",
            message="Since this is a UI flow ticket, I can also generate independent API tests by intercepting network calls during the UI run and cross-referencing with Swagger.\n\nWould you like to include API test generation?",
            options=[
                {"id": "approve", "label": "Yes — include API tests",  "variant": "success"},
                {"id": "reject",  "label": "No — UI tests only",       "variant": "default"},
            ],
            context={
                "ticket": TICKET,
                "swagger_endpoints": len(SWAGGER_ENDPOINTS),
                "note": "API tests intercept network calls from the UI run and test endpoints directly via Swagger schema",
            },
        )

    def run_hitl_postman_scope(self) -> str:
        return self.hitl(
            checkpoint_id="postman-scope",
            message="Would you also like me to export a Postman-compatible collection (.json) for these endpoints?\n\nIt will be saved to plans/ and uploaded directly to the Joulez Postman workspace.",
            options=[
                {"id": "approve", "label": "Yes — export and upload",      "variant": "success"},
                {"id": "reject",  "label": "No — skip Postman export",     "variant": "default"},
            ],
            context={
                "ticket": TICKET,
                "endpoints": len(SWAGGER_ENDPOINTS),
                "workspace": "Joulez (bd9bcbaa-d3ab-48ba-...)",
                "output_file": "plans/postman_jp-1_2026-05-20.json",
            },
        )

    def run_hitl_naming_preview(self) -> str:
        ui_fns  = [t["fn"] for t in TEST_CASES if not t["fn"].startswith("test_api")]
        api_fns = [t["fn"] for t in TEST_CASES if t["fn"].startswith("test_api")]
        return self.hitl(
            checkpoint_id="test-naming-preview",
            message=f"Here are the {len(ui_fns)} UI + {len(api_fns)} API test function names I'll generate. Approve to proceed, or request renames via the feedback field.",
            options=[
                {"id": "approve", "label": "Looks good — proceed",   "variant": "success"},
                {"id": "reject",  "label": "Request renames",         "variant": "feedback"},
            ],
            context={
                "ticket": TICKET,
                "functions_count": len(TEST_CASES),
                "ui_functions": ui_fns[:8],
                "api_functions": api_fns,
                "note": f"... and {max(0, len(ui_fns) - 8)} more UI functions",
            },
        )

    def run_hitl1b_scope(self) -> str:
        fn_list = [t["fn"] for t in TEST_CASES[:6]]
        return self.hitl(
            checkpoint_id="test-execution-scope",
            message=f"I generated 27 test functions in tests/test_jp1_booking.py.\n\nHow would you like to run them?",
            options=[
                {"id": "approve", "label": "Run AC1 scope (TC1–TC5, ~2 min)",  "variant": "success"},
                {"id": "all",     "label": "Run full suite (27 tests, ~15 min)", "variant": "default"},
                {"id": "reject",  "label": "Skip — go straight to commit",       "variant": "warning"},
            ],
            context={
                "total_functions": 27,
                "ui_functions": 21,
                "api_functions": 6,
                "sample_tests": fn_list,
                "artifacts": [
                    {"path": "tests/ui/test_jp1_booking.py",      "type": "python", "label": "UI Tests"},
                    {"path": "tests/api/test_api_jp1_booking.py", "type": "python", "label": "API Tests"},
                ],
            },
        )

    def run_stage4_generate(self):
        self.stage_start("generate_tests", "Generating Playwright test scripts...")
        self.log("Creating tests/test_jp1_booking.py...", stage="generate_tests")
        self.sleep(1.0)

        ui_tests = [t for t in TEST_CASES if not t["fn"].startswith("test_api")]
        for t in ui_tests:
            self.log(f"  + {t['fn']}  [{t['type']}]", stage="generate_tests")
            self.sleep(0.25)

        self.sleep(0.5)
        self.log("Creating tests/test_api_jp1_booking.py...", stage="generate_tests")
        self.sleep(0.6)

        api_tests = [t for t in TEST_CASES if t["fn"].startswith("test_api")]
        for t in api_tests:
            self.log(f"  + {t['fn']}  [API]", stage="generate_tests")
            self.sleep(0.2)

        self.sleep(0.5)
        self.log("Verifying test collection: pytest --collect-only...", stage="generate_tests")
        self.sleep(1.2)
        self.log("27 tests collected in 0.17s ✓", "success", stage="generate_tests")
        self.stage_done("generate_tests", "27 test functions generated", {
            "ui_file": "tests/test_jp1_booking.py",
            "api_file": "tests/test_api_jp1_booking.py",
            "total_functions": 27,
            "collected": "27 items",
            "artifacts": [
                {"path": "tests/ui/test_jp1_booking.py",     "type": "python", "label": "UI Tests"},
                {"path": "tests/api/test_api_jp1_booking.py", "type": "python", "label": "API Tests"},
            ],
        })

    def run_stage5_tests(self):
        self.stage_start("run_tests", "Running tests (AC1 scope — TC1 to TC5)...")
        self.log("pytest tests/test_jp1_booking.py -k AC1 -v -p no:xdist --reruns=1", stage="run_tests")
        self.sleep(1.5)
        self.log("Browser: chromium  |  Headless: false  |  Base URL: https://drivejoulez.com", stage="run_tests")
        self.sleep(1.0)

        ac1_tests = [t for t in TEST_CASES if t["ac"] == "AC1"]
        durations = [28.4, 31.2, 19.7, 24.1, 39.6]

        for i, t in enumerate(ac1_tests):
            result = TEST_RESULTS.get(t["fn"], "skip")
            self.sleep(durations[i] * 0.08)
            if result == "pass":
                self.log(f"  PASSED  {t['fn']}  ({durations[i]:.1f}s)", "success", stage="run_tests")
            elif result == "xpass":
                self.log(f"  XPASS   {t['fn']}  — delivery IS visible  ({durations[i]:.1f}s)", "success", stage="run_tests")
            else:
                self.log(f"  FAILED  {t['fn']}", "error", stage="run_tests")

        self.sleep(0.5)
        self.log("5 passed, 0 failed, 22 not run  |  143.0s", "success", stage="run_tests")
        self.stage_done("run_tests", "5 passed · 0 failed · 22 not run", {
            "passed": 5,
            "failed": 0,
            "skipped": 22,
            "duration_s": 143,
            "scope": "AC1 (TC1–TC5)",
            "browser": "chromium",
        })

    def run_hitl_allure(self) -> str:
        choice = self.hitl(
            checkpoint_id="allure-report",
            message="Tests finished: ✅ 5 passed / ❌ 0 failed / ⏭ 22 not run in 143s\n\nWould you like me to generate the Allure report?",
            options=[
                {"id": "approve", "label": "Yes — generate and open Allure",   "variant": "success"},
                {"id": "reject",  "label": "No — skip, proceed to commit",     "variant": "default"},
            ],
            context={
                "passed": 5,
                "failed": 0,
                "skipped": 22,
                "duration": "143s",
                "allure_output": "reports/allure-html",
            },
        )
        if choice == "approve":
            self.log("allure generate reports/allure-results --clean -o reports/allure-html", stage="run_tests")
            self.sleep(2.5)
            self.log("Allure report ready: reports/allure-html/index.html", "success", stage="run_tests")
            # Unlock the Allure Report artifact pill
            send({
                "type": "stage_complete",
                "stage": "run_tests",
                "message": "Allure report generated",
                "level": "success",
                "data": {
                    "artifacts": [
                        {"path": "reports/allure-html", "type": "report", "label": "Allure Report"},
                    ],
                },
            })
        return choice

    def run_stage_generate_allure(self):
        self.stage_start("generate_allure", "Generating Allure HTML report...")
        self.log("allure generate allure-results --clean -o reports/allure-html", stage="generate_allure")
        self.sleep(1.5)
        self.log("Report successfully generated to reports/allure-html/index.html", "success", stage="generate_allure")
        self.stage_done("generate_allure", "Allure report generated", {
            "artifacts": [
                {"path": "reports/allure-html/index.html", "type": "html", "label": "Allure Report"},
            ],
        })

    def run_stage5b_postman(self):
        self.stage_start("postman_export", "Exporting Postman collection...")
        self.log("Building collection from 12 Swagger endpoints...", stage="postman_export")
        self.sleep(1.0)
        self.log("Grouping into folders: AC1 Location, AC3 Search, AC5 Pricing, AC6 Auth", stage="postman_export")
        self.sleep(0.8)
        self.log("Adding test scripts (status code + response schema checks)...", stage="postman_export")
        self.sleep(0.7)
        self.log("Saved: plans/postman_jp-1_2026-05-20.json", stage="postman_export")
        self.sleep(0.5)
        self.log("Uploading to Joulez Postman workspace (bd9bcbaa-d3ab-48ba-...)...", stage="postman_export")
        self.sleep(1.2)
        self.log("Uploaded ✓  Collection ID: c8f2a9b3-...", "success", stage="postman_export")
        self.stage_done("postman_export", "Postman collection uploaded", {
            "requests": 12,
            "folders": 4,
            "local_file": "plans/postman_jp-1_2026-05-20.json",
            "workspace": "Joulez",
            "artifacts": [
                {"path": "plans/postman_jp-1_2026-05-20.json", "type": "json", "label": "Postman Collection"},
            ],
        })

    def run_stage6_commit(self):
        self.stage_start("commit_push", "Committing and pushing...")
        self.log("Branch guard: current = jp-1-pre-payment-booking-flow-v17 ✓", stage="commit_push")
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
        self.log("git add tests/test_jp1_booking.py tests/test_api_jp1_booking.py plans/...", stage="commit_push")
        self.sleep(0.8)
        self.log(f'git commit -m "test(booking): add pre-payment booking flow tests for JP-1"', stage="commit_push")
        self.sleep(1.0)
        self.log(f"Committed: {COMMIT}", "success", stage="commit_push")
        self.sleep(0.5)
        self.log(f"git push -u origin {BRANCH}", stage="commit_push")
        self.sleep(1.2)
        self.log("Pushed ✓", "success", stage="commit_push")
        self.stage_done("commit_push", f"Committed {COMMIT} and pushed", {
            "commit": COMMIT,
            "branch": BRANCH,
            "files_staged": 4,
        })

    def run_stage7_pr(self):
        self.stage_start("raise_pr", "Creating GitHub pull request...")
        self.log(f"mcp__github__create_pull_request(owner=innocito, repo=AI-Test-Workflow, ...)", stage="raise_pr")
        self.sleep(2.0)
        self.log(f"PR #17 created: [{TICKET}] test(booking): add pre-payment booking flow tests", "success", stage="raise_pr")
        self.log(f"URL: {PR_URL}", "success", stage="raise_pr")
        self.log("Draft: false  |  Base: main  |  Coverage delta: 1 → 28 tests (+27)", stage="raise_pr")
        self.stage_done("raise_pr", f"PR #17 raised — {PR_URL}", {
            "pr_number": 17,
            "pr_url": PR_URL,
            "title": f"[{TICKET}] test(booking): add pre-payment booking flow tests",
            "draft": False,
            "tests_added": 27,
            "coverage_before": 1,
            "coverage_after": 28,
            "artifacts": [
                {"path": "plans/run_summary_jp-1_2026-05-20.md", "type": "markdown", "label": "Run Summary"},
            ],
        })

    def run_stage8_jira(self):
        self.stage_start("update_jira", "Updating Jira ticket...")
        self.log(f"jira_add_comment(issue_key=JP-1, body=...)", stage="update_jira")
        self.sleep(1.5)
        self.log("Comment posted with test results table and PR link ✓", "success", stage="update_jira")
        self.sleep(0.5)
        self.log("jira_transition_issue(JP-1 → In Review)...", stage="update_jira")
        self.sleep(0.8)
        self.log("JP-1 transitioned → In Review ✓", "success", stage="update_jira")
        self.stage_done("update_jira", "JP-1 updated and transitioned → In Review", {
            "ticket": TICKET,
            "transition": "In Review",
            "pr_url": PR_URL,
        })

    def run_stage9_review(self):
        self.stage_start("pr_review", "Spawning PR review agent...")
        self.log("Initialising review agent for PR #17...", stage="pr_review")
        self.sleep(1.2)
        self.log("Fetching PR diff: 4 files changed, +312 −2 lines", stage="pr_review")
        self.sleep(1.0)
        self.log("Checking: @allure.step on all public page methods...", stage="pr_review")
        self.sleep(0.8)
        self.log("  ✓ booking_page.py — all 14 methods decorated", "success", stage="pr_review")
        self.log("Checking: no raw integer timeouts...", stage="pr_review")
        self.sleep(0.6)
        self.log("  ✓ settings.UI_PAUSE_* used throughout", "success", stage="pr_review")
        self.log("Checking: test naming convention...", stage="pr_review")
        self.sleep(0.6)
        self.log("  ✓ test_pos_*/test_err_*/test_perm_* — all 27 pass", "success", stage="pr_review")
        self.log("Checking: no hardcoded credentials or URLs...", stage="pr_review")
        self.sleep(0.5)
        self.log("  ✓ BASE_URL from settings, no inline secrets", "success", stage="pr_review")
        self.sleep(0.8)
        self.log("Review decision: APPROVE ✓", "success", stage="pr_review")
        self.log(f"Review posted to GitHub PR #17", "success", stage="pr_review")
        self.stage_done("pr_review", "Review: APPROVE — posted to PR #17", {
            "decision": "APPROVE",
            "pr_url": PR_URL,
            "issues_found": 0,
            "suggestions": 2,
        })

    # -----------------------------------------------------------------------
    # Main
    # -----------------------------------------------------------------------

    def run(self):
        print()
        print("  ╔══════════════════════════════════════════════╗")
        print("  ║  Joulez · E2E Workflow Mock Run              ║")
        print("  ║  JP-1: Pre Payment Booking Flow              ║")
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
        print(f"  ✓ Opening http://localhost:5173")
        print()
        if self.no_hitl:
            print("  ℹ  --no-hitl: HITL checkpoints will auto-approve")
        print()

        send({"type": "workflow_start", "message": f"JP-1 — {SUMMARY}", "data": {
            "ticket": TICKET,
            "summary": SUMMARY,
            "branch": BRANCH,
            "runner": "mock",
        }})

        self.run_stage1_jira()
        self.sleep(1.0)

        self.run_stage2_branch()
        self.sleep(0.8)

        self.run_stage3a_swagger()
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
        choice_api = self.run_hitl_api_scope()
        self.sleep(0.8)

        if choice_api == "approve":
            choice_postman = self.run_hitl_postman_scope()
            self.sleep(0.8)
        else:
            choice_postman = "reject"

        self.run_hitl_naming_preview()
        self.sleep(0.8)

        self.run_stage4_generate()
        self.sleep(1.0)

        choice1b = self.run_hitl1b_scope()
        # Any choice continues (all/approve/reject all proceed to run or skip)
        self.sleep(0.8)

        if choice1b != "reject":
            self.run_stage5_tests()
            self.sleep(0.8)
            choice_allure = self.run_hitl_allure()
            self.sleep(0.8)
            if choice_allure == "approve":
                self.run_stage_generate_allure()
                self.sleep(0.8)

        if choice_postman == "approve":
            self.run_stage5b_postman()
            self.sleep(0.8)

        self.run_stage6_commit()
        self.sleep(0.8)

        self.run_stage7_pr()
        self.sleep(0.8)

        self.run_stage8_jira()
        self.sleep(0.8)

        self.run_stage9_review()

        send({"type": "workflow_complete", "message": "All 9 stages complete — JP-1 ✓", "level": "success", "data": {
            "ticket": TICKET,
            "pr_url": PR_URL,
            "tests_added": 27,
            "verdict": "APPROVE",
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
    parser = argparse.ArgumentParser(description="Mock e2e workflow run for JP-1")
    speed_group = parser.add_mutually_exclusive_group()
    speed_group.add_argument("--fast",    action="store_true", help="3× faster")
    speed_group.add_argument("--instant", action="store_true", help="No delays")
    parser.add_argument("--no-hitl", action="store_true", help="Auto-approve all HITL checkpoints")
    args = parser.parse_args()

    speed = 0 if args.instant else (3.0 if args.fast else 1.0)
    Runner(speed=speed, no_hitl=args.no_hitl).run()
