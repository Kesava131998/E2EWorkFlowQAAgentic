from playwright.sync_api import Page
import allure
from pages.base_page import BasePage
from config.settings import settings


class UserManagementPage(BasePage):
    """Page object for the User Management page, including the Facility & Role View tab (SCRUM-11)."""

    URL_PATH = "/user-management"

    def __init__(self, page: Page):
        super().__init__(page)
        self.user_view_tab = page.get_by_role("tab", name="User View")
        self.facility_role_tab = page.get_by_role("tab", name="Facility & Role")

        self.show_primary_only_toggle = page.locator("[data-testid='show-primary-only-toggle']")

        self.role_grid = page.locator("[data-testid='facility-role-grid']")
        self.role_grid_rows = self.role_grid.locator("tbody tr")
        self.role_grid_primary_flags = self.role_grid.locator("tbody tr [data-testid='primary-flag']")

        self.empty_state = self.role_grid.get_by_text("No role assignments found", exact=False)

    @allure.step("Navigate to User Management page")
    def navigate_to_user_management(self):
        self.navigate_to(f"{settings.BASE_URL}{self.URL_PATH}")
        self.wait_for_load()

    @allure.step("Click Facility & Role tab")
    def click_facility_role_tab(self):
        self.facility_role_tab.click()

    @allure.step("Click User View tab")
    def click_user_view_tab(self):
        self.user_view_tab.click()

    @allure.step("Verify Show Primary Only toggle is visible")
    def is_show_primary_only_toggle_visible(self) -> bool:
        return self.show_primary_only_toggle.is_visible()

    @allure.step("Get Show Primary Only toggle state")
    def get_show_primary_only_toggle_state(self) -> bool:
        return self.show_primary_only_toggle.is_checked()

    @allure.step("Toggle Show Primary Only")
    def toggle_show_primary_only(self):
        self.show_primary_only_toggle.click()

    @allure.step("Get role grid row count")
    def get_role_grid_row_count(self) -> int:
        return self.role_grid_rows.count()

    @allure.step("Get role grid Primary flags for all rows")
    def get_role_grid_rows_primary_flags(self):
        return self.role_grid_primary_flags.all_inner_texts()

    @allure.step("Verify role grid empty state is visible")
    def is_empty_state_visible(self) -> bool:
        return self.empty_state.is_visible()

    @allure.step("Reload page")
    def reload_page(self):
        self.page.reload()
        self.wait_for_load()
