import pytest
import allure
import requests

from config.settings import settings


API_BASE = settings.API_BASE_URL
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking — API")
class TestAPILocations:

    @allure.story("AC1: Location Selection — API")
    @allure.title("API-TC1: GET available locations returns serviceable list")
    def test_api_pos_get_available_locations(self):
        """
        Jira: JP-1
        AC: AC1 — Location list comes from /location/available-locations/open
        """
        with allure.step("GET /location/available-locations/open"):
            response = requests.get(
                f"{API_BASE}/location/available-locations/open",
                headers=HEADERS,
                timeout=settings.TIMEOUT // 1000,
            )

        with allure.step("Verify 200 status"):
            assert response.status_code == 200, (
                f"Expected 200, got {response.status_code}: {response.text[:200]}"
            )

        with allure.step("Verify response contains locations"):
            data = response.json()
            assert data, "Response body must not be empty"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking — API")
class TestAPIAvailableCars:

    @allure.story("AC3: Vehicle Search — API")
    @allure.title("API-TC2: POST available cars returns results for serviceable location")
    def test_api_pos_get_available_cars(self):
        """
        Jira: JP-1
        AC: AC3 — POST /car/availableCarsV4/open returns vehicles for Bronx NY
        """
        payload = {
            "pickupLocation": "Bronx, NY",
            "dropLocation": "Bronx, NY",
        }

        with allure.step("POST /car/availableCarsV4/open"):
            response = requests.post(
                f"{API_BASE}/car/availableCarsV4/open",
                json=payload,
                headers=HEADERS,
                timeout=settings.TIMEOUT // 1000,
            )

        with allure.step("Verify 200 status"):
            assert response.status_code == 200, (
                f"Expected 200, got {response.status_code}: {response.text[:200]}"
            )

        with allure.step("Verify at least one car in response"):
            data = response.json()
            assert data, "Response must contain at least one vehicle"

    @allure.story("AC3: Vehicle Search — API")
    @allure.title("API-TC3: POST available cars returns empty for unserviceable location")
    def test_api_err_cars_no_location(self):
        """
        Jira: JP-1
        AC: AC3 — No vehicles returned for Seattle WA (outside service area)
        """
        payload = {
            "pickupLocation": "Seattle, WA",
            "dropLocation": "Seattle, WA",
        }

        with allure.step("POST /car/availableCarsV4/open with unserviceable location"):
            response = requests.post(
                f"{API_BASE}/car/availableCarsV4/open",
                json=payload,
                headers=HEADERS,
                timeout=settings.TIMEOUT // 1000,
            )

        with allure.step("Verify response indicates no results (200 with empty list or 4xx)"):
            if response.status_code == 200:
                data = response.json()
                assert not data or (isinstance(data, list) and len(data) == 0), (
                    "Expected empty list for unserviceable location"
                )
            else:
                assert response.status_code in (400, 404, 422), (
                    f"Unexpected status {response.status_code}"
                )


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking — API")
class TestAPICarDetail:

    @allure.story("AC4: Vehicle Selection — API")
    @allure.title("API-TC4: GET available car filters returns filter options")
    def test_api_pos_car_detail(self):
        """
        Jira: JP-1
        AC: AC3/AC4 — GET /car/getCarFilter returns filter metadata (Type, Brand, Model, Price)
        """
        with allure.step("GET /car/getCarFilter"):
            response = requests.get(
                f"{API_BASE}/car/getCarFilter",
                headers=HEADERS,
                timeout=settings.TIMEOUT // 1000,
            )

        with allure.step("Verify 200 status"):
            assert response.status_code == 200, (
                f"Expected 200, got {response.status_code}: {response.text[:200]}"
            )

        with allure.step("Verify filter data is returned"):
            data = response.json()
            assert data, "Car filter response must not be empty"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking — API")
class TestAPIEstimatedPrice:

    @allure.story("AC5: Pricing Details — API")
    @allure.title("API-TC5: POST estimated price returns pricing breakdown")
    def test_api_pos_estimated_price(self):
        """
        Jira: JP-1
        AC: AC5 — POST /booking/estimatedPrice/open returns base rate, taxes, total
        """
        payload = {
            "pickupLocation": "Bronx, NY",
            "dropLocation": "Bronx, NY",
        }

        with allure.step("POST /booking/estimatedPrice/open"):
            response = requests.post(
                f"{API_BASE}/booking/estimatedPrice/open",
                json=payload,
                headers=HEADERS,
                timeout=settings.TIMEOUT // 1000,
            )

        with allure.step("Verify 200 status"):
            assert response.status_code == 200, (
                f"Expected 200, got {response.status_code}: {response.text[:200]}"
            )

        with allure.step("Verify pricing data in response"):
            data = response.json()
            assert data, "Estimated price response must not be empty"


@allure.epic("JP-1: Pre Payment Booking Flow")
@allure.feature("booking — API")
class TestAPIAuthenticate:

    @allure.story("AC6: Booking/Checkout — API")
    @allure.title("API-TC6: POST authenticate returns 401 for invalid credentials")
    def test_api_pos_authenticate(self):
        """
        Jira: JP-1
        AC: AC6 — POST /authenticate rejects invalid credentials with 401
        """
        payload = {
            "email": "invalid@example.com",
            "password": "wrong_password_test",
        }

        with allure.step("POST /authenticate with invalid credentials"):
            response = requests.post(
                f"{API_BASE}/authenticate",
                json=payload,
                headers=HEADERS,
                timeout=settings.TIMEOUT // 1000,
            )

        with allure.step("Verify 401 Unauthorized or appropriate error status"):
            assert response.status_code in (401, 400, 403), (
                f"Expected auth failure (401/400/403), got {response.status_code}"
            )
