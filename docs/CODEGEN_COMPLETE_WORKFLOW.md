# Complete Codegen Workflow: Record, Name, and Add Assertions

## The Problem with Codegen

**Codegen records actions but NOT assertions:**

```python
# What Codegen DOES record ✅
page.goto("https://www.toyota.com/")
page.get_by_role("button", name="Vehicles").click()
page.get_by_role("link", name="Corolla").click()

# What Codegen DOES NOT record ❌
expect(page).to_have_url("https://www.toyota.com/")
expect(page.get_by_role("heading", name="Corolla")).to_be_visible()
```

## Complete 3-Step Workflow

### Step 1: Record Test with Custom Name

**Using the Helper Script:**
```bash
./scripts/record_test.sh
```

**Manual Command:**
```bash
# Record a specific test
playwright codegen https://www.toyota.com \
  --target python-pytest \
  -o tests/recorded/test_checkout.py
```

**Examples:**
```bash
# Record GNAV test
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_gnav.py

# Record dealer search
playwright codegen https://www.toyota.com/dealers \
  -o tests/recorded/test_dealer_search.py

# Record vehicle details
playwright codegen https://www.toyota.com/vehicles \
  -o tests/recorded/test_vehicle_details.py

# Record checkout flow
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_checkout_flow.py
```

**What You'll See:**
1. Browser opens showing the URL
2. Inspector window shows generated code in real-time
3. Every click/type/navigation is recorded
4. Close browser when done → Test saved!

### Step 2: Add Assertions with AI

**Option A: Use the AI Script (Recommended)**
```bash
python scripts/add_assertions.py tests/recorded/test_gnav.py
```

**What Happens:**
- 🔍 Analyzes your recorded test
- 🤖 Uses AI to generate appropriate assertions
- 📝 Saves enhanced version: `test_gnav_with_assertions.py`
- ✅ Keeps all original actions intact

**Option B: Add Assertions Manually**
```python
# Original codegen output
def test_gnav(page: Page):
    page.goto("https://www.toyota.com/")
    page.get_by_role("button", name="Vehicles").click()

# Add assertions manually
def test_gnav(page: Page):
    page.goto("https://www.toyota.com/")
    expect(page).to_have_url("https://www.toyota.com/")  # ← Added

    page.get_by_role("button", name="Vehicles").click()
    expect(page.get_by_role("button", name="Vehicles")).to_be_visible()  # ← Added
```

### Step 3: Run and Watch Your Test

**Run in visible browser:**
```bash
pytest tests/recorded/test_gnav_with_assertions.py --headed
```

**Run in slow motion (see every action):**
```bash
pytest tests/recorded/test_gnav_with_assertions.py --headed --slowmo 1000
```

**Debug step-by-step:**
```bash
PWDEBUG=1 pytest tests/recorded/test_gnav_with_assertions.py -s
```

## Re-Recording Tests

### Don't Like Your Recording? Re-record!

**Option 1: Overwrite Existing Test**
```bash
# Just record again with same filename
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_gnav.py

# It will ask if you want to overwrite - say yes
```

**Option 2: Keep Multiple Versions**
```bash
# Record v1
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_gnav_v1.py

# Record v2 with improvements
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_gnav_v2.py

# Compare and keep the best one
```

**Option 3: Interactive Script (Asks Before Overwriting)**
```bash
./scripts/record_test.sh
# Enter test name: gnav
# If exists, asks: "Overwrite? (y/n)"
```

## Complete Examples

### Example 1: Record GNAV Test with Assertions

```bash
# Step 1: Record test
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_gnav.py

# (Perform actions in browser, then close)

# Step 2: Add assertions
python scripts/add_assertions.py tests/recorded/test_gnav.py

# Step 3: Run and watch
pytest tests/recorded/test_gnav_with_assertions.py --headed --slowmo 500

# Step 4: If good, replace original
mv tests/recorded/test_gnav_with_assertions.py tests/recorded/test_gnav.py
```

### Example 2: Record Dealer Search Flow

```bash
# Record
./scripts/record_test.sh
# Test name: dealer_search
# URL: https://www.toyota.com/dealers

# (In browser: enter zip, search, click dealer)

# Add assertions
python scripts/add_assertions.py tests/recorded/test_dealer_search.py

# Watch it run
pytest tests/recorded/test_dealer_search_with_assertions.py --headed --slowmo 1000
```

### Example 3: Record and Re-record Until Perfect

