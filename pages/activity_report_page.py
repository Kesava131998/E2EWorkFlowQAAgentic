from playwright.sync_api import Page, expect
import allure
from pages.base_page import BasePage
from config.settings import settings

ACTIVITY_REPORT_URL_PATH = "/reports/activity"

COLUMN_TESTIDS = {
    "overdue_open_balance": "activity-report-col-overdue-open-balance-tasks",
    "overdue_overpayment": "activity-report-col-overdue-overpayment-tasks",
}


class ActivityReportPage(BasePage):
    """Page object for the Biller Activity Report grid."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.grid = page.locator("arw-grid-table")
        self.header_row = self.grid.locator("thead tr")
        self.header_cells = self.header_row.locator("th")
        self.biller_rows = self.grid.locator("tbody tr:not([data-testid='summary-row'])")
        self.summary_row = self.grid.locator("tbody tr[data-testid='summary-row']")
        self.export_button = page.locator("[data-testid='activity-report-export-button']")

        self.column_cells = {
            key: page.locator(f"[data-testid='{testid}']")
            for key, testid in COLUMN_TESTIDS.items()
        }

    @allure.step("Navigate to Biller Activity Report")
    def navigate(self):
        self.navigate_to(f"{settings.BASE_URL}{ACTIVITY_REPORT_URL_PATH}")
        self.wait_for_load()

    @allure.step("Get header column names")
    def get_header_column_names(self) -> list[str]:
        expect(self.header_row).to_be_visible(timeout=settings.TIMEOUT)
        return self.header_cells.all_inner_texts()

    @allure.step("Verify {0} column is present in the header")
    def is_column_present(self, column_name: str) -> bool:
        return column_name in self.get_header_column_names()

    @allure.step("Get row for biller {0}")
    def get_biller_row(self, biller_name: str):
        row = self.biller_rows.filter(has_text=biller_name)
        expect(row).to_be_visible(timeout=settings.TIMEOUT)
        return row

    @allure.step("Get {1} cell value for biller {0}")
    def get_cell_value(self, biller_name: str, column_key: str) -> int:
        row = self.get_biller_row(biller_name)
        cell = row.locator(f"[data-testid='{COLUMN_TESTIDS[column_key]}']")
        expect(cell).to_be_visible(timeout=settings.TIMEOUT)
        text = cell.inner_text().strip()
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else 0

    @allure.step("Get {1} cell color for biller {0}")
    def get_cell_color(self, biller_name: str, column_key: str) -> str:
        row = self.get_biller_row(biller_name)
        cell = row.locator(f"[data-testid='{COLUMN_TESTIDS[column_key]}']")
        expect(cell).to_be_visible(timeout=settings.TIMEOUT)
        return cell.evaluate("el => getComputedStyle(el).color")

    @allure.step("Get {0} summary row total")
    def get_summary_value(self, column_key: str) -> int:
        cell = self.summary_row.locator(f"[data-testid='{COLUMN_TESTIDS[column_key]}']")
        expect(cell).to_be_visible(timeout=settings.TIMEOUT)
        text = cell.inner_text().strip()
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else 0

    @allure.step("Click {1} cell for biller {0}")
    def click_cell(self, biller_name: str, column_key: str):
        row = self.get_biller_row(biller_name)
        cell = row.locator(f"[data-testid='{COLUMN_TESTIDS[column_key]}']")
        expect(cell).to_be_visible(timeout=settings.TIMEOUT)
        cell.click()

    @allure.step("Export the Biller Activity Report")
    def export_report(self):
        expect(self.export_button).to_be_visible(timeout=settings.TIMEOUT)
        with self.page.expect_download() as download_info:
            self.export_button.click()
        return download_info.value
