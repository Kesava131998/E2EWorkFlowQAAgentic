---
name: e2e-workflow
description: Unified Jira-to-PR workflow — fetches a Jira ticket, discovers APIs via Swagger MCP, generates tests with live locator discovery via Playwright MCP, runs tests, commits, raises PR, updates Jira, and spawns a separate review agent
tags: [jira, github, swagger, playwright, workflow, e2e, mcp, orchestration]
---

# Skill: End-to-End Workflow

Runs the full automation lifecycle from a single Jira ticket ID.
**Everything is derived at runtime** — no hardcoded repo names, branches, or paths.

> **MCP Required**: `mcp-atlassian` (Jira) + `@modelcontextprotocol/server-github` (GitHub) + `@playwright/mcp` (Playwright) + `@ivotoby/openapi-mcp-server` (Swagger)
> **Rules**: `agents/rules.md`

---

## Usage

```
/e2e-workflow <TICKET-ID>
```

Example: `/e2e-workflow JP-1`

---

## Runtime Context Resolution

Before any stage runs, resolve all dynamic values once and reuse them throughout:

```bash
# GitHub owner and repo — derived from git remote, never hardcoded
git remote get-url origin
# e.g. https://github.com/innocito/AI-Test-Workflow.git
# → owner = "innocito", repo = "AI-Test-Workflow"
```

Parse owner and repo from the remote URL (supports both HTTPS and SSH formats):
- HTTPS: `https://github.com/<owner>/<repo>.git`
- SSH: `git@github.com:<owner>/<repo>.git`

Store as:
- `$OWNER` — GitHub username/org
- `$REPO` — repository name
- `$TICKET` — the Jira ticket ID argument (e.g. `JP-1`)
- `$BRANCH` — computed in Stage 2
- `$MODULE` — computed in Stage 1 from Jira labels/components
- `$PR_NUMBER` — captured in Stage 8
- `$SWAGGER_ENDPOINTS` — captured in Stage 3a
- `$UI_FLOW` — boolean, true if this is a UI ticket, false if explicit API
- `$INCLUDE_API_TESTS` — boolean, user choice from checkpoint
- `$EXPORT_POSTMAN` — boolean, user choice from checkpoint

---

## Workflow

---

### Stage 0 — MCP Health Check

**Before starting the workflow, verify all required MCP servers are responsive.**

```
# Test Jira MCP
jira_get_issue(issue_key="JP-1")

# Test GitHub MCP
mcp__github__list_pull_requests(owner=$OWNER, repo=$REPO, state="open")

# Test Swagger MCP
mcp__swagger__welcome-using-get()

# Test Playwright MCP
mcp__playwright__browser_navigate(url="https://www.google.com")
```

**If any MCP server fails:**
- 🛑 STOP the workflow
- Report to user: "MCP server <name> is not responding. Please check `.mcp.json` configuration and restart Claude Code."
- Exit gracefully

**If all pass:**
- ✅ Confirm: "All MCP servers healthy — proceeding with workflow."

---

### Stage 1 — Fetch Jira Ticket

```
jira_get_issue(
  issue_key=$TICKET,
  fields="summary,description,labels,components,status,priority,assignee,customfield_10010",
  expand="renderedFields",
  comment_limit=5
)
```

Extract and store:
- **`$TICKET_SUMMARY`** — the issue summary line
- **`$TICKET_DESCRIPTION`** — full description body (use `renderedFields` for HTML-rendered content)
- **`$TICKET_ACS`** — acceptance criteria (look for `Given/When/Then`, `AC1:`, `- [ ]` checkboxes, or sections labeled "Acceptance Criteria")
- **`$MODULE`** — derived from:
  1. Jira `components` field (highest priority)
  2. Jira `labels` field (second priority)
  3. Keywords in summary (e.g. "Diagnostic" → `diagnostics`, "Login" → `login`, "Booking" → `booking`)
- **`$STATUS`**, **`$PRIORITY`**, **`$ASSIGNEE`**

**Determine flow type** (`$UI_FLOW`):
- If summary or description contains "API automation", "automate API", "endpoint", "Swagger", "Postman" → `$UI_FLOW = false` (explicit API ticket)
- Otherwise → `$UI_FLOW = true` (UI flow ticket)

Print a structured summary to the user:
```
🎫 Ticket  : $TICKET
📋 Summary : $TICKET_SUMMARY
🔧 Module  : $MODULE
📊 Status  : $STATUS
🎯 Priority: $PRIORITY
🔍 Flow    : <UI Flow | API Automation>
📝 ACs     : <N> found
```

---

### Stage 2 — Create Git Branch

