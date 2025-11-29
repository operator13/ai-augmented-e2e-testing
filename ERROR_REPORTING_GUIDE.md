# Error Reporting & JIRA Integration Guide

## Overview

The AI-Augmented E2E Testing Framework now includes **automatic error detection, categorization, and JIRA-formatted bug report generation** for filtered website errors.

This system allows you to:
- ✅ **Detect** all website errors during testing
- ✅ **Filter** known issues (video errors, network failures, etc.)
- ✅ **Record** filtered errors for future bug reports
- ✅ **Generate** JIRA-ready bug tickets with reproduction steps
- ✅ **Track** error trends over time

---

## Quick Start

### Generate Error Reports

```bash
# Run the error report generator
python scripts/generate_error_reports.py
```

This will create:
- **JSON report** with all error details
- **JIRA tickets** (one per error category)
- **Summary report** with overview

---

## Report Structure

### Generated Files

```
reports/filtered_errors/
├── error_report_YYYYMMDD_HHMMSS.json      # Detailed JSON report
├── SUMMARY_YYYYMMDD_HHMMSS.txt            # Human-readable summary
└── jira_tickets/
    ├── JIRA_video_playback_YYYYMMDD_HHMMSS.txt
    ├── JIRA_network_503_YYYYMMDD_HHMMSS.txt
    ├── JIRA_dealer_lookup_YYYYMMDD_HHMMSS.txt
    └── JIRA_js_undefined_YYYYMMDD_HHMMSS.txt
```

### JSON Report Format

```json
{
  "report_generated": "2025-11-02T19:48:45",
  "test_context": {
    "test_name": "Navigation Test Suite",
    "test_date": "2025-11-02 19:48:45",
    "test_url": "https://www.toyota.com",
    "browser": "Chromium",
    "platform": "macOS"
  },
  "summary": {
    "total_errors": 4,
    "categories": {
      "video_playback": 1,
      "network_503": 1,
      "dealer_lookup": 1,
      "js_undefined": 1
    }
  },
  "errors_by_category": {
    "video_playback": [...],
    "network_503": [...],
    ...
  }
}
```

---

## JIRA Ticket Format

Each JIRA ticket includes:

### 1. Header Information
- **Priority**: Low/Medium/High based on impact
- **Component**: Frontend/Backend/CDN/etc.
- **Environment**: Browser and platform details

### 2. Summary
- Concise description of the issue
- Error frequency

### 3. Description
- Detailed error explanation
- Error messages with code blocks
- Reference links to documentation

### 4. Steps to Reproduce
**Exact, numbered steps** you can follow to reproduce the issue:

```
h2. Steps to Reproduce

# Open Chrome Browser with DevTools (F12)
# Navigate to *Console* tab
# Clear console (trash icon)
# Navigate to: https://www.toyota.com/camry
# Observe errors appearing during page load
```

### 5. Expected vs Actual Behavior
- What should happen
- What actually happens
- Error counts and patterns

### 6. Technical Details
- First occurrence timestamp
- Affected pages
- Error patterns
- Stack traces (if available)

### 7. Impact Assessment
- **Severity**: Low/Medium/High
- **User Impact**: Description of how users are affected
- **Business Impact**: Conversion, UX, etc.
- **Frequency**: How often it occurs

### 8. Root Cause Analysis
- Possible reasons for the error
- Technical investigation suggestions

### 9. Recommended Actions
- Prioritized list of fixes
- Investigation steps
- Monitoring recommendations

### 10. Suggested Fix
Code examples showing:
```javascript
// Current problematic code
someFunction();

// Recommended fix
try {
  someFunction();
} catch (error) {
  // Handle error
}
```

### 11. Test Evidence
- Test name and date
- Total occurrences
- Links to detailed reports

---

## Error Categories

### 1. Video Playback Errors

**Error**: `The play() request was interrupted by pause()`

**Root Cause**: Race condition in video autoplay

**Steps to Reproduce**:
1. Open Chrome DevTools → Console tab
2. Navigate to https://www.toyota.com/camry
3. Watch for video playback errors during page load
4. Navigate to #gallery and #features sections
5. Observe additional errors