```bash
# First attempt
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_checkout_v1.py

# Not happy? Try again
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_checkout_v2.py

# Better? Try one more time
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_checkout_v3.py

# Perfect! Add assertions
python scripts/add_assertions.py tests/recorded/test_checkout_v3.py

# Run it
pytest tests/recorded/test_checkout_v3_with_assertions.py --headed
```

## Naming Best Practices

### Good Test Names

✅ **Descriptive and Clear:**
```bash
test_gnav_vehicle_categories.py      # What it tests
test_dealer_search_by_zip.py         # Specific functionality
test_vehicle_details_corolla.py      # Feature + vehicle
test_checkout_complete_flow.py       # User journey
test_form_quote_request.py           # Form interaction
```

❌ **Bad Test Names:**
```bash
test_1.py                            # Not descriptive
test_homepage_recorded.py            # Generic
test_example.py                      # Too vague
test_foo.py                          # Meaningless
```

### Naming Convention

**Pattern:** `test_<feature>_<action>.py`

```bash
test_gnav_vehicles.py               # GNAV → Vehicles menu
test_search_dealer.py               # Search → Dealer
test_form_contact.py                # Form → Contact
test_nav_footer.py                  # Navigation → Footer
test_filter_vehicles.py             # Filter → Vehicles
test_compare_models.py              # Compare → Models
```

## What AI Adds to Your Tests

### Before (Codegen Only):
```python
def test_example(page: Page) -> None:
    page.goto("https://www.toyota.com/")
    page.get_by_role("button", name="Vehicles").click()
    page.get_by_role("link", name="Corolla").click()
```

### After (AI-Enhanced):
```python
import re
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.critical_path
def test_gnav_vehicle_selection(page: Page) -> None:
    """
    Test GNAV vehicle navigation and selection.
    Verifies all vehicle menu categories are accessible.
    """
    # Navigate to homepage
    page.goto("https://www.toyota.com/")
    expect(page).to_have_url("https://www.toyota.com/")
    expect(page).to_have_title(re.compile("Toyota"))

    # Open Vehicles menu
    vehicles_btn = page.get_by_role("button", name="Vehicles")
    expect(vehicles_btn).to_be_visible()
    vehicles_btn.click()

    # Verify menu opened (check for category)
    expect(page.get_by_role("button", name="Crossovers & SUVs")).to_be_visible()

    # Select Corolla
    corolla_link = page.get_by_role("link", name="Corolla")
    expect(corolla_link).to_be_visible()
    corolla_link.click()

    # Verify navigation to Corolla page
    expect(page).to_have_url(re.compile(".*corolla.*"))
    expect(page.get_by_role("heading", name="Corolla")).to_be_visible()
```

**AI Adds:**
- ✅ Proper function name and docstring
- ✅ pytest markers (@pytest.mark.smoke)
- ✅ URL assertions
- ✅ Visibility checks
- ✅ Page title verification
- ✅ Navigation confirmation
- ✅ Comments explaining each step
- ✅ Proper imports

## Quick Reference

### Record New Test
```bash
./scripts/record_test.sh
```

### Re-record Existing Test
```bash
playwright codegen https://www.toyota.com \
  -o tests/recorded/test_gnav.py
# Choose 'y' to overwrite
```

### Add Assertions
```bash
python scripts/add_assertions.py tests/recorded/test_gnav.py
```

### Watch Test Run
```bash
pytest tests/recorded/test_gnav.py --headed --slowmo 1000
```

### All in One Command
```bash
# Record, enhance, and run
playwright codegen https://www.toyota.com -o tests/recorded/test_new.py && \
python scripts/add_assertions.py tests/recorded/test_new.py && \
pytest tests/recorded/test_new_with_assertions.py --headed --slowmo 500
```

## Troubleshooting

**Q: Codegen window closed but test not saved**
- A: The test is saved when you close the browser, not when you close inspector

**Q: Want to name test during recording**
- A: Use `-o` flag: `playwright codegen URL -o tests/recorded/test_NAME.py`

**Q: Recorded test has too many actions**
- A: Re-record with more focused actions, or edit the file to remove unnecessary steps

**Q: AI assertion script fails**
- A: Check your API keys in .env, or add assertions manually

**Q: Don't like the assertions AI added**
- A: Edit the `_with_assertions.py` file manually to adjust

**Q: Want to see what changed**
- A: Use `diff tests/recorded/test_gnav.py tests/recorded/test_gnav_with_assertions.py`