> **Default branch is `main`.** Always branch from `main`, regardless of what `origin/HEAD` resolves to or what the current branch is.

**`$BRANCH`** is constructed from the ticket at runtime:

```
$BRANCH = slugify($TICKET) + "-" + slugify($TICKET_SUMMARY, max_words=5)
```

Slugify rules:
- Lowercase everything
- Replace spaces and special characters with hyphens
- Strip punctuation
- Truncate to 60 chars total

Examples:
- `JP-1` + "Pre-payment Booking Flow Automation" → `jp-1-pre-payment-booking-flow-automation`
- `SCRUM-42` + "Fix login timeout on slow networks" → `scrum-42-fix-login-timeout-on-slow-networks`

**Branch creation — always run these commands, every time the workflow is triggered:**

```bash
git checkout main
git pull origin main
git checkout -b $BRANCH
```

- **Never reuse an existing ticket branch.** If `$BRANCH` already exists locally or on remote, automatically append a version suffix (`-v2`, `-v3`, …) using the next available number — no prompt needed.
- **Never ask the user** whether to reuse or create — always create a fresh branch.

Confirm the final branch name to the user before proceeding.

Immediately after branch creation, transition the Jira ticket to **In Progress**:
```
jira_transition_issue(issue_key=$TICKET, transition="In Progress")
```
Confirm: `"🔄 Jira ticket $TICKET transitioned → In Progress"`

---

### Stage 3a — Swagger MCP Discovery

**Primary:** Use Swagger MCP tools directly for API discovery.
**Fallback:** If Swagger MCP is unavailable, use the curl approach below.

**Step 1 — Verify Swagger MCP connectivity:**
```
mcp__swagger__welcome-using-get()
```
Should return: `"Application up and running with version: dev_1.0.1158"` (or similar)

**Step 2 — Discover relevant endpoints:**

Since Swagger MCP exposes 250+ individual endpoint tools (one per endpoint), identify which are relevant to this ticket strategically:

1. Extract keywords from `$TICKET_SUMMARY` and `$TICKET_DESCRIPTION`:
   - "booking" → search for `booking`, `crt-booking`, `cancel-booking`
   - "user" → search for `usr`, `get-usr`, `upd-usr`
   - "payment" → search for `payment`, `transaction`, `rental-payment`
   - "location" → search for `location`, `get-all-locations`

2. Use ToolSearch to find relevant Swagger MCP tools — call it as a Claude tool (not bash), e.g.:
   `ToolSearch(query="mcp__swagger__ <module-keyword>", max_results=20)`
   Load the schemas for the top 5–10 most relevant results.

3. Test one simple GET endpoint to verify live API connectivity:
   ```
   # Example for a booking flow:
   mcp__swagger__get-all-locations-using-pst()
   ```

**Fallback (if Swagger MCP unavailable):**
```bash
curl -s "https://beta.drivejoulez.com:8443/joulez-service/v2/api-docs" | \
  python3 -c "
import sys, json
spec = json.load(sys.stdin)
for path, methods in spec.get('paths', {}).items():
    for method in methods:
        if method in ('get','post','put','delete','patch'):
            print(f'{method.upper():6} {path}')
"
```

**Output to user:**
```
🔍 Swagger Discovery Results:
  ✅ API Version: dev_1.0.1158
  ✅ Connectivity: Live
  📡 Relevant Endpoints Found:
     1. POST /booking/create (mcp__swagger__crt-booking-using-pst)
     2. GET  /cars/available (mcp__swagger__get-available-cars-details-using-pst)
     3. GET  /locations      (mcp__swagger__get-all-locations-using-pst)
     4. POST /payment        (mcp__swagger__rental-payment-using-pst)
     ... (<N> total)
```

Store as `$SWAGGER_ENDPOINTS` (list of tool names + descriptions).

---

### Stage 3b — Playwright MCP — Live App Inspection (UI flows only)

**Skip this stage if `$UI_FLOW = false`.**

Use Playwright MCP to navigate to the relevant page and capture the accessibility tree before writing any test cases.

**Prerequisites:**
- App must be accessible at `BASE_URL` (from `.env` or `config/settings.py`)
- Playwright MCP server verified healthy in Stage 0

**Step 1 — Navigate to the target page:**
```
mcp__playwright__browser_navigate(url="<BASE_URL>/<module-path>")
```

**Step 2 — Capture page snapshot:**
```
mcp__playwright__browser_snapshot()
```
Returns the full accessibility tree with all interactive elements.

**Step 3 — Extract stable locators:**

Parse the snapshot and identify:
- Form fields (role=textbox, role=combobox)
- Buttons (role=button, name="...")
- Links (role=link, name="...")
- Error message containers
- Success indicators

