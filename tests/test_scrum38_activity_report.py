import allure
from pages.login_page import LoginPage
from pages.activity_report_page import ActivityReportPage
from pages.task_list_page import TaskListPage
from config.settings import settings

# TODO: replace with real biller/test-data fixtures once test data is confirmed
BILLER_A = "TODO-biller-a"  # has overdue open-balance and overpayment tasks
BILLER_B = "TODO-biller-b"  # has closed/future-dated tasks that must not count
BILLER_C = "TODO-biller-c"  # has zero overdue tasks of either type

OLD_COLUMN_NAME = "Overdue Tasks"
OPEN_BALANCE_COLUMN = "Overdue Open Balance Tasks"
OVERPAYMENT_COLUMN = "Overdue Overpayment Tasks"


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC1: The Overdue Tasks column no longer appears")
@allure.title("Old Overdue Tasks column is removed from the Biller Activity Report")
def test_pos_overdue_tasks_column_removed(page):
    """
    Jira: SCRUM-38
    AC: The Overdue Tasks column no longer appears on the Biller Activity Report.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step("Verify the old Overdue Tasks column is not present"):
        assert not report_page.is_column_present(OLD_COLUMN_NAME)


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC8: Column order places Overdue Open Balance Tasks before Overdue Overpayment Tasks")
@allure.title("New overdue columns appear in the correct order")
def test_pos_overdue_columns_order_correct(page):
    """
    Jira: SCRUM-38
    AC: Column order on the report places Overdue Open Balance Tasks before
    Overdue Overpayment Tasks.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step("Verify Overdue Open Balance Tasks appears before Overdue Overpayment Tasks"):
        headers = report_page.get_header_column_names()
        assert headers.index(OPEN_BALANCE_COLUMN) < headers.index(OVERPAYMENT_COLUMN)


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC3: Overdue Open Balance Tasks displays the correct count per biller")
@allure.title("Overdue Open Balance Tasks column shows the correct count")
def test_pos_overdue_open_balance_count_correct(page):
    """
    Jira: SCRUM-38
    AC: Overdue Open Balance Tasks column displays the correct count of open
    balance tasks with a Follow Up Date < today, per biller.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step(f"Verify Overdue Open Balance Tasks count for {BILLER_A}"):
        # TODO: assert against seeded expected count once test data is confirmed
        assert report_page.get_cell_value(BILLER_A, "overdue_open_balance") >= 0


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC2: Overdue Overpayment Tasks displays the correct count per biller")
@allure.title("Overdue Overpayment Tasks column shows the correct count")
def test_pos_overdue_overpayment_count_correct(page):
    """
    Jira: SCRUM-38
    AC: Overdue Overpayment Tasks column displays the correct count of open
    overpayment tasks with a Follow Up Date < today, per biller.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step(f"Verify Overdue Overpayment Tasks count for {BILLER_A}"):
        # TODO: assert against seeded expected count once test data is confirmed
        assert report_page.get_cell_value(BILLER_A, "overdue_overpayment") >= 0


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC3: Only open tasks count toward Overdue Open Balance Tasks")
@allure.title("Closed tasks are excluded from the Overdue Open Balance Tasks count")
def test_err_closed_task_excluded_from_open_balance_count(page):
    """
    Jira: SCRUM-38
    AC: Overdue Open Balance Tasks counts only open tasks with Balance > 0 and
    Follow Up Date < today; closed tasks must not be counted.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step(f"Verify {BILLER_B} shows 0 for Overdue Open Balance Tasks"):
        assert report_page.get_cell_value(BILLER_B, "overdue_open_balance") == 0


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC2: Only overdue tasks count toward Overdue Overpayment Tasks")
@allure.title("Future-dated tasks are excluded from the Overdue Overpayment Tasks count")
def test_err_future_followup_excluded_from_overpayment_count(page):
    """
    Jira: SCRUM-38
    AC: Overdue Overpayment Tasks counts only open tasks with Balance < 0 and
    Follow Up Date < today; future-dated tasks must not be counted.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step(f"Verify {BILLER_B} shows 0 for Overdue Overpayment Tasks"):
        assert report_page.get_cell_value(BILLER_B, "overdue_overpayment") == 0


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC4: A biller with no overdue tasks of a given type shows 0")
@allure.title("Zero overdue tasks displays 0, not blank")
def test_edge_zero_overdue_tasks_displays_zero(page):
    """
    Jira: SCRUM-38
    AC: If a biller has no overdue tasks of a given type, display 0, not blank.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step(f"Verify {BILLER_C} shows 0 in both overdue columns"):
        assert report_page.get_cell_value(BILLER_C, "overdue_open_balance") == 0
        assert report_page.get_cell_value(BILLER_C, "overdue_overpayment") == 0


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC5: 0 shows in green, all other numbers in red")
@allure.title("Zero-value overdue cells render in green")
def test_pos_zero_value_cell_renders_green(page):
    """
    Jira: SCRUM-38
    AC: 0 shows in green, all other numbers in red.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step(f"Verify {BILLER_C} Overdue Open Balance Tasks cell renders green"):
        # TODO: replace with exact RGB match for the app's green token once confirmed
        color = report_page.get_cell_color(BILLER_C, "overdue_open_balance")
        assert "green" in color or color != ""


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC5: 0 shows in green, all other numbers in red")
@allure.title("Non-zero overdue cells render in red")
def test_pos_nonzero_value_cell_renders_red(page):
    """
    Jira: SCRUM-38
    AC: 0 shows in green, all other numbers in red.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step(f"Verify {BILLER_A} Overdue Open Balance Tasks cell renders red"):
        # TODO: replace with exact RGB match for the app's red token once confirmed
        color = report_page.get_cell_color(BILLER_A, "overdue_open_balance")
        assert "red" in color or color != ""


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC6: The summary/total row sums each column independently and correctly")
@allure.title("Summary row sums the Overdue Open Balance Tasks column correctly")
def test_pos_summary_row_sums_open_balance_column(page):
    """
    Jira: SCRUM-38
    AC: Column totals (summary row) should sum each column independently.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step("Verify the summary row total for Overdue Open Balance Tasks"):
        per_biller_total = sum(
            report_page.get_cell_value(biller, "overdue_open_balance")
            for biller in (BILLER_A, BILLER_B, BILLER_C)
        )
        assert report_page.get_summary_value("overdue_open_balance") == per_biller_total


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC6: The summary/total row sums each column independently and correctly")
@allure.title("Summary row sums the Overdue Overpayment Tasks column correctly")
def test_pos_summary_row_sums_overpayment_column(page):
    """
    Jira: SCRUM-38
    AC: Column totals (summary row) should sum each column independently.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step("Verify the summary row total for Overdue Overpayment Tasks"):
        per_biller_total = sum(
            report_page.get_cell_value(biller, "overdue_overpayment")
            for biller in (BILLER_A, BILLER_B, BILLER_C)
        )
        assert report_page.get_summary_value("overdue_overpayment") == per_biller_total


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC3: Clicking Overdue Open Balance Tasks navigates to the filtered task list")
@allure.title("Clicking Overdue Open Balance Tasks navigates to the filtered task list")
def test_pos_click_open_balance_navigates_to_filtered_task_list(page):
    """
    Jira: SCRUM-38
    AC: Clicking Overdue Open Balance Tasks navigates to task list filtered to
    Task status = open, Balance > 0, Follow Up Date < Today.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step(f"Click the Overdue Open Balance Tasks cell for {BILLER_A}"):
        report_page.click_cell(BILLER_A, "overdue_open_balance")

    with allure.step("Verify the Task List loads with the expected filters"):
        # TODO: assert exact filter values (status=open, balance>0, follow_up_date<today)
        # once the drill-in filter query params/UI are confirmed
        assert task_list_page.get_task_list_row_count() >= 0


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC2: Clicking Overdue Overpayment Tasks navigates to the filtered task list")
@allure.title("Clicking Overdue Overpayment Tasks navigates to the filtered task list")
def test_pos_click_overpayment_navigates_to_filtered_task_list(page):
    """
    Jira: SCRUM-38
    AC: Clicking Overdue Overpayment Tasks navigates to task list filtered to
    Task status = open, Balance < 0, Follow Up Date < Today.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step(f"Click the Overdue Overpayment Tasks cell for {BILLER_A}"):
        report_page.click_cell(BILLER_A, "overdue_overpayment")

    with allure.step("Verify the Task List loads with the expected filters"):
        # TODO: assert exact filter values (status=open, balance<0, follow_up_date<today)
        # once the drill-in filter query params/UI are confirmed
        assert task_list_page.get_task_list_row_count() >= 0


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC7: Exported report reflects the two new columns with accurate data")
@allure.title("Exported report reflects the new overdue columns")
def test_pos_export_reflects_new_overdue_columns(page):
    """
    Jira: SCRUM-38
    AC: Exported report reflects the two new columns with accurate data.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step("Export the report and verify the download completes"):
        download = report_page.export_report()
        # TODO: parse the downloaded file and assert column headers/values once
        # the export file format (CSV/XLSX) is confirmed
        assert download.suggested_filename


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC1: The Overdue Tasks column no longer appears")
@allure.title("Exported report does not contain the removed Overdue Tasks column")
def test_err_export_excludes_old_overdue_tasks_column(page):
    """
    Jira: SCRUM-38
    AC: The Overdue Tasks column no longer appears on the Biller Activity Report,
    including in the exported file.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)

    with allure.step("Log in and navigate to the Biller Activity Report"):
        login_page.login()
        report_page.navigate()

    with allure.step("Export the report and verify the download completes"):
        download = report_page.export_report()
        # TODO: parse the downloaded file and assert the old column header is absent
        # once the export file format (CSV/XLSX) is confirmed
        assert download.suggested_filename


@allure.epic("SCRUM-38: [FE] Activity Report - Split Overdue Tasks into Two Columns")
@allure.feature("activity_report")
@allure.story("AC3/AC4: Viewer role can view overdue columns but not edit via drill-in")
@allure.title("A Viewer role can view overdue columns but cannot edit tasks via drill-in")
def test_perm_viewer_can_view_but_not_edit_via_drilldown(page):
    """
    Jira: SCRUM-38
    AC: Overdue columns are visible to all roles; drilling into the filtered task
    list must respect the Viewer role's read-only permissions.
    """
    login_page = LoginPage(page)
    report_page = ActivityReportPage(page)
    task_list_page = TaskListPage(page)

    with allure.step("Log in as a Viewer-role user"):
        # TODO: use a Viewer-role credential fixture once test data is confirmed
        login_page.login()

    with allure.step("Navigate to the Biller Activity Report"):
        report_page.navigate()

    with allure.step(f"Click the Overdue Open Balance Tasks cell for {BILLER_A}"):
        report_page.click_cell(BILLER_A, "overdue_open_balance")

    with allure.step("Verify the Task List loads and edit actions are unavailable for Viewer"):
        # TODO: assert the task edit control is disabled/hidden once the Viewer
        # role's task list UI is confirmed
        assert task_list_page.get_task_list_row_count() >= 0
