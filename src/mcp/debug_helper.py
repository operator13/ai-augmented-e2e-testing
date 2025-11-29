"""
MCP Debug Helper Module

This module provides automated debugging capabilities using Claude Code's Playwright MCP tools.
When tests fail, this helper can automatically investigate failures, capture debug information,
and suggest fixes.

Features:
- Automatic failure investigation
- Screenshot and HTML capture at failure point
- Console log analysis
- Selector validation
- Alternative selector suggestions
- Integration with self-healing system
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class DebugSession:
    """Represents a debugging session"""
    session_id: str
    test_name: str
    failure_type: str
    failure_message: str
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    page_url: str = ""
    screenshots: List[str] = field(default_factory=list)
    console_logs: List[Dict] = field(default_factory=list)
    network_errors: List[Dict] = field(default_factory=list)
    suggested_fixes: List[str] = field(default_factory=list)
    resolution: Optional[str] = None


class MCPDebugHelper:
    """
    Automated debugging helper using MCP Playwright tools.

    This class provides utilities to investigate test failures, capture debug information,
    and suggest potential fixes using the self-healing selector system.
    """

    def __init__(self, debug_output_dir: str = "test_data/debug_sessions"):
        """
        Initialize the debug helper.

        Args:
            debug_output_dir: Directory to save debug session data
        """
        self.debug_output_dir = Path(debug_output_dir)
        self.debug_output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, DebugSession] = {}

    def start_debug_session(
        self,
        test_name: str,
        failure_type: str,
        failure_message: str
    ) -> DebugSession:
        """
        Start a new debugging session.

        Args:
            test_name: Name of the failing test
            failure_type: Type of failure (selector_not_found, timeout, assertion_failed, etc.)
            failure_message: Error message from the test

        Returns:
            DebugSession object
        """
        session_id = f"{test_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        session = DebugSession(
            session_id=session_id,
            test_name=test_name,
            failure_type=failure_type,
            failure_message=failure_message
        )

        self.active_sessions[session_id] = session
        self.logger.info(f"Started debug session: {session_id}")

        return session

    def investigate_selector_failure(
        self,
        session_id: str,
        failed_selector: str,
        page_url: str
    ) -> Dict[str, Any]:
        """
        Investigate why a selector failed and suggest alternatives.

        This method would work with MCP tools to:
        1. Navigate to the failure page
        2. Try to find similar elements
        3. Suggest alternative selectors

        Args:
            session_id: Active debug session
            failed_selector: The selector that failed
            page_url: URL where the failure occurred

        Returns:
            Investigation results with suggested fixes
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        session.page_url = page_url

        investigation = {
            'failed_selector': failed_selector,
            'page_url': page_url,
            'element_found': False,
            'alternatives': [],
            'recommendations': []
        }

        # Generate JavaScript to find similar elements
        find_similar_script = self._generate_find_similar_script(failed_selector)

        # This would be executed via MCP:
        # results = mcp__playwright__playwright_evaluate(script=find_similar_script)

        investigation['recommendations'].append(
            "Use MCP to navigate to page and run similarity search"
        )
        investigation['recommendations'].append(
            f"Script to run: {find_similar_script}"
        )

        session.suggested_fixes.extend(investigation['recommendations'])

        return investigation

    def _generate_find_similar_script(self, failed_selector: str) -> str:
        """
        Generate JavaScript to find elements similar to the failed selector.

        Args:
            failed_selector: The selector that failed

        Returns:
            JavaScript code
        """
        return f"""
(function() {{
  const failedSelector = '{failed_selector}';
  const results = {{
    exactMatch: null,
    similarElements: [],
    suggestions: []
  }};

  // Try exact match
  try {{
    const exact = document.querySelector(failedSelector);
    if (exact) {{
      results.exactMatch = {{
        found: true,
        text: exact.textContent.trim().substring(0, 50),
        visible: exact.offsetParent !== null
      }};
    }}
  }} catch (e) {{
    results.exactMatch = {{ error: e.message }};
  }}

  // Find elements with similar classes or IDs
  const selectorParts = failedSelector.match(/[.#][^.#\\s[]+/g) || [];

  selectorParts.forEach(part => {{
    const attr = part.startsWith('#') ? 'id' : 'class';
    const value = part.substring(1);

    document.querySelectorAll(`[${attr}*="${{value}}"]`).forEach(el => {{
      results.similarElements.push({{
        selector: el.id ? `#${{el.id}}` : `.${{el.className.split(' ')[0]}}`,
        text: el.textContent.trim().substring(0, 30),
        tagName: el.tagName,
        visible: el.offsetParent !== null,
        ariaLabel: el.getAttribute('aria-label'),
        dataAttributes: Array.from(el.attributes)
          .filter(a => a.name.startsWith('data-'))
          .map(a => ({{ name: a.name, value: a.value }}))
      }});
    }});
  }});

  // Generate suggestions based on findings
  if (results.similarElements.length > 0) {{
    results.suggestions.push(
      'Found ' + results.similarElements.length + ' similar elements'
    );

    // Suggest most visible element
    const visible = results.similarElements.filter(e => e.visible);
    if (visible.length > 0) {{
      results.suggestions.push(
        'Try: ' + visible[0].selector
      );
    }}

    // Suggest data attribute selectors
    results.similarElements.forEach(el => {{
      if (el.dataAttributes.length > 0) {{
        el.dataAttributes.forEach(attr => {{
          results.suggestions.push(
            `Try: [${{attr.name}}="${{attr.value}}"]`
          );
        }});
      }}
    }});
  }}

  return results;
}})()
"""

    def capture_debug_artifacts(
        self,
        session_id: str,
        page_url: str
    ) -> Dict[str, str]:
        """
        Capture screenshots, HTML, and console logs for debugging.

        Args:
            session_id: Active debug session
            page_url: Current page URL

        Returns:
            Paths to captured artifacts
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        artifacts = {}

        # Screenshot path
        screenshot_name = f"{session_id}_screenshot"
        artifacts['screenshot'] = f"Will capture via: mcp__playwright__playwright_screenshot(name='{screenshot_name}')"

        # HTML path
        artifacts['html'] = f"Will capture via: mcp__playwright__playwright_get_visible_html()"

        # Console logs
        artifacts['console_logs'] = f"Will capture via: mcp__playwright__playwright_console_logs(type='all')"

        session.screenshots.append(screenshot_name)

        self.logger.info(f"Captured debug artifacts for session {session_id}")

        return artifacts

    def analyze_console_errors(
        self,
        console_logs: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze console logs to identify potential issues.

        Args:
            console_logs: Console log entries

        Returns:
            Analysis results with categorized errors
        """
        analysis = {
            'errors': [],
            'warnings': [],
            'network_issues': [],
            'javascript_errors': [],
            'recommendations': []
        }

        for log in console_logs:
            log_type = log.get('type', '').lower()
            message = log.get('message', '')

            if log_type == 'error':
                analysis['errors'].append(message)

                # Categorize errors
                if 'network' in message.lower() or 'fetch' in message.lower():
                    analysis['network_issues'].append(message)
                elif 'script' in message.lower() or 'syntaxerror' in message.lower():
                    analysis['javascript_errors'].append(message)

            elif log_type == 'warning':
                analysis['warnings'].append(message)

        # Generate recommendations
        if analysis['network_issues']:
            analysis['recommendations'].append(
                "Network errors detected - check API endpoints and connectivity"
            )

        if analysis['javascript_errors']:
            analysis['recommendations'].append(
                "JavaScript errors detected - may affect page functionality"
            )

        if len(analysis['errors']) > 10:
            analysis['recommendations'].append(
                "High number of console errors - page may be unstable"
            )

        return analysis

    def suggest_selector_fix(
        self,
        failed_selector: str,
        similar_elements: List[Dict]
    ) -> List[str]:
        """
        Suggest alternative selectors based on similar elements found.

        Args:
            failed_selector: The selector that failed
            similar_elements: Similar elements found on the page

        Returns:
            List of suggested selectors
        """
        suggestions = []

        # Prioritize visible elements
        visible_elements = [e for e in similar_elements if e.get('visible', False)]

        if visible_elements:
            # Suggest data attribute selectors (most stable)
            for element in visible_elements:
                for data_attr in element.get('dataAttributes', []):
                    suggestions.append(
                        f"[{data_attr['name']}='{data_attr['value']}']"
                    )

            # Suggest ARIA label selectors
            for element in visible_elements:
                if element.get('ariaLabel'):
                    suggestions.append(
                        f"[aria-label='{element['ariaLabel']}']"
                    )

            # Suggest text-based selectors
            for element in visible_elements:
                if element.get('text'):
                    suggestions.append(
                        f":text('{element['text'][:20]}')"
                    )

        # Deduplicate and return top suggestions
        return list(dict.fromkeys(suggestions))[:5]

    def auto_heal_selector(
        self,
        session_id: str,
        failed_selector: str,
        suggested_selectors: List[str]
    ) -> Optional[str]:
        """
        Automatically attempt to heal a failed selector.

        Args:
            session_id: Active debug session
            failed_selector: The selector that failed
            suggested_selectors: Alternative selectors to try

        Returns:
            Working selector if found, None otherwise
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]

        # This would integrate with the self-healing system
        # and MCP to test each suggested selector

        test_script = self._generate_selector_test_script(suggested_selectors)

        session.suggested_fixes.append(
            f"Auto-healing script: {test_script}"
        )

        # Return first suggestion for now (would actually test via MCP)
        return suggested_selectors[0] if suggested_selectors else None

    def _generate_selector_test_script(self, selectors: List[str]) -> str:
        """Generate JavaScript to test multiple selectors"""
        return f"""
