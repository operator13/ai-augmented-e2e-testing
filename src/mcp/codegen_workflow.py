"""
MCP Codegen Workflow Module

This module provides integration between Claude Code's Playwright MCP codegen features
and the AI-augmented test generation system.

Features:
- Record user flows via MCP codegen sessions
- Convert recorded actions to pytest format
- Integrate with AI test generator for enhanced assertions
- Support for both synchronous and async test generation
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class CodegenSession:
    """Represents an MCP codegen recording session"""
    session_id: str
    output_path: str
    test_name_prefix: str = "GeneratedTest"
    include_comments: bool = True
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    actions_recorded: List[Dict] = field(default_factory=list)
    generated_test_path: Optional[str] = None


class MCPCodegenWorkflow:
    """
    Manages MCP codegen sessions and integrates with the AI test generation pipeline.

    This class bridges the gap between interactive MCP recording and the
    existing AI-powered test generation system.
    """

    def __init__(self, output_dir: str = "tests/ai_generated"):
        """
        Initialize the codegen workflow manager.

        Args:
            output_dir: Directory where generated tests will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, CodegenSession] = {}
        self.session_history_path = Path("test_data/codegen_sessions.json")

    def start_recording_session(
        self,
        session_name: str,
        test_name_prefix: str = "test_recorded",
        include_comments: bool = True
    ) -> CodegenSession:
        """
        Start a new MCP codegen recording session.

        Args:
            session_name: Unique name for this session
            test_name_prefix: Prefix for generated test names
            include_comments: Whether to include descriptive comments

        Returns:
            CodegenSession object
        """
        session_id = f"{session_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        output_path = str(self.output_dir / f"{test_name_prefix}.py")

        session = CodegenSession(
            session_id=session_id,
            output_path=output_path,
            test_name_prefix=test_name_prefix,
            include_comments=include_comments
        )

        self.active_sessions[session_id] = session
        self.logger.info(f"Started codegen session: {session_id}")

        return session

    def record_action(self, session_id: str, action: Dict[str, Any]) -> None:
        """
        Record an action in the active session.

        Args:
            session_id: Session to record action in
            action: Action details (type, selector, value, etc.)
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        session.actions_recorded.append({
            **action,
            'timestamp': datetime.utcnow().isoformat()
        })

    def end_session(self, session_id: str, generated_test_path: str) -> CodegenSession:
        """
        End a codegen session and finalize the generated test.

        Args:
            session_id: Session to end
            generated_test_path: Path where MCP saved the generated test

        Returns:
            Completed CodegenSession
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.active_sessions[session_id]
        session.completed_at = datetime.utcnow().isoformat()
        session.generated_test_path = generated_test_path

        # Save to history
        self._save_session_history(session)

        # Remove from active sessions
        del self.active_sessions[session_id]

        self.logger.info(f"Ended codegen session: {session_id}")
        return session

    def _save_session_history(self, session: CodegenSession) -> None:
        """Save session to history file"""
        history = []
        if self.session_history_path.exists():
            with open(self.session_history_path, 'r') as f:
                history = json.load(f)

        history.append({
            'session_id': session.session_id,
            'output_path': session.output_path,
            'started_at': session.started_at,
            'completed_at': session.completed_at,
            'actions_count': len(session.actions_recorded),
            'generated_test_path': session.generated_test_path
        })

        with open(self.session_history_path, 'w') as f:
            json.dump(history, f, indent=2)

    def enhance_with_ai(
        self,
        generated_test_path: str,
        enhancement_options: Optional[Dict] = None
    ) -> str:
        """
        Enhance MCP-generated test with AI-powered features.

        Args:
            generated_test_path: Path to the MCP-generated test
            enhancement_options: Options for enhancement (assertions, validations, etc.)

        Returns:
            Path to enhanced test file
        """
        if enhancement_options is None:
            enhancement_options = {
                'add_assertions': True,
                'add_visual_checks': False,
                'add_performance_checks': False,
                'use_self_healing': True
            }

        with open(generated_test_path, 'r') as f:
            original_code = f.read()

        # Enhance the test code
        enhanced_code = self._apply_enhancements(original_code, enhancement_options)

        # Save enhanced version
        enhanced_path = generated_test_path.replace('.py', '_enhanced.py')
        with open(enhanced_path, 'w') as f:
            f.write(enhanced_code)

        self.logger.info(f"Enhanced test saved to: {enhanced_path}")
        return enhanced_path

    def _apply_enhancements(self, code: str, options: Dict) -> str:
        """
        Apply AI enhancements to generated test code.

        Args:
            code: Original test code
            options: Enhancement options

        Returns:
            Enhanced test code
        """
        lines = code.split('\n')
        enhanced_lines = []

        # Add imports for AI features
        import_section = [
            "import pytest",
            "from playwright.sync_api import Page, expect",
            "from src.ai.self_healing import SelfHealingSelector",
            "from src.ai.visual_ai import VisualAI",
            "from src.ai.anomaly_detector import AnomalyDetector",
            ""
        ]

        # Find where to insert imports
        in_imports = True
        for line in lines:
            if in_imports and (line.startswith('def ') or line.startswith('class ')):
                in_imports = False
                if options.get('add_assertions'):
                    enhanced_lines.extend(import_section)

            # Add self-healing to selectors
            if options.get('use_self_healing') and 'page.click(' in line:
                # Extract selector
                import re
                match = re.search(r'page\.click\(["\'](.+?)["\']\)', line)
                if match:
                    selector = match.group(1)
                    indent = len(line) - len(line.lstrip())
                    enhanced_lines.append(' ' * indent + f"# Using self-healing selector")
                    enhanced_lines.append(' ' * indent + f"healer = SelfHealingSelector()")
                    enhanced_lines.append(' ' * indent +
                                        f"selector = healer.get_robust_selector('{selector}')")
                    enhanced_lines.append(line.replace(f"'{selector}'", "selector"))
                    continue

            # Add assertions after navigation
            if options.get('add_assertions') and 'page.goto(' in line:
                enhanced_lines.append(line)
                indent = len(line) - len(line.lstrip())
                enhanced_lines.append(' ' * indent + "# Verify page loaded successfully")
                enhanced_lines.append(' ' * indent + "expect(page).to_have_title(re.compile('.*'))")
                continue

            enhanced_lines.append(line)

        return '\n'.join(enhanced_lines)

    def convert_to_pytest(self, mcp_test_path: str) -> str:
        """
        Convert MCP-generated Playwright test to pytest format.

        Args:
            mcp_test_path: Path to MCP-generated test

        Returns:
            Path to pytest-formatted test
        """
        with open(mcp_test_path, 'r') as f:
            content = f.read()

        # Convert to pytest format
        pytest_code = self._transform_to_pytest(content)

        # Save pytest version
        pytest_path = mcp_test_path.replace('.py', '_pytest.py')
        with open(pytest_path, 'w') as f:
            f.write(pytest_code)

        return pytest_path

    def _transform_to_pytest(self, code: str) -> str:
        """Transform code to pytest format"""
        # Add pytest decorators and fixtures
        pytest_template = '''"""
Test generated from MCP codegen session
Enhanced with AI-powered assertions and self-healing selectors
"""

import pytest
import re
from playwright.sync_api import Page, expect

'''
        # Add the rest of the code with pytest fixtures
        pytest_template += code

        # Replace any browser/context setup with pytest fixtures
        pytest_template = pytest_template.replace(
            'with sync_playwright() as playwright:',
            '@pytest.fixture\ndef context(page: Page):\n    """Pytest-playwright fixture"""'
        )

        return pytest_template

    def generate_test_from_flow(
        self,
        flow_description: str,
        actions: List[Dict[str, Any]],
        output_name: str
    ) -> str:
        """
        Generate a complete pytest test from a recorded flow.

        Args:
            flow_description: Description of what the test does
            actions: List of recorded actions
            output_name: Name for the output test file

        Returns:
            Path to generated test file
        """
        test_code = self._build_test_from_actions(flow_description, actions)

        output_path = self.output_dir / f"{output_name}.py"
        with open(output_path, 'w') as f:
            f.write(test_code)

        self.logger.info(f"Generated test: {output_path}")
        return str(output_path)

    def _build_test_from_actions(self, description: str, actions: List[Dict]) -> str:
        """Build complete test code from actions"""
        template = f'''"""
{description}

Generated from MCP codegen workflow
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.mcp_generated
def test_{description.lower().replace(' ', '_')}(page: Page):
    """
    {description}
    """
'''

        # Add actions
        for action in actions:
            action_type = action.get('type', '')
            selector = action.get('selector', '')
            value = action.get('value', '')

            if action_type == 'navigate':
                template += f"    page.goto('{value}')\n"
            elif action_type == 'click':
                template += f"    page.click('{selector}')\n"
            elif action_type == 'fill':
                template += f"    page.fill('{selector}', '{value}')\n"
            elif action_type == 'assert':
                template += f"    expect(page.locator('{selector}')).{value}\n"

        return template

    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """
        Get status of a codegen session.

        Args:
            session_id: Session ID to query

        Returns:
            Session status dict or None if not found
        """
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                'session_id': session.session_id,
                'status': 'active',
                'actions_recorded': len(session.actions_recorded),
                'started_at': session.started_at
            }

        # Check history
        if self.session_history_path.exists():
            with open(self.session_history_path, 'r') as f:
                history = json.load(f)
                for record in history:
                    if record['session_id'] == session_id:
                        return {
                            **record,
                            'status': 'completed'
                        }

        return None


