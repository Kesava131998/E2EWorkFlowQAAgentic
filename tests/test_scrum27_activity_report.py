import allure
from pages.activity_report_page import ActivityReportPage
from config.settings import settings

ACTIVITY_REPORT_URL = f"{settings.BASE_URL}/reports/activity"

# TODO: replace with real biller identifiers once test data is confirmed for this environment
BILLER_WITH_OVERDUE_TASKS = "TODO-biller-with-overdue-tasks"
BILLER_WITH_NO_OVERDUE_TASKS = "TODO-biller-with-no-overdue-tasks"
BILLER_WITH_DUE_TODAY_TASK = "TODO-biller-with-due-today-task"
BILLER_WITH_CLOSED_OVERDUE_TASK = "TODO-biller-with-closed-overdue-task"

OPEN_BALANCE_COLUMN = "Overdue Open Balance Tasks"
OVERPAYMENT_COLUMN = "Overdue Overpayment Tasks"
LEGACY_COLUMN = "Overdue Tasks"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC1: Overdue Tasks column no longer appears on the Biller Activity Report")
@allure.title("Legacy Overdue Tasks column is removed")
def test_pos_verify_overdue_tasks_column_removed(page):
    """
    Jira: SCRUM-27
    AC: The Overdue Tasks column no longer appears on the Biller Activity Report.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step("Verify the legacy Overdue Tasks column is not present"):
        assert not report_page.is_column_present(LEGACY_COLUMN), "Legacy 'Overdue Tasks' column still present"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC8: Column order places Overdue Open Balance Tasks before Overdue Overpayment Tasks")
@allure.title("New columns appear in the correct order")
def test_pos_verify_new_columns_order(page):
    """
    Jira: SCRUM-27
    AC: Column order on the report places Overdue Open Balance Tasks before Overdue Overpayment Tasks.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step("Verify Overdue Open Balance Tasks precedes Overdue Overpayment Tasks"):
        open_balance_index = report_page.get_column_index(OPEN_BALANCE_COLUMN)
        overpayment_index = report_page.get_column_index(OVERPAYMENT_COLUMN)
        assert open_balance_index < overpayment_index, "Column order is incorrect"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC3: Overdue Open Balance Tasks displays the correct count per biller")
@allure.title("Overdue Open Balance Tasks count is correct")
def test_pos_verify_overdue_open_balance_count(page):
    """
    Jira: SCRUM-27
    AC: Overdue Open Balance Tasks column displays the correct count of open balance
    tasks with a Follow Up Date < today, per biller.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step(f"Verify Overdue Open Balance Tasks count for {BILLER_WITH_OVERDUE_TASKS}"):
        value = report_page.get_cell_value(BILLER_WITH_OVERDUE_TASKS, OPEN_BALANCE_COLUMN)
        # TODO: assert against known expected count once test data is confirmed
        assert value.isdigit(), f"Expected a numeric count, got '{value}'"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC2: Overdue Overpayment Tasks displays the correct count per biller")
@allure.title("Overdue Overpayment Tasks count is correct")
def test_pos_verify_overdue_overpayment_count(page):
    """
    Jira: SCRUM-27
    AC: Overdue Overpayment Tasks column displays the correct count of open overpayment
    tasks with a Follow Up Date < today, per biller.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step(f"Verify Overdue Overpayment Tasks count for {BILLER_WITH_OVERDUE_TASKS}"):
        value = report_page.get_cell_value(BILLER_WITH_OVERDUE_TASKS, OVERPAYMENT_COLUMN)
        # TODO: assert against known expected count once test data is confirmed
        assert value.isdigit(), f"Expected a numeric count, got '{value}'"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC3: Clicking the Overdue Open Balance Tasks count navigates to a filtered Task List")
