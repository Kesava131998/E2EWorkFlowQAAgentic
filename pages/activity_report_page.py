from playwright.sync_api import Page
import allure
from pages.base_page import BasePage
from config.settings import settings


class ActivityReportPage(BasePage):
    """Page object for the Biller Activity Report, including the Overdue Open Balance
    / Overdue Overpayment Tasks columns (SCRUM-27)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.grid = page.locator("[data-testid='biller-activity-report-grid']")
        self.header_row = self.grid.locator("[data-testid='grid-header-row']")
        self.header_cells = self.header_row.locator("[data-testid='grid-header-cell']")
        self.body_rows = self.grid.locator("[data-testid='grid-row']")
        self.summary_row = self.grid.locator("[data-testid='grid-summary-row']")

        self.export_button = page.get_by_role("button", name="Export")

    @allure.step("Get all column header labels")
    def get_column_headers(self) -> list:
        self.header_row.wait_for(state="visible", timeout=settings.SHORT_TIMEOUT)
        return self.header_cells.all_inner_texts()

    @allure.step("Check if column {column_name} is present")
    def is_column_present(self, column_name: str) -> bool:
        return column_name in self.get_column_headers()

    @allure.step("Get column index for {column_name}")
    def get_column_index(self, column_name: str) -> int:
        headers = self.get_column_headers()
        return headers.index(column_name)

    def _row_for_biller(self, biller_name: str):
        return self.body_rows.filter(has=self.page.get_by_text(biller_name, exact=True))

    def _cell_for_biller_column(self, biller_name: str, column_name: str):
        row = self._row_for_biller(biller_name)
        column_index = self.get_column_index(column_name)
        return row.locator("[data-testid='grid-cell']").nth(column_index)

    @allure.step("Get cell value for biller {biller_name}, column {column_name}")
    def get_cell_value(self, biller_name: str, column_name: str) -> str:
        cell = self._cell_for_biller_column(biller_name, column_name)
        cell.wait_for(state="visible", timeout=settings.SHORT_TIMEOUT)
        return cell.inner_text().strip()

    @allure.step("Click cell for biller {biller_name}, column {column_name}")
    def click_cell(self, biller_name: str, column_name: str):
        cell = self._cell_for_biller_column(biller_name, column_name)
        cell.click()
        self.page.wait_for_load_state("domcontentloaded")

    @allure.step("Get summary/total row value for column {column_name}")
    def get_summary_value(self, column_name: str) -> str:
        column_index = self.get_column_index(column_name)
        cell = self.summary_row.locator("[data-testid='grid-cell']").nth(column_index)
        cell.wait_for(state="visible", timeout=settings.SHORT_TIMEOUT)
        return cell.inner_text().strip()

    @allure.step("Get computed color for biller {biller_name}, column {column_name}")
    def get_cell_color(self, biller_name: str, column_name: str) -> str:
        cell = self._cell_for_biller_column(biller_name, column_name)
        return cell.evaluate("el => getComputedStyle(el).color")

    @allure.step("Click Export")
    def click_export(self):
        self.export_button.click()

    @allure.step("Verify Export control is enabled")
    def is_export_enabled(self) -> bool:
        return self.export_button.is_enabled()

    @allure.step("Verify Export control is visible")
    def is_export_visible(self) -> bool:
        return self.export_button.is_visible()

    @allure.step("Get applied Task List filters after drill-down navigation")
    def get_task_list_applied_filters(self) -> list:
        filters_panel = self.page.locator("[data-testid='applied-filters']")
        filters_panel.wait_for(state="visible", timeout=settings.SHORT_TIMEOUT)
        return filters_panel.locator("[data-testid='applied-filter-chip']").all_inner_texts()
