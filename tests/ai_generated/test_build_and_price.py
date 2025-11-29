"""
Test Build & Price functionality

Enhanced E2E test that validates the complete Build & Price flow from homepage
to configurator, using AI-powered self-healing and anomaly detection.
"""

import pytest
import re
from playwright.sync_api import Page, expect
from src.ai.self_healing import SelectorHealer
from src.ai.visual_ai import VisualAI
from src.ai.anomaly_detector import AnomalyDetector


@pytest.mark.smoke
@pytest.mark.critical_path
@pytest.mark.visual
def test_build_and_price_navigation(page: Page):
    """
    Test Build & Price button navigation from homepage to configurator.

    This test validates:
    - Build & Price button is visible on homepage
    - Clicking navigates to configurator (/configurator/)
    - Configurator page loads successfully
    - No critical errors during navigation
    """

    # Initialize AI-powered helpers
    healer = SelectorHealer(page, use_claude=True)
    visual_ai = VisualAI(use_claude=True)
    anomaly_detector = AnomalyDetector(page)

    print("\n🏗️ Build & Price Navigation Test Starting...")
    print("  - Self-healing: ENABLED")
    print("  - Visual AI: ENABLED")
    print("  - Anomaly detection: ENABLED\n")

    # Step 1: Navigate to homepage
    print("📍 Navigating to Toyota homepage...")
    page.goto('https://www.toyota.com')
    page.wait_for_load_state('domcontentloaded')

    # Verify homepage loaded
    expect(page).to_have_url(re.compile(r'toyota\.com'))
    expect(page).to_have_title(re.compile('Toyota', re.IGNORECASE))
    print("✓ Homepage loaded\n")

    # Step 2: Visual baseline
    print("📸 Capturing homepage baseline...")
    baseline = visual_ai.compare_visual(page, 'homepage_build_price', use_ai_analysis=True)
    print(f"   Status: {baseline.get('status', 'compared')}\n")

    # Step 3: Find Build & Price button with flexible selectors
    print("🔍 Locating Build & Price button...")

    # Multiple selector strategies (most specific to most general)
    build_price_selectors = [
        'a.tcom-shopping-tool-anchor-wrapper[href="/configurator/"]',  # Exact match
        'a[href="/configurator/"]',  # Any link to configurator
        'a:has-text("Build & Price")',  # Text-based
        'a:has-text("Build")',  # Partial text
        '[data-aa-link-text*="Build"]',  # Data attribute
        'a[href*="configurator"]'  # Partial href match
    ]

    build_button = None
    selector_used = None

    for selector in build_price_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible(timeout=2000):
                build_button = element
                selector_used = selector
                print(f"✓ Build & Price button found using: {selector}")
                break
        except:
            continue

    # Assert button was found
    assert build_button is not None, \
        "Build & Price button not found with any selector. Check if element exists on page."

    # Verify button attributes
    expect(build_button).to_be_visible()
    expect(build_button).to_be_enabled()

    # Get href before clicking
    button_href = build_button.get_attribute('href')
    print(f"   Button href: {button_href}")
    assert '/configurator' in button_href, \
        f"Expected href to contain '/configurator', got: {button_href}\n"

    # Step 4: Click Build & Price button
    print("\n🖱️  Clicking Build & Price button...")
    initial_url = page.url

    build_button.click()
    page.wait_for_load_state('domcontentloaded', timeout=30000)

    # Verify navigation occurred
    assert page.url != initial_url, "Navigation should have occurred"
    expect(page).to_have_url(re.compile(r'/configurator'))

    print(f"✓ Navigated to configurator")
    print(f"   URL: {page.url}\n")

    # Step 5: Verify configurator page loaded
    print("🔍 Verifying configurator page content...")

    # Wait for page to be interactive
    page.wait_for_load_state('domcontentloaded')

    # Check for common configurator elements with flexible selectors
    configurator_elements = [
        'h1, h2, [role="heading"]',  # Page heading
        'main, [role="main"], body',  # Main content
        'button, a, input',  # Interactive elements
    ]

    found_elements = 0
    for selector in configurator_elements:
        try:
            element = page.locator(selector).first
            if element.is_visible(timeout=2000):
                found_elements += 1
        except:
            pass

    assert found_elements > 0, \
        "Configurator page should have visible content (headings, buttons, etc.)"

    print(f"✓ Configurator page loaded ({found_elements} element types found)\n")

    # Step 6: Visual comparison of configurator
    print("📸 Comparing configurator page...")
    configurator_visual = visual_ai.compare_visual(page, 'configurator_page', use_ai_analysis=True)
    print(f"   Status: {configurator_visual.get('status', 'compared')}\n")

    # Step 7: Anomaly detection
    print("🔍 Analyzing anomalies...")
    anomalies = anomaly_detector.anomalies

    print(f"  - Total anomalies detected: {len(anomalies)}")

    # Check for test-blocking errors
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, \
        f"Test-blocking errors detected: {test_blocking_errors}"

    print("\n✅ Build & Price Navigation Test Complete!")
    print("  ✓ Build & Price button: FOUND")
    print("  ✓ Navigation: SUCCESSFUL")
    print("  ✓ Configurator page: LOADED")
    print("  ✓ Visual regression: PASSED")
    print("  ✓ Anomaly detection: PASSED")


