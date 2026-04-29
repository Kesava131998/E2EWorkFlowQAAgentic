---
name: generate-tests
description: Generate Playwright Python test scripts from Excel test cases using the project's page object pattern
tags: [test-generation, excel, playwright, core]
---

# Skill: Generate Tests from Excel

Reads manual test cases from an Excel file and generates pytest + Playwright test scripts,
automatically mapping Excel steps to page object methods.

> **Source**: `utils/test_generator.py`
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
grep -r "<keyword from test case name>" tests/ --include="*.py" -l
```
If coverage already exists, report it and ask the user if they want to supplement or replace.

### Step 1 — Validate prerequisites
```bash
# From project root, with venv active:
python -c "import pandas, openpyxl; print('OK')"
```
If this fails, run:
```bash
pip install pandas openpyxl
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
python utils/test_generator.py <path-to-excel-file>
```

### Step 4 — Review generated output
- Show the user the list of generated files
- Display a sample of the generated code for the first test case
- Flag any steps that landed as `# TODO: Implement` (no matching page method found)

### Step 5 — Fix TODOs (if asked)
For each `# TODO: Implement` step:
1. Check if the action can be added to an existing page object
2. If so, use the `write-page-object` skill to add the missing method
3. Re-run the step manually in the generated test

### Step 6 — Verify generated tests are discoverable
```bash
pytest --collect-only tests/
```
Every generated file should appear. If not, check the filename starts with `test_`.

### Step 7 — Offer manual test cases

**Always ask the user:**

> "Do you also want manual test cases documented for these scenarios? I can generate:
> - **Happy path** cases (positive flows per test case)
> - **Negative / error** cases (invalid inputs, missing fields, permission denials)
> - **Edge cases** (boundary values, empty states, concurrent actions)
>
> Which types would you like?"

If yes, produce a markdown table per test case:

| # | Type | Scenario | Steps | Expected Result |
|---|------|----------|-------|-----------------|
| 1 | Happy Path | Login with valid credentials | 1. Enter valid username/password 2. Click Login | Dashboard is displayed |
| 2 | Negative | Login with wrong password | 1. Enter valid username, wrong password 2. Click Login | Error message "Invalid credentials" shown |
| 3 | Edge Case | Login with empty fields | 1. Leave all fields blank 2. Click Login | Validation messages appear on each required field |

Save to `plans/manual_tests_<module>_<date>.md` if the user wants to keep them.

---

## Output conventions

Generated files go to `tests/` and follow this naming pattern:
```
test_<module>_<test_id_lower>.py
```
Example: `tests/test_diagnostics_tc001.py`

Generated test functions follow naming conventions from `agents/rules.md`:
- `test_pos_<action>` for happy path
- `test_err_<action>` for error/negative cases

Generated code always includes:
- `@allure.title()` and `@allure.description()` decorators
- Steps wrapped in `with allure.step("..."):`
- `page.wait_for_timeout(settings.SMALL_TIMEOUT)` between steps
- Page object instantiation at the top of the function

---

## Notes

- Intelligent keyword matching maps "Click Login" → `login_page.click_login()`
- Module column hints which page object to use (e.g., `Module: Diagnostics` → `DiagnosticPage`)
- All generated tests use `settings.*_TIMEOUT` — never raw integers
- If a new page is needed, run `write-page-object` skill first, then re-generate
