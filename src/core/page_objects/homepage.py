"""
Toyota Homepage Page Object
"""
from playwright.sync_api import Page, expect

from src.core.page_objects.base_page import BasePage


class HomePage(BasePage):
    """Toyota.com homepage page object"""

    # Selectors
    HERO_SECTION = "[data-section='hero'], .hero-section, section.hero"
    HERO_CAROUSEL = "[class*='carousel'], [class*='slider']"
    MAIN_NAV = "nav[role='navigation'], .main-navigation, header nav"
    LOGO = "a[href='/'], [class*='logo'] a, header a img"
    SEARCH_BUTTON = "[aria-label*='Search'], button[class*='search']"
    MENU_BUTTON = "button[aria-label*='Menu'], .hamburger, [class*='menu-toggle']"

    # Navigation links
    VEHICLES_LINK = "a[href*='/vehicles'], nav a:has-text('Vehicles')"
    SHOPPING_TOOLS_LINK = "a[href*='/shopping-tools'], nav a:has-text('Shopping Tools')"
    OWNERS_LINK = "a[href*='/owners'], nav a:has-text('Owners')"
    SPECIAL_OFFERS_LINK = "a[href*='/special-offers'], nav a:has-text('Special Offers')"

    # Featured sections
    FEATURED_VEHICLES = "[data-section='featured-vehicles'], .featured-vehicles"
    SPECIAL_OFFERS_SECTION = "[data-section='offers'], [class*='offers']"
    BUILD_PRICE_CTA = "a[href*='/configurator'], a:has-text('Build & Price')"

    def __init__(self, page: Page):
        super().__init__(page)

    def open(self):
        """Navigate to homepage"""
        self.navigate("/")

    def is_loaded(self) -> bool:
        """Check if homepage is fully loaded"""
        try:
            self.wait_for_selector(self.MAIN_NAV, timeout=10000)
            return True
        except Exception:
            return False

    def verify_hero_section_visible(self):
        """Verify hero section is displayed"""
        expect(self.page.locator(self.HERO_SECTION).first).to_be_visible()

    def click_vehicles_nav(self):
        """Click vehicles navigation link"""
        self.click(self.VEHICLES_LINK)

    def click_shopping_tools(self):
        """Click shopping tools navigation link"""
        self.click(self.SHOPPING_TOOLS_LINK)

    def click_owners(self):
        """Click owners navigation link"""
        self.click(self.OWNERS_LINK)

    def click_special_offers(self):
        """Click special offers navigation link"""
        self.click(self.SPECIAL_OFFERS_LINK)

    def search(self, query: str):
        """
        Perform search

        Args:
            query: Search query
        """
        self.click(self.SEARCH_BUTTON)
        # Assuming search input appears after clicking search button
        self.page.keyboard.type(query)
        self.page.keyboard.press("Enter")

    def get_featured_vehicle_count(self) -> int:
        """Get number of featured vehicles displayed"""
        vehicles = self.page.locator(f"{self.FEATURED_VEHICLES} [class*='vehicle-card'], {self.FEATURED_VEHICLES} .vehicle")
        return vehicles.count()

    def click_build_and_price(self):
        """Click build and price CTA"""
        self.click(self.BUILD_PRICE_CTA)

    def verify_navigation_visible(self):
        """Verify main navigation is visible"""
        expect(self.page.locator(self.MAIN_NAV).first).to_be_visible()

    def verify_logo_visible(self):
        """Verify Toyota logo is visible"""
        expect(self.page.locator(self.LOGO).first).to_be_visible()

    def open_mobile_menu(self):
        """Open mobile navigation menu"""
        if self.is_visible(self.MENU_BUTTON):
            self.click(self.MENU_BUTTON)

    def verify_special_offers_section_visible(self):
        """Verify special offers section is displayed"""
        self.scroll_to_element(self.SPECIAL_OFFERS_SECTION)
        expect(self.page.locator(self.SPECIAL_OFFERS_SECTION).first).to_be_visible()
