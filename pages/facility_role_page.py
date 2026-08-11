from playwright.sync_api import Page, expect
import allure
from pages.base_page import BasePage
from config.settings import settings


class FacilityRolePage(BasePage):
    """Page object for the Facility & Role View / User View tabs on Case Detail (SCRUM-50)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.facility_role_tab = page.get_by_role("tab", name="Facility & Role View")
        self.user_view_tab = page.get_by_role("tab", name="User View")

        self.show_primary_only_toggle = page.locator("[data-testid='show-primary-only-toggle']")

        self.role_grid = page.locator("[data-testid='facility-role-grid']")
        self.role_grid_rows = self.role_grid.locator("tbody tr")
        self.role_grid_primary_cell = self.role_grid_rows.locator("[data-testid='primary-indicator']")

        self.user_view_grid = page.locator("[data-testid='user-view-grid']")
        self.user_view_grid_rows = self.user_view_grid.locator("tbody tr")

    @allure.step("Open Facility & Role View tab")
    def open_facility_role_tab(self):
        self.facility_role_tab.click()
        expect(self.facility_role_tab).to_have_attribute(
            "aria-selected", "true", timeout=settings.TIMEOUT
        )

    @allure.step("Open User View tab")
    def open_user_view_tab(self):
        self.user_view_tab.click()
        expect(self.user_view_tab).to_have_attribute(
            "aria-selected", "true", timeout=settings.TIMEOUT
        )

    @allure.step("Verify Show Primary Only toggle is visible")
    def is_toggle_visible(self) -> bool:
        return self.show_primary_only_toggle.is_visible()

    @allure.step("Verify Show Primary Only toggle is on")
    def is_toggle_on(self) -> bool:
        return self.show_primary_only_toggle.is_checked()

    @allure.step("Click Show Primary Only toggle")
    def click_toggle(self):
        self.show_primary_only_toggle.click()

    @allure.step("Get Facility & Role grid row count")
    def get_role_grid_row_count(self) -> int:
        return self.role_grid_rows.count()

    @allure.step("Get Primary indicator values for all visible rows")
    def get_primary_indicator_values(self) -> list:
        count = self.role_grid_primary_cell.count()
        return [self.role_grid_primary_cell.nth(i).inner_text() for i in range(count)]

    @allure.step("Verify Show Primary Only toggle is not present on User View tab")
    def is_toggle_absent_on_user_view(self) -> bool:
        return self.show_primary_only_toggle.count() == 0

    @allure.step("Get User View grid row count")
    def get_user_view_row_count(self) -> int:
        return self.user_view_grid_rows.count()

    @allure.step("Reload page")
    def reload_page(self):
        self.page.reload(wait_until="domcontentloaded")
