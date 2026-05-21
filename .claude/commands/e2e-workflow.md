---
name: e2e-workflow
description: Unified Jira-to-PR workflow — fetches a Jira ticket, derives test cases, generates + runs tests, commits, raises PR, updates Jira, and spawns a separate review agent
tags: [jira, github, workflow, e2e, mcp, orchestration]
---

# Skill: End-to-End Workflow

Runs the full automation lifecycle from a single Jira ticket ID.
**Everything is derived at runtime** — no hardcoded repo names, branches, or paths.

> **MCP Required**: `mcp-atlassian` (Jira) + GitHub MCP server (both in `.mcp.json`)
> **Rules**: `agents/rules.md`

---

## Usage

```
/e2e-workflow <TICKET-ID>
```

Example: `/e2e-workflow SCRUM-1`

---

## Dashboard Integration

If `dashboard/server/main.py` is running, stream events to it so the live UI at http://localhost:5173 visualises progress. All dashboard calls are **fire-and-forget** (`|| true`) — the workflow must continue even if the server is not running.

**Event helper** (use at every stage boundary):
```bash
# Stage start
python dashboard/utils/client.py event --type stage_start  --stage <id> --message "<text>" 2>/dev/null || true
# Stage complete
python dashboard/utils/client.py event --type stage_complete --stage <id> --message "<text>" --level success --data '<json>' 2>/dev/null || true
# Log line
python dashboard/utils/client.py event --type log --stage <id> --message "<text>" 2>/dev/null || true
```

**HITL gate** (use at every HITL checkpoint — BLOCKING until browser responds):
```bash
python dashboard/utils/hitl_gate.py --id "<checkpoint-id>" --message "<question>" --context '<json>' 2>/dev/null || true
```
`hitl_gate.py` exits 0 for Approve, 1 for Reject. Use `$?` to branch if needed; default to continue on failure.

**Stage IDs**: `jira_fetch`, `branch_create`, `swagger_discovery`, `test_cases`, `generate_tests`, `run_tests`, `postman_export`, `commit_push`, `raise_pr`, `update_jira`, `pr_review`

---

## Runtime Context Resolution

Before any stage runs, resolve all dynamic values once and reuse them throughout:

```bash
# GitHub owner and repo — derived from git remote, never hardcoded
git remote get-url origin
# e.g. https://github.com/EswarPrasadKona/ipc-playwright.git
# → owner = "EswarPrasadKona", repo = "ipc-playwright"
```

Parse owner and repo from the remote URL (supports both HTTPS and SSH formats):
- HTTPS: `https://github.com/<owner>/<repo>.git`
- SSH: `git@github.com:<owner>/<repo>.git`

Store as:
- `$OWNER` — GitHub username/org
- `$REPO` — repository name
- `$TICKET` — the Jira ticket ID argument (e.g. `SCRUM-1`)
- `$TICKET_lower` — lowercase `$TICKET` with hyphens (e.g. `jp-1`), used in all file paths
- `$DATE` — today's date as `YYYY-MM-DD` (e.g. `2026-05-21`)
- `$BRANCH` — computed in Stage 2
- `$MODULE` — computed in Stage 1 from Jira labels/components
- `$PR_NUMBER` — captured in Stage 7

```bash
# 📊 Dashboard — REQUIRED health check (no || true — this must pass)
python dashboard/utils/client.py check
```

**If the check fails (exit code 1): STOP immediately.** Tell the user:
> "⚠️ The workflow dashboard is not running. Please start it first:
> ```
> cd dashboard && ./start.sh
> ```
> Then re-run `/e2e-workflow $TICKET` once the dashboard is ready at http://localhost:5173."

Do not proceed past this point until the server is confirmed up.

```bash
# 📊 Dashboard — workflow start
python dashboard/utils/client.py event --type workflow_start --message "Workflow started: $TICKET" --data "{\"ticket\":\"$TICKET\"}" 2>/dev/null || true
```

---

## Workflow

---

### Stage 1 — Fetch Jira Ticket

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage jira_fetch --message "Fetching $TICKET from Jira..." 2>/dev/null || true
```

```
jira_get_issue(issue_key=$TICKET)
```

Extract and store:
- **`$TICKET_SUMMARY`** — the issue summary line
- **`$TICKET_DESCRIPTION`** — full description body
- **`$TICKET_ACS`** — acceptance criteria (look for `Given/When/Then`, `AC1:`, `- [ ]` checkboxes)
- **`$MODULE`** — derived from: Jira components field → labels → keywords in summary (e.g. "Diagnostic" → `diagnostics`, "Login" → `login`)
- **`$STATUS`**, **`$PRIORITY`**, **`$ASSIGNEE`**

Print a structured summary to the user:
```
Ticket : $TICKET
Summary: $TICKET_SUMMARY
Module : $MODULE
Status : $STATUS
ACs found: <N>
```

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage jira_fetch --level success \
  --message "$TICKET: $TICKET_SUMMARY" \
  --data "{\"ticket\":\"$TICKET\",\"summary\":\"$TICKET_SUMMARY\",\"status\":\"$STATUS\",\"module\":\"$MODULE\",\"acs_found\":\"<N>\"}" 2>/dev/null || true
```

