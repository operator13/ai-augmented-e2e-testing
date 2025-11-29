"""
Global Navigation (GNAV) Test - Recorded with Playwright Codegen
Tests all vehicle categories in the main navigation menu
"""
import re
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.critical_path
def test_gnav_vehicles_menu_complete_flow(page: Page) -> None:
    """
    Complete GNAV test recorded via codegen.

    Tests all vehicle categories:
    - Crossovers & SUVs (Corolla Cross, RAV4)
    - Cars & Minivan (Corolla)
    - Trucks (Tacoma, Tundra)
    - Performance (GR86, GR Corolla, GR Supra)
    - Electrified (Prius)
    - Upcoming Vehicles (2026 RAV4, C-HR, bZ Woodland)
    - Gazoo Racing
    - TRD Pro
    - View All Vehicles

    Also captures:
    - Cookie banner handling
    - Zip code search integration
    - Navigation consistency across all categories
    """
    page.goto("https://www.toyota.com/")
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Crossovers & SUVs").click()
    page.get_by_role("button", name="Cars & Minivan").click()
    page.get_by_role("button", name="Trucks").click()
    page.get_by_role("button", name="Performance").click()
    page.get_by_role("button", name="Electrified").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("button", name="Crossovers & SUVs").click()
    page.get_by_role("button", name="Close Cookie Banner").click()
    page.get_by_role("button", name="Vehicles", exact=True).click()
    page.get_by_role("link", name="Corolla Cross $30,035 as").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("link", name="Hybrid EV Corolla Cross").first.click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Cars & Minivan").click()
    page.get_by_role("link", name="Corolla $28,440 as shown").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("link", name="Hybrid EV RAV4 Hybrid $36,070").first.click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Trucks").click()
    page.get_by_role("link", name="Hybrid EV Available Tacoma $").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Trucks").click()
    page.get_by_role("link", name="Hybrid EV Available Tundra $").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Performance").click()
    page.get_by_role("link", name="GR86 $36,365 as shown").nth(1).click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Performance", exact=True).click()
    page.get_by_role("link", name="GR Corolla $47,965 as shown").nth(1).click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Performance").click()
    page.get_by_role("link", name="GR Supra $68,550 as shown").nth(1).click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("link", name="RAV4 2026 RAV4").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Electrified").click()
    page.get_by_role("link", name="Hybrid EV Prius $36,965 as").nth(1).click()
    page.get_by_role("button", name="Vehicles").click()
    page.locator("li:nth-child(2) > .additional-links > a").first.click()
    page.get_by_role("textbox", name="zip code").fill("60661")
    page.get_by_role("button", name="submit").click()
    page.get_by_role("button", name="Vehicles").click()
    page.locator(".vis-link").first.click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Trucks").click()
    page.locator(".js_slide.active > .slide-wrapper > .vehicles > li > .additional-links > a:nth-child(2)").first.click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Trucks").click()
    page.locator(".js_slide.active > .slide-wrapper > .vehicles > li:nth-child(2) > .additional-links > a").first.click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("link", name="RAV4 2026 RAV4").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("link", name="2026 RAV4 Plug-in Hybrid 2026").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("link", name="bZ Woodland 2026 bZ Woodland").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("link", name="C-HR 2026 C-HR").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_label("Gazoo Racing").click()
    page.goto("https://www.toyota.com/upcoming-vehicles/c-hr/")
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("link", name="TRD Pro", exact=True).click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("link", name="View All Vehicles").click()
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_label("Electrified Vehicles").click()
    page.get_by_role("button", name="Vehicles").click()
    page.goto("https://www.toyota.com/electrified-vehicles/")
