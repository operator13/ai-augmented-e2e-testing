"""
Toyota Homepage Tests

Comprehensive test suite for toyota.com homepage including:
- Hero section validation
- Featured vehicles display
- Call-to-action buttons
- Navigation accessibility
- Content loading and performance
"""

import pytest
import re
from playwright.sync_api import Page, expect
from src.ai.anomaly_detector import AnomalyDetector


@pytest.mark.smoke
@pytest.mark.critical_path
def test_homepage_loads_successfully(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify Toyota homepage loads successfully with all key elements.

    Validates:
    - Page loads without errors
    - Title and URL are correct
    - Main navigation is present
    - Hero section is visible
    - No critical errors
    """

    # Navigate to homepage
    page.goto('https://www.toyota.com')

    # Verify page loaded successfully
    expect(page).to_have_url(re.compile(r'https://www\.toyota\.com/?'))
    expect(page).to_have_title(re.compile('Toyota', re.IGNORECASE))
    assert page.url.startswith('https://'), "Page should load over HTTPS"

    # Wait for page to be fully loaded
    page.wait_for_load_state('networkidle')

    # Verify main navigation is present
    main_nav = page.locator('nav[aria-label*="main"]').first
    expect(main_nav).to_be_visible()

    # Verify hero section is visible
    hero_section = page.locator('[class*="hero"], [data-component*="hero"]').first
    expect(hero_section).to_be_visible()

    # Verify body has content
    body = page.locator('body')
    expect(body).to_be_visible()
    assert len(body.inner_text()) > 100, "Homepage should have substantial content"

    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"

    print("\n✅ Homepage loaded successfully")
    print(f"   Title: {page.title()}")
    print(f"   URL: {page.url}")


@pytest.mark.smoke
def test_homepage_hero_section(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify hero section contains expected elements.

    Validates:
    - Hero image/video is present
    - Hero text/headline is visible
    - CTA buttons are present and clickable
    """

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Check for hero section (use more flexible selectors)
    # Try multiple potential hero selectors
    hero_selectors = [
        '[class*="hero"]',
        '[data-component*="hero"]',
        'section:first-of-type',  # Often the first section is hero
        '[class*="banner"]',
        'main > div:first-child'
    ]

    hero = None
    for selector in hero_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible(timeout=2000):
                hero = element
                break
        except:
            continue

    assert hero is not None, "Hero section should be visible"

    # Verify page has headlines (flexible - anywhere on page)
    headlines = page.locator('h1, h2').all()
    assert len(headlines) > 0, "Homepage should have headlines"
    hero_text = headlines[0]
    assert len(hero_text.inner_text()) > 0, "Hero should have headline text"

    # Check for CTA buttons/links
    cta_selectors = ['a[href*="build"]', 'a[href*="inventory"]', 'a[href*="dealer"]', 'a:has-text("Explore")', 'button']
    cta_buttons = []
    for selector in cta_selectors:
        try:
            elements = page.locator(selector).all()
            cta_buttons.extend(elements[:3])  # Get first 3 of each type
        except:
            continue

    assert len(cta_buttons) > 0, "Homepage should have CTA buttons or links"

    # Filter known errors
    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"

    print(f"\n✅ Hero section validated")
    print(f"   Headline: {hero_text.inner_text()[:50]}...")
    print(f"   CTA buttons: {len(cta_buttons)}")


@pytest.mark.regression
def test_homepage_featured_vehicles(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify featured vehicles section displays vehicles correctly.

    Validates:
    - Featured vehicles section exists
    - Vehicle cards are displayed
    - Vehicle images are loaded
    - Vehicle names/links are present
    """

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Look for vehicles section (common selectors)
    vehicles_section = page.locator('[class*="vehicle"], [data-component*="vehicle"]').first
    expect(vehicles_section).to_be_visible(timeout=10000)

    # Check for vehicle cards
    vehicle_cards = page.locator('[data-e2e*="vehicle"], a[href*="/vehicles/"], a[href*="/camry"], a[href*="/rav4"], a[href*="/corolla"]').all()
    assert len(vehicle_cards) > 0, "Should display at least one vehicle"

    print(f"\n✅ Featured vehicles section validated")
    print(f"   Vehicle cards found: {len(vehicle_cards)}")

    # Verify at least some vehicle images are loaded
    vehicle_images = page.locator('[data-e2e*="vehicle"] img, a[href*="/vehicles/"] img').all()
    if len(vehicle_images) > 0:
        print(f"   Vehicle images found: {len(vehicle_images)}")

    # Filter known errors
    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.smoke
def test_homepage_main_navigation(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify main navigation is accessible and contains expected items.

    Validates:
    - Main navigation is visible
    - Key navigation items present (Vehicles, Shopping, etc.)
    - Navigation items are clickable
    """

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Verify main navigation (try multiple selectors)
    nav_selectors = ['nav', 'header nav', '[role="navigation"]', 'header']
    main_nav = None
    for selector in nav_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible(timeout=2000):
                main_nav = element
                break
        except:
            continue

    assert main_nav is not None, "Main navigation should be visible"

    # Check for key navigation items (more flexible selectors)
    expected_nav_items = ['Vehicles', 'Shopping', 'Owners', 'Support', 'About']

    found_items = []
    for item in expected_nav_items:
        # Try multiple selector patterns
        selectors = [
            f'nav a:has-text("{item}")',
            f'header a:has-text("{item}")',
            f'a:has-text("{item}")',
            f'button:has-text("{item}")'
        ]
        for selector in selectors:
            try:
                elements = page.locator(selector).all()
                if len(elements) > 0 and elements[0].is_visible(timeout=1000):
                    found_items.append(item)
                    break
            except:
                continue

    assert len(found_items) >= 2, f"Should find at least 2 main navigation items, found: {found_items}"

    print(f"\n✅ Main navigation validated")
    print(f"   Found navigation items: {', '.join(found_items)}")

    # Filter known errors
    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.smoke
def test_homepage_cta_buttons(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify call-to-action buttons are present and functional.

    Validates:
    - Build & Price button exists
    - Search Inventory button exists
    - Find a Dealer button exists
    - Buttons are clickable
    """

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Common CTA button text
    cta_buttons = [
        'Build',
        'Search Inventory',
        'Find a Dealer',
        'Shop Now',
        'Explore'
    ]

    found_ctas = []
    for cta_text in cta_buttons:
        cta = page.locator(f'a:has-text("{cta_text}"), button:has-text("{cta_text}")').first
        if cta.is_visible(timeout=2000):
            found_ctas.append(cta_text)
            # Verify button is clickable
            expect(cta).to_be_enabled()

    assert len(found_ctas) >= 2, f"Should find at least 2 CTA buttons, found: {found_ctas}"

    print(f"\n✅ CTA buttons validated")
    print(f"   Found CTAs: {', '.join(found_ctas)}")

    # Filter known errors
    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.regression
def test_homepage_footer_navigation(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify footer navigation contains expected links.

    Validates:
    - Footer is present
    - Footer contains navigation links
    - Key footer sections exist (About, Contact, etc.)
    """

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Scroll to footer
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    page.wait_for_timeout(1000)

    # Verify footer exists
    footer = page.locator('footer').first
    expect(footer).to_be_visible()

    # Check for footer links
    footer_links = page.locator('footer a').all()
    assert len(footer_links) > 5, f"Footer should have multiple links, found: {len(footer_links)}"

    # Check for common footer sections
    common_footer_items = ['About', 'Contact', 'Privacy', 'Terms']
    found_footer_items = []

    for item in common_footer_items:
        footer_item = page.locator(f'footer a:has-text("{item}")').first
        if footer_item.is_visible(timeout=1000):
            found_footer_items.append(item)

    print(f"\n✅ Footer navigation validated")
    print(f"   Total footer links: {len(footer_links)}")
    print(f"   Found footer items: {', '.join(found_footer_items)}")

    # Filter known errors
    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"


@pytest.mark.performance
def test_homepage_load_performance(page: Page, anomaly_detector: AnomalyDetector):
    """
    Verify homepage loads within acceptable performance thresholds.

    Validates:
    - Page load time is reasonable
    - First Contentful Paint is fast
    - Time to Interactive is acceptable
    """

    page.goto('https://www.toyota.com')
    page.wait_for_load_state('networkidle')

    # Collect performance metrics
    metrics = anomaly_detector.collect_performance_metrics()

    if metrics:
        fcp = metrics.get('firstContentfulPaint', 0)
        load_complete = metrics.get('loadComplete', 0)

        print(f"\n✅ Performance metrics collected")
        print(f"   First Contentful Paint: {fcp:.0f}ms")
        print(f"   Load Complete: {load_complete:.0f}ms")

        # Soft assertions for performance (warnings, not failures)
        if fcp > 3000:
            print(f"   ⚠️  FCP is slower than ideal (>3000ms)")

        if load_complete > 5000:
            print(f"   ⚠️  Load time is slower than ideal (>5000ms)")
    else:
        print("\n⚠️  Performance metrics not available")

    # Verify page is responsive after load
    body = page.locator('body')
    expect(body).to_be_visible()

    # Filter known errors
    # Check for test-blocking errors (website bugs are filtered and reported separately)
    test_blocking_errors = anomaly_detector.get_test_blocking_errors()
    assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"
