---
name: commit-changes
description: Review all staged changes against project rules, then compose and execute a conventional commit message
tags: [git, commit, review, workflow]
---

# Skill: Commit Changes

Reviews staged git changes against `agents/rules.md` before committing.
Catches common issues (debug code, raw timeouts, missing allure decorators)
and writes a Conventional Commits format message.

> **Rules**: `agents/rules.md` — "Pre-Commit Checks" and "Commit Conventions" sections

---

## When to invoke

- "Commit my changes"
- "Review and commit"
- "Stage and commit everything"
- User is about to push and wants a review first

---

## Workflow

### Step 1 — Show what is staged vs unstaged
```bash
git status
git diff --staged --stat
```
If nothing is staged, ask the user which files to stage:
```bash
git add <files>
# or
git add -A   # all changes
```

### Step 2 — Read the full staged diff
```bash
git diff --staged
```

Analyse the diff for violations of `agents/rules.md`:

| Check | What to look for |
|-------|-----------------|
| ❌ Raw integers in wait | `waitForTimeout(3000)` / `{ timeout: 3000 }` not via `settings.*` |
| ❌ Hardcoded credentials | strings matching URL/password patterns |
| ❌ console.log() debug statements | `console.log(` in page objects or tests |
| ❌ Missing test.step wrapping | new page action methods not wrapped in `test.step(...)` |
| ❌ BasePage not extended | new page class missing `extends BasePage` |
| ❌ Commented-out test code | large blocks of `//` without `// TODO:` |
| ❌ test.skip without reason | bare `test.skip()` calls with no message |
| ❌ Wrong test title prefix | test title not starting with `'pos: '` / `'err: '` / `'perm: '` |
| ⚠️ TODO comments | flag but don't block |
| ⚠️ No Jira reference | remind to add `Refs: SCRUM-XXX` in body if a ticket is active |

If violations are found:
- List them clearly with file + line number
- Ask user to fix or explicitly approve skipping each one

### Step 3 — Determine commit type and scope

Analyse the changes to select the correct type:
- New page object or test → `feat`
- Bug fix → `fix`
- Adding/modifying tests only → `test`
- Restructuring → `refactor`
- Config, deps, tooling → `chore`
- Docs/skill files → `docs`

Scope = the module or area changed (e.g., `login`, `diagnostics`, `reports`, `conftest`).

### Step 4 — Compose commit message

Format: `<type>(<scope>): <imperative summary>`

Rules for the summary line:
- Imperative mood: "add", "fix", "update" — not "added", "fixing"
- Max 72 characters
- No period at the end

**If a Jira ticket is active, include it in the body:**
```
feat(diagnostics): add CCM reboot parametrized test

Covers AC1 and AC3 from SCRUM-1.
Refs: SCRUM-1
```

**Examples without ticket:**
```
feat(diagnostics): add CCM reboot parametrized test
fix(login): handle network idle timeout on slow env
test(reports): add extension report validation coverage
chore(deps): pin playwright to 1.43.0
docs(agents): streamline skills and MCP configuration
```

### Step 5 — Execute the commit
```bash
git commit -m "<type>(<scope>): <summary>"
# or with body:
git commit -m "<type>(<scope>): <summary>" -m "<body paragraph>"
```

### Step 6 — Confirm and show log
```bash
git log --oneline -5
```
Show the user the last 5 commits to confirm the new one is correct.

---

## Pushing (if requested)

```bash
git push origin <current-branch>
```

If no remote is set yet:
```bash
git remote add origin https://github.com/EswarPrasadKona/ipc-playwright.git
git push -u origin <current-branch>
```

After push is confirmed, offer to run `/raise-pr` skill.
