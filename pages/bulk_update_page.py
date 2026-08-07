import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from config.settings import settings


class BulkUpdatePage(BasePage):
    """Page object for the Bulk Edit Tasks screen (SCRUM-30). URL: /tasks/bulk-update"""

    MODE_FACILITY_PAYER = "Facility + Payer"
    MODE_RESIDENT_PAYER_CATEGORY = "Resident + Payer Category"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Bulk Edit Tasks")
        self.bulk_mode_toggle = page.get_by_role("button", name=re.compile(r"^Bulk mode:"))
        self.mode_menu_panel = page.locator(".mat-mdc-menu-panel")
        self.mode_option_facility_payer = self.mode_menu_panel.get_by_text(
            self.MODE_FACILITY_PAYER, exact=True
        )
        self.mode_option_resident_payer_category = self.mode_menu_panel.get_by_text(
            self.MODE_RESIDENT_PAYER_CATEGORY, exact=True
        )

        self.facility_dropdown = page.get_by_role("button", name=re.compile(r"^Facility(\s\(.*\))?$"))
        self.payer_dropdown = page.get_by_role(
            "button", name=re.compile(r"^Payer(\s\(.*\))?$")
        ).filter(has_not_text="Category")
        self.resident_dropdown = page.get_by_role("button", name=re.compile(r"^Resident(\s\(.*\))?$"))
        self.payer_category_dropdown = page.get_by_role(
            "button", name=re.compile(r"^Payer Category(\s\(.*\))?$")
        )

        self.dropdown_search_box = self.mode_menu_panel.get_by_role("textbox", name="Search")
        self.apply_filters_button = page.get_by_role("button", name="Apply Filters")
        self.clear_button = page.get_by_role("button", name="Clear", exact=True)

        self.empty_state_prompt = page.get_by_text("You don't have any tasks to edit yet")
        self.no_tasks_found_message = page.get_by_text("No tasks found")
        self.clear_filters_link = page.get_by_role("button", name="Clear filters")
        self.results_table = page.locator("arw-grid-table")

    @allure.step("Navigate to Bulk Edit Tasks screen")
    def open(self):
        self.navigate_to(f"{settings.BASE_URL}/tasks/bulk-update")
        self.wait_for_load()
        expect(self.heading).to_be_visible(timeout=settings.TIMEOUT)

    @allure.step("Get active Bulk Mode label")
    def get_active_mode_label(self) -> str:
        return self.bulk_mode_toggle.inner_text()

    @allure.step("Open Bulk Mode menu")
    def open_mode_menu(self):
        self.bulk_mode_toggle.click()

    @allure.step("Switch Bulk Mode to {mode_name}")
    def select_mode(self, mode_name: str):
        self.open_mode_menu()
        option = (
            self.mode_option_resident_payer_category
            if mode_name == self.MODE_RESIDENT_PAYER_CATEGORY
            else self.mode_option_facility_payer
        )
        option.click()

    @allure.step("Open Facility dropdown")
    def open_facility_dropdown(self):
        self.facility_dropdown.click()

    @allure.step("Select Facility {facility_name}")
    def select_facility(self, facility_name: str):
        self.open_facility_dropdown()
        self.mode_menu_panel.get_by_text(facility_name, exact=True).click()

    @allure.step("Open Payer dropdown")
    def open_payer_dropdown(self):
        self.payer_dropdown.click()

    @allure.step("Select Payer {payer_name}")
    def select_payer(self, payer_name: str):
        self.open_payer_dropdown()
        self.mode_menu_panel.get_by_text(payer_name, exact=True).click()

    @allure.step("Open Resident dropdown")
    def open_resident_dropdown(self):
        self.resident_dropdown.click()

    @allure.step("Select Resident {resident_name}")
    def select_resident(self, resident_name: str):
        self.open_resident_dropdown()
        self.mode_menu_panel.get_by_text(resident_name, exact=False).first.click()

    @allure.step("Get visible Resident option labels")
    def get_resident_option_labels(self):
        self.open_resident_dropdown()
        return self.mode_menu_panel.locator(
            ".cdk-virtual-scroll-content-wrapper > *"
        ).all_inner_texts()

    @allure.step("Open Payer Category dropdown")
    def open_payer_category_dropdown(self):
        self.payer_category_dropdown.click()

    @allure.step("Select Payer Category {category_name}")
    def select_payer_category(self, category_name: str):
        self.open_payer_category_dropdown()
        self.mode_menu_panel.get_by_text(category_name, exact=True).click()

    @allure.step("Verify Apply Filters button enabled state")
    def is_apply_filters_enabled(self) -> bool:
        return self.apply_filters_button.is_enabled()

    @allure.step("Click Apply Filters")
    def click_apply_filters(self):
        self.apply_filters_button.click()
        self.wait_for_load()

    @allure.step("Verify Clear button is visible")
    def is_clear_button_visible(self) -> bool:
        return self.clear_button.is_visible()

    @allure.step("Click Clear")
    def click_clear(self):
        self.clear_button.click()

    @allure.step("Verify empty-state prompt is visible")
    def is_empty_state_prompt_visible(self) -> bool:
        return self.empty_state_prompt.is_visible()

    @allure.step("Verify No tasks found message is visible")
    def is_no_tasks_found_visible(self) -> bool:
        return self.no_tasks_found_message.is_visible()

    @allure.step("Get task results row count")
    def get_results_row_count(self) -> int:
        return self.results_table.locator("[role='row']").count()
