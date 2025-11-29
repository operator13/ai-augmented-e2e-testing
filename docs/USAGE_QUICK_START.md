# Quick Start Guide: Error Reporting with JIRA Tickets

## TL;DR

```bash
# Normal test run (no reports)
pytest tests/ai_generated/test_*_navigation.py -v

# Generate JIRA bug tickets from detected errors
pytest tests/ai_generated/test_*_navigation.py -v --generate-error-reports
```

---

## Usage

### Run Tests Normally

```bash
pytest tests/ai_generated/test_*_navigation.py -v
```

Output:
```
test_shopping_dropdown_navigation[chromium] PASSED [ 25%]
test_shopping_dropdown_closes_correctly[chromium] PASSED [ 50%]
test_vehicles_dropdown_navigation[chromium] PASSED [ 75%]
test_vehicles_dropdown_all_categories[chromium] PASSED [100%]

4 passed in 91.53s
```

**Result**: Tests pass, no error reports generated

---

### Generate Error Reports & JIRA Tickets

```bash
pytest tests/ai_generated/test_*_navigation.py -v --generate-error-reports
```

Output:
```
test_shopping_dropdown_navigation[chromium] PASSED [ 25%]
...
4 passed in 91.53s

================================================================================
Generating final reports...
================================================================================
Coverage report: reports/coverage/coverage_20251102_200447.json

================================================================================
Generating error reports for 4 filtered errors...
================================================================================

📊 JSON Report saved: reports/filtered_errors/error_report_20251102_200447.json
🎫 JIRA Ticket created: reports/filtered_errors/jira_tickets/JIRA_dealer_lookup_20251102_200447.txt
🎫 JIRA Ticket created: reports/filtered_errors/jira_tickets/JIRA_js_undefined_20251102_200447.txt
📄 Summary Report: reports/filtered_errors/SUMMARY_20251102_200447.txt

✅ Error reports generated successfully!
   JSON Report: reports/filtered_errors/error_report_20251102_200447.json
   Summary: reports/filtered_errors/SUMMARY_20251102_200447.txt
   JIRA Tickets: 2 created
```

**Result**: Tests pass + JIRA bug tickets generated

---

## View Generated Reports

### Quick View

```bash
# View summary
cat reports/filtered_errors/SUMMARY_*.txt | tail -50

# List JIRA tickets
ls reports/filtered_errors/jira_tickets/

# View a specific ticket
cat reports/filtered_errors/jira_tickets/JIRA_dealer_lookup_*.txt
```

### JSON Report

```bash
# View JSON structure
cat reports/filtered_errors/error_report_*.json | python -m json.tool | less
```

---

## Create JIRA Bugs

### Step 1: Open JIRA Ticket

```bash
cat reports/filtered_errors/jira_tickets/JIRA_dealer_lookup_20251102_200447.txt
```

### Step 2: Copy Content

Select and copy the entire ticket content (Cmd+A, Cmd+C)

### Step 3: Create JIRA Issue

1. Go to your JIRA project
2. Click **"Create Issue"**
3. Select **"Bug"** type
4. **Paste** the content into the description field
5. JIRA will auto-format the markup
6. Adjust priority/assignee
7. Click **"Create"**

### Step 4: Repeat for Other Errors

Create separate JIRA tickets for each error category:
- Dealer Lookup errors
- JavaScript undefined errors
- Video playback errors (if present)
- Network 503 errors (if present)

---

## What Gets Reported

### Errors Captured

The system automatically detects and categorizes:

| Category | Example Error | Priority |
|----------|---------------|----------|
| **dealer_lookup** | Unable to retrieve dealer 12166 | Medium |
| **js_undefined** | Cannot read properties of undefined | Medium |
| **video_playback** | play() interrupted by pause() | Low-Medium |
| **network_503** | HTTP 503 from ad pixels | Low |
| **image_403** | Image CDN 403 Forbidden | High |

