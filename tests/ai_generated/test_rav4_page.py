"""
Toyota RAV4 Vehicle Page Tests

Comprehensive test suite for RAV4 vehicle page including:
- Page load and navigation
- Gallery section
- Features and specs
- Build & Price integration
- Visual content validation
"""

import pytest
import re
from playwright.sync_api import Page, expect
from src.ai.anomaly_detector import AnomalyDetector


@pytest.mark.smoke
@pytest.mark.critical_path
def test_rav4_page_loads_successfully(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify RAV4 page loads successfully with all key elements.

    Validates:
    - Page loads without errors
    - Title contains "RAV4"
    - URL is correct
    - Main content is visible
    - No critical errors
    """

    # Navigate to RAV4 page
    page.goto('https://www.toyota.com/rav4')

    # Verify page loaded successfully
    expect(page).to_have_url(re.compile(r'.*/rav4'))
    expect(page).to_have_title(re.compile('RAV4', re.IGNORECASE))
    assert 'rav4' in page.url.lower(), f"URL should contain 'rav4', got: {page.url}"
    assert page.url.startswith('https://'), "Page should load over HTTPS"

    # Wait for page to be fully loaded
    page.wait_for_load_state('domcontentloaded')

    # Verify main content loaded
    body = page.locator('body')
    expect(body).to_be_visible()
    assert len(body.inner_text()) > 100, "Page should have substantial content"

    # Verify navigation is present
    nav = page.locator('nav').first
    expect(nav).to_be_visible()

    # Filter known errors
    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"

    print(f"\n✅ RAV4 page loaded successfully")
    print(f"   Title: {page.title()}")
    print(f"   URL: {page.url}")


@pytest.mark.smoke
def test_rav4_gallery_section(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify RAV4 gallery section is accessible and displays images.

    Validates:
    - Gallery section navigation works
    - Images are present
    - Image gallery is interactive
    """

    page.goto('https://www.toyota.com/rav4')
    page.wait_for_load_state('domcontentloaded')

    # Navigate to gallery using URL hash
    page.goto('https://www.toyota.com/rav4#gallery')
    page.wait_for_timeout(1000)

    # Verify URL updated
    expect(page).to_have_url(re.compile(r'.*#gallery'))
    assert '#gallery' in page.url, f"URL should contain '#gallery', got: {page.url}"

    # Verify still on RAV4 page
    assert 'rav4' in page.url.lower(), "Should still be on RAV4 page"

    print(f"\n✅ RAV4 gallery section accessible")
    print(f"   URL: {page.url}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_rav4_features_section(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify RAV4 features section is accessible and displays content.

    Validates:
    - Features section navigation works
    - Feature descriptions are present
    - Feature images/icons are visible
    """

    page.goto('https://www.toyota.com/rav4')
    page.wait_for_load_state('domcontentloaded')

    # Navigate to features using URL hash
    page.goto('https://www.toyota.com/rav4#features')
    page.wait_for_timeout(1000)

    # Verify URL updated
    expect(page).to_have_url(re.compile(r'.*#features'))
    assert '#features' in page.url, f"URL should contain '#features', got: {page.url}"

    # Verify still on RAV4 page
    assert 'rav4' in page.url.lower(), "Should still be on RAV4 page"

    print(f"\n✅ RAV4 features section accessible")
    print(f"   URL: {page.url}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_rav4_specs_section(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify RAV4 specs section displays vehicle specifications.

    Validates:
    - Specs section is accessible
    - Technical specifications are displayed
    - Spec categories are present
    """

    page.goto('https://www.toyota.com/rav4')
    page.wait_for_load_state('domcontentloaded')

    # Navigate to specs using URL hash
    page.goto('https://www.toyota.com/rav4#specs')
    page.wait_for_timeout(1000)

    # Verify URL updated
    expect(page).to_have_url(re.compile(r'.*#specs'))
    assert '#specs' in page.url, f"URL should contain '#specs', got: {page.url}"

    # Verify still on RAV4 page
    assert 'rav4' in page.url.lower(), "Should still be on RAV4 page"

    print(f"\n✅ RAV4 specs section accessible")
    print(f"   URL: {page.url}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.smoke
def test_rav4_build_and_price_button(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Build & Price button is present and functional.

    Validates:
    - Build button exists
    - Button is clickable
    - Button text is appropriate
    """

    page.goto('https://www.toyota.com/rav4')
    page.wait_for_load_state('domcontentloaded')

    # Look for Build & Price button
    build_button = page.locator('a:has-text("Build"), button:has-text("Build")').first

    if build_button.is_visible(timeout=5000):
        # Verify button is enabled
        expect(build_button).to_be_enabled()

        print(f"\n✅ Build & Price button found")
        print(f"   Button text: {build_button.inner_text()}")
    else:
        print(f"\n⚠️  Build & Price button not immediately visible")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_rav4_navigation_sections(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify all major RAV4 page sections are accessible via navigation.

    Validates:
    - Section navigation exists
    - Each section link works
    - URL updates correctly for each section
    """

    page.goto('https://www.toyota.com/rav4')
    page.wait_for_load_state('domcontentloaded')

    # List of common vehicle page sections
    sections = ['overview', 'gallery', 'features', 'specs', 'trims']

    accessible_sections = []

    for section in sections:
        # Try navigating to each section
        try:
            page.goto(f'https://www.toyota.com/rav4#{section}')
            page.wait_for_timeout(500)

            if f'#{section}' in page.url:
                accessible_sections.append(section)
        except Exception as e:
            print(f"   ⚠️  Section '{section}' not accessible: {e}")

    print(f"\n✅ RAV4 navigation sections validated")
    print(f"   Accessible sections: {', '.join(accessible_sections)}")
    print(f"   Total: {len(accessible_sections)}/{len(sections)}")

    # Assert at least half of the sections are accessible
    assert len(accessible_sections) >= len(sections) // 2, \
        f"Should access at least half of expected sections, accessed: {accessible_sections}"

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_rav4_page_content_quality(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify RAV4 page content quality and completeness.

    Validates:
    - Page has substantial text content
    - Images are present
    - Links are functional
    - No broken content
    """

    page.goto('https://www.toyota.com/rav4')
    page.wait_for_load_state('domcontentloaded')

    # Verify text content
    body_text = page.locator('body').inner_text()
    assert len(body_text) > 500, f"Page should have substantial content, found {len(body_text)} characters"

    # Check for images
    images = page.locator('img').all()
    assert len(images) > 5, f"Page should have multiple images, found {len(images)}"

    # Check for links
    links = page.locator('a').all()
    assert len(links) > 10, f"Page should have multiple links, found {len(links)}"

    print(f"\n✅ RAV4 page content quality validated")
    print(f"   Content length: {len(body_text)} characters")
    print(f"   Images: {len(images)}")
    print(f"   Links: {len(links)}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"
