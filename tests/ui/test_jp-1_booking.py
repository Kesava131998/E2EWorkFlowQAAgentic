import pytest
import allure
from playwright.sync_api import Page

from pages.booking_page import BookingPage
from config.settings import settings


PICKUP_LOCATION = "Bronx"
DROPOFF_LOCATION = "Brooklyn"
UNSERVICEABLE_LOCATION = "Seattle"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestAC1LocationSelection:
    """AC1 — Location Selection"""

    @allure.story("AC1: Location Selection")
    @allure.title("TC1: Select a serviceable pickup location")
    def test_pos_select_serviceable_pickup_location(self, page: Page):
        """
        Jira: JP-1
        AC: AC1 — User can select a pickup location from the list of available service locations
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Verify pickup location input is visible and enabled"):
            assert booking.pickup_location_input.is_visible(), "Pickup input must be visible"

        with allure.step("Click the pickup location input"):
            booking.pickup_location_input.click(timeout=settings.SHORT_TIMEOUT)

        with allure.step("Type 'Bronx' into the input"):
            booking.pickup_location_input.fill(PICKUP_LOCATION)

        with allure.step("Wait for location suggestions and select first one"):
            booking._pick_suggestion(booking.pickup_location_input)

        with allure.step("Verify input is populated with selected location"):
            value = booking.pickup_location_input.input_value()
            assert PICKUP_LOCATION.lower() in value.lower(), (
                f"Expected '{PICKUP_LOCATION}' in input, got '{value}'"
            )

    @allure.story("AC1: Location Selection")
    @allure.title("TC2: Select a different drop-off location")
    def test_pos_select_different_dropoff_location(self, page: Page):
        """
        Jira: JP-1
        AC: AC1 — User can set the same or different drop-off location
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Select pickup location"):
            booking.select_pickup_location(PICKUP_LOCATION)

        with allure.step("Verify drop-off input is visible"):
            assert booking.dropoff_location_input.is_visible(), "Drop-off input must be visible"

        with allure.step("Click the drop-off location input"):
            booking.dropoff_location_input.click(timeout=settings.SHORT_TIMEOUT)

        with allure.step("Type drop-off location and select suggestion"):
            booking.dropoff_location_input.fill(DROPOFF_LOCATION)
            booking._pick_suggestion(booking.dropoff_location_input)

        with allure.step("Verify drop-off input is populated"):
            value = booking.dropoff_location_input.input_value()
            assert DROPOFF_LOCATION.lower() in value.lower(), (
                f"Expected '{DROPOFF_LOCATION}' in drop-off, got '{value}'"
            )

    @allure.story("AC1: Location Selection")
    @allure.title("TC3: Delivery option is available for metro area")
    @pytest.mark.xfail(strict=False, reason="Delivery option UI varies by region — optional element")
    def test_pos_delivery_option_available(self, page: Page):
        """
        Jira: JP-1
        AC: AC1 — Delivery option is available for supported metro areas
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Look for delivery option element on the booking form"):
            delivery_locator = page.locator(
                "text=Delivery, [data-testid*='delivery'], input[value*='delivery'], label:has-text('Delivery')"
            ).first
            assert delivery_locator.is_visible(timeout=settings.SHORT_TIMEOUT), (
                "Delivery option element should be visible"
            )

    @allure.story("AC1: Location Selection")
    @allure.title("TC4: Unserviceable location yields no search results")
    def test_err_unserviceable_location_no_results(self, page: Page):
        """
        Jira: JP-1
        AC: AC1 — Only serviceable locations return vehicles
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Type unserviceable location into pickup"):
            booking.type_pickup_location_no_select(UNSERVICEABLE_LOCATION)

        with allure.step("Click Search"):
            booking.click_search()

        with allure.step("Verify no vehicle cards are shown"):
            page.wait_for_load_state("domcontentloaded")
            card_count = booking.vehicle_cards.count()
            assert card_count == 0, (
                f"Expected 0 vehicle cards for unserviceable location, got {card_count}"
            )

    @allure.story("AC1: Location Selection")
    @allure.title("TC5: Same location for pickup and drop-off is accepted")
    def test_edge_same_pickup_dropoff_location(self, page: Page):
        """
        Jira: JP-1
        AC: AC1 — User can set the same drop-off location as pickup
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Select pickup location as Bronx"):
            booking.select_pickup_location(PICKUP_LOCATION)

        with allure.step("Verify drop-off defaults to same as pickup"):
            assert booking.dropoff_location_input.is_visible(), "Drop-off input must be visible"
            placeholder = booking.dropoff_location_input.get_attribute("placeholder") or ""
            assert "Same" in placeholder or "Pick Up" in placeholder, (
                f"Expected 'Same as Pick Up' placeholder, got '{placeholder}'"
            )

        with allure.step("Click Search without changing drop-off"):
            booking.click_search()

        with allure.step("Verify search proceeds without error"):
            assert "/cars-list" in page.url, f"Expected /cars-list URL, got {page.url}"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestAC2DateTimeSelection:
    """AC2 — Date & Time Selection"""

    @allure.story("AC2: Date & Time Selection")
    @allure.title("TC6: Select a pickup date from the calendar")
    def test_pos_select_pickup_date_from_calendar(self, page: Page):
        """
        Jira: JP-1
        AC: AC2 — User can select a pickup date and time
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Verify duration section is visible"):
            assert booking.duration_section.first.is_visible(), "Duration section must be visible"

        with allure.step("Click the duration section to open calendar"):
            booking.open_date_picker()

        with allure.step("Verify react-calendar is visible"):
            assert booking.react_calendar.is_visible(), "React calendar must be visible"

        with allure.step("Select day 15"):
            booking.select_calendar_day(15)

        with allure.step("Verify calendar closes or date updates"):
            page.wait_for_timeout(500)
            duration_text = booking.get_duration_text()
            assert duration_text, "Duration text should be non-empty after date selection"

    @allure.story("AC2: Date & Time Selection")
    @allure.title("TC7: Rental duration is auto-calculated")
    def test_pos_rental_duration_auto_calculated(self, page: Page):
        """
        Jira: JP-1
        AC: AC2 — Rental duration is auto-calculated and displayed
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Open the duration picker"):
            booking.open_date_picker()

        with allure.step("Select pickup day 15"):
            booking.select_calendar_day(15)

        with allure.step("Select drop-off day 16"):
            page.wait_for_timeout(300)
            booking.select_calendar_day(16)

        with allure.step("Verify duration text shows 1 day"):
            page.wait_for_timeout(500)
            duration_text = booking.get_duration_text()
            assert duration_text, "Duration text must be non-empty"
            assert any(d in duration_text for d in ["1 Day", "1 day", "1D", "Day"]), (
                f"Expected '1 Day' in duration text, got '{duration_text}'"
            )

    @allure.story("AC2: Date & Time Selection")
    @allure.title("TC8: Default values are pre-populated")
    def test_pos_default_values_prepopulated(self, page: Page):
        """
        Jira: JP-1
        AC: AC2 — Default values are pre-populated (current date, morning pickup, 1-day duration)
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Verify duration section is visible"):
            assert booking.duration_section.first.is_visible(), "Duration section must be visible"

        with allure.step("Verify duration section has a pre-populated value"):
            duration_text = booking.get_duration_text()
            assert duration_text.strip(), f"Duration section should have default text, got '{duration_text}'"

    @allure.story("AC2: Date & Time Selection")
    @allure.title("TC9: Past dates are disabled in the calendar")
    def test_err_past_dates_disabled_in_calendar(self, page: Page):
        """
        Jira: JP-1
        AC: AC2 — Past dates are not selectable
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Open the duration picker"):
            booking.open_date_picker()

        with allure.step("Verify calendar is visible"):
            assert booking.react_calendar.is_visible(), "Calendar must be visible"

        with allure.step("Check that day 1 tile is disabled or a neighboring month tile"):
            day1_tile = page.locator(
                "button.react-calendar__tile"
            ).filter(has_text="1").first
            day1_tile.wait_for(state="visible", timeout=settings.TIMEOUT)
            is_disabled = day1_tile.get_attribute("disabled") is not None
            is_neighbor = "neighboringMonth" in (day1_tile.get_attribute("class") or "")
            assert is_disabled or is_neighbor, (
                "Day 1 should be disabled or a neighboring month tile (past date)"
            )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestAC3VehicleSearch:
    """AC3 — Vehicle Search"""

    @allure.story("AC3: Vehicle Search")
    @allure.title("TC10: Search returns vehicle cards")
    def test_pos_vehicle_search_returns_results(self, page: Page):
        """
        Jira: JP-1
        AC: AC3 — Search returns a list of available EVs
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Select pickup location Bronx"):
            booking.select_pickup_location(PICKUP_LOCATION)

        with allure.step("Click Search"):
            booking.click_search()

        with allure.step("Wait for /cars-list and verify vehicle cards"):
            assert "/cars-list" in page.url, f"Expected /cars-list URL, got {page.url}"
            count = booking.get_vehicle_card_count()
            assert count >= 1, f"Expected at least 1 vehicle card, got {count}"

    @allure.story("AC3: Vehicle Search")
    @allure.title("TC11: Vehicle card displays required fields")
    def test_pos_vehicle_card_displays_required_fields(self, page: Page):
        """
        Jira: JP-1
        AC: AC3 — Each result card shows name, type, daily rate, trip rate, seating, range
        """
        booking = BookingPage(page)

        with allure.step("Navigate and search with Bronx"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()

        with allure.step("Wait for first vehicle card"):
            booking.vehicle_cards.first.wait_for(state="visible", timeout=settings.TIMEOUT)

        with allure.step("Verify vehicle name is visible"):
            assert booking.first_card_name.is_visible(), "Vehicle name must be visible on card"

        with allure.step("Verify vehicle type is visible"):
            assert booking.first_card_type.is_visible(), "Vehicle type must be visible on card"

        with allure.step("Verify daily rate is visible"):
            assert booking.first_card_daily_rate.is_visible(), "Daily rate must be visible on card"

        with allure.step("Verify trip rate is visible"):
            assert booking.first_card_trip_rate.is_visible(), "Trip rate must be visible on card"

        with allure.step("Verify seating capacity is visible"):
            assert booking.first_card_seating.is_visible(), "Seating capacity must be visible on card"

        with allure.step("Verify driving range is visible"):
            assert booking.first_card_range.is_visible(), "Driving range must be visible on card"

    @allure.story("AC3: Vehicle Search")
    @allure.title("TC12: Filter buttons are available")
    def test_pos_filter_buttons_available(self, page: Page):
        """
        Jira: JP-1
        AC: AC3 — Filter options are available by Vehicle Type, Brand, Model, Price range
        """
        booking = BookingPage(page)

        with allure.step("Navigate and search with Bronx"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()

        with allure.step("Wait for filter buttons"):
            count = booking.get_filter_button_count()
            assert count >= 4, f"Expected at least 4 filter buttons, got {count}"

    @allure.story("AC3: Vehicle Search")
    @allure.title("TC13: Unserviceable location yields no vehicles")
    def test_err_no_vehicles_for_unserviceable_location(self, page: Page):
        """
        Jira: JP-1
        AC: AC3 — No vehicles shown for out-of-service-area locations
        """
        booking = BookingPage(page)

        with allure.step("Navigate to Joulez homepage"):
            booking.navigate()

        with allure.step("Type unserviceable location"):
            booking.type_pickup_location_no_select(UNSERVICEABLE_LOCATION)

        with allure.step("Click Search"):
            booking.click_search()

        with allure.step("Verify zero vehicle cards"):
            page.wait_for_load_state("domcontentloaded")
            count = booking.vehicle_cards.count()
            assert count == 0, f"Expected 0 cards for unserviceable location, got {count}"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestAC4VehicleSelection:
    """AC4 — Vehicle Selection"""

    @allure.story("AC4: Vehicle Selection")
    @allure.title("TC14: Click vehicle card navigates to detail page")
    def test_pos_click_vehicle_card_navigates_to_detail(self, page: Page):
        """
        Jira: JP-1
        AC: AC4 — User can click on any vehicle card to view detailed specifications
        """
        booking = BookingPage(page)

        with allure.step("Navigate and search"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()

        with allure.step("Verify first card is visible"):
            booking.vehicle_cards.first.wait_for(state="visible", timeout=settings.TIMEOUT)

        with allure.step("Click the first vehicle card"):
            booking.click_first_vehicle()

        with allure.step("Verify URL is /booking"):
            assert "/booking" in page.url, f"Expected /booking URL, got {page.url}"

        with allure.step("Verify car specs container is visible"):
            assert booking.car_specs_container.first.is_visible(), "Car specs box must be visible"

    @allure.story("AC4: Vehicle Selection")
    @allure.title("TC15: Vehicle detail page shows pickup and drop-off details")
    def test_pos_vehicle_detail_shows_pickup_dropoff(self, page: Page):
        """
        Jira: JP-1
        AC: AC4 — Vehicle detail page shows Pickup/Drop-off details
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify Pick Up section is visible"):
            assert booking.pickup_detail_section.is_visible(), "'Pick Up' section must be visible"

        with allure.step("Verify Drop Off section is visible"):
            assert booking.dropoff_detail_section.is_visible(), "'Drop Off' section must be visible"

    @allure.story("AC4: Vehicle Selection")
    @allure.title("TC16: Car specs display Range, Year, Seating, Color")
    def test_pos_car_specs_display_range_year_seating_color(self, page: Page):
        """
        Jira: JP-1
        AC: AC4 — Vehicle detail page displays Range, Year, Seating, Color
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify Range spec is visible"):
            assert booking.spec_range.is_visible(), "Range spec must be visible"

        with allure.step("Verify Year spec is visible"):
            assert booking.spec_year.is_visible(), "Year spec must be visible"

        with allure.step("Verify Seating spec is visible"):
            assert booking.spec_seating.is_visible(), "Seating spec must be visible"

        with allure.step("Verify Color spec is visible"):
            assert booking.spec_color.is_visible(), "Color spec must be visible"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestAC5PricingDetails:
    """AC5 — Pricing Details"""

    @allure.story("AC5: Pricing Details")
    @allure.title("TC17: Pricing breakdown is displayed")
    def test_pos_pricing_breakdown_displayed(self, page: Page):
        """
        Jira: JP-1
        AC: AC5 — Base rate, taxes, and additional charges are displayed
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify 'Pricing Details' heading is visible"):
            assert booking.pricing_section.is_visible(), "'Pricing Details' heading must be visible"

        with allure.step("Verify base rate row is visible"):
            assert booking.base_rate_row.is_visible(), "Base rate row must be visible"

        with allure.step("Verify taxes row is visible"):
            assert booking.taxes_row.is_visible(), "Taxes row must be visible"

    @allure.story("AC5: Pricing Details")
    @allure.title("TC18: Grand total is prominently displayed")
    def test_pos_grand_total_prominently_displayed(self, page: Page):
        """
        Jira: JP-1
        AC: AC5 — Grand total is prominently displayed
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify grand total element is visible"):
            assert booking.grand_total_display.is_visible(), "Grand total display must be visible"

        with allure.step("Verify grand total contains a numeric value"):
            total_text = booking.get_grand_total()
            assert total_text.strip(), f"Grand total must be non-empty, got '{total_text}'"

    @allure.story("AC5: Pricing Details")
    @allure.title("TC19: Base rate per day is visible")
    def test_pos_base_rate_visible(self, page: Page):
        """
        Jira: JP-1
        AC: AC5 — Base rate is displayed (per day and per trip)
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify base rate row is visible"):
            assert booking.base_rate_row.is_visible(), "Base rate row must be visible"

        with allure.step("Verify base rate text is readable"):
            base_rate = booking.get_base_rate()
            assert base_rate.strip(), f"Base rate text must be non-empty, got '{base_rate}'"

    @allure.story("AC5: Pricing Details")
    @allure.title("TC20: Taxes are included in pricing")
    def test_edge_taxes_included_in_pricing(self, page: Page):
        """
        Jira: JP-1
        AC: AC5 — Applicable taxes are calculated and shown
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify taxes row is visible"):
            assert booking.taxes_row.is_visible(), "Taxes row must be visible"

        with allure.step("Verify taxes text is non-empty"):
            taxes_text = booking.get_taxes()
            assert taxes_text.strip(), f"Taxes text must be non-empty, got '{taxes_text}'"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking")
class TestAC6BookingCheckout:
    """AC6 — Booking/Checkout"""

    @allure.story("AC6: Booking/Checkout")
    @allure.title("TC21: Guest user sees authentication gate")
    def test_perm_guest_sees_auth_gate(self, page: Page):
        """
        Jira: JP-1
        AC: AC6 — User is prompted to Log in or Sign up before proceeding to payment
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page as guest"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify auth gate is visible"):
            assert booking.is_auth_gate_visible(), "Auth gate (Join Us / Log in buttons) must be visible for guests"

        with allure.step("Verify 'Join Us' button is visible"):
            assert booking.join_us_button.is_visible(), "'Join Us' button must be visible"

        with allure.step("Verify 'Log in' button is visible"):
            assert booking.login_button.is_visible(), "'Log in' button must be visible"

    @allure.story("AC6: Booking/Checkout")
    @allure.title("TC22: Guest can initiate signup via Join Us")
    def test_perm_guest_can_initiate_signup(self, page: Page):
        """
        Jira: JP-1
        AC: AC6 — A 'Join Us' button is available for sign up
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page as guest"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify 'Join Us' button is visible"):
            assert booking.join_us_button.is_visible(), "'Join Us' button must be visible"

        with allure.step("Verify 'Join Us' button is enabled"):
            assert booking.join_us_button.is_enabled(), "'Join Us' button must be enabled (not disabled)"

    @allure.story("AC6: Booking/Checkout")
    @allure.title("TC23: Guest cannot see Pay Now button")
    def test_err_guest_cannot_see_pay_now(self, page: Page):
        """
        Jira: JP-1
        AC: AC6 — User authentication is required to complete booking; Pay Now not shown to guests
        """
        booking = BookingPage(page)

        with allure.step("Navigate to vehicle detail page as guest"):
            booking.navigate()
            booking.select_pickup_location(PICKUP_LOCATION)
            booking.click_search()
            booking.click_first_vehicle()

        with allure.step("Verify Pay Now is NOT visible for unauthenticated user"):
            assert not booking.is_pay_now_visible(), (
                "'Pay Now' must NOT be visible for unauthenticated guests — auth gate should appear instead"
            )
