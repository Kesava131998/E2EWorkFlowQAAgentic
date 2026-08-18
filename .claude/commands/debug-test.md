---
name: debug-test
description: Diagnose and fix a failing Playwright (@playwright/test) test — traces errors to root cause and suggests or applies fixes
tags: [debugging, playwright, mcp]
---

# Skill: Debug Test

Takes a failing test name, error log, or traceback, identifies the root cause
(stale locator, timeout, wrong fixture usage, assertion mismatch), and
either suggests or directly applies the fix.

Optionally uses Playwright MCP to inspect live elements if the app is running.

> **MCP Optional**: `@playwright/mcp@latest` (for live element inspection)
> **Rules**: `agents/rules.md`

---

## When to invoke

- "Test X is failing, fix it"
- "I'm getting a TimeoutError on this element"
- "All my payment-schedule tests started failing"
- Paste an error trace

---

## Workflow

### Step 1 — Collect failure information

Ask for (or read from context):
1. Test file and test title
2. Error message / trace (from terminal or Allure/HTML report)
3. When did it last pass? Any recent changes?
4. Is the application currently running / accessible?

If the test was run recently, check the trace/report output:
```
reports/allure-results/   ← look for failed test JSON attachments
test-results/             ← per-test trace.zip / screenshots / videos on failure
reports/html/             ← Playwright's own HTML report (npx playwright show-report reports/html)
```

Inspect a captured trace directly:
```bash
npx playwright show-trace test-results/<test-folder>/trace.zip
```

### Step 1b — Check if this is a known issue

Before diving into debugging, check if the failure is a known issue:
```bash
grep -rn "Known issue" tests/ --include="*.spec.js"
grep -rn "test.skip\|test.fixme" tests/ --include="*.spec.js"
```

If the failure matches a known issue already tracked in Jira:
- Add `test.skip(true, 'Known issue — https://innocito.atlassian.net/browse/SCRUM-XX')` inside the test body (or `test.fixme(...)` if it should still run and be reported as expected-fail)
- Do NOT attempt a fix — report the Jira ticket to the user instead

### Step 2 — Classify the error type

| Error Pattern | Category | Likely Cause |
|--------------|----------|-------------|
| `TimeoutError: locator.click: Timeout ... waiting for locator` | **Stale Locator** | Element changed, page slower, wrong locator |
| `TimeoutError: page.waitForLoadState: Timeout` | **Slow Page** | Network slow, `networkidle` too strict |
| `page.<x> is not a function` / `Cannot read properties of undefined` | **Wrong fixture/argument** | Page object constructed with wrong object, or method typo |
| `expect(received).toBe(expected)` failure | **Assertion Mismatch** | Text/state changed in UI |
| `Cannot find module '../pages/...'` | **Import Error** | File renamed, typo in `require(...)` path |
| `Target page, context or browser has been closed` | **Browser/context closed early** | Stray `page.close()`, unawaited navigation, or test finished before an async step resolved |

### Step 3a — Stale Locator Fix

Open the failed page object file (e.g., `pages/biller_activity_page.js`).
Find the locator referenced in the error.

**If Playwright MCP is available and app is running:**
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```
```
browser_navigate(url="<BASE_URL>/<path-where-element-lives>")
browser_snapshot()   ← returns accessibility tree
```
Find the element in the snapshot. Get a stable locator.
Update the matching `this.<locator>` assignment in the page object's constructor.

**Without Playwright MCP:**
- Review the XPath/CSS in context of the page
- Suggest alternative strategies (`id`, `data-testid`, ARIA role — see the Locator sourcing priority in `write-page-object.md`)
- If element is inside an iframe, note that separately (`page.frameLocator(...)`)

### Step 3b — Timeout Fix

Increase timeout for that specific action OR switch wait strategy:

```js
// Instead of:
await this.page.locator(this.element).click({ timeout: 3000 });

// Use:
await this.page.locator(this.element).waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
await this.page.locator(this.element).click();

// Or for load-state issues, replace networkidle with a specific element wait:
// Instead of: await page.waitForLoadState('networkidle');
// Use:
await this.page.locator(this.someIndicatorElement).waitFor({ state: 'visible', timeout: settings.PAGE_LOAD_TIMEOUT });
```

### Step 3c — Fixture/Isolation Fix

`@playwright/test` gives every test its own `page`/`context` by default (function-scoped) — there is no shared-session leakage to check, unlike a `module`-scoped pytest fixture. If a test depends on state from a previous test, that's a test design issue, not a fixture-scope issue:
- Make the test self-contained: perform its own login/navigation in the test body or a `test.beforeEach`
- If login is expensive, use Playwright's [storage state](https://playwright.dev/docs/auth) (`storageState` in `playwright.config.js` `use`) to reuse an authenticated session across tests, rather than sharing a single `page`

### Step 3d — Assertion Fix

Read the current element state using:
```js
await page.locator(this.element).innerText();
await page.locator(this.element).getAttribute('class');
```
Or via Playwright MCP snapshot. Then update the expected value in the assertion.

### Step 4 — Apply the fix

Edit the relevant file (page object or test). Run the fix:

```bash
# Rerun just the failing test by title
npx playwright test tests/<file>.spec.js -g "<test title>"
```

### Step 5 — Verify fix doesn't break others
```bash
npx playwright test tests/<affected_file>.spec.js
```

Confirm overall suite passes:
```bash
npx playwright test --last-failed
```

### Step 6 — Document in commit
Use `commit-changes` skill with message:
```
fix(<module>): update stale locator for <element> in <page>_page.js
```

---

## Common root causes in THIS project

| Module | Known fragile areas |
|--------|-------------------|
| `pages/biller_activity_page.js` | Dynamic `data-column-definition-name` grid cells and virtual-scroll rows — verify the column key still matches after UI changes |
| `pages/case_detail_page.js` | `[data-testid=...]` locators inside the Payment Schedule modal — check the modal hasn't been re-scoped in the DOM |
| `pages/login_page.js` | Azure AD SSO flow requires a second submit click ("Stay signed in?" prompt) — don't "fix" this away, it's expected |

---

## Playwright MCP — Accessibility Tree Tips

When using `browser_snapshot()`:
- Look for `role=button name="Create New Test"` → use `page.getByRole('button', { name: 'Create New Test' })`
- Look for `role=textbox name="Username"` → use `page.getByRole('textbox', { name: 'Username' })` or a `data-testid`/ARIA alternative
- Avoid using deeply nested `aria-*`/XPath paths — they change with UI rebuilds
