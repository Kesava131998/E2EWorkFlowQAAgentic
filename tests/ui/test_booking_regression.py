"""
Regression suite — booking page homepage elements.

These 3 focused tests cover exactly the two locators used in the self-heal demo:
  - pickup_location_input  (BookingPage line ~14)
  - search_icon            (BookingPage line ~29)

They run in < 15 s and are the canary for locator decay on the Joulez homepage.
"""
import allure
import pytest
from playwright.sync_api import Page

from config.settings import settings
from pages.booking_page import BookingPage


@allure.epic("Regression")
@allure.feature("Booking Homepage — Core Locators")
class TestBookingRegression:

    @allure.story("Location input is present on load")
    @allure.title("REG-01: Location input visible on homepage")
    def test_reg_location_input_visible(self, page: Page):
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Assert pickup location input is visible"):
            assert booking.pickup_location_input.is_visible(
            ), "pickup_location_input must be visible — possible locator decay"

    @allure.story("Location input accepts keyboard input")
    @allure.title("REG-02: Location input accepts typed text")
    def test_reg_location_input_accepts_typing(self, page: Page):
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Click and type into location input"):
            booking.pickup_location_input.click(timeout=settings.SHORT_TIMEOUT)
            booking.pickup_location_input.fill("Bronx")

        with allure.step("Assert input contains typed value"):
            value = booking.pickup_location_input.input_value()
            assert "Bronx" in value, (
                f"Expected 'Bronx' in input value, got '{value}' — possible locator decay"
            )

    @allure.story("Search button is present on load")
    @allure.title("REG-03: Search button visible on homepage")
    def test_reg_search_button_visible(self, page: Page):
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Assert search icon is visible"):
            assert booking.search_icon.is_visible(
            ), "search_icon must be visible — possible locator decay"
