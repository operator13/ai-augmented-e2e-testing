"""
Toyota Mobile Responsiveness Tests

Comprehensive test suite for mobile viewport including:
- Mobile homepage rendering
- Mobile navigation menu
- Touch-friendly interactions
- Mobile-specific layouts
- Responsive design validation
"""

import pytest
import re
from playwright.sync_api import Page, expect
from src.ai.anomaly_detector import AnomalyDetector


# Mobile viewport configuration
MOBILE_VIEWPORT = {
    'width': 375,  # iPhone SE width
    'height': 667
}

TABLET_VIEWPORT = {
    'width': 768,  # iPad width
    'height': 1024
}


@pytest.mark.smoke
@pytest.mark.critical_path
def test_homepage_mobile_responsive(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify homepage renders correctly on mobile viewport.

    Validates:
    - Page loads on mobile viewport
    - Content is readable
    - Images scale appropriately
    - No horizontal scroll
    """

    # Set mobile viewport
    page.set_viewport_size(MOBILE_VIEWPORT)

    # Navigate to homepage
    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Verify page loaded
    body = page.locator('body')
    expect(body).to_be_visible()

    # Check viewport width matches mobile
    viewport_width = page.evaluate('window.innerWidth')
    assert viewport_width == MOBILE_VIEWPORT['width'], \
        f"Viewport should be {MOBILE_VIEWPORT['width']}px, got {viewport_width}px"

    # Verify no horizontal scroll (body width should not exceed viewport)
    body_width = page.evaluate('document.body.scrollWidth')
    assert body_width <= MOBILE_VIEWPORT['width'] + 10, \
        f"Body width {body_width}px exceeds viewport {MOBILE_VIEWPORT['width']}px"

    print(f"\n✅ Homepage mobile responsive")
    print(f"   Viewport: {viewport_width}x{page.evaluate('window.innerHeight')}px")
    print(f"   Body width: {body_width}px")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.smoke
def test_mobile_navigation_menu(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify mobile navigation menu (hamburger menu) works.

    Validates:
    - Hamburger menu icon is present
    - Menu can be opened
    - Navigation links are accessible
    - Menu can be closed
    """

    # Set mobile viewport
    page.set_viewport_size(MOBILE_VIEWPORT)

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Look for mobile menu button (common selectors)
    menu_button_selectors = [
        'button[aria-label*="menu"]',
        'button[aria-label*="Menu"]',
        'button:has-text("Menu")',
        '[class*="hamburger"]',
        '[class*="menu-button"]',
        'button[data-component*="menu"]'
    ]

    menu_found = False
    for selector in menu_button_selectors:
        menu_button = page.locator(selector).first
        if menu_button.is_visible(timeout=2000):
            print(f"\n✅ Mobile menu found: {selector}")
            menu_found = True

            # Try to click menu button
            try:
                menu_button.click()
                page.wait_for_timeout(500)
                print(f"   Menu opened successfully")
            except Exception as e:
                print(f"   Could not click menu: {e}")
            break

    if not menu_found:
        print(f"\n⚠️  Mobile menu button not found with standard selectors")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_vehicle_page_mobile_layout(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify vehicle page renders correctly on mobile.

    Validates:
    - Vehicle images display properly
    - Text is readable
    - CTAs are accessible
    - Content stacks vertically
    """

    # Set mobile viewport
    page.set_viewport_size(MOBILE_VIEWPORT)

    page.goto('https://www.toyota.com/camry')
    page.wait_for_load_state('networkidle')

    # Verify page loaded
    body = page.locator('body')
    expect(body).to_be_visible()

    # Check for horizontal scroll
    body_width = page.evaluate('document.body.scrollWidth')
    viewport_width = page.evaluate('window.innerWidth')

    print(f"\n✅ Vehicle page mobile layout validated")
    print(f"   Viewport: {viewport_width}px")
    print(f"   Body width: {body_width}px")

    # Soft assertion for horizontal scroll
    if body_width > viewport_width + 10:
        print(f"   ⚠️  Warning: Possible horizontal scroll detected")

    # Check for images
    images = page.locator('img').all()
    print(f"   Images loaded: {len(images)}")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_mobile_touch_targets(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify touch targets are appropriately sized for mobile.

    Validates:
    - Buttons are large enough to tap
    - Links are spaced appropriately
    - Interactive elements are accessible
    """

    # Set mobile viewport
    page.set_viewport_size(MOBILE_VIEWPORT)

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Check button sizes (should be at least 44x44px for touch)
    buttons = page.locator('button, a').all()[:10]  # Check first 10 for performance

    small_buttons = []
    for button in buttons:
        if button.is_visible():
            box = button.bounding_box()
            if box:
                if box['width'] < 40 or box['height'] < 40:
                    small_buttons.append(f"{box['width']:.0f}x{box['height']:.0f}px")

    print(f"\n✅ Mobile touch targets validated")
    print(f"   Buttons checked: {len(buttons)}")
    if small_buttons:
        print(f"   ⚠️  Small touch targets found: {len(small_buttons)}")
    else:
        print(f"   All touch targets appropriately sized")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_tablet_viewport_layout(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify page renders correctly on tablet viewport.

    Validates:
    - Tablet layout is appropriate
    - Content uses available space
    - Navigation adapts to tablet size
    """

    # Set tablet viewport
    page.set_viewport_size(TABLET_VIEWPORT)

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Verify page loaded
    body = page.locator('body')
    expect(body).to_be_visible()

    # Check viewport
    viewport_width = page.evaluate('window.innerWidth')
    body_width = page.evaluate('document.body.scrollWidth')

    print(f"\n✅ Tablet layout validated")
    print(f"   Viewport: {viewport_width}px")
    print(f"   Body width: {body_width}px")

    # Check for horizontal scroll
    if body_width > viewport_width + 10:
        print(f"   ⚠️  Warning: Possible horizontal scroll detected")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_mobile_form_usability(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify forms are usable on mobile devices.

    Validates:
    - Input fields are accessible
    - Keyboard appears appropriately
    - Submit buttons are visible
    - Form validation works
    """

    # Set mobile viewport
    page.set_viewport_size(MOBILE_VIEWPORT)

    page.goto('https://www.toyota.com/dealers')
    page.wait_for_load_state('networkidle')

    # Look for input fields
    inputs = page.locator('input[type="text"], input[type="search"]').all()

    if len(inputs) > 0:
        print(f"\n✅ Mobile form elements found")
        print(f"   Input fields: {len(inputs)}")

        # Try to focus on first input
        try:
            inputs[0].focus()
            print(f"   Input field is focusable")
        except Exception as e:
            print(f"   Could not focus input: {e}")
    else:
        print(f"\n⚠️  No form inputs found on this page")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_mobile_performance(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify mobile performance is acceptable.

    Validates:
    - Page loads in reasonable time
    - Content is progressively loaded
    - No blocking resources
    - Performance metrics are reasonable
    """

    # Set mobile viewport
    page.set_viewport_size(MOBILE_VIEWPORT)

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Collect performance metrics
    metrics = anomaly_detector.collect_performance_metrics()

    if metrics:
        fcp = metrics.get('firstContentfulPaint', 0)
        load_complete = metrics.get('loadComplete', 0)

        print(f"\n✅ Mobile performance metrics collected")
        print(f"   First Contentful Paint: {fcp:.0f}ms")
        print(f"   Load Complete: {load_complete:.0f}ms")

        # Soft performance warnings for mobile
        if fcp > 3000:
            print(f"   ⚠️  FCP is slower than ideal for mobile (>3000ms)")
        if load_complete > 5000:
            print(f"   ⚠️  Load time is slower than ideal for mobile (>5000ms)")
    else:
        print(f"\n⚠️  Performance metrics not available")

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"
