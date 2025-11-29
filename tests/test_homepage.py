"""
Toyota Homepage Tests

Tests for toyota.com homepage functionality including:
- Page load and navigation
- Hero section and carousel
- Main navigation
- Featured vehicles
- Visual regression
"""
import pytest
from playwright.sync_api import Page

from src.ai.visual_ai import VisualAI
from src.core.page_objects.homepage import HomePage


@pytest.mark.smoke
@pytest.mark.homepage
def test_homepage_loads_successfully(home_page: HomePage):
    """Test that homepage loads successfully"""
    # Navigate to homepage
    home_page.open()

    # Verify page loaded
    assert home_page.is_loaded(), "Homepage did not load successfully"

    # Verify URL
    assert "toyota.com" in home_page.get_current_url()

    # Verify title
    assert "Toyota" in home_page.get_title()


@pytest.mark.smoke
@pytest.mark.homepage
def test_homepage_navigation_visible(home_page: HomePage):
    """Test that main navigation is visible and functional"""
    home_page.open()

    # Verify navigation elements are visible
    home_page.verify_navigation_visible()
    home_page.verify_logo_visible()


@pytest.mark.smoke
@pytest.mark.homepage
def test_hero_section_displayed(home_page: HomePage):
    """Test that hero section is displayed"""
    home_page.open()

    # Verify hero section is visible
    home_page.verify_hero_section_visible()


@pytest.mark.regression
@pytest.mark.homepage
def test_navigation_links_functional(home_page: HomePage):
    """Test that navigation links are functional"""
    home_page.open()

    # Test Vehicles link
    home_page.click_vehicles_nav()
    home_page.wait_for_navigation()
    assert "/vehicles" in home_page.get_current_url() or "vehicle" in home_page.get_current_url().lower()

    # Go back to homepage
    home_page.open()

    # Test Shopping Tools link (if available)
    if home_page.is_visible(home_page.SHOPPING_TOOLS_LINK):
        home_page.click_shopping_tools()
        home_page.wait_for_navigation()


@pytest.mark.regression
@pytest.mark.homepage
def test_special_offers_section(home_page: HomePage):
    """Test special offers section"""
    home_page.open()

    # Scroll to and verify special offers section
    if home_page.is_visible(home_page.SPECIAL_OFFERS_SECTION):
        home_page.verify_special_offers_section_visible()


@pytest.mark.visual
@pytest.mark.homepage
def test_homepage_visual_regression(home_page: HomePage, visual_ai: VisualAI):
    """Test homepage visual regression"""
    home_page.open()

    # Wait for page to be fully loaded
    home_page.wait_for_page_load()

    # Take screenshot and compare with baseline
    result = visual_ai.compare_visual(
        home_page.page,
        screenshot_name="homepage",
        use_ai_analysis=True,
    )

    # Check if visual differences are acceptable
    if result["status"] == "failed":
        # If AI analysis is available, check verdict
        if "ai_analysis" in result:
            ai_verdict = result["ai_analysis"].get("verdict")
            assert ai_verdict == "PASS", (
                f"Visual regression detected: {result['diff_percentage']}%. "
                f"AI Analysis: {result['ai_analysis'].get('recommendation', 'No recommendation')}"
            )
        else:
            # Fallback to threshold check
            assert result["diff_percentage"] <= result["threshold"], (
                f"Visual regression detected: {result['diff_percentage']}% exceeds threshold"
            )


@pytest.mark.performance
@pytest.mark.homepage
def test_homepage_performance(home_page: HomePage, anomaly_detector):
    """Test homepage performance metrics"""
    home_page.open()

    # Collect performance metrics
    metrics = anomaly_detector.collect_performance_metrics()

    # Assert performance budgets
    assert metrics.get("firstContentfulPaint", 0) < 3000, "FCP exceeds 3 seconds"
    assert metrics.get("loadComplete", 0) < 10000, "Page load exceeds 10 seconds"


@pytest.mark.regression
@pytest.mark.homepage
def test_build_and_price_cta(home_page: HomePage):
    """Test Build & Price call-to-action"""
    home_page.open()

    # Check if Build & Price CTA is visible
    if home_page.is_visible(home_page.BUILD_PRICE_CTA):
        home_page.click_build_and_price()
        home_page.wait_for_navigation()

        # Verify navigation to configurator or build page
        current_url = home_page.get_current_url()
        assert any(keyword in current_url.lower() for keyword in ["configurator", "build", "customize"]), \
            "Build & Price CTA did not navigate to expected page"


@pytest.mark.smoke
@pytest.mark.homepage
@pytest.mark.accessibility
def test_homepage_accessibility_basics(home_page: HomePage, page: Page):
    """Test basic accessibility requirements"""
    home_page.open()

    # Check for main landmark
    main_landmark = page.locator("main, [role='main']")
    assert main_landmark.count() > 0, "Page should have a main landmark"

    # Check for navigation landmark
    nav_landmark = page.locator("nav, [role='navigation']")
    assert nav_landmark.count() > 0, "Page should have navigation landmark"

    # Check that logo has alt text or aria-label
    logo = page.locator(home_page.LOGO)
    if logo.count() > 0:
        # Either img should have alt or link should have aria-label
        img = logo.locator("img")
        if img.count() > 0:
            alt_text = img.get_attribute("alt")
            aria_label = logo.get_attribute("aria-label")
            assert alt_text or aria_label, "Logo should have alt text or aria-label"


@pytest.mark.regression
@pytest.mark.homepage
def test_featured_vehicles_displayed(home_page: HomePage):
    """Test that featured vehicles are displayed"""
    home_page.open()

    # Check if featured vehicles section exists
    if home_page.is_visible(home_page.FEATURED_VEHICLES):
        vehicle_count = home_page.get_featured_vehicle_count()
        assert vehicle_count > 0, "Featured vehicles section should display at least one vehicle"


@pytest.mark.critical_path
@pytest.mark.homepage
def test_homepage_to_vehicles_flow(home_page: HomePage, vehicles_page):
    """Test critical user flow from homepage to vehicles page"""
    # Start at homepage
    home_page.open()
    assert home_page.is_loaded()

    # Navigate to vehicles
    home_page.click_vehicles_nav()

    # Verify vehicles page loaded
    vehicles_page.wait_for_page_load()
    assert vehicles_page.is_loaded(), "Vehicles page did not load"

    # Verify vehicles are displayed
    vehicle_count = vehicles_page.get_vehicle_count()
    assert vehicle_count > 0, "No vehicles displayed on vehicles page"
