"""
Anomaly Detection System

Monitors and detects anomalies in performance, console errors, network requests,
and user behavior during E2E testing.
"""
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from openai import OpenAI
from playwright.sync_api import Page, Response

from src.config.constants import PERFORMANCE_BUDGETS, AnomalyType
from src.config.settings import settings


@dataclass
class Anomaly:
    """Anomaly data class"""

    type: str
    severity: str  # critical, high, medium, low
    message: str
    timestamp: str
    details: Dict[str, Any]
    page_url: str


class AnomalyDetector:
    """Detect and analyze anomalies during test execution"""

    def __init__(self, page: Page, use_claude: bool = True):
        """
        Initialize anomaly detector

        Args:
            page: Playwright page object
            use_claude: Use Claude for AI analysis
        """
        self.page = page
        self.anomalies: List[Anomaly] = []
        self.console_messages: List[Dict] = []
        self.network_requests: List[Dict] = []
        self.performance_metrics: Dict[str, float] = {}

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

        self._setup_listeners()

    def _setup_listeners(self):
        """Set up event listeners for anomaly detection"""
        # Console message listener
        self.page.on("console", self._handle_console_message)

        # Page error listener
        self.page.on("pageerror", self._handle_page_error)

        # Request/Response listeners
        self.page.on("request", self._handle_request)
        self.page.on("response", self._handle_response)

        # Request failed listener
        self.page.on("requestfailed", self._handle_request_failed)

    def _handle_console_message(self, msg):
        """Handle console messages"""
        console_data = {
            "type": msg.type,
            "text": msg.text,
            "location": msg.location,
            "timestamp": datetime.now().isoformat(),
        }
        self.console_messages.append(console_data)

        # Check for errors or warnings
        if msg.type in ["error", "warning"]:
            severity = "high" if msg.type == "error" else "medium"
            self._record_anomaly(
                anomaly_type=AnomalyType.CONSOLE_ERROR.value,
                severity=severity,
                message=f"Console {msg.type}: {msg.text}",
                details=console_data,
            )

    def _handle_page_error(self, error):
        """Handle page errors"""
        self._record_anomaly(
            anomaly_type=AnomalyType.CONSOLE_ERROR.value,
            severity="critical",
            message=f"Page Error: {str(error)}",
            details={"error": str(error), "type": "page_error"},
        )

    def _handle_request(self, request):
        """Handle network requests"""
        request_data = {
            "url": request.url,
            "method": request.method,
            "resource_type": request.resource_type,
            "timestamp": datetime.now().isoformat(),
        }
        self.network_requests.append(request_data)

    def _handle_response(self, response: Response):
        """Handle network responses"""
        # Check for failed responses
        if response.status >= 400:
            severity = "critical" if response.status >= 500 else "high"
            self._record_anomaly(
                anomaly_type=AnomalyType.NETWORK_ERROR.value,
                severity=severity,
                message=f"HTTP {response.status}: {response.url}",
                details={
                    "status": response.status,
                    "url": response.url,
                    "status_text": response.status_text,
                },
            )

        # Check for slow responses
        timing = response.request.timing
        if timing and "responseEnd" in timing:
            response_time = timing["responseEnd"] - timing["requestStart"]
            if response_time > 5000:  # 5 seconds
                self._record_anomaly(
                    anomaly_type=AnomalyType.PERFORMANCE.value,
                    severity="medium",
                    message=f"Slow response: {response.url} ({response_time}ms)",
                    details={
                        "url": response.url,
                        "response_time_ms": response_time,
                        "resource_type": response.request.resource_type,
                    },
                )

    def _handle_request_failed(self, request):
        """Handle failed requests"""
        self._record_anomaly(
            anomaly_type=AnomalyType.NETWORK_ERROR.value,
            severity="high",
            message=f"Request failed: {request.url}",
            details={
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
                "failure": request.failure,
            },
        )

    def collect_performance_metrics(self) -> Dict[str, float]:
        """Collect Web Vitals and performance metrics"""
        try:
            # Collect performance metrics using Performance API
            metrics = self.page.evaluate(
                """() => {
                const perfEntries = performance.getEntriesByType('navigation')[0];
                const paintEntries = performance.getEntriesByType('paint');

                return {
                    // Navigation timing
                    domContentLoaded: perfEntries.domContentLoadedEventEnd - perfEntries.domContentLoadedEventStart,
                    loadComplete: perfEntries.loadEventEnd - perfEntries.loadEventStart,
                    domInteractive: perfEntries.domInteractive,

                    // Paint timing
                    firstPaint: paintEntries.find(e => e.name === 'first-paint')?.startTime || 0,
                    firstContentfulPaint: paintEntries.find(e => e.name === 'first-contentful-paint')?.startTime || 0,

                    // Resource timing
                    totalRequests: performance.getEntriesByType('resource').length,
                    totalTransferSize: performance.getEntriesByType('resource')
                        .reduce((sum, r) => sum + (r.transferSize || 0), 0),
                };
            }"""
            )

            self.performance_metrics = metrics
            self._check_performance_budgets(metrics)

            return metrics

        except Exception as e:
            print(f"Failed to collect performance metrics: {e}")
            return {}

    def _check_performance_budgets(self, metrics: Dict[str, float]):
        """Check if performance metrics exceed budgets"""
        # Check First Contentful Paint
        if "firstContentfulPaint" in metrics:
            fcp = metrics["firstContentfulPaint"]
            if fcp > PERFORMANCE_BUDGETS["FCP"]:
                self._record_anomaly(
                    anomaly_type=AnomalyType.PERFORMANCE.value,
                    severity="medium",
                    message=f"First Contentful Paint exceeded budget: {fcp}ms > {PERFORMANCE_BUDGETS['FCP']}ms",
                    details={"metric": "FCP", "value": fcp, "budget": PERFORMANCE_BUDGETS["FCP"]},
                )

        # Check page load time
        if "loadComplete" in metrics:
            load_time = metrics["loadComplete"]
            if load_time > settings.max_page_load_time:
                self._record_anomaly(
                    anomaly_type=AnomalyType.PERFORMANCE.value,
                    severity="high",
                    message=f"Page load time exceeded: {load_time}ms > {settings.max_page_load_time}ms",
                    details={
                        "metric": "PageLoad",
                        "value": load_time,
                        "budget": settings.max_page_load_time,
                    },
                )

    def detect_behavioral_anomalies(self, expected_behavior: Dict[str, Any]) -> List[Anomaly]:
        """
        Detect behavioral anomalies based on expected patterns

        Args:
            expected_behavior: Expected behavior patterns
                {
                    'min_elements': 5,
                    'required_sections': ['header', 'footer'],
                    'max_load_time': 3000
                }

        Returns:
            List of detected anomalies
        """
        behavioral_anomalies = []

        # Check for required elements
        if "required_sections" in expected_behavior:
            for section in expected_behavior["required_sections"]:
                try:
                    element = self.page.locator(f"[data-section='{section}'], #{section}, .{section}")
                    if not element.is_visible(timeout=5000):
                        self._record_anomaly(
                            anomaly_type=AnomalyType.BEHAVIORAL.value,
                            severity="high",
                            message=f"Required section not visible: {section}",
                            details={"section": section},
                        )
                except Exception:
                    self._record_anomaly(
                        anomaly_type=AnomalyType.BEHAVIORAL.value,
                        severity="high",
                        message=f"Required section not found: {section}",
                        details={"section": section},
                    )

        return behavioral_anomalies

    def _record_anomaly(
        self, anomaly_type: str, severity: str, message: str, details: Dict[str, Any]
    ):
        """Record an anomaly"""
        anomaly = Anomaly(
            type=anomaly_type,
            severity=severity,
            message=message,
            timestamp=datetime.now().isoformat(),
            details=details,
            page_url=self.page.url,
        )
        self.anomalies.append(anomaly)

        # Log critical anomalies immediately
        if severity == "critical":
            print(f"[CRITICAL ANOMALY] {message}")

    def get_anomalies_by_type(self, anomaly_type: str) -> List[Anomaly]:
        """Get anomalies filtered by type"""
        return [a for a in self.anomalies if a.type == anomaly_type]

    def get_critical_anomalies(self) -> List[Anomaly]:
        """Get all critical anomalies"""
        return [a for a in self.anomalies if a.severity == "critical"]

    def get_test_blocking_errors(self) -> List[Anomaly]:
        """
        Get critical errors that should fail tests (excludes known website bugs).

        This method filters out known website errors that don't affect test execution.
        Website bugs are still collected and can be reported via --generate-error-reports.

        Returns:
            List of critical anomalies that indicate actual test failures
        """
        critical = self.get_critical_anomalies()

        # Filter out known website errors that don't affect test functionality
        test_blocking = []
        for anomaly in critical:
            message_lower = str(anomaly.message).lower()

            # Skip known website bugs (these get reported separately)
            if 'play()' in message_lower and 'pause()' in message_lower:
                # Video autoplay errors - website bug, not test failure
                continue
            elif '12166' in anomaly.message or '12161' in anomaly.message or 'dgid' in message_lower:
                # Dealer lookup errors - website bug, not test failure
                continue
            elif 'cannot read properties of undefined' in message_lower or 'cannot read properties of null' in message_lower:
                # JavaScript null/undefined errors - website bug, not test failure
                continue
            elif 'http 503' in message_lower:
                # Third-party service errors - website bug, not test failure
                continue
            elif 'awswaf-captcha' in message_lower or 'customelementregistry' in message_lower:
                # AWS WAF CAPTCHA registration errors - website bug, not test failure
                continue
            elif 'mutationobserver' in message_lower:
                # MutationObserver errors - website bug, not test failure
                continue
            elif 'http 403' in message_lower:
                # Image 403 errors - website bug, not test failure
                continue
            else:
                # This is an actual test-blocking error
                test_blocking.append(anomaly)

        return test_blocking

    def analyze_anomalies_with_ai(self) -> Dict[str, Any]:
        """Use AI to analyze all detected anomalies and provide insights"""
        if not self.ai_client or not self.anomalies:
            return {"error": "No AI client or no anomalies to analyze"}

        # Prepare anomaly data
        anomaly_summary = {
            "total_anomalies": len(self.anomalies),
            "by_type": {},
            "by_severity": {},
            "anomalies": [asdict(a) for a in self.anomalies],
        }

        for anomaly in self.anomalies:
            # Count by type
            anomaly_summary["by_type"][anomaly.type] = (
                anomaly_summary["by_type"].get(anomaly.type, 0) + 1
            )
            # Count by severity
            anomaly_summary["by_severity"][anomaly.severity] = (
                anomaly_summary["by_severity"].get(anomaly.severity, 0) + 1
            )

        prompt = f"""
        Analyze the following anomalies detected during E2E testing of toyota.com:

        {json.dumps(anomaly_summary, indent=2)}

        Provide:
        1. Root cause analysis for major issues
        2. Which anomalies are critical and which can be ignored
        3. Recommended actions to fix each issue
        4. Patterns or correlations between anomalies
        5. Overall health assessment

        Return as JSON:
        {{
            "overall_assessment": "critical|concerning|acceptable|good",
            "critical_issues": [
                {{
                    "issue": "description",
                    "impact": "description",
                    "recommended_action": "description"
                }}
            ],
            "patterns_detected": ["pattern descriptions"],
            "false_positives": ["anomaly indices that are likely false positives"],
            "summary": "overall summary"
        }}
        """

        try:
            if self.use_claude:
                response = self.ai_client.messages.create(
                    model=self.ai_model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}],
                )
                analysis_text = response.content[0].text
            else:
                response = self.ai_client.chat.completions.create(
                    model=self.ai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                )
                analysis_text = response.choices[0].message.content

            analysis = self._extract_json(analysis_text)
            return analysis if analysis else {"raw_response": analysis_text}

        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from AI response"""
        import re

        json_match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        json_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        return None

    def generate_report(self, output_path: Optional[Path] = None) -> Path:
        """Generate anomaly detection report"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = settings.report_dir / f"anomaly_report_{timestamp}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "page_url": self.page.url,
            "total_anomalies": len(self.anomalies),
            "anomalies_by_type": {},
            "anomalies_by_severity": {},
            "performance_metrics": self.performance_metrics,
            "console_messages": self.console_messages[-50:],  # Last 50 messages
            "network_summary": {
                "total_requests": len(self.network_requests),
                "failed_requests": len(
                    [a for a in self.anomalies if a.type == AnomalyType.NETWORK_ERROR.value]
                ),
            },
            "anomalies": [asdict(a) for a in self.anomalies],
        }

        # Group anomalies
        for anomaly in self.anomalies:
            report["anomalies_by_type"][anomaly.type] = (
                report["anomalies_by_type"].get(anomaly.type, 0) + 1
            )
            report["anomalies_by_severity"][anomaly.severity] = (
                report["anomalies_by_severity"].get(anomaly.severity, 0) + 1
            )

        # Add AI analysis if available
        if settings.enable_anomaly_detection:
            ai_analysis = self.analyze_anomalies_with_ai()
            report["ai_analysis"] = ai_analysis

        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Anomaly report generated: {output_path}")
        return output_path

    def reset(self):
        """Reset anomaly detection state"""
        self.anomalies = []
        self.console_messages = []
        self.network_requests = []
        self.performance_metrics = {}
