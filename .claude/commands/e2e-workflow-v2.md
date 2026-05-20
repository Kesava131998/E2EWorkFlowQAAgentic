---
name: e2e-workflow-v2
description: Enhanced Jira-to-PR workflow with Playwright and Swagger MCP integration — fetches ticket, discovers APIs via Swagger MCP, generates tests with live locator discovery via Playwright MCP, runs tests, commits, raises PR, updates Jira
tags: [jira, github, swagger, playwright, workflow, e2e, mcp, orchestration]
---

# Skill: End-to-End Workflow V2 (MCP-Enhanced)

Runs the full automation lifecycle from a single Jira ticket ID with **systematic Playwright MCP and Swagger MCP integration** for superior test quality and API coverage.

> **MCP Required**: `mcp-atlassian` (Jira) + `@modelcontextprotocol/server-github` (GitHub) + `@playwright/mcp` (Playwright) + `@ivotoby/openapi-mcp-server` (Swagger)  
> **Rules**: `agents/rules.md`  
> **Version**: 2.0 — MCP-Enhanced Edition

---

## Key Enhancements Over V1

| Feature | V1 (Bash/curl) | V2 (MCP-Enhanced) |
|---------|----------------|-------------------|
| **API Discovery** | curl + jq manual parsing | ✅ Direct Swagger MCP tool calls |
| **Locator Discovery** | Manual guessing | ✅ Live Playwright MCP snapshots |
| **API Validation** | Manual curl requests | ✅ Swagger schema validation via MCP |
| **Test Debugging** | Log-based, manual | ✅ Interactive Playwright MCP inspection |
| **API Test Generation** | Manual requests.post() | ✅ Schema-driven via Swagger MCP |
| **Network Analysis** | Browser DevTools export | ✅ Real-time via Playwright MCP |

---

## Usage

```
/e2e-workflow-v2 <TICKET-ID>
```

Example: `/e2e-workflow-v2 JP-1`

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
jira_get_issue(issue_key="TEST-1")  # Any known ticket, just to verify connectivity

# Test GitHub MCP
github_list_pull_requests(owner=$OWNER, repo=$REPO, state="open")  # Should return list

# Test Swagger MCP
mcp__swagger__welcome-using-get()  # Should return API version

# Test Playwright MCP
mcp__playwright__browser_navigate(url="https://www.google.com")  # Should succeed
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
🎫 Ticket : $TICKET
📋 Summary: $TICKET_SUMMARY
🔧 Module : $MODULE
📊 Status : $STATUS
🎯 Priority: $PRIORITY
🔍 Flow Type: <UI Flow | API Automation>
📝 ACs found: <N>
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

### Stage 3a — Swagger MCP Discovery (Replaces curl-based discovery)

**Previous V1 approach:** Used `curl` + `jq` to parse Swagger spec manually.  
**V2 enhancement:** Use Swagger MCP tools directly for robust API discovery.

**Step 1 — Verify Swagger MCP connectivity:**
```
mcp__swagger__welcome-using-get()
```
Should return: `"Application up and running with version: dev_1.0.1158"` (or similar)

**Step 2 — Discover relevant endpoints:**

Since Swagger MCP exposes **250+ individual endpoint tools** (one per endpoint), we need to strategically identify which endpoints are relevant to this ticket.

**Strategy:**
1. Extract keywords from `$TICKET_SUMMARY` and `$TICKET_DESCRIPTION`:
   - "booking" → search for `booking`, `crt-booking`, `cancel-booking`
   - "user" → search for `usr`, `get-usr`, `upd-usr`
   - "payment" → search for `payment`, `transaction`, `rental-payment`
   - "location" → search for `location`, `get-all-locations`
   
2. **List all available Swagger MCP tools** matching those keywords:
   ```bash
   # Use ToolSearch to find Swagger tools matching the module
   ToolSearch(query="mcp__swagger__*$MODULE*", max_results=20)
   ```

3. **Load the schemas** for the top 5-10 most relevant endpoint tools and store them.

**Step 3 — Test a sample endpoint for connectivity:**

Pick one simple GET endpoint related to the module and call it to verify the Swagger MCP can reach the live API:

```
# Example: For a booking flow
mcp__swagger__get-all-locations-using-pst()
```

If this succeeds, store the response shape for later test generation.

**Output to user:**
```
🔍 Swagger Discovery Results:
  ✅ API Version: dev_1.0.1158
  ✅ Connectivity: Live
  📡 Relevant Endpoints Found:
     1. POST /booking/create (mcp__swagger__crt-booking-using-pst)
     2. GET /cars/available (mcp__swagger__get-available-cars-details-using-pst)
     3. GET /locations (mcp__swagger__get-all-locations-using-pst)
     4. POST /payment (mcp__swagger__rental-payment-using-pst)
     ... (<N> total)
```