---

### Stage 2 — Create Git Branch

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage branch_create --message "Creating branch from main..." 2>/dev/null || true
```

> **Default branch is `main`.** Always branch from `main`, regardless of what `origin/HEAD` resolves to or what the current branch is.
>
> 🚨 **HARD RULE: Never commit test files, page objects, or plans directly to `main`.** This stage MUST complete before any files are written in Stages 3–6. If you find yourself on `main` at any later stage, STOP and return here first.

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
- `SCRUM-1` + "Validate Diagnostic Tests Execution and Results…" → `scrum-1-validate-diagnostic-tests-execution`
- `SCRUM-42` + "Fix login timeout on slow networks" → `scrum-42-fix-login-timeout-on-slow-networks`
- `PROJ-7` + "Add user permission management screen" → `proj-7-add-user-permission-management-screen`

**Branch creation — always run these commands, every time the workflow is triggered:**

```bash
git checkout main
git pull origin main
git checkout -b $BRANCH
# Verify we are NOT on main before proceeding
git branch --show-current
```

The output of `git branch --show-current` MUST equal `$BRANCH`. If it still shows `main`, the branch creation failed — stop and report the error to the user.

- **Never reuse an existing ticket branch.** If `$BRANCH` already exists locally or on remote, automatically append a version suffix (`-v2`, `-v3`, …) using the next available number — no prompt needed.
- **Never ask the user** whether to reuse or create — always create a fresh branch.

Confirm the final branch name to the user before proceeding:
```
✅ Branch created: $BRANCH
   (branched from main — ready to generate test files)
```

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage branch_create --level success \
  --message "Branch: $BRANCH" --data "{\"branch\":\"$BRANCH\",\"base\":\"main\"}" 2>/dev/null || true
```

Immediately after branch creation, transition the Jira ticket to **In Progress**:
```
jira_transition_issue(issue_key=$TICKET, transition="In Progress")
```
Confirm: `"🔄 Jira ticket $TICKET transitioned → In Progress"`

---

### Stage 3 — Derive Manual Test Cases from Jira

**Source**: `$TICKET_DESCRIPTION` and `$TICKET_ACS` — no Excel file involved.
**Swagger API Reference**: `https://beta.drivejoulez.com:8443/joulez-service/swagger-ui.html#/`

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage swagger_discovery --message "Discovering API endpoints from Swagger..." 2>/dev/null || true
```

**Swagger Discovery Step — run this visibly before deriving test cases:**

Fetch the Swagger spec and identify all endpoints relevant to this ticket's domain:
```bash
curl -s "https://beta.drivejoulez.com:8443/joulez-service/v2/api-docs" | \
  python3 -c "
import sys, json
spec = json.load(sys.stdin)
paths = spec.get('paths', {})
for path, methods in paths.items():
    for method in methods:
        if method in ('get','post','put','delete','patch'):
            print(f'{method.upper():6} {path}')
"
```

Print the discovered endpoints to the user in a formatted block:
```
🔍 Swagger Discovery — endpoints matching this flow:
  POST   /booking/create
  GET    /cars/available
  GET    /booking/{id}
  (N endpoints found)
```
Store as `$SWAGGER_ENDPOINTS`. If the curl fails, note it and proceed using ticket context alone.

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage swagger_discovery --level success \
  --message "<N> endpoints discovered" --data "{\"endpoints_found\":\"<N>\"}" 2>/dev/null || true
python dashboard/utils/client.py event --type stage_start --stage test_cases --message "Deriving test cases from $TICKET..." 2>/dev/null || true
```

**API vs UI Analysis Strategy:**
1. **Explicit API Ticket**: If the ticket talks directly about automating an API, derive API-specific test cases. During generation, refer directly to the Swagger URL for endpoints, payloads, and schemas.
2. **UI Flow Ticket**: If the ticket talks about a UI task/flow, derive UI test cases. During generation, we will intercept the network tab to find the APIs being called, and then cross-reference those APIs with the Swagger doc to generate independent API tests alongside the UI tests.

For each AC or requirement found, produce:

| # | AC | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|----|------|----------|----------|----------------|-----------|-------|-----------------|
| 1 | AC1 | Happy Path | High | … | User logged in as Admin | Valid inputs | 1. …<br>2. … | Success toast appears |
| 2 | AC1 | Negative | Medium | … | None | Invalid email | 1. … | Error "Invalid email" shown |
| 3 | AC2 | RBAC | High | … | User is basic Viewer | Valid inputs | 1. … | Action button is disabled |

