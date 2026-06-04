from playwright.sync_api import Page, APIResponse
from typing import Dict, Any, Optional
import allure

from pages.base_page import BasePage


class AvailableCarsApiPage(BasePage):
    """Page object for the Available Cars API endpoint."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.base_url = "https://beta.drivejoulez.com:8443"
        self.endpoint = "/joulez-beta-service/car/availableCarsV4/open"
        self.full_url = f"{self.base_url}{self.endpoint}"

    @allure.step("Get available cars")
    def get_available_cars(
        self,
        pickup_location: Optional[str] = None,
        dropoff_location: Optional[str] = None,
        pickup_date: Optional[str] = None,
        dropoff_date: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> APIResponse:
        params: Dict[str, Any] = {}
        if pickup_location:
            params["pickupLocation"] = pickup_location
        if dropoff_location:
            params["dropoffLocation"] = dropoff_location
        if pickup_date:
            params["pickupDate"] = pickup_date
        if dropoff_date:
            params["dropoffDate"] = dropoff_date
        if filters:
            params.update(filters)
        return self.page.request.get(self.full_url, params=params)

    @allure.step("Validate response status: expected {expected_status}")
    def validate_response_status(self, response: APIResponse, expected_status: int = 200) -> bool:
        return response.status == expected_status

    @allure.step("Parse response JSON")
    def get_response_json(self, response: APIResponse) -> Dict[str, Any]:
        return response.json()

    @allure.step("Validate car data structure")
    def validate_car_data_structure(self, car_data: Dict[str, Any]) -> bool:
        required_fields = ["id", "brand", "model", "type", "price"]
        return all(field in car_data for field in required_fields)

    @allure.step("Filter cars by brand: {brand}")
    def filter_cars_by_brand(self, cars: list, brand: str) -> list:
        return [car for car in cars if car.get("brand", "").lower() == brand.lower()]

    @allure.step("Filter cars by type: {vehicle_type}")
    def filter_cars_by_type(self, cars: list, vehicle_type: str) -> list:
        return [car for car in cars if car.get("type", "").lower() == vehicle_type.lower()]

    @allure.step("Filter cars by price range: {min_price}–{max_price}")
    def filter_cars_by_price_range(self, cars: list, min_price: float, max_price: float) -> list:
        return [
            car for car in cars
            if min_price <= float(car.get("price", 0)) <= max_price
        ]

    @allure.step("Get car count from response")
    def get_car_count(self, response_data: Dict[str, Any]) -> int:
        if "cars" in response_data:
            return len(response_data["cars"])
        if "data" in response_data and isinstance(response_data["data"], list):
            return len(response_data["data"])
        if isinstance(response_data, list):
            return len(response_data)
        return 0

    @allure.step("Validate location filter: {expected_location}")
    def validate_location_filter(self, cars: list, expected_location: str) -> bool:
        return all(
            expected_location.lower() in car.get("location", "").lower()
            for car in cars
        )
