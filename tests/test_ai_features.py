"""
AI-Powered Test Features Demo

Demonstrates the AI-augmented capabilities of the framework:
- Self-healing selectors
- AI-powered visual regression
- Anomaly detection
- Intelligent test generation
"""
import pytest
from playwright.sync_api import Page

from src.ai.anomaly_detector import AnomalyDetector
from src.ai.self_healing import SelectorHealer
from src.ai.test_generator import AITestGenerator
from src.ai.visual_ai import VisualAI
from src.core.page_objects.homepage import HomePage


@pytest.mark.ai_generated
@pytest.mark.smoke
def test_self_healing_selector_demo(page: Page, selector_healer: SelectorHealer):
    """
    Demonstrate self-healing selectors

    This test shows how the framework automatically heals broken selectors
    """
    page.goto("https://www.toyota.com")

    # Try to find an element with a potentially fragile selector
    # If the selector breaks, the healer will attempt to fix it
    try:
        element = selector_healer.find_element(
            "nav a:has-text('Vehicles')",  # Flexible text-based selector
            timeout=10000,
            auto_heal=True
        )
        assert element is not None
        print("\n[Self-Healing] Element found successfully")
    except Exception as e:
        pytest.fail(f"Self-healing selector failed: {e}")


@pytest.mark.visual
@pytest.mark.ai_generated
def test_ai_visual_regression_demo(home_page: HomePage, visual_ai: VisualAI):
    """
    Demonstrate AI-powered visual regression testing

    AI can differentiate between acceptable changes (dates, ads, dynamic content)
    and real visual regressions (layout, missing elements)
    """
    home_page.open()
    home_page.wait_for_page_load()

    # Perform AI-powered visual comparison
    result = visual_ai.compare_visual(
        home_page.page,
        screenshot_name="homepage_ai_demo",
        use_ai_analysis=True
    )

    print(f"\n[Visual AI] Status: {result['status']}")
    print(f"[Visual AI] Difference: {result['diff_percentage']}%")

    if "ai_analysis" in result:
        analysis = result["ai_analysis"]
        print(f"[Visual AI] Verdict: {analysis.get('verdict', 'N/A')}")
        print(f"[Visual AI] Recommendation: {analysis.get('recommendation', 'N/A')}")


@pytest.mark.performance
@pytest.mark.ai_generated
def test_anomaly_detection_demo(home_page: HomePage, anomaly_detector: AnomalyDetector):
    """
    Demonstrate anomaly detection

    Detects performance issues, console errors, network problems
    """
    home_page.open()

    # Collect performance metrics
    metrics = anomaly_detector.collect_performance_metrics()

    print(f"\n[Anomaly Detection] Performance Metrics:")
    print(f"  FCP: {metrics.get('firstContentfulPaint', 0):.0f}ms")
    print(f"  Load Time: {metrics.get('loadComplete', 0):.0f}ms")
    print(f"  Total Requests: {metrics.get('totalRequests', 0)}")

    # Get detected anomalies
    all_anomalies = anomaly_detector.anomalies

    if all_anomalies:
        print(f"\n[Anomaly Detection] Detected {len(all_anomalies)} anomalies:")
        for anomaly in all_anomalies[:5]:  # Show first 5
            print(f"  - [{anomaly.severity}] {anomaly.message}")

    # Get AI analysis of anomalies
    if all_anomalies:
        ai_analysis = anomaly_detector.analyze_anomalies_with_ai()
        if "overall_assessment" in ai_analysis:
            print(f"\n[AI Analysis] Overall: {ai_analysis['overall_assessment']}")


@pytest.mark.ai_generated
def test_generate_test_scenario_demo(ai_test_generator: AITestGenerator):
    """
    Demonstrate AI test generation

    Generate test scenarios based on feature descriptions
    """
    # Generate test scenarios for a feature
    scenarios = ai_test_generator.suggest_test_scenarios(
        feature="Vehicle Search and Filter",
        context="Users should be able to search and filter vehicles by type, price, and features"
    )

    print(f"\n[AI Test Generator] Generated {len(scenarios)} test scenarios:")
    for i, scenario in enumerate(scenarios[:3], 1):  # Show first 3
        print(f"\n{i}. {scenario.get('name', 'Unnamed scenario')}")
        print(f"   Priority: {scenario.get('priority', 'N/A')}")
        print(f"   Type: {scenario.get('type', 'N/A')}")
        print(f"   Description: {scenario.get('description', 'N/A')}")

    assert len(scenarios) > 0, "AI should generate at least one scenario"


