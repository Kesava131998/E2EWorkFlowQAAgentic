# Run Summary — SCRUM-41: Split "Overdue Tasks" into Two Columns
Date    : 2026-08-10
Repo    : manohar10173/Revflow-e2e-workflow
Branch  : scrum-41-split-overdue-tasks-into-two
PR      : https://github.com/manohar10173/Revflow-e2e-workflow/pull/13 (draft)
Jira    : https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-41

## Stage Results
| Stage | Status | Output |
|-------|--------|--------|
| Jira Fetch | ✅ | SCRUM-41: Split "Overdue Tasks" into Two Columns |
| QA Subtasks Created | ✅ | Design: SCRUM-42, Execution: SCRUM-43 |
| Swagger Discovery | ⏭️ | No Swagger spec configured for this project — skipped |
| Test Cases Derived | ✅ | 16 cases → plans/manual_tests_scrum-41_2026-08-10.md & .csv |
| CSV Attached to QA Design | ⚠️ | No `jira_attach_file` tool available on this MCP server — attach skipped, did not block workflow |
| QA TC Design → Done | ✅ | SCRUM-42 |
| Scripts Generated | ✅ | tests/test_scrum41_biller_activity_report.py (+ pages/biller_activity_report_page.py) |
| Test Run | ⏭️ | Skipped at user's request (Checkpoint 1b) |
| QA TC Execution → Done | ⏭️ | SCRUM-43 left as-is — execution has not occurred |
| Postman Export | ⏭️ | Skipped — user declined API test generation |
| Branch Created | ✅ | scrum-41-split-overdue-tasks-into-two |
| Commit + Push | ✅ | 9d1c040 |
| PR Raised | ✅ | https://github.com/manohar10173/Revflow-e2e-workflow/pull/13 (draft: yes) |
| PR Review | ⏳ | Pending — handing off to review agent |

## Coverage Delta
Before: 15 tests | After: 31 tests | Added: +16

## AC Coverage
| AC | Tests | Run Status |
|----|-------|-----------|
| AC1 | test_pos_overdue_tasks_column_removed, test_perm_viewer_report_access_no_export | ⏭️ Not run |
| AC2 | test_pos_overdue_overpayment_count_correct, test_err_future_followup_date_excluded_overpayment | ⏭️ Not run |
| AC3 | test_pos_overdue_open_balance_count_correct, test_err_closed_tasks_excluded_open_balance | ⏭️ Not run |
| AC4 | test_pos_zero_overdue_overpayment_shows_zero, test_pos_zero_overdue_open_balance_shows_zero | ⏭️ Not run |
| AC5 | test_pos_zero_value_renders_green, test_pos_nonzero_value_renders_red | ⏭️ Not run |
| AC6 | test_pos_total_row_sums_open_balance_column, test_pos_total_row_sums_overpayment_column | ⏭️ Not run |
| AC7 | test_pos_export_includes_new_columns_accurately, test_err_export_excludes_removed_column | ⏭️ Not run |
| AC8 | test_pos_new_columns_correct_order, test_pos_export_preserves_column_order | ⏭️ Not run |

## Notes
- The `BillerActivityReportPage` page object was newly scaffolded (no prior page object existed for this report). Locators are best-guess `data-testid` selectors and will need reconciliation against the live RevFlow DOM before these tests can pass.
- Test execution and the resulting QA TC Execution (SCRUM-43) "Done" transition are still outstanding — run the suite locally or via CI and update SCRUM-43 manually once verified.
