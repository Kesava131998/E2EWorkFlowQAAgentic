---
name: project-review
description: Full codebase audit — checks coverage, locator quality, architecture compliance, and writes a report to plans/
tags: [review, audit, planning, quality]
---

# Skill: Project Review

Performs a comprehensive static audit of the entire `playwright_python` codebase.
Checks coverage gaps, architecture compliance, locator hygiene, fixture design, and
report configuration. Writes findings as a dated markdown report to `plans/`.

> **Rules**: `agents/rules.md` — all sections
> **Output**: `plans/review-<YYYY-MM-DD>.md`

---

## When to invoke

- "Do a project review"
- "Audit the codebase"
- "What's the state of our test suite?"
- Before a major release or sprint planning
- When onboarding a new team member

---

## Workflow

### Step 1 — Scan directory structure
Map out all files in: `pages/`, `tests/`, `utils/`, `config/`, root-level configs.

Build an inventory:
```
pages/        : base_page.py, login_page.py, diagnostics_page.py, reports_page.py
tests/        : conftest.py, diagnostics_tests.py, reboot_validation.py, ...
utils/        : config.py, test_generator.py, pdf_reader.py
config/       : settings.py
```

### Step 2 — Architecture compliance check

**For each file in `pages/`:**
- [ ] Inherits `BasePage`?
- [ ] All locators in `__init__`?
- [ ] All methods have `@allure.step`?
- [ ] No assertions in page methods?
- [ ] Imports are clean (only `allure`, `BasePage`, `playwright`)?

**For each file in `tests/`:**
- [ ] Filename starts with `test_`?
- [ ] Uses `page` fixture from conftest?
- [ ] All steps in `with allure.step(...)`?
- [ ] Uses `settings.*_TIMEOUT` not raw ints?
- [ ] Allure metadata (`@allure.title`, `@allure.description`) present?
- [ ] Parametrize used wherever there are data variants?

**For `conftest.py` files:**
- [ ] Root conftest handles screenshot on failure?
- [ ] Root conftest handles allure-results cleanup?
- [ ] `tests/conftest.py` scope is `module` for login session?

**For `config/settings.py`:**
- [ ] All timeouts are `os.getenv()` with defaults?
- [ ] No secrets in settings file?

**For `utils/config.py`:**
- [ ] Uses `load_dotenv()`?
- [ ] No hardcoded values?

### Step 3 — Locator hygiene audit

For each page object, check locators for fragility:
- XPath with `text()` matching → fragile (UI text changes)
- Deep nested XPath → fragile (DOM restructure)
- Positional CSS (`nth-child`) → fragile
- Stable: `id`, `data-*` attributes, ARIA roles

Flag each fragile locator with a risk rating: 🔴 High / 🟡 Medium / 🟢 Low

### Step 4 — Coverage gap analysis

Map each page object to tests that use it:
```
DiagnosticPage → diagnostics_tests.py, reboot_validation.py ✅
LoginPage      → tests/conftest.py (fixture), test_2943.py ✅
ReportsPage    → extension_report_validation.py, ... ✅
BasePage       → (base class, not tested directly) ℹ️
```

Identify:
- Page objects with no test coverage
- Tests that access the app without going through a page object (direct `page.locator()` calls in tests)

### Step 5 — Dead code check

Look for:
- Locators defined in `__init__` but never used in any method
- Methods defined in page objects but never called from any test
- Imported modules never used

### Step 6 — Configuration review

- Is `.env` in `.gitignore`?
- Does `pytest.ini` `testpaths` still match actual test locations?
- Is Allure version compatible with installed `allure-pytest`?
- Does `requirements.txt` match what's actually installed in venv?

```bash
pip list --format=columns | grep -E "playwright|pytest|allure|pandas"
```

### Step 7 — Summarise findings and write report

Write the report to `plans/review-<YYYY-MM-DD>.md`:

```markdown
# Project Review — playwright_python
**Date**: <YYYY-MM-DD>
**Reviewer**: AI Agent (.claude/skills/project-review.md)

---

## Executive Summary

| Area | Status | Issues |
|------|--------|--------|
| Architecture (POM) | ✅ / ⚠️ / ❌ | N |
| Test Coverage | ✅ / ⚠️ / ❌ | N |
| Locator Quality | ✅ / ⚠️ / ❌ | N |
| Config / Environment | ✅ / ⚠️ / ❌ | N |
| Dead Code | ✅ / ⚠️ / ❌ | N |

**Overall Health: 🟢 Good / 🟡 Needs Attention / 🔴 Critical Issues**

---

## 1. Architecture Compliance

### Issues Found
<!-- table of violations -->

### Recommendations
<!-- ordered by impact -->

---

## 2. Test Coverage

### Page Object Coverage Map
<!-- table -->

### Uncovered Scenarios
<!-- list of gaps -->

---

## 3. Locator Quality

### Fragile Locators
<!-- table with risk rating -->

### Recommendations
<!-- suggest stable alternatives -->

---

## 4. Configuration

<!-- findings -->

---

## 5. Dead Code

<!-- unused methods/locators -->

---

## 6. Action Plan

| Priority | Action | File | Effort |
|----------|--------|------|--------|
| P1 | Fix raw timeouts in reboot_validation.py | tests/ | Low |
| P2 | Add @allure.step to 3 methods in reports_page.py | pages/ | Low |
| P3 | Replace fragile XPath in diagnostics_page.py | pages/ | Medium |
```

### Step 8 — Tell the user

- Path to the generated plan file: `plans/review-<date>.md`
- Top 3 highest-priority findings
- Suggested next skills to run (e.g., `debug-test` for failures, `write-page-object` for gaps)

---

## Notes

- This is a **static analysis** skill — it does not run tests
- Combine with `run-tests` skill for runtime validation
- Re-run periodically (e.g., before each release sprint) to track improvement over time
- Each report in `plans/` is preserved; do not overwrite previous reviews
