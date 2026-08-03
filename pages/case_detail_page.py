from playwright.sync_api import Page, Locator, expect
import allure

from pages.base_page import BasePage
from config.settings import settings


class CaseDetailPage(BasePage):
    """Page object for the RevFlow Case Detail view — Payment Schedule section (ARW-2579).

    Feature not yet shipped — locators are best-guess placeholders based on the
    Figma spec, verify once the "Add Payment Schedule" modal exists in the DOM.
    """

    def __init__(self, page: Page):
        super().__init__(page)

        # Payment Schedule table / entry points
        self.payment_schedule_table: Locator = page.locator(".payment-schedule-table")
        self.payment_schedule_rows: Locator = page.locator(".payment-schedule-table__row")
        self.empty_state_add_button: Locator = page.locator(
            ".payment-schedule-empty-state"
        ).get_by_role("button", name="Add Payment Schedule")
        self.populated_view_add_button: Locator = page.locator(
            ".payment-schedule-table button", has_text="Add Payment Schedule"
        )

        # Modal
        self.modal: Locator = page.locator("[role='dialog'].payment-schedule-modal")
        self.modal_title: Locator = self.modal.locator(".modal-title")
        self.modal_subtitle: Locator = self.modal.locator(".modal-subtitle")

        # Payer field
        self.payer_dropdown: Locator = self.modal.locator("[name='payer']")
        self.payer_option_tooltip: Locator = page.locator(".payer-option-tooltip")

        # Schedule Type / Details
        self.schedule_type_dropdown: Locator = self.modal.locator("[name='scheduleType']")
        self.day_selector: Locator = self.modal.locator("[name='scheduleDay']")
        self.weekday_pattern_selector: Locator = self.modal.locator("[name='scheduleWeekdayPattern']")

        # Payment Method
        self.payment_method_dropdown: Locator = self.modal.locator("[name='paymentMethod']")

        # Auto-Pay
        self.auto_pay_checkbox: Locator = self.modal.locator("[name='autoPayStatus']")
        self.auto_pay_helper_text: Locator = self.modal.locator(".auto-pay-helper-text")

        # Save / Toast
        self.save_button: Locator = self.modal.get_by_role("button", name="Save")
        self.success_toast: Locator = page.locator(".toast-success")

    @allure.step("Click empty-state Add Payment Schedule CTA")
    def click_empty_state_add_button(self):
        self.empty_state_add_button.wait_for(state="visible", timeout=settings.TIMEOUT)
        self.empty_state_add_button.click()

    @allure.step("Click Add Payment Schedule button (populated view)")
    def click_populated_view_add_button(self):
        self.populated_view_add_button.wait_for(state="visible", timeout=settings.TIMEOUT)
        self.populated_view_add_button.click()

    @allure.step("Verify Add Payment Schedule modal is open")
    def verify_modal_open(self):
        expect(self.modal).to_be_visible(timeout=settings.TIMEOUT)

    @allure.step("Get payer dropdown option: {payer_name}")
    def get_payer_option(self, payer_name: str) -> Locator:
        return self.payer_dropdown.get_by_role("option", name=payer_name)

    @allure.step("Select payer: {payer_name}")
    def select_payer(self, payer_name: str):
        self.payer_dropdown.click()
        self.get_payer_option(payer_name).click()

    @allure.step("Is payer option disabled: {payer_name}")
    def is_payer_option_disabled(self, payer_name: str) -> bool:
        return self.get_payer_option(payer_name).is_disabled()

    @allure.step("Hover payer option: {payer_name}")
    def hover_payer_option(self, payer_name: str):
        option = self.get_payer_option(payer_name)
        option.hover()
        self.payer_option_tooltip.wait_for(state="visible", timeout=settings.TIMEOUT)

    @allure.step("Get payer option tooltip text")
    def get_payer_option_tooltip_text(self) -> str:
        return self.payer_option_tooltip.inner_text()

    @allure.step("Select schedule type: {schedule_type}")
    def select_schedule_type(self, schedule_type: str):
        self.schedule_type_dropdown.click()
        self.schedule_type_dropdown.get_by_role("option", name=schedule_type).click()

    @allure.step("Verify day selector is visible")
    def is_day_selector_visible(self) -> bool:
        return self.day_selector.is_visible()

    @allure.step("Verify weekday pattern selector is visible")
    def is_weekday_pattern_selector_visible(self) -> bool:
        return self.weekday_pattern_selector.is_visible()

    @allure.step("Select specific day: {day}")
    def select_specific_day(self, day: str):
        self.day_selector.click()
        self.day_selector.get_by_role("option", name=day).click()

    @allure.step("Select weekday pattern: {pattern}")
    def select_weekday_pattern(self, pattern: str):
        self.weekday_pattern_selector.click()
        self.weekday_pattern_selector.get_by_role("option", name=pattern).click()

    @allure.step("Select payment method: {method}")
    def select_payment_method(self, method: str):
        self.payment_method_dropdown.click()
        self.payment_method_dropdown.get_by_role("option", name=method).click()

    @allure.step("Toggle Auto-Pay Status checkbox")
    def toggle_auto_pay_status(self):
        self.auto_pay_checkbox.click()

    @allure.step("Get Auto-Pay helper text")
    def get_auto_pay_helper_text(self) -> str:
        return self.auto_pay_helper_text.inner_text()

    @allure.step("Is Save button enabled")
    def is_save_enabled(self) -> bool:
        return self.save_button.is_enabled()

    @allure.step("Click Save")
    def click_save(self):
        self.save_button.click()

    @allure.step("Get success toast text")
    def get_success_toast_text(self) -> str:
        self.success_toast.wait_for(state="visible", timeout=settings.TIMEOUT)
        return self.success_toast.inner_text()

    @allure.step("Get payment schedule row for payer: {payer_name}")
    def get_schedule_row(self, payer_name: str) -> Locator:
        return self.payment_schedule_rows.filter(has_text=payer_name).first
