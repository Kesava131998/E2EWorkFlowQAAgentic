---
name: e2e-workflow
description: Unified Jira-to-PR workflow — fetches a Jira ticket, creates QA subtasks, derives test cases, generates + runs tests, commits, raises PR, updates Jira, and spawns a separate review agent
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
- `$BRANCH` — computed in Stage 2
- `$MODULE` — computed in Stage 1 from Jira labels/components
- `$QA_DESIGN_KEY` — QA TC Design subtask key, captured in Stage 1b
- `$QA_EXEC_KEY` — QA TC Execution subtask key, captured in Stage 1b
- `$PR_NUMBER` — captured in Stage 7

---

## Workflow

---

### Stage 1 — Fetch Jira Ticket

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

---

### Stage 1b — QA Subtask Creation

Mirrors `jira-ticket` skill Step 6.1–6.4. Creates (or reuses) **exactly two**
QA subtasks — Design and Execution — that track test-case design and
execution for this ticket, independent of the parent Story's own status.

**This stage must never result in more than these two subtasks.** Any other
subtask under the parent (default onboarding tasks, unrelated pre-existing
subtasks, etc.) must be ignored entirely — it is never counted, created,
modified, or allowed to affect this logic.

**Expected subtask summaries** (Story summary appended dynamically):
```
QA TC Design - $TICKET_SUMMARY
QA TC Execution - $TICKET_SUMMARY
```

**Step 1 — Search existing subtasks:**
```
jira_search(jql="parent = $TICKET")
```

**Step 2 — Classify by pattern, never by count.**

Do NOT use a "both exist" / "none exist" style check — that is what allows
unrelated subtasks to be miscounted. Instead, iterate every returned subtask
and classify each individually:

- Summary contains `"QA TC Design"` → this is the Design subtask.
  Extract its issue key and store as `$QA_DESIGN_KEY`.
- Summary contains `"QA TC Execution"` → this is the Execution subtask.
  Extract its issue key and store as `$QA_EXEC_KEY`.
- Anything else (e.g. "Delegate this work item to...", or any other
  pre-existing/default subtask) → ignore completely. Do not touch it,
  do not count it, do not let it block or trigger creation logic.

**Step 3 — Create only whichever of the two is actually missing:**

```
if $QA_DESIGN_KEY is not set:
    jira_create_issue(
        parent=$TICKET,
        issue_type="Sub-task",
        summary="QA TC Design - $TICKET_SUMMARY"
    )
    # capture returned key as $QA_DESIGN_KEY

if $QA_EXEC_KEY is not set:
    jira_create_issue(
        parent=$TICKET,
        issue_type="Sub-task",
        summary="QA TC Execution - $TICKET_SUMMARY"
    )
    # capture returned key as $QA_EXEC_KEY
```

**Hard rule:** this stage issues at most 2 `jira_create_issue` calls per run
— one for Design, one for Execution — and only when Step 2's pattern match
didn't already find that subtask. It must never create a third subtask, and
it must never create a duplicate of Design or Execution just because some
unrelated subtask happens to exist under the same parent.

Confirm to the user:
```
🧩 QA subtasks ready
   Design    : $QA_DESIGN_KEY
   Execution : $QA_EXEC_KEY
```

> See **Parent Story Protection** near Stage 8 — `$TICKET` itself must never be auto-transitioned by this workflow.

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
- `SCRUM-1` + "Validate Diagnostic Tests Execution and Results…" → `scrum-1-validate-diagnostic-tests-execution`
- `SCRUM-42` + "Fix login timeout on slow networks" → `scrum-42-fix-login-timeout-on-slow-networks`
- `PROJ-7` + "Add user permission management screen" → `proj-7-add-user-permission-management-screen`

**Branch creation — always run these commands, every time the workflow is triggered:**

```bash
git checkout main
git pull origin main
git checkout -b $BRANCH
```

- **Never reuse an existing ticket branch.** If `$BRANCH` already exists locally or on remote, automatically append a version suffix (`-v2`, `-v3`, …) using the next available number — no prompt needed.
- **Never ask the user** whether to reuse or create — always create a fresh branch.

Confirm the final branch name to the user before proceeding.

> **Note:** The parent Story `$TICKET` is intentionally **not** auto-transitioned to "In Progress" here (or anywhere else in this workflow). Progress is tracked through the `$QA_DESIGN_KEY` / `$QA_EXEC_KEY` subtasks instead — see **Parent Story Protection** below. If you want the parent Story itself transitioned, do it explicitly outside this workflow.

