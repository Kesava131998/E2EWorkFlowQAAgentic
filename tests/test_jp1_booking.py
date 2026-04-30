import pytest
import allure
from pages.booking_page import BookingPage
from config.settings import settings


PICKUP_LOCATION = "New York"
DROPOFF_LOCATION_ALT = "Los Angeles"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestLocationSelection:
    """AC1: Location Selection"""

    @allure.story("AC1: Location Selection")
    @allure.title("Select same pickup and drop-off location")
    def test_pos_select_same_pickup_dropoff_location(self, page):
        """
        Jira: JP-1
        AC: User can select a pickup location and the drop-off auto-fills to the same location.
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Select pickup location"):
            booking.select_pickup_location(PICKUP_LOCATION)

        with allure.step("Verify drop-off auto-populated with same location"):
            pickup_val = booking.pickup_location_input.input_value()
            dropoff_val = booking.dropoff_location_input.input_value()
            assert pickup_val != "", "Pickup location should be set"
            assert dropoff_val != "", "Drop-off should auto-populate when same location selected"

    @allure.story("AC1: Location Selection")
    @allure.title("Select a different drop-off location from pickup")
    def test_pos_select_different_pickup_dropoff_location(self, page):
        """
        Jira: JP-1
        AC: User can set a different drop-off location from the pickup location.
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Select pickup location"):
            booking.select_pickup_location(PICKUP_LOCATION)

        with allure.step("Select a different drop-off location"):
            booking.select_dropoff_location(DROPOFF_LOCATION_ALT)

        with allure.step("Verify locations are set and differ"):
            pickup_val = booking.pickup_location_input.input_value()
            dropoff_val = booking.dropoff_location_input.input_value()
            assert pickup_val != "", "Pickup location should be set"
            assert dropoff_val != "", "Drop-off location should be set"
            assert pickup_val != dropoff_val, "Pickup and drop-off should differ"