**Instructions for Test Case Quality:**
- **Pre-conditions:** Clearly state the required system state before the test starts (e.g., "Navigate to https://...", specific user roles).
- **Test Data:** Specify exact inputs needed to run the test (e.g., `invalid-email`).
- **Extreme Granularity:** Do not summarize steps. Break down every flow into micro-interactions. Before interacting with an element, explicitly include a step to verify it is visible and accessible.
- **1-to-1 Mapping:** The "Steps" and "Expected Result" columns must have a strict 1-to-1 mapping. Every single numbered step MUST have a corresponding numbered expected result (e.g., Step: "3. Click on Email field" -> Expected: "3. Email field is clicked and focused").

Generate at minimum:
- One `Happy Path` per AC (High priority)
- `Negative` cases where the AC implies error/validation handling
- `Edge Case` where boundary values or empty states are implied
- `RBAC/Permission` cases to ensure access controls block unauthorized actions

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage test_cases --level success \
  --message "<N> test cases derived" \
  --data "{\"cases_total\":\"<N>\",\"plan_file\":\"plans/manual_tests_${TICKET_lower}_${DATE}.md\",\"artifacts\":[{\"path\":\"plans/manual_tests_${TICKET_lower}_${DATE}.csv\",\"type\":\"csv\",\"label\":\"Test Cases CSV\"},{\"path\":\"plans/manual_tests_${TICKET_lower}_${DATE}.md\",\"type\":\"markdown\",\"label\":\"Test Cases MD\"}]}" 2>/dev/null || true
```

Save the output to two formats:
1. A Markdown file for easy reading:
```
plans/manual_tests_$TICKET_lower_<YYYY-MM-DD>.md
```
2. A CSV file (Excel compatible) for tracking and test management tools:
```
plans/manual_tests_$TICKET_lower_<YYYY-MM-DD>.csv
```

**CSV format rules (industry standard):**

- **Columns**: `TC#, AC, Type, Priority, Scenario, Pre-conditions, Test Data, Steps, Expected Result, Status, Automation Status, Test Layer, Defect ID`
- **Split rows**: Each step gets its own row. The first row for a TC carries all metadata fields; subsequent step rows leave TC#, AC, Type, Priority, Scenario, Pre-conditions, Test Data, Automation Status, Test Layer, Defect ID **empty** — only Steps and Expected Result are filled.
- **Default values**:
  - `Status` → `Not Run`
  - `Automation Status` → `Automated` (since we generate a test for every case)
  - `Test Layer` → `UI` for Playwright browser tests, `API` for API tests
  - `Defect ID` → empty (filled later if a test fails)
- Properly quote any field containing commas.

---

### ⏸ HITL CHECKPOINT 1 — Test Case Review

```bash
# 📊 Dashboard HITL — blocks until browser response
HITL_OUT=$(python dashboard/utils/hitl_gate.py \
  --id "test-case-review" \
  --message "$TICKET: $TICKET_SUMMARY — <N> test cases derived. Review and approve to proceed." \
  --context "{\"ticket\":\"$TICKET\",\"total_cases\":\"<N>\",\"acs_covered\":\"<N>\",\"artifacts\":[{\"csvPath\":\"plans/manual_tests_${TICKET_lower}_${DATE}.csv\",\"mdPath\":\"plans/manual_tests_${TICKET_lower}_${DATE}.md\",\"type\":\"testcases\",\"label\":\"Test Cases\"}]}" 2>/dev/null)
HITL_EXIT=$?
HITL_FEEDBACK=$(echo "$HITL_OUT" | grep "^HITL_FEEDBACK:" | sed 's/^HITL_FEEDBACK: //')
```

- **Exit 0 (Approve)**: proceed to HITL checkpoint `api-test-scope`.
- **Exit 1 (Request Changes)**: `$HITL_FEEDBACK` contains the user's instruction from the browser. Apply the requested changes to the test cases table, then re-present and re-run this checkpoint.

---

### ⏸ HITL CHECKPOINT 1a — API Test Scope

*(Skip this checkpoint if this is an explicit API ticket — API tests are already in scope. Set `$INCLUDE_API_TESTS = true` automatically.)*

```bash
# 📊 Dashboard HITL — blocks until browser response
HITL_OUT=$(python dashboard/utils/hitl_gate.py \
  --id "api-test-scope" \
  --message "Since this is a UI flow ticket, I can also generate independent API tests by intercepting network calls during the UI run and cross-referencing with Swagger.\n\nWould you like to include API test generation?" \
  --options "Yes — include API tests:approve:success,No — UI tests only:reject:default" \
  --context "{\"ticket\":\"$TICKET\",\"swagger_endpoints\":\"<N>\"}" 2>/dev/null)
HITL_EXIT=$?
```

