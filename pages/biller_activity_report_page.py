from playwright.sync_api import Page
import allure
from pages.base_page import BasePage
from config.settings import settings


class BillerActivityReportPage(BasePage):
    """Page object for the Biller Activity Report (SCRUM-41)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.grid = page.locator("[data-testid='biller-activity-report-grid']")
        self.header_row = self.grid.locator("thead tr")
        self.legacy_overdue_tasks_header = self.header_row.get_by_text("Overdue Tasks", exact=True)
        self.overdue_open_balance_header = self.header_row.get_by_text("Overdue Open Balance Tasks", exact=True)
        self.overdue_overpayment_header = self.header_row.get_by_text("Overdue Overpayment Tasks", exact=True)

        self.summary_row = self.grid.locator("[data-testid='biller-activity-report-summary-row']")

        self.export_button = page.get_by_role("button", name="Export")

    @allure.step("Navigate to Biller Activity Report")
    def open(self):
        self.navigate_to(f"{settings.BASE_URL}/reports/biller-activity")
        self.wait_for_load()

    @allure.step("Get biller row for {biller_name}")
    def get_biller_row(self, biller_name: str):
        return self.grid.locator("tbody tr").filter(has_text=biller_name)

    @allure.step("Get Overdue Open Balance Tasks cell for {biller_name}")
    def get_overdue_open_balance_cell(self, biller_name: str):
        return self.get_biller_row(biller_name).locator("[data-testid='overdue-open-balance-tasks-cell']")

    @allure.step("Get Overdue Overpayment Tasks cell for {biller_name}")
    def get_overdue_overpayment_cell(self, biller_name: str):
        return self.get_biller_row(biller_name).locator("[data-testid='overdue-overpayment-tasks-cell']")

    @allure.step("Get Overdue Open Balance Tasks total from summary row")
    def get_summary_open_balance_total(self):
        return self.summary_row.locator("[data-testid='overdue-open-balance-tasks-cell']")

    @allure.step("Get Overdue Overpayment Tasks total from summary row")
    def get_summary_overpayment_total(self):
        return self.summary_row.locator("[data-testid='overdue-overpayment-tasks-cell']")

    @allure.step("Get column header index for {header_text}")
    def get_column_index(self, header_text: str) -> int:
        headers = self.header_row.locator("th")
        count = headers.count()
        for i in range(count):
            if headers.nth(i).inner_text().strip() == header_text:
                return i
        return -1

    @allure.step("Click Export button")
    def export_report(self):
        with self.page.expect_download() as download_info:
            self.export_button.click()
        return download_info.value