Store as `$PAGE_ELEMENTS` (dict of element descriptions → stable locators).

**Step 4 — Take a reference screenshot:**
```
mcp__playwright__browser_take_screenshot(
  type="png",
  fullPage=true,
  filename="plans/$TICKET_lower_reference_screenshot.png"
)
```

**Output to user:**
```
🎭 Playwright MCP — Live UI Inspection:
  ✅ Navigated to: <BASE_URL>/<module-path>
  📸 Reference screenshot: plans/$TICKET_lower_reference_screenshot.png
  🔍 Discovered <N> interactive elements:
     • "Select Pickup Location" → role=combobox[name="Pickup Location"]
     • "Search Cars"           → role=button[name="Search"]
     • "Start Date"            → input[name="startDate"]
     ... (list all)
```

---

### Stage 3c — Derive Manual Test Cases

**Sources:**
1. `$TICKET_DESCRIPTION` and `$TICKET_ACS` from Jira
2. `$SWAGGER_ENDPOINTS` from Stage 3a
3. `$PAGE_ELEMENTS` from Stage 3b (if UI flow)

**Approach:**
- **UI Flow**: Derive test cases from ACs, use actual element names from Playwright MCP snapshot
- **API Ticket**: Derive test cases from ACs, use Swagger endpoint schemas for payloads and response validation

**For each AC or requirement, produce:**

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|----|------|----------|----------|----------------|-----------|-------|-----------------|
| 1 | AC1 | Happy Path | High | … | Navigate to /booking | Valid location "LAX" | 1. Verify dropdown visible<br>2. Click<br>3. Select "LAX" | 1. Visible<br>2. Expands<br>3. "LAX" selected |
| 2 | AC1 | Negative | Medium | … | Navigate to /booking | Non-existent location | 1. Enter invalid<br>2. Click Search | 1. Entered<br>2. Error shown |

**Test Case Quality Rules:**
- **Pre-conditions:** State the required system state before the test (e.g., "Navigate to https://...", auth tokens for API)
- **Test Data:** Specify exact inputs. For API tests, include sample JSON payloads from Swagger schema
- **Extreme Granularity:** Break every flow into micro-interactions. Before interacting with an element, verify it is visible
- **1-to-1 Mapping:** Every step MUST have a corresponding expected result — no exceptions
- **Use live element names**: Reference actual names from Playwright MCP (e.g., "Select Pickup Location", not "dropdown")
- **Use Swagger schemas**: Reference actual field names from Swagger MCP (e.g., `booking_id`, `start_date`, `car_id`)

Generate at minimum:
- One `Happy Path` per AC (High priority)
- `Negative` cases where the AC implies error/validation handling
- `Edge Case` where boundary values or empty states are implied
- `RBAC/Permission` cases to ensure access controls block unauthorized actions
- `API Happy Path` / `API Negative` for each API interaction in the AC (if applicable)

Save to two formats:
```
plans/manual_tests_$TICKET_lower_<YYYY-MM-DD>.md   # Markdown for reading
plans/manual_tests_$TICKET_lower_<YYYY-MM-DD>.csv  # CSV for tracking
```

---

### ⏸ HITL CHECKPOINT 1 — Test Case Review

**STOP. Ask 3 separate questions, one at a time. Wait for a response before asking the next.**

**Question 1 — Test case sign-off:**
> "Here are the **<N> test cases** I derived from **$TICKET: $TICKET_SUMMARY**.
>
> <render the table in markdown>
>
> I used **Swagger MCP** to discover <M> relevant API endpoints and **Playwright MCP** to inspect the live UI (if applicable).
>
> Would you like to add, remove, or modify any cases before I proceed?"

**Wait for user response.** Apply any changes, then continue.

---

**Question 2 — API test generation** *(ask only if `$UI_FLOW = true`):*
> "Since this is a UI flow, I can use **Playwright MCP** to intercept network calls during the UI test run, then cross-reference them with **Swagger MCP** to generate independent API tests.
>
> Would you like me to include API test generation?
> - **[Y] Yes** — generate a separate API test file alongside the UI tests
> - **[N] No** — UI tests only"

**Wait for user response.** Store as `$INCLUDE_API_TESTS` (true/false).

---

**Question 3 — Postman collection export** *(ask only if `$INCLUDE_API_TESTS = true` OR `$UI_FLOW = false`):*
> "Would you like me to export a **Postman-compatible collection** (`.json`) for these endpoints?
> It will be saved to `plans/` and uploaded directly to the Joulez Postman workspace.
> - **[Y] Yes** — export and upload after tests run
> - **[N] No** — skip Postman export"

