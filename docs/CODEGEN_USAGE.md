# Using Playwright Codegen for Test Generation

## What is Codegen?

Playwright's code generator (`codegen`) opens a browser and records your interactions, generating test code automatically with **real, working selectors**.

## How to Use It

### 1. Basic Usage - Record Homepage Test

```bash
source venv/bin/activate
playwright codegen https://www.toyota.com \
  --target python-pytest \
  -o tests/recorded/test_homepage_recorded.py
```

**What happens:**
- Browser opens showing toyota.com
- A code generator window shows the generated code in real-time
- As you click/type/navigate, code is generated automatically
- When done, close browser and code is saved

### 2. Record Dealers Search Flow

```bash
playwright codegen https://www.toyota.com/dealers \
  --target python-pytest \
  -o tests/recorded/test_dealers_recorded.py
```

**Example actions to record:**
1. Wait for page to load
2. Dismiss any modals
3. Click zip input
4. Type "94016"
5. Press Enter or click Search
6. Verify results appear

### 3. Record Vehicle Browse Flow

```bash
playwright codegen https://www.toyota.com/vehicles \
  --target python-pytest \
  -o tests/recorded/test_vehicles_recorded.py
```

### 4. Advanced Options

```bash
# Save and load user state (cookies, auth)
playwright codegen --save-storage=auth.json https://www.toyota.com

# Use saved state for authenticated tests
playwright codegen --load-storage=auth.json https://www.toyota.com/account

# Emulate mobile device
playwright codegen --device="iPhone 12" https://www.toyota.com

# Generate with custom test-id attribute
playwright codegen --test-id-attribute="data-testid" https://www.toyota.com
```

## Generated Code Example

When you interact with the dealers page, codegen generates:

```python
import pytest
from playwright.sync_api import Page, expect

def test_dealers_search(page: Page):
    page.goto("https://www.toyota.com/dealers/")

    # Real selector extracted from DOM
    page.get_by_placeholder("Example: New York, NY").click()
    page.get_by_placeholder("Example: New York, NY").fill("94016")
    page.get_by_placeholder("Example: New York, NY").press("Enter")

    # Generated assertion
    expect(page).to_have_url(re.compile(".*dealers.*"))
```

## Benefits Over AI Generation

| AI Generation | Codegen |
|---------------|---------|
| ❌ Guesses selectors | ✅ Uses actual working selectors |
| ❌ Assumes navigation paths | ✅ Records real navigation |
| ❌ Doesn't know about modals | ✅ Captures modal interactions |
| ❌ May use deprecated syntax | ✅ Uses Playwright best practices |

## Combining Codegen with AI

**Best workflow:**
1. **Record with codegen** → Get working test skeleton
2. **Extract selectors** → Save to selector database
3. **Use AI to enhance** → Add assertions, error handling, parameterization
4. **Self-healing** → Auto-fix when selectors break

## Try It Now

```bash
# Create directory for recorded tests
mkdir -p tests/recorded

# Record your first test (opens browser)
source venv/bin/activate
playwright codegen https://www.toyota.com --target python-pytest
```

Interact with the site, then close the browser. The generated code appears in the terminal!
