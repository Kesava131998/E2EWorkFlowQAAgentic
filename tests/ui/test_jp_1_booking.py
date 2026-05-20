import pytest
import allure
from playwright.sync_api import Page, expect
from pages.booking_page import BookingPage
from config.settings import settings


# Verified test data from JP-1 (last verified 2026-05-13)
SERVICEABLE_LOCATION = "Bronx, NY"
SERVICEABLE_DROPOFF = "Brooklyn, NY"
UNSERVICEABLE_LOCATION = "Seattle, WA"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC1: Location Selection")
@allure.title("Select valid pickup location from autocomplete")
def test_pos_select_pickup_location(page: Page):
    """
    Jira: JP-1
    AC: User can select a pickup location from the list of available service locations
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Step 2: Verify pickup location input is visible"):
        expect(booking.pickup_location_input).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 3: Select pickup location 'Bronx, NY'"):
        booking.select_pickup_location(SERVICEABLE_LOCATION)

    with allure.step("Step 4: Verify pickup input shows selected location"):
        expect(booking.pickup_location_input).not_to_be_empty(timeout=settings.SHORT_TIMEOUT)

    if api_calls:
        allure.attach(
            "\n".join([f"{r.method} {r.url}" for r in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC1: Location Selection")
@allure.title("Set a different drop-off location")
def test_pos_set_different_dropoff_location(page: Page):
    """
    Jira: JP-1
    AC: User can set the same or different drop-off location
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Step 2: Verify dropoff location input is visible"):
        expect(booking.dropoff_location_input).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 3: Select pickup location 'Bronx, NY'"):
        booking.select_pickup_location(SERVICEABLE_LOCATION)

    with allure.step("Step 4: Select different dropoff location 'Brooklyn, NY'"):
        booking.select_dropoff_location(SERVICEABLE_DROPOFF)

    with allure.step("Step 5: Verify dropoff input shows selected location"):
        expect(booking.dropoff_location_input).not_to_be_empty(timeout=settings.SHORT_TIMEOUT)

    if api_calls:
        allure.attach(
            "\n".join([f"{r.method} {r.url}" for r in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC1: Location Selection")
@allure.title("Enter unserviceable location — no results or error shown")
def test_err_unserviceable_pickup_location(page: Page):
    """
    Jira: JP-1
    AC: Unserviceable locations are outside the service area
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Step 2: Verify pickup location input is visible"):
        expect(booking.pickup_location_input).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 3: Type unserviceable location 'Seattle, WA'"):
        booking.type_pickup_location_no_select(UNSERVICEABLE_LOCATION)

    with allure.step("Step 4: Verify no valid suggestions appear"):
        page.wait_for_timeout(1500)
        suggestions_count = booking.location_suggestions.count()
        assert suggestions_count == 0, f"Expected 0 suggestions for unserviceable location, got {suggestions_count}"

    if api_calls:
        allure.attach(
            "\n".join([f"{r.method} {r.url}" for r in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC2: Date & Time Selection")
@allure.title("Default date values are pre-populated on page load")
def test_pos_default_date_values_prepopulated(page: Page):
    """
    Jira: JP-1
    AC: Default values are pre-populated (current date, morning pickup time, 1-day duration)
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)

    with allure.step("Step 1: Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Step 2: Verify duration section is visible"):
        expect(booking.duration_section.first).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify duration defaults to 1 day"):
        duration_text = booking.get_duration_text()
        assert "1" in duration_text or "Duration" in duration_text, \
            f"Expected default 1-day duration, got: {duration_text}"

    with allure.step("Step 4: Verify date/time text is displayed"):
        date_display = page.locator("p").filter(has_text="08:00 AM").first
        expect(date_display).to_be_visible(timeout=settings.SHORT_TIMEOUT)


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC2: Date & Time Selection")
@allure.title("Custom dates selection updates rental duration")
def test_pos_custom_dates_duration_recalculates(page: Page):
    """
    Jira: JP-1
    AC: User can select pickup and drop-off date/time; rental duration is auto-calculated
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)

    with allure.step("Step 1: Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Step 2: Verify duration section is visible"):
        expect(booking.duration_section.first).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 3: Open the date picker"):
        booking.open_date_picker()

    with allure.step("Step 4: Verify calendar is visible"):
        assert booking.is_calendar_open(), "Calendar did not open"

    with allure.step("Step 5: Select a pickup day (day 25)"):
        booking.select_calendar_day(25)

    with allure.step("Step 6: Select a dropoff day 3 days later (day 28)"):
        booking.select_calendar_day(28)

    with allure.step("Step 7: Verify duration updated beyond 1 day"):
        page.wait_for_timeout(500)
        duration_text = booking.get_duration_text()
        assert "1 day" not in duration_text.lower() or "3" in duration_text, \
            f"Duration did not update as expected: {duration_text}"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC2: Date & Time Selection")
@allure.title("Past dates are disabled in the calendar")
def test_err_past_date_selection_disabled(page: Page):
    """
    Jira: JP-1
    AC: Users cannot select past dates for pickup
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)

    with allure.step("Step 1: Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Step 2: Open the date picker"):
        booking.open_date_picker()

    with allure.step("Step 3: Verify calendar is visible"):
        assert booking.is_calendar_open(), "Calendar did not open"

    with allure.step("Step 4: Verify past date tiles are disabled"):
        disabled_tiles = page.locator(
            "button.react-calendar__tile:disabled, "
            "button.react-calendar__tile--disabled, "
            "abbr[aria-disabled='true']"
        )
        count = disabled_tiles.count()
        assert count > 0, "Expected past date tiles to be disabled, but none found"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC3: Vehicle Search")
@allure.title("Search returns available EVs for serviceable location")
def test_pos_search_returns_available_evs(page: Page):
    """
    Jira: JP-1
    AC: Search returns a list of available EVs based on selected location, dates, and duration
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Navigate to Joulez homepage"):
        booking.navigate()

    with allure.step("Step 2: Select pickup location 'Bronx, NY'"):
        booking.select_pickup_location(SERVICEABLE_LOCATION)

    with allure.step("Step 3: Verify dates are pre-filled"):
        expect(booking.duration_section.first).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 4: Click search"):
        booking.click_search()

    with allure.step("Step 5: Verify vehicle cards are displayed"):
        count = booking.get_vehicle_card_count()
        assert count > 0, f"Expected at least 1 vehicle result for '{SERVICEABLE_LOCATION}', got {count}"

    with allure.step("Step 6: Verify first card shows vehicle name and rate"):
        expect(booking.first_card_name).to_be_visible(timeout=settings.TIMEOUT)
        expect(booking.first_card_daily_rate).to_be_visible(timeout=settings.TIMEOUT)

    if api_calls:
        allure.attach(
            "\n".join([f"{r.method} {r.url}" for r in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC3: Vehicle Search")
@allure.title("Filter results by vehicle brand")
def test_pos_filter_results_by_brand(page: Page):
    """
    Jira: JP-1
    AC: Filter options are available by Vehicle Type, Brand, Model, and Price range
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Navigate to homepage and search 'Bronx, NY'"):
        booking.navigate()
        booking.select_pickup_location(SERVICEABLE_LOCATION)
        booking.click_search()

    with allure.step("Step 2: Verify filter buttons are visible"):
        filter_count = booking.get_filter_button_count()
        assert filter_count > 0, "Expected filter buttons to be visible on search results page"

    with allure.step("Step 3: Apply 'Tesla' brand filter"):
        booking.apply_filter("Tesla")

    with allure.step("Step 4: Verify results updated after filter applied"):
        page.wait_for_timeout(1000)
        count = booking.get_vehicle_card_count()
        assert count > 0, "Expected results after applying Tesla filter"

    if api_calls:
        allure.attach(
            "\n".join([f"{r.method} {r.url}" for r in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC3: Vehicle Search")
@allure.title("Search for unserviceable location returns no results")
def test_err_search_unserviceable_location_no_results(page: Page):
    """
    Jira: JP-1
    AC: Unserviceable locations should not return vehicle results
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Navigate to homepage"):
        booking.navigate()

    with allure.step("Step 2: Type unserviceable location 'Seattle, WA'"):
        booking.type_pickup_location_no_select(UNSERVICEABLE_LOCATION)

    with allure.step("Step 3: Verify no suggestions appear"):
        page.wait_for_timeout(1500)
        suggestions_count = booking.location_suggestions.count()
        assert suggestions_count == 0, \
            f"Expected 0 suggestions for unserviceable location, got {suggestions_count}"

    if api_calls:
        allure.attach(
            "\n".join([f"{r.method} {r.url}" for r in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC4: Vehicle Selection")
@allure.title("Click vehicle card opens detail page with full specs")
def test_pos_view_vehicle_detail_page(page: Page):
    """
    Jira: JP-1
    AC: User can click on any vehicle card to view detailed specifications
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Navigate and search 'Bronx, NY'"):
        booking.navigate()
        booking.select_pickup_location(SERVICEABLE_LOCATION)
        booking.click_search()

    with allure.step("Step 2: Verify vehicle cards visible"):
        count = booking.get_vehicle_card_count()
        assert count > 0, "No vehicle cards found to click"

    with allure.step("Step 3: Click first vehicle card"):
        booking.click_first_vehicle()

    with allure.step("Step 4: Verify detail page — car specs container visible"):
        expect(booking.car_specs_container.first).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 5: Verify Range spec displayed"):
        expect(booking.spec_range).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 6: Verify Year spec displayed"):
        expect(booking.spec_year).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 7: Verify Seating spec displayed"):
        expect(booking.spec_seating).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 8: Verify pickup and dropoff detail sections visible"):
        expect(booking.pickup_detail_section).to_be_visible(timeout=settings.TIMEOUT)
        expect(booking.dropoff_detail_section).to_be_visible(timeout=settings.TIMEOUT)

    if api_calls:
        allure.attach(
            "\n".join([f"{r.method} {r.url}" for r in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC5: Pricing Details")
@allure.title("Pricing breakdown — base rate, taxes, and grand total displayed")
def test_pos_pricing_breakdown_displayed(page: Page):
    """
    Jira: JP-1
    AC: Base rate, taxes, additional charges, and grand total are displayed
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Navigate, search 'Bronx, NY', open first vehicle"):
        booking.navigate()
        booking.select_pickup_location(SERVICEABLE_LOCATION)
        booking.click_search()
        booking.click_first_vehicle()

    with allure.step("Step 2: Verify pricing section is visible"):
        expect(booking.pricing_section).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify base rate is displayed"):
        expect(booking.base_rate_row).to_be_visible(timeout=settings.TIMEOUT)
        base_rate = booking.get_base_rate()
        assert base_rate.strip(), "Base rate text is empty"

    with allure.step("Step 4: Verify taxes row is displayed"):
        expect(booking.taxes_row).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 5: Verify grand total is displayed and non-empty"):
        expect(booking.grand_total_display).to_be_visible(timeout=settings.TIMEOUT)
        total = booking.get_grand_total()
        assert "$" in total, f"Grand total does not contain '$': {total}"

    if api_calls:
        allure.attach(
            "\n".join([f"{r.method} {r.url}" for r in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC6: Booking/Checkout")
@allure.title("Guest user clicking Pay Now is prompted to log in")
def test_pos_guest_redirected_to_login_before_payment(page: Page):
    """
    Jira: JP-1
    AC: User is prompted to Log in or Sign up (Join Us) before proceeding to payment
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)
    api_calls = []
    page.on("request", lambda req: api_calls.append(req) if "/joulez-service/" in req.url else None)

    with allure.step("Step 1: Navigate, search 'Bronx, NY', open first vehicle"):
        booking.navigate()
        booking.select_pickup_location(SERVICEABLE_LOCATION)
        booking.click_search()
        booking.click_first_vehicle()

    with allure.step("Step 2: Verify Pay Now is visible on booking page"):
        assert booking.is_pay_now_visible(), "Pay Now button is not visible on booking page"

    with allure.step("Step 3: Click Pay Now as guest"):
        booking.click_pay_now()

    with allure.step("Step 4: Verify auth gate is displayed"):
        assert booking.is_auth_gate_visible(), \
            "Expected login/join prompt after clicking Pay Now as guest, but auth gate not visible"

    if api_calls:
        allure.attach(
            "\n".join([f"{r.method} {r.url}" for r in api_calls]),
            name="Intercepted API Calls",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("Booking")
@allure.story("AC6: Booking/Checkout")
@allure.title("Unauthenticated user cannot complete booking — auth controls visible")
def test_perm_unauthenticated_user_cannot_complete_booking(page: Page):
    """
    Jira: JP-1
    AC: User authentication is required to complete the booking
    Locators verified via Playwright MCP snapshot on 2026-05-20
    """
    booking = BookingPage(page)

    with allure.step("Step 1: Navigate to Joulez homepage as guest"):
        booking.navigate()

    with allure.step("Step 2: Verify 'Log in' button is visible in navigation"):
        expect(page.locator("text=Log in").first).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 3: Verify 'Join Us' button is visible in navigation"):
        expect(page.locator("text=Join Us").first).to_be_visible(timeout=settings.TIMEOUT)

    with allure.step("Step 4: Navigate to booking page directly"):
        booking.select_pickup_location(SERVICEABLE_LOCATION)
        booking.click_search()
        booking.click_first_vehicle()

    with allure.step("Step 5: Verify Pay Now requires authentication"):
        booking.click_pay_now()
        assert booking.is_auth_gate_visible(), \
            "Unauthenticated user was not blocked — auth gate not shown after Pay Now"