Store as `$SWAGGER_ENDPOINTS` (list of tool names + descriptions).

---

### Stage 3b — Playwright MCP — Live App Inspection (for UI flows only)

**Skip this stage if `$UI_FLOW = false` (explicit API ticket).**

**For UI flow tickets**, use Playwright MCP to navigate to the relevant page and capture the accessibility tree to inform test case derivation.

**Prerequisites:**
- App must be accessible at `BASE_URL` (from `.env` or `config/settings.py`)
- Playwright MCP server must be running (verified in Stage 0)

**Step 1 — Navigate to the target page:**
```
mcp__playwright__browser_navigate(url="<BASE_URL>/<module-path>")
```

Example: For a booking flow, navigate to `/booking` or `/cars`.

**Step 2 — Capture page snapshot:**
```
mcp__playwright__browser_snapshot()
```

This returns the accessibility tree with all interactive elements visible on the page.

**Step 3 — Extract stable locators for key elements:**

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

This gives the user and future reviewers a visual reference for the UI state at the time of test generation.

**Output to user:**
```
🎭 Playwright MCP — Live UI Inspection:
  ✅ Navigated to: <BASE_URL>/<module-path>
  📸 Reference screenshot saved: plans/$TICKET_lower_reference_screenshot.png
  🔍 Discovered <N> interactive elements:
     • "Select Pickup Location" → role=combobox[name="Pickup Location"]
     • "Search Cars" → role=button[name="Search"]
     • "Start Date" → input[name="startDate"]
     ... (list all)
```

---

### Stage 3c — Derive Manual Test Cases from Jira + Live Context

**Source**: 
1. `$TICKET_DESCRIPTION` and `$TICKET_ACS` from Jira
2. `$SWAGGER_ENDPOINTS` from Swagger MCP discovery
3. `$PAGE_ELEMENTS` from Playwright MCP snapshot (if UI flow)

**Approach**:
- **UI Flow Ticket**: Derive UI test cases from Jira ACs, enriched with actual element names from Playwright MCP snapshot
- **API Ticket**: Derive API test cases from Jira ACs, using Swagger endpoint schemas for accurate payloads and response validation

**For each AC or requirement found, produce:**

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|----|------|----------|----------|----------------|-----------|-------|-----------------|
| 1 | AC1 | Happy Path | High | User selects pickup location | Navigate to /booking | Valid location "LAX" | 1. Verify "Select Pickup Location" dropdown is visible<br>2. Click dropdown<br>3. Select "LAX" | 1. Dropdown is visible<br>2. Dropdown expands<br>3. "LAX" is selected and displayed |
| 2 | AC1 | Negative | Medium | Invalid location selection | Navigate to /booking | Non-existent location | 1. Enter invalid location<br>2. Click Search | 1. Location entered<br>2. Error "Location not found" shown |
| 3 | AC2 | API Happy Path | High | Create booking via API | Valid auth token | Valid booking payload | 1. Call POST /booking/create with valid data<br>2. Verify response status<br>3. Verify booking ID returned | 1. Request sent<br>2. Status 200<br>3. booking_id present in response |

**Instructions for Test Case Quality:**
- **Pre-conditions:** Clearly state the required system state before the test starts (e.g., "Navigate to https://...", specific user roles, auth tokens for API).
- **Test Data:** Specify exact inputs needed to run the test. For API tests, include sample JSON payloads from Swagger schema.
- **Extreme Granularity:** Do not summarize steps. Break down every flow into micro-interactions. Before interacting with an element, explicitly include a step to verify it is visible and accessible.
- **1-to-1 Mapping:** The "Steps" and "Expected Result" columns must have a strict 1-to-1 mapping. Every single numbered step MUST have a corresponding numbered expected result.
- **Use live element names**: For UI tests, reference the actual element names discovered by Playwright MCP (e.g., "Select Pickup Location" not just "dropdown").
- **Use Swagger schemas**: For API tests, reference the actual request/response field names from Swagger MCP (e.g., `booking_id`, `start_date`, `car_id`).

Generate at minimum:
- One `Happy Path` per AC (High priority)
- `Negative` cases where the AC implies error/validation handling
- `Edge Case` where boundary values or empty states are implied
- `RBAC/Permission` cases to ensure access controls block unauthorized actions
- `API Happy Path` / `API Negative` for each API interaction mentioned in the AC (if applicable)

