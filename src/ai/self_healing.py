"""
Self-Healing Selector System

Automatically detects and fixes broken selectors using AI and multiple fallback strategies.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from anthropic import Anthropic
from openai import OpenAI
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from src.config.constants import SelectorStrategy
from src.config.settings import settings


class SelectorHealer:
    """Heal broken selectors using AI and fallback strategies"""

    def __init__(self, page: Page, use_claude: bool = True):
        """
        Initialize the selector healer

        Args:
            page: Playwright page object
            use_claude: Use Claude instead of GPT
        """
        self.page = page
        self.use_claude = use_claude
        self.selector_history: Dict[str, List[str]] = {}
        self.selector_db_path = Path("test_data/selectors.json")

        # Initialize AI client
        if use_claude and settings.anthropic_api_key:
            self.ai_client = Anthropic(api_key=settings.anthropic_api_key)
            self.ai_model = settings.claude_model
        elif settings.openai_api_key:
            self.ai_client = OpenAI(api_key=settings.openai_api_key)
            self.ai_model = settings.ai_model
            self.use_claude = False
        else:
            self.ai_client = None

        self._load_selector_database()

    def find_element(
        self, selector: str, timeout: int = 5000, auto_heal: bool = True
    ) -> Optional[Any]:
        """
        Find element with automatic healing if selector fails

        Args:
            selector: CSS selector or locator string
            timeout: Timeout in milliseconds
            auto_heal: Automatically attempt to heal if selector fails

        Returns:
            Element locator or None
        """
        try:
            # Try primary selector
            element = self.page.locator(selector)
            element.wait_for(timeout=timeout)
            self._record_successful_selector(selector)
            return element
        except PlaywrightTimeoutError:
            if not auto_heal or not settings.enable_self_healing:
                raise

            print(f"Selector failed: {selector}")
            print("Attempting to heal selector...")

            # Try healing
            healed_selector = self.heal_selector(selector, timeout)
            if healed_selector:
                print(f"Selector healed: {healed_selector}")
                self._save_healed_selector(selector, healed_selector)
                element = self.page.locator(healed_selector)
                element.wait_for(timeout=timeout)
                return element

            raise

    def heal_selector(self, failed_selector: str, timeout: int = 5000) -> Optional[str]:
        """
        Attempt to heal a failed selector using multiple strategies

        Args:
            failed_selector: The selector that failed
            timeout: Timeout for each attempt

        Returns:
            Working selector or None
        """
        strategies = [
            self._try_fallback_selectors,
            self._try_semantic_selectors,
            self._try_ai_suggested_selectors,
            self._try_fuzzy_text_match,
            self._try_position_based,
        ]

        for strategy in strategies:
            healed_selector = strategy(failed_selector, timeout)
            if healed_selector:
                return healed_selector

        return None

    def _try_fallback_selectors(self, selector: str, timeout: int) -> Optional[str]:
        """Try known fallback selectors from history"""
        if selector in self.selector_history:
            for fallback in self.selector_history[selector]:
                try:
                    self.page.locator(fallback).wait_for(timeout=timeout)
                    return fallback
                except PlaywrightTimeoutError:
                    continue
        return None

    def _try_semantic_selectors(self, selector: str, timeout: int) -> Optional[str]:
        """Try semantic HTML and ARIA-based selectors"""
        # Extract text content or identifying information
        text_match = re.search(r'text=["\']([^"\']+)["\']', selector)
        id_match = re.search(r'#([\w-]+)', selector)
        class_match = re.search(r'\.([\w-]+)', selector)

        alternatives = []

        # Try different semantic approaches
        if text_match:
            text = text_match.group(1)
            alternatives.extend(
                [
                    f"text={text}",
                    f'[aria-label="{text}"]',
                    f'button:has-text("{text}")',
                    f'a:has-text("{text}")',
                    f'//*[contains(text(), "{text}")]',
                ]
            )

        if id_match:
            id_val = id_match.group(1)
            alternatives.extend([f"#{id_val}", f'[id="{id_val}"]', f'//*[@id="{id_val}"]'])

        if class_match:
            class_val = class_match.group(1)
            alternatives.extend(
                [
                    f".{class_val}",
                    f'[class*="{class_val}"]',
                    f'[role][class*="{class_val}"]',
                ]
            )

        # Try ARIA roles
        common_roles = ["button", "link", "navigation", "main", "article", "search"]
        for role in common_roles:
            alternatives.append(f'[role="{role}"]')

        return self._test_selectors(alternatives, timeout)

    def _try_ai_suggested_selectors(self, selector: str, timeout: int) -> Optional[str]:
        """Use AI to suggest alternative selectors"""
        if not self.ai_client:
            return None

        try:
            # Get page HTML context
            html_snippet = self._get_html_context(selector)

            prompt = f"""
            The following selector failed to find an element:
            {selector}

            Here's the relevant HTML context:
            ```html
            {html_snippet}
            ```

            Suggest 5 alternative selectors that would be more resilient, prioritizing:
            1. Semantic HTML attributes (role, aria-label, etc.)
            2. Data attributes (data-testid, data-qa, etc.)
            3. Stable text content
            4. Specific element types with clear context

            Return only a JSON array of selector strings, no explanation:
            ["selector1", "selector2", "selector3", "selector4", "selector5"]
            """

            response = self._call_ai(prompt, max_tokens=500)
            suggestions = self._extract_json(response)

            if isinstance(suggestions, list):
                return self._test_selectors(suggestions, timeout)

        except Exception as e:
            print(f"AI selector suggestion failed: {e}")

        return None

    def _try_fuzzy_text_match(self, selector: str, timeout: int) -> Optional[str]:
        """Try fuzzy text matching"""
        # Extract potential text content
        text_patterns = [
            r'text=["\']([^"\']+)["\']',
            r':has-text\(["\']([^"\']+)["\']\)',
            r'contains\(text\(\),\s*["\']([^"\']+)["\']\)',
        ]

        for pattern in text_patterns:
            match = re.search(pattern, selector)
            if match:
                text = match.group(1)
                # Try partial text match
                alternatives = [
                    f'text=/{text}/i',  # Case insensitive
                    f':has-text("{text[:10]}")',  # First 10 chars
                    f'//*[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{text.lower()}")]',
                ]
                result = self._test_selectors(alternatives, timeout)
                if result:
                    return result

        return None

    def _try_position_based(self, selector: str, timeout: int) -> Optional[str]:
        """Try position-based selectors as last resort"""
        # This is least stable but sometimes necessary
        base_selectors = ["button", "a", "input", "div", "span"]

        alternatives = []
        for base in base_selectors:
            alternatives.extend(
                [
                    f"{base}:first-child",
                    f"{base}:last-child",
                    f"{base}:nth-child(1)",
                    f"{base}:nth-child(2)",
                ]
            )

        return self._test_selectors(alternatives, timeout)

    def _test_selectors(self, selectors: List[str], timeout: int) -> Optional[str]:
        """Test a list of selectors and return first working one"""
        for sel in selectors:
            try:
                self.page.locator(sel).wait_for(timeout=timeout)
                return sel
            except (PlaywrightTimeoutError, Exception):
                continue
        return None

    def _get_html_context(self, selector: str, context_size: int = 500) -> str:
        """Get HTML context around the failed selector"""
        try:
            # Get page HTML
            html = self.page.content()

            # Try to find similar elements or context
            # This is simplified - in production, you'd want more sophisticated parsing
            return html[:context_size] if len(html) > context_size else html

        except Exception:
            return ""

    def _call_ai(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call AI API"""
        if self.use_claude:
            response = self.ai_client.messages.create(
                model=self.ai_model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        else:
            response = self.ai_client.chat.completions.create(
                model=self.ai_model, messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens
            )
            return response.choices[0].message.content

    def _extract_json(self, text: str) -> Any:
        """Extract JSON from AI response"""
        json_match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        return None

    def _record_successful_selector(self, selector: str):
        """Record a successful selector use"""
        if selector not in self.selector_history:
            self.selector_history[selector] = []

    def _save_healed_selector(self, original: str, healed: str):
        """Save healed selector to history and database"""
        if original not in self.selector_history:
            self.selector_history[original] = []

        if healed not in self.selector_history[original]:
            self.selector_history[original].insert(0, healed)

        self._save_selector_database()

    def _load_selector_database(self):
        """Load selector database from file"""
        if self.selector_db_path.exists():
            try:
                with open(self.selector_db_path, "r") as f:
                    self.selector_history = json.load(f)
            except Exception as e:
                print(f"Failed to load selector database: {e}")
                self.selector_history = {}
        else:
            self.selector_history = {}

    def _save_selector_database(self):
        """Save selector database to file"""
        self.selector_db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.selector_db_path, "w") as f:
                json.dump(self.selector_history, f, indent=2)
        except Exception as e:
            print(f"Failed to save selector database: {e}")

    def generate_robust_selector(self, element_description: str) -> List[str]:
        """
        Generate multiple robust selector options for an element

        Args:
            element_description: Description of the element to find

        Returns:
            List of suggested selectors in order of preference
        """
        if not self.ai_client:
            return []

        prompt = f"""
        Generate robust Playwright selectors for the following element:
        {element_description}

        Create 5 different selector strategies, prioritizing:
        1. ARIA roles and labels
        2. Data attributes (data-testid)
        3. Semantic HTML
        4. Stable text content
        5. CSS classes (as last resort)

        Return as JSON array of objects:
        [
            {{"selector": "selector string", "strategy": "strategy name", "reliability": "high|medium|low"}}
        ]
        """

        response = self._call_ai(prompt)
        suggestions = self._extract_json(response)

        if isinstance(suggestions, list):
            return [s.get("selector") for s in suggestions if "selector" in s]

        return []
