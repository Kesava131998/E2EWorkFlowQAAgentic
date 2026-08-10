from playwright.sync_api import Page, expect
import allure
from pages.base_page import BasePage
from config.settings import settings

TASK_LIST_URL_PATH = "/tasks"

FILTER_TESTIDS = {
    "global_facility": "global-facility-filter",
    "resident": "task-list-resident-filter",
    "facility": "task-list-facility-filter",
    "payer": "task-list-payer-filter",
    "assigned_to": "task-list-assigned-to-filter",
}


class TaskListPage(BasePage):
    """Page object for the Task List grid (arw-grid-table) and its filters."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.grid = page.locator("arw-grid-table")
        self.grid_rows = self.grid.locator("tbody tr")

        self.filter_dropdowns = {
            key: page.locator(f"[data-testid='{testid}']")
            for key, testid in FILTER_TESTIDS.items()
        }
        self.filter_option_lists = {
            key: page.locator(f"[data-testid='{testid}'] [role='option']")
            for key, testid in FILTER_TESTIDS.items()
        }
        self.filter_selected_counts = {
            key: page.locator(f"[data-testid='{testid}'] [data-testid='selected-count']")
            for key, testid in FILTER_TESTIDS.items()
        }

    @allure.step("Navigate to Task List")
    def navigate(self):
        self.navigate_to(f"{settings.BASE_URL}{TASK_LIST_URL_PATH}")
        self.wait_for_load()

    @allure.step("Open the {0} filter dropdown")
    def open_filter(self, filter_name: str):
        dropdown = self.filter_dropdowns[filter_name]
        expect(dropdown).to_be_visible(timeout=settings.TIMEOUT)
        dropdown.click()

    @allure.step("Select {1} in the {0} filter")
    def select_value(self, filter_name: str, value: str):
        self.open_filter(filter_name)
        option = self.filter_option_lists[filter_name].filter(has_text=value)
        expect(option).to_be_visible(timeout=settings.TIMEOUT)
        option.click()

    @allure.step("Deselect {1} in the {0} filter")
    def deselect_value(self, filter_name: str, value: str):
        self.open_filter(filter_name)
        option = self.filter_option_lists[filter_name].filter(has_text=value)
        expect(option).to_be_visible(timeout=settings.TIMEOUT)
        option.click()

    @allure.step("Get selected values in the {0} filter")
    def get_selected_values(self, filter_name: str) -> list[str]:
        options = self.filter_option_lists[filter_name]
        selected = options.filter(has=self.page.locator("[aria-selected='true']"))
        return selected.all_inner_texts()

    @allure.step("Get selected count for the {0} filter")
    def get_selected_count(self, filter_name: str) -> int:
        count_locator = self.filter_selected_counts[filter_name]
        expect(count_locator).to_be_visible(timeout=settings.TIMEOUT)
        text = count_locator.inner_text().strip()
        digits = "".join(ch for ch in text if ch.isdigit())
        return int(digits) if digits else 0

    @allure.step("Verify {1} is present in the {0} filter options")
    def is_value_present_in_options(self, filter_name: str, value: str) -> bool:
        self.open_filter(filter_name)
        option = self.filter_option_lists[filter_name].filter(has_text=value)
        return option.count() > 0

    @allure.step("Verify the {0} filter is fully cleared")
    def is_filter_cleared(self, filter_name: str) -> bool:
        return self.get_selected_count(filter_name) == 0

    @allure.step("Get Task List row count")
    def get_task_list_row_count(self) -> int:
        return self.grid_rows.count()
