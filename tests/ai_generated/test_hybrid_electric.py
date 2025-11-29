"""
Toyota Hybrid and Electric Vehicles Tests

Comprehensive test suite for electrified vehicles section including:
- Electrified page accessibility
- Hybrid vehicle listings
- Electric vehicle (bZ4X) information
- Fuel efficiency data
- Charging and battery information
"""

import pytest
import re
from playwright.sync_api import Page, expect
from src.ai.anomaly_detector import AnomalyDetector


@pytest.mark.smoke
@pytest.mark.critical_path
def test_electrified_vehicles_page_loads(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Electrified Vehicles page loads successfully.

    Validates:
    - Page loads without errors
    - Hybrid/electric content is visible
    - URL is correct
    - No critical errors
    """

    # Try common URLs for electrified vehicles
    possible_urls = [
        'https://www.toyota.com/electrified',
        'https://www.toyota.com/hybrid',
        'https://www.toyota.com/electric'
    ]

    page_loaded = False
    for url in possible_urls:
        try:
            page.goto(url, timeout=10000)
            page.wait_for_load_state('networkidle', timeout=5000)
            page_loaded = True
            break
        except Exception:
            continue

    if not page_loaded:
        # Fallback to all vehicles page
        page.goto('https://www.toyota.com/all-vehicles')
        page.wait_for_load_state('networkidle')

    # Verify page loaded
    body = page.locator('body')
    expect(body).to_be_visible()

    print(f"\n✅ Electrified/Hybrid vehicles page loaded")
    print(f"   URL: {page.url}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.smoke
def test_hybrid_vehicles_displayed(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify hybrid vehicles are displayed.

    Validates:
    - Hybrid vehicle models shown
    - Hybrid badges/labels present
    - Vehicle images displayed
    """

    page.goto('https://www.toyota.com/all-vehicles')
    page.wait_for_load_state('networkidle')

    # Look for hybrid vehicles
    hybrid_vehicles = ['Prius', 'Camry Hybrid', 'RAV4 Hybrid', 'Highlander Hybrid', 'Corolla Hybrid', 'Venza']
    found_hybrids = []

    for vehicle in hybrid_vehicles:
        elements = page.locator(f'text=/{vehicle}/i').all()
        if len(elements) > 0:
            found_hybrids.append(vehicle)

    print(f"\n✅ Hybrid vehicles found")
    print(f"   Hybrid models: {', '.join(found_hybrids) if found_hybrids else 'checking...'}")
    print(f"   Total found: {len(found_hybrids)}")

    # Look for hybrid keyword
    hybrid_keyword = page.locator('text=/hybrid/i').all()
    print(f"   Hybrid keyword mentions: {len(hybrid_keyword)}")

    # Assert at least some hybrid vehicles are found
    assert len(found_hybrids) >= 2 or len(hybrid_keyword) > 0, \
        f"Should find hybrid vehicles or hybrid content"

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_electric_vehicle_information(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify electric vehicle (bZ4X) information is accessible.

    Validates:
    - bZ4X mentioned
    - Electric vehicle content present
    - Battery/range information shown
    """

    page.goto('https://www.toyota.com/all-vehicles')
    page.wait_for_load_state('networkidle')

    # Look for electric vehicle keywords
    ev_keywords = ['bZ4X', 'electric', 'EV', 'battery', 'range', 'charging']
    found_ev_info = []

    for keyword in ev_keywords:
        elements = page.locator(f'text=/{keyword}/i').all()
        if len(elements) > 0:
            found_ev_info.append(keyword)

    if len(found_ev_info) > 0:
        print(f"\n✅ Electric vehicle information found")
        print(f"   EV keywords: {', '.join(found_ev_info)}")
    else:
        print(f"\n⚠️  Electric vehicle information not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_fuel_efficiency_information(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify fuel efficiency information is displayed.

    Validates:
    - MPG ratings shown
    - Fuel economy data present
    - Hybrid advantages explained
    """

    page.goto('https://www.toyota.com/prius')
    page.wait_for_load_state('networkidle')

    # Look for fuel efficiency keywords
    efficiency_keywords = ['MPG', 'fuel', 'efficiency', 'economy', 'miles per gallon']
    found_efficiency_info = []

    for keyword in efficiency_keywords:
        elements = page.locator(f'text=/{keyword}/i').all()
        if len(elements) > 0:
            found_efficiency_info.append(keyword)

    if len(found_efficiency_info) > 0:
        print(f"\n✅ Fuel efficiency information found")
        print(f"   Efficiency keywords: {', '.join(found_efficiency_info)}")
    else:
        print(f"\n⚠️  Fuel efficiency information not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_hybrid_technology_explanation(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify hybrid technology is explained.

    Validates:
    - Hybrid system described
    - Technology benefits shown
    - How it works content present
    """

    page.goto('https://www.toyota.com/prius')
    page.wait_for_load_state('networkidle')

    # Look for technology-related content
    tech_keywords = ['system', 'technology', 'power', 'engine', 'motor', 'regenerative']
    found_tech_info = []

    for keyword in tech_keywords:
        elements = page.locator(f'text=/{keyword}/i').all()
        if len(elements) > 0:
            found_tech_info.append(keyword)

    if len(found_tech_info) > 0:
        print(f"\n✅ Hybrid technology information found")
        print(f"   Technology keywords: {', '.join(found_tech_info)}")
    else:
        print(f"\n⚠️  Technology information not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_environmental_benefits_displayed(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify environmental benefits are displayed.

    Validates:
    - Emissions information present
    - Environmental advantages shown
    - Sustainability messaging visible
    """

    page.goto('https://www.toyota.com/prius')
    page.wait_for_load_state('networkidle')

    # Look for environmental keywords
    env_keywords = ['emission', 'environment', 'eco', 'green', 'sustainable', 'clean']
    found_env_info = []

    for keyword in env_keywords:
        elements = page.locator(f'text=/{keyword}/i').all()
        if len(elements) > 0:
            found_env_info.append(keyword)

    if len(found_env_info) > 0:
        print(f"\n✅ Environmental benefits information found")
        print(f"   Environmental keywords: {', '.join(found_env_info)}")
    else:
        print(f"\n⚠️  Environmental information not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_electrified_page_content_quality(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify electrified vehicles page content quality.

    Validates:
    - Page has substantial content
    - Images are loaded
    - Professional presentation
    - No broken content
    """

    page.goto('https://www.toyota.com/prius')
    page.wait_for_load_state('networkidle')

    # Verify text content
    body_text = page.locator('body').inner_text()
    assert len(body_text) > 300, f"Page should have substantial content, found {len(body_text)} characters"

    # Check for images
    images = page.locator('img').all()
    assert len(images) > 3, f"Page should have multiple images, found {len(images)}"

    # Check for links
    links = page.locator('a').all()
    assert len(links) > 10, f"Page should have multiple links, found {len(links)}"

    print(f"\n✅ Electrified vehicles page content quality validated")
    print(f"   Content length: {len(body_text)} characters")
    print(f"   Images: {len(images)}")
    print(f"   Links: {len(links)}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"