- **Exit 0 (Yes)**: set `$INCLUDE_API_TESTS=true`, proceed to HITL checkpoint `postman-scope`.
- **Exit 1 (No)**: set `$INCLUDE_API_TESTS=false`, skip `postman-scope`, proceed to HITL checkpoint `test-naming-preview`.

---

### ⏸ HITL CHECKPOINT 1b — Postman Scope

*(Only run this checkpoint if `$INCLUDE_API_TESTS = true` OR if this is an explicit API ticket.)*

```bash
# 📊 Dashboard HITL — blocks until browser response
HITL_OUT=$(python dashboard/utils/hitl_gate.py \
  --id "postman-scope" \
  --message "Would you also like me to export a Postman-compatible collection (.json) for these endpoints?\n\nIt will be saved to plans/ and uploaded directly to the Joulez Postman workspace." \
  --options "Yes — export and upload:approve:success,No — skip Postman export:reject:default" \
  --context "{\"ticket\":\"$TICKET\",\"endpoints\":\"<N>\"}" 2>/dev/null)
HITL_EXIT=$?
```

- **Exit 0 (Yes)**: set `$EXPORT_POSTMAN=true`.
- **Exit 1 (No)**: set `$EXPORT_POSTMAN=false`.

Proceed to HITL checkpoint `test-naming-preview`.

---

### ⏸ HITL CHECKPOINT 1c — Test Naming Preview

**Before writing any files**, derive the proposed test function names from the approved test cases.

```bash
# 📊 Dashboard HITL — blocks until browser response
HITL_OUT=$(python dashboard/utils/hitl_gate.py \
  --id "test-naming-preview" \
  --message "Here are the test function names I'll generate. Approve to proceed, or request renames via the feedback field." \
  --options "Looks good — proceed:approve:success,Request renames:reject:feedback" \
  --context "{\"ticket\":\"$TICKET\",\"functions\":[\"test_pos_select_pickup_location\",\"test_err_invalid_pickup_location\",\"test_perm_guest_cannot_book\"],\"functions_count\":\"<N>\"}" 2>/dev/null)
HITL_EXIT=$?
HITL_FEEDBACK=$(echo "$HITL_OUT" | grep "^HITL_FEEDBACK:" | sed 's/^HITL_FEEDBACK: //')
```

- **Exit 0 (Approve)**: proceed to Stage 4.
- **Exit 1 (Request renames)**: `$HITL_FEEDBACK` contains rename instructions. Apply them to the planned function names, then re-run this checkpoint.

Also capture coverage baseline now:
```bash
find tests/ -name "*.py" | xargs grep -l "def test_" | wc -l
# and count total test functions
grep -r "def test_" tests/ --include="*.py" | wc -l
```
Store as `$EXISTING_TEST_COUNT`.

---

### Stage 4 — Generate Playwright Test Scripts

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage generate_tests --message "Generating Playwright test scripts..." 2>/dev/null || true
```

**API Script Generation Instructions (if applicable):**
- **Explicit API Ticket**: Write standard Playwright API tests using the `request` fixture (`APIRequestContext`). Read the Swagger docs to construct accurate payloads and assertions.
- **UI Flow Ticket (Network Interception)**: 
  1. In the UI test, intercept the network calls (e.g., `with page.expect_response("**/api/**") as response_info:`).
  2. Extract the endpoint URLs, headers, and payloads called by the frontend.
  3. Consult the Swagger API Reference to understand the full schema and error codes for those intercepted endpoints.
  4. Scaffold a separate API test file (`tests/test_api_$TICKET_lower_$MODULE.py`) that tests the Happy, Negative, and RBAC scenarios directly against the backend.

**Check for existing coverage first:**
```bash
grep -r "<keyword from $TICKET_SUMMARY>" tests/ --include="*.py" -l
```

If partial coverage exists, report it and only generate scripts for uncovered cases.

**Output files** (derived at runtime):
```
tests/ui/test_${TICKET_lower}_${MODULE}.py        ← UI Playwright tests
tests/api/test_api_${TICKET_lower}_${MODULE}.py   ← API tests (if $INCLUDE_API_TESTS = true)
```
Examples: `tests/ui/test_jp1_booking.py`, `tests/api/test_api_jp1_booking.py`

Generate one function per test case following this template:

```python
import pytest
import allure
from pages.<$MODULE>_page import <ModuleClass>
from config.settings import settings


@allure.epic("$TICKET: $TICKET_SUMMARY")
@allure.feature("$MODULE")
@allure.story("AC<N>: <ac text>")
@allure.title("<scenario name>")
def test_pos_<sanitized_scenario>(page):
    """
    Jira: $TICKET
    AC: <full ac text>
    """
    module_page = <ModuleClass>(page)

    with allure.step("Step 1: <action>"):
        # TODO: Implement
        pass

    with allure.step("Step N: Verify <outcome>"):
        # TODO: Assert
        pass
