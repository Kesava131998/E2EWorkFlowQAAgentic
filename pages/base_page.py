from playwright.sync_api import Page
import allure

class BasePage:
    """Base page object with common functionality."""

    def __init__(self, page: Page):
        self.page = page

    @allure.step("Navigate to {url}")
    def navigate_to(self, url: str):
        """Navigate to a URL."""
        self.page.goto(url)

    @allure.step("Wait for page load")
    def wait_for_load(self):
        """Wait for page to load completely."""
        self.page.wait_for_load_state("networkidle")

    @allure.step("Take screenshot")
    def take_screenshot(self, name: str):
        """Take a screenshot."""
        self.page.screenshot(path=f"screenshots/{name}.png")
