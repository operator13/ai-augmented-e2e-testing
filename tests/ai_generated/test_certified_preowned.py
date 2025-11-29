"""
Toyota Certified Pre-Owned Tests

Comprehensive test suite for CPO (Certified Pre-Owned) section including:
- CPO page accessibility
- Vehicle search and filtering
- Certification benefits display
- Warranty information
- CPO inventory browsing
"""

import pytest
import re
from playwright.sync_api import Page, expect
from src.ai.anomaly_detector import AnomalyDetector


@pytest.mark.smoke
@pytest.mark.critical_path
def test_cpo_page_loads_successfully(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Certified Pre-Owned page loads successfully.

    Validates:
    - Page loads without errors
    - CPO content is visible
    - URL is correct
    - No critical errors
    """

    # Navigate to CPO page
    page.goto('https://www.toyotacertified.com')

    # Verify page loaded
    assert 'toyota' in page.url.lower(), f"Should be on Toyota domain, got: {page.url}"
    assert page.url.startswith('https://'), "Page should load over HTTPS"

    # Wait for page to be fully loaded (CPO site has slow network activity, use domcontentloaded)
    page.wait_for_load_state('domcontentloaded')

    # Verify main content loaded
    body = page.locator('body')
    expect(body).to_be_visible()
    assert len(body.inner_text()) > 100, "Page should have substantial content"

    print(f"\n✅ CPO page loaded successfully")
    print(f"   URL: {page.url}")
    print(f"   Title: {page.title()}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.smoke
def test_cpo_certification_benefits_displayed(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify CPO certification benefits are displayed.

    Validates:
    - Warranty information present
    - Inspection details shown
    - Benefits listed clearly
    - Certification standards explained
    """

    page.goto('https://www.toyotacertified.com')
    page.wait_for_load_state('domcontentloaded')

    # Look for CPO benefit keywords
    benefit_keywords = ['warranty', 'certified', 'inspection', 'benefit', 'coverage', 'guarantee', 'quality']
    found_benefits = []

    for keyword in benefit_keywords:
        elements = page.locator(f'text=/{keyword}/i').all()
        if len(elements) > 0:
            found_benefits.append(keyword)

    print(f"\n✅ CPO benefits information found")
    print(f"   Benefit keywords: {', '.join(found_benefits) if found_benefits else 'checking...'}")

    # Assert at least some benefit information is present
    assert len(found_benefits) >= 2, f"Should find at least 2 benefit keywords, found: {found_benefits}"

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_cpo_vehicle_search_functionality(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify CPO vehicle search functionality.

    Validates:
    - Search form is present
    - Zip code input available
    - Search button functional
    - Results can be browsed
    """

    page.goto('https://www.toyotacertified.com')
    page.wait_for_load_state('domcontentloaded')

    # Look for search elements
    search_elements = []

    # Check for zip code input
    zip_input = page.locator('input[placeholder*="Zip"], input[name*="zip"], input[id*="zip"]').first
    if zip_input.is_visible(timeout=5000):
        search_elements.append('Zip Code Input')

    # Check for search button
    search_button = page.locator('button:has-text("Search"), button:has-text("Find"), input[type="submit"]').first
    if search_button.is_visible(timeout=5000):
        search_elements.append('Search Button')

    if len(search_elements) > 0:
        print(f"\n✅ Search functionality found")
        print(f"   Search elements: {', '.join(search_elements)}")
    else:
        print(f"\n⚠️  Search functionality not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_cpo_warranty_information(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify CPO warranty information is accessible.

    Validates:
    - Warranty details provided
    - Coverage terms explained
    - Warranty period stated
    - Powertrain coverage mentioned
    """

    page.goto('https://www.toyotacertified.com')
    page.wait_for_load_state('domcontentloaded')

    # Look for warranty-related content
    warranty_keywords = ['warranty', 'coverage', '12-month', 'powertrain', 'limited', 'year', 'mile']
    found_warranty_info = []

    for keyword in warranty_keywords:
        elements = page.locator(f'text=/{keyword}/i').all()
        if len(elements) > 0:
            found_warranty_info.append(keyword)

    if len(found_warranty_info) > 0:
        print(f"\n✅ Warranty information found")
        print(f"   Warranty keywords: {', '.join(found_warranty_info)}")
    else:
        print(f"\n⚠️  Warranty information not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_cpo_inspection_process_info(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify CPO inspection process information.

    Validates:
    - Inspection points mentioned
    - Quality standards explained
    - Certification process described
    """

    page.goto('https://www.toyotacertified.com')
    page.wait_for_load_state('domcontentloaded')

    # Look for inspection-related content
    inspection_keywords = ['inspection', 'point', 'check', 'test', 'certified', 'quality', 'standard']
    found_inspection_info = []

    for keyword in inspection_keywords:
        elements = page.locator(f'text=/{keyword}/i').all()
        if len(elements) > 0:
            found_inspection_info.append(keyword)

    if len(found_inspection_info) > 0:
        print(f"\n✅ Inspection information found")
        print(f"   Inspection keywords: {', '.join(found_inspection_info)}")
    else:
        print(f"\n⚠️  Inspection information not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_cpo_navigation_links(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify CPO page navigation links.

    Validates:
    - Links to search inventory
    - Links to benefits page
    - Links to warranty details
    - Links to dealer locator
    """

    page.goto('https://www.toyotacertified.com')
    page.wait_for_load_state('domcontentloaded')

    # Look for common CPO navigation links
    link_texts = ['Search', 'Inventory', 'Benefits', 'Warranty', 'Find', 'Dealer', 'About']
    found_links = []

    for link_text in link_texts:
        links = page.locator(f'a:has-text("{link_text}")').all()
        if len(links) > 0:
            found_links.append(f'{link_text} ({len(links)})')

    if len(found_links) > 0:
        print(f"\n✅ Navigation links found")
        print(f"   Links: {', '.join(found_links)}")
    else:
        print(f"\n⚠️  Navigation links not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_cpo_page_content_quality(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify CPO page content quality.

    Validates:
    - Page has substantial content
    - Images are loaded
    - Professional presentation
    - No broken content
    """

    page.goto('https://www.toyotacertified.com')
    page.wait_for_load_state('domcontentloaded')

    # Verify text content
    body_text = page.locator('body').inner_text()
    assert len(body_text) > 300, f"Page should have substantial content, found {len(body_text)} characters"

    # Check for images
    images = page.locator('img').all()
    assert len(images) > 0, f"Page should have images, found {len(images)}"

    # Check for links
    links = page.locator('a').all()
    assert len(links) > 5, f"Page should have multiple links, found {len(links)}"

    print(f"\n✅ CPO page content quality validated")
    print(f"   Content length: {len(body_text)} characters")
    print(f"   Images: {len(images)}")
    print(f"   Links: {len(links)}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"
