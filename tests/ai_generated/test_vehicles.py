"""
Test "View All Vehicles" link in vehicle configurator

This test validates that after selecting a vehicle in the configurator,
the "View All Vehicles" link appears and functions correctly.
"""

import re
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.headed_only  # REQUIRED: Configurator fails in headless mode
def test_view_all_vehicles_link_in_configurator(page: Page):
    """
    Test that "View All Vehicles" link appears after selecting a vehicle.

    Flow:
    1. Navigate to Build & Price (configurator)
    2. Handle zip code modal
    3. Click Electrified tab
    4. Select Camry
    5. Verify "View All Vehicles" link appears on configuration page
    6. Click it and verify navigation

    NOTE: Requires --headed mode due to configurator website bug.
    Run with: pytest tests/ai_generated/test_vehicles.py --headed
    """

    print("\n🔗 Testing 'View All Vehicles' Link...")

    # Step 1: Navigate to homepage - ASSERTIONS
    print("📍 Navigating to homepage...")
    page.goto("https://www.toyota.com/")
    page.wait_for_load_state('domcontentloaded')

    expect(page).to_have_url(re.compile(r'toyota\.com'))
    expect(page).to_have_title(re.compile('Toyota', re.IGNORECASE))
    assert page.url.startswith('https://'), "Page should be loaded over HTTPS"
    print("✓ Homepage loaded (URL, title, HTTPS validated)")

    # Step 2: Click Build & Price - ASSERTIONS
    print("\n🖱️  Clicking Build & Price...")
    build_price_btn = page.get_by_role("link", name="Build & Price Build & Price")
    expect(build_price_btn).to_be_visible()
    expect(build_price_btn).to_be_enabled()

    build_price_btn.click()
    page.wait_for_load_state('domcontentloaded')

    expect(page).to_have_url(re.compile(r'/configurator'))
    assert '/configurator' in page.url, f"Should navigate to configurator, got: {page.url}"
    print(f"✓ Navigated to configurator: {page.url}")

    # Step 3: Handle zip code modal - ASSERTIONS
    print("\n📍 Entering zip code...")
    zip_input = page.get_by_placeholder("Zip Code")
    expect(zip_input).to_be_visible(timeout=5000)
    expect(zip_input).to_be_editable()

    zip_input.click()
    zip_input.fill("90210")
    assert zip_input.input_value() == "90210", "Zip code should be filled"

    submit_btn = page.get_by_label("submit")
    expect(submit_btn).to_be_visible()
    expect(submit_btn).to_be_enabled()
    submit_btn.click()
    page.wait_for_timeout(1000)
    print("✓ Zip code submitted (input validated)")

    # Step 4: Close cookie banner (no assertions needed)
    try:
        page.get_by_label("Close Cookie Banner").click(timeout=2000)
        print("✓ Cookie banner closed")
    except:
        pass

    # Step 5: Click Electrified tab - ASSERTIONS
    print("\n📋 Clicking Electrified tab...")
    electrified_tab = page.get_by_role("button", name="Electrified")
    expect(electrified_tab).to_be_visible(timeout=10000)
    expect(electrified_tab).to_be_enabled()

    electrified_tab.click()
    page.wait_for_timeout(2000)
    print("✓ Electrified tab clicked (visibility and state validated)")

    # Step 6: Select Camry - ASSERTIONS
    print("\n🚗 Selecting Camry...")
    camry_select_selector = ".show > .vcr-category-section-wrap > .vcr-category-section-grid > div:nth-child(4) > .vcr-vehicle-card-inner > .vcr-vehicle-card-front > .vcr-vehicle-card-front-bottom > .vcr-vehicle-card-front-ctas > .cta"

    # Scroll into view
    escaped_selector = camry_select_selector.replace("'", "\\'")
    page.evaluate(f"""
        const element = document.querySelector('{escaped_selector}');
        if (element) {{
            element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
    """)
    page.wait_for_timeout(1000)

    # Click Camry Select - ASSERTIONS
    camry_select = page.locator(camry_select_selector).first
    expect(camry_select).to_be_visible(timeout=5000)
    expect(camry_select).to_be_enabled()

    initial_url = page.url
    camry_select.click()
    page.wait_for_load_state('domcontentloaded', timeout=15000)

    # Verify navigation occurred
    assert page.url != initial_url, "Should navigate after selecting Camry"
    assert 'camry' in page.url.lower() or '/configurator/build' in page.url, \
        f"URL should contain camry or build, got: {page.url}"
    print(f"✓ Camry selected, navigated to: {page.url}")

    # Step 7: Verify "View All Vehicles" link appears - COMPREHENSIVE ASSERTIONS
    print("\n🔍 Looking for 'View All Vehicles' link...")

    # Wait for page content to load
    page.wait_for_timeout(3000)

    # Use multiple selector strategies
    view_all_selectors = [
        'a.vis-link:has-text("View All Vehicles")',
        'a[href*="/configurator/"]:has-text("View All Vehicles")',
        'a:has-text("View All Vehicles")'
    ]

    view_all_link = None
    selector_used = None
    for selector in view_all_selectors:
        try:
            link = page.locator(selector).first
            if link.is_visible(timeout=5000):
                view_all_link = link
                selector_used = selector
                print(f"✓ Found 'View All Vehicles' link using: {selector}")
                break
        except:
            continue

    # ASSERT link was found
    assert view_all_link is not None, \
        "'View All Vehicles' link should be visible on vehicle configuration page"

    # ASSERT link is visible and enabled
    expect(view_all_link).to_be_visible()
    expect(view_all_link).to_be_enabled()

    # ASSERT link attributes are correct
    href = view_all_link.get_attribute('href')
    assert href is not None, "Link should have href attribute"
    assert '/configurator' in href, \
        f"Expected link to point to configurator, got: {href}"

    # ASSERT link text contains expected text
    link_text = view_all_link.inner_text()
    assert 'View All Vehicles' in link_text, \
        f"Link text should contain 'View All Vehicles', got: {link_text}"

    print(f"✓ Link validated - href: {href}, text: {link_text}")

    # Step 8: Click "View All Vehicles" and verify navigation - ASSERTIONS
    print("\n🖱️  Clicking 'View All Vehicles'...")
    config_page_url = page.url

    view_all_link.click()
    page.wait_for_load_state('domcontentloaded', timeout=10000)

    # ASSERT navigation occurred
    final_url = page.url
    assert final_url != config_page_url, \
        f"Should navigate away from config page. Before: {config_page_url}, After: {final_url}"

    # ASSERT we're on configurator page
    expect(page).to_have_url(re.compile(r'/configurator'))
    assert '/configurator' in final_url, \
        f"Should navigate to configurator, got: {final_url}"

    # ASSERT page loaded successfully
    main_content = page.locator('main, [role="main"], body').first
    expect(main_content).to_be_visible()

    # ASSERT we're back on a different configurator view (not the same config page)
    assert 'build' not in final_url or final_url != config_page_url, \
        "Should return to main configurator view, not same config page"

    print(f"✓ Navigated successfully: {final_url}")
    print("✓ Main content loaded and visible")

    print("\n✅ 'View All Vehicles' Link Test Complete!")
    print("  ✓ All navigation steps: VALIDATED")
    print("  ✓ Link existence: ASSERTED")
    print("  ✓ Link attributes: ASSERTED")
    print("  ✓ Link functionality: ASSERTED")
    print("  ✓ Page state: ASSERTED")
    print(f"  ✓ Total assertions passed: 20+")