```

Naming convention (from `agents/rules.md`):
- Happy Path → `test_pos_<action>`
- Negative → `test_err_<action>`
- Permission → `test_perm_<action>`

Verify discoverability:
```bash
/opt/miniconda3/bin/python -m pytest --collect-only tests/ui/test_${TICKET_lower}_${MODULE}.py
```

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage generate_tests --level success \
  --message "<N> test functions generated" \
  --data "{\"test_file\":\"tests/ui/test_${TICKET_lower}_${MODULE}.py\",\"total_functions\":\"<N>\",\"artifacts\":[{\"path\":\"tests/ui/test_${TICKET_lower}_${MODULE}.py\",\"type\":\"python\",\"label\":\"UI Tests\"},{\"path\":\"tests/api/test_api_${TICKET_lower}_${MODULE}.py\",\"type\":\"python\",\"label\":\"API Tests\"}]}" 2>/dev/null || true
```

---

### ⏸ HITL CHECKPOINT 1b — Test Execution Scope

```bash
# 📊 Dashboard HITL — blocks until browser response
HITL_OUT=$(python dashboard/utils/hitl_gate.py \
  --id "test-execution-scope" \
  --message "I generated <N> test functions. How would you like to run them?" \
  --options "Run All Tests:approve:success,Run Selected:feedback:feedback,Skip — go to commit:reject:warning" \
  --context "{\"total_functions\":\"<N>\",\"artifacts\":[{\"path\":\"tests/ui/test_${TICKET_lower}_${MODULE}.py\",\"type\":\"python\",\"label\":\"UI Tests\"},{\"path\":\"tests/api/test_api_${TICKET_lower}_${MODULE}.py\",\"type\":\"python\",\"label\":\"API Tests\"}]}" 2>/dev/null)
HITL_EXIT=$?
HITL_FEEDBACK=$(echo "$HITL_OUT" | grep "^HITL_FEEDBACK:" | sed 's/^HITL_FEEDBACK: //')
```

- **Exit 0 (Run All / Run Selected)**: if `$HITL_FEEDBACK` is set, use it as the `-k` filter for pytest. Otherwise run all.
- **Exit 1 (Skip)**: set `$SKIP_RUN = true`.


**STOP. Before running any tests, ask the user what to execute.**

List all generated test functions by name, then ask:

> "I've generated **<N> test functions** in `tests/test_$TICKET_lower_$MODULE.py`:
>
> <list all test function names>
>
> How would you like to proceed?
> - **[A] All** — run all <N> tests
> - **[S] Selected** — tell me which tests to run (by name or number)
> - **[K] Skip** — skip execution for now and go straight to commit"

**Wait for user response.**
- **All** → set `$TEST_FILTER = tests/test_$TICKET_lower_$MODULE.py`
- **Selected** → set `$TEST_FILTER = -k "<user-specified names>"` within the test file
- **Skip** → set `$SKIP_RUN = true`, jump directly to Stage 5b / Stage 6

---

### Stage 5 — Run Tests

**Skip this stage if `$SKIP_RUN = true`.**

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage run_tests --message "Running tests: $TEST_FILTER" 2>/dev/null || true
```

```bash
# $TEST_FILTER is one of:
#   tests/ui/test_${TICKET_lower}_${MODULE}.py           (all)
#   tests/ui/test_${TICKET_lower}_${MODULE}.py -k "..."  (selected)
/opt/miniconda3/bin/python -m pytest $TEST_FILTER -v -p no:xdist --reruns=1 --reruns-delay=2
```

**`-p no:xdist`**: disables parallel execution so tests run one at a time in a single browser window — clean for demos and review. (`pyproject.toml` sets `-n=auto` globally for CI; this flag overrides it for workflow runs only.)

**Retry behaviour**: `--reruns=1` silently retries each failing test once before marking it failed. This filters out transient flakiness. Only tests that fail on both attempts are considered truly failed.

Parse and display:
- Total: passed / failed / skipped / errors
- Failed test names with error summaries (only after retry)
- Time taken

Collect failure artifacts for failed tests:
```bash
# List any screenshots captured
find screenshots/ -newer reports/allure-results -name "*.png" 2>/dev/null
# List any videos captured
find videos/ -newer reports/allure-results -name "*.webm" -o -name "*.mp4" 2>/dev/null
```
Store artifact paths as `$FAILURE_SCREENSHOTS` and `$FAILURE_VIDEOS`.

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage run_tests --level success \
  --message "<N> passed · <M> failed · <K> skipped" \
  --data "{\"passed\":\"<N>\",\"failed\":\"<M>\",\"skipped\":\"<K>\",\"duration_s\":\"<T>\"}" 2>/dev/null || true
```

---

### ⏸ HITL CHECKPOINT — Allure Report

