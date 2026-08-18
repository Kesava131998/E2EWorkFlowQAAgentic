---
name: raise-pr
description: Create a comprehensive, well-structured GitHub Pull Request from the current branch using GitHub MCP
tags: [github, pr, workflow, mcp]
---

# Skill: Raise Pull Request

Pushes the current branch (if needed) and creates a structured GitHub PR with a rich body
including change summary, test coverage, checklist, and Allure report reference.

> **MCP Required**: GitHub MCP server (pre-configured in `.mcp.json`)
> **Rules**: See `agents/rules.md` — Commit Conventions, PR and Issue Rules

---

## When to invoke

- "Raise a PR"
- "Open a pull request for my changes"
- "Create PR to main"
- After running `commit-changes` skill and changes are pushed

---

## Workflow

### Step 1 — Get context
```bash
git branch --show-current
git log main..HEAD --oneline
git diff main..HEAD --stat
git diff main..HEAD --name-only
```

Also check the active Jira ticket (if known) — it goes in the PR title.

### Step 2 — Ensure branch is pushed
```bash
git push origin <current-branch>
```
If remote not configured:
```bash
git remote add origin https://github.com/EswarPrasadKona/ipc-playwright.git
git push -u origin <current-branch>
```

### Step 3 — Categorise changes

| Category | Files |
|----------|-------|
| 📄 Page Objects | `pages/*.js` |
| 🧪 Tests | `tests/*.spec.js` |
| ⚙️ Config / Utils | `utils/`, `config/`, `playwright.config.js` |
| 📚 Skills / Docs | `agents/`, `.claude/` |
| 🔧 Setup | `package.json`, `playwright.config.js` |

### Step 4 — Build PR title

**Format**: `[SCRUM-XXX] <type>(<scope>): <summary>`

- If a Jira ticket is associated, it MUST be the first thing in the title
- If no Jira ticket, omit the brackets: `<type>(<scope>): <summary>`
- Keep the title under 72 characters after the ticket prefix

**Examples:**
```
[SCRUM-1] feat(diagnostics): add CCM reboot parametrized tests
[SCRUM-4] fix(login): handle networkidle timeout on slow environments
docs(agents): streamline Claude skills and MCP configuration
```

### Step 5 — Build PR body

```markdown
## Summary

<!-- 1-3 sentence description of what this PR does -->

## Changes

### 📄 Page Objects
- `pages/x_page.js` — Added `methodName()` for Y interaction

### 🧪 Tests
- `tests/x.spec.js` — Covers scenario A with B data-driven variants

### ⚙️ Config / Utils
- `config/settings.js` — Added `NEW_TIMEOUT`

## Test Coverage

| Test File | Scenarios Covered | Status |
|-----------|-------------------|--------|
| `arw2579-payment-schedule.spec.js` | Modal open/close, payer eligibility, schedule save | ✅ Passing |

## How to test

```bash
npx playwright test tests/<changed-file>.spec.js
npx allure serve reports/allure-results
```

## Checklist

- [ ] All new page classes extend `BasePage`
- [ ] All page action methods wrapped in `test.step(...)`
- [ ] No hardcoded credentials or URLs
- [ ] No raw integer timeouts (uses `settings.*_TIMEOUT`)
- [ ] No debug `console.log()` statements left in
- [ ] Tests collected without error (`npx playwright test --list`)
- [ ] Test titles follow `'pos: ...'` / `'err: ...'` / `'perm: ...'` convention
- [ ] Allure report generated and verified locally

## Related

- Jira: <!-- [SCRUM-XXX](https://innocito.atlassian.net/browse/SCRUM-XXX) -->
```

### Step 6 — Create PR via GitHub MCP
```
mcp__github__create_pull_request(
  owner="EswarPrasadKona",
  repo="ipc-playwright",
  title="[SCRUM-XXX] <type>(<scope>): <summary>",
  head="<current-branch>",
  base="main",
  body="<rendered body from Step 5>",
  draft=false
)
```

### Step 7 — Share PR link with user
- PR URL
- PR number
- Summary of what was included

---

## Tips

- Use `draft=true` for PRs that are WIP or have failing tests
- If the branch contains multiple logical changes, suggest splitting into multiple PRs
- Always target `main` unless user specifies otherwise
- After PR is created, offer to run `/review-pr` on it immediately
