"""
MCP (Model Context Protocol) Integration

Integrates with Claude Code's Playwright MCP server for:
- Real-time test execution
- Live selector discovery
- Interactive test generation
- Visual validation
"""
import json
from typing import Any, Dict, List, Optional

import requests
from playwright.sync_api import Page

from src.config.settings import settings


class MCPClient:
    """Client for interacting with Playwright MCP server"""

    def __init__(self, server_url: Optional[str] = None):
        """
        Initialize MCP client

        Args:
            server_url: MCP server URL (defaults to settings)
        """
        self.server_url = server_url or f"http://{settings.mcp_server_url}"
        self.enabled = settings.mcp_enabled

    def execute_action(
        self, page: Page, action: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a Playwright action through MCP

        Args:
            page: Playwright page object
            action: Action to execute (click, fill, navigate, etc.)
            params: Action parameters

        Returns:
            Result from MCP server
        """
        if not self.enabled:
            return {"error": "MCP integration is disabled"}

        payload = {
            "action": action,
            "params": params or {},
            "page_url": page.url,
        }

        try:
            response = requests.post(
                f"{self.server_url}/execute", json=payload, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"MCP request failed: {str(e)}"}

    def discover_selectors(self, page: Page, element_description: str) -> List[str]:
        """
        Use MCP to discover selectors for an element

        Args:
            page: Playwright page object
            element_description: Description of element to find

        Returns:
            List of suggested selectors
        """
        if not self.enabled:
            return []

        payload = {
            "action": "discover_selectors",
            "params": {
                "description": element_description,
                "page_url": page.url,
            },
        }

        try:
            response = requests.post(
                f"{self.server_url}/selectors", json=payload, timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("selectors", [])
        except requests.RequestException as e:
            print(f"MCP selector discovery failed: {e}")
            return []

    def generate_test_code(
        self, page: Page, recorded_actions: List[Dict]
    ) -> Optional[str]:
        """
        Generate test code from recorded actions

        Args:
            page: Playwright page object
            recorded_actions: List of recorded actions

        Returns:
            Generated test code
        """
        if not self.enabled:
            return None

        payload = {
            "action": "generate_test",
            "params": {
                "actions": recorded_actions,
                "page_url": page.url,
            },
        }

        try:
            response = requests.post(
                f"{self.server_url}/generate", json=payload, timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("test_code")
        except requests.RequestException as e:
            print(f"MCP test generation failed: {e}")
            return None

    def validate_element(
        self, page: Page, selector: str
    ) -> Dict[str, Any]:
        """
        Validate an element through MCP

        Args:
            page: Playwright page object
            selector: Element selector

        Returns:
            Validation result
        """
        if not self.enabled:
            return {"valid": False, "error": "MCP disabled"}

        payload = {
            "action": "validate_element",
            "params": {
                "selector": selector,
                "page_url": page.url,
            },
        }

        try:
            response = requests.post(
                f"{self.server_url}/validate", json=payload, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"valid": False, "error": str(e)}

    def get_page_snapshot(self, page: Page) -> Dict[str, Any]:
        """
        Get a snapshot of current page state through MCP

        Args:
            page: Playwright page object

        Returns:
            Page snapshot data
        """
        if not self.enabled:
            return {}

        payload = {
            "action": "snapshot",
            "params": {"page_url": page.url},
        }

        try:
            response = requests.post(
                f"{self.server_url}/snapshot", json=payload, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"MCP snapshot failed: {e}")
            return {}

    def health_check(self) -> bool:
        """
        Check if MCP server is accessible

        Returns:
            True if server is healthy
        """
        if not self.enabled:
            return False

        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False


class ActionRecorder:
    """Records user actions for test generation"""

    def __init__(self, page: Page, mcp_client: Optional[MCPClient] = None):
        """
        Initialize action recorder

        Args:
            page: Playwright page object
            mcp_client: Optional MCP client instance
        """
        self.page = page
        self.mcp_client = mcp_client or MCPClient()
        self.recorded_actions: List[Dict] = []
        self.recording = False

    def start_recording(self):
        """Start recording actions"""
        self.recording = True
        self.recorded_actions = []
        print("Action recording started")

    def stop_recording(self):
        """Stop recording actions"""
        self.recording = False
        print(f"Action recording stopped. Recorded {len(self.recorded_actions)} actions")

    def record_action(
        self,
        action_type: str,
        selector: Optional[str] = None,
        value: Optional[str] = None,
        **kwargs,
    ):
        """
        Record an action

        Args:
            action_type: Type of action (click, fill, navigate, etc.)
            selector: Element selector
            value: Input value (for fill actions)
            **kwargs: Additional action metadata
        """
        if not self.recording:
            return

        action = {
            "type": action_type,
            "selector": selector,
            "value": value,
            "page_url": self.page.url,
            "timestamp": json.loads(json.dumps({"time": "now"})),  # Placeholder
            **kwargs,
        }
        self.recorded_actions.append(action)

    def click(self, selector: str, **kwargs):
        """Record a click action"""
        self.record_action("click", selector=selector, **kwargs)
        return self.page.locator(selector).click(**kwargs)

    def fill(self, selector: str, value: str, **kwargs):
        """Record a fill action"""
        self.record_action("fill", selector=selector, value=value, **kwargs)
        return self.page.locator(selector).fill(value, **kwargs)

    def navigate(self, url: str, **kwargs):
        """Record a navigation action"""
        self.record_action("navigate", value=url, **kwargs)
        return self.page.goto(url, **kwargs)

    def select_option(self, selector: str, value: str, **kwargs):
        """Record a select option action"""
        self.record_action("select", selector=selector, value=value, **kwargs)
        return self.page.locator(selector).select_option(value, **kwargs)

    def check(self, selector: str, **kwargs):
        """Record a check action"""
        self.record_action("check", selector=selector, **kwargs)
        return self.page.locator(selector).check(**kwargs)

    def uncheck(self, selector: str, **kwargs):
        """Record an uncheck action"""
        self.record_action("uncheck", selector=selector, **kwargs)
        return self.page.locator(selector).uncheck(**kwargs)

    def get_recorded_actions(self) -> List[Dict]:
        """Get list of recorded actions"""
        return self.recorded_actions.copy()

    def generate_test_from_recording(self) -> Optional[str]:
        """
        Generate test code from recorded actions using MCP

        Returns:
            Generated test code
        """
        if not self.recorded_actions:
            print("No actions recorded")
            return None

        if self.mcp_client.enabled:
            return self.mcp_client.generate_test_code(self.page, self.recorded_actions)
        else:
            # Fallback to simple code generation
            return self._generate_test_code_fallback()

    def _generate_test_code_fallback(self) -> str:
        """Fallback test code generation without MCP"""
        lines = [
            "import pytest",
            "from playwright.sync_api import Page",
            "",
            "def test_recorded_flow(page: Page):",
        ]

        for action in self.recorded_actions:
            action_type = action["type"]
            selector = action.get("selector")
            value = action.get("value")

            if action_type == "navigate":
                lines.append(f'    page.goto("{value}")')
            elif action_type == "click":
                lines.append(f'    page.locator("{selector}").click()')
            elif action_type == "fill":
                lines.append(f'    page.locator("{selector}").fill("{value}")')
            elif action_type == "select":
                lines.append(f'    page.locator("{selector}").select_option("{value}")')
            elif action_type == "check":
                lines.append(f'    page.locator("{selector}").check()')
            elif action_type == "uncheck":
                lines.append(f'    page.locator("{selector}").uncheck()')

        return "\n".join(lines)

    def save_recording(self, output_file: str):
        """Save recorded actions to file"""
        with open(output_file, "w") as f:
            json.dump(self.recorded_actions, f, indent=2)
        print(f"Recording saved to {output_file}")

    def load_recording(self, input_file: str):
        """Load recorded actions from file"""
        with open(input_file, "r") as f:
            self.recorded_actions = json.load(f)
        print(f"Loaded {len(self.recorded_actions)} actions from {input_file}")