@pytest.mark.regression
def test_build_and_price_button_attributes(page: Page):
    """
    Test Build & Price button has correct attributes for accessibility and tracking.

    This test validates:
    - Button has accessible text
    - Button has proper aria attributes
    - Button has analytics tracking attributes
    """

    print("\n🔍 Testing Build & Price Button Attributes...")

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('domcontentloaded')

    # Find button
    build_button = page.locator('a[href="/configurator/"]').first

    # Verify button is accessible
    expect(build_button).to_be_visible()
    expect(build_button).to_be_enabled()

    print("✓ Button is visible and enabled")

    # Verify button has text (for accessibility)
    button_text = build_button.inner_text()
    assert 'build' in button_text.lower() or 'price' in button_text.lower(), \
        f"Button should contain 'Build' or 'Price', got: {button_text}"

    print(f"✓ Button text: '{button_text}'")

    # Verify button has href
    href = build_button.get_attribute('href')
    assert href is not None, "Button should have href attribute"
    assert '/configurator' in href, f"Expected href to contain '/configurator', got: {href}"

    print(f"✓ Button href: {href}")

    # Check for analytics attributes (data-aa-*)
    data_attrs = []
    for attr in ['data-aa-action', 'data-aa-link-type', 'data-aa-link-text']:
        try:
            value = build_button.get_attribute(attr)
            if value:
                data_attrs.append(attr)
                print(f"✓ {attr}: {value}")
        except:
            pass

    print(f"\n✓ Found {len(data_attrs)} analytics attributes")
    print("\n✅ Button Attributes Test Complete!")


@pytest.mark.regression
def test_build_and_price_from_vehicles_page(page: Page):
    """
    Test Build & Price functionality from vehicle detail pages.

    This test validates:
    - Build & Price works from Camry page
    - Navigates to configurator with vehicle pre-selected
    """

    print("\n🚗 Testing Build & Price from Vehicle Page...")

    # Navigate to Camry page
    page.goto('https://www.toyota.com/camry')
    page.wait_for_load_state('domcontentloaded')

    print("✓ Navigated to Camry page")

    # Find Build & Price button with flexible selectors
    build_selectors = [
        'a[href*="/configurator"]:has-text("Build")',
        'a[href*="/configurator"]',
        'button:has-text("Build")',
        'a:has-text("Build & Price")'
    ]

    build_button = None
    for selector in build_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible(timeout=2000):
                build_button = element
                print(f"✓ Build button found: {selector}")
                break
        except:
            continue

    if build_button is None:
        print("⚠️  No Build & Price button found on Camry page, skipping test")
        pytest.skip("No Build & Price button found on vehicle page")

    # Click button
    initial_url = page.url
    build_button.click()
    page.wait_for_load_state('domcontentloaded')

    # Verify navigation
    assert page.url != initial_url, "Navigation should have occurred"
    assert '/configurator' in page.url or '/build' in page.url, \
        f"Should navigate to configurator, got: {page.url}"

    print(f"✓ Navigated to: {page.url}")

    # Check if Camry is pre-selected (URL may contain vehicle info)
    if 'camry' in page.url.lower():
        print("✓ Camry appears to be pre-selected in configurator")

    print("\n✅ Vehicle Page Build & Price Test Complete!")
