import pytest
import allure
from playwright.sync_api import expect
from pages.booking_page import BookingPage
from config.settings import settings


PICKUP_QUERY = "New York"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
@allure.story("AC3: Search returns a list of available EVs based on selected location, dates, and duration")
@allure.title("Search returns at least one vehicle card after location selection")
def test_pos_search_returns_vehicle_cards(page):
    """
    Jira: JP-1
    AC3: Search returns a list of available EVs based on selected location, dates, and duration.
          Each result card displays: vehicle name, vehicle type, daily rate, total trip rate,
          seating capacity, and driving range.
    """
    booking_page = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking_page.navigate()

    with allure.step(f"Select pickup location '{PICKUP_QUERY}' from autocomplete"):
        booking_page.select_pickup_location(PICKUP_QUERY)

    with allure.step("Click Search button"):
        booking_page.click_search()

    with allure.step("Verify URL navigated to /cars-list"):
        assert "/cars-list" in page.url, f"Expected /cars-list in URL, got: {page.url}"

    with allure.step("Verify at least one vehicle card is displayed"):
        expect(booking_page.vehicle_cards.first).to_be_visible(timeout=settings.TIMEOUT)
        card_count = booking_page.get_vehicle_card_count()
        assert card_count >= 1, f"Expected ≥1 vehicle card on /cars-list, got {card_count}"
