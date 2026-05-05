import allure
from playwright.sync_api import expect
from pages.booking_page import BookingPage
from config.settings import settings


AC1_TEXT = "User should be able to select the pickup location from the auto dropdown and search"
PICKUP_QUERY_VALID = "New York"


@allure.epic("JP-7: Jourez check Pickup location enhanced with search")
@allure.feature("booking")
@allure.story(f"AC1: {AC1_TEXT}")
@allure.title("Pickup selection + Search navigates to /cars-list")
def test_pos_search_after_pickup_navigates_to_cars_list(page):
    """
    Jira: JP-7
    AC1: User should be able to select the pickup location from the auto dropdown and search.
    """
    booking_page = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking_page.navigate()

    with allure.step(f"Select pickup location '{PICKUP_QUERY_VALID}' from autocomplete"):
        booking_page.select_pickup_location(PICKUP_QUERY_VALID)

    with allure.step("Click Search button"):
        booking_page.click_search()

    with allure.step("Verify URL navigated to /cars-list"):
        assert "/cars-list" in page.url, f"Expected /cars-list, got {page.url}"


@allure.epic("JP-7: Jourez check Pickup location enhanced with search")
@allure.feature("booking")
@allure.story(f"AC1: {AC1_TEXT}")
@allure.title("Search returns at least one vehicle card")
def test_pos_search_results_show_vehicle_cards(page):
    """
    Jira: JP-7
    AC1: User should be able to select the pickup location from the auto dropdown and search.
    """
    booking_page = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking_page.navigate()

    with allure.step(f"Select pickup location '{PICKUP_QUERY_VALID}' and click Search"):
        booking_page.select_pickup_location(PICKUP_QUERY_VALID)
        booking_page.click_search()

    with allure.step("Verify at least one vehicle card is displayed"):
        expect(booking_page.vehicle_cards.first).to_be_visible(timeout=settings.TIMEOUT)
        card_count = booking_page.get_vehicle_card_count()
        assert card_count >= 1, f"Expected ≥1 vehicle card on /cars-list, got {card_count}"


@allure.epic("JP-7: Jourez check Pickup location enhanced with search")
@allure.feature("booking")
@allure.story(f"AC1: {AC1_TEXT}")
@allure.title("Default 'Same as Pick Up' drop-off carries through to search")
def test_edge_search_with_default_dropoff_succeeds(page):
    """
    Jira: JP-7
    AC1: User should be able to select the pickup location from the auto dropdown and search.

    Edge case: user touches only the pickup field; drop-off defaults to "Same as Pick Up".
    Search should still succeed without requiring an explicit drop-off entry.
    """
    booking_page = BookingPage(page)

    with allure.step("Navigate to Joulez homepage"):
        booking_page.navigate()

    with allure.step(f"Select pickup '{PICKUP_QUERY_VALID}' (leaving drop-off untouched)"):
        booking_page.select_pickup_location(PICKUP_QUERY_VALID)

    with allure.step("Verify drop-off field still shows the default placeholder behaviour"):
        placeholder = booking_page.dropoff_location_input.get_attribute("placeholder")
        assert placeholder == "Same as Pick Up", (
            f"Expected default drop-off placeholder 'Same as Pick Up', got '{placeholder}'"
        )

    with allure.step("Click Search and verify navigation succeeds"):
        booking_page.click_search()
        assert "/cars-list" in page.url, f"Expected /cars-list, got {page.url}"