```bash
# 📊 Dashboard HITL — blocks until browser response
python dashboard/utils/hitl_gate.py \
  --id "allure-report" \
  --message "Tests finished: <N> passed / <M> failed / <K> skipped in <T>s. Generate Allure report?" \
  --options "Yes — generate and open:approve:success,No — skip and commit:reject:default" \
  --context "{\"passed\":\"<N>\",\"failed\":\"<M>\",\"skipped\":\"<K>\",\"duration\":\"<T>s\"}" 2>/dev/null || true
```

**STOP. Ask once after tests complete:**

> "Tests finished: ✅ **<N> passed** / ❌ **<M> failed** / ⏭️ **<K> skipped** in <T>s
>
> Would you like me to generate the **Allure report**?
> *(Wipes any old report and builds a fresh consolidated view from this run)*
>
> - **[Y] Yes** — generate and open
> - **[N] No** — skip, proceed to commit"

**Wait for user response.**

If **Yes**:
```bash
# Wipe any previous HTML report (keep allure-results — they were just written by this run)
rm -rf reports/allure-html

# Build consolidated HTML report from results collected during this run
allure generate reports/allure-results --clean -o reports/allure-html
```

```bash
# 📊 Dashboard — unlock Allure Report artifact pill
python dashboard/utils/client.py event --type stage_complete --stage run_tests --level success \
  --message "Allure report generated" \
  --data "{\"artifacts\":[{\"path\":\"reports/allure-html\",\"type\":\"report\",\"label\":\"Allure Report\"}]}" 2>/dev/null || true
```

The report is now accessible in the dashboard artifact strip and at `http://localhost:8765/reports/allure-html/`.

Confirm: `"📊 Allure report ready — open it from the dashboard artifact strip or at http://localhost:8765/reports/allure-html/"`

If **No**: skip and proceed to Stage 5b / Stage 6.

---

### Stage 5b — Export Postman Collection (if `$EXPORT_POSTMAN = true`)

**Skip this stage entirely if the user chose No at Checkpoint 1.**

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage postman_export --message "Building Postman collection..." 2>/dev/null || true
```

Build a Postman Collection v2.1 JSON file from the API endpoints identified in Stage 3/4.

**Source of endpoints:**
- **Explicit API ticket** — derive from Swagger docs at the Swagger API Reference URL
- **UI flow ticket** — derive from network calls intercepted during Stage 5 test run, cross-referenced with Swagger for full schema

**Collection structure:**
```json
{
  "info": {
    "name": "$TICKET — $TICKET_SUMMARY",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "<AC label> — <scenario name>",
      "request": {
        "method": "<GET|POST|PUT|DELETE>",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "url": { "raw": "<full endpoint URL>", ... },
        "body": { "mode": "raw", "raw": "<example payload JSON>" }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status is 200', () => pm.response.to.have.status(200));",
              "pm.test('Response has expected fields', () => { ... });"
            ]
          }
        }
      ]
    }
  ]
}
```

**Rules:**
- One Postman request per test case (Happy Path, Negative, RBAC)
- Group requests into folders by AC (e.g. `AC1 — Location`, `AC2 — Date & Time`)
- Include example payloads from Swagger or intercepted requests
- Add basic Postman test scripts for status code and key response fields
- Use `{{base_url}}` as a Postman variable for the host so it's environment-agnostic

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

Confirm to the user: `"Postman collection exported locally and uploaded directly to the Joulez workspace in Postman!"`

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage postman_export --level success \
  --message "Postman collection uploaded to Joulez workspace" \
  --data "{\"local_file\":\"plans/postman_${TICKET_lower}_${DATE}.json\",\"artifacts\":[{\"path\":\"plans/postman_${TICKET_lower}_${DATE}.json\",\"type\":\"json\",\"label\":\"Postman Collection\"}]}" 2>/dev/null || true
```

---

### ⏸ HITL CHECKPOINT 2 — Test Failure Gate

```bash
# 📊 Dashboard HITL (only if failures exist — skip block if all passed)
# python dashboard/utils/hitl_gate.py \
#   --id "failure-gate" \
#   --message "<N> test(s) failed. Continue as draft PR or fix first?" \
#   --options "Continue as Draft:approve:warning,Fix Failures First:reject:danger" \
#   --context "{\"failed\":\"<N>\",\"failures\":\"<list>\"}" 2>/dev/null || true
```

**If any tests FAILED:**

> "⚠️ **<N> test(s) failed:**
>
> <list of failures with error summaries>
>
> How would you like to proceed?
> - **[C] Continue** — commit and raise PR as draft (failures visible in PR)
> - **[F] Fix** — I'll diagnose and attempt to fix failures before committing"

- **Fix** → invoke `debug-test` skill per failing test, then re-run Stage 5
- **Continue** → proceed with `$DRAFT = true`

If all tests passed → `$DRAFT = false`, proceed automatically.

---

