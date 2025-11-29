#!/usr/bin/env python3
"""
Generate Error Reports from Test Runs

This script demonstrates how to generate JIRA-formatted bug reports
for filtered website errors detected during testing.

Usage:
    python scripts/generate_error_reports.py

Or run after specific tests to generate reports for those errors.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reporting.error_reporter import ErrorReporter
from datetime import datetime


def create_sample_errors():
    """Create sample errors for demonstration."""
    # Simulate errors that would be detected during testing
    sample_errors = [
        {
            'type': 'page_error',
            'severity': 'critical',
            'message': 'The play() request was interrupted by a call to pause(). https://goo.gl/LdLk22',
            'timestamp': datetime.now().isoformat(),
            'page_url': 'https://www.toyota.com/camry',
            'details': {}
        },
        {
            'type': 'network_error',
            'severity': 'critical',
            'message': 'HTTP 503: https://d.agkn.com/pixel/9343/?che=140694558&mvcsid=59988629724403261381975705367329781651',
            'timestamp': datetime.now().isoformat(),
            'page_url': 'https://www.toyota.com',
            'details': {
                'status': 503,
                'url': 'https://d.agkn.com/pixel/9343/?che=140694558&mvcsid=59988629724403261381975705367329781651'
            }
        },
        {
            'type': 'page_error',
            'severity': 'critical',
            'message': 'Uncaught (in promise) Unable to retrieve dealer details for dealer code: 12166',
            'timestamp': datetime.now().isoformat(),
            'page_url': 'https://www.toyota.com/camry',
            'details': {}
        },
        {
            'type': 'page_error',
            'severity': 'critical',
            'message': "Cannot read properties of undefined (reading 'remove')",
            'timestamp': datetime.now().isoformat(),
            'page_url': 'https://www.toyota.com/rav4/',
            'details': {}
        }
    ]

    # Convert to anomaly-like objects
    class MockAnomaly:
        def __init__(self, data):
            self.type = data['type']
            self.severity = data['severity']
            self.message = data['message']
            self.timestamp = data['timestamp']
            self.page_url = data['page_url']
            self.details = data['details']

    return [MockAnomaly(e) for e in sample_errors]


def main():
    """Generate sample error reports."""
    print("=" * 80)
    print("TOYOTA WEBSITE ERROR REPORTER")
    print("=" * 80)
    print()

    # Initialize reporter
    reporter = ErrorReporter(report_dir="reports/filtered_errors")

    # Create sample errors (in real usage, these come from AnomalyDetector)
    anomalies = create_sample_errors()

    print(f"📊 Generating reports for {len(anomalies)} detected errors...")
    print()

    # Generate reports
    result = reporter.generate_report(
        anomalies=anomalies,
        test_name="Navigation Test Suite",
        test_url="https://www.toyota.com",
        browser="Chromium",
        platform="macOS"
    )

    print()
    print("=" * 80)
    print("✅ REPORTS GENERATED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print(f"📁 Reports Location: reports/filtered_errors/")
    print()
    print(f"📄 JSON Report: {Path(result['json_report']).name}")
    print(f"📋 Summary Report: {Path(result['summary']).name}")
    print()
    print(f"🎫 JIRA Tickets Generated: {len(result['jira_tickets'])}")
    for category, path in result['jira_tickets'].items():
        print(f"   • {category}: {Path(path).name}")
    print()
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Review the JSON report for detailed error information:")
    print(f"   cat {result['json_report']}")
    print()
    print("2. Open JIRA tickets to create bug reports:")
    print(f"   ls reports/filtered_errors/jira_tickets/")
    print()
    print("3. Copy/paste JIRA ticket content into your JIRA system")
    print()
    print("4. Each ticket includes:")
    print("   • Detailed steps to reproduce")
    print("   • Expected vs actual behavior")
    print("   • Technical details and error messages")
    print("   • Impact assessment")
    print("   • Suggested fixes")
    print()


if __name__ == "__main__":
    main()
