import pytest
import allure
from pages.login_page import LoginPage
from pages.case_detail_page import CaseDetailPage
from config.settings import settings


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC1: User can open Add Payment Schedule modal from empty state")
@allure.title("Open Add Payment Schedule modal from empty-state CTA")
def test_pos_open_add_payment_schedule_modal_from_empty_state(page):
    """
    Jira: ARW-2579
    AC: User can click "Add Payment Schedule" from the empty state CTA and the
    modal opens titled "Add Payment Schedule".
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case with no existing payment schedules"):
        # TODO: Implement navigation to a case detail view with zero schedules
        pass

    with allure.step("Step 2: Click empty-state Add Payment Schedule CTA"):
        case_detail_page.click_empty_state_add_button()

    with allure.step("Step 3: Verify modal opens with expected title"):
        case_detail_page.verify_modal_open()
        assert case_detail_page.modal_title.inner_text() == "Add Payment Schedule"


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC1: User can open Add Payment Schedule modal from populated view")
@allure.title("Open Add Payment Schedule modal from populated view button")
def test_pos_open_add_payment_schedule_modal_from_populated_view(page):
    """
    Jira: ARW-2579
    AC: User can click "Add Payment Schedule" from the button in the populated
    table view and the modal opens.
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case with an existing payment schedule"):
        # TODO: Implement navigation to a case detail view with an existing schedule
        pass

    with allure.step("Step 2: Click Add Payment Schedule button in populated view"):
        case_detail_page.click_populated_view_add_button()

    with allure.step("Step 3: Verify modal opens"):
        case_detail_page.verify_modal_open()


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: Payer dropdown only includes payers flagged Allow Payment Schedule")
@allure.title("Payer dropdown shows only eligible payers")
def test_pos_payer_dropdown_shows_only_eligible_payers(page):
    """
    Jira: ARW-2579
    AC: Payer dropdown only includes payers whose payer category is flagged
    "Allow Payment Schedule".
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case with eligible and ineligible payers"):
        # TODO: Implement navigation to a case with mixed payer eligibility
        pass

    with allure.step("Step 2: Open Add Payment Schedule modal"):
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()

    with allure.step("Step 3: Open Payer dropdown"):
        case_detail_page.payer_dropdown.click()

    with allure.step("Step 4: Verify only eligible payers are listed"):
        # TODO: Assert eligible payer options are visible and ineligible payer is absent
        pass


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: Payer with existing schedule is disabled with tooltip")
@allure.title("Payer with existing schedule is disabled with tooltip")
def test_err_payer_with_existing_schedule_disabled_with_tooltip(page):
    """
    Jira: ARW-2579
    AC: Payers with an existing schedule for this case are disabled with
    tooltip "A payment schedule already exists for this payer."
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case where Payer A already has a schedule"):
        # TODO: Implement navigation to a case with an existing schedule for Payer A
        pass

    with allure.step("Step 2: Open Add Payment Schedule modal and Payer dropdown"):
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()
        case_detail_page.payer_dropdown.click()

    with allure.step("Step 3: Verify Payer A option is disabled"):
        assert case_detail_page.is_payer_option_disabled("Payer A")

    with allure.step("Step 4: Verify tooltip text on hover"):
        case_detail_page.hover_payer_option("Payer A")
        assert (
            case_detail_page.get_payer_option_tooltip_text()
            == "A payment schedule already exists for this payer."
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: Schedule Type 'Specific day of the month' shows day selector")
@allure.title("Specific day schedule type shows day selector")
def test_pos_specific_day_schedule_type_shows_day_selector(page):
    """
    Jira: ARW-2579
    AC: Schedule Details show a day selector when Schedule Type is
    "Specific day of the month".
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case and open Add Payment Schedule modal"):
        # TODO: Implement navigation to a case detail view
        pass
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()

    with allure.step("Step 2: Select an eligible payer"):
        # TODO: Select a known eligible payer
        pass

    with allure.step("Step 3: Select Schedule Type 'Specific day of the month'"):
        case_detail_page.select_schedule_type("Specific day of the month")

    with allure.step("Step 4: Verify day selector is visible"):
        assert case_detail_page.is_day_selector_visible()


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: Schedule Type 'Relative weekday' shows weekday pattern selector")
@allure.title("Relative weekday schedule type shows pattern selector")
def test_pos_relative_weekday_schedule_type_shows_pattern_selector(page):
    """
    Jira: ARW-2579
    AC: Schedule Details show a weekday pattern selector when Schedule Type is
    "Relative weekday" (e.g., 3rd Thursday, last Wednesday).
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case and open Add Payment Schedule modal"):
        # TODO: Implement navigation to a case detail view
        pass
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()

    with allure.step("Step 2: Select an eligible payer"):
        # TODO: Select a known eligible payer
        pass

    with allure.step("Step 3: Select Schedule Type 'Relative weekday'"):
        case_detail_page.select_schedule_type("Relative weekday")

    with allure.step("Step 4: Verify weekday pattern selector is visible"):
        assert case_detail_page.is_weekday_pattern_selector_visible()


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: Payment Method dropdown lists all defined methods")
@allure.title("Payment Method dropdown lists all options")
def test_pos_payment_method_dropdown_lists_all_options(page):
    """
    Jira: ARW-2579
    AC: Payment Method options are ACH, Credit Card, Direct Deposit,
    Personal Check, Other.
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case and open Add Payment Schedule modal"):
        # TODO: Implement navigation to a case detail view
        pass
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()

    with allure.step("Step 2: Open Payment Method dropdown"):
        case_detail_page.payment_method_dropdown.click()

    with allure.step("Step 3: Verify all five payment method options are present"):
        for method in ["ACH", "Credit Card", "Direct Deposit", "Personal Check", "Other"]:
            assert case_detail_page.payment_method_dropdown.get_by_role(
                "option", name=method
            ).is_visible()


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: Auto-Pay Status checkbox shows helper text")
@allure.title("Auto-Pay checkbox shows helper text")
def test_pos_autopay_checkbox_shows_helper_text(page):
    """
    Jira: ARW-2579
    AC: Auto-Pay Status checkbox with helper text "Indicates whether this
    payer is set up for auto-pay."
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case and open Add Payment Schedule modal"):
        # TODO: Implement navigation to a case detail view
        pass
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()

    with allure.step("Step 2: Toggle Auto-Pay Status checkbox"):
        case_detail_page.toggle_auto_pay_status()

    with allure.step("Step 3: Verify helper text is displayed"):
        assert (
            case_detail_page.get_auto_pay_helper_text()
            == "Indicates whether this payer is set up for auto-pay."
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC3: Save button disabled until all required fields are completed")
@allure.title("Save button disabled until required fields complete")
def test_err_save_disabled_until_required_fields_complete(page):
    """
    Jira: ARW-2579
    AC: Save button disabled until all required fields are completed.
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case and open Add Payment Schedule modal"):
        # TODO: Implement navigation to a case detail view
        pass
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()

    with allure.step("Step 2: Verify Save button is disabled by default"):
        assert not case_detail_page.is_save_enabled()

    with allure.step("Step 3: Select only a Payer field"):
        # TODO: Select an eligible payer, leave remaining fields empty
        pass

    with allure.step("Step 4: Verify Save button is still disabled"):
        assert not case_detail_page.is_save_enabled()


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC3: Save button enabled once all required fields are completed")
@allure.title("Save button enabled when required fields complete")
def test_pos_save_enabled_when_required_fields_complete(page):
    """
    Jira: ARW-2579
    AC: Save button becomes enabled once Payer, Schedule Type, Schedule
    Details, and Payment Method are all completed.
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case and open Add Payment Schedule modal"):
        # TODO: Implement navigation to a case detail view
        pass
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()

    with allure.step("Step 2: Fill Payer, Schedule Type, Schedule Details, Payment Method"):
        # TODO: Fill in all required fields with valid data
        pass

    with allure.step("Step 3: Verify Save button is enabled"):
        assert case_detail_page.is_save_enabled()


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC3: System prevents duplicate payment schedule for same payer")
@allure.title("Duplicate payment schedule prevented for same payer")
def test_err_duplicate_payment_schedule_prevented(page):
    """
    Jira: ARW-2579
    AC: System prevents saving more than one payment schedule for the same
    payer on a case.
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case where Payer A already has a schedule"):
        # TODO: Implement navigation to a case with an existing schedule for Payer A
        pass

    with allure.step("Step 2: Open Add Payment Schedule modal and Payer dropdown"):
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()
        case_detail_page.payer_dropdown.click()

    with allure.step("Step 3: Verify Payer A cannot be selected"):
        assert case_detail_page.is_payer_option_disabled("Payer A")


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC4: Successful save closes modal, updates table, shows success toast")
@allure.title("Save payment schedule succeeds")
def test_pos_save_payment_schedule_success(page):
    """
    Jira: ARW-2579
    AC: On save, modal closes, new schedule appears in table, and success
    toast "Payment schedule added successfully." is shown.
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Step 1: Navigate to a case and open Add Payment Schedule modal"):
        # TODO: Implement navigation to a case detail view
        pass
        case_detail_page.click_populated_view_add_button()
        case_detail_page.verify_modal_open()

    with allure.step("Step 2: Fill all required fields with valid data for Payer C"):
        # TODO: Fill in Payer C, Relative weekday / 3rd Thursday, Direct Deposit, Auto-Pay checked
        pass

    with allure.step("Step 3: Click Save"):
        case_detail_page.click_save()

    with allure.step("Step 4: Verify modal closes"):
        expect_modal_closed = case_detail_page.modal
        assert not expect_modal_closed.is_visible()

    with allure.step("Step 5: Verify new schedule row appears for Payer C"):
        assert case_detail_page.get_schedule_row("Payer C").is_visible()

    with allure.step("Step 6: Verify success toast text"):
        assert (
            case_detail_page.get_success_toast_text()
            == "Payment schedule added successfully."
        )


@allure.epic("ARW-2579: FE - Add a Payment Schedule to a Case")
@allure.feature("payment_schedule")
@allure.story("AC2: Viewer role cannot add a payment schedule")
@allure.title("Viewer role cannot add payment schedule")
def test_perm_viewer_cannot_add_payment_schedule(page):
    """
    Jira: ARW-2579
    AC: Access-control assumption — role restrictions are not explicitly
    defined in the ticket; validate against actual role definitions before
    relying on this test.
    """
    login_page = LoginPage(page)
    case_detail_page = CaseDetailPage(page)

    with allure.step("Log in to RevFlow as a Viewer-role user"):
        # TODO: Implement login with a Viewer-role account
        pass

    with allure.step("Step 1: Navigate to the case detail view"):
        # TODO: Implement navigation to a case detail view
        pass

    with allure.step("Step 2: Verify Add Payment Schedule CTA/button is disabled or hidden"):
        # TODO: Assert CTA/button is not enabled for Viewer role
        pass
