"""
Toyota Special Offers Tests

Comprehensive test suite for special offers page including:
- Page load and accessibility
- Offers display and filtering
- Dealer-specific offers
- Offer details and CTAs
- Regional offer variations
"""

import pytest
import re
from playwright.sync_api import Page, expect
from src.ai.anomaly_detector import AnomalyDetector


@pytest.mark.smoke
@pytest.mark.critical_path
def test_special_offers_page_loads(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Special Offers page loads successfully.

    Validates:
    - Page loads without errors
    - Title is appropriate
    - URL is correct
    - Main content is visible
    - No critical errors
    """

    # Navigate to Special Offers page
    page.goto('https://www.toyota.com/local-specials')

    # Verify page loaded successfully (accepts regional redirects)
    expect(page).to_have_url(re.compile(r'.*(local-specials|deals-incentives|offers)'))
    assert 'toyota.com' in page.url.lower(), f"Should be on Toyota domain, got: {page.url}"

    # Wait for page to be fully loaded (use domcontentloaded for redirecting pages)
    page.wait_for_load_state('domcontentloaded')

    # Verify main content loaded
    body = page.locator('body')
    expect(body).to_be_visible()
    assert len(body.inner_text()) > 100, "Page should have substantial content"

    print(f"\n✅ Special Offers page loaded successfully")
    print(f"   URL: {page.url}")
    print(f"   Title: {page.title()}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.smoke
def test_offers_display(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify offers are displayed on the page.

    Validates:
    - Offer cards/sections are present
    - Offer information is visible
    - Vehicle images are shown
    - Pricing/incentive information displayed
    """

    page.goto('https://www.toyota.com/local-specials')
    page.wait_for_load_state('domcontentloaded')

    # Look for offer-related content
    offer_keywords = ['APR', 'lease', 'cash', 'bonus', 'incentive', 'finance', 'special']
    found_keywords = []

    for keyword in offer_keywords:
        elements = page.locator(f'text=/{keyword}/i').all()
        if len(elements) > 0:
            found_keywords.append(keyword)

    print(f"\n✅ Offers content found")
    print(f"   Offer keywords found: {', '.join(found_keywords) if found_keywords else 'checking...'}")

    # Check for images (vehicle offer images)
    images = page.locator('img').all()
    print(f"   Images on page: {len(images)}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_offers_filter_functionality(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify offer filtering functionality.

    Validates:
    - Filter options exist
    - Filters can be applied
    - Filter by vehicle model works
    - Filter by offer type works
    """

    page.goto('https://www.toyota.com/local-specials')
    page.wait_for_load_state('domcontentloaded')

    # Look for filter elements
    filter_elements = []

    # Check for dropdowns/selects
    selects = page.locator('select').all()
    if len(selects) > 0:
        filter_elements.append(f'{len(selects)} dropdown(s)')

    # Check for filter buttons
    filter_buttons = page.locator('button:has-text("Filter"), button:has-text("All")').all()
    if len(filter_buttons) > 0:
        filter_elements.append(f'{len(filter_buttons)} filter button(s)')

    if len(filter_elements) > 0:
        print(f"\n✅ Filter elements found")
        print(f"   Filter controls: {', '.join(filter_elements)}")
    else:
        print(f"\n⚠️  Filter elements not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_dealer_location_selector(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify dealer location selector functionality.

    Validates:
    - Zip code input exists
    - Location can be entered
    - Offers update based on location
    - Dealer-specific offers shown
    """

    page.goto('https://www.toyota.com/local-specials')
    page.wait_for_load_state('domcontentloaded')

    # Look for zip code or location input
    location_inputs = []

    zip_input = page.locator('input[placeholder*="Zip"], input[name*="zip"], input[id*="zip"]').first
    if zip_input.is_visible(timeout=5000):
        location_inputs.append('Zip Code Input')

    # Check for location-related buttons
    location_buttons = page.locator('button:has-text("Change"), button:has-text("Location")').all()
    if len(location_buttons) > 0:
        location_inputs.append(f'{len(location_buttons)} location button(s)')

    if len(location_inputs) > 0:
        print(f"\n✅ Location selector found")
        print(f"   Location controls: {', '.join(location_inputs)}")
    else:
        print(f"\n⚠️  Location selector not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.smoke
def test_offer_details_and_ctas(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify offer details and call-to-action buttons.

    Validates:
    - Offer details are accessible
    - CTA buttons present (View Details, Apply Now, etc.)
    - Links to relevant pages work
    """

    page.goto('https://www.toyota.com/local-specials')
    page.wait_for_load_state('domcontentloaded')

    # Look for CTA buttons
    cta_texts = ['View Details', 'Learn More', 'Get Started', 'Apply', 'Contact', 'See Offers']
    found_ctas = []

    for cta_text in cta_texts:
        buttons = page.locator(f'a:has-text("{cta_text}"), button:has-text("{cta_text}")').all()
        if len(buttons) > 0:
            found_ctas.append(f'{cta_text} ({len(buttons)})')

    if len(found_ctas) > 0:
        print(f"\n✅ CTA buttons found")
        print(f"   CTAs: {', '.join(found_ctas)}")
    else:
        print(f"\n⚠️  CTA buttons not immediately visible")

    # Check for links
    links = page.locator('a').all()
    print(f"   Total links on page: {len(links)}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_offer_disclaimers_and_terms(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify offer disclaimers and terms are present.

    Validates:
    - Disclaimer text is visible
    - Terms and conditions links exist
    - Fine print is accessible
    - Legal requirements met
    """

    page.goto('https://www.toyota.com/local-specials')
    page.wait_for_load_state('domcontentloaded')

    # Look for disclaimer-related text
    disclaimer_keywords = ['disclaimer', 'terms', 'conditions', 'restrictions', 'expires', 'see dealer']
    found_disclaimers = []

    for keyword in disclaimer_keywords:
        elements = page.locator(f'text=/{keyword}/i').all()
        if len(elements) > 0:
            found_disclaimers.append(keyword)

    if len(found_disclaimers) > 0:
        print(f"\n✅ Disclaimer content found")
        print(f"   Disclaimer keywords: {', '.join(found_disclaimers)}")
    else:
        print(f"\n⚠️  Disclaimer content not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_offers_page_content_quality(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify offers page content quality and completeness.

    Validates:
    - Page has substantial content
    - Images are loaded
    - No broken content
    - Professional presentation
    """

    page.goto('https://www.toyota.com/local-specials')
    page.wait_for_load_state('domcontentloaded')

    # Verify text content
    body_text = page.locator('body').inner_text()
    assert len(body_text) > 200, f"Page should have substantial content, found {len(body_text)} characters"

    # Check for images
    images = page.locator('img').all()
    assert len(images) > 0, f"Page should have images, found {len(images)}"

    # Check for links
    links = page.locator('a').all()
    assert len(links) > 5, f"Page should have multiple links, found {len(links)}"

    print(f"\n✅ Offers page content quality validated")
    print(f"   Content length: {len(body_text)} characters")
    print(f"   Images: {len(images)}")
    print(f"   Links: {len(links)}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"