**Wait for user response.** Store as `$EXPORT_POSTMAN` (true/false).

---

### Stage 3d — Test Naming Preview

**Before writing any files**, present the proposed test function names:

> "Here are the **test function names** I'll generate:
>
> | # | Function Name | Type | AC | Locator / Endpoint |
> |---|--------------|------|----|-------------------|
> | 1 | `test_pos_select_pickup_location` | Happy Path (UI) | AC1 | `role=combobox[name="Pickup Location"]` |
> | 2 | `test_err_invalid_pickup_location` | Negative (UI) | AC1 | `role=combobox[name="Pickup Location"]` |
> | 3 | `test_api_pos_create_booking` | Happy Path (API) | AC2 | POST /booking/create |
> | 4 | `test_api_err_create_booking_missing_fields` | Negative (API) | AC2 | POST /booking/create |
>
> Shall I proceed with these names, or would you like to rename any?"

**Wait for user response.** Apply any renames, then proceed.

Also capture coverage baseline now:
```bash
grep -r "def test_" tests/ --include="*.py" | wc -l
```
Store as `$EXISTING_TEST_COUNT`.

---

### Stage 4 — Generate Playwright Test Scripts

**Check for existing coverage first:**
```bash
grep -r "<keyword from $TICKET_SUMMARY>" tests/ --include="*.py" -l
```
If partial coverage exists, report it and only generate scripts for uncovered cases.

**Output files:**
```
tests/ui/test_$TICKET_lower_$MODULE.py       # UI tests (if UI flow)
tests/api/test_api_$TICKET_lower_$MODULE.py  # API tests (if API or $INCLUDE_API_TESTS = true)
```

**UI Test Template:**
```python
import pytest
import allure
from playwright.sync_api import Page, expect
from pages.<$MODULE>_page import <ModuleClass>
from config.settings import settings


@allure.epic("$TICKET: $TICKET_SUMMARY")
@allure.feature("$MODULE")
@allure.story("AC<N>: <ac text>")
@allure.title("<scenario name>")
def test_pos_<sanitized_scenario>(page: Page):
    """
    Jira: $TICKET
    AC: <full ac text>
    Locators verified via Playwright MCP snapshot on <date>
    """
    module_page = <ModuleClass>(page)

    # Network interception — captures API calls for Stage 5b (if $INCLUDE_API_TESTS = true)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Verify '<element>' is visible"):
        expect(page.locator("<stable-locator-from-mcp>")).to_be_visible(timeout=settings.MEDIUM_TIMEOUT)

    with allure.step("Step 2: <action>"):
        module_page.<method>("<test-data>")

    with allure.step("Step N: Verify <outcome>"):
        expect(page.locator("<result-locator>")).to_have_text("<expected-text>", timeout=settings.SMALL_TIMEOUT)

    if api_calls:
        allure.attach(
            "\n".join([f"{req.method} {req.url}" for req in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )
```

**API Test Template:**
```python
import pytest
import allure
from playwright.sync_api import APIRequestContext


@allure.epic("$TICKET: $TICKET_SUMMARY")
@allure.feature("$MODULE API")
@allure.story("AC<N>: <ac text>")
@allure.title("<scenario name>")
def test_api_pos_<sanitized_scenario>(api_request_context: APIRequestContext):
    """
    Jira: $TICKET
    AC: <full ac text>
    Endpoint: POST /booking/create
    Schema validated via Swagger MCP
    """
    payload = {
        "car_id": "test_car_123",
        "start_date": "2026-05-20T10:00:00Z",
        "end_date": "2026-05-21T10:00:00Z",
        # ... all required fields from Swagger schema
    }

    with allure.step("Step 1: Send POST request to /booking/create"):
        response = api_request_context.post(
            "https://beta.drivejoulez.com:8443/joulez-service/booking/create",
            data=payload
        )

    with allure.step("Step 2: Verify response status is 200"):
        assert response.status == 200, f"Expected 200, got {response.status}"

    with allure.step("Step 3: Verify response schema matches Swagger spec"):
        response_json = response.json()
        assert "booking_id" in response_json, "Response missing booking_id"
        assert "status" in response_json, "Response missing status"

    allure.attach(str(response_json), name="API Response", attachment_type=allure.attachment_type.JSON)
```

**Naming convention:**
- UI Happy Path → `test_pos_<action>`
- UI Negative → `test_err_<action>`
- UI Permission → `test_perm_<action>`
- API Happy Path → `test_api_pos_<action>`
- API Negative → `test_api_err_<action>`