Save the output to two formats:
1. **Markdown file** for easy reading:
```
plans/manual_tests_$TICKET_lower_<YYYY-MM-DD>.md
```
2. **CSV file** (Excel compatible) for tracking:
```
plans/manual_tests_$TICKET_lower_<YYYY-MM-DD>.csv
```
Ensure the CSV is properly formatted with commas and appropriate quoting for text fields.

---

### ⏸ HITL CHECKPOINT 1 — Test Case Review

**STOP. Present the derived test cases to the user and ask 3 separate questions, one at a time. Wait for a response before asking the next.**

**Question 1 — Test case sign-off:**
> "Here are the **<N> test cases** I derived from **$TICKET: $TICKET_SUMMARY**.
>
> <render the table in markdown>
>
> I used **Swagger MCP** to discover <M> relevant API endpoints and **Playwright MCP** to inspect the live UI (if applicable).
>
> Would you like to add, remove, or modify any cases before I proceed?"

**Wait for user response.** Apply any requested changes, then continue.

---

**Question 2 — API test generation** *(ask only if `$UI_FLOW = true`; skip if explicit API ticket — API tests are already in scope):*
> "Since this is a UI flow, I can use **Playwright MCP** to intercept network calls during the UI test run to capture the underlying API calls, then cross-reference them with **Swagger MCP** to generate independent API tests.
>
> Would you like me to include API test generation?
> - **[Y] Yes** — generate a separate API test file alongside the UI tests
> - **[N] No** — UI tests only"

**Wait for user response.** Store as `$INCLUDE_API_TESTS` (true/false).

---

**Question 3 — Postman collection export** *(ask only if `$INCLUDE_API_TESTS = true` OR if `$UI_FLOW = false`):*
> "Would you also like me to export a **Postman-compatible collection** (`.json`) for these endpoints? 
> 
> I'll use **Swagger MCP** to generate accurate payloads and examples. The collection will be saved to `plans/` and uploaded directly to the Joulez Postman workspace.
> 
> - **[Y] Yes** — export and upload Postman collection after tests run
> - **[N] No** — skip Postman export"

**Wait for user response.** Store as `$EXPORT_POSTMAN` (true/false).

---

After all three questions are answered, proceed to Stage 3d.

---

### Stage 3d — Test Naming Preview

**Before writing any files**, derive the proposed test function names from the approved test cases and present them:

> "Here are the **test function names** I'll generate:
>
> | # | Function Name | Type | AC | Locator/Endpoint |
> |---|--------------|------|----|------------------|
> | 1 | `test_pos_select_pickup_location` | Happy Path (UI) | AC1 | `role=combobox[name="Pickup Location"]` |
> | 2 | `test_err_invalid_pickup_location` | Negative (UI) | AC1 | `role=combobox[name="Pickup Location"]` |
> | 3 | `test_api_pos_create_booking` | Happy Path (API) | AC2 | POST /booking/create |
> | 4 | `test_api_err_create_booking_missing_fields` | Negative (API) | AC2 | POST /booking/create |
> | … | … | … | … | … |
>
> All locators are sourced from **Playwright MCP live inspection**. All API payloads are validated against **Swagger MCP schemas**.
>
> Shall I proceed with these names, or would you like to rename any?"

**Wait for user response.** Apply any renames, then proceed to Stage 4.

Also capture coverage baseline now:
```bash
find tests/ -name "*.py" | xargs grep -l "def test_" | wc -l
grep -r "def test_" tests/ --include="*.py" | wc -l
```
Store as `$EXISTING_TEST_COUNT`.

---

### Stage 4 — Generate Playwright Test Scripts (MCP-Enhanced)

**UI Test Generation (if `$UI_FLOW = true`):**

For each UI test case, generate a Playwright Python test that uses:
- **Locators from Playwright MCP snapshot** (stored in `$PAGE_ELEMENTS`)
- **Network interception** to capture API calls made by the UI (for later API test generation if `$INCLUDE_API_TESTS = true`)

