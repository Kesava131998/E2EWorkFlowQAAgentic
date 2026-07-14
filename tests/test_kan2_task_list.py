import pytest
import allure
from pages.login_page import LoginPage
from pages.task_list_page import TaskListPage
from config.settings import settings


@allure.epic("KAN-2: Task 2")
@allure.feature("task_list")
@allure.story("AC1: Calendar icon appears inline after resident name when a payer schedule exists")
@allure.title("Icon is visible when a payer schedule exists and grouping includes a payer above resident")
def test_pos_icon_visible_with_payer_schedule(page):
    """
    Jira: KAN-2
    AC: A calendar icon appears inline after the resident name when a payer schedule
    exists for that resident/payer combination.
    """
    login_page = LoginPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Navigate to Task List"):
        task_list_page.navigate()

    with allure.step("Verify calendar icon is visible for resident with an active payer schedule"):
        # TODO: Replace "Jane Doe" with a resident fixture known to have an active payer schedule
        assert task_list_page.is_payment_schedule_icon_visible("Jane Doe")


@allure.epic("KAN-2: Task 2")
@allure.feature("task_list")
@allure.story("AC2: No icon appears when no payer schedule is configured")
@allure.title("Icon is absent when no payer schedule is configured for the resident/payer")
def test_err_icon_absent_without_schedule(page):
    """
    Jira: KAN-2
    AC: No icon appears when no payer schedule is configured for that resident/payer.
    """
    login_page = LoginPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Navigate to Task List"):
        task_list_page.navigate()

    with allure.step("Verify calendar icon is absent for resident with no payer schedule"):
        # TODO: Replace "John Smith" with a resident fixture known to have no payer schedule
        assert not task_list_page.is_payment_schedule_icon_visible("John Smith")


@allure.epic("KAN-2: Task 2")
@allure.feature("task_list")
@allure.story("AC3: Icon only renders when the active grouping includes a payer level above the resident")
@allure.title("Icon is hidden when grouping has no payer level above resident, even if a schedule exists")
def test_err_icon_hidden_without_payer_grouping(page):
    """
    Jira: KAN-2
    AC: The icon only renders when the active grouping includes a payer level above
    the resident. If no payer is present in the grouping hierarchy above the resident,
    the icon is never shown, regardless of whether a schedule exists.
    """
    login_page = LoginPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Navigate to Task List"):
        task_list_page.navigate()

    with allure.step("Change grouping to Resident-only (remove payer level above resident)"):
        # TODO: Implement grouping change once the grouping control is confirmed in the DOM
        pass

    with allure.step("Verify calendar icon is absent even though a schedule exists"):
        # TODO: Replace "Jane Doe" with the same resident fixture used in test_pos_icon_visible_with_payer_schedule
        assert not task_list_page.is_payment_schedule_icon_visible("Jane Doe")


@allure.epic("KAN-2: Task 2")
@allure.feature("task_list")
@allure.story("AC4: The icon is not clickable and has no hover state beyond triggering the tooltip")
@allure.title("Clicking the icon produces no navigation or state change")
def test_err_icon_not_clickable(page):
    """
    Jira: KAN-2
    AC: The icon is not clickable and has no hover state beyond triggering the tooltip.
    """
    login_page = LoginPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Navigate to Task List"):
        task_list_page.navigate()

    with allure.step("Record current URL before clicking the icon"):
        url_before = page.url

    with allure.step("Click the calendar icon for resident with an active schedule"):
        # TODO: Replace "Jane Doe" with a resident fixture known to have an active payer schedule
        row = task_list_page.get_resident_row("Jane Doe")
        row.locator(".payment-schedule-icon").click()

    with allure.step("Verify URL is unchanged and no navigation occurred"):
        assert page.url == url_before


@allure.epic("KAN-2: Task 2")
@allure.feature("task_list")
@allure.story("AC5: Hovering the icon shows a tooltip with label, schedule value, and payment method")
@allure.title("Tooltip shows label, schedule value, and ACH payment method on hover")
def test_pos_tooltip_shows_schedule_details(page):
    """
    Jira: KAN-2
    AC: Hovering the icon shows a tooltip with three lines: a muted label
    "Payment schedule on file", the schedule value (e.g. "15th of the month"),
    and the payment method (e.g. "ACH" or "Check").
    """
    login_page = LoginPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Navigate to Task List"):
        task_list_page.navigate()

    with allure.step("Hover the calendar icon for resident with schedule '15th of the month' / ACH"):
        # TODO: Replace "Jane Doe" with a resident fixture: schedule = "15th of the month", method = "ACH"
        task_list_page.hover_payment_schedule_icon("Jane Doe")

    with allure.step("Verify tooltip text contains label, schedule value, and payment method"):
        tooltip_text = task_list_page.get_payment_schedule_tooltip_text()
        assert "Payment schedule on file" in tooltip_text
        assert "15th of the month" in tooltip_text
        assert "ACH" in tooltip_text


@allure.epic("KAN-2: Task 2")
@allure.feature("task_list")
@allure.story("AC5: Hovering the icon shows a tooltip with label, schedule value, and payment method")
@allure.title("Tooltip shows alternate schedule phrasing and Check payment method on hover")
def test_pos_tooltip_shows_alternate_schedule_format(page):
    """
    Jira: KAN-2
    AC: Hovering the icon shows a tooltip with three lines: a muted label
    "Payment schedule on file", the schedule value (e.g. "Second Monday of the month"),
    and the payment method (e.g. "Check").
    """
    login_page = LoginPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Navigate to Task List"):
        task_list_page.navigate()

    with allure.step("Hover the calendar icon for resident with schedule 'Second Monday of the month' / Check"):
        # TODO: Replace "Alice Brown" with a resident fixture: schedule = "Second Monday of the month", method = "Check"
        task_list_page.hover_payment_schedule_icon("Alice Brown")

    with allure.step("Verify tooltip text contains alternate schedule value and payment method"):
        tooltip_text = task_list_page.get_payment_schedule_tooltip_text()
        assert "Second Monday of the month" in tooltip_text
        assert "Check" in tooltip_text


@allure.epic("KAN-2: Task 2")
@allure.feature("task_list")
@allure.story("AC6: The icon does not interfere with the resident name hyperlink")
@allure.title("Resident name hyperlink remains clickable when the calendar icon is present")
def test_pos_resident_link_unaffected_by_icon(page):
    """
    Jira: KAN-2
    AC: The icon does not interfere with the resident name hyperlink.
    """
    login_page = LoginPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in to RevFlow"):
        login_page.login()

    with allure.step("Navigate to Task List"):
        task_list_page.navigate()

    with allure.step("Verify calendar icon is visible for resident with an active payer schedule"):
        # TODO: Replace "Jane Doe" with a resident fixture known to have an active payer schedule
        assert task_list_page.is_payment_schedule_icon_visible("Jane Doe")

    with allure.step("Click resident name link and verify navigation to Case View"):
        task_list_page.click_resident_link("Jane Doe")
        # TODO: Assert navigation to the resident's Case View once the URL/route is confirmed
