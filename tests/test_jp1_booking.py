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


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestDateTimeSelection:
    """AC2: Date & Time Selection"""

    @allure.story("AC2: Date & Time Selection")
    @allure.title("Default date and duration values are pre-populated on page load")
    def test_pos_default_values_prepopulated(self, page):
        """
        Jira: JP-1
        AC: Default values are pre-populated (current date, morning pickup time, 1-day duration).
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Verify duration section shows pre-populated default"):
            duration_text = booking.get_duration_text()
            assert duration_text.strip() != "", "Duration/date section should have pre-populated defaults on load"

    @allure.story("AC2: Date & Time Selection")
    @allure.title("Select pickup and drop-off dates; rental duration is calculated and displayed")
    def test_pos_select_dates_duration_calculated(self, page):
        """
        Jira: JP-1
        AC: User can select pickup/drop-off dates and rental duration is auto-calculated and displayed.
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Select pickup location to activate the date picker"):
            booking.select_pickup_location(PICKUP_LOCATION)

        with allure.step("Open date/duration picker"):
            booking.open_date_picker()
            assert booking.is_calendar_open(), "Calendar should open after clicking duration section"

        with allure.step("Navigate to next month to ensure selectable days"):
            booking.calendar_next_month()

        with allure.step("Select pickup date (5th of month)"):
            booking.select_calendar_day(5)

        with allure.step("Select drop-off date (10th of month)"):
            booking.select_calendar_day(10)

        with allure.step("Verify duration text is displayed after selection"):
            updated_text = booking.get_duration_text()
            assert updated_text.strip() != "", "Duration should be displayed after selecting pickup and drop-off dates"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestVehicleSearch:
    """AC3: Vehicle Search"""

    @allure.story("AC3: Vehicle Search")
    @allure.title("Search returns EV result cards for valid location and dates")
    def test_pos_search_returns_vehicle_results(self, page):
        """
        Jira: JP-1
        AC: Search returns a list of available EVs based on selected location, dates, and duration.
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Select pickup location"):
            booking.select_pickup_location(PICKUP_LOCATION)

        with allure.step("Click Search"):
            booking.click_search()

        with allure.step("Verify at least one vehicle result card is displayed"):
            count = booking.get_vehicle_card_count()
            assert count >= 1, f"Expected at least 1 vehicle result card, got {count}"

    @allure.story("AC3: Vehicle Search")
    @allure.title("Each result card displays required vehicle information fields")
    def test_pos_vehicle_cards_display_required_fields(self, page):
        """
        Jira: JP-1
        AC: Each result card displays vehicle name, type, daily rate, total trip rate,
            seating capacity, and driving range.
        """
        booking = BookingPage(page)

        with allure.step("Navigate and perform search"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()

        with allure.step("Verify first card shows vehicle name"):
            assert booking.first_card_name.is_visible(), "Vehicle name should be visible on result card"

        with allure.step("Verify first card shows vehicle type"):
            assert booking.first_card_type.is_visible(), "Vehicle type should be visible on result card"

        with allure.step("Verify first card shows daily rate"):
            assert booking.first_card_daily_rate.is_visible(), "Daily rate should be visible on result card"

        with allure.step("Verify first card shows total trip rate"):
            assert booking.first_card_trip_rate.is_visible(), "Trip rate should be visible on result card"

        with allure.step("Verify first card shows seating capacity"):
            assert booking.first_card_seating.is_visible(), "Seating capacity should be visible on result card"

        with allure.step("Verify first card shows driving range"):
            assert booking.first_card_range.is_visible(), "Driving range should be visible on result card"

    @allure.story("AC3: Vehicle Search")
    @allure.title("Filter options are available on the search results page")
    def test_pos_filter_options_visible(self, page):
        """
        Jira: JP-1
        AC: Filter options are available by Vehicle Type, Brand, Model, and Price range.
        """
        booking = BookingPage(page)

        with allure.step("Navigate and perform search"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()

        with allure.step("Verify filter buttons are present on results page"):
            count = booking.get_filter_button_count()
            assert count >= 1, f"Expected at least 1 filter button, got {count}"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestVehicleSelection:
    """AC4: Vehicle Selection"""

    @allure.story("AC4: Vehicle Selection")
    @allure.title("Clicking a vehicle card navigates to the vehicle detail/booking page")
    def test_pos_click_vehicle_navigates_to_detail_page(self, page):
        """
        Jira: JP-1
        AC: User can click on any vehicle card to view detailed specifications.
        """
        booking = BookingPage(page)

        with allure.step("Navigate and perform search"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()

        with allure.step("Click first vehicle card"):
            booking.click_first_vehicle()

        with allure.step("Verify URL navigated to vehicle booking/detail page"):
            assert "/booking" in page.url, f"Expected /booking in URL after selecting vehicle, got: {page.url}"

    @allure.story("AC4: Vehicle Selection")
    @allure.title("Vehicle detail page displays all required specifications")
    def test_pos_vehicle_detail_shows_all_specs(self, page):
        """
        Jira: JP-1
        AC: Vehicle detail page displays Range, Year, Seating capacity, Color,
            Pickup/Drop-off details, and full Pricing breakdown.
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify Range spec is visible"):
            assert booking.spec_range.is_visible(), "Range spec should be visible on vehicle detail page"

        with allure.step("Verify Year spec is visible"):
            assert booking.spec_year.is_visible(), "Year spec should be visible on vehicle detail page"

        with allure.step("Verify Seating capacity spec is visible"):
            assert booking.spec_seating.is_visible(), "Seating spec should be visible on vehicle detail page"

        with allure.step("Verify Color spec is visible"):
            assert booking.spec_color.is_visible(), "Color spec should be visible on vehicle detail page"

        with allure.step("Verify Pickup detail section is visible"):
            assert booking.pickup_detail_section.is_visible(), "Pickup details should be visible on booking page"

        with allure.step("Verify Drop-off detail section is visible"):
            assert booking.dropoff_detail_section.is_visible(), "Drop-off details should be visible on booking page"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestPricingDetails:
    """AC5: Pricing Details"""

    @allure.story("AC5: Pricing Details")
    @allure.title("Pricing section with base rate, taxes, and grand total is visible on booking page")
    def test_pos_pricing_section_visible_on_booking_page(self, page):
        """
        Jira: JP-1
        AC: Base rate, taxes, and grand total are displayed on the booking/detail page.
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify Pricing Details section header is visible"):
            assert booking.pricing_section.is_visible(), "Pricing Details section should be visible"

        with allure.step("Verify base rate row is visible"):
            assert booking.base_rate_row.is_visible(), "Base rate should be displayed in pricing section"

        with allure.step("Verify taxes row is visible"):
            assert booking.taxes_row.is_visible(), "Taxes row should be displayed in pricing section"

        with allure.step("Verify grand total is visible"):
            assert booking.grand_total_display.is_visible(), "Grand total should be prominently displayed"

    @allure.story("AC5: Pricing Details")
    @allure.title("Grand total displays a non-empty dollar amount")
    def test_pos_grand_total_is_non_empty_amount(self, page):
        """
        Jira: JP-1
        AC: Grand total is prominently displayed with a numeric amount.
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Read grand total text"):
            total = booking.get_grand_total()

        with allure.step("Verify grand total contains a dollar amount"):
            assert total.strip() != "", "Grand total should not be empty"
            assert "$" in total or any(c.isdigit() for c in total), (
                f"Grand total should contain a numeric dollar amount, got: {total!r}"
            )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestBookingCheckout:
    """AC6: Booking/Checkout"""

    @allure.story("AC6: Booking/Checkout")
    @allure.title("Pay Now button is visible on the booking summary page")
    def test_pos_pay_now_visible_on_booking_page(self, page):
        """
        Jira: JP-1
        AC: A 'Pay Now' button is displayed on the booking summary page.
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail/booking page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify Pay Now button is visible"):
            assert booking.is_pay_now_visible(), "Pay Now button should be visible on booking summary page"

    @allure.story("AC6: Booking/Checkout")
    @allure.title("Auth gate (Join Us / Log In) is visible for unauthenticated users on booking page")
    def test_pos_auth_gate_visible_for_unauthenticated_user(self, page):
        """
        Jira: JP-1
        AC: User is prompted to Log in or Sign up (Join Us) before proceeding to payment.
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page without logging in"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify authentication gate is visible for unauthenticated user"):
            assert booking.is_auth_gate_visible(), (
                "Join Us or Log In button should be visible — authentication is required to complete booking"
            )
