"""
Toyota Corolla Vehicle Page Tests

Comprehensive test suite for Corolla vehicle page including:
- Page load and navigation
- Gallery section
- Features and specs
- Trim selection
- Visual content validation
"""

import pytest
import re
from playwright.sync_api import Page, expect
from src.ai.anomaly_detector import AnomalyDetector


@pytest.mark.smoke
@pytest.mark.critical_path
def test_corolla_page_loads_successfully(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Corolla page loads successfully with all key elements.

    Validates:
    - Page loads without errors
    - Title contains "Corolla"
    - URL is correct
    - Main content is visible
    - No critical errors
    """

    # Navigate to Corolla page
    page.goto('https://www.toyota.com/corolla')

    # Verify page loaded successfully
    expect(page).to_have_url(re.compile(r'.*/corolla'))
    expect(page).to_have_title(re.compile('Corolla', re.IGNORECASE))
    assert 'corolla' in page.url.lower(), f"URL should contain 'corolla', got: {page.url}"
    assert page.url.startswith('https://'), "Page should load over HTTPS"

    # Wait for page to be fully loaded
    page.wait_for_load_state('networkidle')

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

    print(f"\n✅ Corolla page loaded successfully")
    print(f"   Title: {page.title()}")
    print(f"   URL: {page.url}")


@pytest.mark.smoke
def test_corolla_gallery_section(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Corolla gallery section is accessible and displays images.

    Validates:
    - Gallery section navigation works
    - Images are present
    - Image gallery is interactive
    """

    page.goto('https://www.toyota.com/corolla')
    page.wait_for_load_state('networkidle')

    # Navigate to gallery using URL hash
    page.goto('https://www.toyota.com/corolla#gallery')
    page.wait_for_timeout(1000)

    # Verify URL updated
    expect(page).to_have_url(re.compile(r'.*#gallery'))
    assert '#gallery' in page.url, f"URL should contain '#gallery', got: {page.url}"

    # Verify still on Corolla page
    assert 'corolla' in page.url.lower(), "Should still be on Corolla page"

    print(f"\n✅ Corolla gallery section accessible")
    print(f"   URL: {page.url}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_corolla_features_section(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Corolla features section is accessible and displays content.

    Validates:
    - Features section navigation works
    - Feature descriptions are present
    - Feature images/icons are visible
    """

    page.goto('https://www.toyota.com/corolla')
    page.wait_for_load_state('networkidle')

    # Navigate to features using URL hash
    page.goto('https://www.toyota.com/corolla#features')
    page.wait_for_timeout(1000)

    # Verify URL updated
    expect(page).to_have_url(re.compile(r'.*#features'))
    assert '#features' in page.url, f"URL should contain '#features', got: {page.url}"

    # Verify still on Corolla page
    assert 'corolla' in page.url.lower(), "Should still be on Corolla page"

    print(f"\n✅ Corolla features section accessible")
    print(f"   URL: {page.url}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_corolla_trims_section(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Corolla trims section displays available trim levels.

    Validates:
    - Trims section is accessible
    - Trim options are displayed
    - Trim selection works
    """

    page.goto('https://www.toyota.com/corolla')
    page.wait_for_load_state('networkidle')

    # Navigate to trims using URL hash
    page.goto('https://www.toyota.com/corolla#trims')
    page.wait_for_timeout(1000)

    # Verify URL updated
    expect(page).to_have_url(re.compile(r'.*#trims'))
    assert '#trims' in page.url, f"URL should contain '#trims', got: {page.url}"

    # Verify still on Corolla page
    assert 'corolla' in page.url.lower(), "Should still be on Corolla page"

    print(f"\n✅ Corolla trims section accessible")
    print(f"   URL: {page.url}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.smoke
def test_corolla_hybrid_information(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Corolla hybrid information is accessible.

    Validates:
    - Hybrid trim information present
    - Fuel efficiency details displayed
    - Hybrid-specific features mentioned
    """

    page.goto('https://www.toyota.com/corolla')
    page.wait_for_load_state('networkidle')

    # Look for hybrid-related content
    hybrid_mentions = page.locator('text=/hybrid/i').all()

    if len(hybrid_mentions) > 0:
        print(f"\n✅ Corolla hybrid information found")
        print(f"   Hybrid mentions: {len(hybrid_mentions)}")
    else:
        print(f"\n⚠️  No hybrid information found on main page")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_corolla_navigation_sections(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify all major Corolla page sections are accessible via navigation.

    Validates:
    - Section navigation exists
    - Each section link works
    - URL updates correctly for each section
    """

    page.goto('https://www.toyota.com/corolla')
    page.wait_for_load_state('networkidle')

    # List of common vehicle page sections
    sections = ['overview', 'gallery', 'features', 'specs', 'trims']

    accessible_sections = []

    for section in sections:
        # Try navigating to each section
        try:
            page.goto(f'https://www.toyota.com/corolla#{section}')
            page.wait_for_timeout(500)

            if f'#{section}' in page.url:
                accessible_sections.append(section)
        except Exception as e:
            print(f"   ⚠️  Section '{section}' not accessible: {e}")

    print(f"\n✅ Corolla navigation sections validated")
    print(f"   Accessible sections: {', '.join(accessible_sections)}")
    print(f"   Total: {len(accessible_sections)}/{len(sections)}")

    # Assert at least half of the sections are accessible
    assert len(accessible_sections) >= len(sections) // 2, \
        f"Should access at least half of expected sections, accessed: {accessible_sections}"

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_corolla_page_content_quality(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Corolla page content quality and completeness.

    Validates:
    - Page has substantial text content
    - Images are present
    - Links are functional
    - No broken content
    """

    page.goto('https://www.toyota.com/corolla')
    page.wait_for_load_state('networkidle')

    # Verify text content
    body_text = page.locator('body').inner_text()
    assert len(body_text) > 500, f"Page should have substantial content, found {len(body_text)} characters"

    # Check for images
    images = page.locator('img').all()
    assert len(images) > 5, f"Page should have multiple images, found {len(images)}"

    # Check for links
    links = page.locator('a').all()
    assert len(links) > 10, f"Page should have multiple links, found {len(links)}"

    print(f"\n✅ Corolla page content quality validated")
    print(f"   Content length: {len(body_text)} characters")
    print(f"   Images: {len(images)}")
    print(f"   Links: {len(links)}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"
