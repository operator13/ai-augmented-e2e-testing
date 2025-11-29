"""
Pytest Fixtures for AI-Augmented E2E Testing

Provides fixtures for:
- Page objects
- AI services (test generator, self-healing, visual AI, anomaly detector)
- Coverage tracking
- MCP integration
"""
import pytest
from playwright.sync_api import Page

from src.ai.anomaly_detector import AnomalyDetector
from src.ai.coverage_analyzer import CoverageAnalyzer
from src.ai.self_healing import SelectorHealer
from src.ai.test_generator import AITestGenerator
from src.ai.visual_ai import VisualAI
from src.config.settings import settings
from src.core.page_objects.homepage import HomePage
from src.core.page_objects.vehicles_page import VehiclesPage
from src.mcp.integration import ActionRecorder, MCPClient
from src.reporting.error_reporter import ErrorReporter


# Page Object Fixtures
@pytest.fixture
def home_page(page: Page) -> HomePage:
    """
    Fixture for HomePage object

    Args:
        page: Playwright page fixture

    Returns:
        HomePage instance
    """
    return HomePage(page)


@pytest.fixture
def vehicles_page(page: Page) -> VehiclesPage:
    """
    Fixture for VehiclesPage object

    Args:
        page: Playwright page fixture

    Returns:
        VehiclesPage instance
    """
    return VehiclesPage(page)


# AI Service Fixtures
@pytest.fixture
def ai_test_generator() -> AITestGenerator:
    """
    Fixture for AI test generator

    Returns:
        AITestGenerator instance
    """
    return AITestGenerator(use_claude=True)


@pytest.fixture
def selector_healer(page: Page) -> SelectorHealer:
    """
    Fixture for self-healing selector system

    Args:
        page: Playwright page fixture

    Returns:
        SelectorHealer instance
    """
    return SelectorHealer(page, use_claude=True)


@pytest.fixture
def visual_ai() -> VisualAI:
    """
    Fixture for visual regression AI

    Returns:
        VisualAI instance
    """
    return VisualAI(use_claude=True)


@pytest.fixture
def anomaly_detector(page: Page, request) -> AnomalyDetector:
    """
    Fixture for anomaly detection

    Args:
        page: Playwright page fixture
        request: Pytest request object

    Returns:
        AnomalyDetector instance
    """
    detector = AnomalyDetector(page, use_claude=True)
    yield detector

    # After test: check for anomalies
    if settings.enable_anomaly_detection:
        critical_anomalies = detector.get_critical_anomalies()
        if critical_anomalies:
            print(f"\n[WARNING] {len(critical_anomalies)} critical anomalies detected")
            for anomaly in critical_anomalies:
                print(f"  - {anomaly.message}")

        # Store all anomalies for error reporting (if flag enabled)
        if request.config.getoption("--generate-error-reports", default=False):
            if detector.anomalies:
                # Store critical anomalies for report generation
                filtered = [a for a in detector.anomalies if a.severity == 'critical']
                if filtered:
                    request.config._all_anomalies.extend(filtered)
                    request.config._test_contexts.append({
                        'test_name': request.node.name,
                        'test_file': str(request.node.fspath),
                        'page_url': page.url if hasattr(page, 'url') else 'unknown'
                    })


@pytest.fixture(scope="session")
def error_reporter() -> ErrorReporter:
    """
    Session-scoped fixture for error reporting and JIRA ticket generation

    Returns:
        ErrorReporter instance
    """
    return ErrorReporter(report_dir="reports/filtered_errors")


@pytest.fixture(scope="session")
def coverage_analyzer() -> CoverageAnalyzer:
    """
    Session-scoped fixture for coverage tracking

    Returns:
        CoverageAnalyzer instance
    """
    return CoverageAnalyzer(use_claude=True)


@pytest.fixture
def mcp_client() -> MCPClient:
    """
    Fixture for MCP client

    Returns:
        MCPClient instance
    """
    return MCPClient()


@pytest.fixture
def action_recorder(page: Page, mcp_client: MCPClient) -> ActionRecorder:
    """
    Fixture for action recording

    Args:
        page: Playwright page fixture
        mcp_client: MCP client fixture

    Returns:
        ActionRecorder instance
    """
    return ActionRecorder(page, mcp_client)


# Test Lifecycle Hooks
@pytest.fixture(autouse=True)
def test_lifecycle(request, page: Page, coverage_analyzer: CoverageAnalyzer):
    """
    Auto-use fixture to track test lifecycle

    Args:
        request: Pytest request object
        page: Playwright page fixture
        coverage_analyzer: Coverage analyzer fixture
    """
    test_name = request.node.name
    test_file = request.node.fspath.basename

    # Before test
    pages_visited = []
    features_used = []

    yield

    # After test: record coverage
    if hasattr(page, "url"):
        current_url = page.url
        if "toyota.com" in current_url:
            # Extract page path
            path = current_url.replace(settings.base_url, "")
            pages_visited.append(path or "/")

    # Record test execution
    if pages_visited or features_used:
        coverage_analyzer.record_test_execution(
            test_name=test_name,
            test_file=test_file,
            pages_visited=pages_visited,
            features_used=features_used,
        )