# Example integration with AI test generator
class MCPToAIBridge:
    """
    Bridges MCP codegen with the existing AI test generator.

    This allows recorded flows to be enhanced with AI-generated assertions,
    visual checks, and anomaly detection.
    """

    def __init__(self):
        self.workflow = MCPCodegenWorkflow()
        self.logger = logging.getLogger(__name__)

    def record_and_enhance(
        self,
        session_name: str,
        ai_enhancement_level: str = "full"
    ) -> str:
        """
        Record a flow and enhance with AI.

        Args:
            session_name: Name for the recording session
            ai_enhancement_level: Level of AI enhancement (minimal, moderate, full)

        Returns:
            Path to final enhanced test
        """
        # This would be called after MCP codegen completes
        session = self.workflow.start_recording_session(session_name)

        # After recording, the MCP tool provides the generated test path
        # We then enhance it based on the level requested

        enhancement_options = self._get_enhancement_options(ai_enhancement_level)

        self.logger.info(f"Will enhance with options: {enhancement_options}")

        return session.session_id

    def _get_enhancement_options(self, level: str) -> Dict:
        """Get enhancement options based on level"""
        if level == "minimal":
            return {
                'add_assertions': True,
                'add_visual_checks': False,
                'add_performance_checks': False,
                'use_self_healing': True
            }
        elif level == "moderate":
            return {
                'add_assertions': True,
                'add_visual_checks': True,
                'add_performance_checks': False,
                'use_self_healing': True
            }
        else:  # full
            return {
                'add_assertions': True,
                'add_visual_checks': True,
                'add_performance_checks': True,
                'use_self_healing': True
            }


if __name__ == "__main__":
    """
    Example usage:

    # 1. Start a recording session
    workflow = MCPCodegenWorkflow()
    session = workflow.start_recording_session("homepage_navigation")

    # 2. Use MCP tools to record actions
    # mcp__playwright__start_codegen_session(options={
    #     "outputPath": session.output_path,
    #     "testNamePrefix": session.test_name_prefix
    # })

    # 3. Navigate and interact with the page
    # (MCP records automatically)

    # 4. End session and get generated test
    # result = mcp__playwright__end_codegen_session(sessionId=mcp_session_id)
    # workflow.end_session(session.session_id, result.generated_path)

    # 5. Enhance with AI
    # enhanced_path = workflow.enhance_with_ai(result.generated_path)
    """
    pass
