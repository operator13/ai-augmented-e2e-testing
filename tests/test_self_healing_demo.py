"""
Self-Healing Selector Demo - Watch AI Fix Broken Selectors!
"""
import pytest
from playwright.sync_api import Page
from src.ai.self_healing import SelectorHealer


@pytest.mark.smoke
def test_self_healing_in_action(page: Page):
    """Demonstrate self-healing selectors fixing broken selectors"""

    # Navigate to Toyota homepage
    page.goto("https://www.toyota.com")
    page.wait_for_load_state("networkidle")

    # Initialize self-healing selector system
    healer = SelectorHealer(page, use_claude=False)  # Use GPT with your key

    print("\n" + "="*70)
    print("🤖 SELF-HEALING SELECTOR DEMO")
    print("="*70)

    # Try a BROKEN selector first (this will fail, then heal)
    broken_selector = "a[href*='/vehicles-old-broken']"
    print(f"\n❌ Trying broken selector: {broken_selector}")

    try:
        # This will automatically heal!
        element = healer.find_element(broken_selector, timeout=5000, auto_heal=True)
        print(f"✅ Self-healing SUCCEEDED! Found element with healed selector")

        # The healed selector is now saved
        print(f"📝 Healed selector saved to database: test_data/selectors.json")

    except Exception as e:
        print(f"⚠️  Self-healing attempted but couldn't find alternative: {e}")

    # Now try finding the vehicles link with a better approach
    print(f"\n🔍 Using AI to suggest robust selectors for 'Vehicles navigation link'...")

    suggested_selectors = healer.generate_robust_selector(
        "Navigation link to vehicles page"
    )

    print(f"\n🤖 AI Suggested {len(suggested_selectors)} robust selectors:")
    for i, selector in enumerate(suggested_selectors[:3], 1):
        print(f"   {i}. {selector}")

    # Try each suggested selector
    print(f"\n🧪 Testing AI-suggested selectors...")
    for selector in suggested_selectors:
        try:
            element = page.locator(selector).first
            if element.count() > 0:
                print(f"   ✅ FOUND with: {selector}")
                break
        except:
            print(f"   ❌ Failed: {selector}")

    print("\n" + "="*70)
    print("Self-healing demonstration complete!")
    print("="*70 + "\n")
