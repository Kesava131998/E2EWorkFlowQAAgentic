---
name: run-tests
description: Run the Playwright/pytest test suite with options for filtering, live output tailing, and Allure report viewing
tags: [testing, pytest, allure, runner, core]
---

# Skill: Run Tests

Runs the project test suite, streams live output, parses results, and optionally opens the Allure report.

> **Rules**: See `agents/rules.md`
> **Config**: `pytest.ini` (default flags), `config/settings.py` (timeouts), `.env` (credentials)

---

## When to invoke

- "Run the tests"
- "Run only diagnostics tests"
- "Show me the Allure report"
- "Re-run only failed tests"
- After generating new tests or fixing a page object

---

## Workflow

### Step 1 — Ensure venv is active and app is reachable
```bash
# Activate virtual environment
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate    # Windows

# Verify BASE_URL is accessible
python -c "from utils.config import BASE_URL; print('TARGET:', BASE_URL)"
```

### Step 2 — Choose run mode

**Run ALL tests (default — uses pytest.ini settings):**
```bash
pytest
```
This runs with `-v -s --html=reports/html/report.html --alluredir=reports/allure-results` automatically.

**Run a specific test FILE:**
```bash
pytest tests/<filename>.py -v
```

**Run a specific test FUNCTION:**
```bash
pytest tests/<filename>.py::<test_function_name> -v
```

**Run by keyword (partial name match):**
```bash
pytest -k "diagnostics" -v
```

**Run by parametrize mark:**
```bash
pytest tests/diagnostics_tests.py -k "CCM Software Version" -v
```

**Run ONLY failed tests from last run:**
```bash
pytest --lf -v
```

**Run with visible browser (overrides HEADLESS=true in .env):**
```bash
HEADLESS=false pytest -v
```

### Step 3 — Parse and summarise results
After the run completes, report to the user:
- Total: passed / failed / skipped / errors
- List of failed test names with their error summary
- Time taken

### Step 4 — Open Allure report (if requested or on failure)

**Serve interactive Allure report:**
```bash
allure serve reports/allure-results
```

**Or generate static HTML:**
```bash
allure generate reports/allure-results -o reports/allure-html --clean
```

**OR use the project's helper script:**
```bash
python run_tests.py
```
(This runs pytest + auto-opens Allure)

---

## Common failure patterns to check

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `TimeoutError` on locator | Stale locator or slow page load | Use `debug-test` skill |
| `fixture 'page' not found` | Wrong conftest scope | Check `tests/conftest.py` scope |
| `ModuleNotFoundError` | Missing import or bad page object name | Check `pages/` for typo |
| `AssertionError` | UI changed or expected result wrong | Update page object or assertion |
| `playwright._impl._errors.Error: Target page, context or browser has been closed` | fixture scope mismatch | Switch from `function` to `module` scope |

---

## Slow test mitigation

If tests are slow, check:
```bash
# Profile which tests take longest
pytest --durations=10
```

Consider raising `MEDIUM_TIMEOUT` or `LARGE_TIMEOUT` in `.env` for flaky environments.

---

## CI/headless guidance

For CI runs, ensure `.env` has:
```
HEADLESS=true
BROWSER=chromium
```

Or override inline:
```bash
HEADLESS=true pytest --tb=short -q
```
