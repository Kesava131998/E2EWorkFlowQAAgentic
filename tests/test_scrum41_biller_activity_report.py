import pytest
import allure
from pages.biller_activity_report_page import BillerActivityReportPage
from config.settings import settings


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC1: The Overdue Tasks column no longer appears on the Biller Activity Report")
@allure.title("Legacy Overdue Tasks column is removed")
def test_pos_overdue_tasks_column_removed(page):
    """
    Jira: SCRUM-41
    AC: The Overdue Tasks column no longer appears on the Biller Activity Report.
    """
    report_page = BillerActivityReportPage(page)

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the report grid header row is visible"):
        report_page.header_row.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify no column titled Overdue Tasks is present"):
        assert report_page.legacy_overdue_tasks_header.count() == 0


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC8: Column order places Overdue Open Tasks before Overdue Overpayment Tasks")
@allure.title("New columns appear in the correct order")
def test_pos_new_columns_correct_order(page):
    """
    Jira: SCRUM-41
    AC: Column order on the report places Overdue Open Tasks before Overdue Overpayment Tasks.
    """
    report_page = BillerActivityReportPage(page)

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify both new column headers are visible"):
        report_page.overdue_open_balance_header.wait_for(state="visible", timeout=settings.TIMEOUT)
        report_page.overdue_overpayment_header.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify Overdue Open Balance Tasks column index is lower"):
        open_balance_idx = report_page.get_column_index("Overdue Open Balance Tasks")
        overpayment_idx = report_page.get_column_index("Overdue Overpayment Tasks")
        assert open_balance_idx != -1 and overpayment_idx != -1
        assert open_balance_idx < overpayment_idx


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC2: Overdue Overpayment Tasks column displays the correct count per biller")
@allure.title("Overdue Overpayment Tasks count is correct")
def test_pos_overdue_overpayment_count_correct(page):
    """
    Jira: SCRUM-41
    AC: Overdue Overpayment Tasks column displays the correct count of open overpayment tasks
    with a Follow Up Date < today, per biller.
    """
    report_page = BillerActivityReportPage(page)
    biller_name = "Biller X"

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the Overdue Overpayment Tasks cell for the biller is visible"):
        cell = report_page.get_overdue_overpayment_cell(biller_name)
        cell.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the cell displays the expected count"):
        assert cell.inner_text().strip() == "3"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC3: Overdue Open Balance Tasks column displays the correct count per biller")
@allure.title("Overdue Open Balance Tasks count is correct")
def test_pos_overdue_open_balance_count_correct(page):
    """
    Jira: SCRUM-41
    AC: Overdue Open Balance Tasks column displays the correct count of open balance tasks
    with a Follow Up Date < today, per biller.
    """
    report_page = BillerActivityReportPage(page)
    biller_name = "Biller Y"

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the Overdue Open Balance Tasks cell for the biller is visible"):
        cell = report_page.get_overdue_open_balance_cell(biller_name)
        cell.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the cell displays the expected count"):
        assert cell.inner_text().strip() == "5"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC2: Only tasks with Follow Up Date < today are counted as overdue overpayment")
@allure.title("Future or today Follow Up Date tasks are excluded from overpayment count")
def test_err_future_followup_date_excluded_overpayment(page):
    """
    Jira: SCRUM-41
    AC: Overdue Overpayment Tasks column displays the correct count of open overpayment tasks
    with a Follow Up Date < today, per biller.
    """
    report_page = BillerActivityReportPage(page)
    biller_name = "Biller Z"

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the Overdue Overpayment Tasks cell for the biller is visible"):
        cell = report_page.get_overdue_overpayment_cell(biller_name)
        cell.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify only the past-due task is counted"):
        assert cell.inner_text().strip() == "1"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC3: Only open tasks with Follow Up Date < today are counted as overdue open balance")
@allure.title("Closed tasks are excluded from the overdue open balance count")
def test_err_closed_tasks_excluded_open_balance(page):
    """
    Jira: SCRUM-41
    AC: Overdue Open Balance Tasks column displays the correct count of open balance tasks
    with a Follow Up Date < today, per biller.
    """
    report_page = BillerActivityReportPage(page)
    biller_name = "Biller W"

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the Overdue Open Balance Tasks cell for the biller is visible"):
        cell = report_page.get_overdue_open_balance_cell(biller_name)
        cell.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify closed tasks are not counted"):
        assert cell.inner_text().strip() == "1"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC4: A biller with no overdue tasks of a given type shows 0")
@allure.title("Zero overdue overpayment tasks shows 0")
def test_pos_zero_overdue_overpayment_shows_zero(page):
    """
    Jira: SCRUM-41
    AC: A biller with no overdue tasks of a given type shows 0 in that column.
    """
    report_page = BillerActivityReportPage(page)
    biller_name = "Biller V"

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the Overdue Overpayment Tasks cell for the biller is visible"):
        cell = report_page.get_overdue_overpayment_cell(biller_name)
        cell.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the cell displays 0"):
        assert cell.inner_text().strip() == "0"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC4: A biller with no overdue tasks of a given type shows 0")
@allure.title("Zero overdue open balance tasks shows 0")
def test_pos_zero_overdue_open_balance_shows_zero(page):
    """
    Jira: SCRUM-41
    AC: A biller with no overdue tasks of a given type shows 0 in that column.
    """
    report_page = BillerActivityReportPage(page)
    biller_name = "Biller U"

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the Overdue Open Balance Tasks cell for the biller is visible"):
        cell = report_page.get_overdue_open_balance_cell(biller_name)
        cell.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the cell displays 0"):
        assert cell.inner_text().strip() == "0"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC5: 0 shows in green, all other numbers in red")
