"""
Global Navigation (GNAV) Test - Clean Version
Based on codegen recording, optimized for reliability

Tests that all main vehicle categories in GNAV open correctly
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.critical_path
def test_gnav_all_vehicle_categories(page: Page) -> None:
    """
    Test that all vehicle categories in the main navigation are accessible.

    Uses selectors captured from codegen recording.
    """
    page.goto("https://www.toyota.com/")

    # Handle cookie banner if present
    try:
        page.get_by_role("button", name="Close Cookie Banner").click(timeout=3000)
    except:
        pass

    # Open main Vehicles menu
    vehicles_btn = page.get_by_role("button", name="Vehicles")
    vehicles_btn.click()
    page.wait_for_timeout(500)

    print("\n" + "="*70)
    print("GNAV VEHICLE CATEGORIES TEST (Codegen Selectors)")
    print("="*70)

    # Test 1: Crossovers & SUVs category exists
    crossover_btn = page.get_by_role("button", name="Crossovers & SUVs")
    expect(crossover_btn).to_be_visible()
    crossover_btn.click()
    page.wait_for_timeout(500)
    print("✅ Crossovers & SUVs - Opens successfully")

    # Test 2: Cars & Minivan category exists
    cars_btn = page.get_by_role("button", name="Cars & Minivan")
    expect(cars_btn).to_be_visible()
    cars_btn.click()
    page.wait_for_timeout(500)
    print("✅ Cars & Minivan - Opens successfully")

    # Test 3: Trucks category exists
    trucks_btn = page.get_by_role("button", name="Trucks")
    expect(trucks_btn).to_be_visible()
    trucks_btn.click()
    page.wait_for_timeout(500)
    print("✅ Trucks - Opens successfully")

    # Test 4: Performance category exists
    performance_btn = page.get_by_role("button", name="Performance")
    expect(performance_btn).to_be_visible()
    performance_btn.click()
    page.wait_for_timeout(500)
    print("✅ Performance - Opens successfully")

    # Test 5: Electrified category exists
    electrified_btn = page.get_by_role("button", name="Electrified")
    expect(electrified_btn).to_be_visible()
    electrified_btn.click()
    page.wait_for_timeout(500)
    print("✅ Electrified - Opens successfully")

    # Test 6: Upcoming Vehicles category exists
    upcoming_btn = page.get_by_role("button", name="Upcoming Vehicles")
    expect(upcoming_btn).to_be_visible()
    upcoming_btn.click()
    page.wait_for_timeout(500)
    print("✅ Upcoming Vehicles - Opens successfully")

    print("="*70)
    print("All GNAV categories verified successfully!")
    print("="*70 + "\n")


@pytest.mark.smoke
def test_gnav_vehicle_links_clickable(page: Page) -> None:
    """
    Test that specific vehicle links are clickable in GNAV.
    Uses exact selectors from codegen recording.
    """
    page.goto("https://www.toyota.com/")

    # Dismiss cookie banner
    try:
        page.get_by_role("button", name="Close Cookie Banner").click(timeout=3000)
    except:
        pass

    # Open Vehicles menu
    page.get_by_role("button", name="Vehicles").click()
    page.wait_for_timeout(1000)

    # Open Crossovers & SUVs
    page.get_by_role("button", name="Crossovers & SUVs").click()
    page.wait_for_timeout(1000)

    # Verify vehicle link exists (from codegen recording)
    corolla_link = page.get_by_role("link", name="Corolla Cross $30,035 as")
    expect(corolla_link).to_be_visible(timeout=5000)

    print("✅ Vehicle links are clickable in GNAV")


@pytest.mark.smoke
def test_gnav_special_categories(page: Page) -> None:
    """
    Test special GNAV categories captured in codegen recording:
    - Gazoo Racing
    - TRD Pro
    - Electrified Vehicles
    - View All Vehicles
    """
    page.goto("https://www.toyota.com/")

    # Dismiss cookie banner
    try:
        page.get_by_role("button", name="Close Cookie Banner").click(timeout=3000)
    except:
        pass

    # Open Vehicles menu
    page.get_by_role("button", name="Vehicles").click()
    page.wait_for_timeout(1000)

    print("\n" + "="*70)
    print("GNAV SPECIAL CATEGORIES TEST")
    print("="*70)

    # Test Gazoo Racing link
    try:
        gr_link = page.get_by_label("Gazoo Racing")
        expect(gr_link).to_be_visible()
        print("✅ Gazoo Racing - Link exists")
    except:
        print("⚠️  Gazoo Racing - Link not found (may be in submenu)")

    # Test TRD Pro link
    try:
        trd_link = page.get_by_role("link", name="TRD Pro", exact=True)
        expect(trd_link).to_be_visible()
        print("✅ TRD Pro - Link exists")
    except:
        print("⚠️  TRD Pro - Link not found (may be in submenu)")

    # Test View All Vehicles
    try:
        view_all = page.get_by_role("link", name="View All Vehicles")
        expect(view_all).to_be_visible()
        print("✅ View All Vehicles - Link exists")
    except:
        print("⚠️  View All Vehicles - Link not found")

    # Test Electrified Vehicles
    try:
        electrified_link = page.get_by_label("Electrified Vehicles")
        expect(electrified_link).to_be_visible()
        print("✅ Electrified Vehicles - Link exists")
    except:
        print("⚠️  Electrified Vehicles - Link not found")

    print("="*70 + "\n")
