from playwright.sync_api import Page
import allure
from pages.base_page import BasePage
from config.settings import settings


class CaseDetailPage(BasePage):
    """Page object for the Case Detail view, including the Payment Schedule modal (ARW-2579)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.empty_state_cta = page.get_by_role("button", name="Add Payment Schedule")
        self.populated_view_button = page.get_by_role("button", name="Add Payment Schedule")
        self.schedule_table = page.locator("[data-testid='payment-schedule-table']")
        self.schedule_table_rows = self.schedule_table.locator("tbody tr")

        self.modal = page.locator("[data-testid='add-payment-schedule-modal']")
        self.modal_title = self.modal.get_by_text("Add Payment Schedule", exact=False)
        self.modal_subtitle = self.modal.get_by_text(
            "Define the expected payment timing and method for a payer.", exact=False
        )
        self.modal_close_button = self.modal.get_by_role("button", name="Close")

        self.payer_dropdown = self.modal.locator("[data-testid='payer-select']")
        self.payer_options = self.modal.locator("[data-testid='payer-select'] [role='option']")

        self.schedule_type_dropdown = self.modal.locator("[data-testid='schedule-type-select']")
        self.day_selector = self.modal.locator("[data-testid='schedule-day-selector']")
        self.weekday_selector = self.modal.locator("[data-testid='schedule-weekday-selector']")

        self.payment_method_dropdown = self.modal.locator("[data-testid='payment-method-select']")
        self.payment_method_options = self.modal.locator(
            "[data-testid='payment-method-select'] [role='option']"
        )

        self.autopay_checkbox = self.modal.locator("[data-testid='autopay-checkbox']")
        self.autopay_helper_text = self.modal.get_by_text(
            "Indicates whether this payer is set up for auto-pay.", exact=False
        )

        self.save_button = self.modal.get_by_role("button", name="Save")
        self.success_toast = page.get_by_text("Payment schedule added successfully.")

    @allure.step("Open Add Payment Schedule modal from empty-state CTA")
    def open_modal_from_empty_state(self):
        self.empty_state_cta.click()

    @allure.step("Open Add Payment Schedule modal from populated-view button")
    def open_modal_from_button(self):
        self.populated_view_button.click()

    @allure.step("Verify Add Payment Schedule modal is visible")
    def is_modal_visible(self) -> bool:
        return self.modal.is_visible()

    @allure.step("Close Add Payment Schedule modal")
    def close_modal(self):
        self.modal_close_button.click()

    @allure.step("Get payment schedule table row count")
    def get_schedule_row_count(self) -> int:
        return self.schedule_table_rows.count()

    @allure.step("Select payer {payer_name}")
    def select_payer(self, payer_name: str):
        self.payer_dropdown.click()
        self.modal.get_by_role("option", name=payer_name).click()

    @allure.step("Open payer dropdown")
    def open_payer_dropdown(self):
        self.payer_dropdown.click()

    @allure.step("Check if payer option {payer_name} is present")
    def is_payer_option_visible(self, payer_name: str) -> bool:
        return self.modal.get_by_role("option", name=payer_name).is_visible()

    @allure.step("Check if payer option {payer_name} is disabled")
    def is_payer_option_disabled(self, payer_name: str) -> bool:
        return self.modal.get_by_role("option", name=payer_name).is_disabled()

    @allure.step("Get tooltip text for disabled payer {payer_name}")
    def get_payer_tooltip_text(self, payer_name: str) -> str:
        option = self.modal.get_by_role("option", name=payer_name)
        option.hover()
        tooltip = self.page.locator("[role='tooltip']")
        tooltip.wait_for(state="visible", timeout=settings.SHORT_TIMEOUT)
        return tooltip.inner_text()

    @allure.step("Select schedule type {schedule_type}")
    def select_schedule_type(self, schedule_type: str):
        self.schedule_type_dropdown.click()
        self.modal.get_by_role("option", name=schedule_type).click()

    @allure.step("Verify day selector is visible")
    def is_day_selector_visible(self) -> bool:
        return self.day_selector.is_visible()

    @allure.step("Verify weekday pattern selector is visible")
    def is_weekday_selector_visible(self) -> bool:
        return self.weekday_selector.is_visible()

    @allure.step("Select day {day}")
    def select_day(self, day: str):
        self.day_selector.select_option(label=day)

    @allure.step("Select weekday pattern {pattern}")
    def select_weekday_pattern(self, pattern: str):
        self.weekday_selector.select_option(label=pattern)

    @allure.step("Select payment method {method}")
    def select_payment_method(self, method: str):
        self.payment_method_dropdown.click()
        self.modal.get_by_role("option", name=method).click()

    @allure.step("Get available payment method options")
    def get_payment_method_options(self):
        return self.payment_method_options.all_inner_texts()

    @allure.step("Toggle Auto-Pay checkbox")
    def toggle_autopay(self):
        self.autopay_checkbox.click()

    @allure.step("Verify Auto-Pay checkbox checked state")
    def is_autopay_checked(self) -> bool:
        return self.autopay_checkbox.is_checked()

    @allure.step("Verify Auto-Pay helper text is visible")
    def is_autopay_helper_text_visible(self) -> bool:
        return self.autopay_helper_text.is_visible()

    @allure.step("Verify Save button enabled state")
    def is_save_button_enabled(self) -> bool:
        return self.save_button.is_enabled()

    @allure.step("Click Save")
    def click_save(self):
        self.save_button.click()

    @allure.step("Verify success toast is visible")
    def is_success_toast_visible(self) -> bool:
        return self.success_toast.is_visible()