@pytest.mark.ai_generated
@pytest.mark.skip(reason="Demo only - requires manual review")
def test_generate_test_code_demo(ai_test_generator: AITestGenerator):
    """
    Demonstrate generating actual test code from descriptions

    This is a demonstration - generated code should be reviewed before use
    """
    # Generate test code for a user flow
    test_code = ai_test_generator.generate_test_from_flow(
        page="/vehicles",
        user_flow="User navigates to vehicles page, filters by SUV category, and selects a vehicle",
        requirements=[
            "Verify vehicles page loads",
            "Verify filtering works correctly",
            "Verify vehicle selection navigates to details page"
        ],
        test_name="test_vehicle_selection_flow"
    )

    print("\n[AI Generated Test Code]:")
    print("=" * 80)
    print(test_code)
    print("=" * 80)

    assert "def test_vehicle_selection_flow" in test_code
    assert "import pytest" in test_code


@pytest.mark.ai_generated
@pytest.mark.regression
def test_comprehensive_page_analysis(home_page: HomePage, anomaly_detector: AnomalyDetector):
    """
    Comprehensive page analysis using multiple AI features

    This test combines:
    - Performance monitoring
    - Console error detection
    - Network request analysis
    - Behavioral anomaly detection
    """
    home_page.open()

    # Collect all metrics
    metrics = anomaly_detector.collect_performance_metrics()

    # Check for behavioral anomalies
    expected_behavior = {
        "required_sections": ["navigation", "header"],
        "min_elements": 3,
        "max_load_time": 10000
    }

    anomaly_detector.detect_behavioral_anomalies(expected_behavior)

    # Generate comprehensive report
    report_path = anomaly_detector.generate_report()

    print(f"\n[Comprehensive Analysis] Report generated: {report_path}")

    # Get summary
    critical_anomalies = anomaly_detector.get_critical_anomalies()
    if critical_anomalies:
        print(f"[WARNING] Found {len(critical_anomalies)} critical anomalies")
        for anomaly in critical_anomalies:
            print(f"  - {anomaly.message}")
    else:
        print("[SUCCESS] No critical anomalies detected")


@pytest.mark.ai_generated
def test_selector_suggestions(selector_healer: SelectorHealer):
    """
    Demonstrate AI-powered selector suggestions

    Given an element description, AI suggests multiple robust selector options
    """
    # Get AI suggestions for robust selectors
    suggestions = selector_healer.generate_robust_selector(
        element_description="The main navigation menu containing links to Vehicles, Shopping Tools, and Owners"
    )

    print("\n[Selector Suggestions] AI-generated selectors:")
    for i, selector in enumerate(suggestions[:5], 1):
        print(f"  {i}. {selector}")

    assert len(suggestions) > 0, "AI should suggest at least one selector"


@pytest.mark.critical_path
@pytest.mark.ai_generated
def test_ai_assisted_debugging(home_page: HomePage, page: Page, anomaly_detector: AnomalyDetector):
    """
    Demonstrate AI-assisted debugging

    When a test fails, AI can analyze the failure and suggest fixes
    """
    home_page.open()

    # Intentionally interact with page to collect data
    home_page.wait_for_page_load()

    # Collect console messages and network data
    console_errors = [msg for msg in anomaly_detector.console_messages
                     if msg.get("type") == "error"]

    network_errors = anomaly_detector.get_anomalies_by_type("network_error")

    print(f"\n[AI Debugging] Console Errors: {len(console_errors)}")
    print(f"[AI Debugging] Network Errors: {len(network_errors)}")

    # If there are issues, AI can analyze them
    if console_errors or network_errors:
        print("\n[AI Debugging] Analyzing issues...")
        analysis = anomaly_detector.analyze_anomalies_with_ai()

        if "critical_issues" in analysis:
            print(f"\nCritical Issues Found:")
            for issue in analysis["critical_issues"]:
                print(f"  - {issue.get('issue')}")
                print(f"    Action: {issue.get('recommended_action')}")
