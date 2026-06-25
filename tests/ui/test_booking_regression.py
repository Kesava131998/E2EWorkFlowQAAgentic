"""
Regression suite — canary for locator decay on the Joulez homepage.
Goal: fail when selectors break, pass after self-heal patches them.
"""
import allure
from playwright.sync_api import Page, expect

from config.settings import settings
from pages.booking_page import BookingPage


@allure.epic("Regression")
@allure.feature("Booking Homepage — Core Locators")
class TestBookingRegression:

    @allure.story("Location input is present on load")
    @allure.title("REG-01: Location input visible on homepage")
    def test_reg_location_input_visible(self, page: Page):
        booking = BookingPage(page)
        booking.navigate()
        expect(booking.pickup_location_input).to_be_visible(timeout=settings.SHORT_TIMEOUT)

    @allure.story("Location input accepts keyboard input")
    @allure.title("REG-02: Location input accepts typed text")
    def test_reg_location_input_accepts_typing(self, page: Page):
        booking = BookingPage(page)
        booking.navigate()
        booking.pickup_location_input.click(timeout=settings.SHORT_TIMEOUT)
        booking.pickup_location_input.fill("Bronx")
        value = booking.pickup_location_input.input_value()
        assert "Bronx" in value, f"Expected 'Bronx' in input, got '{value}' — locator decay"