**Template:**
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
    
    # Network interception (if $INCLUDE_API_TESTS = true)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/api/" in req.url else None)
    
    with allure.step("Step 1: Verify '<element>' is visible"):
        # Use locator from $PAGE_ELEMENTS
        expect(page.locator("<stable-locator-from-mcp>")).to_be_visible(timeout=settings.MEDIUM_TIMEOUT)
    
    with allure.step("Step 2: <action>"):
        module_page.<method>("<test-data>")
    
    with allure.step("Step N: Verify <outcome>"):
        # Assert expected result
        expect(page.locator("<result-locator>")).to_have_text("<expected-text>", timeout=settings.SMALL_TIMEOUT)
    
    # Save intercepted API calls for later API test generation
    if api_calls:
        allure.attach(
            "\n".join([f"{req.method} {req.url}" for req in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )
```

**API Test Generation (if `$UI_FLOW = false` OR `$INCLUDE_API_TESTS = true`):**

For each API test case, generate a Playwright API test using `APIRequestContext` with payloads and schemas from Swagger MCP:

**Template:**
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
    # Payload from Swagger MCP schema
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
        # ... validate all required fields from Swagger schema
    
    allure.attach(
        str(response_json),
        name="API Response",
        attachment_type=allure.attachment_type.JSON
    )
```

**Key Enhancements Over V1:**
- ✅ All locators come from **live Playwright MCP snapshot**, not manual guessing
- ✅ API payloads are **schema-validated** against Swagger MCP, not manually constructed
- ✅ Network interception captures real API calls for cross-validation
- ✅ Each test includes MCP-sourced locator/endpoint in docstring for traceability

**Output files** (derived at runtime):
```
tests/ui/test_$TICKET_lower_$MODULE.py       # UI tests (if UI flow)
tests/api/test_api_$TICKET_lower_$MODULE.py  # API tests (if API or $INCLUDE_API_TESTS = true)
```

Verify discoverability:
```bash
python -m pytest --collect-only tests/ui/test_$TICKET_lower_$MODULE.py
python -m pytest --collect-only tests/api/test_api_$TICKET_lower_$MODULE.py
```

---

### ⏸ HITL CHECKPOINT 1b — Test Execution Scope

**STOP. Before running any tests, ask the user what to execute.**

List all generated test functions by name, then ask:

> "I've generated **<N> test functions** across UI and API test files:
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
> - **[K] Skip** — skip execution for now and go straight to commit"

**Wait for user response.**
- **All** → set `$TEST_FILTER = tests/ui/test_$TICKET_lower_$MODULE.py tests/api/test_api_$TICKET_lower_$MODULE.py`
- **UI Only** → set `$TEST_FILTER = tests/ui/test_$TICKET_lower_$MODULE.py`
- **API Only** → set `$TEST_FILTER = tests/api/test_api_$TICKET_lower_$MODULE.py`
- **Selected** → set `$TEST_FILTER = -k "<user-specified names>"` within the relevant test file
- **Skip** → set `$SKIP_RUN = true`, jump directly to Stage 5c / Stage 6

---

### Stage 5 — Run Tests with Live Playwright MCP Debugging

**Skip this stage if `$SKIP_RUN = true`.**

```bash
python -m pytest $TEST_FILTER -v --reruns=1 --reruns-delay=2 --alluredir=reports/allure-results
```

**Retry behaviour**: `--reruns=1` silently retries each failing test once before marking it failed. This filters out transient flakiness.

**Live debugging on failure** (NEW in V2):

If any test fails after retry, **automatically** use Playwright MCP to diagnose:

**For UI test failures:**
1. **Navigate to the failure point:**
   ```
   mcp__playwright__browser_navigate(url="<BASE_URL>/<page-where-test-failed>")
   ```

2. **Take a screenshot:**
   ```
   mcp__playwright__browser_take_screenshot(
     type="png",
     filename="plans/$TICKET_lower_failure_<test_name>.png"
   )
   ```

3. **Capture current page snapshot:**
   ```
   mcp__playwright__browser_snapshot()
   ```
   Compare with the original snapshot from Stage 3b to identify what changed.

4. **Check console errors:**
   ```
   mcp__playwright__browser_console_messages()
   ```

5. **Report diagnosis to user:**
   ```
   ⚠️ Test `test_pos_select_pickup_location` failed.
   
   🔍 Playwright MCP Diagnosis:
   • Element locator: role=combobox[name="Pickup Location"]
   • Current page state: Element not found (screenshot attached)
   • Console errors: <list any JS errors>
   • Possible cause: Locator changed or page structure modified
   
   Suggested fix: Update locator in pages/$MODULE_page.py
   ```

**For API test failures:**
1. **Call the failing endpoint directly via Swagger MCP** to verify it's not an endpoint issue:
   ```
   mcp__swagger__<endpoint-tool-name>(<params-from-test>)
   ```

2. **Compare expected vs actual response:**
   - Expected schema from Swagger MCP
   - Actual response from test
   - Highlight differences

3. **Report diagnosis to user:**
   ```
   ⚠️ Test `test_api_pos_create_booking` failed.
   
   🔍 Swagger MCP Diagnosis:
   • Endpoint: POST /booking/create
   • Expected status: 200
   • Actual status: 400
   • Response: {"error": "Missing required field: car_id"}
   • Swagger schema: car_id is required (confirmed)
   
   Suggested fix: Update test payload to include car_id
   ```

Parse and display:
- Total: passed / failed / skipped / errors
- Failed test names with error summaries (only after retry)
- MCP-generated diagnoses (attached as Allure attachments)
- Time taken

Collect failure artifacts for failed tests:
```bash
find reports/screenshots/ -newer reports/allure-results -name "*.png" 2>/dev/null
find reports/videos/ -newer reports/allure-results -name "*.webm" -o -name "*.mp4" 2>/dev/null
```
Store artifact paths as `$FAILURE_SCREENSHOTS` and `$FAILURE_VIDEOS`.

Open Allure report:
```bash
allure serve reports/allure-results
```

---

### Stage 5b — API Test Generation from Intercepted Network Calls (if `$INCLUDE_API_TESTS = true` and UI tests were run)

**Prerequisites:**
- UI tests were executed in Stage 5
- Network interception was enabled (see Stage 4 template)
- At least one API call was intercepted

**Step 1 — Extract intercepted API calls from Allure attachments:**
```bash
# Parse Allure JSON files to extract "Intercepted API Calls" attachments
grep -r "Intercepted API Calls" reports/allure-results/ -A 10
```

Store as `$INTERCEPTED_CALLS` (list of method + URL pairs).

**Step 2 — Cross-reference with Swagger MCP:**

For each intercepted call, find the corresponding Swagger MCP tool:
```
# Example: If we intercepted "POST /booking/create"
# Find tool: mcp__swagger__crt-booking-using-pst
```

Load the schema for each tool using ToolSearch.

**Step 3 — Generate API tests for intercepted calls:**

For each unique API call, generate a test in `tests/api/test_api_$TICKET_lower_$MODULE.py` following the API test template from Stage 4.

**Step 4 — Report to user:**
```
🔗 Network Interception Results:
  ✅ Intercepted <N> unique API calls during UI test run
  ✅ Matched <M> calls to Swagger MCP endpoints
  ✅ Generated <M> new API tests in tests/api/test_api_$TICKET_lower_$MODULE.py
  
  New API tests:
   • test_api_pos_get_locations (from GET /locations)
   • test_api_pos_create_booking (from POST /booking/create)
   • test_api_pos_rental_payment (from POST /payment)
```

---

### Stage 5c — Export Postman Collection (if `$EXPORT_POSTMAN = true`)

**Skip this stage entirely if the user chose No at Checkpoint 1.**

Build a Postman Collection v2.1 JSON file from:
1. API endpoints identified in Stage 3a (Swagger MCP discovery)
2. Intercepted API calls from Stage 5b (if applicable)

**Collection structure:**
```json
{
  "info": {
    "name": "$TICKET — $TICKET_SUMMARY",
    "description": "Generated via Swagger MCP on <date>",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "<AC label> — <scenario name>",
      "request": {
        "method": "<GET|POST|PUT|DELETE>",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": {
          "raw": "{{base_url}}<endpoint-path>",
          "host": ["{{base_url}}"],
          "path": ["<path-segment>"]
        },
        "body": {
          "mode": "raw",
          "raw": "<example payload JSON from Swagger MCP schema>"
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status is 200', () => pm.response.to.have.status(200));",
              "pm.test('Response has booking_id', () => pm.expect(pm.response.json()).to.have.property('booking_id'));"
            ]
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "https://beta.drivejoulez.com:8443/joulez-service",
      "type": "string"
    }
  ]
}
```

**Rules:**
- One Postman request per test case (Happy Path, Negative, RBAC)
- Group requests into folders by AC (e.g. `AC1 — Location`, `AC2 — Date & Time`)
- Include example payloads **directly from Swagger MCP schema** (not manually crafted)
- Add basic Postman test scripts for status code and key response fields (derived from Swagger schema)
- Use `{{base_url}}` as a Postman variable for environment-agnostic collections

**Output & Upload:**
1. Save the file locally to:
```
plans/postman_$TICKET_lower_<YYYY-MM-DD>.json
```

2. Automatically upload it to Postman using `curl` (the API requires the JSON to be wrapped in a `{"collection": ...}` object):
```bash
# Wrap the generated collection in the required format
jq '{collection: .}' plans/postman_$TICKET_lower_<YYYY-MM-DD>.json > plans/postman_payload.json

# Upload to the Joulez workspace
curl --silent --location 'https://api.getpostman.com/collections?workspace=bd9bcbaa-d3ab-48ba-9757-38a6a6404d54' \
--header 'X-API-Key: PMAK-REDACTED-ROTATE-THIS-KEY' \
--header 'Content-Type: application/json' \
--data "@plans/postman_payload.json"

# Clean up the temporary payload file
rm plans/postman_payload.json
```

Confirm to the user: `"✅ Postman collection exported locally and uploaded directly to the Joulez workspace in Postman!"`

---

### ⏸ HITL CHECKPOINT 2 — Test Failure Gate

**If any tests FAILED:**

> "⚠️ **<N> test(s) failed:**
>
> <list of failures with MCP-generated diagnoses>
>
> I used **Playwright MCP** to capture the failure state (screenshots attached) and **Swagger MCP** to verify API endpoint behavior.
>
> How would you like to proceed?
> - **[C] Continue** — commit and raise PR as draft (failures visible in PR)
> - **[F] Fix** — I'll diagnose and attempt to fix failures before committing
> - **[I] Investigate** — Let me use Playwright MCP to interactively debug the failures with you"

**Options:**
- **Fix** → invoke `debug-test` skill per failing test, apply fixes, then re-run Stage 5
- **Continue** → proceed with `$DRAFT = true`
- **Investigate** → Open an interactive Playwright MCP session, let user inspect live

If all tests passed → `$DRAFT = false`, proceed automatically.

---

### Stage 6 — Commit and Push

**Pre-commit checks** (from `agents/rules.md`) — block on any violation:
- [ ] No `print()` statements in page objects or tests
- [ ] No raw integer timeouts — must use `settings.*_TIMEOUT`
- [ ] All new page methods have `@allure.step(...)`
- [ ] Test function names follow `test_pos_` / `test_err_` / `test_perm_` / `test_api_pos_` / `test_api_err_` convention
- [ ] No hardcoded credentials or URLs
- [ ] All locators in page objects are sourced from Playwright MCP snapshots (include date in docstring)
- [ ] All API test payloads are validated against Swagger MCP schemas (include endpoint in docstring)

Stage files:
```bash
git add tests/ui/test_$TICKET_lower_$MODULE.py           # UI tests (if applicable)
git add tests/api/test_api_$TICKET_lower_$MODULE.py      # API tests (if applicable)
git add plans/manual_tests_$TICKET_lower_*.md
git add plans/manual_tests_$TICKET_lower_*.csv
git add plans/postman_$TICKET_lower_*.json               # only if $EXPORT_POSTMAN = true
git add plans/$TICKET_lower_reference_screenshot.png     # Playwright MCP reference (if UI flow)
git add plans/$TICKET_lower_failure_*.png                # Playwright MCP failure screenshots (if failures)
git add plans/run_summary_$TICKET_lower_*.md
# add any page objects created or modified during this session
```

Commit message (derived from ticket):
```
test($MODULE): add MCP-enhanced automation tests for $TICKET

Covers <N> ACs from $TICKET: $TICKET_SUMMARY
- Generated <M> UI tests using Playwright MCP live locators
- Generated <K> API tests using Swagger MCP schema validation
- Intercepted <L> network calls for API correlation
- Exported Postman collection (if applicable)

Locators verified via Playwright MCP on <YYYY-MM-DD>
API schemas validated via Swagger MCP (version: dev_1.0.1158)

Refs: $TICKET
```

Push:
```bash
git push -u origin $BRANCH
```

---

### Stage 7 — Count Coverage Delta

Calculate the test coverage increase:
```bash
# Count new tests
NEW_UI_TESTS=$(grep -c "^def test_" tests/ui/test_$TICKET_lower_$MODULE.py)
NEW_API_TESTS=$(grep -c "^def test_api_" tests/api/test_api_$TICKET_lower_$MODULE.py)
TOTAL_NEW_TESTS=$((NEW_UI_TESTS + NEW_API_TESTS))

# Count total tests after this PR
TOTAL_TESTS_AFTER=$(grep -r "def test_" tests/ --include="*.py" | wc -l)

# Calculate delta
COVERAGE_DELTA=$((TOTAL_TESTS_AFTER - EXISTING_TEST_COUNT))
```

Store as `$COVERAGE_DELTA`, `$NEW_UI_TESTS`, `$NEW_API_TESTS`.

---

### Stage 8 — Raise Pull Request

**PR title** (derived at runtime):
```
[$TICKET] test($MODULE): <concise description from $TICKET_SUMMARY>
```

**PR body** includes:

```markdown
## 🎫 [$TICKET] $TICKET_SUMMARY
> Jira: https://innocito.atlassian.net/browse/$TICKET

## 🎭 MCP-Enhanced Test Generation

This PR was generated using the **V2 MCP-Enhanced Workflow** with:
- ✅ **Playwright MCP**: Live UI inspection for stable locators
- ✅ **Swagger MCP**: API schema validation and payload generation
- ✅ **Network Interception**: Captured <L> API calls during UI tests
- ✅ **Interactive Debugging**: MCP-powered failure diagnosis (if applicable)

## 📋 Test Coverage

### UI Tests (`tests/ui/test_$TICKET_lower_$MODULE.py`)
| AC | Test Function | Type | Locator Source | Status |
|----|--------------|------|----------------|--------|
| AC1 | `test_pos_select_pickup_location` | Happy Path | Playwright MCP snapshot (2026-05-19) | ✅ Passed |
| AC1 | `test_err_invalid_pickup_location` | Negative | Playwright MCP snapshot (2026-05-19) | ✅ Passed |

### API Tests (`tests/api/test_api_$TICKET_lower_$MODULE.py`)
| AC | Test Function | Type | Endpoint | Schema Source | Status |
|----|--------------|------|----------|---------------|--------|
| AC2 | `test_api_pos_create_booking` | Happy Path | POST /booking/create | Swagger MCP (dev_1.0.1158) | ✅ Passed |
| AC2 | `test_api_err_create_booking_invalid` | Negative | POST /booking/create | Swagger MCP (dev_1.0.1158) | ✅ Passed |

**Coverage delta:** $EXISTING_TEST_COUNT → $TOTAL_TESTS_AFTER tests (+$COVERAGE_DELTA for $TICKET)
- +$NEW_UI_TESTS UI tests
- +$NEW_API_TESTS API tests

## 🧪 Test Results
- ✅ Passed: <N>  ❌ Failed: <M>  ⏭️ Skipped: <K>
- Run time: <T>s

<if failures exist>
## ⚠️ Failures
| Test | Error Summary | MCP Diagnosis |
|------|--------------|---------------|
| `test_err_...` | AssertionError: expected 400 got 200 | Swagger MCP confirms endpoint returns 200 for this input — test expectation incorrect |

**Artifacts:**
- Failure screenshots (Playwright MCP): <list paths>
- Live page snapshot (Playwright MCP): `plans/$TICKET_lower_failure_snapshot.yml`
</if>

## 📦 Postman Collection
<if $EXPORT_POSTMAN = true>
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
- Swagger API: https://beta.drivejoulez.com:8443/joulez-service/swagger-ui.html
- Playwright MCP Reference: `plans/$TICKET_lower_reference_screenshot.png`
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

Post a rich comment with full test evidence:

```
jira_add_comment(
  issue_key=$TICKET,
  body="""
✅ *Automation PR raised (V2 MCP-Enhanced):* <PR URL>
*Branch:* $BRANCH
*Status:* <All passing ✅ | Draft — <N> failures ⚠️>

----
*🎭 Playwright MCP Integration*
• Live UI inspection performed: ✅
• Locators verified on: <YYYY-MM-DD>
• Failure screenshots captured: <N>
• Reference screenshot: plans/$TICKET_lower_reference_screenshot.png

*🔗 Swagger MCP Integration*
• API schema validated: ✅ (version: dev_1.0.1158)
• Endpoints discovered: <M>
• API tests generated: <K>
• Postman collection exported: <Yes ✅ | No ⏭️>

----
*Test Results*
|| AC || Test Function || Type || Locator/Endpoint Source || Result ||
| AC1 | test_pos_select_pickup_location | UI Happy Path | Playwright MCP | ✅ Passed |
| AC1 | test_err_invalid_pickup_location | UI Negative | Playwright MCP | ✅ Passed |
| AC2 | test_api_pos_create_booking | API Happy Path | Swagger MCP | ✅ Passed |
| AC2 | test_api_err_create_booking_invalid | API Negative | Swagger MCP | ✅ Passed |

*Coverage:* $EXISTING_TEST_COUNT → $TOTAL_TESTS_AFTER tests total (+$COVERAGE_DELTA new: $NEW_UI_TESTS UI + $NEW_API_TESTS API)
*Run time:* <T>s
"""
)
```

Then transition the ticket to **In Review**:
```
jira_transition_issue(issue_key=$TICKET, transition="In Review")
```

Confirm to the user: `"✅ Jira $TICKET updated with MCP-enhanced test results and transitioned → In Review"`

---

### Stage 10 — PR Review Agent

Announce the handoff clearly:

> "Handing off PR #$PR_NUMBER to a dedicated review agent…"

Spawn the `review-pr` skill as a **separate sequential agent**. Pass it:
- `$PR_NUMBER`
- `$OWNER`
- `$REPO`

The review agent independently:
1. Fetches PR files and diff via GitHub MCP
2. Analyses against `agents/rules.md`
3. Validates that locators reference Playwright MCP in docstrings
4. Validates that API tests reference Swagger MCP schema in docstrings
5. Posts a structured review (`APPROVE` / `REQUEST_CHANGES` / `COMMENT`)

After it completes, surface to the user:
- Review decision and key findings
- Link to the posted GitHub review
- Recommended next step (merge / fix and re-push)

---

## Final Status Summary

Render and display the summary table, then **save it as a shareable artifact**:

```
plans/run_summary_$TICKET_lower_<YYYY-MM-DD>.md
```

Content to save:
```markdown
# Run Summary — $TICKET: $TICKET_SUMMARY (V2 MCP-Enhanced)
Date    : <YYYY-MM-DD>
Repo    : $OWNER/$REPO
Branch  : $BRANCH
PR      : <PR URL>
Jira    : https://innocito.atlassian.net/browse/$TICKET

## MCP Integration Status
| MCP Server | Used | Purpose |
|-----------|------|---------|
| Jira | ✅ | Ticket fetch, transitions, comments |
| GitHub | ✅ | PR creation, review |
| Playwright | ✅ | Live UI inspection, locator discovery, failure debugging |
| Swagger | ✅ | API schema validation, endpoint discovery, payload generation |

## Stage Results
| Stage | Status | Output |
|-------|--------|--------|
| MCP Health Check | ✅ | All 4 MCP servers healthy |
| Jira Fetch | ✅ | $TICKET: <summary> |
| Branch Created | ✅ | $BRANCH |
| Swagger Discovery | ✅ | <N> endpoints found via Swagger MCP |
| Playwright UI Inspection | ✅ | <M> elements discovered, reference screenshot saved |
| Test Cases Derived | ✅ | <K> cases → plans/manual_tests_*.md & .csv |
| Scripts Generated | ✅ | tests/ui/ + tests/api/ (MCP-sourced locators/schemas) |
| Test Run | ✅/⚠️ | <N> passed / <M> failed |
| MCP Failure Diagnosis | ✅ | <L> failures diagnosed via Playwright MCP |
| Postman Export | ✅/⏭️ | plans/postman_*.json (or skipped) |
| Commit + Push | ✅ | <commit hash> |
| PR Raised | ✅ | <PR URL> (draft: yes/no) |
| Jira Updated | ✅ | Transitioned → In Review |
| PR Review | ✅ | APPROVE / REQUEST_CHANGES |

## Coverage Delta
Before: $EXISTING_TEST_COUNT tests | After: $TOTAL_TESTS_AFTER tests | Added: +$COVERAGE_DELTA ($NEW_UI_TESTS UI + $NEW_API_TESTS API)

## AC Coverage
| AC | UI Tests | API Tests | All Passing? |
|----|----------|-----------|-------------|
| AC1 | test_pos_..., test_err_... | - | ✅ |
| AC2 | - | test_api_pos_..., test_api_err_... | ✅ |

## Locator/Schema Traceability
All UI test locators verified via **Playwright MCP** on <YYYY-MM-DD>.
All API test schemas validated via **Swagger MCP** (version: dev_1.0.1158).
Reference screenshot: `plans/$TICKET_lower_reference_screenshot.png`
```

Confirm to the user: `"📄 Run summary saved to plans/run_summary_$TICKET_lower_<date>.md — ready to share!"`

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Any MCP server not responding (Stage 0) | 🛑 STOP workflow — prompt user to check `.mcp.json` |
| Jira ticket not found | Stop — ask user to verify `$TICKET` |
| `git remote` not set | Stop — ask user to configure remote origin |
| Branch already exists | Auto-append next available version suffix (`-v2`, `-v3`, …) — never reuse, never prompt |
| No ACs parseable from Jira | Show raw description, ask user to define test scope |
| `$MODULE` cannot be inferred | Ask user: "Which module does this ticket belong to?" |
| Page object missing for `$MODULE` | Run `write-page-object` skill (with Playwright MCP), then resume from Stage 4 |
| Playwright MCP snapshot returns no elements | Warn user: "Page may be behind auth or not loaded. Falling back to manual locator definition." |
| Swagger MCP endpoint call returns 403/401 | Note: "Authentication required. Include auth token in API test fixtures." |
| Tests still failing after MCP diagnosis | Raise as draft, include MCP diagnosis in PR body and Jira comment |
| GitHub MCP not authenticated | Stop — prompt user to check `.mcp.json` |

---

## V2 Key Differentiators Summary

| Feature | V1 (Bash/curl) | V2 (MCP-Enhanced) |
|---------|----------------|-------------------|
| API Discovery | Manual curl + jq parsing | ✅ Direct Swagger MCP tools |
| Locator Discovery | Manual guessing | ✅ Live Playwright MCP snapshots |
| Test Generation | Generic templates | ✅ MCP-sourced locators + schemas |
| Failure Debugging | Manual log parsing | ✅ Interactive Playwright MCP |
| API Validation | Manual requests | ✅ Swagger schema validation |
| Traceability | None | ✅ MCP source + date in docstrings |

---

**End of Workflow V2**
