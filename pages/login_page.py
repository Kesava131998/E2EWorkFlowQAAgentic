from playwright.sync_api import Page, expect
import allure
from pages.base_page import BasePage
from config.settings import settings


class LoginPage(BasePage):
    """Page object for the RevFlow login flow via Microsoft Azure AD SSO."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.sign_in_with_microsoft_button = page.get_by_role(
            "button", name="Sign in with Microsoft"
        )
        self.ms_email_input = page.locator("input[type='email']")
        self.ms_next_button = page.get_by_role("button", name="Next")
        self.ms_password_input = page.locator("input[type='password']")
        self.ms_signin_button = page.get_by_role("button", name="Sign in")
        self.ms_stay_signed_in_no_button = page.get_by_role("button", name="No")
        self.app_shell = page.locator("[data-testid='app-shell']")

    @allure.step("Log in to RevFlow via Microsoft SSO")
    def login(self):
        self.navigate_to(settings.BASE_URL)
        self.sign_in_with_microsoft_button.click()

        self.ms_email_input.fill(settings.AUTH_USERNAME)
        self.ms_next_button.click()

        self.ms_password_input.fill(settings.AUTH_PASSWORD)
        self.ms_signin_button.click()

        if self.ms_stay_signed_in_no_button.is_visible(timeout=settings.SHORT_TIMEOUT):
            self.ms_stay_signed_in_no_button.click()

        self.wait_for_load()
        expect(self.app_shell).to_be_visible(timeout=settings.PAGE_LOAD_TIMEOUT)