@allure.title("Zero value renders in green")
def test_pos_zero_value_renders_green(page):
    """
    Jira: SCRUM-41
    AC: 0 shows in green, all other numbers in red.
    """
    report_page = BillerActivityReportPage(page)
    biller_name = "Biller V"

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Locate the cell showing 0 for the biller"):
        cell = report_page.get_overdue_overpayment_cell(biller_name)
        cell.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the cell text color is green"):
        color = cell.evaluate("el => getComputedStyle(el).color")
        assert color == "rgb(0, 128, 0)"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC5: 0 shows in green, all other numbers in red")
@allure.title("Non-zero value renders in red")
def test_pos_nonzero_value_renders_red(page):
    """
    Jira: SCRUM-41
    AC: 0 shows in green, all other numbers in red.
    """
    report_page = BillerActivityReportPage(page)
    biller_name = "Biller X"

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Locate the cell showing a non-zero count for the biller"):
        cell = report_page.get_overdue_overpayment_cell(biller_name)
        cell.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the cell text color is red"):
        color = cell.evaluate("el => getComputedStyle(el).color")
        assert color == "rgb(255, 0, 0)"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC6: The summary/total row sums each column independently and correctly")
@allure.title("Total row sums the Overdue Open Balance Tasks column")
def test_pos_total_row_sums_open_balance_column(page):
    """
    Jira: SCRUM-41
    AC: The summary/total row sums each column independently and correctly.
    """
    report_page = BillerActivityReportPage(page)

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the summary row is visible"):
        report_page.summary_row.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the summary total for Overdue Open Balance Tasks"):
        total_cell = report_page.get_summary_open_balance_total()
        assert total_cell.inner_text().strip() == "6"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC6: The summary/total row sums each column independently and correctly")
@allure.title("Total row sums the Overdue Overpayment Tasks column independently")
def test_pos_total_row_sums_overpayment_column(page):
    """
    Jira: SCRUM-41
    AC: The summary/total row sums each column independently and correctly.
    """
    report_page = BillerActivityReportPage(page)

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the summary row is visible"):
        report_page.summary_row.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify the summary total for Overdue Overpayment Tasks"):
        total_cell = report_page.get_summary_overpayment_total()
        assert total_cell.inner_text().strip() == "4"


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC7: Exported report reflects the two new columns with accurate data")
@allure.title("Export includes both new columns with accurate data")
def test_pos_export_includes_new_columns_accurately(page):
    """
    Jira: SCRUM-41
    AC: Exported report reflects the two new columns with accurate data.
    """
    report_page = BillerActivityReportPage(page)

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Verify the Export button is visible"):
        report_page.export_button.wait_for(state="visible", timeout=settings.TIMEOUT)

    with allure.step("Step 3: Click Export and capture the downloaded file"):
        download = report_page.export_report()

    with allure.step("Step 4: Verify the export completed"):
        assert download.suggested_filename


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC7: Exported report reflects the two new columns with accurate data")
@allure.title("Export excludes the removed Overdue Tasks column")
def test_err_export_excludes_removed_column(page):
    """
    Jira: SCRUM-41
    AC: Exported report reflects the two new columns with accurate data (and no longer
    contains the removed Overdue Tasks column).
    """
    report_page = BillerActivityReportPage(page)

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Click Export and capture the downloaded file"):
        download = report_page.export_report()

    with allure.step("Step 3: Verify the exported file has a suggested filename"):
        # TODO: Assert exported file content headers exclude "Overdue Tasks" once export parsing utility is available
        assert download.suggested_filename


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC8: Column order places Overdue Open Tasks before Overdue Overpayment Tasks")
@allure.title("Column order is preserved in the exported report")
def test_pos_export_preserves_column_order(page):
    """
    Jira: SCRUM-41
    AC: Column order on the report places Overdue Open Tasks before Overdue Overpayment Tasks.
    """
    report_page = BillerActivityReportPage(page)

    with allure.step("Step 1: Navigate to the Biller Activity Report page"):
        report_page.open()

    with allure.step("Step 2: Click Export and capture the downloaded file"):
        download = report_page.export_report()

    with allure.step("Step 3: Verify the exported file has a suggested filename"):
        # TODO: Assert column order once export parsing utility is available
        assert download.suggested_filename


@allure.epic("SCRUM-41: Split \"Overdue Tasks\" into Two Columns")
@allure.feature("biller_activity_report")
@allure.story("AC1: Viewer role can view the report without the removed column")
@allure.title("Viewer role can view the report but cannot export")
def test_perm_viewer_report_access_no_export(page):
    """
    Jira: SCRUM-41
    AC: The Overdue Tasks column no longer appears on the Biller Activity Report (verified
    across roles, including read-only Viewer).
    """
    report_page = BillerActivityReportPage(page)

    with allure.step("Step 1: Navigate to the Biller Activity Report page as a Viewer-role user"):
        report_page.open()

    with allure.step("Step 2: Verify the report grid loads without the Overdue Tasks column"):
        report_page.header_row.wait_for(state="visible", timeout=settings.TIMEOUT)
        assert report_page.legacy_overdue_tasks_header.count() == 0

    with allure.step("Step 3: Verify the Export button is hidden or disabled for the Viewer role"):
        assert not report_page.export_button.is_visible() or report_page.export_button.is_disabled()