---

### Stage 3 — Derive Manual Test Cases from Jira

**Source**: `$TICKET_DESCRIPTION` and `$TICKET_ACS` — no Excel file involved.
**Swagger API Reference**: none currently configured for this project. If a `$SWAGGER_URL` env var or project-specific OpenAPI spec URL is known, use it; otherwise skip Swagger Discovery entirely and proceed using ticket context alone.

**Swagger Discovery Step — only run this if a Swagger/OpenAPI spec URL is known for this project:**

Fetch the Swagger spec and identify all endpoints relevant to this ticket's domain:
```bash
curl -s "$SWAGGER_URL/v2/api-docs" | \
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
Store as `$SWAGGER_ENDPOINTS`. If no spec URL is configured, or the curl fails, note it and proceed using ticket context alone.

**API vs UI Analysis Strategy:**
1. **Explicit API Ticket**: If the ticket talks directly about automating an API, derive API-specific test cases. During generation, refer directly to the Swagger URL for endpoints, payloads, and schemas (if a spec is configured for this project).
2. **UI Flow Ticket**: If the ticket talks about a UI task/flow, derive UI test cases. During generation, we will intercept the network tab to find the APIs being called, and then cross-reference those APIs with the Swagger doc (if available) to generate independent API tests alongside the UI tests.

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

Save the output to two formats:
1. A Markdown file for easy reading:
```
plans/manual_tests_$TICKET_lower_<YYYY-MM-DD>.md
```
2. A CSV file (Excel compatible) for tracking and test management tools:
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
> <render the table>
>
> Would you like to add, remove, or modify any cases before I proceed?"

**Wait for user response.** Apply any requested changes, then continue.

---

**Question 2 — API test generation** *(ask only if this is a UI flow ticket; skip if it is an explicit API ticket — API tests are already in scope):*
> "Since this is a UI flow, I can intercept network calls during the UI test run to capture the underlying API calls, then cross-reference them with our Swagger docs to generate independent API tests.
>
> Would you like me to include API test generation?
> - **[Y] Yes** — generate a separate API test file alongside the UI tests
> - **[N] No** — UI tests only"

**Wait for user response.** Store as `$INCLUDE_API_TESTS` (true/false).

---

**Question 3 — Postman collection export** *(ask only if `$INCLUDE_API_TESTS = true` OR if this is an explicit API ticket):*
> "Would you also like me to export a **Postman-compatible collection** (`.json`) for these endpoints? It will be saved to `plans/` and, if `POSTMAN_API_KEY` and `POSTMAN_WORKSPACE_ID` are set in `.env`, uploaded directly to that Postman workspace.
> - **[Y] Yes** — export and upload Postman collection after tests run
> - **[N] No** — skip Postman export"

**Wait for user response.** Store as `$EXPORT_POSTMAN` (true/false).

---

Once all three questions are answered and the test-case set is signed off, **attach the test-case CSV to the QA TC Design subtask**, then mark it complete:

```
jira_attach_file(
  issue_key=$QA_DESIGN_KEY,
  file_path="plans/manual_tests_$TICKET_lower_<YYYY-MM-DD>.csv"
)
```

Confirm: `"📎 manual_tests_$TICKET_lower_<date>.csv attached to $QA_DESIGN_KEY"`

If the attach call fails (e.g. size limit, unsupported MIME type, permissions), report the failure to the user but do **not** block the rest of the workflow — proceed to the Done transition below regardless.

```
jira_transition_issue(issue_key=$QA_DESIGN_KEY, transition="Done")
```

If the `"Done"` transition name isn't valid for this workflow/project:
1. Fetch available transitions for `$QA_DESIGN_KEY`
2. Find the transition named **Done**
3. Retry using its `transition_id`

```
jira_transition_issue(issue_key=$QA_DESIGN_KEY, transition_id="<resolved id>")
```

Confirm: `"✅ $QA_DESIGN_KEY (QA TC Design) → Done"`

> This only transitions the **subtask**, never `$TICKET` itself — see Parent Story Protection.

Proceed to Stage 3b.

---

### Stage 3b — Test Naming Preview

**Before writing any files**, derive the proposed test function names from the approved test cases and present them:

> "Here are the **test function names** I'll generate:
>
> | # | Function Name | Type | AC |
> |---|--------------|------|----|
> | 1 | `test_pos_select_pickup_location` | Happy Path | AC1 |
> | 2 | `test_err_invalid_pickup_location` | Negative | AC1 |
> | 3 | `test_perm_guest_cannot_book` | RBAC | AC3 |
> | … | … | … | … |
>
> Shall I proceed with these names, or would you like to rename any?"

**Wait for user response.** Apply any renames, then proceed to Stage 4.

Also capture coverage baseline now:
```bash
find tests/ -name "*.py" | xargs grep -l "def test_" | wc -l
# and count total test functions
grep -r "def test_" tests/ --include="*.py" | wc -l
```
Store as `$EXISTING_TEST_COUNT`.

---

### Stage 4 — Generate Playwright Test Scripts

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

**Output file** (derived at runtime):
```
tests/test_$TICKET_lower_$MODULE.py
```
Examples: `tests/test_scrum1_diagnostics.py`, `tests/test_proj7_permissions.py`

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
/opt/miniconda3/bin/python -m pytest --collect-only tests/test_$TICKET_lower_$MODULE.py
```

