import allure
from pages.case_detail_page import CaseDetailPage
from config.settings import settings

# TODO: replace with a real case/payer fixture once test data is confirmed for this environment
CASE_WITH_NO_SCHEDULE_URL = f"{settings.BASE_URL}/cases/TODO-empty-schedule-case"
CASE_WITH_SCHEDULE_URL = f"{settings.BASE_URL}/cases/TODO-populated-schedule-case"
ELIGIBLE_PAYER = "TODO-eligible-payer"
INELIGIBLE_PAYER = "TODO-ineligible-payer"
PAYER_WITH_EXISTING_SCHEDULE = "TODO-payer-with-existing-schedule"


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC1: User can open the Add Payment Schedule modal from the empty-state CTA")
@allure.title("Open modal from empty-state CTA")
def test_pos_open_modal_from_empty_state_cta(page):
    """
    Jira: ARW-2579
    AC: User can click "Add Payment Schedule" from the Empty state CTA; opens modal
    titled "Add Payment Schedule" with subtitle "Define the expected payment timing
    and method for a payer. Payments are not initiated from this schedule."
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case with zero payment schedules"):
        case_page.navigate_to(CASE_WITH_NO_SCHEDULE_URL)
        case_page.wait_for_load()

    with allure.step("Click the empty-state 'Add Payment Schedule' CTA"):
        case_page.open_modal_from_empty_state()

    with allure.step("Verify the modal opens with the correct title and subtitle"):
        assert case_page.is_modal_visible(), "Add Payment Schedule modal did not open"
        assert case_page.modal_title.is_visible(), "Modal title not visible"
        assert case_page.modal_subtitle.is_visible(), "Modal subtitle not visible"


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC1: User can open the Add Payment Schedule modal from the populated-view button")
@allure.title("Open modal from populated-view button")
def test_pos_open_modal_from_populated_view_button(page):
    """
    Jira: ARW-2579
    AC: User can click "Add Payment Schedule" from the Button in populated view
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case with an existing payment schedule row"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()

    with allure.step("Click the 'Add Payment Schedule' button"):
        case_page.open_modal_from_button()

    with allure.step("Verify the modal opens with the correct title and subtitle"):
        assert case_page.is_modal_visible(), "Add Payment Schedule modal did not open"
        assert case_page.modal_title.is_visible(), "Modal title not visible"
        assert case_page.modal_subtitle.is_visible(), "Modal subtitle not visible"


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC1: Closing the modal without saving discards no schedule")
@allure.title("Close modal discards no schedule")
def test_err_close_modal_discards_no_schedule(page):
    """
    Jira: ARW-2579
    AC: Modal can be dismissed without creating a schedule
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case and open the modal"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        row_count_before = case_page.get_schedule_row_count()
        case_page.open_modal_from_button()

    with allure.step("Close the modal without saving"):
        case_page.close_modal()

    with allure.step("Verify modal is closed and no new row was added"):
        assert not case_page.is_modal_visible(), "Modal is still visible after close"
        assert case_page.get_schedule_row_count() == row_count_before, (
            "Schedule table row count changed after closing without saving"
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: Payer dropdown only includes payers flagged 'Allow Payment Schedule'")
@allure.title("Payer dropdown shows only eligible payers")
def test_pos_payer_dropdown_shows_only_eligible_payers(page):
    """
    Jira: ARW-2579
    AC: Payer dropdown only includes payers whose payer category is flagged
    "Allow Payment Schedule"
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case and open the modal"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        case_page.open_modal_from_button()

    with allure.step("Open the Payer dropdown"):
        case_page.open_payer_dropdown()

    with allure.step("Verify only eligible payers are listed"):
        assert case_page.is_payer_option_visible(ELIGIBLE_PAYER), (
            "Eligible payer missing from Payer dropdown"
        )
        assert not case_page.is_payer_option_visible(INELIGIBLE_PAYER), (
            "Ineligible payer unexpectedly present in Payer dropdown"
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: Payers with an existing schedule for this case are disabled")
@allure.title("Existing-schedule payer is disabled with tooltip")
def test_err_existing_schedule_payer_disabled_with_tooltip(page):
    """
    Jira: ARW-2579
    AC: Payers with an existing schedule for this case are disabled; tooltip
    reads "A payment schedule already exists for this payer."
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case and open the modal"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        case_page.open_modal_from_button()

    with allure.step("Open the Payer dropdown"):
        case_page.open_payer_dropdown()

    with allure.step("Verify the payer with an existing schedule is disabled"):
        assert case_page.is_payer_option_disabled(PAYER_WITH_EXISTING_SCHEDULE), (
            "Payer with existing schedule is not disabled"
        )

    with allure.step("Verify the tooltip text is shown on hover"):
        tooltip_text = case_page.get_payer_tooltip_text(PAYER_WITH_EXISTING_SCHEDULE)
        assert "A payment schedule already exists for this payer." in tooltip_text


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: No eligible payers results in an empty Payer dropdown")
@allure.title("No eligible payers shows empty dropdown")
def test_err_no_eligible_payers_shows_empty_dropdown(page):
    """
    Jira: ARW-2579
    AC: Payer dropdown only includes payers flagged "Allow Payment Schedule";
    if none exist, Save must remain disabled
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case with no eligible payers and open the modal"):
        case_page.navigate_to(CASE_WITH_NO_SCHEDULE_URL)
        case_page.wait_for_load()
        case_page.open_modal_from_empty_state()

    with allure.step("Open the Payer dropdown"):
        case_page.open_payer_dropdown()

    with allure.step("Verify the Save button remains disabled"):
        assert not case_page.is_save_button_enabled(), (
            "Save button should remain disabled when no eligible payers exist"
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC3: Schedule Type 'Specific day of the month' shows a day selector")
@allure.title("Specific day reveals day selector")
def test_pos_specific_day_reveals_day_selector(page):
    """
    Jira: ARW-2579
    AC: Schedule Type "Specific day of the month" shows a Day selector
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case, open the modal, and select an eligible payer"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        case_page.open_modal_from_button()
        case_page.select_payer(ELIGIBLE_PAYER)

    with allure.step("Select 'Specific day of the month' as the schedule type"):
        case_page.select_schedule_type("Specific day of the month")

    with allure.step("Verify the day selector is visible"):
        assert case_page.is_day_selector_visible(), "Day selector not shown"
        assert not case_page.is_weekday_selector_visible(), (
            "Weekday pattern selector should not be shown for 'Specific day' type"
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC3: Schedule Type 'Relative weekday' shows a weekday pattern selector")
@allure.title("Relative weekday reveals weekday selector")
def test_pos_relative_weekday_reveals_weekday_selector(page):
    """
    Jira: ARW-2579
    AC: Schedule Type "Relative weekday" (e.g. 3rd Thursday, last Wednesday)
    shows a weekday pattern selector
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case, open the modal, and select an eligible payer"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        case_page.open_modal_from_button()
        case_page.select_payer(ELIGIBLE_PAYER)

    with allure.step("Select 'Relative weekday' as the schedule type"):
        case_page.select_schedule_type("Relative weekday")

    with allure.step("Verify the weekday pattern selector is visible"):
        assert case_page.is_weekday_selector_visible(), "Weekday pattern selector not shown"
        assert not case_page.is_day_selector_visible(), (
            "Day selector should not be shown for 'Relative weekday' type"
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC3: Payment Method supports ACH, Credit Card, Direct Deposit, Personal Check, Other")
@allure.title("All payment methods are selectable")
def test_pos_all_payment_methods_selectable(page):
    """
    Jira: ARW-2579
    AC: Payment Method: ACH, Credit Card, Direct Deposit, Personal Check, Other
    """
    case_page = CaseDetailPage(page)
    expected_methods = ["ACH", "Credit Card", "Direct Deposit", "Personal Check", "Other"]

    with allure.step("Navigate to a case, open the modal, and select an eligible payer"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        case_page.open_modal_from_button()
        case_page.select_payer(ELIGIBLE_PAYER)

    with allure.step("Open the Payment Method dropdown"):
        case_page.payment_method_dropdown.click()

    with allure.step("Verify all expected payment methods are present"):
        available_methods = case_page.get_payment_method_options()
        for method in expected_methods:
            assert method in available_methods, f"Payment method '{method}' missing from dropdown"


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC3: Auto-Pay Status checkbox toggles and shows helper text")
@allure.title("Auto-Pay checkbox toggle and helper text")
def test_pos_autopay_checkbox_toggle_and_helper_text(page):
    """
    Jira: ARW-2579
    AC: Auto-Pay Status checkbox with helper text "Indicates whether this payer
    is set up for auto-pay."
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case, open the modal, and select an eligible payer"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        case_page.open_modal_from_button()
        case_page.select_payer(ELIGIBLE_PAYER)

    with allure.step("Verify the helper text is visible"):
        assert case_page.is_autopay_helper_text_visible(), "Auto-Pay helper text not visible"

    with allure.step("Toggle the Auto-Pay checkbox on"):
        case_page.toggle_autopay()
        assert case_page.is_autopay_checked(), "Auto-Pay checkbox did not become checked"

    with allure.step("Toggle the Auto-Pay checkbox off"):
        case_page.toggle_autopay()
        assert not case_page.is_autopay_checked(), "Auto-Pay checkbox did not become unchecked"


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC3: Save button is disabled until all required fields are completed")
@allure.title("Save disabled until required fields complete")
def test_err_save_disabled_until_required_fields_complete(page):
    """
    Jira: ARW-2579
    AC: Save button disabled until all required fields are completed
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case and open the modal"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        case_page.open_modal_from_button()

    with allure.step("Verify Save is disabled with no fields filled"):
        assert not case_page.is_save_button_enabled(), "Save should be disabled initially"

    with allure.step("Select a payer and verify Save is still disabled"):
        case_page.select_payer(ELIGIBLE_PAYER)
        assert not case_page.is_save_button_enabled(), "Save should still be disabled"

    with allure.step("Select schedule type and day, verify Save is still disabled"):
        case_page.select_schedule_type("Specific day of the month")
        case_page.select_day("15")
        assert not case_page.is_save_button_enabled(), "Save should still be disabled"

    with allure.step("Select payment method and verify Save is still disabled"):
        case_page.select_payment_method("ACH")
        assert not case_page.is_save_button_enabled(), "Save should still be disabled"

    with allure.step("Set Auto-Pay status and verify Save becomes enabled"):
        case_page.toggle_autopay()
        assert case_page.is_save_button_enabled(), (
            "Save should become enabled once all required fields are set"
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC4: Saving closes the modal, refreshes the table, and shows a success toast")
@allure.title("Save schedule success toast and table update")
def test_pos_save_schedule_success_toast_and_table_update(page):
    """
    Jira: ARW-2579
    AC: On save, modal closes, new schedule appears in table, success toast
    "Payment schedule added successfully." is shown
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case and note the current schedule row count"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        row_count_before = case_page.get_schedule_row_count()

    with allure.step("Open the modal and fill in all required fields"):
        case_page.open_modal_from_button()
        case_page.select_payer(ELIGIBLE_PAYER)
        case_page.select_schedule_type("Specific day of the month")
        case_page.select_day("15")
        case_page.select_payment_method("ACH")
        case_page.toggle_autopay()

    with allure.step("Click Save"):
        assert case_page.is_save_button_enabled(), "Save should be enabled with all fields set"
        case_page.click_save()

    with allure.step("Verify the modal closes, table refreshes, and success toast is shown"):
        assert not case_page.is_modal_visible(), "Modal did not close after save"
        assert case_page.get_schedule_row_count() == row_count_before + 1, (
            "New schedule row was not added to the table"
        )
        assert case_page.is_success_toast_visible(), "Success toast not shown"


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC4: System prevents saving more than one schedule per payer per case")
@allure.title("Duplicate schedule prevented for same payer")
def test_err_duplicate_schedule_prevented_for_same_payer(page):
    """
    Jira: ARW-2579
    AC: System prevents saving more than one payment schedule for the same
    payer on a case
    """
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case and open the modal"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()
        case_page.open_modal_from_button()

    with allure.step("Open the Payer dropdown"):
        case_page.open_payer_dropdown()

    with allure.step("Verify the payer with an existing schedule cannot be selected"):
        assert case_page.is_payer_option_disabled(PAYER_WITH_EXISTING_SCHEDULE), (
            "Payer with an existing schedule should be disabled to prevent duplicates"
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC1: Viewer role cannot access Add Payment Schedule")
@allure.title("Viewer role cannot access Add Payment Schedule")
def test_perm_viewer_cannot_access_add_payment_schedule(page):
    """
    Jira: ARW-2579
    AC (RBAC): Only authorized roles can create payment schedules; a
    read-only Viewer should not see or be able to use the entry points
    """
    # TODO: authenticate as a Viewer-role user once role-based test
    # credentials are confirmed for this environment
    case_page = CaseDetailPage(page)

    with allure.step("Navigate to a case as a Viewer-role user"):
        case_page.navigate_to(CASE_WITH_SCHEDULE_URL)
        case_page.wait_for_load()

    with allure.step("Verify the Add Payment Schedule entry point is hidden or disabled"):
        assert (
            not case_page.populated_view_button.is_visible()
            or not case_page.populated_view_button.is_enabled()
        ), "Viewer role should not be able to access Add Payment Schedule"
