---
name: review-pr
description: Fetch an open GitHub PR, analyse the diff against project rules, and post a structured review comment
tags: [github, pr, review, mcp, workflow]
---

# Skill: Review Pull Request

Fetches a PR from GitHub, reads all changed files, analyses them against `agents/rules.md`,
and posts a structured review (APPROVE / REQUEST_CHANGES / COMMENT).

Designed to be run by a **second agent** independently from the author — true async code review.

> **MCP Required**: GitHub MCP server (pre-configured in `.mcp.json`)
> **Rules**: `agents/rules.md` — all sections apply

---

## When to invoke

- "Review PR #42"
- "Can you review the open PRs?"
- "Check if this PR follows our standards"

---

## Workflow

### Step 1 — Listing open PRs (when no number given)

If no PR number is provided, list the open pull requests:
```
mcp__github__list_pull_requests(owner="EswarPrasadKona", repo="ipc-playwright", state="open")
```
Show user a list, let them pick which to review.

### Step 2 — Get PR Details (run in parallel)

For the target PR number, fetch the necessary context simultaneously:
- `mcp__github__get_pull_request` — PR metadata (title, description, author, branch)
- `mcp__github__get_pull_request_files` — Changed files with diff patches
- `mcp__github__get_pull_request_status` — CI/status check results
- `mcp__github__get_pull_request_reviews` — Existing reviews

For each file from the files tool, read its patch/diff content.

### Step 3 — Analyse each changed file

**For files in `pages/`:**
- [ ] Class inherits `BasePage`?
- [ ] All locators defined in `__init__` as `self.*`?
- [ ] All methods have `@allure.step(...)`?
- [ ] No assertions inside page methods?
- [ ] No raw `page.locator(...)` strings inside methods (should use `self.*`)?

**For files in `tests/`:**
- [ ] File starts with `test_`?
- [ ] Test function names use `test_pos_` / `test_err_` / `test_perm_` prefix?
- [ ] `test_err_` tests assert the specific error message — not just that an exception occurred?
- [ ] Uses `page` fixture — not direct `sync_playwright()`?
- [ ] Steps wrapped in `with allure.step(...)`?
- [ ] Parametrize used for data-driven variants?
- [ ] No raw integer timeouts — uses `settings.*_TIMEOUT`?
- [ ] Known issue workarounds use `pytest.skip("Known issue — <url>")` with ticket link?

**For `conftest.py`:**
- [ ] Fixture scope is appropriate (`module` for login session, `function` for isolated)?
- [ ] Screenshot on failure is hooked?

**For `utils/` or `config/`:**
- [ ] No hardcoded credentials?
- [ ] `settings.py` uses `os.getenv()` with sensible defaults?

**For `requirements.txt`:**
- [ ] No yanked/vulnerable packages?
- [ ] Versions pinned or reasonably bounded?

### Step 4 — Build review body

Use this template:

```markdown
## PR Review — playwright_python Standards Check

**PR**: #<number> — <title>
**Author**: @<author>
**Reviewed by**: AI Agent (.claude/skills/review-pr.md)

---

### ✅ Passes

- <list of things done correctly>

### ❌ Issues (must fix before merge)

| File | Line | Issue | Rule |
|------|------|-------|------|
| `pages/x_page.py` | 23 | Missing `@allure.step` on `click_button()` | rules.md §3 |
| `tests/x_test.py` | 41 | Raw timeout `3000` — use `settings.SMALL_TIMEOUT` | rules.md §11 |

### ⚠️ Suggestions (optional improvements)

- `pages/x_page.py` — Consider using CSS selector instead of XPath on line 17 for resilience
- `tests/x_test.py` — This test is data-driven but not using `@pytest.mark.parametrize`

### 📋 Summary

<!-- APPROVE / REQUEST_CHANGES / COMMENT with reasoning -->
```

### Step 5 — Post review via GitHub MCP

Post a **sophisticated, comprehensive review** that captures every finding — both issues and positives.
The review body must be thorough: include every ❌ issue and ⚠️ suggestion with precise file + line context, reasoning, and the rule being violated. Do not omit or summarise findings — a sparse review is a bad review.

Additionally, post **inline comments** on specific diff lines for each ❌ issue and ⚠️ suggestion using the `comments` array. Each inline comment must reference the exact file path and diff position.

```
mcp__github__create_pull_request_review(
  owner="EswarPrasadKona",
  repo="ipc-playwright",
  pull_number=<number>,
  body="<full review body from Step 4>",
  event="APPROVE" | "REQUEST_CHANGES" | "COMMENT",
  comments=[
    {
      path: "<file path>",
      position: <diff hunk line number>,
      body: "❌ **Issue**: <description>\n\n**Rule**: rules.md §<section>\n\n**Fix**: <concrete suggestion>"
    },
    ...
  ]
)
```

**Inline comment guidelines:**
- Every ❌ issue → mandatory inline comment with fix suggestion
- Every ⚠️ suggestion → inline comment explaining the improvement
- Write comments as if a senior engineer is reviewing — precise, actionable, not vague
- Reference the specific rule or pattern from `agents/rules.md`

**Decision logic:**
- `APPROVE` — No ❌ issues found and CI checks are passing.
- `REQUEST_CHANGES` — One or more ❌ issues found or CI is failing.
- `COMMENT` — Minor ⚠️ suggestions only, no blockers.

### Step 6 — Merge (if approved)

If the PR review logic leads to an `APPROVE` decision, request to merge the PR:
```
mcp__github__merge_pull_request(
  owner="EswarPrasadKona",
  repo="ipc-playwright",
  pull_number=<number>,
  merge_method="squash"
)
```

### Step 7 — Report back to user
- Link to the review posted
- Summary of verdict and key findings
- Status of the merge (if applicable)

## Notes

- This skill does **static analysis** of the diff — it doesn't run tests locally, relying on `mcp_github_get_pull_request_status`.
- For local runtime validation, use `run-tests` skill on the PR's branch.
- Review comments are posted **both** at the PR level (summary body) **and** inline on specific diff lines — every finding must appear in both places.
- The review must be sophisticated and exhaustive: no finding should be omitted or glossed over. A reviewer reading only the inline comments should get the full picture.
- The review is meant to complement, not replace, human review.
