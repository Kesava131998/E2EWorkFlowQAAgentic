---
name: run-tests
description: Run the Playwright (@playwright/test) test suite with options for filtering, live output tailing, and Allure report viewing
tags: [testing, playwright, allure, runner, core]
---

# Skill: Run Tests

Runs the project test suite, streams live output, parses results, and optionally opens the Allure report.

> **Rules**: See `agents/rules.md`
> **Config**: `playwright.config.js` (default flags/projects), `config/settings.js` (timeouts), `.env` (credentials)

---

## When to invoke

- "Run the tests"
- "Run only diagnostics tests"
- "Show me the Allure report"
- "Re-run only failed tests"
- After generating new tests or fixing a page object

---

## Workflow

### Step 1 — Ensure dependencies are installed and app is reachable

```bash
# Install dependencies (first run / after pulling changes)
npm ci
npx playwright install --with-deps

# Verify BASE_URL is accessible
node -e "require('dotenv').config(); console.log('TARGET:', process.env.BASE_URL)"
```

### Step 2 — Clear stale artifacts, then choose run mode

`reports/allure-results` and `test-results` are never cleaned automatically — results
from every prior run accumulate on disk and get merged into the next Allure report
unless removed first. Clear them before every run (running via `npm test`/`npm run
test:*` does this automatically via the `pretest*` npm hooks; if invoking `npx
playwright test` directly, run this first):
```bash
rm -rf reports/allure-results/* test-results/* 2>/dev/null || true
```

**Run ALL tests (default — uses `playwright.config.js` settings):**
```bash
npx playwright test
```
This runs with the reporters configured in `playwright.config.js` (`html` + `allure-playwright` + `list`) automatically.

**Run a specific test FILE:**
```bash
npx playwright test tests/<filename>.spec.js
```

**Run a specific test by TITLE:**
```bash
npx playwright test tests/<filename>.spec.js -g "<test title>"
```

**Run by keyword (partial title match, across all files):**
```bash
npx playwright test -g "diagnostics"
```

**Run against a specific browser project:**
```bash
npx playwright test --project=chromium
```

**Run ONLY failed tests from the last run:**
```bash
npx playwright test --last-failed
```

**Run with visible browser (overrides HEADLESS=true in .env):**
```bash
npx playwright test --headed
```

### Step 3 — Parse and summarise results
After the run completes, report to the user:
- Total: passed / failed / skipped / flaky
- List of failed test names with their error summary
- Time taken

### Step 4 — Open the report (if requested or on failure)

**Open Playwright's own HTML report** (auto-launches the default browser):
```bash
npx playwright show-report reports/html
```

**Serve interactive Allure report** (also auto-launches the browser; since Step 2
cleared `reports/allure-results` before this run, it reflects only this run):
```bash
npx allure serve reports/allure-results
```

**Or generate static HTML:**
```bash
npx allure generate reports/allure-results -o reports/allure-report --clean
```

**Or view Playwright's own HTML report:**
```bash
npx playwright show-report reports/html
```

**OR use the project's npm scripts:**
```bash
npm test              # runs the suite
npm run allure:serve  # runs + opens Allure
npm run report        # opens the Playwright HTML report
```

---

## Common failure patterns to check

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `TimeoutError` on locator | Stale locator or slow page load | Use `debug-test` skill |
| `Cannot find module '../pages/...'` | Wrong relative import path or bad page-object filename | Check `pages/` for typo |
| `TypeError: page.locator is not a function` | Wrong fixture/argument passed to a page-object constructor | Verify the test destructures `{ page }` from the test callback |
| `expect(...).toBe(...)` failure | UI changed or expected result wrong | Update page object or assertion |
| `page.click: Target closed` | Test navigated away or closed context mid-step | Check for a stray `page.close()`/unawaited navigation |

---

## Slow test mitigation

If tests are slow, check:
```bash
# Playwright reports per-test duration in its HTML/list reporter output automatically
npx playwright test --reporter=list
```

Consider raising `PAGE_LOAD_TIMEOUT` or `TIMEOUT` in `.env` for flaky environments.

---

## CI/headless guidance

For CI runs, ensure `.env` has:
```
HEADLESS=true
BROWSER=chromium
```

Or override inline:
```bash
HEADLESS=true npx playwright test --reporter=dot
```
