from playwright.sync_api import Page
import allure
from pages.base_page import BasePage
from config.settings import settings


class UserManagementPage(BasePage):
    """Page object for the User Management page, including the User View and
    Facility & Role View tabs (SCRUM-11)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.user_view_tab = page.get_by_role("tab", name="User View")
        self.facility_role_view_tab = page.get_by_role("tab", name="Facility & Role View")

        self.grid = page.locator("[data-testid='user-management-grid']")
        self.grid_rows = self.grid.locator("tbody tr")
        self.grid_empty_state = self.grid.locator("[data-testid='grid-empty-state']")

        self.show_primary_only_toggle = page.get_by_role(
            "switch", name="Show Primary Only"
        )
        self.primary_badge = self.grid_rows.locator("[data-testid='primary-badge']")

    @allure.step("Navigate to User Management page")
    def navigate_to_user_management(self):
        self.navigate_to(f"{settings.BASE_URL}/user-management")

    @allure.step("Click Facility & Role View tab")
    def open_facility_role_view_tab(self):
        self.facility_role_view_tab.click()

    @allure.step("Click User View tab")
    def open_user_view_tab(self):
        self.user_view_tab.click()

    @allure.step("Verify Facility & Role View tab is visible")
    def is_facility_role_view_tab_visible(self) -> bool:
        return self.facility_role_view_tab.is_visible()

    @allure.step("Verify Show Primary Only toggle is visible")
    def is_show_primary_only_toggle_visible(self) -> bool:
        return self.show_primary_only_toggle.is_visible()

    @allure.step("Get Show Primary Only toggle checked state")
    def is_show_primary_only_toggle_checked(self) -> bool:
        return self.show_primary_only_toggle.is_checked()

    @allure.step("Click Show Primary Only toggle")
    def click_show_primary_only_toggle(self):
        self.show_primary_only_toggle.click()

    @allure.step("Focus Show Primary Only toggle via keyboard")
    def focus_show_primary_only_toggle(self):
        self.show_primary_only_toggle.focus()

    @allure.step("Press keyboard key {key} on the focused element")
    def press_key(self, key: str):
        self.page.keyboard.press(key)

    @allure.step("Get Show Primary Only toggle accessible name")
    def get_show_primary_only_toggle_accessible_name(self) -> str:
        return self.show_primary_only_toggle.get_attribute("aria-label") or ""

    @allure.step("Get grid row count")
    def get_grid_row_count(self) -> int:
        return self.grid_rows.count()

    @allure.step("Verify all visible rows are marked Primary")
    def all_rows_marked_primary(self) -> bool:
        count = self.primary_badge.count()
        return count == self.grid_rows.count() and count > 0

    @allure.step("Verify at least one visible row is not marked Primary")
    def any_row_not_primary(self) -> bool:
        return self.primary_badge.count() < self.grid_rows.count()

    @allure.step("Verify grid empty state is visible")
    def is_grid_empty_state_visible(self) -> bool:
        return self.grid_empty_state.is_visible()

    @allure.step("Reload the page")
    def reload_page(self):
        self.page.reload()
        self.wait_for_load()