---

### ⏸ HITL CHECKPOINT 1b — Test Execution Scope

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
/opt/miniconda3/bin/python -m pytest $TEST_FILTER -v --reruns=1 --reruns-delay=2
```

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

Open Allure report:
```bash
allure serve reports/allure-results
```

Execution itself (not the pass/fail outcome) is what QA TC Execution tracks, so mark it complete now that the run has finished:

```
jira_transition_issue(issue_key=$QA_EXEC_KEY, transition="Done")
```

If `"Done"` isn't a valid transition name, resolve the transition ID the same way as in Stage 3 (fetch available transitions, match on **Done**, retry with `transition_id`).

Confirm: `"✅ $QA_EXEC_KEY (QA TC Execution) → Done"`

> If `$SKIP_RUN = true`, do **not** transition `$QA_EXEC_KEY` — execution hasn't happened yet.

---

### Stage 5b — Export Postman Collection (if `$EXPORT_POSTMAN = true`)

**Skip this stage entirely if the user chose No at Checkpoint 1.**

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
2. If `POSTMAN_API_KEY` and `POSTMAN_WORKSPACE_ID` are set in `.env`, automatically upload it to Postman using `curl` (the API requires the JSON to be wrapped in a `{"collection": ...}` object). Otherwise, skip the upload and just report the local file path.
```bash
# Wrap the generated collection in the required format
jq '{collection: .}' plans/postman_$TICKET_lower_<YYYY-MM-DD>.json > plans/postman_payload.json

# Upload to the configured Postman workspace
curl --silent --location "https://api.getpostman.com/collections?workspace=$POSTMAN_WORKSPACE_ID" \
--header "X-API-Key: $POSTMAN_API_KEY" \
--header 'Content-Type: application/json' \
--data "@plans/postman_payload.json"

# Clean up the temporary payload file
rm plans/postman_payload.json
```

Confirm to the user: `"Postman collection exported locally and uploaded directly to the configured workspace in Postman!"` (or, if no workspace/key configured: `"Postman collection exported locally to plans/ — set POSTMAN_API_KEY and POSTMAN_WORKSPACE_ID in .env to enable auto-upload."`)

---

### ⏸ HITL CHECKPOINT 2 — Test Failure Gate

**If any tests FAILED:**

> "⚠️ **<N> test(s) failed:**
>
> <list of failures with error summaries>
>
> How would you like to proceed?
> - **[C] Continue** — commit and raise PR as draft (failures visible in PR)
> - **[F] Fix** — I'll diagnose and attempt to fix failures before committing"

- **Fix** → invoke `debug-test` skill per failing test, then re-run Stage 5 (note: `$QA_EXEC_KEY` was already marked Done after the first run and does not need to be re-transitioned)
- **Continue** → proceed with `$DRAFT = true`

If all tests passed → `$DRAFT = false`, proceed automatically.

---

### Stage 6 — Commit and Push

**Pre-commit checks** (from `agents/rules.md`) — block on any violation:
- [ ] No `print()` statements in page objects or tests
- [ ] No raw integer timeouts — must use `settings.*_TIMEOUT`
- [ ] All new page methods have `@allure.step(...)`
- [ ] Test function names follow `test_pos_` / `test_err_` / `test_perm_` convention
- [ ] No hardcoded credentials or URLs

Stage files:
```bash
git add tests/test_$TICKET_lower_$MODULE.py
git add plans/manual_tests_$TICKET_lower_*.md
git add plans/manual_tests_$TICKET_lower_*.csv
git add plans/postman_$TICKET_lower_*.json  # only if $EXPORT_POSTMAN = true
git add plans/run_summary_$TICKET_lower_*.md
# add any page objects created during this session
```

Commit message (derived from ticket):
```
test($MODULE): add automation tests for $TICKET

