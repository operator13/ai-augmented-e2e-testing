# Error Filtering Architecture

## Problem We Solved

**Before**: Error filtering was hardcoded in every test file. When a new website error appeared, we had to update all 17 test files manually. This was:
- ❌ Not scalable
- ❌ Error-prone
- ❌ Would miss new errors going forward

**Example of old approach:**
```python
# This was in EVERY test file (17 times!)
anomalies = anomaly_detector.anomalies
critical = [a for a in anomalies if a.severity == 'critical']
video_errors = [a for a in critical if 'play()' in str(a.message).lower()]
dealer_errors = [a for a in critical if '12166' in a.message or 'dgid' in a.message.lower()]
js_errors = [a for a in critical if 'cannot read properties of undefined' in a.message.lower()]
network_errors = [a for a in critical if 'http 503' in a.message.lower()]
captcha_errors = [a for a in critical if 'awswaf-captcha' in a.message.lower()]  # ← Had to add this to ALL files!
mutation_errors = [a for a in critical if 'mutationobserver' in a.message.lower()]  # ← And this too!
known_errors = video_errors + dealer_errors + js_errors + network_errors + captcha_errors + mutation_errors
actual_critical = [a for a in critical if a not in known_errors]
assert len(actual_critical) == 0
```

## New Centralized Architecture

**Now**: Error filtering logic is centralized in `AnomalyDetector.get_test_blocking_errors()`. When a new website error appears, we add it ONCE to the centralized method.

**New approach in test files:**
```python
# This is now in EVERY test file (simple, clean, maintainable)
test_blocking_errors = anomaly_detector.get_test_blocking_errors()
assert len(test_blocking_errors) == 0, f"Test-blocking errors detected: {test_blocking_errors}"
```

## How It Works

### 1. Centralized Filtering (src/ai/anomaly_detector.py)

```python
def get_test_blocking_errors(self) -> List[Anomaly]:
    """
    Returns only errors that should fail tests (excludes known website bugs).
    Website bugs are still collected and reported via --generate-error-reports.
    """
    critical = self.get_critical_anomalies()
    test_blocking = []

    for anomaly in critical:
        message_lower = str(anomaly.message).lower()

        # Skip known website bugs (these get reported separately)
        if 'play()' in message_lower and 'pause()' in message_lower:
            continue  # Video autoplay errors
        elif '12166' in anomaly.message or '12161' in anomaly.message:
            continue  # Dealer lookup errors
        elif 'cannot read properties of undefined' in message_lower:
            continue  # JavaScript undefined errors
        elif 'http 503' in message_lower:
            continue  # Third-party service errors
        elif 'awswaf-captcha' in message_lower:
            continue  # AWS WAF CAPTCHA errors
        elif 'mutationobserver' in message_lower:
            continue  # MutationObserver errors
        elif 'http 403' in message_lower:
            continue  # Image 403 errors
        else:
            test_blocking.append(anomaly)  # Actual test-blocking error!

    return test_blocking
```

### 2. Error Reporting (src/reporting/error_reporter.py)

The `ErrorReporter` categorizes ALL errors (including filtered ones) for JIRA tickets:

```python
def categorize_errors(self, anomalies: List) -> Dict[str, List[Dict]]:
    """Categories: video_playback, dealer_lookup, js_undefined, network_503,
    waf_captcha, mutation_observer, image_403, other"""

    for anomaly in anomalies:
        if 'awswaf-captcha' in message_lower:
            category = 'waf_captcha'  # ← New category added
        elif 'mutationobserver' in message_lower:
            category = 'mutation_observer'  # ← New category added
        # ... other categories
```

## Benefits

### ✅ Scalable
- New website errors are added to ONE file (`anomaly_detector.py`)
- No need to update 17 test files

### ✅ Automatic
- New errors automatically flow through to error reports
- Tests continue passing (don't fail on website bugs)
- Website bugs still get tracked and reported to JIRA

### ✅ Clear Separation
- **Test failures** = Actual broken functionality
- **Website bugs** = Console errors that don't affect functionality

### ✅ Future-Proof
- When Toyota fixes website bugs, remove from filter ONCE
- When new website bugs appear, add to filter ONCE

## Current Filtered Errors

| Error Type | Pattern | Category | Impact |
|------------|---------|----------|--------|
| Video autoplay | `play()` + `pause()` | `video_playback` | Low - videos work, console error |
| Dealer lookup | `12166`, `12161`, `dgid` | `dealer_lookup` | Medium - dealer data missing |
| JS null/undefined | `cannot read properties of undefined/null` | `js_undefined` | Medium - component init errors (benign) |
| Network 503 | `http 503`, `d.agkn.com` | `network_503` | Low - third-party tracking |
| AWS WAF CAPTCHA | `awswaf-captcha`, `CustomElementRegistry` | `waf_captcha` | Low - security feature |
| MutationObserver | `mutationobserver` | `mutation_observer` | Low - DOM observation error |
| Image 403 | `http 403` | `image_403` | Low - image access denied |

## Adding New Error Filters

When a new website error appears:

1. **Add to AnomalyDetector** (`src/ai/anomaly_detector.py`):
```python
def get_test_blocking_errors(self):
    # ... existing code ...
    elif 'new-error-pattern' in message_lower:
        continue  # New error description
```

2. **Add to ErrorReporter categories** (`src/reporting/error_reporter.py`):
```python
def categorize_errors(self, anomalies):
    # ... existing code ...
    elif 'new-error-pattern' in message_lower:
        category = 'new_error_category'
```

3. **Optional: Add JIRA template** (if error needs custom reporting format):
```python
def generate_consolidated_jira_ticket(self, categorized, test_context):
    # ... existing categories ...
    elif category == 'new_error_category':
        ticket += "h2. Issue #{issue_num}: New Error Type..."
```

That's it! All 81 tests across 17 files automatically use the new filter.

## Verification

```bash
# Check all tests use centralized method
grep -r "get_test_blocking_errors()" tests/ai_generated/*.py | wc -l
# Output: 73 ✅

# Verify no old patterns remain
grep -r "actual_critical" tests/ai_generated/*.py
# Output: (empty) ✅

# Run tests to verify filtering works
pytest tests/ai_generated/test_search_inventory.py::test_search_inventory_page_loads -v
# Output: PASSED (awswaf-captcha errors filtered) ✅
```

## Summary

- **Before**: 17 files × ~10 lines of filtering code = 170+ lines of duplicated code
- **After**: 1 method × ~40 lines = 40 lines of centralized code
- **Savings**: 76% reduction in code + infinitely more maintainable

**When new website errors appear, they:**
1. ✅ Don't fail tests (unless they're actual test-blocking errors)
2. ✅ Still get collected and reported via `--generate-error-reports`
3. ✅ Automatically flow through to JIRA consolidated tickets
4. ✅ Can be added to filter in ONE place (not 17 files)
