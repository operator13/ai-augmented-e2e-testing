"""
Simple Homepage Test - Your First Test!

This test runs without requiring the full AI framework.
"""
import re
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_toyota_homepage_loads(page: Page):
    """Test that Toyota homepage loads successfully"""
    # Navigate to Toyota homepage
    page.goto("https://www.toyota.com")

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    # Verify title contains "Toyota"
    expect(page).to_have_title(re.compile("Toyota", re.IGNORECASE))

    # Verify URL
    assert "toyota.com" in page.url

    print(f"\n✅ Toyota homepage loaded successfully!")
    print(f"   URL: {page.url}")
    print(f"   Title: {page.title()}")


@pytest.mark.smoke
def test_toyota_homepage_has_navigation(page: Page):
    """Test that homepage has main navigation"""
    page.goto("https://www.toyota.com")
    page.wait_for_load_state("networkidle")

    # Check for navigation element (flexible selector)
    nav = page.locator("nav, header").first
    expect(nav).to_be_visible()

    print(f"\n✅ Navigation is visible!")


@pytest.mark.smoke
def test_toyota_homepage_has_logo(page: Page):
    """Test that Toyota logo is visible"""
    page.goto("https://www.toyota.com")
    page.wait_for_load_state("networkidle")

    # Look for logo (flexible - could be image or link)
    logo = page.locator("img[alt*='Toyota'], a[aria-label*='Toyota'], [class*='logo']").first

    # Give it a moment to appear
    logo.wait_for(state="visible", timeout=10000)

    expect(logo).to_be_visible()

    print(f"\n✅ Toyota logo is visible!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