@pytest.fixture(autouse=True)
def performance_monitoring(page: Page, anomaly_detector: AnomalyDetector):
    """
    Auto-use fixture to monitor performance

    Args:
        page: Playwright page fixture
        anomaly_detector: Anomaly detector fixture
    """
    yield

    # After test: collect performance metrics
    if settings.enable_anomaly_detection:
        try:
            metrics = anomaly_detector.collect_performance_metrics()
            if metrics:
                print(f"\n[Performance] FCP: {metrics.get('firstContentfulPaint', 0):.0f}ms, "
                      f"Load: {metrics.get('loadComplete', 0):.0f}ms")
        except Exception as e:
            print(f"[Warning] Failed to collect performance metrics: {e}")


# Configuration Fixtures
@pytest.fixture(scope="session")
def base_url() -> str:
    """
    Get base URL for tests

    Returns:
        Base URL string
    """
    return settings.base_url


@pytest.fixture
def test_data():
    """
    Fixture providing test data

    Returns:
        Dictionary of test data
    """
    from src.config.constants import TEST_DATA_TEMPLATES

    return TEST_DATA_TEMPLATES


# Playwright Configuration Hooks
def pytest_addoption(parser):
    """Add custom command-line options"""
    parser.addoption(
        "--generate-error-reports",
        action="store_true",
        default=False,
        help="Generate JIRA-formatted error reports for filtered website bugs"
    )


def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line("markers", "smoke: Smoke tests for critical functionality")
    config.addinivalue_line("markers", "regression: Regression tests")
    config.addinivalue_line("markers", "visual: Visual regression tests")
    config.addinivalue_line("markers", "ai_generated: AI-generated test cases")
    config.addinivalue_line("markers", "critical_path: Critical user journey tests")
    config.addinivalue_line("markers", "performance: Performance tests")


def pytest_runtest_makereport(item, call):
    """Hook to capture test results"""
    if call.when == "call":
        # Access test outcome
        outcome = "passed" if call.excinfo is None else "failed"

        # You can add custom reporting here
        if outcome == "failed":
            print(f"\n[TEST FAILED] {item.name}")


# Session hooks for reporting
@pytest.fixture(scope="session", autouse=True)
def generate_final_reports(request, coverage_analyzer: CoverageAnalyzer, error_reporter: ErrorReporter):
    """
    Generate final reports at end of test session

    Args:
        request: Pytest request object
        coverage_analyzer: Coverage analyzer fixture
        error_reporter: Error reporter fixture
    """
    # Initialize storage for anomalies
    if not hasattr(request.config, '_all_anomalies'):
        request.config._all_anomalies = []
        request.config._test_contexts = []

    yield

    # After all tests complete
    print("\n" + "=" * 80)
    print("Generating final reports...")
    print("=" * 80)

    try:
        # Generate coverage report
        coverage_report_path = coverage_analyzer.generate_coverage_report()
        print(f"Coverage report: {coverage_report_path}")

        # Display coverage summary
        overall_coverage = coverage_analyzer.get_coverage_percentage()
        page_coverage = coverage_analyzer.get_coverage_percentage("page")
        flow_coverage = coverage_analyzer.get_coverage_percentage("flow")

        print(f"\nCoverage Summary:")
        print(f"  Overall: {overall_coverage:.1f}%")
        print(f"  Pages: {page_coverage:.1f}%")
        print(f"  Flows: {flow_coverage:.1f}%")

        # Check coverage threshold
        if overall_coverage < settings.min_coverage_threshold:
            print(f"\n[WARNING] Coverage {overall_coverage:.1f}% is below "
                  f"threshold {settings.min_coverage_threshold}%")

        # Generate error report if flag is enabled AND anomalies were detected
        generate_reports = request.config.getoption("--generate-error-reports", default=False)
        all_anomalies = getattr(request.config, '_all_anomalies', [])
        test_contexts = getattr(request.config, '_test_contexts', [])

        if generate_reports and all_anomalies:
            print(f"\n" + "=" * 80)
            print(f"Generating error reports for {len(all_anomalies)} filtered errors...")
            print("=" * 80)

            # Use first test context for report metadata
            context = test_contexts[0] if test_contexts else {}

            report_result = error_reporter.generate_report(
                anomalies=all_anomalies,
                test_name=context.get('test_name', 'Test Suite'),
                test_url=context.get('page_url', 'https://www.toyota.com'),
                browser="Chromium",
                platform="macOS"
            )

            print(f"\n✅ Error reports generated successfully!")
            print(f"   JSON Report: {report_result['json_report']}")
            print(f"   Summary: {report_result['summary']}")
            print(f"   JIRA Ticket: {report_result['jira_ticket']}")
        elif generate_reports and not all_anomalies:
            print(f"\n📊 No filtered errors detected during this test run.")
            print(f"   (This is good! No website bugs were found)")
        elif not generate_reports:
            # Flag not enabled - don't mention error reports
            pass

    except Exception as e:
        print(f"[Error] Failed to generate reports: {e}")