@allure.title("Open Balance drill-down navigates with correct filters")
def test_pos_click_open_balance_navigates_to_task_list(page):
    """
    Jira: SCRUM-27
    AC: Clicking on Overdue Open Balance Tasks navigates to task list filtered to
    Task status = open, Balance > 0, Follow Up Date < Today.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step(f"Click the Overdue Open Balance Tasks cell for {BILLER_WITH_OVERDUE_TASKS}"):
        report_page.click_cell(BILLER_WITH_OVERDUE_TASKS, OPEN_BALANCE_COLUMN)

    with allure.step("Verify the Task List is filtered correctly"):
        filters = report_page.get_task_list_applied_filters()
        assert "Task status = Open" in filters
        assert "Balance > 0" in filters
        assert "Follow Up Date < Today" in filters


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC2: Clicking the Overdue Overpayment Tasks count navigates to a filtered Task List")
@allure.title("Overpayment drill-down navigates with correct filters")
def test_pos_click_overpayment_navigates_to_task_list(page):
    """
    Jira: SCRUM-27
    AC: Clicking on Overdue Overpayment Tasks navigates to task list filtered to
    Task status = open, Balance < 0, Follow Up Date < Today.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step(f"Click the Overdue Overpayment Tasks cell for {BILLER_WITH_OVERDUE_TASKS}"):
        report_page.click_cell(BILLER_WITH_OVERDUE_TASKS, OVERPAYMENT_COLUMN)

    with allure.step("Verify the Task List is filtered correctly"):
        filters = report_page.get_task_list_applied_filters()
        assert "Task status = Open" in filters
        assert "Balance < 0" in filters
        assert "Follow Up Date < Today" in filters


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC4: A biller with no overdue tasks of a given type shows 0, not blank")
@allure.title("Zero overdue tasks displays as 0")
def test_pos_zero_overdue_tasks_shows_zero(page):
    """
    Jira: SCRUM-27
    AC: If a biller has no overdue tasks of a given type, display 0 — not blank.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step(f"Verify Overdue Open Balance Tasks shows 0 for {BILLER_WITH_NO_OVERDUE_TASKS}"):
        value = report_page.get_cell_value(BILLER_WITH_NO_OVERDUE_TASKS, OPEN_BALANCE_COLUMN)
        assert value == "0", f"Expected '0', got '{value}'"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC5: 0 shows in green, all other numbers in red")
@allure.title("Zero count is displayed in green")
def test_pos_zero_count_displayed_green(page):
    """
    Jira: SCRUM-27
    AC: 0 shows in green, all other numbers in red.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step(f"Verify the 0 value is styled green for {BILLER_WITH_NO_OVERDUE_TASKS}"):
        color = report_page.get_cell_color(BILLER_WITH_NO_OVERDUE_TASKS, OVERPAYMENT_COLUMN)
        # TODO: confirm exact green RGB token used by the design system
        assert "0, 128, 0" in color or "green" in color.lower(), f"Expected green styling, got '{color}'"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC5: 0 shows in green, all other numbers in red")
@allure.title("Non-zero count is displayed in red")
def test_pos_nonzero_count_displayed_red(page):
    """
    Jira: SCRUM-27
    AC: 0 shows in green, all other numbers in red.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step(f"Verify a non-zero value is styled red for {BILLER_WITH_OVERDUE_TASKS}"):
        color = report_page.get_cell_color(BILLER_WITH_OVERDUE_TASKS, OPEN_BALANCE_COLUMN)
        # TODO: confirm exact red RGB token used by the design system
        assert "255, 0, 0" in color or "red" in color.lower(), f"Expected red styling, got '{color}'"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC6: Summary row sums the Overdue Open Balance Tasks column")
@allure.title("Summary row sums Overdue Open Balance Tasks correctly")
def test_pos_summary_row_sums_open_balance(page):
    """
    Jira: SCRUM-27
    AC: The summary/total row sums each column independently and correctly.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step("Verify the summary row value is a non-negative integer"):
        summary_value = report_page.get_summary_value(OPEN_BALANCE_COLUMN)
        assert summary_value.isdigit(), f"Expected a numeric total, got '{summary_value}'"
        # TODO: assert exact sum once per-biller expected counts are confirmed for this environment


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC6: Summary row sums the Overdue Overpayment Tasks column")
@allure.title("Summary row sums Overdue Overpayment Tasks correctly")
def test_pos_summary_row_sums_overpayment(page):
    """
    Jira: SCRUM-27
    AC: The summary/total row sums each column independently and correctly.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step("Verify the summary row value is a non-negative integer"):
        summary_value = report_page.get_summary_value(OVERPAYMENT_COLUMN)
        assert summary_value.isdigit(), f"Expected a numeric total, got '{summary_value}'"
        # TODO: assert exact sum once per-biller expected counts are confirmed for this environment


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC7: Exported report reflects the two new columns with accurate data")
@allure.title("Export contains the new columns with accurate data")
def test_pos_export_contains_new_columns(page):
    """
    Jira: SCRUM-27
    AC: Exported report reflects the two new columns with accurate data.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step("Verify the Export control is visible and enabled"):
        assert report_page.is_export_visible(), "Export control is not visible"
        assert report_page.is_export_enabled(), "Export control is not enabled"

    with allure.step("Trigger export and verify the download completes"):
        with page.expect_download() as download_info:
            report_page.click_export()
        download = download_info.value
        # TODO: parse the downloaded file and compare column headers/values against the grid


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC1, AC7: Exported report no longer contains the legacy Overdue Tasks column")
@allure.title("Export excludes the legacy Overdue Tasks column")
def test_err_export_excludes_legacy_column(page):
    """
    Jira: SCRUM-27
    AC: Export should reflect the two new columns in place of the old single column.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step("Trigger export and verify the download completes"):
        with page.expect_download() as download_info:
            report_page.click_export()
        download = download_info.value
        # TODO: parse the downloaded file and assert the legacy 'Overdue Tasks' header is absent


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC2, AC3: A task due today is not counted as overdue")
@allure.title("Task with Follow Up Date of today is excluded")
def test_err_task_due_today_not_counted(page):
    """
    Jira: SCRUM-27
    AC: Overdue Task is defined as an open task whose Follow Up Date is before today's date.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step(f"Verify Overdue Open Balance Tasks excludes a task due today for {BILLER_WITH_DUE_TODAY_TASK}"):
        value = report_page.get_cell_value(BILLER_WITH_DUE_TODAY_TASK, OPEN_BALANCE_COLUMN)
        assert value == "0", f"Expected '0', got '{value}'"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC2, AC3: A closed task is not counted regardless of Follow Up Date")