Verify discoverability:
```bash
python -m pytest --collect-only tests/ui/test_$TICKET_lower_$MODULE.py
python -m pytest --collect-only tests/api/test_api_$TICKET_lower_$MODULE.py
```

---

### ⏸ HITL CHECKPOINT 1b — Test Execution Scope

**STOP. List all generated test functions by name, then ask:**

> "I've generated **<N> test functions**:
>
> **UI Tests** (`tests/ui/test_$TICKET_lower_$MODULE.py`):
> <list all UI test function names>
>
> **API Tests** (`tests/api/test_api_$TICKET_lower_$MODULE.py`):
> <list all API test function names>
>
> How would you like to proceed?
> - **[A] All** — run all <N> tests (UI + API)
> - **[U] UI Only** — run only UI tests
> - **[P] API Only** — run only API tests
> - **[S] Selected** — tell me which tests to run (by name or number)
> - **[K] Skip** — skip execution and go straight to commit"

**Wait for user response.**
- **All** → `$TEST_FILTER = tests/ui/test_$TICKET_lower_$MODULE.py tests/api/test_api_$TICKET_lower_$MODULE.py`
- **UI Only** → `$TEST_FILTER = tests/ui/test_$TICKET_lower_$MODULE.py`
- **API Only** → `$TEST_FILTER = tests/api/test_api_$TICKET_lower_$MODULE.py`
- **Selected** → `$TEST_FILTER = -k "<user-specified names>"`
- **Skip** → `$SKIP_RUN = true`, jump to Stage 5c / Stage 6

---

### Stage 5 — Run Tests with Live MCP Debugging

**Skip this stage if `$SKIP_RUN = true`.**

```bash
python -m pytest $TEST_FILTER -v --reruns=1 --reruns-delay=2 --alluredir=reports/allure-results
```

**Retry behaviour**: `--reruns=1` retries each failing test once before marking it failed, filtering transient flakiness.

**On failure — automatically use MCP to diagnose:**

**For UI test failures:**
1. Navigate to the failure point: `mcp__playwright__browser_navigate(url="<BASE_URL>/<page>")`
2. Take a screenshot: `mcp__playwright__browser_take_screenshot(filename="plans/$TICKET_lower_failure_<test>.png")`
3. Capture current snapshot: `mcp__playwright__browser_snapshot()` — compare with Stage 3b reference
4. Check console errors: `mcp__playwright__browser_console_messages()`
5. Report:
   ```
   ⚠️ Test `<test_name>` failed.
   🔍 Playwright MCP Diagnosis:
   • Locator: <locator used>
   • Page state: <element not found / stale / hidden>
   • Console errors: <list JS errors>
   • Suggested fix: <update locator / check auth / wait for element>
   ```

**For API test failures:**
1. Call the endpoint directly via Swagger MCP: `mcp__swagger__<endpoint-tool>(<params>)`
2. Compare expected schema vs actual response and highlight differences
3. Report:
   ```
   ⚠️ Test `<test_name>` failed.
   🔍 Swagger MCP Diagnosis:
   • Endpoint: <method> <path>
   • Expected: <status> / <fields>
   • Actual: <status> / <response body>
   • Suggested fix: <payload fix / auth token / field name correction>
   ```

Parse and display: passed / failed / skipped / errors, time taken.

Collect failure artifacts:
```bash
find reports/screenshots/ -newer reports/allure-results -name "*.png" 2>/dev/null
find reports/videos/ -newer reports/allure-results -name "*.webm" -o -name "*.mp4" 2>/dev/null
```
Store as `$FAILURE_SCREENSHOTS` and `$FAILURE_VIDEOS`.

Open Allure report:
```bash
allure serve reports/allure-results
```

---

### Stage 5b — API Tests from Intercepted Network Calls (if `$INCLUDE_API_TESTS = true` and UI tests ran)

**Step 1 — Parse intercepted API calls from Allure result files:**

Read the Allure JSON result files directly and extract attachments named "Intercepted API Calls":
```python
import os, json

intercepted = []
results_dir = "reports/allure-results"
for fname in os.listdir(results_dir):
    if not fname.endswith("-result.json"):
        continue
    with open(os.path.join(results_dir, fname)) as f:
        result = json.load(f)
    for att in result.get("attachments", []):
        if att.get("name") == "Intercepted API Calls":
            att_path = os.path.join(results_dir, att["source"])
            if os.path.exists(att_path):
                with open(att_path) as af:
                    intercepted.extend(af.read().splitlines())
print("\n".join(set(intercepted)))
```

Store unique entries as `$INTERCEPTED_CALLS` (list of `METHOD URL` strings).

**Step 2 — Match to Swagger MCP tools:**

