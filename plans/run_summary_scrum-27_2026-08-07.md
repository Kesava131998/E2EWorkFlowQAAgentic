# Run Summary — SCRUM-27: [FE] Activity Report — Split "Overdue Tasks" into Two Columns
Date    : 2026-08-07
Repo    : manohar10173/Revflow-e2e-workflow
Branch  : scrum-27-fe-activity-report-split-overdue
PR      : https://github.com/manohar10173/Revflow-e2e-workflow/pull/10
Jira    : https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-27

## Stage Results
| Stage | Status | Output |
|-------|--------|--------|
| Jira Fetch | ✅ | SCRUM-27: [FE] Activity Report — Split "Overdue Tasks" into Two Columns |
| QA Subtasks Created | ✅ | Design: SCRUM-28, Execution: SCRUM-29 |
| Branch Created | ✅ | scrum-27-fe-activity-report-split-overdue |
| Swagger Discovery | ⏭️ | No Swagger/OpenAPI spec configured for this project — skipped |
| Test Cases Derived | ✅ | 17 cases → plans/manual_tests_scrum-27_2026-08-07.md & .csv |
| CSV Attached to QA Design | ⚠️ | No `jira_attach_file` tool exposed by the Jira MCP server — attach skipped, did not block workflow |
| QA TC Design → Done | ✅ | SCRUM-28 |
| API Test Generation | ⏭️ | Declined by user (UI-only scope) |
| Postman Export | ⏭️ | Skipped (Gate 3 not applicable — API tests declined) |
| Test Naming Preview | ✅ | 17 function names approved |
| Scripts Generated | ✅ | tests/test_scrum27_activity_report.py + pages/activity_report_page.py |
| Test Run | ⏭️ | Skipped by user request at the Test Execution Scope checkpoint |
| QA TC Execution → Done | ⏸️ | Not transitioned — execution has not occurred (`$SKIP_RUN = true`) |
| Commit + Push | ✅ | 200610e |
| PR Raised | ✅ | https://github.com/manohar10173/Revflow-e2e-workflow/pull/10 (draft: yes) |
| PR Review | ⚠️ | REQUEST_CHANGES — https://github.com/manohar10173/Revflow-e2e-workflow/pull/10#pullrequestreview-4883060749 |

## Coverage Delta
Before: 15 tests | After: 15 + 17 tests | Added: +17

## AC Coverage
| AC | Tests | All Passing? |
|----|-------|--------------|
| AC1 | test_pos_verify_overdue_tasks_column_removed, test_err_export_excludes_legacy_column | ⏸️ Not run |
| AC2 | test_pos_verify_overdue_overpayment_count, test_pos_click_overpayment_navigates_to_task_list, test_err_task_due_today_not_counted, test_err_closed_task_not_counted | ⏸️ Not run |
| AC3 | test_pos_verify_overdue_open_balance_count, test_pos_click_open_balance_navigates_to_task_list, test_err_task_due_today_not_counted, test_err_closed_task_not_counted, test_perm_unauthorized_user_cannot_view_report | ⏸️ Not run |
| AC4 | test_pos_zero_overdue_tasks_shows_zero | ⏸️ Not run |
| AC5 | test_pos_zero_count_displayed_green, test_pos_nonzero_count_displayed_red | ⏸️ Not run |
| AC6 | test_pos_summary_row_sums_open_balance, test_pos_summary_row_sums_overpayment | ⏸️ Not run |
| AC7 | test_pos_export_contains_new_columns, test_err_export_excludes_legacy_column, test_perm_view_only_user_cannot_export | ⏸️ Not run |
| AC8 | test_pos_verify_new_columns_order | ⏸️ Not run |

## PR Review Findings (REQUEST_CHANGES)
**Passes**: `ActivityReportPage` inherits `BasePage`, locators mostly in `__init__`, all public methods carry `@allure.step`, no in-page assertions, all tests use the `page` fixture + `allure.step` + `settings.SHORT_TIMEOUT`, naming convention followed throughout.

**Blocking issues**:
1. `get_task_list_applied_filters()` in `activity_report_page.py` builds a raw `page.locator(...)` inline instead of defining it in `__init__`.
2. `test_pos_export_contains_new_columns` / `test_err_export_excludes_legacy_column` trigger a download but never assert on its contents (end on `# TODO`).
3. `test_perm_unauthorized_user_cannot_view_report` / `test_perm_view_only_user_cannot_export` never actually switch to the target role/permission level — RBAC assertions test nothing meaningful yet.
4. `BILLER_WITH_*` constants are literal `"TODO-..."` placeholders — 11 of 17 tests depend on these and will fail to locate a matching row on first real run.

**Suggestions**: dead `"green"/"red" in color.lower()` branches (computed style returns `rgb(...)`, never a color word); consider `@pytest.mark.parametrize` for near-duplicate test pairs; run `self-heal-pr` against the live app once reachable since locators are unverified guesses.

## Notes
- Locators in `pages/activity_report_page.py` are best-guess `data-testid` selectors — the live app requires Microsoft Azure AD SSO login, which could not be completed via Playwright MCP in this session (only a Jira Service Management help-center widget rendered on initial navigation). Expect self-healing/adjustment once run against the real DOM.
- Test data placeholders (`TODO-biller-with-overdue-tasks`, etc.) need real fixtures for this environment before the suite can pass.
- `.mcp.json` and `.claude/commands/e2e-workflow.md` had pre-existing uncommitted local changes unrelated to this ticket — left untouched, not staged or committed by this workflow run.
