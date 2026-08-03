# Manual Test Mapping — SCRUM-2: Create Payment Schedule

> **Finding:** SCRUM-2 describes the same feature already automated under **ARW-2579**
> (`tests/test_arw2579_payment_schedule.py`). All 4 ACs below map 1:1 onto existing tests.
> No new test file was generated — see `plans/run_summary_scrum2_2026-08-03.md` for the full decision trail.

| # | AC | Type | Scenario | Existing Test (ARW-2579) |
|---|----|------|----------|---------------------------|
| 1 | AC1 | Happy Path | Open modal from empty-state CTA | `test_pos_open_modal_from_empty_state_cta` |
| 2 | AC1 | Happy Path | Open modal from populated-view button | `test_pos_open_modal_from_populated_view_button` |
| 3 | AC1 | Negative | Close modal discards no schedule | `test_err_close_modal_discards_no_schedule` |
| 4 | AC1 | RBAC | Viewer role cannot access Add Payment Schedule | `test_perm_viewer_cannot_access_add_payment_schedule` |
| 5 | AC2 (Payer) | Happy Path | Payer dropdown shows only eligible payers | `test_pos_payer_dropdown_shows_only_eligible_payers` |
| 6 | AC2 (Payer) | Negative | Existing-schedule payer disabled with tooltip | `test_err_existing_schedule_payer_disabled_with_tooltip` |
| 7 | AC2 (Payer) | Edge Case | No eligible payers shows empty dropdown / Save disabled | `test_err_no_eligible_payers_shows_empty_dropdown` |
| 8 | AC2 (Schedule Type) | Happy Path | "Specific day of the month" reveals day selector | `test_pos_specific_day_reveals_day_selector` |
| 9 | AC2 (Schedule Type) | Happy Path | "Relative weekday" reveals weekday selector | `test_pos_relative_weekday_reveals_weekday_selector` |
| 10 | AC2 (Payment Method) | Happy Path | All payment methods selectable (ACH, Credit Card, Direct Deposit, Personal Check, Other) | `test_pos_all_payment_methods_selectable` |
| 11 | AC2 (Auto-Pay) | Happy Path | Auto-Pay checkbox toggles + helper text shown | `test_pos_autopay_checkbox_toggle_and_helper_text` |
| 12 | AC3 (Save Behavior) | Negative | Save disabled until all required fields complete | `test_err_save_disabled_until_required_fields_complete` |
| 13 | AC3 (Save Behavior) | Happy Path | Save success: modal closes, table updates, toast shown | `test_pos_save_schedule_success_toast_and_table_update` |
| 14 | AC3 (Save Behavior) | Negative | Duplicate schedule prevented for same payer | `test_err_duplicate_schedule_prevented_for_same_payer` |

**Coverage gaps found: 0** — no new automation required for SCRUM-2.