### Report Contents

Each JIRA ticket includes:

✅ **Exact Steps to Reproduce**
```
# Open Chrome Browser with DevTools (F12)
# Navigate to Console tab
# Navigate to: https://www.toyota.com/rav4/
# Observe JavaScript errors
```

✅ **Error Details** - Full error messages, timestamps, URLs

✅ **Impact Assessment** - Severity, user impact, frequency

✅ **Suggested Fixes** - Code examples showing how to fix

✅ **Test Evidence** - When detected, which test, which page

---

## Example: Real Test Run

### Command:
```bash
pytest tests/ai_generated/test_vehicles_navigation.py::test_vehicles_dropdown_navigation -v --generate-error-reports
```

### Errors Detected:
- 1 dealer lookup error (Error code: 12166)
- 3 JavaScript undefined errors (RAV4 page)

### Reports Generated:
```
reports/filtered_errors/
├── error_report_20251102_200447.json          # Detailed data
├── SUMMARY_20251102_200447.txt                # Human summary
└── jira_tickets/
    ├── JIRA_dealer_lookup_20251102_200447.txt  # Ready for JIRA
    └── JIRA_js_undefined_20251102_200447.txt   # Ready for JIRA
```

### JSON Report:
```json
{
  "summary": {
    "total_errors": 4,
    "categories": {
      "dealer_lookup": 1,
      "js_undefined": 3
    }
  }
}
```

---

## When to Use

### Use `--generate-error-reports` When:

✅ **Weekly bug tracking** - Generate reports once a week to track trends

✅ **Before reporting to Toyota** - Create professional bug tickets

✅ **Debugging new issues** - Get detailed error information

✅ **Trend analysis** - Compare error counts over time

### Don't Use the Flag When:

❌ **Normal development** - Speeds up test runs

❌ **CI/CD pipelines** - Unless you want to archive error data

❌ **Quick smoke tests** - Not needed for fast validation

---

## Weekly Workflow Example

```bash
# Monday: Run tests to validate functionality
pytest tests/ai_generated/ -v

# Friday: Generate weekly error report
pytest tests/ai_generated/ -v --generate-error-reports

# Review reports
cat reports/filtered_errors/SUMMARY_*.txt

# Create JIRA tickets for new errors
cat reports/filtered_errors/jira_tickets/JIRA_*.txt
```

---

## Comparing Reports Over Time

```bash
# Week 1
pytest tests/ai_generated/ -v --generate-error-reports
# → error_report_20251102_*.json

# Week 2
pytest tests/ai_generated/ -v --generate-error-reports
# → error_report_20251109_*.json

# Compare error counts
echo "Week 1:"
jq '.summary.categories' reports/filtered_errors/error_report_20251102_*.json

echo "Week 2:"
jq '.summary.categories' reports/filtered_errors/error_report_20251109_*.json
```

---

## Pytest Help

```bash
# View all pytest options
pytest --help | grep "generate-error"
```

Output:
```
  --generate-error-reports
                        Generate JIRA-formatted error reports for filtered
                        website bugs
```

---

## Full Documentation

For complete details, see:
- **[ERROR_REPORTING_GUIDE.md](ERROR_REPORTING_GUIDE.md)** - Complete guide
- **[reports/filtered_errors/README.md](reports/filtered_errors/README.md)** - Report directory reference

---

## Summary

| Command | Result |
|---------|--------|
| `pytest tests/ -v` | Tests run, no reports |
| `pytest tests/ -v --generate-error-reports` | Tests run + JIRA tickets generated |
| `cat reports/filtered_errors/SUMMARY_*.txt` | View latest summary |
| `ls reports/filtered_errors/jira_tickets/` | List all tickets |
| `cat reports/filtered_errors/jira_tickets/JIRA_*.txt` | View ticket for JIRA |

**That's it!** 🎉

Run tests with `--generate-error-reports` whenever you want JIRA bug tickets for website errors.
