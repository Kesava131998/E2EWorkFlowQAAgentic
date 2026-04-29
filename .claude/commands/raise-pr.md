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
| 📄 Page Objects | `pages/*.py` |
| 🧪 Tests | `tests/*.py` |
| ⚙️ Config / Utils | `utils/`, `config/`, `conftest.py` |
| 📚 Skills / Docs | `agents/`, `.claude/` |
| 🔧 Setup | `requirements.txt`, `pytest.ini`, `run_tests.py` |

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
- `pages/X_page.py` — Added `method_name()` for Y interaction

### 🧪 Tests
- `tests/test_X.py` — Covers scenario A with B parametrize variants

### ⚙️ Config / Utils
- `config/settings.py` — Added `NEW_TIMEOUT`

## Test Coverage

| Test File | Scenarios Covered | Status |
|-----------|-------------------|--------|
| `test_diagnostics.py` | CCM Software Version, CCM Time Verification | ✅ Passing |
| `test_reboot.py` | CCM Reboot, MM Reboot | ✅ Passing |

## How to test

```bash
pytest tests/<changed-file>.py -v
allure serve reports/allure-results
```

## Checklist

- [ ] All new page classes inherit `BasePage`
- [ ] All page methods have `@allure.step(...)` decorator
- [ ] No hardcoded credentials or URLs
- [ ] No raw integer timeouts (uses `settings.*_TIMEOUT`)
- [ ] No debug `print()` statements
- [ ] Tests collected without error (`pytest --collect-only`)
- [ ] Test function names follow `test_pos_` / `test_err_` / `test_perm_` convention
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
