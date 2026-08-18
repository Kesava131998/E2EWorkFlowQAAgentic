---
name: project-review
description: Full codebase audit — checks coverage, locator quality, architecture compliance, and writes a report to plans/
tags: [review, audit, planning, quality]
---

# Skill: Project Review

Performs a comprehensive static audit of the entire `@playwright/test` JavaScript codebase.
Checks coverage gaps, architecture compliance, locator hygiene, config design, and
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
pages/        : base_page.js, login_page.js, case_detail_page.js, biller_activity_page.js
tests/        : basic.spec.js, arw2579-payment-schedule.spec.js, ...
utils/        : test_generator.js (if present)
config/       : settings.js
```

### Step 2 — Architecture compliance check

**For each file in `pages/`:**
- [ ] Class extends `BasePage`?
- [ ] All locators assigned in the constructor?
- [ ] All action methods wrapped in `test.step(...)`?
- [ ] No assertions (`expect(...)`) inside page methods — only simple actions/getters?
- [ ] Imports are clean (only `@playwright/test`, `./base_page`, `../config/settings`)?

**For each file in `tests/`:**
- [ ] Filename ends with `.spec.js`?
- [ ] Uses the built-in `page` fixture from `@playwright/test`?
- [ ] All steps in `await test.step(...)`?
- [ ] Uses `settings.*_TIMEOUT` not raw integers?
- [ ] Allure metadata (`epic`/`feature`/`story` from `allure-js-commons`) present?
- [ ] `test.describe.parametrize`-style data variants use a loop over a data array, not copy-pasted tests?

**For `playwright.config.js`:**
- [ ] Reporters include `allure-playwright` and `html`?
- [ ] `use.baseURL`/timeouts sourced from env, not hardcoded?
- [ ] Screenshot/video/trace capture set to failure-only (not `on` for every run, which bloats artifacts)?

**For `config/settings.js`:**
- [ ] All timeouts are `process.env.*` with defaults?
- [ ] No secrets in settings file?

**For `utils/test_generator.js`:**
- [ ] Uses `dotenv`/`require('dotenv').config()`?
- [ ] No hardcoded values?

### Step 3 — Locator hygiene audit

For each page object, check locators for fragility:
- XPath with `text()` matching → fragile (UI text changes)
- Deep nested XPath → fragile (DOM restructure)
- Positional CSS (`:nth-child`) → fragile
- Stable: `id`, `data-*` attributes, `getByRole`/`getByTestId`

Flag each fragile locator with a risk rating: 🔴 High / 🟡 Medium / 🟢 Low

### Step 4 — Coverage gap analysis

Map each page object to tests that use it:
```
CaseDetailPage     → arw2579-payment-schedule.spec.js ✅
LoginPage          → (no dedicated spec yet) ⚠️
BillerActivityPage → (no dedicated spec yet) ⚠️
BasePage           → (base class, not tested directly) ℹ️
```

Identify:
- Page objects with no test coverage
- Tests that access the app without going through a page object (direct `page.locator()` calls in test files)

### Step 5 — Dead code check

Look for:
- Locators defined in the constructor but never used in any method
- Methods defined in page objects but never called from any test
- Required modules never used

### Step 6 — Configuration review

- Is `.env` in `.gitignore`?
- Does `playwright.config.js` `testDir`/`testMatch` still match actual test locations?
- Is the `allure-playwright` version compatible with `allure-commandline`?
- Does `package.json` match what's actually installed (`npm ls` clean, no missing peer deps)?

```bash
npm ls @playwright/test allure-playwright allure-commandline dotenv
```

### Step 7 — Summarise findings and write report

Write the report to `plans/review-<YYYY-MM-DD>.md`:

```markdown
# Project Review — AI-Test-Workflow (JavaScript/@playwright/test)
**Date**: <YYYY-MM-DD>
**Reviewer**: AI Agent (.claude/commands/project-review.md)

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
| P1 | Fix raw timeouts in x.spec.js | tests/ | Low |
| P2 | Add `test.step` wrapping to 3 methods in biller_activity_page.js | pages/ | Low |
| P3 | Replace fragile XPath in login_page.js | pages/ | Medium |
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