**Impact**: Low - videos still work, but console errors present

---

### 2. Network 503 Errors

**Error**: `HTTP 503: https://d.agkn.com/pixel/...`

**Root Cause**: Third-party advertising pixel service unavailable

**Steps to Reproduce**:
1. Open Chrome DevTools → Network tab
2. Filter by `d.agkn.com`
3. Navigate to https://www.toyota.com
4. Observe red 503 errors in network panel

**Impact**: Low - page functionality unaffected, tracking data incomplete

---

### 3. Dealer Lookup Errors

**Error**: `Unable to retrieve dealer details for dealer code: 12166`

**Root Cause**: Dealer API returning errors for specific dealer codes

**Steps to Reproduce**:
1. Open Chrome DevTools → Console tab
2. Navigate to https://www.toyota.com
3. Wait for page load
4. Observe "Unable to retrieve dealer details" error

**Impact**: Medium - users may not see local dealer information

---

### 4. JavaScript Undefined Errors

**Error**: `Cannot read properties of undefined (reading 'remove')`

**Root Cause**: Missing null checks before accessing object properties

**Steps to Reproduce**:
1. Open Chrome DevTools → Console tab
2. Navigate to https://www.toyota.com
3. Click Vehicles → RAV4
4. Observe JavaScript errors during page load

**Impact**: Medium - page works but potential for UI glitches

---

### 5. Image 403 Errors

**Error**: `HTTP 403 Forbidden` for image assets

**Root Cause**: CDN access control issues or invalid image URLs

**Steps to Reproduce**:
1. Open Chrome DevTools → Network tab
2. Filter by `Img` or `tmna.aemassets.toyota.com`
3. Navigate to https://www.toyota.com/camry
4. Observe red 403 errors for images

**Impact**: High - images not displaying affects UX

---

## Using JIRA Tickets

### 1. Open JIRA Ticket File

```bash
# View list of tickets
ls reports/filtered_errors/jira_tickets/

# Open specific ticket
cat reports/filtered_errors/jira_tickets/JIRA_video_playback_*.txt
```

### 2. Copy Content to JIRA

1. Open your JIRA project
2. Click "Create Issue"
3. Select issue type: "Bug"
4. **Copy the entire ticket content** from the `.txt` file
5. **Paste into JIRA description** (JIRA will auto-format the markup)
6. Adjust priority/assignee as needed
7. Click "Create"

### 3. JIRA Formatting

The tickets use **JIRA Wiki Markup**:

| Markdown | JIRA Display |
|----------|--------------|
| `h1. Title` | Large heading |
| `h2. Section` | Medium heading |
| `*Bold*` | **Bold text** |
| `{code:javascript}...{code}` | Code block |
| `# Step 1` | Numbered list |
| `* Item` | Bullet list |

---

## Tracking Error Trends

### Generate Reports Over Time

```bash
# Week 1
python scripts/generate_error_reports.py
# → error_report_20251102_*.json

# Week 2
python scripts/generate_error_reports.py
# → error_report_20251109_*.json

# Compare trends
diff <(jq .summary.categories reports/filtered_errors/error_report_20251102_*.json) \
     <(jq .summary.categories reports/filtered_errors/error_report_20251109_*.json)
```

### Monitoring Dashboard (Future Enhancement)

Create a simple dashboard:

```python
import json
from pathlib import Path

reports = sorted(Path("reports/filtered_errors").glob("error_report_*.json"))

for report_path in reports[-5:]:  # Last 5 reports
    with open(report_path) as f:
        data = json.load(f)
        print(f"{data['report_generated']}: {data['summary']['total_errors']} errors")
        for category, count in data['summary']['categories'].items():
            print(f"  - {category}: {count}")
```

---

## Integration with Tests

### Automatic Error Collection (Future)

The error reporter integrates with the anomaly detector:

```python
@pytest.fixture
def anomaly_detector(page: Page, request):
    """Fixture that automatically collects errors."""
    detector = AnomalyDetector(page, use_claude=True)
    yield detector

    # Errors are automatically collected during test
    # Access with: detector.anomalies
```

### Manual Error Reporting

You can also manually generate reports from test code:

