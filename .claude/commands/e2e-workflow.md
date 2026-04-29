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

```bash
git checkout main
git pull origin main
git checkout -b $BRANCH
```

Confirm branch name to the user before proceeding.

---

### Stage 3 — Derive Manual Test Cases from Jira

**Source**: `$TICKET_DESCRIPTION` and `$TICKET_ACS` — no Excel file involved.

For each AC or requirement found, produce:

| # | AC | Type | Scenario | Steps | Expected Result |
|---|----|------|----------|-------|-----------------|
| 1 | AC1 | Happy Path | … | 1. … 2. … | … |
| 2 | AC1 | Negative | … | 1. … | Error shown |
| 3 | AC2 | Edge Case | … | … | … |

Generate at minimum:
- One `Happy Path` per AC
- `Negative` cases where the AC implies error/validation handling
- `Edge Case` where boundary values or empty states are implied

Save to:
```
plans/manual_tests_$TICKET_lower_<YYYY-MM-DD>.md
```

---

### ⏸ HITL CHECKPOINT 1 — Test Case Review

**STOP. Present the derived test cases to the user.**

> "Here are the **<N> test cases** I derived from **$TICKET: $TICKET_SUMMARY**.
>
> <render the table>
>
> Shall I proceed to generate Playwright test scripts from these?
> You can ask me to add, remove, or modify any cases before I generate."

**Wait for explicit user approval before continuing.**

---

### Stage 4 — Generate Playwright Test Scripts

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
pytest --collect-only tests/test_$TICKET_lower_$MODULE.py
```

---

### Stage 5 — Run Tests

```bash
source venv/bin/activate
pytest tests/test_$TICKET_lower_$MODULE.py -v
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
Test Cases Derived  ✅        <N> cases → plans/manual_tests_*.md
Scripts Generated   ✅        tests/test_$TICKET_lower_$MODULE.py
Test Run            ✅/⚠️     <N> passed / <M> failed
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
| Branch already exists | Ask: checkout existing branch or append `-v2` suffix |
| No ACs parseable from Jira | Show raw description, ask user to define test scope |
| `$MODULE` cannot be inferred | Ask user: "Which module does this ticket belong to?" |
| Page object missing for `$MODULE` | Run `write-page-object` skill first, then resume from Stage 4 |
| Tests still failing after fix attempt | Raise as draft, note failures in PR body and Jira comment |
| GitHub MCP not authenticated | Stop — prompt user to check `.mcp.json` |
