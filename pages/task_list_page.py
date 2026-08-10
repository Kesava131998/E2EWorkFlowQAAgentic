from playwright.sync_api import Page
import allure
from pages.base_page import BasePage
from config.settings import settings


class TaskListPage(BasePage):
    """Page object for the Task List grid and its filter bar (SCRUM-44)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.grid = page.locator("[data-testid='arw-grid-table']")
        self.task_rows = self.grid.locator("tbody tr")
        self.empty_state = page.locator("[data-testid='task-list-empty-state']")

        self.filter_bar = page.locator("[data-testid='task-list-filter-bar']")
        self.bulk_mode_control = self.filter_bar.locator("[data-testid='bulk-mode-select']")
        self.bulk_mode_options = self.filter_bar.locator("[data-testid='bulk-mode-select'] [role='option']")

        self.facility_dropdown = self.filter_bar.locator("[data-testid='facility-select']")
        self.payer_dropdown = self.filter_bar.locator("[data-testid='payer-select']")
        self.resident_dropdown = self.filter_bar.locator("[data-testid='resident-select']")
        self.payer_category_dropdown = self.filter_bar.locator("[data-testid='payer-category-select']")
        self.resident_options = self.filter_bar.locator("[data-testid='resident-select'] [role='option']")

        self.apply_filters_button = self.filter_bar.get_by_role("button", name="Apply Filters")
        self.clear_button = self.filter_bar.get_by_role("button", name="Clear")

    @allure.step("Open Task List page")
    def open(self):
        self.navigate_to(f"{settings.BASE_URL}/tasks")
        self.wait_for_load()

    @allure.step("Get current Bulk Mode selection")
    def get_bulk_mode_value(self) -> str:
        return self.bulk_mode_control.inner_text().strip()

    @allure.step("Open Bulk Mode dropdown")
    def open_bulk_mode_dropdown(self):
        self.bulk_mode_control.click()

    @allure.step("Select Bulk Mode {mode_label}")
    def select_bulk_mode(self, mode_label: str):
        self.bulk_mode_control.click()
        self.filter_bar.get_by_role("option", name=mode_label).click()

    @allure.step("Check if Bulk Mode option {mode_label} is visible")
    def is_bulk_mode_option_visible(self, mode_label: str) -> bool:
        return self.filter_bar.get_by_role("option", name=mode_label).is_visible()

    @allure.step("Get first filter dropdown label text")
    def get_first_dropdown_label(self) -> str:
        return self.filter_bar.locator("[data-testid='first-filter-label']").inner_text().strip()

    @allure.step("Get second filter dropdown label text")
    def get_second_dropdown_label(self) -> str:
        return self.filter_bar.locator("[data-testid='second-filter-label']").inner_text().strip()

    @allure.step("Select Facility {facility_name}")
    def select_facility(self, facility_name: str):
        self.facility_dropdown.click()
        self.filter_bar.get_by_role("option", name=facility_name).click()

    @allure.step("Select Payer {payer_name}")
    def select_payer(self, payer_name: str):
        self.payer_dropdown.click()
        self.filter_bar.get_by_role("option", name=payer_name).click()

    @allure.step("Select Resident {resident_label}")
    def select_resident(self, resident_label: str):
        self.resident_dropdown.click()
        self.filter_bar.get_by_role("option", name=resident_label).click()

    @allure.step("Select Payer Category {category_name}")
    def select_payer_category(self, category_name: str):
        self.payer_category_dropdown.click()
        self.filter_bar.get_by_role("option", name=category_name).click()

    @allure.step("Open Resident dropdown")
    def open_resident_dropdown(self):
        self.resident_dropdown.click()

    @allure.step("Get all Resident dropdown option texts")
    def get_resident_option_texts(self):
        return self.resident_options.all_inner_texts()

    @allure.step("Clear Payer selection")
    def clear_payer_selection(self):
        self.payer_dropdown.locator("[data-testid='clear-selection']").click()

    @allure.step("Check if Apply Filters button is enabled")
    def is_apply_filters_enabled(self) -> bool:
        return self.apply_filters_button.is_enabled()

    @allure.step("Click Apply Filters")
    def click_apply_filters(self):
        self.apply_filters_button.click()

    @allure.step("Click Clear")
    def click_clear(self):
        self.clear_button.click()

    @allure.step("Get task table row count")
    def get_task_row_count(self) -> int:
        return self.task_rows.count()

    @allure.step("Check if task list empty state is visible")
    def is_empty_state_visible(self) -> bool:
        return self.empty_state.is_visible()

    @allure.step("Get facility value for task row {row_index}")
    def get_row_facility(self, row_index: int) -> str:
        return self.task_rows.nth(row_index).locator("[data-testid='task-facility-cell']").inner_text().strip()

    @allure.step("Get payer value for task row {row_index}")
    def get_row_payer(self, row_index: int) -> str:
        return self.task_rows.nth(row_index).locator("[data-testid='task-payer-cell']").inner_text().strip()

    @allure.step("Get resident value for task row {row_index}")
    def get_row_resident(self, row_index: int) -> str:
        return self.task_rows.nth(row_index).locator("[data-testid='task-resident-cell']").inner_text().strip()

    @allure.step("Get payer category value for task row {row_index}")
    def get_row_payer_category(self, row_index: int) -> str:
        return self.task_rows.nth(row_index).locator("[data-testid='task-payer-category-cell']").inner_text().strip()
