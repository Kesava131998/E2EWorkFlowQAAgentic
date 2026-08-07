# Run Summary — SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View
Date    : 2026-08-07
Repo    : manohar10173/Revflow-e2e-workflow
Branch  : scrum-11-add-show-primary-only-toggle
PR      : https://github.com/manohar10173/Revflow-e2e-workflow/pull/8
Jira    : https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-11

## Note on prior run
This ticket previously went through this workflow (2026-08-04). That run's draft
PR #5 (branch `scrum-11-add-show-primary-only-toggle-v3`) was closed without
merging on 2026-08-07. The QA Design/Execution subtasks (SCRUM-12, SCRUM-13)
created during that run were reused rather than duplicated. A fresh branch and
PR were created for this run per workflow rules (never reuse a ticket branch).

## Stage Results
| Stage | Status | Output |
|-------|--------|--------|
| Jira Fetch | ✅ | SCRUM-11: Add "Show Primary Only" Toggle to Facility & Role View |
| QA Subtasks | ✅ | Reused — Design: SCRUM-12 (Done), Execution: SCRUM-13 (To Do) |
| Branch Created | ✅ | scrum-11-add-show-primary-only-toggle (from main) |
| Swagger Discovery | ⏭️ | Skipped — no Swagger/OpenAPI spec configured for RevFlow |
| Test Cases Derived | ✅ | 12 cases → plans/manual_tests_scrum-11_2026-08-07.md & .csv |
| CSV Attached to QA Design | ⚠️ | Skipped — Jira MCP server exposes no attachment-upload tool |
| QA TC Design → Done | ✅ | SCRUM-12 (already Done, no-op) |
| API Test Generation | ⏭️ | Declined by user |
| Postman Export | ⏭️ | Skipped (API tests declined) |
| Scripts Generated | ✅ | tests/test_scrum11_user_management.py + pages/user_management_page.py |
| Test Run | ⏭️ | Skipped by user at execution-scope checkpoint |
| QA TC Execution → Done | ⏭️ | Not transitioned — execution didn't occur this run |
| Commit + Push | ✅ | f3294fe |
| PR Raised | ✅ | https://github.com/manohar10173/Revflow-e2e-workflow/pull/8 (draft: yes) |
| PR Review | ⏳ | Pending — handed off to review-pr agent |

## Coverage Delta
Before: 15 tests | After: 27 tests | Added: +12

## AC Coverage
| AC | Tests | Status |
|----|-------|--------|
| AC1 | test_pos_toggle_visible_on_facility_role_view, test_pos_toggle_keyboard_operable_with_accessible_name, test_perm_viewer_cannot_access_facility_role_view | ⏭️ Not run |
| AC2 | test_pos_toggle_on_by_default | ⏭️ Not run |
| AC3 | test_pos_toggle_on_shows_only_primary_rows, test_err_no_primary_roles_shows_empty_grid | ⏭️ Not run |
| AC4 | test_pos_toggle_off_shows_all_role_assignments, test_pos_toggle_off_then_on_is_idempotent | ⏭️ Not run |
| AC5 | test_pos_toggle_resets_to_on_after_page_reload, test_pos_toggle_resets_to_on_after_tab_switch | ⏭️ Not run |
| AC6 | test_pos_toggle_not_visible_on_user_view_tab, test_err_toggle_does_not_affect_user_view_rows | ⏭️ Not run |

## Known Gaps (carried into PR body)
- No `pages/login_page.py` / Azure AD SSO auth step exists in this suite yet (matches existing ARW-2579 convention)
- Locators derived from ticket wording, not yet reconciled against the live DOM for this new feature
- Two tests have `TODO` placeholder test data (no-primary-roles user, Viewer-role credentials)