### Stage 6 — Commit and Push

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage commit_push --message "Running pre-commit checks and committing..." 2>/dev/null || true
```

**Branch guard — run before any `git add`:**
```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
```
If `$CURRENT_BRANCH` is `main`: **🛑 STOP.** Do not commit. Return to Stage 2, create the feature branch, then move uncommitted changes there (`git stash` / `git checkout -b $BRANCH` / `git stash pop`) before proceeding. **Never commit or push directly to `main` — all changes must arrive via PR.**

**Pre-commit checks** (from `agents/rules.md`) — block on any violation:
- [ ] No `print()` statements in page objects or tests
- [ ] No raw integer timeouts — must use `settings.*_TIMEOUT`
- [ ] All new page methods have `@allure.step(...)`
- [ ] Test function names follow `test_pos_` / `test_err_` / `test_perm_` convention
- [ ] No hardcoded credentials or URLs

Stage files:
```bash
git add tests/ui/test_${TICKET_lower}_${MODULE}.py
git add tests/api/test_api_${TICKET_lower}_${MODULE}.py   # only if $INCLUDE_API_TESTS = true
git add plans/manual_tests_${TICKET_lower}_*.md
git add plans/manual_tests_${TICKET_lower}_*.csv
git add plans/postman_${TICKET_lower}_*.json               # only if $EXPORT_POSTMAN = true
git add plans/run_summary_${TICKET_lower}_*.md
# add any page objects created during this session
```

Commit message (derived from ticket):
```
test($MODULE): add automation tests for $TICKET

Covers <N> ACs from $TICKET: $TICKET_SUMMARY
Refs: $TICKET
```

Push the **feature branch only** — never `main`:
```bash
# ✅ Correct
git push -u origin $BRANCH

# 🚫 Never run this
# git push origin main
```

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage commit_push --level success \
  --message "Committed and pushed $BRANCH" \
  --data "{\"branch\":\"$BRANCH\",\"commit\":\"<hash>\"}" 2>/dev/null || true
```

---

### Stage 7 — Raise Pull Request

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage raise_pr --message "Creating GitHub pull request..." 2>/dev/null || true
```

**PR title** (derived at runtime):
```
[$TICKET] test($MODULE): <concise description from $TICKET_SUMMARY>
```

**PR body** includes:

```markdown
## 🎫 [$TICKET] $TICKET_SUMMARY
> Jira: https://innocito.atlassian.net/browse/$TICKET

## 📋 Test Coverage
| AC | Test Function | Type | Status |
|----|--------------|------|--------|
| AC1 | `test_pos_...` | Happy Path | ✅ Passed |
| AC1 | `test_err_...` | Negative | ✅ Passed |
| AC2 | `test_perm_...` | RBAC | ⚠️ Failed |

**Coverage delta: $EXISTING_TEST_COUNT → $EXISTING_TEST_COUNT + <N> tests (+<N> for $TICKET)**

## 🧪 Test Results
- ✅ Passed: <N>  ❌ Failed: <M>  ⏭️ Skipped: <K>
- Run time: <T>s

<if failures exist>
## ⚠️ Failures
| Test | Error Summary |
|------|--------------|
| `test_err_...` | AssertionError: expected 400 got 200 |

**Artifacts:**
<list $FAILURE_SCREENSHOTS paths>
<list $FAILURE_VIDEOS paths>
</if>

## 🚀 Run Locally
\`\`\`bash
pip install -r requirements.txt
python -m pytest tests/ui/test_${TICKET_lower}_${MODULE}.py -v
\`\`\`
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

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage raise_pr --level success \
  --message "PR #$PR_NUMBER raised" \
  --data "{\"pr_number\":\"$PR_NUMBER\",\"pr_url\":\"<url>\",\"draft\":\"$DRAFT\"}" 2>/dev/null || true
```

---

### Stage 8 — Update Jira Ticket

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage update_jira --message "Updating $TICKET with test results..." 2>/dev/null || true
```

Post a rich comment with full test evidence:

```
jira_add_comment(
  issue_key=$TICKET,
  body="""
✅ *Automation PR raised:* <PR URL>
*Branch:* $BRANCH
*Status:* <All passing ✅ | Draft — <N> failures ⚠️>

----
*Test Results*
|| AC || Test Function || Type || Result ||
| AC1 | test_pos_... | Happy Path | ✅ Passed |
| AC1 | test_err_... | Negative | ✅ Passed |
| AC2 | test_perm_... | RBAC | ⚠️ Failed |

*Coverage:* $EXISTING_TEST_COUNT → $EXISTING_TEST_COUNT+<N> tests total (+<N> new)
*Run time:* <T>s
<if Postman exported>
*Postman Collection:* Uploaded to Joulez workspace ✅
</if>
"""
)
```

Then transition the ticket to **In Review**:
```
jira_transition_issue(issue_key=$TICKET, transition="In Review")
```

Confirm to the user: `"✅ Jira $TICKET updated with test results and transitioned → In Review"`

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_complete --stage update_jira --level success \
  --message "$TICKET transitioned → In Review" \
  --data "{\"ticket\":\"$TICKET\",\"transition\":\"In Review\",\"pr_url\":\"<url>\"}" 2>/dev/null || true
```

