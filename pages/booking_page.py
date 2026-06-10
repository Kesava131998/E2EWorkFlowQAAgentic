from playwright.sync_api import Page, Locator
import allure
from pages.base_page import BasePage
from config.settings import settings


class BookingPage(BasePage):
    """Page object for the Joulez EV pre-payment booking flow."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Location inputs (custom autocomplete - not standard Google Places)
        self.pickup_location_input: Locator = page.locator("input[placeholder='Location']")
        self.dropoff_location_input: Locator = page.locator("input[placeholder='Same as Pick Up']")
        # Custom dropdown uses listitem > paragraph structure (verified via Playwright MCP 2026-05-19)
        self.location_suggestions: Locator = page.locator(".pac-item")

        # Duration / date picker — commonBgInput parent that holds the "Duration" span
        self.duration_section: Locator = page.locator(".commonBgInput").filter(has_text="Duration")
        self.react_calendar: Locator = page.locator(".react-calendar")
        self.calendar_day_tiles: Locator = page.locator("button.react-calendar__tile")
        self.calendar_nav_label: Locator = page.locator(".react-calendar__navigation__label")
        self.duration_display: Locator = page.locator("[class*='Duration']").or_(
            page.locator("span:has-text('Duration'), div:has-text('Duration (')").first
        )

        # Search
        self.search_icon: Locator = page.locator(".searchBtn")
        self.search_button_mobile: Locator = page.locator(".searchButton")

        # Vehicle result cards (on /cars-list)
        self.vehicle_cards: Locator = page.locator(".card.cursorPointer")
        self.first_card_name: Locator = page.locator(".carModelWidth").first
        self.first_card_type: Locator = page.locator(".card.cursorPointer p.opacity70").first
        self.first_card_daily_rate: Locator = page.locator(".card.cursorPointer p.fontSize13").first
        self.first_card_trip_rate: Locator = page.locator(".card.cursorPointer p.tripFontSize").first
        self.first_card_seating: Locator = page.locator("p:has(img[alt='membersIcon'])").first
        self.first_card_range: Locator = page.locator("p:has(img[alt='milesIcon'])").first

        # Filter buttons (on /cars-list)
        self.filter_buttons: Locator = page.locator(".filterButtons")

        # Vehicle detail page (/booking) — Car Specs
        self.car_specs_container: Locator = page.locator(".carSpecsBox")
        self.spec_range: Locator = page.locator(".carSpecsBox").filter(has_text="Range")
        self.spec_year: Locator = page.locator(".carSpecsBox").filter(has_text="Year")
        self.spec_seating: Locator = page.locator(".carSpecsBox").filter(has_text="Seating")
        self.spec_color: Locator = page.locator(".carSpecsBox").filter(has_text="Color")

        # Pickup / drop-off details on booking page
        self.pickup_detail_section: Locator = page.get_by_text("Pick Up", exact=True).first
        self.dropoff_detail_section: Locator = page.get_by_text("Drop Off", exact=True).first

        # Pricing section on booking page
        self.pricing_section: Locator = page.get_by_text("Pricing Details", exact=True)
        self.base_rate_row: Locator = page.locator("div").filter(has_text="Base Rate").first
        self.taxes_row: Locator = page.locator("div").filter(has_text="Taxes").first
        # Grand total: the fontSize22 amount inside the "Total" summary block
        self.grand_total_display: Locator = page.locator(
            "div.cursorPointer:has(div.fontSize17:has-text('Total')) div.fontSize22"
        ).first

        # Pay Now — rendered as a div, not a button
        self.pay_now_div: Locator = page.locator(".nextBookingButton")
        self.pay_now_text: Locator = page.get_by_text("Pay Now", exact=True)

        # Auth gate on booking page
        self.join_us_button: Locator = page.get_by_role("button", name="Join Us")
        self.login_button: Locator = page.get_by_role("button", name="Log in")
        self.auth_heading: Locator = page.get_by_text("Let's Get You on the Road!")

    # ── Navigation ────────────────────────────────────────────────────────

    @allure.step("Navigate to Joulez homepage")
    def navigate(self):
        self.page.goto(settings.BASE_URL, timeout=settings.PAGE_LOAD_TIMEOUT, wait_until="load")

    # ── Location ─────────────────────────────────────────────────────────

    @allure.step("Select pickup location: {location}")
    def select_pickup_location(self, location: str):
        self.pickup_location_input.click()
        self.pickup_location_input.fill(location)
        self._pick_suggestion(self.pickup_location_input)

    @allure.step("Type pickup location without selecting suggestion: {text}")
    def type_pickup_location_no_select(self, text: str):
        """Type into pickup input (key-by-key) but do not click a suggestion.
        Caller asserts the resulting suggestion-list state (visible / empty)."""
        self.pickup_location_input.click()
        self.pickup_location_input.press_sequentially(text, delay=50)

    @allure.step("Select drop-off location: {location}")
    def select_dropoff_location(self, location: str):
        self.dropoff_location_input.click()
        self.dropoff_location_input.fill(location)
        self._pick_suggestion(self.dropoff_location_input)

    def _pick_suggestion(self, input_locator: Locator):
        """Click first .pac-item suggestion, or fall back to ArrowDown+Enter if none appear."""
        try:
            self.location_suggestions.first.wait_for(state="visible", timeout=settings.SHORT_TIMEOUT)
            self.location_suggestions.first.click()
        except Exception:
            input_locator.press("ArrowDown")
            self.page.wait_for_timeout(400)
            input_locator.press("Enter")
        self.page.wait_for_timeout(600)

    @allure.step("Click Search")
    def click_search(self):
        if self.search_icon.is_visible():
            self.search_icon.click()
        else:
            self.search_button_mobile.click()
        self.page.wait_for_url("**/cars-list", timeout=settings.PAGE_LOAD_TIMEOUT)
        self.page.wait_for_load_state("domcontentloaded")

    # ── Date picker ───────────────────────────────────────────────────────

    @allure.step("Open the date/duration picker")
    def open_date_picker(self):
        self.duration_section.first.click()
        self.react_calendar.wait_for(state="visible", timeout=settings.TIMEOUT)

    @allure.step("Get displayed duration text")
    def get_duration_text(self) -> str:
        return self.duration_section.first.inner_text()

    @allure.step("Navigate calendar to next month")
    def calendar_next_month(self):
        self.page.locator(".react-calendar__navigation__next-button").click()
        self.page.wait_for_timeout(300)

    @allure.step("Select a calendar day by number: {day}")
    def select_calendar_day(self, day: int):
        # Match enabled tiles from current month only (exclude neighboring month tiles)
        # Filter out disabled and neighboring month tiles
        current_month_tiles = self.calendar_day_tiles.locator(
            f"button.react-calendar__tile:not(.react-calendar__month-view__days__day--neighboringMonth):has-text('{day}')"
        )
        # Wait for at least one matching tile
        current_month_tiles.first.wait_for(state="visible", timeout=settings.TIMEOUT)
        current_month_tiles.first.click()

    @allure.step("Check whether calendar is open")
    def is_calendar_open(self) -> bool:
        return self.react_calendar.is_visible()

    # ── Search results ────────────────────────────────────────────────────

    @allure.step("Get vehicle card count")
    def get_vehicle_card_count(self) -> int:
        self.vehicle_cards.first.wait_for(state="visible", timeout=settings.TIMEOUT)
        return self.vehicle_cards.count()

    @allure.step("Get filter button count")
    def get_filter_button_count(self) -> int:
        self.filter_buttons.first.wait_for(state="visible", timeout=settings.TIMEOUT)
        return self.filter_buttons.count()

    @allure.step("Apply filter by text: {label}")
    def apply_filter(self, label: str):
        self.filter_buttons.first.wait_for(state="visible", timeout=settings.TIMEOUT)
        btn = self.filter_buttons.filter(has_text=label).first
        btn.wait_for(state="visible", timeout=settings.TIMEOUT)
        btn.click()
        self.page.wait_for_timeout(1000)

    # ── Vehicle selection ─────────────────────────────────────────────────

    @allure.step("Click the first vehicle card")
    def click_first_vehicle(self):
        self.vehicle_cards.first.wait_for(state="visible", timeout=settings.TIMEOUT)
        self.vehicle_cards.first.click()
        self.page.wait_for_url("**/booking", timeout=settings.PAGE_LOAD_TIMEOUT)
        self.page.wait_for_load_state("domcontentloaded")
        # Wait for key booking-page elements to be present
        self.car_specs_container.first.wait_for(state="visible", timeout=settings.TIMEOUT)

    # ── Pricing ───────────────────────────────────────────────────────────

    @allure.step("Get grand total text")
    def get_grand_total(self) -> str:
        return self.grand_total_display.inner_text()

    @allure.step("Get base rate text")
    def get_base_rate(self) -> str:
        return self.base_rate_row.inner_text()

    @allure.step("Get taxes text")
    def get_taxes(self) -> str:
        return self.taxes_row.inner_text()

    # ── Auth / Checkout ───────────────────────────────────────────────────

    @allure.step("Check if auth gate is visible")
    def is_auth_gate_visible(self) -> bool:
        return self.join_us_button.is_visible() or self.login_button.is_visible()

    @allure.step("Check if Pay Now is visible")
    def is_pay_now_visible(self) -> bool:
        try:
            self.pay_now_text.wait_for(state="visible", timeout=settings.TIMEOUT)
            return True
        except Exception:
            return False

    @allure.step("Click Pay Now")
    def click_pay_now(self):
        self.pay_now_div.click()
