# Run Summary — SCRUM-50: Add "Show Primary Only" Toggle to Facility & Role View
Date    : 2026-08-11
Repo    : manohar10173/Revflow-e2e-workflow
Branch  : scrum-50-add-show-primary-only-toggle
PR      : https://github.com/manohar10173/Revflow-e2e-workflow/pull/16 (draft)
Jira    : https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-50

## Stage Results
| Stage | Status | Output |
|-------|--------|--------|
| Jira Fetch | ✅ | SCRUM-50: Add "Show Primary Only" Toggle to Facility & Role View |
| QA Subtasks Created | ✅ | Design: SCRUM-51, Execution: SCRUM-52 |
| Swagger Discovery | ⏭️ | No Swagger/OpenAPI spec configured for this project — skipped |
| Test Cases Derived | ✅ | 10 cases → plans/manual_tests_scrum-50_2026-08-11.md & .csv |
| CSV Attached to QA Design | ⚠️ | Attach failed — no `jira_attach_file` tool available on this Jira MCP server; does not block workflow |
| QA TC Design → Done | ✅ | SCRUM-51 |
| API Test Generation | ⏭️ | Declined by user at Gate 2 (UI tests only) |
| Postman Export | ⏭️ | Skipped (not applicable — no API tests generated) |
| Scripts Generated | ✅ | tests/test_scrum50_facility_role.py (+ pages/facility_role_page.py) |
| Test Run | ⏭️ | Skipped by user at Execution Scope checkpoint |
| QA TC Execution → Done | ⏭️ | Not transitioned — execution has not occurred |
| Branch Created | ✅ | scrum-50-add-show-primary-only-toggle |
| Commit + Push | ✅ | 81bdba1 |
| PR Raised | ✅ | https://github.com/manohar10173/Revflow-e2e-workflow/pull/16 (draft: yes) |
| PR Review | ⏳ | Pending — handed off to review agent |

## Coverage Delta
Before: 15 tests | After: 25 tests | Added: +10

## AC Coverage
| AC | Tests | All Passing? |
|----|-------|---------------|
| AC1 | test_pos_toggle_visible_on_facility_role_tab | ⏭️ Not run |
| AC2 | test_pos_toggle_enabled_by_default | ⏭️ Not run |
| AC3 | test_pos_toggle_on_filters_primary_rows_only, test_pos_toggle_on_with_no_primary_rows_shows_empty_grid | ⏭️ Not run |
| AC4 | test_pos_toggle_off_shows_all_role_assignments, test_pos_toggle_off_with_all_rows_primary_unchanged | ⏭️ Not run |
| AC5 | test_pos_toggle_resets_on_after_page_reload, test_pos_toggle_resets_on_after_tab_switch | ⏭️ Not run |
| AC6 | test_err_toggle_not_visible_on_user_view_tab, test_err_toggle_has_no_effect_on_user_view_data | ⏭️ Not run |

## Notes
- Test URLs in `tests/test_scrum50_facility_role.py` and locators in `pages/facility_role_page.py` are placeholders (`TODO-*` case IDs, best-guess `data-testid` selectors) pending verification against the live RevFlow UI and real test data.
- Parent Story SCRUM-50 was **not** transitioned — only the QA subtasks are updated by this workflow.
