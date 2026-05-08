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

---

### Stage 3 — Derive Manual Test Cases from Jira

**Source**: `$TICKET_DESCRIPTION` and `$TICKET_ACS` — no Excel file involved.
**Swagger API Reference**: `https://beta.drivejoulez.com:8443/joulez-service/swagger-ui.html#/`

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

**STOP. Present the derived test cases to the user.**

> "Here are the **<N> test cases** I derived from **$TICKET: $TICKET_SUMMARY**.
>
> <render the table>
>
> *(If the ticket was primarily a UI flow, add this prompt:)*
> "Since this is a UI flow, I can run the UI tests while intercepting the network tab to capture the underlying API calls. I will then cross-reference them with our Swagger documentation to automatically generate robust API tests. Would you like me to include API test generation?"
>
> *(If API test generation is in scope — either explicit API ticket or UI flow with interception — add this prompt:)*
> "Would you also like me to export a **Postman-compatible collection** (`.json`) for these endpoints? It will be saved to `plans/` and can be imported directly into Postman or Insomnia for manual exploratory testing.
> - **[Y] Yes** — export Postman collection after tests run
> - **[N] No** — skip Postman export"
>
> Store user's choice as `$EXPORT_POSTMAN` (true/false).
>
> Shall I proceed to generate Playwright test scripts?"

**Wait for explicit user approval before continuing.**

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

### Stage 5 — Run Tests

```bash
/opt/miniconda3/bin/python -m pytest tests/test_$TICKET_lower_$MODULE.py -v
```

Parse and display:
- Total: passed / failed / skipped / errors
- Failed test names with error summaries
- Time taken

Open Allure report:
```bash
allure serve reports/allure-results
```

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

- **Fix** → invoke `debug-test` skill per failing test, then re-run Stage 5
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
git add plans/postman_$TICKET_lower_*.json  # only if $EXPORT_POSTMAN = true
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
- Summary from `$TICKET_DESCRIPTION`
- Jira link: `https://innocito.atlassian.net/browse/$TICKET`
- Test coverage table (ACs → test functions)
- How to run locally
- Standard checklist from `raise-pr.md`

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

```
jira_add_comment(
  issue_key=$TICKET,
  body="✅ Automation PR raised: <PR URL>\n\nBranch: `$BRANCH`\nTests: <N> cases covering <M> ACs.\nStatus: <All passing | Draft — <N> failures>"
)
```

Confirm to the user that Jira has been updated.

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

```
Ticket  : $TICKET — $TICKET_SUMMARY
Branch  : $BRANCH
Module  : $MODULE
Repo    : $OWNER/$REPO

Stage               Status    Output
─────────────────── ──────── ──────────────────────────────────────
Jira Fetch          ✅        $TICKET: <summary>
Branch Created      ✅        $BRANCH
Test Cases Derived  ✅        <N> cases → plans/manual_tests_*.md & .csv
Scripts Generated   ✅        tests/test_$TICKET_lower_$MODULE.py
Test Run            ✅/⚠️     <N> passed / <M> failed
Postman Export      ✅/⏭️     plans/postman_$TICKET_lower_<date>.json (or skipped)
Commit + Push       ✅        <commit hash>
PR Raised           ✅        <PR URL> (draft: yes/no)
Jira Updated        ✅        Comment added to $TICKET
PR Review           ✅        APPROVE / REQUEST_CHANGES
```

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