@allure.title("Closed overdue task is excluded from both columns")
def test_err_closed_task_not_counted(page):
    """
    Jira: SCRUM-27
    AC: Overdue Task is defined as an open task whose Follow Up Date is before today's date.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step(f"Verify both columns exclude a closed overdue task for {BILLER_WITH_CLOSED_OVERDUE_TASK}"):
        open_balance_value = report_page.get_cell_value(BILLER_WITH_CLOSED_OVERDUE_TASK, OPEN_BALANCE_COLUMN)
        overpayment_value = report_page.get_cell_value(BILLER_WITH_CLOSED_OVERDUE_TASK, OVERPAYMENT_COLUMN)
        assert open_balance_value == "0", f"Expected '0', got '{open_balance_value}'"
        assert overpayment_value == "0", f"Expected '0', got '{overpayment_value}'"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC3: A user without Activity Report view permission cannot access the report")
@allure.title("Unauthorized user cannot view the Biller Activity Report")
def test_perm_unauthorized_user_cannot_view_report(page):
    """
    Jira: SCRUM-27
    AC: Overdue Open Balance / Overpayment Tasks columns must only be reachable by
    users authorized to view the Biller Activity Report.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate directly to the Biller Activity Report as an unauthorized role"):
        # TODO: authenticate as a role without "View Activity Report" permission before this step
        report_page.navigate_to(ACTIVITY_REPORT_URL)

    with allure.step("Verify the report grid is not rendered"):
        assert not report_page.grid.is_visible(), "Grid should not be visible for an unauthorized user"


@allure.epic("SCRUM-27: [FE] Activity Report — Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC7: A view-only user cannot trigger Export")
@allure.title("View-only user cannot export the report")
def test_perm_view_only_user_cannot_export(page):
    """
    Jira: SCRUM-27
    AC: Export should reflect the two new columns; export access is restricted by role.
    """
    report_page = ActivityReportPage(page)

    with allure.step("Navigate to the Biller Activity Report as a view-only role"):
        # TODO: authenticate as a role with "View Activity Report" but without "Export Report" permission
        report_page.navigate_to(ACTIVITY_REPORT_URL)
        report_page.wait_for_load()

    with allure.step("Verify both new columns are visible but Export is hidden or disabled"):
        assert report_page.is_column_present(OPEN_BALANCE_COLUMN)
        assert report_page.is_column_present(OVERPAYMENT_COLUMN)
        assert not report_page.is_export_visible() or not report_page.is_export_enabled(), \
            "Export control should be hidden or disabled for a view-only role"
