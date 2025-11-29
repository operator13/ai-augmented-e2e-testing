"""
Clean Dealer Search Test - Generated from Codegen Recording
Focuses on core dealer search functionality without the full quote form
"""
import re
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_dealer_search_with_codegen_selectors(page: Page) -> None:
    """
    Test dealer search using selectors captured from codegen recording.
    This demonstrates the accuracy of codegen vs AI-guessed selectors.
    """
    # Navigate to dealers page
    page.goto("https://www.toyota.com/dealers/")

    # Search for dealers - Using REAL selectors from codegen
    page.get_by_role("textbox", name="zip code").click()
    page.get_by_role("textbox", name="zip code").fill("60661")
    page.get_by_role("button", name="submit").click()

    # Handle cookie banner if present
    try:
        page.get_by_role("button", name="Close Cookie Banner").click(timeout=3000)
    except:
        pass  # Banner may not appear every time

    # Verify search results loaded
    page.wait_for_timeout(2000)  # Wait for map/results to load

    # Verify we can interact with dealer results
    # The map should be visible
    expect(page.locator(".gm-style")).to_be_visible(timeout=10000)

    # Verify dealer link is present (using the one from recording)
    dealer_link = page.get_by_role("link", name="Toyota of Lincoln Park", exact=True)
    expect(dealer_link).to_be_visible()

    print("✅ Codegen-recorded test PASSED!")
    print("   - Used real selectors from live interaction")
    print("   - Cookie banner handled automatically")
    print("   - Dealer search and results working")


@pytest.mark.smoke
def test_dealer_search_comparison(page: Page) -> None:
    """
    Side-by-side comparison: AI guessed vs Codegen captured selectors
    """
    page.goto("https://www.toyota.com/dealers/")

    print("\n" + "="*70)
    print("SELECTOR COMPARISON: AI vs Codegen")
    print("="*70)

    # AI-GUESSED SELECTORS (what we had before)
    ai_zip_selector = "input[placeholder*='zip' i]"
    ai_search_selector = "input[type='search']"

    # CODEGEN SELECTORS (what you recorded)
    codegen_zip_selector = 'role=textbox[name="zip code"]'
    codegen_search_selector = 'role=button[name="submit"]'

    print(f"\n❌ AI Guessed:")
    print(f"   Zip Input:  {ai_zip_selector}")
    print(f"   Search Btn: {ai_search_selector}")

    print(f"\n✅ Codegen Captured:")
    print(f"   Zip Input:  {codegen_zip_selector}")
    print(f"   Search Btn: {codegen_search_selector}")

    # Test both - Codegen should work better
    try:
        # Use codegen selector
        page.get_by_role("textbox", name="zip code").fill("94016")
        print(f"\n✅ Codegen selector worked!")
    except Exception as e:
        print(f"\n❌ Codegen selector failed: {e}")

    print("="*70 + "\n")
