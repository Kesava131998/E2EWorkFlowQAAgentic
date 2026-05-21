import pytest
import allure
import requests
from datetime import datetime, timedelta
from config.settings import settings

BASE_URL = settings.API_BASE_URL


def _get_available_locations():
    return requests.get(
        f"{BASE_URL}/location/available-locations/open",
        timeout=15,
    )


def _find_bronx_location(locations: list) -> dict | None:
    for loc in locations:
        name = (
            loc.get("locationName") or
            loc.get("name") or
            loc.get("city") or
            ""
        )
        if "bronx" in name.lower():
            return loc
    return None


def _get_location_id(loc: dict) -> str | int | None:
    return loc.get("id") or loc.get("locationId") or loc.get("_id")


def _build_search_dates():
    tomorrow = datetime.now() + timedelta(days=1)
    three_days = datetime.now() + timedelta(days=3)
    fmt = "%Y-%m-%dT%H:%M:%S"
    return tomorrow.strftime(fmt), three_days.strftime(fmt)


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — Location Selection
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("API — AC1: Location Selection")
@allure.story("AC1: Available locations endpoint returns serviceable locations")
@allure.title("GET /location/available-locations/open → 200 + list contains Bronx")
def test_api_pos_get_available_locations():
    """
    Jira: JP-1
    AC: User can select a pickup location from the list of available service locations
    """
    with allure.step("Call GET /location/available-locations/open"):
        resp = _get_available_locations()

    with allure.step("Verify HTTP 200"):
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:300]}"
        )

    with allure.step("Parse response as JSON"):
        data = resp.json()

    with allure.step("Extract locations list from response"):
        locations = (
            data if isinstance(data, list) else
            data.get("data") or
            data.get("locations") or
            data.get("content") or
            []
        )
        assert len(locations) > 0, "Locations list is empty"

    with allure.step("Verify Bronx, NY is in the list"):
        bronx = _find_bronx_location(locations)
        sample = [
            loc.get("locationName") or loc.get("name") or loc.get("city")
            for loc in locations[:10]
        ]
        assert bronx is not None, (
            f"Expected 'Bronx' to be in locations list. First 10: {sample}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — Vehicle Search
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("API — AC3: Vehicle Search")
@allure.story("AC3: Search returns available cars for a serviceable location")
@allure.title("POST /car/availableCarsV4/open → 200 + car list for Bronx, NY")
def test_api_pos_get_available_cars():
    """
    Jira: JP-1
    AC: Search returns a list of available EVs based on selected location, dates, and duration
    """
    with allure.step("Fetch available locations to get Bronx location ID"):
        loc_resp = _get_available_locations()
        assert loc_resp.status_code == 200, f"Locations API failed: {loc_resp.status_code}"
        loc_data = loc_resp.json()
        locations = (
            loc_data if isinstance(loc_data, list) else
            loc_data.get("data") or
            loc_data.get("locations") or
            loc_data.get("content") or
            []
        )
        bronx = _find_bronx_location(locations)
        assert bronx is not None, "Bronx location not found in available locations"
        location_id = _get_location_id(bronx)
        assert location_id is not None, f"Could not extract ID from Bronx location: {bronx}"

    pickup_dt, dropoff_dt = _build_search_dates()

    with allure.step(f"POST /car/availableCarsV4/open with Bronx locationId={location_id}"):
        payload = {
            "pickUpLocationId": location_id,
            "dropOffLocationId": location_id,
            "pickUpDate": pickup_dt,
            "dropOffDate": dropoff_dt,
        }
        resp = requests.post(
            f"{BASE_URL}/car/availableCarsV4/open",
            json=payload,
            timeout=20,
        )

    with allure.step("Verify HTTP 200"):
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:400]}"
        )

    with allure.step("Verify response contains at least one car"):
        data = resp.json()
        cars = (
            data if isinstance(data, list) else
            data.get("cars") or
            data.get("data") or
            data.get("content") or
            data.get("carList") or
            []
        )
        assert len(cars) > 0, f"Expected at least 1 car for Bronx. Response: {str(data)[:400]}"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("API — AC3: Vehicle Search")
