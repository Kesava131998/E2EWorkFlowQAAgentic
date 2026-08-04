# Run Summary — SCRUM-15: [FE] - Month Over Month (MOM) Report

| Field | Value |
|-------|-------|
| Date | 2026-08-04 |
| Repo | manohar10173/Revflow-e2e-workflow |
| Branch | `scrum-15-fe-month-over-month-mom` |
| Commit | `641d414` |
| PR | https://github.com/manohar10173/Revflow-e2e-workflow/pull/6 (draft) |
| Jira | https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-15 |
| QA Design | https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-16 (Done) |
| QA Execution | https://vwiki281-1785763863770.atlassian.net/browse/SCRUM-17 (open) |

## Stage Results

| Stage | Status | Output |
|-------|--------|--------|
| Jira Fetch | ✅ | SCRUM-15: [FE] - Month Over Month (MOM) Report — 15 ACs parsed, status `To Do` |
| QA Subtasks Created | ✅ | Design: SCRUM-16, Execution: SCRUM-17 (neither existed; exactly 2 created) |
| Branch Created | ✅ | `scrum-15-fe-month-over-month-mom` (fresh from `main`, no version suffix needed) |
| Swagger Discovery | ⏭️ | Skipped — no OpenAPI spec configured for RevFlow |
| Test Cases Derived | ✅ | 26 cases → `plans/manual_tests_scrum-15_2026-08-04.md` & `.csv` |
| CSV Attached to QA Design | ✅ | SCRUM-16 (24,911 bytes, text/csv — via Jira REST API; the MCP server exposes no attach tool) |
| QA TC Design → Done | ✅ | SCRUM-16 (transition id 41) |
| Scripts Generated | ✅ | `tests/test_scrum15_mom_report.py` (26 tests) + `pages/mom_report_page.py` (new page object) |
| Collection Verified | ✅ | `pytest --collect-only` → 26 tests collected in 0.11s |
| Test Run | ⏭️ | Skipped at operator request (HITL Checkpoint 1b) — feature not yet built |
| QA TC Execution → Done | ⏭️ | **Not transitioned** — execution did not occur, SCRUM-17 remains open |
| Postman Export | ⏭️ | Skipped — UI-only was selected at HITL Checkpoint 1 |
| Commit + Push | ✅ | `641d414` pushed to `origin/scrum-15-fe-month-over-month-mom` |
| PR Raised | ✅ | PR #6 (draft: **yes** — tests unexecuted against an unbuilt feature) |
| PR Review | — | See "PR Review" section below |

## HITL Decisions

| Checkpoint | Question | Answer |
|-----------|----------|--------|
| 1 | Test case sign-off | Approve all 26 as-is |
| 1 | Include API test generation? | No — UI tests only |
| 1 | Postman collection export? | Not asked (skipped, since API tests were declined) |
| 3b | Test function naming | Proceed as-is |
| 1b | Execution scope | Skip execution — go to commit |

## Coverage Delta

| Before | After | Added |
|--------|-------|-------|
| 15 tests | 41 tests | +26 |

## AC Coverage

| AC | Tests | All Passing? |
|----|-------|-------------|
| AC1 — MOM Report in AR Reports nav below Percent Collected Trend | `test_pos_mom_report_nav_entry_below_percent_collected_trend`, `test_pos_mom_report_nav_entry_loads_report_page`, `test_perm_user_without_ar_reports_cannot_access_mom_report` | ⏭️ Not run |
| AC2 — Rows = service months, columns = posting months (chronological) | `test_pos_pivot_rows_service_months_columns_posting_months`, `test_pos_posting_columns_ordered_chronologically` | ⏭️ Not run |
| AC3 — Cells populated only where posting month > service month | `test_pos_cells_populated_when_posting_after_service_month`, `test_err_cells_blank_when_posting_not_after_service_month` | ⏭️ Not run |
| AC4 — Cell scoped to months between service and posting month | `test_pos_cell_matches_percent_collected_trend_interval` | ⏭️ Not run |
| AC5 — Posting columns offset +1 month from the service range | `test_pos_posting_columns_offset_one_month_from_service_range`, `test_pos_single_month_custom_range_renders_one_row_one_column` | ⏭️ Not run |
| AC6 — 6 / 12 / 18 / Custom toggle controls the range | `test_pos_six_month_toggle_renders_six_rows_and_columns`, `test_pos_eighteen_month_toggle_renders_eighteen_rows_and_columns`, `test_pos_toggle_eighteen_to_six_shrinks_grid` | ⏭️ Not run |
| AC7 — 12 months is the default | `test_pos_twelve_month_range_is_default` | ⏭️ Not run |
| AC8 — Custom allows up to 24 months | `test_pos_custom_range_accepts_twenty_four_months`, `test_err_custom_range_rejects_span_over_twenty_four_months` | ⏭️ Not run |
| AC9 — Future service dates not selectable | `test_err_future_service_dates_not_selectable` | ⏭️ Not run |
| AC10 — Write-offs / Overpayments parity with Percent Collected Trend | `test_pos_write_offs_toggle_applies_to_pivot_values`, `test_pos_overpayments_control_matches_percent_collected_trend` | ⏭️ Not run |
| AC11 — No "Transactions Within" filter | `test_err_no_transactions_within_filter_present` | ⏭️ Not run |
| AC12 — No grouping selector | `test_err_no_grouping_selector_present` | ⏭️ Not run |
| AC13 — Global Facility Filter affects the report | `test_pos_global_facility_filter_scopes_report_data` | ⏭️ Not run |
| AC14 — Exportable in pivot layout | `test_pos_export_mirrors_pivot_layout`, `test_pos_export_empty_result_set_is_well_formed`, `test_perm_user_without_export_permission_cannot_export` | ⏭️ Not run |
| AC15 — New card on the reports landing page | `test_pos_reports_landing_card_navigates_to_mom_report` | ⏭️ Not run |

**All 15 ACs have at least one test. None have been executed.**

## Known Gaps Before This Can Run Green

1. **Feature not built.** SCRUM-15 is `To Do`. Every `data-testid` locator in `pages/mom_report_page.py` is inferred from the ticket text plus existing project conventions — none were verified against live DOM. Re-verify (or self-heal) once the MOM Report ships to `revflow-dev`.
2. **Route guesses.** `REPORTS_LANDING_URL`, `MOM_REPORT_URL` and `PERCENT_COLLECTED_TREND_URL` are marked `TODO` in the page object.
3. **No auth step.** Tests navigate straight to `/reports/*`; RevFlow uses Azure AD SSO. This matches the existing `test_arw2579_payment_schedule.py` pattern, so it is a project-wide gap rather than a SCRUM-15 one.
4. **Test data placeholders.** `FACILITY_A`, `FACILITY_B`, `FACILITY_WITH_NO_ACTIVITY` are `TODO`; the two RBAC tests need restricted-role credentials.
5. **SCRUM-17 still open** — mark QA TC Execution Done only after a real run.

## Parent Story Protection

| Story Status | QA Design | QA Execution | Final Story Status |
|--------------|-----------|--------------|--------------------|
| To Do | Done | To Do (not run) | **To Do — unchanged** |

No `jira_add_comment` call was made, and SCRUM-15 was never transitioned.
