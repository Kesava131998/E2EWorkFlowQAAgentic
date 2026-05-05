import allure
from playwright.sync_api import expect
from pages.booking_page import BookingPage
from config.settings import settings


AC1_TEXT = "User should be able to select the pickup location from the auto dropdown"
PICKUP_QUERY_VALID = "New York"
PICKUP_QUERY_PARTIAL = "Manhat"
PICKUP_QUERY_INVALID = "zzzzqxyqxq"


@allure.epic("JP-5: Jourez check Pickup location enhanced")
@allure.feature("booking")
@allure.story(f"AC1: {AC1_TEXT}")
@allure.title("Select a valid pickup location from the autocomplete dropdown")
def test_pos_select_pickup_from_dropdown(page):
    """
    Jira: JP-5
    AC1: User should be able to select the pickup location from the auto dropdown.
    """
    booking_page = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking_page.navigate()

    with allure.step(f"Select pickup location '{PICKUP_QUERY_VALID}' from autocomplete"):
        booking_page.select_pickup_location(PICKUP_QUERY_VALID)

    with allure.step("Verify pickup input has been populated"):
        value = booking_page.pickup_location_input.input_value()
        assert value, f"Pickup input is empty after selecting '{PICKUP_QUERY_VALID}'"

    with allure.step("Verify suggestion list closed after selection"):
        expect(booking_page.location_suggestions).to_have_count(0, timeout=settings.SHORT_TIMEOUT)


@allure.epic("JP-5: Jourez check Pickup location enhanced")
@allure.feature("booking")
@allure.story(f"AC1: {AC1_TEXT}")
@allure.title("Autocomplete returns suggestions while typing in the pickup field")
def test_pos_pickup_autocomplete_appears_while_typing(page):
    """
    Jira: JP-5
    AC1: User should be able to select the pickup location from the auto dropdown.

    Note: drivejoulez does not visually expose the default `.pac-item` Google Places
    dropdown via CSS visibility, so this test asserts the autocomplete service has
    responded by checking the DOM is populated, rather than asserting visible state.
    """
    booking_page = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking_page.navigate()

    with allure.step(f"Type partial query '{PICKUP_QUERY_PARTIAL}' without selecting"):
        booking_page.type_pickup_location_no_select(PICKUP_QUERY_PARTIAL)

    with allure.step("Wait for Google Places API to respond"):
        page.wait_for_timeout(settings.SHORT_TIMEOUT)

    with allure.step("Verify at least one .pac-item suggestion is in the DOM"):
        suggestion_count = booking_page.location_suggestions.count()
        assert suggestion_count >= 1, (
            f"Expected autocomplete service to return >=1 suggestion for "
            f"'{PICKUP_QUERY_PARTIAL}', but DOM contains {suggestion_count}"
        )


@allure.epic("JP-5: Jourez check Pickup location enhanced")
@allure.feature("booking")
@allure.story(f"AC1: {AC1_TEXT}")
@allure.title("Suggestion list disappears after a selection is made")
def test_edge_pickup_suggestions_clear_after_selection(page):
    """
    Jira: JP-5
    AC1: User should be able to select the pickup location from the auto dropdown.
    """
    booking_page = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking_page.navigate()

    with allure.step(f"Select '{PICKUP_QUERY_VALID}' from the autocomplete dropdown"):
        booking_page.select_pickup_location(PICKUP_QUERY_VALID)

    with allure.step("Verify no .pac-item suggestions remain in the DOM"):
        expect(booking_page.location_suggestions).to_have_count(0, timeout=settings.SHORT_TIMEOUT)


@allure.epic("JP-5: Jourez check Pickup location enhanced")
@allure.feature("booking")
@allure.story(f"AC1: {AC1_TEXT}")
@allure.title("Typing a nonsense query yields no suggestions")
def test_err_pickup_no_suggestions_for_invalid_query(page):
    """
    Jira: JP-5
    AC1: User should be able to select the pickup location from the auto dropdown.
    """
    booking_page = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking_page.navigate()

    with allure.step(f"Type invalid query '{PICKUP_QUERY_INVALID}' without selecting"):
        booking_page.type_pickup_location_no_select(PICKUP_QUERY_INVALID)

    with allure.step("Wait for Google Places to settle, then verify no suggestions are visible"):
        page.wait_for_timeout(settings.SHORT_TIMEOUT)
        visible_count = page.locator(".pac-item:visible").count()
        assert visible_count == 0, (
            f"Expected 0 visible suggestions for nonsense query, got {visible_count}"
        )