For each intercepted call, use ToolSearch as a Claude tool to find the corresponding Swagger MCP endpoint:
- `POST /booking/create` → `mcp__swagger__crt-booking-using-pst`
- `GET /locations` → `mcp__swagger__get-all-locations-using-pst`

Load the schema for each matched tool.

**Step 3 — Generate API tests** following the API test template from Stage 4.

**Step 4 — Report:**
```
🔗 Network Interception Results:
  ✅ Intercepted <N> unique API calls during UI test run
  ✅ Matched <M> to Swagger MCP endpoints
  ✅ Generated <M> API tests in tests/api/test_api_$TICKET_lower_$MODULE.py
```

---

### Stage 5c — Export Postman Collection (if `$EXPORT_POSTMAN = true`)

Build a Postman Collection v2.1 JSON from:
1. Endpoints in `$SWAGGER_ENDPOINTS` (Stage 3a)
2. Intercepted calls from Stage 5b (if applicable)

**Rules:**
- One request per test case (Happy Path, Negative, RBAC)
- Group into folders by AC
- Payloads from Swagger MCP schema — not manually crafted
- Add Postman test scripts for status code and key response fields
- Use `{{base_url}}` variable for environment-agnostic collections

**Output & Upload:**
```bash
# Save locally
plans/postman_$TICKET_lower_<YYYY-MM-DD>.json

# Wrap and upload to Joulez workspace
jq '{collection: .}' plans/postman_$TICKET_lower_<YYYY-MM-DD>.json > plans/postman_payload.json
curl --silent --location 'https://api.getpostman.com/collections?workspace=bd9bcbaa-d3ab-48ba-9757-38a6a6404d54' \
  --header 'X-API-Key: PMAK-REDACTED-ROTATE-THIS-KEY' \
  --header 'Content-Type: application/json' \
  --data "@plans/postman_payload.json"
rm plans/postman_payload.json
```

Confirm: `"✅ Postman collection exported and uploaded to the Joulez workspace!"`

---

### ⏸ HITL CHECKPOINT 2 — Test Failure Gate

**If any tests FAILED:**

> "⚠️ **<N> test(s) failed:**
>
> <list failures with MCP diagnoses>
>
> How would you like to proceed?
> - **[C] Continue** — commit and raise PR as draft (failures visible in PR)
> - **[F] Fix** — I'll diagnose and fix failures before committing
> - **[I] Investigate** — use Playwright MCP to interactively debug with you"

- **Fix** → invoke `debug-test` skill per failing test, re-run Stage 5
- **Continue** → `$DRAFT = true`
- **Investigate** → open interactive Playwright MCP session for live inspection

If all tests passed → `$DRAFT = false`, proceed automatically.

---

### Stage 6 — Commit and Push

**Pre-commit checks** (from `agents/rules.md`) — block on any violation:
- [ ] No `print()` statements in page objects or tests
- [ ] No raw integer timeouts — must use `settings.*_TIMEOUT`
- [ ] All new page methods have `@allure.step(...)`
- [ ] Test function names follow naming convention (`test_pos_` / `test_err_` / `test_perm_` / `test_api_pos_` / `test_api_err_`)
- [ ] No hardcoded credentials or URLs
- [ ] All UI test locators sourced from Playwright MCP snapshots (date in docstring)
- [ ] All API test payloads validated against Swagger MCP schemas (endpoint in docstring)

Stage files:
```bash
git add tests/ui/test_$TICKET_lower_$MODULE.py
git add tests/api/test_api_$TICKET_lower_$MODULE.py
git add plans/manual_tests_$TICKET_lower_*.md
git add plans/manual_tests_$TICKET_lower_*.csv
git add plans/postman_$TICKET_lower_*.json              # only if $EXPORT_POSTMAN = true
git add plans/$TICKET_lower_reference_screenshot.png    # Playwright MCP reference (if UI flow)
git add plans/$TICKET_lower_failure_*.png               # failure screenshots (if any)
git add plans/run_summary_$TICKET_lower_*.md
# add any page objects created or modified during this session
```

Commit message:
```
test($MODULE): add automation tests for $TICKET

Covers <N> ACs from $TICKET: $TICKET_SUMMARY
- <M> UI tests (locators from Playwright MCP, <YYYY-MM-DD>)
- <K> API tests (schemas from Swagger MCP)
- Postman collection exported (if applicable)

Refs: $TICKET
```

Push:
```bash
git push -u origin $BRANCH
```

---

### Stage 7 — Count Coverage Delta

