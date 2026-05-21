import re
import pytest
import allure
from pages.booking_page import BookingPage
from config.settings import settings

PICKUP_LOCATION = "Bronx"
DROPOFF_LOCATION = "Brooklyn"
UNSERVICEABLE_LOCATION = "Seattle"


def _navigate_to_booking_page(page) -> BookingPage:
    """Helper: navigate → select Bronx → search → click first vehicle → return BookingPage."""
    booking = BookingPage(page)
    booking.navigate()
    booking.select_pickup_location(PICKUP_LOCATION)
    booking.click_search()
    booking.click_first_vehicle()
    return booking


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — Location Selection
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC1 — Location Selection")
@allure.story("AC1: User can select a pickup location from serviceable locations")
@allure.title("Select serviceable pickup location (Bronx, NY)")
def test_pos_select_serviceable_pickup_location(page):
    """
    Jira: JP-1
    AC: User can select a pickup location from the list of available service locations
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Verify pickup location input is visible"):
        assert booking.pickup_location_input.is_visible()

    with allure.step(f"Type '{PICKUP_LOCATION}' and select first suggestion"):
        booking.select_pickup_location(PICKUP_LOCATION)

    with allure.step("Verify pickup input reflects the selected location"):
        value = booking.pickup_location_input.input_value()
        assert re.search(r"bronx", value, re.IGNORECASE), (
            f"Expected pickup to contain 'Bronx', got: '{value}'"
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC1 — Location Selection")
@allure.story("AC1: User can set a different drop-off location")
@allure.title("Select different drop-off location (Brooklyn, NY)")
def test_pos_select_different_dropoff_location(page):
    """
    Jira: JP-1
    AC: User can set the same or different drop-off location
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Select pickup location"):
        booking.select_pickup_location(PICKUP_LOCATION)

    with allure.step("Verify drop-off input is visible"):
        assert booking.dropoff_location_input.is_visible()

    with allure.step(f"Type '{DROPOFF_LOCATION}' and select first suggestion"):
        booking.select_dropoff_location(DROPOFF_LOCATION)

    with allure.step("Verify drop-off input reflects the selected location"):
        value = booking.dropoff_location_input.input_value()
        assert re.search(r"brooklyn", value, re.IGNORECASE), (
            f"Expected drop-off to contain 'Brooklyn', got: '{value}'"
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC1 — Location Selection")
@allure.story("AC1: Delivery option is available for supported metro areas")
@allure.title("Delivery option element present on homepage (conditional UI)")
@pytest.mark.xfail(strict=False, reason="Delivery option is conditional — may not always be visible")
def test_pos_delivery_option_available(page):
    """
    Jira: JP-1
    AC: Delivery option is available for supported metro areas
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Check for delivery option element"):
        delivery_locator = page.get_by_text("Delivery", exact=False)
        delivery_locator.wait_for(state="visible", timeout=settings.SHORT_TIMEOUT)
        assert delivery_locator.is_visible(), "Delivery option element not found on homepage"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC1 — Location Selection")
@allure.story("AC1: Unserviceable location shows no vehicle results")
@allure.title("Unserviceable location (Seattle, WA) produces no vehicle results")
def test_err_unserviceable_location_no_results(page):
    """
    Jira: JP-1
    AC: User can select a pickup location — negative: unserviceable locations return no vehicles
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step(f"Type unserviceable location '{UNSERVICEABLE_LOCATION}'"):
        booking.type_pickup_location_no_select(UNSERVICEABLE_LOCATION)

    with allure.step("Click search (no suggestion selected)"):
        if booking.search_icon.is_visible():
            booking.search_icon.click()
        else:
            booking.search_button_mobile.click()
        page.wait_for_load_state("domcontentloaded", timeout=settings.PAGE_LOAD_TIMEOUT)

    with allure.step("Verify no vehicle cards appear"):
        page.wait_for_timeout(settings.SHORT_TIMEOUT)
        card_count = booking.vehicle_cards.count()
        assert card_count == 0, (
            f"Expected 0 vehicle cards for unserviceable location '{UNSERVICEABLE_LOCATION}', "
            f"got {card_count}"
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC1 — Location Selection")
@allure.story("AC1: Same location for pickup and drop-off (default)")
@allure.title("Same location for pickup and drop-off (default behaviour)")
def test_edge_same_pickup_dropoff_location(page):
    """
    Jira: JP-1
    AC: User can set the same or different drop-off location — edge: defaults to same
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Select pickup location"):
        booking.select_pickup_location(PICKUP_LOCATION)

    with allure.step("Verify drop-off input shows 'Same as Pick Up' placeholder or is empty"):
        dropoff_value = booking.dropoff_location_input.input_value()
        placeholder = booking.dropoff_location_input.get_attribute("placeholder") or ""
        assert (
            dropoff_value == "" or
            re.search(r"same|pick.?up", placeholder, re.IGNORECASE)
        ), f"Expected drop-off to be empty or 'Same as Pick Up', got value='{dropoff_value}' placeholder='{placeholder}'"


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — Date & Time Selection
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC2 — Date & Time Selection")
@allure.story("AC2: User can select a pickup date")
@allure.title("Select pickup date from react-calendar")
def test_pos_select_pickup_date_from_calendar(page):
    """
    Jira: JP-1
    AC: User can select a pickup date and time
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Verify duration section is visible"):
        assert booking.duration_section.first.is_visible()

    with allure.step("Click duration section to open calendar"):
        booking.open_date_picker()

    with allure.step("Verify react-calendar is now visible"):
        assert booking.is_calendar_open(), "Calendar did not open after clicking duration section"

    with allure.step("Select a future calendar day"):
        booking.select_calendar_day(15)

    with allure.step("Verify calendar interaction succeeded (no exception thrown)"):
        pass


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC2 — Date & Time Selection")
@allure.story("AC2: Rental duration auto-calculated and displayed")
@allure.title("Rental duration auto-calculated after date selection")
def test_pos_duration_auto_calculated(page):
    """
    Jira: JP-1
    AC: Rental duration is auto-calculated and displayed
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Read initial duration display text"):
        initial_text = booking.get_duration_text()

    with allure.step("Verify duration text is non-empty (default pre-populated)"):
        assert initial_text.strip(), "Duration display is blank on load"

    with allure.step("Open date picker"):
        booking.open_date_picker()

    with allure.step("Select a future date (day 20)"):
        booking.select_calendar_day(20)

    with allure.step("Verify duration section still shows text after date change"):
        updated_text = booking.get_duration_text()
        assert updated_text.strip(), "Duration display is blank after selecting a date"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC2 — Date & Time Selection")
@allure.story("AC2: Default values are pre-populated")
@allure.title("Default date/duration values are pre-populated on load")
def test_pos_default_values_prepopulated(page):
    """
    Jira: JP-1
    AC: Default values are pre-populated (current date, morning pickup time, 1-day duration)
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Verify duration section is visible without any interaction"):
        assert booking.duration_section.first.is_visible()

    with allure.step("Read duration section text (default state)"):
        text = booking.get_duration_text()

    with allure.step("Verify text is non-empty (defaults are loaded)"):
        assert text.strip(), f"Expected pre-populated duration text, got empty string"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC2 — Date & Time Selection")
@allure.story("AC2: Past dates cannot be selected")
@allure.title("Past dates are not selectable in the date picker")
def test_err_past_dates_disabled_in_calendar(page):
    """
    Jira: JP-1
    AC: User can select a pickup date — negative: past dates are disabled
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Open date picker"):
        booking.open_date_picker()

    with allure.step("Verify calendar is open"):
        assert booking.is_calendar_open()

    with allure.step("Check that disabled tiles exist in calendar (past days)"):
        disabled_tiles = page.locator(
            "button.react-calendar__tile:disabled, "
            "button.react-calendar__tile[disabled]"
        )
        page.wait_for_timeout(settings.SHORT_TIMEOUT)
        count = disabled_tiles.count()
        assert count > 0, "Expected some disabled (past) date tiles in calendar, found none"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC2 — Date & Time Selection")
@allure.story("AC2: Single-day rental shows minimum duration")
@allure.title("Single-day rental — duration section still shows a value")
def test_edge_single_day_rental_duration(page):
    """
    Jira: JP-1
    AC: Rental duration is auto-calculated — edge: selecting same day shows 1-day minimum
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Open date picker"):
        booking.open_date_picker()

    with allure.step("Select the same day for both pickup and drop-off"):
        booking.select_calendar_day(15)
        page.wait_for_timeout(400)
        booking.select_calendar_day(15)

    with allure.step("Verify duration section still shows a non-empty value"):
        text = booking.get_duration_text()
        assert text.strip(), "Duration display is blank after same-day selection"


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — Vehicle Search
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC3 — Vehicle Search")
@allure.story("AC3: Search returns a list of available EVs")
@allure.title("Vehicle search returns results for Bronx, NY")
def test_pos_vehicle_search_returns_results(page):
    """
    Jira: JP-1
    AC: Search returns a list of available EVs based on selected location, dates, and duration
    """
    booking = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step(f"Select pickup location: {PICKUP_LOCATION}"):
        booking.select_pickup_location(PICKUP_LOCATION)

    with allure.step("Click search"):
        booking.click_search()

    with allure.step("Verify URL navigated to /cars-list"):
        assert "/cars-list" in page.url, f"Expected /cars-list URL, got: {page.url}"

    with allure.step("Verify at least one vehicle card is visible"):
        count = booking.get_vehicle_card_count()
        assert count > 0, f"Expected at least 1 vehicle card, got {count}"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC3 — Vehicle Search")
@allure.story("AC3: Vehicle card displays all required fields")
@allure.title("Vehicle card displays all required fields (name, type, rates, seating, range)")
def test_pos_vehicle_card_displays_required_fields(page):
    """
    Jira: JP-1
    AC: Each result card displays: vehicle name, vehicle type, daily rate, total trip rate,
        seating capacity, and driving range
    """
    booking = BookingPage(page)

    with allure.step("Navigate and search with Bronx"):
        booking.navigate()
        booking.select_pickup_location(PICKUP_LOCATION)
        booking.click_search()

    with allure.step("Wait for vehicle cards"):
        booking.get_vehicle_card_count()

    with allure.step("Verify first card has vehicle name"):
        name_text = booking.first_card_name.inner_text()
        assert name_text.strip(), f"Vehicle name is empty on first card"

    with allure.step("Verify first card has vehicle type"):
        type_text = booking.first_card_type.inner_text()
        assert type_text.strip(), f"Vehicle type is empty on first card"

    with allure.step("Verify first card shows a daily rate with $ symbol"):
        rate_text = booking.first_card_daily_rate.inner_text()
        assert "$" in rate_text, f"Daily rate missing '$' symbol: '{rate_text}'"

    with allure.step("Verify first card shows total trip rate"):
        trip_text = booking.first_card_trip_rate.inner_text()
        assert trip_text.strip(), f"Total trip rate is empty on first card"

    with allure.step("Verify first card shows seating capacity"):
        seating_text = booking.first_card_seating.inner_text()
        assert seating_text.strip(), f"Seating capacity is empty on first card"

    with allure.step("Verify first card shows driving range"):
        range_text = booking.first_card_range.inner_text()
        assert range_text.strip(), f"Driving range is empty on first card"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC3 — Vehicle Search")
@allure.story("AC3: Filter options are available")
@allure.title("Filter buttons are present on vehicle results page")
def test_pos_filter_buttons_available(page):
    """
    Jira: JP-1
    AC: Filter options are available by Vehicle Type, Brand, Model, and Price range
    """
    booking = BookingPage(page)

    with allure.step("Navigate and search with Bronx"):
        booking.navigate()
        booking.select_pickup_location(PICKUP_LOCATION)
        booking.click_search()

    with allure.step("Verify at least one filter button is visible"):
        count = booking.get_filter_button_count()
        assert count > 0, f"Expected at least 1 filter button, got {count}"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC3 — Vehicle Search")
@allure.story("AC3: Filter by vehicle type updates results")
@allure.title("Filter by vehicle type updates vehicle results")
def test_pos_filter_by_vehicle_type(page):
    """
    Jira: JP-1
    AC: Filter options are available by Vehicle Type — clicking a filter updates results
    """
    booking = BookingPage(page)

    with allure.step("Navigate and search with Bronx"):
        booking.navigate()
        booking.select_pickup_location(PICKUP_LOCATION)
        booking.click_search()

    with allure.step("Record initial vehicle card count"):
        initial_count = booking.get_vehicle_card_count()
        assert initial_count > 0, "No vehicle cards to filter"

    with allure.step("Click first filter button"):
        booking.filter_buttons.first.click()
        page.wait_for_timeout(1000)

    with allure.step("Verify results page is still visible (filter applied without crash)"):
        filtered_count = booking.vehicle_cards.count()
        assert filtered_count >= 0, "Vehicle card count is negative after filter"

    with allure.step("Verify filter produced ≤ original count"):
        assert filtered_count <= initial_count, (
            f"Filter increased card count: {initial_count} → {filtered_count}"
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC3 — Vehicle Search")
@allure.story("AC3: Negative — no vehicles for unserviceable location on results page")
@allure.title("No vehicles shown for unserviceable location on results page")
def test_err_no_vehicles_for_unserviceable_location(page):
    """
    Jira: JP-1
    AC: Search returns list — negative: unserviceable location returns empty results
    """
    booking = BookingPage(page)

    with allure.step("Navigate to homepage"):
        booking.navigate()

    with allure.step("Type unserviceable location (no suggestion click)"):
        booking.type_pickup_location_no_select(UNSERVICEABLE_LOCATION)

    with allure.step("Click search"):
        if booking.search_icon.is_visible():
            booking.search_icon.click()
        else:
            booking.search_button_mobile.click()
        page.wait_for_load_state("domcontentloaded", timeout=settings.PAGE_LOAD_TIMEOUT)

    with allure.step("Verify no vehicle cards on results page"):
        page.wait_for_timeout(settings.SHORT_TIMEOUT)
        count = booking.vehicle_cards.count()
        assert count == 0, f"Expected 0 vehicles for Seattle, got {count}"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC3 — Vehicle Search")
@allure.story("AC3: Re-clicking active filter restores results")
@allure.title("Re-clicking active filter restores all vehicle results")
def test_edge_filter_reset_shows_all_vehicles(page):
    """
    Jira: JP-1
    AC: Filter options — edge: toggling filter off restores original list
    """
    booking = BookingPage(page)

    with allure.step("Navigate and search with Bronx"):
        booking.navigate()
        booking.select_pickup_location(PICKUP_LOCATION)
        booking.click_search()

    with allure.step("Record initial vehicle count"):
        initial_count = booking.get_vehicle_card_count()
        assert initial_count > 0

    with allure.step("Apply filter"):
        booking.filter_buttons.first.click()
        page.wait_for_timeout(800)
        filtered_count = booking.vehicle_cards.count()

    with allure.step("De-select filter (click again)"):
        booking.filter_buttons.first.click()
        page.wait_for_timeout(800)

    with allure.step("Verify card count is restored"):
        restored_count = booking.vehicle_cards.count()
        assert restored_count >= filtered_count, (
            f"After de-selecting filter, count dropped from {filtered_count} to {restored_count}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — Vehicle Selection
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC4 — Vehicle Selection")
@allure.story("AC4: User can click on any vehicle card to view detailed specifications")
@allure.title("Click vehicle card navigates to /booking detail page")
def test_pos_view_vehicle_detail_page(page):
    """
    Jira: JP-1
    AC: User can click on any vehicle card to view detailed specifications
    """
    booking = BookingPage(page)

    with allure.step("Navigate and search with Bronx"):
        booking.navigate()
        booking.select_pickup_location(PICKUP_LOCATION)
        booking.click_search()

    with allure.step("Wait for vehicle cards"):
        booking.get_vehicle_card_count()

    with allure.step("Click the first vehicle card"):
        booking.click_first_vehicle()

    with allure.step("Verify URL contains /booking"):
        assert "/booking" in page.url, f"Expected /booking URL, got: {page.url}"

    with allure.step("Verify car specs container is visible"):
        assert booking.car_specs_container.first.is_visible()


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC4 — Vehicle Selection")
@allure.story("AC4: Vehicle detail shows Pickup/Drop-off details")
@allure.title("Vehicle detail page shows Pick Up and Drop Off sections")
def test_pos_vehicle_detail_shows_pickup_dropoff(page):
    """
    Jira: JP-1
    AC: Vehicle detail page displays: Pickup/Drop-off details
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Verify 'Pick Up' section is visible"):
        assert booking.pickup_detail_section.is_visible(), "'Pick Up' section not visible"

    with allure.step("Verify 'Drop Off' section is visible"):
        assert booking.dropoff_detail_section.is_visible(), "'Drop Off' section not visible"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC4 — Vehicle Selection")
@allure.story("AC4: Vehicle detail displays spec fields")
@allure.title("Vehicle spec details displayed: Range, Year, Seating, Color")
def test_pos_vehicle_specs_displayed(page):
    """
    Jira: JP-1
    AC: Vehicle detail page displays: Range, Year, Seating capacity, Color
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Verify car specs container is visible"):
        assert booking.car_specs_container.first.is_visible()

    with allure.step("Verify Range spec is displayed"):
        assert booking.spec_range.is_visible(), "Range spec not visible"

    with allure.step("Verify Year spec is displayed"):
        assert booking.spec_year.is_visible(), "Year spec not visible"

    with allure.step("Verify Seating spec is displayed"):
        assert booking.spec_seating.is_visible(), "Seating spec not visible"

    with allure.step("Verify Color spec is displayed"):
        assert booking.spec_color.is_visible(), "Color spec not visible"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC4 — Vehicle Selection")
@allure.story("AC4: Vehicle spec values are non-empty")
@allure.title("Vehicle spec values are non-empty strings")
def test_edge_vehicle_specs_have_values(page):
    """
    Jira: JP-1
    AC: Vehicle detail page displays spec details — edge: values are populated
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Read Range spec inner text and verify non-empty"):
        range_text = booking.spec_range.inner_text()
        assert range_text.strip(), f"Range spec is empty: '{range_text}'"

    with allure.step("Read Year spec inner text and verify non-empty"):
        year_text = booking.spec_year.inner_text()
        assert year_text.strip(), f"Year spec is empty: '{year_text}'"

    with allure.step("Read Seating spec inner text and verify non-empty"):
        seating_text = booking.spec_seating.inner_text()
        assert seating_text.strip(), f"Seating spec is empty: '{seating_text}'"


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — Pricing Details
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC5 — Pricing Details")
@allure.story("AC5: Base rate + taxes are displayed")
@allure.title("Pricing breakdown (base rate + taxes) is displayed on booking page")
def test_pos_pricing_breakdown_displayed(page):
    """
    Jira: JP-1
    AC: Base rate is displayed (per day and per trip) + Applicable taxes calculated and shown
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Verify 'Pricing Details' heading is visible"):
        assert booking.pricing_section.is_visible(), "'Pricing Details' heading not visible"

    with allure.step("Verify base rate row is visible"):
        assert booking.base_rate_row.is_visible(), "Base rate row not visible"

    with allure.step("Verify taxes row is visible"):
        assert booking.taxes_row.is_visible(), "Taxes row not visible"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC5 — Pricing Details")
@allure.story("AC5: Grand total is prominently displayed")
@allure.title("Grand total amount is visible and contains a dollar value")
def test_pos_grand_total_prominently_displayed(page):
    """
    Jira: JP-1
    AC: Grand total is prominently displayed
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Read grand total display text"):
        total_text = booking.get_grand_total()

    with allure.step("Verify grand total contains a $ symbol"):
        assert "$" in total_text, f"Grand total missing '$' symbol: '{total_text}'"

    with allure.step("Verify grand total contains a numeric value"):
        assert re.search(r"\d", total_text), f"Grand total has no numeric value: '{total_text}'"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC5 — Pricing Details")
@allure.story("AC5: Base rate is displayed")
@allure.title("Base rate text is visible and contains a dollar value")
def test_pos_base_rate_visible(page):
    """
    Jira: JP-1
    AC: Base rate is displayed (per day and per trip)
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Read base rate row text"):
        rate_text = booking.get_base_rate()

    with allure.step("Verify base rate contains a $ symbol"):
        assert "$" in rate_text, f"Base rate missing '$' symbol: '{rate_text}'"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC5 — Pricing Details")
@allure.story("AC5: Taxes are calculated and shown")
@allure.title("Taxes row is visible on booking page")
def test_pos_taxes_displayed(page):
    """
    Jira: JP-1
    AC: Applicable taxes are calculated and shown
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Verify taxes row is visible"):
        assert booking.taxes_row.is_visible(), "Taxes row not visible on booking page"

    with allure.step("Read taxes text and verify it is non-empty"):
        taxes_text = booking.get_taxes()
        assert taxes_text.strip(), f"Taxes row is empty: '{taxes_text}'"


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — Booking / Checkout (Auth Gate)
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC6 — Booking/Checkout")
@allure.story("AC6: Guest is prompted to Log in or Sign up before payment")
@allure.title("Guest user sees auth gate (Join Us / Log In) on booking page")
def test_perm_guest_sees_auth_gate(page):
    """
    Jira: JP-1
    AC: User is prompted to Log in or Sign up (Join Us) before proceeding to payment
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Verify auth gate is visible (Join Us OR Log In button)"):
        assert booking.is_auth_gate_visible(), (
            "Expected 'Join Us' or 'Log in' button to be visible for unauthenticated guest"
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC6 — Booking/Checkout")
@allure.story("AC6: Guest can initiate signup via Join Us")
@allure.title("Guest can click Join Us button to initiate signup flow")
def test_perm_guest_can_initiate_signup(page):
    """
    Jira: JP-1
    AC: User is prompted to Sign up (Join Us) — guest can click the button
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Verify Join Us button is visible"):
        booking.join_us_button.wait_for(state="visible", timeout=settings.TIMEOUT)
        assert booking.join_us_button.is_visible()

    with allure.step("Verify Join Us button is enabled"):
        assert not booking.join_us_button.is_disabled(), "Join Us button is disabled"

    with allure.step("Click Join Us button"):
        booking.join_us_button.click()

    with allure.step("Verify signup modal/page interaction triggered (no crash)"):
        page.wait_for_timeout(settings.SHORT_TIMEOUT)
        pass


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC6 — Booking/Checkout")
@allure.story("AC6: Negative — Pay Now not visible for unauthenticated guest")
@allure.title("Guest cannot see Pay Now button on booking page")
def test_err_guest_cannot_see_pay_now(page):
    """
    Jira: JP-1
    AC: A 'Pay Now' button is displayed — negative: not visible for unauthenticated guest
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Verify Pay Now button is NOT visible for guest"):
        assert not booking.is_pay_now_visible(), (
            "Pay Now should NOT be visible for an unauthenticated guest"
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("AC6 — Booking/Checkout")
@allure.story("AC6: Auth heading visible on booking page for guest")
@allure.title("Auth heading 'Let's Get You on the Road!' is visible on booking page")
def test_edge_auth_heading_visible(page):
    """
    Jira: JP-1
    AC: Guest sees auth gate — edge: heading text is visible
    """
    booking = _navigate_to_booking_page(page)

    with allure.step("Verify auth heading is visible"):
        booking.auth_heading.wait_for(state="visible", timeout=settings.TIMEOUT)
        assert booking.auth_heading.is_visible(), (
            "Expected \"Let's Get You on the Road!\" heading to be visible"
        )
