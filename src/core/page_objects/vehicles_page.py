"""
Toyota Vehicles Page Object
"""
from typing import List

from playwright.sync_api import Page, expect

from src.core.page_objects.base_page import BasePage


class VehiclesPage(BasePage):
    """Toyota vehicles browsing page object"""

    # Selectors
    VEHICLE_GRID = "[data-testid='vehicle-grid'], [class*='vehicle-grid'], .vehicles-container"
    VEHICLE_CARD = "[class*='vehicle-card'], .vehicle-tile, [data-component='vehicle-card']"
    VEHICLE_FILTER = "[data-testid='filter'], aside[class*='filter'], .filters"
    BODY_TYPE_FILTER = "select[name*='bodyType'], [aria-label*='Body Type']"
    PRICE_FILTER = "select[name*='price'], [aria-label*='Price']"
    FUEL_TYPE_FILTER = "select[name*='fuel'], [aria-label*='Fuel Type']"

    # Vehicle details
    VEHICLE_NAME = "[class*='vehicle-name'], h3, [class*='model-name']"
    VEHICLE_PRICE = "[class*='price'], .price, [data-testid='price']"
    VEHICLE_IMAGE = "[class*='vehicle-image'] img, .vehicle img"
    VIEW_DETAILS_BUTTON = "a:has-text('View Details'), button:has-text('Details'), [class*='details-link']"
    BUILD_PRICE_BUTTON = "a:has-text('Build & Price'), button:has-text('Configure'), [href*='configurator']"

    # Categories
    CARS_TAB = "button:has-text('Cars'), a:has-text('Cars'), [data-category='cars']"
    TRUCKS_TAB = "button:has-text('Trucks'), a:has-text('Trucks'), [data-category='trucks']"
    SUVS_TAB = "button:has-text('SUVs'), a:has-text('SUVs'), [data-category='suvs']"
    HYBRIDS_TAB = "button:has-text('Hybrids'), a:has-text('Hybrids'), [data-category='hybrids']"

    def __init__(self, page: Page):
        super().__init__(page)

    def open(self):
        """Navigate to vehicles page"""
        self.navigate("/vehicles")

    def is_loaded(self) -> bool:
        """Check if vehicles page is loaded"""
        try:
            self.wait_for_selector(self.VEHICLE_GRID, timeout=10000)
            return True
        except Exception:
            return False

    def get_vehicle_count(self) -> int:
        """Get number of vehicles displayed"""
        self.wait_for_selector(self.VEHICLE_CARD)
        return self.page.locator(self.VEHICLE_CARD).count()

    def filter_by_body_type(self, body_type: str):
        """
        Filter vehicles by body type

        Args:
            body_type: Body type (e.g., 'SUV', 'Sedan', 'Truck')
        """
        if self.is_visible(self.BODY_TYPE_FILTER):
            self.select_dropdown(self.BODY_TYPE_FILTER, body_type)
        else:
            # Try clicking category tabs
            if "suv" in body_type.lower():
                self.click(self.SUVS_TAB)
            elif "truck" in body_type.lower():
                self.click(self.TRUCKS_TAB)
            elif "car" in body_type.lower() or "sedan" in body_type.lower():
                self.click(self.CARS_TAB)

    def filter_by_price(self, price_range: str):
        """
        Filter vehicles by price range

        Args:
            price_range: Price range (e.g., 'Under $30K', '$30K-$40K')
        """
        if self.is_visible(self.PRICE_FILTER):
            self.select_dropdown(self.PRICE_FILTER, price_range)

    def filter_by_fuel_type(self, fuel_type: str):
        """
        Filter vehicles by fuel type

        Args:
            fuel_type: Fuel type (e.g., 'Hybrid', 'Electric', 'Gasoline')
        """
        if self.is_visible(self.FUEL_TYPE_FILTER):
            self.select_dropdown(self.FUEL_TYPE_FILTER, fuel_type)
        elif "hybrid" in fuel_type.lower():
            if self.is_visible(self.HYBRIDS_TAB):
                self.click(self.HYBRIDS_TAB)

    def click_vehicle_by_name(self, vehicle_name: str):
        """
        Click on a specific vehicle by name

        Args:
            vehicle_name: Vehicle model name (e.g., 'Camry', 'RAV4')
        """
        vehicle_locator = self.page.locator(f"{self.VEHICLE_CARD}:has-text('{vehicle_name}')")
        vehicle_locator.first.click()

    def get_vehicle_names(self) -> List[str]:
        """
        Get list of all displayed vehicle names

        Returns:
            List of vehicle names
        """
        self.wait_for_selector(self.VEHICLE_NAME)
        names = self.page.locator(self.VEHICLE_NAME).all_text_contents()
        return [name.strip() for name in names if name.strip()]

    def click_build_and_price_for_vehicle(self, vehicle_name: str):
        """
        Click build & price for a specific vehicle

        Args:
            vehicle_name: Vehicle model name
        """
        vehicle_card = self.page.locator(f"{self.VEHICLE_CARD}:has-text('{vehicle_name}')")
        build_button = vehicle_card.locator(self.BUILD_PRICE_BUTTON)
        build_button.first.click()

    def verify_vehicle_displayed(self, vehicle_name: str):
        """
        Verify a specific vehicle is displayed

        Args:
            vehicle_name: Vehicle model name
        """
        vehicle = self.page.locator(f"{self.VEHICLE_CARD}:has-text('{vehicle_name}')")
        expect(vehicle.first).to_be_visible()

    def get_vehicle_starting_price(self, vehicle_name: str) -> str:
        """
        Get starting price for a vehicle

        Args:
            vehicle_name: Vehicle model name

        Returns:
            Price string
        """
        vehicle_card = self.page.locator(f"{self.VEHICLE_CARD}:has-text('{vehicle_name}')")
        price_element = vehicle_card.locator(self.VEHICLE_PRICE)
        return price_element.first.text_content() or ""

    def scroll_to_vehicle(self, vehicle_name: str):
        """
        Scroll to a specific vehicle

        Args:
            vehicle_name: Vehicle model name
        """
        vehicle = self.page.locator(f"{self.VEHICLE_CARD}:has-text('{vehicle_name}')")
        vehicle.first.scroll_into_view_if_needed()

    def verify_filters_visible(self):
        """Verify filter section is visible"""
        expect(self.page.locator(self.VEHICLE_FILTER).first).to_be_visible()

    def click_cars_category(self):
        """Click cars category tab"""
        self.click(self.CARS_TAB)

    def click_trucks_category(self):
        """Click trucks category tab"""
        self.click(self.TRUCKS_TAB)

    def click_suvs_category(self):
        """Click SUVs category tab"""
        self.click(self.SUVS_TAB)

    def click_hybrids_category(self):
        """Click hybrids category tab"""
        self.click(self.HYBRIDS_TAB)
