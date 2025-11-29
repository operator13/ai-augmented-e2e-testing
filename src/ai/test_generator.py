"""
AI-Powered Test Case Generator

This module uses AI (Claude/GPT) to automatically generate E2E test cases
based on user flows, requirements, and site analysis.

Enhanced with MCP integration for:
- Converting MCP-recorded sessions to AI-enhanced tests
- Combining interactive recording with AI-generated assertions
- Integrating with selector discovery and self-healing
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from openai import OpenAI

from src.config.constants import AI_PROMPTS, ToyotaPages
from src.config.settings import settings

# MCP integration imports (optional, lazy loaded)
try:
    from src.mcp.codegen_workflow import MCPCodegenWorkflow
    from src.mcp.selector_discovery import MCPSelectorDiscovery
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class AITestGenerator:
    """Generate test cases using AI models"""

    def __init__(self, use_claude: bool = True):
        """
        Initialize the AI test generator

        Args:
            use_claude: If True, use Claude; otherwise use OpenAI GPT
        """
        self.use_claude = use_claude

        if use_claude and settings.anthropic_api_key:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.claude_model
        elif settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.ai_model
            self.use_claude = False
        else:
            raise ValueError("No AI API key configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")

    def generate_test_from_flow(
        self,
        page: str,
        user_flow: str,
        requirements: Optional[List[str]] = None,
        test_name: Optional[str] = None,
    ) -> str:
        """
        Generate a test case from a user flow description

        Args:
            page: The page or feature being tested
            user_flow: Description of the user flow
            requirements: Optional list of specific requirements
            test_name: Optional custom test name

        Returns:
            Generated Python test code
        """
        prompt = self._build_test_generation_prompt(page, user_flow, requirements)
        generated_code = self._call_ai(prompt)
        return self._clean_generated_code(generated_code, test_name)

    def generate_tests_from_sitemap(
        self, pages: Optional[List[str]] = None, critical_only: bool = False
    ) -> Dict[str, str]:
        """
        Generate test cases for multiple pages

        Args:
            pages: List of pages to generate tests for (None = all pages)
            critical_only: Only generate tests for critical paths

        Returns:
            Dictionary mapping test file names to generated code
        """
        if pages is None:
            pages = [page.value for page in ToyotaPages]

        tests = {}
        for page in pages:
            if critical_only and not self._is_critical_page(page):
                continue

            test_code = self.generate_test_from_flow(
                page=page, user_flow=f"Standard navigation and interaction with {page}", requirements=[]
            )
            test_file_name = f"test_{page.replace('/', '_').strip('_')}.py"
            tests[test_file_name] = test_code

        return tests

    def enhance_existing_test(self, test_file_path: Path, enhancement_type: str) -> str:
        """
        Enhance an existing test with AI suggestions

        Args:
            test_file_path: Path to existing test file
            enhancement_type: Type of enhancement (accessibility, performance, assertions)

        Returns:
            Enhanced test code
        """
        with open(test_file_path, "r") as f:
            existing_code = f.read()

        prompt = f"""
        Enhance the following Playwright test with {enhancement_type} checks:

        ```python
        {existing_code}
        ```

        Add comprehensive {enhancement_type} validations while maintaining the existing test structure.
        Return only the enhanced Python code.
        """

        enhanced_code = self._call_ai(prompt)
        return self._clean_generated_code(enhanced_code)

    def suggest_test_scenarios(self, feature: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Suggest test scenarios for a feature

        Args:
            feature: Feature description
            context: Optional additional context

        Returns:
            List of suggested test scenarios with metadata
        """
        prompt = f"""
        Suggest comprehensive test scenarios for the following feature on toyota.com:

        Feature: {feature}
        {f"Context: {context}" if context else ""}

        Provide test scenarios covering:
        1. Happy path
        2. Edge cases
        3. Error handling
        4. Accessibility
        5. Performance
        6. Mobile responsiveness

        Return as JSON array with this structure:
        [
            {{
                "name": "Test scenario name",
                "description": "What this test validates",
                "priority": "critical|high|medium|low",
                "type": "smoke|regression|visual|performance",
                "steps": ["Step 1", "Step 2", ...]
            }}
        ]
        """

        response = self._call_ai(prompt)
        scenarios = self._extract_json(response)
        return scenarios if isinstance(scenarios, list) else []

    def _build_test_generation_prompt(
        self, page: str, user_flow: str, requirements: Optional[List[str]]
    ) -> str:
        """Build the prompt for test generation"""
        requirements_text = "\n".join(f"- {req}" for req in (requirements or []))

        return f"""
        Generate a comprehensive Playwright Python test for toyota.com:

        Page/Feature: {page}
        User Flow: {user_flow}
        Requirements:
        {requirements_text if requirements_text else "- Standard functionality validation"}

        Generate a pytest test that:
        1. Uses page object pattern for selectors
        2. Includes proper assertions
        3. Handles waits and timeouts appropriately
        4. Includes accessibility checks
        5. Has clear test documentation
        6. Uses fixtures for setup/teardown
        7. Includes visual regression checkpoints if appropriate
        8. Validates performance metrics

        Return ONLY valid Python code with no explanations.
        Use this structure:

        ```python
        import pytest
        from playwright.sync_api import Page, expect
        from src.core.page_objects.base_page import BasePage

        @pytest.mark.smoke
        def test_feature_name(page: Page):
            '''Test description'''
            # Test implementation
            pass
        ```
        """

    def _call_ai(self, prompt: str, max_tokens: int = 4096) -> str:
        """Call the AI API"""
        if self.use_claude:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        else:
            response = self.client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens
            )
            return response.choices[0].message.content

    def _clean_generated_code(self, code: str, custom_name: Optional[str] = None) -> str:
        """Clean and format generated code"""
        # Remove markdown code blocks
        code = re.sub(r"```python\n", "", code)
        code = re.sub(r"```\n?", "", code)

        # Ensure proper imports
        if "import pytest" not in code:
            code = "import pytest\n" + code

        # Custom test name if provided
        if custom_name:
            code = re.sub(r"def test_\w+", f"def {custom_name}", code, count=1)

        return code.strip()

    def _extract_json(self, text: str) -> Any:
        """Extract JSON from AI response"""
        # Try to find JSON in markdown blocks
        json_match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # Try to find raw JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON array or object
            json_match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

        return None

    def _is_critical_page(self, page: str) -> bool:
        """Determine if a page is critical"""
        critical_pages = [
            ToyotaPages.HOMEPAGE.value,
            ToyotaPages.VEHICLES.value,
            ToyotaPages.BUILD_AND_PRICE.value,
            ToyotaPages.DEALERS.value,
        ]
        return page in critical_pages

    def save_generated_test(self, test_code: str, filename: str, output_dir: Optional[Path] = None):
        """
        Save generated test to file

        Args:
            test_code: Generated test code
            filename: Output filename
            output_dir: Output directory (default: tests/ai_generated)
        """
        if output_dir is None:
            output_dir = Path("tests/ai_generated")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename

        with open(output_path, "w") as f:
            f.write(test_code)

        print(f"Generated test saved to: {output_path}")

    # ============================================================================
    # MCP Integration Methods
    # ============================================================================

    def enhance_mcp_recording(
        self,
        recorded_test_path: str,
        flow_description: str,
        enhancement_level: str = "full"
    ) -> str:
        """
        Enhance an MCP-recorded test with AI-generated assertions and validations.

        This method takes a test recorded via MCP codegen and enhances it with:
        - Meaningful assertions based on the user flow
        - Visual regression checks
        - Performance validations
        - Accessibility checks
        - Self-healing selector integration

        Args:
            recorded_test_path: Path to MCP-generated test file
            flow_description: Description of what the test does
            enhancement_level: Level of enhancement (minimal, moderate, full)

        Returns:
            Enhanced test code
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP modules not available. Install MCP dependencies.")

        with open(recorded_test_path, 'r') as f:
            recorded_code = f.read()

        prompt = f"""
        Enhance the following Playwright test that was recorded via MCP codegen:

        Flow Description: {flow_description}

        Recorded Test:
        ```python
        {recorded_code}
        ```

        Enhancement Level: {enhancement_level}

        Please enhance this test with:
        {self._get_enhancement_requirements(enhancement_level)}

        IMPORTANT:
        - Preserve all the original actions and selectors
        - Add assertions after key actions to validate state
        - Use expect() assertions from playwright.sync_api
        - Add comments explaining what each assertion validates
        - Integrate self-healing selectors from src.ai.self_healing
        - Add visual regression checks if appropriate
        - Include performance checks for page load and interactions

        Return ONLY the enhanced Python code with proper pytest format.
        """

        enhanced_code = self._call_ai(prompt, max_tokens=6000)
        return self._clean_generated_code(enhanced_code)

    def generate_from_mcp_actions(
        self,
        actions: List[Dict[str, Any]],
        test_name: str,
        flow_description: str
    ) -> str:
        """
        Generate a complete test from MCP-recorded actions.

        Args:
            actions: List of actions recorded by MCP (navigate, click, fill, etc.)
            test_name: Name for the generated test
            flow_description: Description of the user flow

        Returns:
            Generated pytest code
        """
        # Format actions for the prompt
        actions_text = self._format_actions_for_prompt(actions)

        prompt = f"""
        Generate a comprehensive Playwright pytest test from these recorded actions:

        Test Name: {test_name}
        Flow Description: {flow_description}

        Recorded Actions:
        {actions_text}

        Generate a complete pytest test that:
        1. Implements all the recorded actions
        2. Adds meaningful assertions after each major action
        3. Uses self-healing selectors from src.ai.self_healing
        4. Includes error handling
        5. Adds visual regression checks at key points
        6. Validates page state and transitions
        7. Includes accessibility checks
        8. Uses proper pytest fixtures and markers

        Structure:
        ```python
        import pytest
        from playwright.sync_api import Page, expect
        from src.ai.self_healing import SelfHealingSelector
        from src.ai.visual_ai import VisualAI

        @pytest.mark.mcp_generated
        @pytest.mark.smoke  # or appropriate marker
        def {test_name}(page: Page):
            '''
            {flow_description}
            '''
            # Test implementation with all actions and assertions
        ```

        Return ONLY valid Python code.
        """

        generated_code = self._call_ai(prompt, max_tokens=6000)
        return self._clean_generated_code(generated_code, test_name)

    def suggest_assertions_for_recording(
        self,
        recorded_actions: List[Dict[str, Any]],
        page_url: str
    ) -> List[Dict[str, str]]:
        """
        Suggest meaningful assertions to add to a recorded test.

        Args:
            recorded_actions: Actions recorded during MCP session
            page_url: URL of the page being tested

        Returns:
            List of suggested assertions with placement info
        """
        actions_text = self._format_actions_for_prompt(recorded_actions)

        prompt = f"""
        For the following recorded user actions on {page_url}, suggest meaningful assertions
        to validate the application state:

        Recorded Actions:
        {actions_text}

        Suggest assertions that:
        1. Verify page transitions completed successfully
        2. Check that elements are visible/clickable after interactions
        3. Validate form submissions
        4. Check URL changes
        5. Verify content updates

        Return as JSON array:
        [
            {{
                "after_action": "Action number (0-based index)",
                "assertion_type": "expect_visible|expect_url|expect_text|expect_count",
                "selector": "CSS selector to check",
                "description": "What this assertion validates",
                "code": "expect(page.locator('...')).to_be_visible()"
            }}
        ]
        """

        response = self._call_ai(prompt)
        assertions = self._extract_json(response)
        return assertions if isinstance(assertions, list) else []

    def merge_mcp_with_page_object(
        self,
        recorded_test_path: str,
        page_object_class: str
    ) -> str:
        """
        Convert an MCP-recorded test to use page object pattern.

        Args:
            recorded_test_path: Path to MCP-generated test
            page_object_class: Name of the page object class to use

        Returns:
            Refactored test code using page objects
        """
        with open(recorded_test_path, 'r') as f:
            recorded_code = f.read()

        prompt = f"""
        Refactor this Playwright test to use the page object pattern:

        Original Test:
        ```python
        {recorded_code}
        ```

        Convert this to use the page object: {page_object_class}

        Requirements:
        1. Replace direct page.click(), page.fill() etc. with page object methods
        2. Import from src.core.page_objects.{page_object_class.lower()}
        3. Maintain all test logic and assertions
        4. Follow page object best practices
        5. Keep the test readable and maintainable

        Example structure:
        ```python
        from src.core.page_objects.{page_object_class.lower()} import {page_object_class}

        def test_name(page: Page):
            page_obj = {page_object_class}(page)
            page_obj.navigate()
            page_obj.click_element(...)
            # etc
        ```

        Return ONLY the refactored Python code.
        """

        refactored_code = self._call_ai(prompt, max_tokens=6000)
        return self._clean_generated_code(refactored_code)

    def _get_enhancement_requirements(self, level: str) -> str:
        """Get enhancement requirements based on level"""
        requirements = {
            "minimal": """
                - Add basic expect() assertions after navigation and clicks
                - Validate page loaded successfully
                - Use self-healing selectors
            """,
            "moderate": """
                - Add comprehensive expect() assertions after all interactions
                - Validate page state and element visibility
                - Use self-healing selectors with fallbacks
                - Add basic visual regression checks at key points
                - Include accessibility checks for interactive elements
            """,
            "full": """
                - Add comprehensive expect() assertions for all actions
                - Validate page state, URL, content, and element states
                - Use self-healing selectors with multiple fallback strategies
                - Add visual regression checks at all major UI states
                - Include comprehensive accessibility checks
                - Add performance validations for page load and interactions
                - Include anomaly detection for console errors
                - Add data-driven test variations if applicable
            """
        }
        return requirements.get(level, requirements["moderate"])

    def _format_actions_for_prompt(self, actions: List[Dict[str, Any]]) -> str:
        """Format actions list for AI prompt"""
        formatted = []
        for i, action in enumerate(actions):
            action_type = action.get('type', 'unknown')
            selector = action.get('selector', '')
            value = action.get('value', '')
            url = action.get('url', '')

            if action_type == 'navigate':
                formatted.append(f"{i}. Navigate to: {url}")
            elif action_type == 'click':
                formatted.append(f"{i}. Click: {selector}")
            elif action_type == 'fill':
                formatted.append(f"{i}. Fill '{selector}' with: {value}")
            elif action_type == 'select':
                formatted.append(f"{i}. Select '{value}' in: {selector}")
            else:
                formatted.append(f"{i}. {action_type}: {selector}")

        return "\n".join(formatted)

    def create_test_suite_from_mcp_sessions(
        self,
        sessions: List[Dict[str, Any]],
        suite_name: str
    ) -> Dict[str, str]:
        """
        Create a complete test suite from multiple MCP recording sessions.

        Args:
            sessions: List of MCP session data
            suite_name: Name for the test suite

        Returns:
            Dictionary mapping test names to generated code
        """
        test_suite = {}

        for session in sessions:
            test_name = session.get('test_name', f"test_{len(test_suite) + 1}")
            flow_description = session.get('description', 'Generated from MCP recording')
            actions = session.get('actions', [])

            test_code = self.generate_from_mcp_actions(
                actions=actions,
                test_name=test_name,
                flow_description=flow_description
            )

            test_suite[f"{test_name}.py"] = test_code

        return test_suite


def main():
    """CLI interface for test generation"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Test Case Generator")
    parser.add_argument("--url", help="Target URL or page")
    parser.add_argument("--flow", help="User flow description")
    parser.add_argument("--feature", help="Feature to generate scenarios for")
    parser.add_argument("--sitemap", action="store_true", help="Generate tests from sitemap")
    parser.add_argument("--critical-only", action="store_true", help="Only critical pages")
    parser.add_argument("--output", help="Output directory", default="tests/ai_generated")
    parser.add_argument("--use-gpt", action="store_true", help="Use GPT instead of Claude")

    args = parser.parse_args()

    generator = AITestGenerator(use_claude=not args.use_gpt)

    if args.sitemap:
        print("Generating tests from sitemap...")
        tests = generator.generate_tests_from_sitemap(critical_only=args.critical_only)
        for filename, code in tests.items():
            generator.save_generated_test(code, filename, Path(args.output))
        print(f"Generated {len(tests)} test files")

    elif args.feature:
        print(f"Generating test scenarios for: {args.feature}")
        scenarios = generator.suggest_test_scenarios(args.feature)
        print(json.dumps(scenarios, indent=2))

    elif args.url and args.flow:
        print(f"Generating test for: {args.url}")
        test_code = generator.generate_test_from_flow(page=args.url, user_flow=args.flow)
        filename = f"test_{args.url.replace('/', '_').strip('_')}.py"
        generator.save_generated_test(test_code, filename, Path(args.output))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
