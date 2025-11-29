"""
Automated Coverage Analyzer

Tracks test coverage across pages, features, and user flows.
Uses AI to identify gaps and suggest missing test scenarios.
"""
import json
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from anthropic import Anthropic
from openai import OpenAI

from src.config.constants import ToyotaPages, VehicleModels
from src.config.settings import settings


@dataclass
class CoverageItem:
    """Coverage tracking item"""

    identifier: str
    type: str  # page, feature, flow, component
    tested: bool
    test_count: int
    last_tested: Optional[str]
    test_files: List[str]


class CoverageAnalyzer:
    """Analyze and track test coverage"""

    def __init__(self, use_claude: bool = True):
        """
        Initialize coverage analyzer

        Args:
            use_claude: Use Claude for AI analysis
        """
        self.coverage_data: Dict[str, CoverageItem] = {}
        self.test_execution_history: List[Dict] = []
        self.coverage_db_path = Path("test_data/coverage.json")

        # Initialize AI client
        if use_claude and settings.anthropic_api_key:
            self.ai_client = Anthropic(api_key=settings.anthropic_api_key)
            self.ai_model = settings.claude_model
            self.use_claude = True
        elif settings.openai_api_key:
            self.ai_client = OpenAI(api_key=settings.openai_api_key)
            self.ai_model = settings.ai_model
            self.use_claude = False
        else:
            self.ai_client = None

        self._load_coverage_database()
        self._initialize_coverage_items()

    def _initialize_coverage_items(self):
        """Initialize coverage items for known pages and features"""
        # Track all Toyota pages
        for page in ToyotaPages:
            key = f"page:{page.value}"
            if key not in self.coverage_data:
                self.coverage_data[key] = CoverageItem(
                    identifier=page.value,
                    type="page",
                    tested=False,
                    test_count=0,
                    last_tested=None,
                    test_files=[],
                )

        # Track vehicle models
        for model in VehicleModels:
            key = f"vehicle:{model.value}"
            if key not in self.coverage_data:
                self.coverage_data[key] = CoverageItem(
                    identifier=model.value,
                    type="vehicle",
                    tested=False,
                    test_count=0,
                    last_tested=None,
                    test_files=[],
                )

        # Track critical user flows
        critical_flows = [
            "homepage_navigation",
            "vehicle_browsing",
            "build_and_price",
            "dealer_locator",
            "special_offers",
            "finance_calculator",
            "contact_form",
            "test_drive_scheduling",
        ]

        for flow in critical_flows:
            key = f"flow:{flow}"
            if key not in self.coverage_data:
                self.coverage_data[key] = CoverageItem(
                    identifier=flow,
                    type="flow",
                    tested=False,
                    test_count=0,
                    last_tested=None,
                    test_files=[],
                )

    def record_test_execution(
        self, test_name: str, test_file: str, pages_visited: List[str], features_used: List[str]
    ):
        """
        Record a test execution for coverage tracking

        Args:
            test_name: Name of the test
            test_file: Test file path
            pages_visited: List of pages visited during test
            features_used: List of features/flows tested
        """
        timestamp = datetime.now().isoformat()

        # Record execution
        self.test_execution_history.append(
            {
                "test_name": test_name,
                "test_file": test_file,
                "timestamp": timestamp,
                "pages_visited": pages_visited,
                "features_used": features_used,
            }
        )

        # Update coverage for pages
        for page in pages_visited:
            key = f"page:{page}"
            if key in self.coverage_data:
                item = self.coverage_data[key]
                item.tested = True
                item.test_count += 1
                item.last_tested = timestamp
                if test_file not in item.test_files:
                    item.test_files.append(test_file)

        # Update coverage for features
        for feature in features_used:
            key = f"flow:{feature}"
            if key in self.coverage_data:
                item = self.coverage_data[key]
                item.tested = True
                item.test_count += 1
                item.last_tested = timestamp
                if test_file not in item.test_files:
                    item.test_files.append(test_file)

        self._save_coverage_database()

    def get_coverage_percentage(self, coverage_type: Optional[str] = None) -> float:
        """
        Calculate coverage percentage

        Args:
            coverage_type: Filter by type (page, vehicle, flow) or None for all

        Returns:
            Coverage percentage (0-100)
        """
        items = self.coverage_data.values()

        if coverage_type:
            items = [item for item in items if item.type == coverage_type]

        if not items:
            return 0.0

        tested_count = sum(1 for item in items if item.tested)
        return (tested_count / len(items)) * 100

    def get_untested_items(self, coverage_type: Optional[str] = None) -> List[CoverageItem]:
        """Get list of untested items"""
        items = self.coverage_data.values()

        if coverage_type:
            items = [item for item in items if item.type == coverage_type]

        return [item for item in items if not item.tested]

    def get_coverage_gaps(self) -> Dict[str, List[str]]:
        """Identify coverage gaps"""
        gaps = {
            "untested_pages": [],
            "untested_vehicles": [],
            "untested_flows": [],
            "low_coverage_items": [],
        }

        for key, item in self.coverage_data.items():
            if not item.tested:
                if item.type == "page":
                    gaps["untested_pages"].append(item.identifier)
                elif item.type == "vehicle":
                    gaps["untested_vehicles"].append(item.identifier)
                elif item.type == "flow":
                    gaps["untested_flows"].append(item.identifier)
            elif item.test_count < 2:  # Items with low test count
                gaps["low_coverage_items"].append(
                    f"{item.type}:{item.identifier} (tested {item.test_count} time(s))"
                )

        return gaps

    def analyze_sitemap_coverage(self, sitemap_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Analyze coverage based on sitemap

        Args:
            sitemap_file: Path to sitemap.xml or list of URLs

        Returns:
            Coverage analysis
        """
        # This is a simplified version - in production, parse actual sitemap
        known_pages = set(page.value for page in ToyotaPages)
        tested_pages = set(
            item.identifier for item in self.coverage_data.values() if item.type == "page" and item.tested
        )

        return {
            "total_pages": len(known_pages),
            "tested_pages": len(tested_pages),
            "coverage_percentage": (len(tested_pages) / len(known_pages) * 100)
            if known_pages
            else 0,
            "untested_pages": list(known_pages - tested_pages),
        }

    def suggest_tests_with_ai(self, focus_area: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Use AI to suggest missing test scenarios

        Args:
            focus_area: Focus on specific area (e.g., 'homepage', 'vehicles')

        Returns:
            List of suggested test scenarios
        """
        if not self.ai_client:
            return []

        # Get coverage gaps
        gaps = self.get_coverage_gaps()
        coverage_stats = {
            "overall_coverage": self.get_coverage_percentage(),
            "page_coverage": self.get_coverage_percentage("page"),
            "flow_coverage": self.get_coverage_percentage("flow"),
            "gaps": gaps,
        }

        prompt = f"""
        Analyze the test coverage for toyota.com and suggest missing test scenarios:

        Current Coverage:
        {json.dumps(coverage_stats, indent=2)}

        {f"Focus Area: {focus_area}" if focus_area else ""}

        Suggest 5-10 high-priority test scenarios that would improve coverage, considering:
        1. Untested pages and features
        2. Critical user journeys
        3. Edge cases and error scenarios
        4. Mobile and accessibility testing
        5. Performance and visual regression

        Return as JSON array:
        [
            {{
                "test_name": "descriptive_test_name",
                "priority": "critical|high|medium|low",
                "description": "what this test validates",
                "covers": ["page1", "flow1", "feature1"],
                "type": "smoke|regression|visual|performance|accessibility",
                "estimated_value": "why this test is important"
            }}
        ]
        """

        try:
            if self.use_claude:
                response = self.ai_client.messages.create(
                    model=self.ai_model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )
                suggestions_text = response.content[0].text
            else:
                response = self.ai_client.chat.completions.create(
                    model=self.ai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                )
                suggestions_text = response.choices[0].message.content

            suggestions = self._extract_json(suggestions_text)
            return suggestions if isinstance(suggestions, list) else []

        except Exception as e:
            print(f"AI suggestion failed: {e}")
            return []

    def generate_coverage_report(self, output_path: Optional[Path] = None) -> Path:
        """Generate comprehensive coverage report"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = settings.report_dir / f"coverage_report_{timestamp}.json"

        # Generate report
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "overall_coverage": self.get_coverage_percentage(),
                "page_coverage": self.get_coverage_percentage("page"),
                "vehicle_coverage": self.get_coverage_percentage("vehicle"),
                "flow_coverage": self.get_coverage_percentage("flow"),
                "total_items": len(self.coverage_data),
                "tested_items": sum(1 for item in self.coverage_data.values() if item.tested),
                "total_test_executions": len(self.test_execution_history),
            },
            "coverage_by_type": self._get_coverage_by_type(),
            "gaps": self.get_coverage_gaps(),
            "detailed_coverage": {
                key: asdict(item) for key, item in self.coverage_data.items()
            },
            "recent_test_executions": self.test_execution_history[-20:],  # Last 20
        }

        # Add AI suggestions if enabled
        if settings.enable_auto_generation and self.ai_client:
            report["ai_suggestions"] = self.suggest_tests_with_ai()

        # Check if coverage meets threshold
        if report["summary"]["overall_coverage"] < settings.min_coverage_threshold:
            report["warning"] = (
                f"Coverage {report['summary']['overall_coverage']:.1f}% "
                f"is below threshold {settings.min_coverage_threshold}%"
            )

        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Coverage report generated: {output_path}")
        print(f"Overall Coverage: {report['summary']['overall_coverage']:.1f}%")

        return output_path

    def _get_coverage_by_type(self) -> Dict[str, Dict]:
        """Get coverage statistics by type"""
        by_type = defaultdict(lambda: {"total": 0, "tested": 0, "percentage": 0.0})

        for item in self.coverage_data.values():
            by_type[item.type]["total"] += 1
            if item.tested:
                by_type[item.type]["tested"] += 1

        # Calculate percentages
        for type_data in by_type.values():
            if type_data["total"] > 0:
                type_data["percentage"] = (type_data["tested"] / type_data["total"]) * 100

        return dict(by_type)

    def _extract_json(self, text: str) -> any:
        """Extract JSON from AI response"""
        import re

        json_match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        return None

    def _load_coverage_database(self):
        """Load coverage database from file"""
        if self.coverage_db_path.exists():
            try:
                with open(self.coverage_db_path, "r") as f:
                    data = json.load(f)
                    # Reconstruct CoverageItem objects
                    for key, item_data in data.get("coverage", {}).items():
                        self.coverage_data[key] = CoverageItem(**item_data)
                    self.test_execution_history = data.get("history", [])
            except Exception as e:
                print(f"Failed to load coverage database: {e}")

    def _save_coverage_database(self):
        """Save coverage database to file"""
        self.coverage_db_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = {
                "coverage": {key: asdict(item) for key, item in self.coverage_data.items()},
                "history": self.test_execution_history,
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.coverage_db_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save coverage database: {e}")


def main():
    """CLI interface for coverage analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Coverage Analyzer")
    parser.add_argument("--report", action="store_true", help="Generate coverage report")
    parser.add_argument("--suggest-tests", action="store_true", help="Suggest missing tests")
    parser.add_argument("--focus", help="Focus area for suggestions")
    parser.add_argument("--gaps", action="store_true", help="Show coverage gaps")

    args = parser.parse_args()

    analyzer = CoverageAnalyzer()

    if args.gaps:
        gaps = analyzer.get_coverage_gaps()
        print("Coverage Gaps:")
        print(json.dumps(gaps, indent=2))

    elif args.suggest_tests:
        suggestions = analyzer.suggest_tests_with_ai(focus_area=args.focus)
        print("Suggested Tests:")
        print(json.dumps(suggestions, indent=2))

    elif args.report:
        report_path = analyzer.generate_coverage_report()
        print(f"Report generated: {report_path}")

    else:
        # Show summary
        print(f"Overall Coverage: {analyzer.get_coverage_percentage():.1f}%")
        print(f"Page Coverage: {analyzer.get_coverage_percentage('page'):.1f}%")
        print(f"Flow Coverage: {analyzer.get_coverage_percentage('flow'):.1f}%")


if __name__ == "__main__":
    main()