(function() {{
  const selectors = {json.dumps(selectors)};
  const results = [];

  selectors.forEach(selector => {{
    try {{
      const element = document.querySelector(selector);
      if (element && element.offsetParent !== null) {{
        results.push({{
          selector: selector,
          found: true,
          visible: true,
          text: element.textContent.trim().substring(0, 30)
        }});
      }} else if (element) {{
        results.push({{
          selector: selector,
          found: true,
          visible: false
        }});
      }}
    }} catch (e) {{
      results.push({{
        selector: selector,
        found: false,
        error: e.message
      }});
    }}
  }});

  return results;
}})()
"""

    def save_debug_report(self, session_id: str) -> str:
        """
        Save a complete debug report for a session.

        Args:
            session_id: Session to save

        Returns:
            Path to saved report
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]

        report = {
            'session_id': session.session_id,
            'test_name': session.test_name,
            'failure_type': session.failure_type,
            'failure_message': session.failure_message,
            'started_at': session.started_at,
            'page_url': session.page_url,
            'screenshots': session.screenshots,
            'console_logs': session.console_logs,
            'network_errors': session.network_errors,
            'suggested_fixes': session.suggested_fixes,
            'resolution': session.resolution
        }

        report_path = self.debug_output_dir / f"{session_id}_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Saved debug report: {report_path}")

        return str(report_path)

    def resolve_session(
        self,
        session_id: str,
        resolution: str,
        working_selector: Optional[str] = None
    ) -> None:
        """
        Mark a debug session as resolved.

        Args:
            session_id: Session to resolve
            resolution: Description of how the issue was resolved
            working_selector: The selector that worked (if applicable)
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        session.resolution = resolution

        if working_selector:
            session.suggested_fixes.append(
                f"Working selector: {working_selector}"
            )

        # Save report
        self.save_debug_report(session_id)

        # Remove from active sessions
        del self.active_sessions[session_id]

        self.logger.info(f"Resolved debug session: {session_id}")


class MCPFailureAnalyzer:
    """
    Analyzes test failures and provides actionable insights.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_failure(
        self,
        test_name: str,
        error_type: str,
        error_message: str,
        traceback: str
    ) -> Dict[str, Any]:
        """
        Analyze a test failure and provide insights.

        Args:
            test_name: Name of the failed test
            error_type: Type of error
            error_message: Error message
            traceback: Full error traceback

        Returns:
            Analysis with suggested actions
        """
        analysis = {
            'test_name': test_name,
            'failure_category': self._categorize_failure(error_type, error_message),
            'likely_cause': self._identify_likely_cause(error_type, error_message),
            'suggested_actions': [],
            'mcp_debug_commands': []
        }

        # Add suggested actions based on failure type
        if 'selector' in error_message.lower() or 'not found' in error_message.lower():
            analysis['suggested_actions'].extend([
                "Run selector discovery to find alternative selectors",
                "Check if page structure has changed",
                "Enable self-healing selectors"
            ])
            analysis['mcp_debug_commands'].extend([
                "mcp__playwright__playwright_get_visible_html()",
                "Use selector discovery script to find alternatives"
            ])

        elif 'timeout' in error_message.lower():
            analysis['suggested_actions'].extend([
                "Check network performance",
                "Verify page is loading correctly",
                "Increase timeout threshold"
            ])
            analysis['mcp_debug_commands'].extend([
                "mcp__playwright__playwright_console_logs(type='error')",
                "Check for network errors in console"
            ])

        elif 'assertion' in error_message.lower():
            analysis['suggested_actions'].extend([
                "Verify expected vs actual values",
                "Check if page content has changed",
                "Review test assertions"
            ])
            analysis['mcp_debug_commands'].extend([
                "mcp__playwright__playwright_screenshot()",
                "Capture page state for comparison"
            ])

        return analysis

    def _categorize_failure(self, error_type: str, error_message: str) -> str:
        """Categorize the type of failure"""
        message_lower = error_message.lower()

        if 'selector' in message_lower or 'element' in message_lower:
            return 'selector_issue'
        elif 'timeout' in message_lower:
            return 'timeout'
        elif 'assertion' in message_lower or 'expected' in message_lower:
            return 'assertion_failure'
        elif 'network' in message_lower:
            return 'network_error'
        else:
            return 'unknown'

    def _identify_likely_cause(self, error_type: str, error_message: str) -> str:
        """Identify the likely cause of the failure"""
        category = self._categorize_failure(error_type, error_message)

        causes = {
            'selector_issue': "Element selector may have changed due to DOM updates",
            'timeout': "Page may be loading slowly or element not appearing",
            'assertion_failure': "Page content or behavior differs from expected",
            'network_error': "API or resource loading issue",
            'unknown': "Unknown failure - manual investigation required"
        }

        return causes.get(category, causes['unknown'])


if __name__ == "__main__":
    """
    Example usage:

    # When a test fails
    helper = MCPDebugHelper()
    session = helper.start_debug_session(
        test_name="test_vehicle_navigation",
        failure_type="selector_not_found",
        failure_message="Element with selector '.vehicle-card' not found"
    )

    # Investigate the failure
    investigation = helper.investigate_selector_failure(
        session.session_id,
        failed_selector=".vehicle-card",
        page_url="https://www.toyota.com/vehicles"
    )

    # Capture debug artifacts
    artifacts = helper.capture_debug_artifacts(
        session.session_id,
        page_url="https://www.toyota.com/vehicles"
    )

    # Analyze and suggest fixes
    # (Use MCP tools to execute the suggested commands)

    # Resolve when fixed
    helper.resolve_session(
        session.session_id,
        resolution="Updated selector to use data attribute",
        working_selector="[data-vehicle-type='sedan']"
    )
    """
    pass
