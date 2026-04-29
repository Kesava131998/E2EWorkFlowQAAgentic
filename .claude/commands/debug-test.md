---
name: debug-test
description: Diagnose and fix a failing Playwright/pytest test — traces errors to root cause and suggests or applies fixes
tags: [debugging, playwright, pytest, mcp]
---

# Skill: Debug Test

Takes a failing test name, error log, or traceback, identifies the root cause
(stale locator, timeout, wrong fixture scope, assertion mismatch), and
either suggests or directly applies the fix.

Optionally uses Playwright MCP to inspect live elements if the app is running.

> **MCP Optional**: `@playwright/mcp@latest` (for live element inspection)
> **Rules**: `agents/rules.md`

---

## When to invoke

- "Test X is failing, fix it"
- "I'm getting a TimeoutError on this element"
- "All my diagnostics tests started failing"
- Paste an error traceback

---

## Workflow

### Step 1 — Collect failure information

Ask for (or read from context):
1. Test file and function name
2. Error message / traceback (from terminal or Allure report)
3. When did it last pass? Any recent changes?
4. Is the application currently running / accessible?

If the test was run recently, check `pytestdebug.log`:
```
reports/allure-results/   ← look for failed test JSON attachments
pytestdebug.log           ← verbose pytest debug log
```

### Step 1b — Check if this is a known issue

Before diving into debugging, check if the failure is a known issue:
```bash
grep -r "Known issue" tests/ --include="*.py" -n
grep -r "pytest.skip" tests/ --include="*.py" -n
```

If the failure matches a known issue already tracked in Jira:
- Add a `pytest.skip("Known issue — https://innocito.atlassian.net/browse/SCRUM-XX")` to the test
- Tag with `@pytest.mark.known_issue`
- Do NOT attempt a fix — report the Jira ticket to the user instead

### Step 2 — Classify the error type

| Error Pattern | Category | Likely Cause |
|--------------|----------|-------------|
| `TimeoutError: waiting for locator` | **Stale Locator** | Element changed, page slower, wrong locator |
| `TimeoutError: waiting for load state` | **Slow Page** | Network slow, `networkidle` too strict |
| `fixture 'X' not found` | **Fixture Issue** | Wrong conftest scope, missing import |
| `AttributeError: 'NoneType'` | **None return** | Method returns nothing but test uses return value |
| `AssertionError` on `expect()` | **Assertion Mismatch** | Text/state changed in UI |
| `ModuleNotFoundError` | **Import Error** | File renamed, typo in import |
| `playwright._impl._errors.Error: Target closed` | **Browser Closed** | Fixture scope mismatch |
| `StaleElementReferenceError` | **DOM reload** | Page navigated before action completed |

### Step 3a — Stale Locator Fix

Open the failed page object file (e.g., `pages/diagnostics_page.py`).
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
playwright_navigate(url="<BASE_URL>/<path-where-element-lives>")
playwright_snapshot()   ← returns accessibility tree
```
Find the element in the snapshot. Get a stable locator.
Update `self.<locator>` in `__init__` of the page object.

**Without Playwright MCP:**
- Review the XPath/CSS in context of the page
- Suggest alternative strategies (ID, data-testid, ARIA role)
- If element is inside an iframe, note that separately

### Step 3b — Timeout Fix

Increase timeout for that specific action OR switch wait strategy:

```python
# Instead of:
self.page.locator(self.element).click(timeout=3000)

# Use:
self.page.locator(self.element).wait_for(state="visible", timeout=settings.LARGE_TIMEOUT)
self.page.locator(self.element).click()

# Or for load-state issues, replace networkidle with a specific element wait:
# Instead of: page.wait_for_load_state("networkidle")
# Use:
self.page.locator(self.some_indicator_element).wait_for(state="visible", timeout=settings.LARGE_TIMEOUT)
```

### Step 3c — Fixture Scope Fix

Check whether the `page` fixture in `tests/conftest.py` has scope `module`.
If a test is failing because the browser session is shared across tests and state leaks:

- For isolated tests: switch fixture scope to `function` in the root `conftest.py`
- For tests that need login: keep `module` scope but ensure login is idempotent

### Step 3d — Assertion Fix

Read the current element state using:
```python
page.locator(self.element).inner_text()
page.locator(self.element).get_attribute("class")
```
Or via Playwright MCP snapshot. Then update the expected value in the assertion.

### Step 4 — Apply the fix

Edit the relevant file (page object or test). Run the fix:

```bash
# Rerun just the failing test
pytest tests/<file>.py::<test_name> -v -s

# If parametrized, run the specific variant:
pytest tests/<file>.py -k "<parameter_value>" -v -s
```

### Step 5 — Verify fix doesn't break others
```bash
pytest tests/<affected_module_file>.py -v
```

Confirm overall suite passes:
```bash
pytest --lf   # last failed only
```

### Step 6 — Document in commit
Use `commit-changes` skill with message:
```
fix(<module>): update stale locator for <element> in <page>_page.py
```

---

## Common root causes in THIS project

| Module | Known fragile areas |
|--------|-------------------|
| `diagnostics_page.py` | Dynamic test IDs in grid rows — use `get_new_test_id()` pattern |
| `reports_page.py` | Iframe-based content — check iframe handling |
| `login_page.py` | `networkidle` can be slow — consider element-wait instead |
| `conftest.py (root)` | Video recording dir must exist before context creation |

---

## Playwright MCP — Accessibility Tree Tips

When using `playwright_snapshot()`:
- Look for `role=button name="Create New Test"` → use `role=button[name="Create New Test"]`
- Look for `role=textbox name="Username"` → use `input[name="userName"]` or ARIA alternative
- Avoid using deeply nested `aria-*` paths — they change with UI rebuilds
