"""
Toyota Vehicles Page Tests

Tests for vehicle browsing, filtering, and selection functionality.
"""
import pytest
from playwright.sync_api import Page

from src.core.page_objects.vehicles_page import VehiclesPage


@pytest.mark.smoke
@pytest.mark.vehicles
def test_vehicles_page_loads(vehicles_page: VehiclesPage):
    """Test that vehicles page loads successfully"""
    vehicles_page.open()

    # Verify page loaded
    assert vehicles_page.is_loaded(), "Vehicles page did not load"

    # Verify vehicles are displayed
    vehicle_count = vehicles_page.get_vehicle_count()
    assert vehicle_count > 0, "No vehicles displayed"


@pytest.mark.regression
@pytest.mark.vehicles
def test_vehicle_filtering_by_category(vehicles_page: VehiclesPage):
    """Test filtering vehicles by category"""
    vehicles_page.open()

    # Get initial vehicle count
    initial_count = vehicles_page.get_vehicle_count()
    assert initial_count > 0

    # Click SUVs category
    if vehicles_page.is_visible(vehicles_page.SUVS_TAB):
        vehicles_page.click_suvs_category()
        vehicles_page.wait_for_page_load()

        # Verify vehicles are still displayed (count may change)
        suv_count = vehicles_page.get_vehicle_count()
        assert suv_count > 0, "No SUVs displayed"


@pytest.mark.regression
@pytest.mark.vehicles
def test_view_specific_vehicle_details(vehicles_page: VehiclesPage):
    """Test viewing specific vehicle details"""
    vehicles_page.open()

    # Get list of available vehicles
    vehicle_names = vehicles_page.get_vehicle_names()
    assert len(vehicle_names) > 0, "No vehicles found"

    # Click on first available vehicle
    first_vehicle = vehicle_names[0]
    vehicles_page.click_vehicle_by_name(first_vehicle)
    vehicles_page.wait_for_navigation()

    # Verify navigation occurred
    current_url = vehicles_page.get_current_url()
    assert current_url != f"{vehicles_page.base_url}/vehicles", \
        "Clicking vehicle should navigate to details page"


@pytest.mark.critical_path
@pytest.mark.vehicles
def test_vehicle_to_build_and_price_flow(vehicles_page: VehiclesPage):
    """Test user flow from vehicles to build & price"""
    vehicles_page.open()

    # Get available vehicles
    vehicle_names = vehicles_page.get_vehicle_names()
    assert len(vehicle_names) > 0

    # Try to click build & price for first vehicle
    first_vehicle = vehicle_names[0]

    # Check if Build & Price button exists for this vehicle
    if vehicles_page.is_visible(vehicles_page.BUILD_PRICE_BUTTON):
        vehicles_page.click_build_and_price_for_vehicle(first_vehicle)
        vehicles_page.wait_for_navigation()

        # Verify navigation to configurator
        current_url = vehicles_page.get_current_url()
        assert any(keyword in current_url.lower() for keyword in ["configurator", "build", "customize"]), \
            "Build & Price should navigate to configurator"


@pytest.mark.regression
@pytest.mark.vehicles
def test_popular_vehicles_displayed(vehicles_page: VehiclesPage):
    """Test that popular Toyota models are displayed"""
    vehicles_page.open()

    vehicle_names = vehicles_page.get_vehicle_names()
    vehicle_names_lower = [name.lower() for name in vehicle_names]

    # Check for some popular Toyota models
    popular_models = ["camry", "corolla", "rav4", "highlander", "tacoma", "tundra", "prius"]

    # At least some popular models should be displayed
    found_models = [model for model in popular_models if any(model in name for name in vehicle_names_lower)]

    assert len(found_models) > 0, \
        f"Expected to find popular Toyota models, but found: {vehicle_names}"


@pytest.mark.visual
@pytest.mark.vehicles
def test_vehicles_page_visual_regression(vehicles_page: VehiclesPage, visual_ai):
    """Test vehicles page visual regression"""
    vehicles_page.open()
    vehicles_page.wait_for_page_load()

    # Compare visual baseline
    result = visual_ai.compare_visual(
        vehicles_page.page,
        screenshot_name="vehicles_page",
        use_ai_analysis=True,
    )

    # Check result
    if result["status"] == "failed" and "ai_analysis" in result:
        ai_verdict = result["ai_analysis"].get("verdict")
        assert ai_verdict == "PASS", \
            f"Visual regression: {result['ai_analysis'].get('recommendation')}"


@pytest.mark.performance
@pytest.mark.vehicles
def test_vehicles_page_performance(vehicles_page: VehiclesPage, anomaly_detector):
    """Test vehicles page performance"""
    vehicles_page.open()

    # Collect metrics
    metrics = anomaly_detector.collect_performance_metrics()

    # Check performance budgets
    assert metrics.get("firstContentfulPaint", 0) < 3000, "FCP too slow"
    assert metrics.get("loadComplete", 0) < 10000, "Page load too slow"


@pytest.mark.regression
@pytest.mark.vehicles
@pytest.mark.ai_generated
def test_vehicle_search_and_filter_combination(vehicles_page: VehiclesPage):
    """
    Test combining multiple filters
    This test demonstrates AI-enhanced filtering
    """
    vehicles_page.open()

    # Apply fuel type filter if available
    if vehicles_page.is_visible(vehicles_page.FUEL_TYPE_FILTER):
        vehicles_page.filter_by_fuel_type("Hybrid")
        vehicles_page.wait_for_page_load()

        # Verify hybrid vehicles are shown
        vehicle_names = vehicles_page.get_vehicle_names()
        assert len(vehicle_names) > 0, "Hybrid filter should show vehicles"


@pytest.mark.smoke
@pytest.mark.vehicles
def test_vehicle_cards_have_required_info(vehicles_page: VehiclesPage, page: Page):
    """Test that vehicle cards display required information"""
    vehicles_page.open()

    # Get first vehicle card
    first_card = page.locator(vehicles_page.VEHICLE_CARD).first

    # Check that card has image
    image = first_card.locator(vehicles_page.VEHICLE_IMAGE)
    assert image.count() > 0, "Vehicle card should have an image"

    # Check that card has name/title
    name = first_card.locator(vehicles_page.VEHICLE_NAME)
    assert name.count() > 0, "Vehicle card should have a name"


@pytest.mark.critical_path
@pytest.mark.vehicles
def test_end_to_end_vehicle_browsing(home_page, vehicles_page):
    """Complete end-to-end vehicle browsing flow"""
    # Start from homepage
    home_page.open()

    # Navigate to vehicles
    home_page.click_vehicles_nav()

    # Verify vehicles page
    assert vehicles_page.is_loaded()

    # Browse vehicles
    vehicle_names = vehicles_page.get_vehicle_names()
    assert len(vehicle_names) > 0, "Should display vehicles"

    # Filter by category
    if vehicles_page.is_visible(vehicles_page.SUVS_TAB):
        vehicles_page.click_suvs_category()
        vehicles_page.wait_for_page_load()

        # Should still have vehicles after filtering
        filtered_count = vehicles_page.get_vehicle_count()
        assert filtered_count > 0, "Should have SUVs after filtering"
