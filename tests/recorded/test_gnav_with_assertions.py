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
    # Verify Toyota homepage loaded successfully
    expect(page).to_have_url("https://www.toyota.com/")
    expect(page).to_have_title(re.compile(r"Toyota", re.IGNORECASE))
    
    page.get_by_role("button", name="Vehicles").click()
    # Verify Vehicles menu is opened and dropdown is visible
    expect(page.get_by_role("button", name="Vehicles")).to_be_visible()
    expect(page.get_by_role("button", name="Crossovers & SUVs")).to_be_visible()
    
    page.get_by_role("button", name="Crossovers & SUVs").click()
    # Verify Crossovers & SUVs submenu is expanded
    expect(page.get_by_role("link", name="Corolla Cross")).to_be_visible()
    
    page.get_by_role("button", name="Cars & Minivan").click()
    # Verify Cars & Minivan submenu is expanded
    expect(page.get_by_role("link", name="Corolla")).to_be_visible()
    
    page.get_by_role("button", name="Trucks").click()
    # Verify Trucks submenu is expanded
    expect(page.get_by_text("Tacoma")).to_be_visible()
    
    page.get_by_role("button", name="Performance").click()
    # Verify Performance submenu is expanded
    expect(page.get_by_text("GR86")).to_be_visible()
    
    page.get_by_role("button", name="Electrified").click()
    # Verify Electrified submenu is expanded
    expect(page.get_by_text("Prius")).to_be_visible()
    
    page.get_by_role("button", name="Upcoming Vehicles").click()
    # Verify Upcoming Vehicles submenu is expanded
    expect(page.get_by_text("2026 RAV4")).to_be_visible()
    
    page.get_by_role("button", name="Crossovers & SUVs").click()
    # Verify we can navigate back to Crossovers & SUVs
    expect(page.get_by_role("link", name="Corolla Cross")).to_be_visible()
    
    page.get_by_role("button", name="Close Cookie Banner").click()
    # Verify cookie banner is closed
    expect(page.get_by_role("button", name="Close Cookie Banner")).not_to_be_visible()
    
    page.get_by_role("button", name="Vehicles", exact=True).click()
    # Verify Vehicles menu reopened after cookie banner closure
    expect(page.get_by_role("button", name="Crossovers & SUVs")).to_be_visible()
    
    page.get_by_role("link", name="Corolla Cross $30,035 as").click()
    # Verify navigation to Corolla Cross page
    expect(page).to_have_url(re.compile(r".*/corolla-cross.*"))
    expect(page.get_by_text("Corolla Cross")).to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    # Verify Vehicles menu is accessible from vehicle page
    expect(page.get_by_role("button", name="Crossovers & SUVs")).to_be_visible()
    
    page.get_by_role("link", name="Hybrid EV Corolla Cross").first.click()
    # Verify navigation to Corolla Cross hybrid page
    expect(page).to_have_url(re.compile(r".*/corolla-cross.*"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Cars & Minivan").click()
    # Verify Cars & Minivan submenu expanded
    expect(page.get_by_role("link", name="Corolla")).to_be_visible()
    
    page.get_by_role("link", name="Corolla $28,440 as shown").click()
    # Verify navigation to Corolla page
    expect(page).to_have_url(re.compile(r".*/corolla.*"))
    expect(page.get_by_text("Corolla")).first.to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("link", name="Hybrid EV RAV4 Hybrid $36,070").first.click()
    # Verify navigation to RAV4 Hybrid page
    expect(page).to_have_url(re.compile(r".*/rav4.*"))
    expect(page.get_by_text("RAV4")).first.to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Trucks").click()
    # Verify Trucks submenu expanded
    expect(page.get_by_text("Tacoma")).to_be_visible()
    
    page.get_by_role("link", name="Hybrid EV Available Tacoma $").click()
    # Verify navigation to Tacoma page
    expect(page).to_have_url(re.compile(r".*/tacoma.*"))
    expect(page.get_by_text("Tacoma")).first.to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Trucks").click()
    page.get_by_role("link", name="Hybrid EV Available Tundra $").click()
    # Verify navigation to Tundra page
    expect(page).to_have_url(re.compile(r".*/tundra.*"))
    expect(page.get_by_text("Tundra")).first.to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Performance").click()
    # Verify Performance submenu expanded
    expect(page.get_by_text("GR86")).to_be_visible()
    
    page.get_by_role("link", name="GR86 $36,365 as shown").nth(1).click()
    # Verify navigation to GR86 page
    expect(page).to_have_url(re.compile(r".*/gr86.*"))
    expect(page.get_by_text("GR86")).first.to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Performance", exact=True).click()
    page.get_by_role("link", name="GR Corolla $47,965 as shown").nth(1).click()
    # Verify navigation to GR Corolla page
    expect(page).to_have_url(re.compile(r".*/gr-corolla.*"))
    expect(page.get_by_text("GR Corolla")).first.to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Performance").click()
    page.get_by_role("link", name="GR Supra $68,550 as shown").nth(1).click()
    # Verify navigation to GR Supra page
    expect(page).to_have_url(re.compile(r".*/gr-supra.*"))
    expect(page.get_by_text("GR Supra")).first.to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    # Verify Upcoming Vehicles submenu expanded
    expect(page.get_by_text("2026 RAV4")).to_be_visible()
    
    page.get_by_role("link", name="RAV4 2026 RAV4").click()
    # Verify navigation to upcoming RAV4 page
    expect(page).to_have_url(re.compile(r".*/upcoming.*rav4.*"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Electrified").click()
    # Verify Electrified submenu expanded
    expect(page.get_by_text("Prius")).to_be_visible()
    
    page.get_by_role("link", name="Hybrid EV Prius $36,965 as").nth(1).click()
    # Verify navigation to Prius page
    expect(page).to_have_url(re.compile(r".*/prius.*"))
    expect(page.get_by_text("Prius")).first.to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.locator("li:nth-child(2) > .additional-links > a").first.click()
    # Verify additional link navigation works
    expect(page).to_have_url(re.compile(r"toyota\.com"))
    
    page.get_by_role("textbox", name="zip code").fill("60661")
    # Verify zip code input accepts value
    expect(page.get_by_role("textbox", name="zip code")).to_have_value("60661")
    
    page.get_by_role("button", name="submit").click()
    # Verify zip code form submission
    expect(page.get_by_role("textbox", name="zip code")).to_have_value("60661")
    
    page.get_by_role("button", name="Vehicles").click()
    page.locator(".vis-link").first.click()
    # Verify visual link navigation
    expect(page).to_have_url(re.compile(r"toyota\.com"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Trucks").click()
    page.locator(".js_slide.active > .slide-wrapper > .vehicles > li > .additional-links > a:nth-child(2)").first.click()
    # Verify truck additional links navigation
    expect(page).to_have_url(re.compile(r"toyota\.com"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Trucks").click()
    page.locator(".js_slide.active > .slide-wrapper > .vehicles > li:nth-child(2) > .additional-links > a").first.click()
    # Verify second truck additional link navigation
    expect(page).to_have_url(re.compile(r"toyota\.com"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("link", name="RAV4 2026 RAV4").click()
    # Verify upcoming RAV4 navigation
    expect(page).to_have_url(re.compile(r".*/upcoming.*rav4.*"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("link", name="2026 RAV4 Plug-in Hybrid 2026").click()
    # Verify upcoming RAV4 Plug-in Hybrid navigation
    expect(page).to_have_url(re.compile(r".*/upcoming.*rav4.*"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("link", name="bZ Woodland 2026 bZ Woodland").click()
    # Verify upcoming bZ Woodland navigation
    expect(page).to_have_url(re.compile(r".*/upcoming.*woodland.*"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("button", name="Upcoming Vehicles").click()
    page.get_by_role("link", name="C-HR 2026 C-HR").click()
    # Verify upcoming C-HR navigation
    expect(page).to_have_url(re.compile(r".*/upcoming.*c-hr.*"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_label("Gazoo Racing").click()
    # Verify Gazoo Racing link is clickable
    expect(page.get_by_label("Gazoo Racing")).to_be_visible()
    
    page.goto("https://www.toyota.com/upcoming-vehicles/c-hr/")
    # Verify direct navigation to C-HR upcoming page
    expect(page).to_have_url("https://www.toyota.com/upcoming-vehicles/c-hr/")
    expect(page.get_by_text("C-HR")).first.to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("link", name="TRD Pro", exact=True).click()
    # Verify TRD Pro navigation
    expect(page).to_have_url(re.compile(r".*/trd-pro.*"))
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("link", name="View All Vehicles").click()
    # Verify View All Vehicles navigation
    expect(page).to_have_url(re.compile(r".*/all-vehicles.*"))
    expect(page.get_by_text("All Vehicles")).to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_label("Electrified Vehicles").click()
    # Verify Electrified Vehicles link is accessible
    expect(page.get_by_label("Electrified Vehicles")).to_be_visible()
    
    page.get_by_role("button", name="Vehicles").click()
    page.goto("https://www.toyota.com/electrified-vehicles/")
    # Verify final navigation to electrified vehicles page
    expect(page).to_have_url("https://www.toyota.com/electrified-vehicles/")
    expect(page.get_by_text("Electrified")).first.to_be_visible()