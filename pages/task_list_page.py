from playwright.sync_api import Page
import allure
from pages.base_page import BasePage
from config.settings import settings


class TaskListPage(BasePage):
    """Page object for the Task List grid (/tasks), including the global facility filter
    and the per-column Resident/Facility/Payer/Assigned To filters (SCRUM-47)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{settings.BASE_URL}/tasks"

        self.grid = page.locator("arw-grid-table")
        self.grid_rows = self.grid.locator("[role='row']")
        self.grid_loading_indicator = self.grid.locator("[data-testid='grid-loading-indicator']")
        self.grid_error_state = self.grid.locator("[data-testid='grid-error-state']")
        self.search_input = page.locator("[data-testid='task-list-search-input']")

        self.global_facility_filter = page.locator("[data-testid='global-facility-filter']")
        self.global_facility_filter_options = page.locator(
            "[data-testid='global-facility-filter'] [role='option']"
        )
        self.global_facility_filter_apply_button = page.locator(
            "[data-testid='global-facility-filter-apply']"
        )

        self.resident_filter = page.locator("[data-testid='task-list-resident-filter']")
        self.resident_filter_options = page.locator(
            "[data-testid='task-list-resident-filter'] [role='option']"
        )
        self.resident_filter_selected = page.locator(
            "[data-testid='task-list-resident-filter'] [data-testid='selected-chip']"
        )

        self.facility_filter = page.locator("[data-testid='task-list-facility-filter']")
        self.facility_filter_options = page.locator(
            "[data-testid='task-list-facility-filter'] [role='option']"
        )
        self.facility_filter_selected = page.locator(
            "[data-testid='task-list-facility-filter'] [data-testid='selected-chip']"
        )

        self.payer_filter = page.locator("[data-testid='task-list-payer-filter']")
        self.payer_filter_options = page.locator(
            "[data-testid='task-list-payer-filter'] [role='option']"
        )
        self.payer_filter_selected = page.locator(
            "[data-testid='task-list-payer-filter'] [data-testid='selected-chip']"
        )

        self.assigned_to_filter = page.locator("[data-testid='task-list-assigned-to-filter']")
        self.assigned_to_filter_options = page.locator(
            "[data-testid='task-list-assigned-to-filter'] [role='option']"
        )
        self.assigned_to_filter_selected = page.locator(
            "[data-testid='task-list-assigned-to-filter'] [data-testid='selected-chip']"
        )

    @allure.step("Open global facility filter dropdown")
    def open_global_facility_filter(self):
        self.global_facility_filter.click()

    @allure.step("Select global facility option: {facility_name}")
    def select_global_facility(self, facility_name: str):
        self.global_facility_filter_options.get_by_text(facility_name, exact=True).click()

    @allure.step("Deselect global facility option: {facility_name}")
    def deselect_global_facility(self, facility_name: str):
        self.global_facility_filter_options.get_by_text(facility_name, exact=True).click()

    @allure.step("Apply global facility filter")
    def apply_global_facility_filter(self):
        self.global_facility_filter_apply_button.click()
        self.wait_for_load()

    @allure.step("Get selected global facility names")
    def get_selected_global_facilities(self) -> list:
        return self.global_facility_filter.locator("[data-testid='selected-chip']").all_inner_texts()

    def _filter_locator(self, filter_name: str):
        return {
            "resident": self.resident_filter,
            "facility": self.facility_filter,
            "payer": self.payer_filter,
            "assigned_to": self.assigned_to_filter,
        }[filter_name]

    def _filter_options_locator(self, filter_name: str):
        return {
            "resident": self.resident_filter_options,
            "facility": self.facility_filter_options,
            "payer": self.payer_filter_options,
            "assigned_to": self.assigned_to_filter_options,
        }[filter_name]

    def _filter_selected_locator(self, filter_name: str):
        return {
            "resident": self.resident_filter_selected,
            "facility": self.facility_filter_selected,
            "payer": self.payer_filter_selected,
            "assigned_to": self.assigned_to_filter_selected,
        }[filter_name]

    @allure.step("Open {filter_name} filter dropdown")
    def open_filter(self, filter_name: str):
        self._filter_locator(filter_name).click()

    @allure.step("Get {filter_name} filter option texts")
    def get_filter_option_texts(self, filter_name: str) -> list:
        return self._filter_options_locator(filter_name).all_inner_texts()

    @allure.step("Get {filter_name} filter selected values")
    def get_filter_selected_texts(self, filter_name: str) -> list:
        return self._filter_selected_locator(filter_name).all_inner_texts()

    @allure.step("Verify {filter_name} filter is cleared")
    def is_filter_cleared(self, filter_name: str) -> bool:
        return self._filter_selected_locator(filter_name).count() == 0

    @allure.step("Enter search text: {text}")
    def search(self, text: str):
        self.search_input.fill(text)
        self.search_input.press("Enter")

    @allure.step("Verify Task List grid is visible")
    def is_grid_visible(self) -> bool:
        return self.grid.is_visible()

    @allure.step("Verify Task List grid shows loading indicator")
    def is_loading(self) -> bool:
        return self.grid_loading_indicator.is_visible()

    @allure.step("Verify Task List grid shows error state")
    def is_error_state_visible(self) -> bool:
        return self.grid_error_state.is_visible()

    @allure.step("Get Task List grid row count")
    def get_grid_row_count(self) -> int:
        return self.grid_rows.count()
