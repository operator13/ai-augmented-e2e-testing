"""
Base Page Object

Provides common functionality for all page objects with AI-powered features.
"""
from typing import Optional

from playwright.sync_api import Page, expect

from src.ai.self_healing import SelectorHealer
from src.config.settings import settings


class BasePage:
    """Base page object with AI-enhanced capabilities"""

    def __init__(self, page: Page):
        """
        Initialize base page

        Args:
            page: Playwright page object
        """
        self.page = page
        self.base_url = settings.base_url

        # Initialize self-healing selector system
        if settings.enable_self_healing:
            self.selector_healer = SelectorHealer(page)
        else:
            self.selector_healer = None

    def navigate(self, path: str = "/"):
        """
        Navigate to a page

        Args:
            path: URL path relative to base_url
        """
        url = f"{self.base_url}{path}" if path.startswith("/") else path
        self.page.goto(url)
        self.wait_for_page_load()

    def wait_for_page_load(self, timeout: int = 30000):
        """Wait for page to fully load"""
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    def find_element(self, selector: str, use_healing: bool = True):
        """
        Find element with optional self-healing

        Args:
            selector: Element selector
            use_healing: Use self-healing if selector fails

        Returns:
            Playwright Locator
        """
        if use_healing and self.selector_healer:
            return self.selector_healer.find_element(selector)
        return self.page.locator(selector)

    def click(self, selector: str, timeout: int = 10000):
        """
        Click an element

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
        """
        element = self.find_element(selector)
        element.click(timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = 10000):
        """
        Fill an input field

        Args:
            selector: Element selector
            value: Value to fill
            timeout: Timeout in milliseconds
        """
        element = self.find_element(selector)
        element.fill(value, timeout=timeout)

    def get_text(self, selector: str) -> str:
        """
        Get text content of an element

        Args:
            selector: Element selector

        Returns:
            Text content
        """
        element = self.find_element(selector)
        return element.text_content() or ""

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Check if element is visible

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds

        Returns:
            True if visible
        """
        try:
            element = self.find_element(selector)
            return element.is_visible(timeout=timeout)
        except Exception:
            return False

    def wait_for_selector(self, selector: str, timeout: int = 10000):
        """
        Wait for selector to appear

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
        """
        element = self.find_element(selector)
        element.wait_for(state="visible", timeout=timeout)

    def scroll_to_element(self, selector: str):
        """
        Scroll to an element

        Args:
            selector: Element selector
        """
        element = self.find_element(selector)
        element.scroll_into_view_if_needed()

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """
        Get element attribute value

        Args:
            selector: Element selector
            attribute: Attribute name

        Returns:
            Attribute value or None
        """
        element = self.find_element(selector)
        return element.get_attribute(attribute)

    def select_dropdown(self, selector: str, value: str):
        """
        Select dropdown option

        Args:
            selector: Dropdown selector
            value: Option value
        """
        element = self.find_element(selector)
        element.select_option(value)

    def check_checkbox(self, selector: str):
        """
        Check a checkbox

        Args:
            selector: Checkbox selector
        """
        element = self.find_element(selector)
        if not element.is_checked():
            element.check()

    def uncheck_checkbox(self, selector: str):
        """
        Uncheck a checkbox

        Args:
            selector: Checkbox selector
        """
        element = self.find_element(selector)
        if element.is_checked():
            element.uncheck()

    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url

    def get_title(self) -> str:
        """Get page title"""
        return self.page.title()

    def take_screenshot(self, name: str, full_page: bool = False) -> str:
        """
        Take a screenshot

        Args:
            name: Screenshot name
            full_page: Capture full page

        Returns:
            Screenshot path
        """
        from pathlib import Path

        screenshot_dir = Path("screenshots")
        screenshot_dir.mkdir(exist_ok=True)
        screenshot_path = screenshot_dir / f"{name}.png"

        self.page.screenshot(path=str(screenshot_path), full_page=full_page)
        return str(screenshot_path)

    def wait_for_navigation(self, timeout: int = 30000):
        """Wait for navigation to complete"""
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    def assert_text_visible(self, text: str):
        """
        Assert that text is visible on page

        Args:
            text: Text to find
        """
        expect(self.page.get_by_text(text)).to_be_visible()

    def assert_url_contains(self, url_fragment: str):
        """
        Assert that current URL contains fragment

        Args:
            url_fragment: URL fragment to check
        """
        expect(self.page).to_have_url(f".*{url_fragment}.*")

    def assert_title_contains(self, title_fragment: str):
        """
        Assert that page title contains fragment

        Args:
            title_fragment: Title fragment to check
        """
        expect(self.page).to_have_title(f".*{title_fragment}.*")
