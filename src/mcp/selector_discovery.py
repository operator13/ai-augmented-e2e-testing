"""
MCP-based Selector Discovery Module

This module integrates Playwright MCP tools to discover selectors on toyota.com pages
and automatically update the selector database for use in self-healing tests.

Features:
- Live selector discovery using MCP Playwright tools
- Integration with existing selectors.json database
- Automatic selector validation and categorization
- Support for data attributes and ARIA selectors
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class DiscoveredSelector:
    """Represents a discovered selector with metadata"""
    selector: str
    element_type: str  # button, link, input, etc.
    text_content: str
    page_url: str
    data_attributes: Dict[str, str]
    aria_label: Optional[str]
    discovered_at: str


class MCPSelectorDiscovery:
    """
    MCP-based selector discovery system that works with Claude Code's Playwright MCP.

    This class provides utilities to discover selectors during interactive sessions
    and automatically integrate them with the test framework's selector database.
    """

    def __init__(self, selector_db_path: str = "test_data/selectors.json"):
        """
        Initialize the selector discovery system.

        Args:
            selector_db_path: Path to the selectors.json database
        """
        self.selector_db_path = Path(selector_db_path)
        self.logger = logging.getLogger(__name__)
        self.discovered_selectors: List[DiscoveredSelector] = []

    def load_selector_database(self) -> Dict[str, Any]:
        """Load existing selector database"""
        if self.selector_db_path.exists():
            with open(self.selector_db_path, 'r') as f:
                return json.load(f)
        return {}

    def save_selector_database(self, selectors: Dict[str, Any]) -> None:
        """Save selectors to database"""
        with open(self.selector_db_path, 'w') as f:
            json.dump(selectors, f, indent=2)

    def parse_mcp_discovery_results(self, mcp_results: Dict[str, List]) -> List[DiscoveredSelector]:
        """
        Parse results from MCP JavaScript selector discovery.

        Args:
            mcp_results: Results from MCP evaluate() call with selector discovery script

        Returns:
            List of DiscoveredSelector objects
        """
        discovered = []
        timestamp = datetime.utcnow().isoformat() + 'Z'

        # Parse navigation elements
        for nav_item in mcp_results.get('navigation', []):
            selector_obj = DiscoveredSelector(
                selector=nav_item.get('selector', ''),
                element_type='navigation',
                text_content=nav_item.get('text', ''),
                page_url=nav_item.get('href', ''),
                data_attributes={},
                aria_label=nav_item.get('ariaLabel'),
                discovered_at=timestamp
            )
            discovered.append(selector_obj)

        # Parse buttons
        for button in mcp_results.get('buttons', []):
            selector_obj = DiscoveredSelector(
                selector=button.get('selector', ''),
                element_type='button',
                text_content=button.get('text', ''),
                page_url='',
                data_attributes={},
                aria_label=button.get('ariaLabel'),
                discovered_at=timestamp
            )
            discovered.append(selector_obj)

        # Parse links
        for link in mcp_results.get('links', []):
            data_attrs = {}
            if link.get('dataId'):
                data_attrs['data-di-id'] = link['dataId']
            if link.get('aaLinkText'):
                data_attrs['data-aa-link-text'] = link['aaLinkText']

            selector_obj = DiscoveredSelector(
                selector=link.get('href', ''),
                element_type='link',
                text_content=link.get('text', ''),
                page_url=link.get('href', ''),
                data_attributes=data_attrs,
                aria_label=None,
                discovered_at=timestamp
            )
            discovered.append(selector_obj)

        self.discovered_selectors.extend(discovered)
        return discovered

    def categorize_selectors(self, selectors: List[DiscoveredSelector]) -> Dict[str, Any]:
        """
        Categorize discovered selectors by type and function.

        Returns:
            Dictionary with categorized selectors
        """
        categorized = {
            'navigation': {},
            'buttons': {},
            'links': {},
            'forms': {},
            'vehicles': {}
        }

        for sel in selectors:
            # Navigation items
            if sel.element_type == 'navigation':
                if sel.text_content:
                    key = sel.text_content.lower().replace(' ', '_')
                    categorized['navigation'][key] = sel.selector

            # Buttons
            elif sel.element_type == 'button':
                if sel.text_content:
                    key = sel.text_content.lower().replace(' ', '_')
                    categorized['buttons'][key] = sel.selector

            # Links
            elif sel.element_type == 'link':
                if 'vehicle' in sel.page_url.lower() or any(v in sel.page_url.lower()
                    for v in ['camry', 'corolla', 'rav4', 'tacoma', 'tundra', 'highlander']):
                    vehicle_name = self._extract_vehicle_name(sel.page_url)
                    if vehicle_name:
                        categorized['vehicles'][vehicle_name] = f"a[href*='/{vehicle_name}/']"
                elif sel.text_content:
                    key = sel.text_content.lower().replace(' ', '_')
                    categorized['links'][key] = f"a[href='{sel.page_url}']"

        return categorized

    def _extract_vehicle_name(self, url: str) -> Optional[str]:
        """Extract vehicle name from URL"""
        vehicles = ['camry', 'corolla', 'rav4', 'tacoma', 'tundra', 'highlander',
                   'prius', '4runner', 'sequoia', 'sienna', 'gr86', 'grcorolla', 'grsupra']
        for vehicle in vehicles:
            if vehicle in url.lower():
                return vehicle
        return None

    def merge_with_database(self, new_selectors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge newly discovered selectors with existing database.

        Args:
            new_selectors: Categorized selectors to merge

        Returns:
            Updated selector database
        """
        db = self.load_selector_database()

        # Update with new discoveries
        for category, selectors in new_selectors.items():
            if category in db:
                db[category].update(selectors)
            else:
                db[category] = selectors

        # Add metadata
        if 'mcp_discovery_metadata' not in db:
            db['mcp_discovery_metadata'] = []

        db['mcp_discovery_metadata'].append({
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'selectors_added': sum(len(v) for v in new_selectors.values()),
            'categories': list(new_selectors.keys())
        })

        return db

    def generate_mcp_discovery_script(self) -> str:
        """
        Generate JavaScript code to run via MCP evaluate() for selector discovery.

        Returns:
            JavaScript code as string
        """
        return """
(function() {
  const elements = {
    navigation: [],
    buttons: [],
    links: [],
    forms: [],
    interactive: []
  };

  // Get navigation items
  document.querySelectorAll('nav a, nav button').forEach(el => {
    elements.navigation.push({
      text: el.textContent.trim().substring(0, 50),
      selector: el.getAttribute('data-di-id') || el.id || el.className,
      href: el.href || '',
      ariaLabel: el.getAttribute('aria-label'),
      role: el.getAttribute('role')
    });
  });

  // Get all buttons
  document.querySelectorAll('button').forEach(el => {
    if (el.textContent.trim()) {
      elements.buttons.push({
        text: el.textContent.trim().substring(0, 30),
        selector: el.id || el.className.split(' ')[0],
        ariaLabel: el.getAttribute('aria-label'),
        type: el.type
      });
    }
  });

  // Get all links with data attributes (important for toyota.com)
  document.querySelectorAll('a[data-aa-action], a[data-di-id]').forEach(el => {
    elements.links.push({
      text: el.textContent.trim().substring(0, 40),
      href: el.href,
      dataId: el.getAttribute('data-di-id'),
      aaLinkText: el.getAttribute('data-aa-link-text'),
      aaAction: el.getAttribute('data-aa-action')
    });
  });

  // Get form elements
  document.querySelectorAll('input, select, textarea').forEach(el => {
    elements.forms.push({
      type: el.type || el.tagName.toLowerCase(),
      name: el.name,
      id: el.id,
      placeholder: el.placeholder,
      ariaLabel: el.getAttribute('aria-label'),
      selector: el.id ? `#${el.id}` : (el.name ? `[name="${el.name}"]` : el.className.split(' ')[0])
    });
  });

  // Get interactive elements (clickable)
  document.querySelectorAll('[onclick], [role="button"], .cta, .btn').forEach(el => {
    elements.interactive.push({
      text: el.textContent.trim().substring(0, 30),
      selector: el.id || el.className.split(' ')[0],
      role: el.getAttribute('role'),
      tagName: el.tagName
    });
  });

  return elements;
})()
"""

    def save_discovery_report(self, report_path: Optional[str] = None) -> str:
        """
        Generate and save a discovery report.

        Args:
            report_path: Path to save report (default: test_data/mcp_discovery_report.json)

        Returns:
            Path to saved report
        """
        if report_path is None:
            report_path = "test_data/mcp_discovery_report.json"

        report = {
            'discovery_timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_selectors_discovered': len(self.discovered_selectors),
            'selectors': [asdict(sel) for sel in self.discovered_selectors],
            'categorized': self.categorize_selectors(self.discovered_selectors)
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        return report_path


class MCPSelectorValidator:
    """Validates selectors discovered via MCP"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_selector(self, selector: str) -> bool:
        """
        Validate that a selector is properly formatted.

        Args:
            selector: CSS selector string

        Returns:
            True if valid, False otherwise
        """
        if not selector or not isinstance(selector, str):
            return False

        # Check for common invalid patterns
        invalid_patterns = ['undefined', 'null', 'NaN', '']
        if selector.lower() in invalid_patterns:
            return False

        # Must have some content
        if len(selector.strip()) == 0:
            return False

        return True

    def suggest_alternatives(self, selector: str, element_data: Dict) -> List[str]:
        """
        Suggest alternative selectors based on element data.

        Args:
            selector: Original selector
            element_data: Data about the element

        Returns:
            List of alternative selectors
        """
        alternatives = [selector]

        # Add data attribute selectors
        if 'data_attributes' in element_data:
            for attr, value in element_data['data_attributes'].items():
                alternatives.append(f"[{attr}='{value}']")

        # Add ARIA label selector
        if element_data.get('aria_label'):
            alternatives.append(f"[aria-label='{element_data['aria_label']}']")

        # Add text-based selector
        if element_data.get('text_content'):
            text = element_data['text_content'][:20]
            alternatives.append(f":text('{text}')")

        return alternatives


# Usage example (for documentation)
if __name__ == "__main__":
    """
    Example usage with MCP Playwright tools:

    1. In Claude Code, navigate to a page:
       mcp__playwright__playwright_navigate(url="https://www.toyota.com")

    2. Run selector discovery:
       discovery = MCPSelectorDiscovery()
       script = discovery.generate_mcp_discovery_script()
       # Run script via mcp__playwright__playwright_evaluate(script=script)

    3. Parse and save results:
       results = {...}  # Results from MCP evaluate
       selectors = discovery.parse_mcp_discovery_results(results)
       categorized = discovery.categorize_selectors(selectors)
       merged_db = discovery.merge_with_database(categorized)
       discovery.save_selector_database(merged_db)

    4. Generate report:
       discovery.save_discovery_report()
    """
    pass