Covers <N> ACs from $TICKET: $TICKET_SUMMARY
Refs: $TICKET
```

Push:
```bash
git push -u origin $BRANCH
```

---

### Stage 7 — Raise Pull Request

**PR title** (derived at runtime):
```
[$TICKET] test($MODULE): <concise description from $TICKET_SUMMARY>
```

**PR body** includes:

```markdown
## 🎫 [$TICKET] $TICKET_SUMMARY
> Jira: https://innocito.atlassian.net/browse/$TICKET
> QA Design: https://innocito.atlassian.net/browse/$QA_DESIGN_KEY (Done)
> QA Execution: https://innocito.atlassian.net/browse/$QA_EXEC_KEY (Done)

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
python -m pytest tests/test_$TICKET_lower_$MODULE.py -v
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

---

### Stage 8 — Update Jira Ticket

**This workflow no longer posts any comment on the Jira ticket.** No
`jira_add_comment` call is made at any point, for any outcome (all passing,
partial failures, draft PR, or no new tests). The parent ticket's comment
thread is left completely untouched by this automation.

All run details (PR link, branch, QA subtask status, test results, coverage
delta) are instead:
- Displayed to the user in chat as the workflow progresses, and
- Saved to the shareable `plans/run_summary_$TICKET_lower_<date>.md` file
  (see **Final Status Summary** below).

If you want a summary posted to Jira, copy the relevant section from the run
summary file and paste it manually — this workflow will not do it for you.

#### Parent Story Protection

The parent Story `$TICKET` **MUST NEVER** be transitioned automatically by this workflow — only its `$QA_DESIGN_KEY` and `$QA_EXEC_KEY` subtasks are. The automation **must not** execute:

```
jira_transition_issue(
    issue_key=$TICKET,
    transition="Done"  # or "In Progress", "In Review", etc.
)
```

...unless the user explicitly requests it in the conversation.

Allowed pattern:
```
Story ($TICKET)      = unchanged (e.g. In Progress)
QA TC Design          = Done
QA TC Execution       = Done
```

Example outcomes:

| Story Status | QA Design | QA Execution | Final Story Status |
|--------------|-----------|---------------|--------------------|
| To Do | Done | Done | To Do |
| In Progress | Done | Done | In Progress |
| QA | Done | Done | QA |
| UAT | Done | Done | UAT |

---

### Stage 9 — PR Review Agent

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
| QA Subtasks Created | ✅ | Design: $QA_DESIGN_KEY, Execution: $QA_EXEC_KEY |
| Branch Created | ✅ | $BRANCH |
| Swagger Discovery | ✅ | <N> endpoints found |
| Test Cases Derived | ✅ | <N> cases → plans/manual_tests_*.md & .csv |
| CSV Attached to QA Design | ✅/⚠️ | $QA_DESIGN_KEY (or: attach failed, see note) |
| QA TC Design → Done | ✅ | $QA_DESIGN_KEY |
| Scripts Generated | ✅ | tests/test_$TICKET_lower_$MODULE.py |
| Test Run | ✅/⚠️ | <N> passed / <M> failed |
| QA TC Execution → Done | ✅ | $QA_EXEC_KEY |
| Postman Export | ✅/⏭️ | plans/postman_*.json (or skipped) |
| Commit + Push | ✅ | <commit hash> |
| PR Raised | ✅ | <PR URL> (draft: yes/no) |
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
| QA subtasks already exist | Reuse their keys as `$QA_DESIGN_KEY`/`$QA_EXEC_KEY` (matched by summary pattern, not count) — never create duplicates, never let unrelated subtasks affect this |
| `"Done"` transition unavailable for a subtask | Fetch available transitions, match by name, retry with `transition_id` |
| Page object missing for `$MODULE` | Run `write-page-object` skill first, then resume from Stage 4 |
| Tests still failing after fix attempt | Raise as draft, note failures in PR body and Jira comment; `$QA_EXEC_KEY` still marked Done (execution occurred) |
| GitHub MCP not authenticated | Stop — prompt user to check `.mcp.json` |
| Any outcome at Stage 8 | Never post a Jira comment — report results in chat and in `plans/run_summary_*.md` only |
| CSV attach to `$QA_DESIGN_KEY` fails | Report the failure to the user, continue the workflow anyway (does not block the "Done" transition or any later stage) |
