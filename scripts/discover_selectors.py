#!/usr/bin/env python3
"""
Selector Discovery Script - Extract Real Selectors from Toyota.com

This script uses Playwright to browse the live site and discover
accurate selectors for test generation.
"""
import json
from playwright.sync_api import sync_playwright
from typing import Dict, List, Any


def discover_page_elements(page, url: str, element_descriptions: Dict[str, str]) -> Dict[str, Any]:
    """
    Navigate to a page and discover selectors for specified elements

    Args:
        page: Playwright page object
        url: URL to navigate to
        element_descriptions: Dict of element_name -> description/strategy

    Returns:
        Dict containing discovered selectors
    """
    print(f"\n🔍 Discovering selectors for: {url}")
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(2000)  # Wait for dynamic content

    discovered = {
        "url": url,
        "elements": {}
    }

    for element_name, description in element_descriptions.items():
        print(f"   Looking for: {element_name} ({description})")

        # Try multiple selector strategies
        selectors = []

        # Strategy 1: Try common patterns
        if "logo" in element_name.lower():
            candidates = [
                "img[alt*='Toyota' i]",
                "img[alt*='logo' i]",
                ".header img",
                "header img",
                "[class*='logo'] img"
            ]
        elif "menu" in element_name.lower():
            candidates = [
                "button[aria-label*='menu' i]",
                "[aria-label*='navigation' i]",
                ".menu-button",
                ".hamburger",
                "button.nav-toggle"
            ]
        elif "search" in element_name.lower():
            candidates = [
                "button[aria-label*='search' i]",
                "input[type='search']",
                "[class*='search']",
                "#search"
            ]
        elif "vehicles" in element_name.lower():
            candidates = [
                "a[href*='vehicles']",
                "nav >> text=/vehicles/i",
                "[data-analytics*='vehicles']"
            ]
        elif "zip" in element_name.lower():
            candidates = [
                "input[name='zip']",
                "input[name='zipCode']",
                "input[id*='zip' i]",
                "input[placeholder*='zip' i]",
                "input[type='text'][maxlength='5']"
            ]
        else:
            candidates = [description]

        # Test each candidate selector
        for selector in candidates:
            try:
                element = page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    selectors.append(selector)
                    print(f"      ✅ Found: {selector}")
                    break
            except:
                continue

        if not selectors:
            # Try AI-like text search as fallback
            try:
                text_locator = page.get_by_text(description, exact=False).first
                if text_locator.count() > 0:
                    selector = f"text=/{description}/i"
                    selectors.append(selector)
                    print(f"      ✅ Found (text): {selector}")
            except:
                print(f"      ❌ Not found")

        discovered["elements"][element_name] = {
            "description": description,
            "selectors": selectors,
            "found": len(selectors) > 0
        }

    return discovered


def main():
    print("="*70)
    print("🤖 SELECTOR DISCOVERY SCRIPT")
    print("="*70)

    all_discoveries = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Homepage elements
        homepage_elements = {
            "logo": "Toyota logo",
            "menu_button": "Menu button",
            "search_button": "Search button",
            "vehicles_link": "Vehicles navigation link"
        }
        all_discoveries["homepage"] = discover_page_elements(
            page, "https://www.toyota.com", homepage_elements
        )

        # Vehicles page elements
        vehicles_elements = {
            "page_heading": "All Vehicles",
            "first_vehicle_card": "First vehicle card",
            "vehicle_grid": "Vehicle grid container"
        }
        all_discoveries["vehicles"] = discover_page_elements(
            page, "https://www.toyota.com/vehicles", vehicles_elements
        )

        # Dealers page elements
        dealers_elements = {
            "zip_input": "Zip code input",
            "search_button": "Search button",
            "dealer_results": "Dealer results container"
        }
        all_discoveries["dealers"] = discover_page_elements(
            page, "https://www.toyota.com/dealers", dealers_elements
        )

        browser.close()

    # Save discoveries
    output_file = "test_data/discovered_selectors.json"
    with open(output_file, "w") as f:
        json.dump(all_discoveries, f, indent=2)

    print(f"\n{'='*70}")
    print(f"✅ Selector discovery complete!")
    print(f"📝 Saved to: {output_file}")
    print(f"{'='*70}\n")

    # Print summary
    print("Summary:")
    for page_name, data in all_discoveries.items():
        found = sum(1 for e in data["elements"].values() if e["found"])
        total = len(data["elements"])
        print(f"  {page_name}: {found}/{total} elements found")


if __name__ == "__main__":
    main()
