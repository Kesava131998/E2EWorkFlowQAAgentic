---
name: generate-tests
description: Generate Playwright JavaScript (@playwright/test) test scripts from Excel test cases using the project's page object pattern
tags: [test-generation, excel, playwright, core]
---

# Skill: Generate Tests from Excel

Reads manual test cases from an Excel file and generates `@playwright/test` scripts,
automatically mapping Excel steps to page object methods.

> **Source**: `utils/test_generator.js`
> **Rules**: See `agents/rules.md` — Page Objects, Tests, Timeouts, Test Naming Conventions

---

## When to invoke

- User provides an Excel/`.xlsx` file with test cases
- User says "generate tests from this sheet", "automate these test cases"
- User pastes a Jira ticket and wants coverage generated (combine with `jira-ticket` skill)

---

## Workflow

### Step 0 — Explore first
Before generating, search for existing tests that may already cover these cases:
```bash
grep -r "<keyword from test case name>" tests/ --include="*.spec.js" -l
```
If coverage already exists, report it and ask the user if they want to supplement or replace.

### Step 1 — Validate prerequisites
```bash
node -e "require('xlsx'); console.log('OK')"
```
If this fails, run:
```bash
npm install --save-dev xlsx
```

### Step 2 — Inspect the Excel file
Before running, open the file and check:
- Column names match expected schema (see below)
- Test IDs are present and non-empty
- Module names match existing page object files in `pages/`

**Expected columns** (flexible matching):
| Column | Aliases accepted |
|--------|-----------------|
| `Test Case ID` | `testcase`, `tc_id`, `id` |
| `Test Case Name` | `testname`, `name`, `title` |
| `Module` | `feature`, `page`, `component` |
| `Step` | `action`, `steps`, `description` |
| `Test Data` | `data`, `input`, `value` |
| `Expected Result` | `expected`, `result` |

### Step 3 — Run the generator
```bash
node utils/test_generator.js <path-to-excel-file>
```

### Step 4 — Review generated output
- Show the user the list of generated files
- Display a sample of the generated code for the first test case
- Flag any steps that landed as `// TODO: Implement` (no matching page method found)

### Step 5 — Fix TODOs (if asked)
For each `// TODO: Implement` step:
1. Check if the action can be added to an existing page object
2. If so, use the `write-page-object` skill to add the missing method
3. Re-run the step manually in the generated test

### Step 6 — Verify generated tests are discoverable
```bash
npx playwright test --list
```
Every generated file should appear. If not, check the filename ends with `.spec.js`.

### Step 7 — Offer manual test cases

**Always ask the user:**

> "Do you also want manual test cases documented for these scenarios? I can generate:
> - **Happy path** cases (positive flows per test case)
> - **Negative / error** cases (invalid inputs, missing fields)
> - **Edge cases** (boundary values, empty states, concurrent actions)
> - **RBAC / Permission** cases (unauthorized access attempts)
>
> Which types would you like?"

If yes, produce the manual tests following QA best practices:

| # | Type | Priority | Scenario | Pre-conditions | Test Data | Steps | Expected Result |
|---|------|----------|----------|----------------|-----------|-------|-----------------|
| 1 | Happy Path | High | Login with valid credentials | User exists | `valid_user` | 1. Enter credentials<br>2. Click Login | Dashboard is displayed |
| 2 | Negative | Medium | Login with wrong password | User exists | `wrong_pwd` | 1. Enter credentials<br>2. Click Login | Error message "Invalid credentials" shown |
| 3 | Edge Case | Low | Login with empty fields | None | Empty fields | 1. Leave fields blank<br>2. Click Login | Validation messages appear on each field |
| 4 | RBAC | High | Viewer trying admin action | Logged in as Viewer | Valid data | 1. Go to Admin page | Access Denied message shown |

**Instructions for Test Case Quality:**
- **Pre-conditions:** Clearly state the required system state before the test starts (e.g., "Navigate to https://...", specific user roles).
- **Test Data:** Specify exact inputs needed to run the test.
- **Extreme Granularity:** Do not summarize steps. Break down every flow into micro-interactions. Before interacting with an element, explicitly include a step to verify it is visible and accessible.
- **1-to-1 Mapping:** The "Steps" and "Expected Result" columns must have a strict 1-to-1 mapping. Every single numbered step MUST have a corresponding numbered expected result (e.g., Step: "3. Click on Email field" -> Expected: "3. Email field is clicked and focused").

Save the output to two formats:
1. A Markdown file for easy reading:
```
plans/manual_tests_<module>_<date>.md
```
2. A CSV file (Excel compatible) for tracking and test management tools:
```
plans/manual_tests_<module>_<date>.csv
```
Ensure the CSV is properly formatted with commas and appropriate quoting for text fields.

---

## Output conventions

Generated files go to `tests/` and follow this naming pattern:
```
<module>-<test_id_lower>.spec.js
```
Example: `tests/diagnostics-tc001.spec.js`

Generated test titles follow naming conventions from `agents/rules.md`:
- `'pos: <action>'` for happy path
- `'err: <action>'` for error/negative cases

Generated code always includes:
- `test.describe(...)` grouping with an Allure `epic`/`feature`/`story` call (`allure-js-commons`) in a `beforeEach`
- Steps wrapped in `await test.step("...", async () => { ... })`
- Page object instantiation at the top of the test callback

---

## Notes

- Intelligent keyword matching maps "Click Login" → `loginPage.clickLoginButton()`
- Module column hints which page object to use (e.g., `Module: Diagnostics` → `DiagnosticsPage`)
- All generated tests use `settings.*_TIMEOUT` — never raw integers
- If a new page is needed, run `write-page-object` skill first, then re-generate
