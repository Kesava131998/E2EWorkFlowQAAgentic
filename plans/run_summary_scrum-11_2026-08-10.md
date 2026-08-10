# Run Summary — SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View
Date    : 2026-08-10
Repo    : manohar10173/Revflow-e2e-workflow
Branch  : scrum-11-add-show-primary-only-toggle-v2
PR      : https://github.com/manohar10173/Revflow-e2e-workflow/pull/12 (draft)
Jira    : https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-11

## Stage Results
| Stage | Status | Output |
|-------|--------|--------|
| Jira Fetch | ✅ | SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View |
| QA Subtasks Created | ✅ | Design: SCRUM-33, Execution: SCRUM-34 |
| Branch Created | ✅ | scrum-11-add-show-primary-only-toggle-v2 (base branch already existed, appended -v2) |
| Test Cases Derived | ✅ | 12 cases → plans/manual_tests_scrum-11_2026-08-10.md & .csv |
| CSV Attached to QA Design | ⚠️ | No jira_attach_file tool available in this MCP server — attach skipped, does not block workflow |
| QA TC Design → Done | ✅ | SCRUM-33 |
| Page Object Created | ✅ | pages/user_management_page.py (locators derived from ticket text, not verified against live DOM — no login_page.py exists yet for Azure AD SSO) |
| Scripts Generated | ✅ | tests/test_scrum11_user_management.py |
| Test Run | ⏭️ | Skipped at user's request (test-execution-scope checkpoint) |
| QA TC Execution → Done | ⏭️ | Not transitioned — execution was skipped, not performed |
| Postman Export | ⏭️ | Declined at api-test-scope checkpoint (UI tests only) |
| Commit + Push | ✅ | 6911e1c |
| PR Raised | ✅ | PR #12 (draft, tests not executed) |
| PR Review | Pending | Stage 9 — spawned after PR raised |

## Coverage Delta
Before: 15 tests | After: 27 tests | Added: +12

## AC Coverage
| AC | Tests | All Passing? |
|----|-------|-------------|
| AC1 | test_pos_toggle_visible_on_facility_role_view, test_pos_toggle_keyboard_operable_with_accessible_name, test_perm_viewer_cannot_access_facility_role_view | ⏭️ Not run |
| AC2 | test_pos_toggle_on_by_default | ⏭️ Not run |
| AC3 | test_pos_toggle_on_shows_only_primary_rows, test_err_no_primary_roles_shows_empty_grid | ⏭️ Not run |
| AC4 | test_pos_toggle_off_shows_all_role_assignments, test_pos_toggle_off_then_on_is_idempotent | ⏭️ Not run |
| AC5 | test_pos_toggle_resets_to_on_after_page_reload, test_pos_toggle_resets_to_on_after_tab_switch | ⏭️ Not run |
| AC6 | test_pos_toggle_not_visible_on_user_view_tab, test_err_toggle_does_not_affect_user_view_rows | ⏭️ Not run |

## Notes
- This is a re-run of a prior workflow execution for SCRUM-11 (original draft PR #5 on branch `scrum-11-add-show-primary-only-toggle-v3`, per user's explicit choice to do a fresh full run rather than resolve blockers on the existing PR).
- Same two blockers apply as before: (1) no `pages/login_page.py` exists yet for Azure AD SSO login, so tests cannot authenticate; (2) locators were derived from ticket wording, not the live DOM, since SCRUM-11 has not been inspected in the deployed app.
- Recommend reconciling locators via `/self-heal-pr` or Playwright MCP once the feature is deployed and a login flow is automated.