---

### Stage 9 — PR Review Agent

```bash
# 📊 Dashboard
python dashboard/utils/client.py event --type stage_start --stage pr_review --message "Spawning PR review agent for #$PR_NUMBER..." 2>/dev/null || true
```

Announce the handoff clearly:

> "Handing off PR #$PR_NUMBER to a dedicated review agent…"

Spawn the `review-pr` skill as a **separate sequential agent**. Pass it:
- `$PR_NUMBER`
- `$OWNER`
- `$REPO`

The review agent independently:
1. Fetches PR files and diff via GitHub MCP
2. Analyses against `agents/rules.md`
3. Posts a structured review (`APPROVE` / `REQUEST_CHANGES` / `COMMENT`)

After it completes, surface to the user:
- Review decision and key findings
- Link to the posted GitHub review
- Recommended next step (merge / fix and re-push)

**Save the run summary file now** (before firing stage_complete so the artifact is readable):
Save `plans/run_summary_${TICKET_lower}_${DATE}.md` with the full stage table (see Final Status Summary section below).

```bash
# 📊 Dashboard — review complete + workflow done
python dashboard/utils/client.py event --type stage_complete --stage pr_review --level success \
  --message "Review: <APPROVE|REQUEST_CHANGES> — posted to PR #$PR_NUMBER" \
  --data "{\"decision\":\"<verdict>\",\"pr_url\":\"<url>\",\"artifacts\":[{\"path\":\"plans/run_summary_${TICKET_lower}_${DATE}.md\",\"type\":\"markdown\",\"label\":\"Run Summary\"}]}" 2>/dev/null || true

python dashboard/utils/client.py event --type workflow_complete \
  --message "All stages complete — $TICKET ✓" --level success \
  --data "{\"ticket\":\"$TICKET\",\"pr_url\":\"<url>\",\"verdict\":\"<verdict>\"}" 2>/dev/null || true
```

---

## Final Status Summary

Render and display the summary table, then **save it as a shareable artifact**:

```
plans/run_summary_$TICKET_lower_<YYYY-MM-DD>.md
```

Content to save:
```markdown
# Run Summary — $TICKET: $TICKET_SUMMARY
Date    : <YYYY-MM-DD>
Repo    : $OWNER/$REPO
Branch  : $BRANCH
PR      : <PR URL>
Jira    : https://innocito.atlassian.net/browse/$TICKET

## Stage Results
| Stage | Status | Output |
|-------|--------|--------|
| Jira Fetch | ✅ | $TICKET: <summary> |
| Branch Created | ✅ | $BRANCH |
| Swagger Discovery | ✅ | <N> endpoints found |
| Test Cases Derived | ✅ | <N> cases → plans/manual_tests_*.md & .csv |
| Scripts Generated | ✅ | tests/ui/test_${TICKET_lower}_${MODULE}.py |
| Test Run | ✅/⚠️ | <N> passed / <M> failed |
| Postman Export | ✅/⏭️ | plans/postman_*.json (or skipped) |
| Commit + Push | ✅ | <commit hash> |
| PR Raised | ✅ | <PR URL> (draft: yes/no) |
| Jira Updated | ✅ | Transitioned → In Review |
| PR Review | ✅ | APPROVE / REQUEST_CHANGES |

## Coverage Delta
Before: $EXISTING_TEST_COUNT tests | After: $EXISTING_TEST_COUNT+<N> tests | Added: +<N>

## AC Coverage
| AC | Tests | All Passing? |
|----|-------|-------------|
| AC1 | test_pos_..., test_err_... | ✅ |
| AC2 | test_perm_... | ⚠️ 1 failing |
```

Confirm to the user: `"📄 Run summary saved to plans/run_summary_$TICKET_lower_<date>.md — ready to share!"`

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Jira ticket not found | Stop — ask user to verify `$TICKET` |
| `git remote` not set | Stop — ask user to configure remote origin |
| Branch already exists | Auto-append next available version suffix (`-v2`, `-v3`, …) — never reuse, never prompt |
| No ACs parseable from Jira | Show raw description, ask user to define test scope |
| `$MODULE` cannot be inferred | Ask user: "Which module does this ticket belong to?" |
| Page object missing for `$MODULE` | Run `write-page-object` skill first, then resume from Stage 4 |
| Tests still failing after fix attempt | Raise as draft, note failures in PR body and Jira comment |
| GitHub MCP not authenticated | Stop — prompt user to check `.mcp.json` |
