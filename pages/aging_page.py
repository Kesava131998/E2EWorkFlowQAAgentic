from playwright.sync_api import Page, expect
import allure
from pages.base_page import BasePage
from config.settings import settings


class AgingPage(BasePage):
    """Page object for the Aging grid and its balance-cell tooltip (SCRUM-53)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.show_all_comments_toggle = page.locator("[data-testid='aging-show-all-comments-toggle']")
        self.save_view_button = page.locator("[data-testid='aging-save-view-button']")

        self.aging_grid = page.locator("[data-testid='aging-grid']")
        self.balance_cells = self.aging_grid.locator("[data-testid='aging-balance-cell']")

        self.tooltip = page.locator("[data-testid='aging-balance-tooltip']")
        self.tooltip_followup_date = self.tooltip.locator("[data-testid='aging-tooltip-followup-date']")
        self.tooltip_comments_section = self.tooltip.locator("[data-testid='aging-tooltip-comments-section']")
        self.tooltip_comment_rows = self.tooltip_comments_section.locator("[data-testid='aging-tooltip-comment-row']")
        self.tooltip_see_task_button = self.tooltip.get_by_role("button", name="See Task")

        self.case_view_aging_section = page.locator("[data-testid='case-view-aging-section']")
        self.case_view_show_all_comments_toggle = self.case_view_aging_section.locator(
            "[data-testid='aging-show-all-comments-toggle']"
        )

    @allure.step("Navigate to the Aging page")
    def open(self):
        self.navigate_to(f"{settings.BASE_URL}/aging")
        self.wait_for_load()

    @allure.step("Verify 'Show all comments in tooltip' toggle is visible")
    def is_show_all_comments_toggle_visible(self) -> bool:
        return self.show_all_comments_toggle.is_visible()

    @allure.step("Verify 'Show all comments in tooltip' toggle checked state")
    def is_show_all_comments_toggle_on(self) -> bool:
        return self.show_all_comments_toggle.is_checked()

    @allure.step("Toggle 'Show all comments in tooltip'")
    def toggle_show_all_comments(self):
        self.show_all_comments_toggle.click()

    @allure.step("Save current view as {view_name}")
    def save_view(self, view_name: str):
        self.save_view_button.click()
        self.page.get_by_placeholder("View name").fill(view_name)
        self.page.get_by_role("button", name="Save").click()

    @allure.step("Load saved view {view_name}")
    def load_saved_view(self, view_name: str):
        self.page.get_by_role("option", name=view_name).click()

    @allure.step("Open Aging tooltip for balance cell at index {index}")
    def open_tooltip_for_cell(self, index: int = 0):
        self.balance_cells.nth(index).click()
        expect(self.tooltip).to_be_visible(timeout=settings.SHORT_TIMEOUT)

    @allure.step("Close Aging tooltip")
    def close_tooltip(self):
        self.page.keyboard.press("Escape")

    @allure.step("Verify Aging tooltip is visible")
    def is_tooltip_visible(self) -> bool:
        return self.tooltip.is_visible()

    @allure.step("Get Follow Up Date text from tooltip")
    def get_followup_date_text(self) -> str:
        return self.tooltip_followup_date.inner_text()

    @allure.step("Verify Comments section is visible")
    def is_comments_section_visible(self) -> bool:
        return self.tooltip_comments_section.is_visible()

    @allure.step("Get comment count in tooltip")
    def get_comment_count(self) -> int:
        return self.tooltip_comment_rows.count()

    @allure.step("Get all comment texts in tooltip")
    def get_comment_texts(self):
        return self.tooltip_comment_rows.all_inner_texts()

    @allure.step("Get comment author at row {index}")
    def get_comment_author(self, index: int) -> str:
        return self.tooltip_comment_rows.nth(index).locator("[data-testid='comment-author']").inner_text()

    @allure.step("Get comment timestamp at row {index}")
    def get_comment_timestamp(self, index: int) -> str:
        return self.tooltip_comment_rows.nth(index).locator("[data-testid='comment-timestamp']").inner_text()

    @allure.step("Verify See Task button is visible")
    def is_see_task_button_visible(self) -> bool:
        return self.tooltip_see_task_button.is_visible()

    @allure.step("Click See Task button")
    def click_see_task(self):
        self.tooltip_see_task_button.click()

    @allure.step("Navigate to a case's Case View")
    def open_case_view(self, case_id: str):
        self.navigate_to(f"{settings.BASE_URL}/cases/{case_id}")
        self.wait_for_load()

    @allure.step("Verify 'Show all comments in tooltip' toggle is visible within Case View")
    def is_case_view_toggle_visible(self) -> bool:
        return self.case_view_show_all_comments_toggle.is_visible()

    @allure.step("Toggle 'Show all comments in tooltip' within Case View")
    def toggle_case_view_show_all_comments(self):
        self.case_view_show_all_comments_toggle.click()
