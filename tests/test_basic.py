import pytest
import allure
from pages.base_page import BasePage

@allure.feature("Basic Navigation")
@allure.story("Navigate to homepage")
def test_homepage_load(page):
    """Test that the homepage loads successfully."""
    base_page = BasePage(page)

    with allure.step("Navigate to base URL"):
        base_page.navigate_to("https://example.com")

    with allure.step("Verify page title"):
        assert "Example Domain" in page.title()

    with allure.step("Take screenshot"):
        base_page.take_screenshot("homepage")