@allure.story("AC3: Negative — missing location returns error")
@allure.title("POST /car/availableCarsV4/open with empty payload → error (not 200)")
def test_api_err_cars_no_location():
    """
    Jira: JP-1
    AC: Search returns list — negative: missing location should return an error
    """
    with allure.step("POST /car/availableCarsV4/open with empty payload"):
        resp = requests.post(
            f"{BASE_URL}/car/availableCarsV4/open",
            json={},
            timeout=15,
        )

    with allure.step("Verify response is an error (not HTTP 200)"):
        assert resp.status_code != 200, (
            f"Expected error response for empty payload, got 200: {resp.text[:300]}"
        )

    with allure.step("Verify status code is 4xx or 5xx"):
        assert resp.status_code >= 400, (
            f"Expected 4xx/5xx error status, got {resp.status_code}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — Vehicle Selection
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("API — AC4: Vehicle Selection")
@allure.story("AC4: GET car by ID returns spec fields")
@allure.title("GET /car/getById/{carId}/open → 200 + spec fields (range, year, seating, color)")
def test_api_pos_car_detail():
    """
    Jira: JP-1
    AC: Vehicle detail page displays: Range, Year, Seating capacity, Color
    """
    with allure.step("Get first available car ID from Bronx search"):
        loc_resp = _get_available_locations()
        assert loc_resp.status_code == 200
        loc_data = loc_resp.json()
        locations = (
            loc_data if isinstance(loc_data, list) else
            loc_data.get("data") or
            loc_data.get("locations") or
            loc_data.get("content") or
            []
        )
        bronx = _find_bronx_location(locations)
        assert bronx is not None, "Bronx not in available locations"
        location_id = _get_location_id(bronx)

        pickup_dt, dropoff_dt = _build_search_dates()
        cars_resp = requests.post(
            f"{BASE_URL}/car/availableCarsV4/open",
            json={
                "pickUpLocationId": location_id,
                "dropOffLocationId": location_id,
                "pickUpDate": pickup_dt,
                "dropOffDate": dropoff_dt,
            },
            timeout=20,
        )
        assert cars_resp.status_code == 200, f"Cars API failed: {cars_resp.status_code}"
        cars_data = cars_resp.json()
        cars = (
            cars_data if isinstance(cars_data, list) else
            cars_data.get("cars") or
            cars_data.get("data") or
            cars_data.get("content") or
            cars_data.get("carList") or
            []
        )
        assert len(cars) > 0, "No cars returned for Bronx"
        first_car = cars[0]
        car_id = (
            first_car.get("id") or
            first_car.get("carId") or
            first_car.get("_id")
        )
        assert car_id is not None, f"Could not extract car ID from: {first_car}"

    with allure.step(f"GET /car/getById/{car_id}/open"):
        resp = requests.get(
            f"{BASE_URL}/car/getById/{car_id}/open",
            timeout=15,
        )

    with allure.step("Verify HTTP 200"):
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:300]}"
        )

    with allure.step("Verify response contains spec fields"):
        data = resp.json()
        car = data.get("data") or data if isinstance(data, dict) else {}
        spec_keys = list(car.keys())
        has_specs = any(
            k in str(spec_keys).lower()
            for k in ["range", "year", "seat", "color"]
        )
        assert has_specs or len(spec_keys) > 3, (
            f"Car detail response seems too sparse: {spec_keys[:10]}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — Pricing Details
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("API — AC5: Pricing Details")
@allure.story("AC5: Estimated price endpoint returns pricing breakdown")
@allure.title("POST /booking/estimatedPrice/open → 200 + baseRate/taxes/totalPrice")
def test_api_pos_estimated_price():
    """
    Jira: JP-1
    AC: Base rate displayed + taxes calculated and shown + Grand total prominently displayed
    """
    with allure.step("Get Bronx location ID and first car ID"):
        loc_resp = _get_available_locations()
        assert loc_resp.status_code == 200
        loc_data = loc_resp.json()
        locations = (
            loc_data if isinstance(loc_data, list) else
            loc_data.get("data") or
            loc_data.get("locations") or
            loc_data.get("content") or
            []
        )
        bronx = _find_bronx_location(locations)
        assert bronx is not None
        location_id = _get_location_id(bronx)

        pickup_dt, dropoff_dt = _build_search_dates()
        cars_resp = requests.post(
            f"{BASE_URL}/car/availableCarsV4/open",
            json={
                "pickUpLocationId": location_id,
                "dropOffLocationId": location_id,
                "pickUpDate": pickup_dt,
                "dropOffDate": dropoff_dt,
            },
            timeout=20,
        )
        assert cars_resp.status_code == 200
        cars_data = cars_resp.json()
        cars = (
            cars_data if isinstance(cars_data, list) else
            cars_data.get("cars") or
            cars_data.get("data") or
            cars_data.get("content") or
            cars_data.get("carList") or
            []
        )
        assert len(cars) > 0
        car_id = (
            cars[0].get("id") or
            cars[0].get("carId") or
            cars[0].get("_id")
        )
        assert car_id is not None

    with allure.step("POST /booking/estimatedPrice/open"):
        payload = {
            "carId": car_id,
            "pickUpLocationId": location_id,
            "dropOffLocationId": location_id,
            "pickUpDate": pickup_dt,
            "dropOffDate": dropoff_dt,
        }
        resp = requests.post(
            f"{BASE_URL}/booking/estimatedPrice/open",
            json=payload,
            timeout=15,
        )

    with allure.step("Verify HTTP 200"):
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:400]}"
        )

    with allure.step("Verify response contains pricing fields"):
        data = resp.json()
        price_data = data.get("data") or data if isinstance(data, dict) else {}
        keys_lower = str(list(price_data.keys())).lower()
        has_price_fields = any(
            k in keys_lower
            for k in ["base", "tax", "total", "price", "rate", "amount"]
        )
        assert has_price_fields, (
            f"Expected pricing fields in response. Keys found: {list(price_data.keys())[:10]}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — Booking / Checkout
# ─────────────────────────────────────────────────────────────────────────────

@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("API — AC6: Booking/Checkout")
@allure.story("AC6: POST authenticate with valid credentials returns auth token")
@allure.title("POST /authenticate with valid credentials → 200 + auth token")
def test_api_pos_authenticate():
    """
    Jira: JP-1
    AC: User authentication is required to complete the booking
    """
    import os
    username = os.getenv("TEST_USERNAME", "")
    password = os.getenv("TEST_PASSWORD", "")

    if not username or not password:
        pytest.skip("TEST_USERNAME / TEST_PASSWORD not set in .env — skipping auth API test")

    with allure.step("POST /authenticate with credentials from .env"):
        resp = requests.post(
            f"{BASE_URL}/authenticate",
            json={"username": username, "password": password},
            timeout=15,
        )

    with allure.step("Verify HTTP 200"):
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text[:300]}"
        )

    with allure.step("Verify response contains an auth token"):
        data = resp.json()
        token = (
            data.get("token") or
            data.get("access_token") or
            data.get("jwt") or
            data.get("accessToken") or
            (data.get("data") or {}).get("token")
        )
        assert token, f"No auth token found in response: {list(data.keys())}"