```python
from src.reporting.error_reporter import ErrorReporter

def test_with_error_reporting(page, anomaly_detector):
    # Your test code...
    page.goto("https://www.toyota.com/camry")

    # After test
    reporter = ErrorReporter()
    report = reporter.generate_report(
        anomalies=anomaly_detector.anomalies,
        test_name="Camry Test",
        test_url=page.url
    )
    print(f"Report: {report['json_report']}")
```

---

## Best Practices

### 1. Regular Report Generation

Run error reports weekly to track trends:

```bash
# Add to weekly CI job
python scripts/generate_error_reports.py
```

### 2. Error Prioritization

**High Priority** (Fix immediately):
- Image loading failures (403)
- API errors affecting functionality
- JavaScript errors causing UI breaks

**Medium Priority** (Fix soon):
- Dealer lookup failures
- JS undefined errors on specific pages

**Low Priority** (Monitor):
- Video playback race conditions
- Third-party service failures (503)

### 3. Communication with Toyota

When reporting bugs to Toyota:
1. Use the generated JIRA tickets as templates
2. Include the JSON report for detailed data
3. Reference the "Test Evidence" section for credibility
4. Highlight business impact

### 4. Version Control

```bash
# Don't commit generated reports
echo "reports/filtered_errors/*.json" >> .gitignore
echo "reports/filtered_errors/*.txt" >> .gitignore

# Do commit the reporting code
git add src/reporting/
git add scripts/generate_error_reports.py
```

---

## Customization

### Add New Error Category

Edit `src/reporting/error_reporter.py`:

```python
def categorize_errors(self, anomalies: List) -> Dict[str, List[Dict]]:
    """Add your custom category."""
    for anomaly in anomalies:
        message_lower = str(anomaly.message).lower()

        # Add new category
        if 'your_error_pattern' in message_lower:
            category = 'custom_error'
            categorized[category].append(error_dict)
```

### Create Custom JIRA Template

Add template method to `JiraFormatter`:

```python
@staticmethod
def _custom_error_template(errors: List[Dict], context: Dict) -> str:
    """Your custom JIRA template."""
    return f"""
h1. Custom Error Title

*Priority:* Medium
*Component:* Your Component

h2. Summary
{len(errors)} errors detected

h2. Steps to Reproduce
# Your steps here
"""
```

---

## Troubleshooting

### No Reports Generated

```bash
# Check if directory exists
ls -la reports/filtered_errors/

# Run with verbose output
python -v scripts/generate_error_reports.py
```

### JIRA Formatting Issues

If JIRA doesn't format correctly:
1. Ensure you're using JIRA Wiki Markup (not Markdown)
2. Check JIRA project settings for markup support
3. Try pasting in "Text Mode" then switching to "Visual Mode"

### Missing Error Categories

If errors aren't categorized:
1. Check error message patterns in `categorize_errors()`
2. Add debug print to see raw error messages
3. Add new patterns to match your errors

---

## Summary

You now have a complete error reporting system that:

✅ **Detects** all website errors automatically
✅ **Filters** known issues so tests pass
✅ **Records** errors for bug tracking
✅ **Generates** professional JIRA-ready reports
✅ **Provides** exact reproduction steps
✅ **Tracks** error trends over time

**Next Steps:**
1. Run `python scripts/generate_error_reports.py` to see it in action
2. Review the generated JIRA tickets in `reports/filtered_errors/jira_tickets/`
3. Copy a ticket into your JIRA system
4. Set up weekly report generation
5. Monitor error trends and prioritize fixes

---

## Files Created

| File | Purpose |
|------|---------|
| `src/reporting/error_reporter.py` | Main error reporter module |
| `src/reporting/__init__.py` | Package initialization |
| `scripts/generate_error_reports.py` | CLI script to generate reports |
| `reports/filtered_errors/` | Output directory for all reports |
| `ERROR_REPORTING_GUIDE.md` | This documentation |

---

## Support

For questions or issues:
1. Review this guide
2. Check example reports in `reports/filtered_errors/`
3. Review code in `src/reporting/error_reporter.py`
4. Test with `python scripts/generate_error_reports.py`

**Happy Bug Reporting!** 🎫🐛