```bash
NEW_UI_TESTS=$(grep -c "^def test_" tests/ui/test_$TICKET_lower_$MODULE.py 2>/dev/null || echo 0)
NEW_API_TESTS=$(grep -c "^def test_api_" tests/api/test_api_$TICKET_lower_$MODULE.py 2>/dev/null || echo 0)
TOTAL_TESTS_AFTER=$(grep -r "def test_" tests/ --include="*.py" | wc -l)
COVERAGE_DELTA=$((TOTAL_TESTS_AFTER - EXISTING_TEST_COUNT))
```

Store as `$COVERAGE_DELTA`, `$NEW_UI_TESTS`, `$NEW_API_TESTS`.

---

### Stage 8 — Raise Pull Request

**PR title:**
```
[$TICKET] test($MODULE): <concise description from $TICKET_SUMMARY>
```

**PR body:**
```markdown
## 🎫 [$TICKET] $TICKET_SUMMARY
> Jira: https://innocito.atlassian.net/browse/$TICKET

## 📋 Test Coverage

### UI Tests (`tests/ui/test_$TICKET_lower_$MODULE.py`)
| AC | Test Function | Type | Locator Source | Status |
|----|--------------|------|----------------|--------|
| AC1 | `test_pos_...` | Happy Path | Playwright MCP (<date>) | ✅ Passed |
| AC1 | `test_err_...` | Negative | Playwright MCP (<date>) | ✅ Passed |

### API Tests (`tests/api/test_api_$TICKET_lower_$MODULE.py`)
| AC | Test Function | Type | Endpoint | Schema Source | Status |
|----|--------------|------|----------|---------------|--------|
| AC2 | `test_api_pos_...` | Happy Path | POST /booking/create | Swagger MCP | ✅ Passed |
| AC2 | `test_api_err_...` | Negative | POST /booking/create | Swagger MCP | ✅ Passed |

**Coverage delta:** $EXISTING_TEST_COUNT → $TOTAL_TESTS_AFTER tests (+$COVERAGE_DELTA: +$NEW_UI_TESTS UI, +$NEW_API_TESTS API)

## 🧪 Test Results
- ✅ Passed: <N>  ❌ Failed: <M>  ⏭️ Skipped: <K>
- Run time: <T>s

<if failures exist>
## ⚠️ Failures
| Test | Error | MCP Diagnosis |
|------|-------|---------------|
| `test_err_...` | AssertionError: expected 400 got 200 | Swagger MCP: endpoint returns 200 for this input — expectation incorrect |

**Artifacts:** <list $FAILURE_SCREENSHOTS paths>
</if>

<if $EXPORT_POSTMAN = true>
## 📦 Postman Collection
✅ Exported and uploaded to Joulez Postman workspace: `plans/postman_$TICKET_lower_<date>.json`
</if>

## 🚀 Run Locally
\`\`\`bash
pip install -r requirements.txt
playwright install --with-deps
python -m pytest tests/ui/test_$TICKET_lower_$MODULE.py -v
python -m pytest tests/api/test_api_$TICKET_lower_$MODULE.py -v
allure serve reports/allure-results
\`\`\`

## 🔗 Related
- Jira: [$TICKET](https://innocito.atlassian.net/browse/$TICKET)
- Swagger: https://beta.drivejoulez.com:8443/joulez-service/swagger-ui.html
- Reference screenshot: `plans/$TICKET_lower_reference_screenshot.png`
```

```
mcp__github__create_pull_request(
  owner=$OWNER,
  repo=$REPO,
  title="[$TICKET] test($MODULE): <description>",
  head=$BRANCH,
  base="main",
  body=<rendered body>,
  draft=$DRAFT
)
```

Capture `$PR_NUMBER` from the response. Display PR URL to the user.

---

### Stage 9 — Update Jira Ticket

```
jira_add_comment(
  issue_key=$TICKET,
  body="""
✅ *Automation PR raised:* <PR URL>
*Branch:* $BRANCH
*Status:* <All passing ✅ | Draft — <N> failures ⚠️>

----
*🎭 Playwright MCP*
• Live UI inspection: ✅ | Locators verified: <YYYY-MM-DD>
• Reference screenshot: plans/$TICKET_lower_reference_screenshot.png

*🔗 Swagger MCP*
• API schema validated: ✅ | Endpoints discovered: <M>
• API tests generated: <K> | Postman exported: <Yes ✅ | No ⏭️>

----
*Test Results*
|| AC || Test Function || Type || Source || Result ||
| AC1 | test_pos_... | UI Happy Path | Playwright MCP | ✅ Passed |
| AC1 | test_err_... | UI Negative | Playwright MCP | ✅ Passed |
| AC2 | test_api_pos_... | API Happy Path | Swagger MCP | ✅ Passed |
| AC2 | test_api_err_... | API Negative | Swagger MCP | ✅ Passed |

*Coverage:* $EXISTING_TEST_COUNT → $TOTAL_TESTS_AFTER (+$COVERAGE_DELTA: $NEW_UI_TESTS UI + $NEW_API_TESTS API)
*Run time:* <T>s
"""
)
```

