---
name: jira-ticket
description: Fetch a Jira ticket, analyse acceptance criteria, map to existing tests or generate automation stubs
tags: [jira, mcp, ticket, planning, workflow]
---

# Skill: Jira Ticket

Fetches a Jira issue via `mcp-atlassian`, extracts acceptance criteria, maps them to
existing tests, and either reports coverage gaps or generates Playwright test stubs.

> **MCP Required**: `mcp-atlassian` (configured in `.mcp.json`)
> **Rules**: `agents/rules.md`

---

## When to invoke

- "Work on IPC-123" / "Show me ticket PROJ-456"
- "What tests cover this ticket?"
- "Automate the ACs in IPC-789"
- "List open tickets for the Diagnostics module"

---

## Available MCP Tools

| Tool | Purpose |
|------|---------|
| `jira_get_issue` | Fetch full issue by key (summary, description, ACs, status) |
| `jira_search` | JQL search — find issues by project, label, component, sprint |
| `jira_create_issue` | Create a new issue |
| `jira_update_issue` | Update fields on an existing issue |
| `jira_transition_issue` | Move issue to a new status |
| `jira_add_comment` | Add a comment to an issue |

---

## Workflow

### Step 1 — Fetch the ticket

**If ticket key is given (e.g. `SCRUM-123`)**:
```
jira_get_issue(issue_key="SCRUM-123")
```

**If no key — find by topic or sprint**:
```
jira_search(jql="project = SCRUM AND status = 'To Do' AND labels = 'automation'")
jira_search(jql="project = SCRUM AND sprint in openSprints() ORDER BY created DESC")
```

Extract from the response:
- Summary, Description, Status
- Acceptance Criteria (look in description, custom fields, or "Definition of Done")
- Labels / Components → map to page object modules

### Step 2 — Parse Acceptance Criteria

Look for patterns in the description:
```
Given ... When ... Then ...
AC1: <text>
- [ ] <checkbox item>
```

Number each AC: AC1, AC2, AC3…

### Step 3 — Explore existing tests first

Before generating anything, search for existing coverage:
```bash
grep -r "<keyword from ticket summary>" tests/ --include="*.spec.js" -l
grep -r "<keyword>" tests/ --include="*.spec.js" -n
```

Build a coverage table:

| AC | Status | Test File | Test Title |
|----|--------|-----------|---------------|
| AC1: User can log in | ✅ Covered | `tests/login.spec.js` | `'pos: login with valid user'` |
| AC2: Error on bad password | ❌ Not covered | — | — |
| AC3: Session persists | ⚠️ Partial | `tests/login.spec.js` | `'pos: login session persists'` |

### Step 4a — If fully covered
Report coverage. Offer next steps:
- Run tests → `/run-tests`
- Raise PR → `/raise-pr`

### Step 4b — If gaps found
Generate a stub per uncovered AC following the naming convention from `agents/rules.md`. Before writing any locators, check `pages/<module>_page.js` for existing ones to reuse (see the Locator sourcing rule in `.claude/CLAUDE.md`):

```js
const { test, expect } = require('@playwright/test');
const { epic, feature, story } = require('allure-js-commons');
const { <ModulePage> } = require('../pages/<module>_page');

test.describe('<TICKET-KEY>: <ticket summary>', () => {
  test.beforeEach(async () => {
    await epic('<TICKET-KEY>: <ticket summary>');
    await feature('<component>');
  });

  test('pos: <sanitized ac name>', async ({ page }) => {
    await story('AC<N>: <ac text>');
    // Jira: <TICKET-KEY>
    // AC: <full acceptance criteria text>
    const modulePage = new <ModulePage>(page);

    await test.step('Step 1: <first action>', async () => {
      // TODO: Implement
    });

    await test.step('Step N: Verify <expected outcome>', async () => {
      // TODO: Assert
    });
  });
});
```

Generate both `'pos: ...'` and `'err: ...'` stubs where the AC implies error handling.

Save to `tests/<ticket-key-lowercase>-<module>.spec.js`

### Step 5 — Offer manual test cases

**Always ask the user after generating stubs:**

> "Do you also want manual test cases documented for these ACs? I can produce:
> - **Happy path** scenarios (one per AC, step-by-step)
> - **Negative / error** scenarios (invalid inputs, missing permissions, edge states)
> - **Edge cases** (boundary values, empty states, concurrent actions)
>
> Which types would you like?"

If yes, produce a markdown table per AC:

| # | AC | Type | Scenario | Steps | Expected Result |
|---|----|----|----------|-------|-----------------|
| 1 | AC1 | Happy Path | Successful diagnostic execution | 1. Select component 2. Click Run | Status shows "Completed" |
| 2 | AC1 | Negative | Run diagnostic without selecting component | 1. Click Run without selection | Error: "No component selected" |
| 3 | AC2 | Edge Case | Run when precondition service is down | 1. Stop service 2. Attempt diagnostic | Error message shown with troubleshooting info |

Save to `plans/manual_tests_<ticket-key>_<date>.md` if the user wants to keep them.

### Step 6 — Update the Jira ticket (optional)
```
jira_add_comment(
  issue_key="SCRUM-123",
  body="Automation analysis complete.\n\nCoverage: X/Y ACs.\nGaps: AC2, AC3.\nStubs: tests/scrum123-<module>.spec.js\n\nNext: implement stubs and raise PR."
)
```

Or transition to In Progress once stubs are committed:
```
jira_transition_issue(issue_key="SCRUM-123", transition_id="<in-progress-id>")
```

### Step 7 — Report to user
- Ticket title + key + status
- Coverage table
- Stub file paths (if generated)
- Suggested next steps

---

## Connecting Jira → GitHub

- PR title MUST start with ticket: `[SCRUM-123] feat(module): <summary>`
- Commit body: `Refs: SCRUM-123`
- After committing stubs → run `/raise-pr` to open a PR linked to the ticket