Transition the ticket to **In Review**:
```
jira_transition_issue(issue_key=$TICKET, transition="In Review")
```

Confirm: `"✅ Jira $TICKET updated with test results and transitioned → In Review"`

---

### Stage 10 — PR Review Agent

> "Handing off PR #$PR_NUMBER to a dedicated review agent…"

Spawn the `review-pr` skill as a **separate sequential agent**. Pass it `$PR_NUMBER`, `$OWNER`, `$REPO`.

The review agent independently:
1. Fetches PR files and diff via GitHub MCP
2. Analyses against `agents/rules.md`
3. Validates that UI test locators reference Playwright MCP in docstrings
4. Validates that API test payloads reference Swagger MCP schema in docstrings
5. Posts a structured review (`APPROVE` / `REQUEST_CHANGES` / `COMMENT`)

Surface to the user: review decision, key findings, link to posted review, recommended next step.

---

## Final Status Summary

Save and display:
```
plans/run_summary_$TICKET_lower_<YYYY-MM-DD>.md
```

```markdown
# Run Summary — $TICKET: $TICKET_SUMMARY
Date  : <YYYY-MM-DD>
Repo  : $OWNER/$REPO
Branch: $BRANCH
PR    : <PR URL>
Jira  : https://innocito.atlassian.net/browse/$TICKET

## MCP Integration
| Server | Status | Purpose |
|--------|--------|---------|
| Jira | ✅ | Ticket fetch, transitions, comments |
| GitHub | ✅ | Branch, PR creation, review |
| Playwright | ✅ | Live UI inspection, locator discovery, failure debugging |
| Swagger | ✅ | API schema validation, endpoint discovery, payload generation |

## Stage Results
| Stage | Status | Output |
|-------|--------|--------|
| MCP Health Check | ✅ | All 4 servers healthy |
| Jira Fetch | ✅ | $TICKET: <summary> |
| Branch | ✅ | $BRANCH |
| Swagger Discovery | ✅ | <N> endpoints |
| Playwright UI Inspection | ✅/⏭️ | <M> elements, reference screenshot |
| Test Cases | ✅ | <K> cases → plans/manual_tests_*.md & .csv |
| Scripts | ✅ | tests/ui/ + tests/api/ |
| Test Run | ✅/⚠️ | <N> passed / <M> failed |
| MCP Failure Diagnosis | ✅/⏭️ | <L> failures diagnosed |
| Postman Export | ✅/⏭️ | plans/postman_*.json (or skipped) |
| Commit + Push | ✅ | <commit hash> |
| PR | ✅ | <PR URL> (draft: yes/no) |
| Jira Updated | ✅ | → In Review |
| PR Review | ✅ | APPROVE / REQUEST_CHANGES |

## Coverage Delta
Before: $EXISTING_TEST_COUNT | After: $TOTAL_TESTS_AFTER | Added: +$COVERAGE_DELTA ($NEW_UI_TESTS UI + $NEW_API_TESTS API)
```

Confirm: `"📄 Run summary saved to plans/run_summary_$TICKET_lower_<date>.md"`

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Any MCP server not responding (Stage 0) | 🛑 STOP — prompt user to check `.mcp.json` and restart Claude Code |
| Jira ticket not found | Stop — ask user to verify `$TICKET` |
| `git remote` not set | Stop — ask user to configure remote origin |
| Branch already exists | Auto-append next available version suffix (`-v2`, `-v3`, …) — never prompt |
| No ACs parseable from Jira | Show raw description, ask user to define test scope |
| `$MODULE` cannot be inferred | Ask user: "Which module does this ticket belong to?" |
| Page object missing for `$MODULE` | Run `write-page-object` skill (with Playwright MCP), resume from Stage 4 |
| Playwright MCP snapshot returns no elements | Warn: "Page may be behind auth or not loaded. Falling back to manual locator definition." |
| Swagger MCP returns 403/401 | Note: "Auth required. Include token in API test fixtures." |
| Swagger MCP unavailable | Fall back to curl discovery (Stage 3a fallback) |
| Tests still failing after MCP diagnosis | Raise as draft, include diagnosis in PR body and Jira comment |
| GitHub MCP not authenticated | Stop — prompt user to check `.mcp.json` |
