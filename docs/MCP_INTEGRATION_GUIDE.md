# Playwright MCP Integration Guide

## Complete Integration with AI-Augmented E2E Testing Framework

This guide explains how to leverage Claude Code's Playwright MCP (Model Context Protocol) tools with your AI-augmented testing framework for toyota.com.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Integration Architecture](#integration-architecture)
4. [Core Features](#core-features)
5. [Usage Workflows](#usage-workflows)
6. [API Reference](#api-reference)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The MCP integration brings **interactive browser control** to your AI-powered testing framework. This creates a powerful workflow:

```
MCP Interactive Recording → AI Enhancement → Self-Healing Tests
```

### Key Benefits

- **Record Once, Enhance Forever**: Record user flows interactively, then AI adds assertions
- **Live Selector Discovery**: Find and validate selectors in real-time
- **Instant Debugging**: Investigate failures with live browser control
- **Hybrid Approach**: Combine manual exploration with automated test generation

---

## Prerequisites

### 1. Claude Code with MCP Support

Ensure you're using Claude Code with Playwright MCP server enabled:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "node",
      "args": ["/path/to/playwright-mcp/index.js"]
    }
  }
}
```

### 2. Framework Setup

Your framework should already have:
- ✅ Playwright installed
- ✅ AI test generator (`src/ai/test_generator.py`)
- ✅ Self-healing selectors (`src/ai/self_healing.py`)
- ✅ Visual AI testing (`src/ai/visual_ai.py`)

### 3. MCP Integration Modules

The following modules have been added:
- `src/mcp/selector_discovery.py` - Live selector discovery
- `src/mcp/codegen_workflow.py` - Recording and test generation
- `src/mcp/debug_helper.py` - Automated debugging
- Enhanced `src/ai/test_generator.py` - MCP integration methods

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code (You)                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Playwright MCP Tools                         │   │
│  │  • Navigate  • Click  • Fill  • Screenshot           │   │
│  │  • Evaluate JS  • Console Logs  • Get HTML           │   │
│  └────────────────────-┬────────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Integration Layer                          │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │   Selector     │  │   Codegen    │  │     Debug      │   │
│  │  Discovery     │  │   Workflow   │  │     Helper     │   │
│  └────────────────┘  └──────────────┘  └────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           AI-Augmented Testing Framework                    │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │   AI Test      │  │ Self-Healing │  │   Visual AI    │   │
│  │  Generator     │  │   Selectors  │  │    Testing     │   │
│  └────────────────┘  └──────────────┘  └────────────────┘   │
│                                                             │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │   Anomaly      │  │   Coverage   │  │  Page Objects  │   │
│  │  Detection     │  │   Analyzer   │  │                │   │
│  └────────────────┘  └──────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
                  toyota.com Application
```

---

## Core Features

### 1. Interactive Selector Discovery

Discover selectors on live pages and automatically update your selector database.

**Module**: `src/mcp/selector_discovery.py`

**Workflow**:
1. Navigate to a page via MCP
2. Run JavaScript selector discovery
3. Parse and categorize results
4. Merge with existing `selectors.json`
5. Generate discovery report

**Example**:
```python
from src.mcp.selector_discovery import MCPSelectorDiscovery

# Initialize
discovery = MCPSelectorDiscovery()

# Generate discovery script
script = discovery.generate_mcp_discovery_script()

# In Claude Code:
# mcp__playwright__playwright_navigate(url="https://www.toyota.com")
# results = mcp__playwright__playwright_evaluate(script=script)

# Parse results
selectors = discovery.parse_mcp_discovery_results(results)
categorized = discovery.categorize_selectors(selectors)
merged_db = discovery.merge_with_database(categorized)
discovery.save_selector_database(merged_db)
```

### 2. Codegen Workflow

Record user flows and convert them to AI-enhanced pytest tests.

**Module**: `src/mcp/codegen_workflow.py`

**Workflow**:
1. Start recording session
2. Use MCP to interact with toyota.com
3. Actions are recorded automatically
4. End session to generate test
5. AI enhances with assertions and validations

**Example**:
```python
from src.mcp.codegen_workflow import MCPCodegenWorkflow

workflow = MCPCodegenWorkflow()

# Start session
session = workflow.start_recording_session(
    session_name="vehicle_navigation",
    test_name_prefix="test_navigate_vehicles"
)

# In Claude Code, use MCP to record:
# mcp__playwright__start_codegen_session(options={
#     "outputPath": session.output_path,
#     "testNamePrefix": session.test_name_prefix,
#     "includeComments": True
# })

# Navigate and interact (MCP records automatically)
# mcp__playwright__playwright_navigate(url="https://www.toyota.com")
# mcp__playwright__playwright_click(selector=".vehicle-menu")

# End and get generated test
# result = mcp__playwright__end_codegen_session(sessionId=mcp_session_id)

# Enhance with AI
enhanced = workflow.enhance_with_ai(
    generated_test_path=result.generated_path,
    enhancement_options={
        'add_assertions': True,
        'add_visual_checks': True,
        'use_self_healing': True
    }
)
```

### 3. AI Test Generator with MCP

Enhanced test generator that works with MCP recordings.

**Module**: `src/ai/test_generator.py` (enhanced)

**New Methods**:
- `enhance_mcp_recording()` - Add AI assertions to recorded tests
- `generate_from_mcp_actions()` - Generate tests from action list
- `suggest_assertions_for_recording()` - AI-suggested validations
- `merge_mcp_with_page_object()` - Convert to page object pattern

**Example**:
```python
from src.ai.test_generator import AITestGenerator

generator = AITestGenerator(use_claude=True)

# Enhance recorded test
enhanced_code = generator.enhance_mcp_recording(
    recorded_test_path="tests/recorded/test_vehicles.py",
    flow_description="Navigate to vehicles page and filter by type",
    enhancement_level="full"  # minimal, moderate, or full
)

# Save enhanced test
generator.save_generated_test(
    enhanced_code,
    "test_vehicles_enhanced.py",
    Path("tests/ai_generated")
)
```

### 4. Debug Helper

Automated debugging using MCP tools when tests fail.

**Module**: `src/mcp/debug_helper.py`

**Workflow**:
1. Test fails with selector error
2. Start debug session
3. Use MCP to investigate failure
4. Capture screenshots and logs
5. Suggest alternative selectors
6. Auto-heal and update selector DB

**Example**:
```python
from src.mcp.debug_helper import MCPDebugHelper

helper = MCPDebugHelper()

# Test failed
session = helper.start_debug_session(
    test_name="test_vehicle_selection",
    failure_type="selector_not_found",
    failure_message="Locator('.vehicle-card') not found"
)

# Investigate (use MCP to navigate to failure point)
investigation = helper.investigate_selector_failure(
    session.session_id,
    failed_selector=".vehicle-card",
    page_url="https://www.toyota.com/vehicles"
)

# Capture artifacts
# screenshots = mcp__playwright__playwright_screenshot()
# html = mcp__playwright__playwright_get_visible_html()
# logs = mcp__playwright__playwright_console_logs()

# Analyze and resolve
helper.resolve_session(
    session.session_id,
    resolution="Updated to data attribute selector",
    working_selector="[data-vehicle-type='sedan']"
)
```

---

## Usage Workflows

### Workflow 1: Discover and Test New Page

**Scenario**: You need to test a new Toyota vehicle page.

**Steps**:

1. **Discover Selectors**
   ```python
   # In Claude Code
   mcp__playwright__playwright_navigate(url="https://www.toyota.com/camry")

   # Run selector discovery
   from src.mcp.selector_discovery import MCPSelectorDiscovery
   discovery = MCPSelectorDiscovery()
   script = discovery.generate_mcp_discovery_script()

   # Execute via MCP
   results = mcp__playwright__playwright_evaluate(script=script)

   # Save to database
   selectors = discovery.parse_mcp_discovery_results(results)
   categorized = discovery.categorize_selectors(selectors)
   discovery.merge_with_database(categorized)
   ```

2. **Record User Flow**
   ```python
   # Start codegen session
   workflow = MCPCodegenWorkflow()
   session = workflow.start_recording_session("camry_exploration")

   # Use MCP to interact and record
   # (Navigate, click features, view gallery, etc.)
   ```

3. **Enhance with AI**
   ```python
   generator = AITestGenerator()
   enhanced = generator.enhance_mcp_recording(
       recorded_test_path=session.generated_test_path,
       flow_description="Explore Camry features and gallery",
       enhancement_level="full"
   )
   ```

4. **Run and Validate**
   ```bash
   pytest tests/ai_generated/test_camry_exploration.py -v
   ```

### Workflow 2: Debug Failing Test

**Scenario**: A test is failing with "Element not found"

**Steps**:

1. **Start Debug Session**
   ```python
   helper = MCPDebugHelper()
   session = helper.start_debug_session(
       test_name="test_dealer_search",
       failure_type="selector_not_found",
       failure_message="Locator('#zip-input') not found"
   )
   ```

2. **Navigate to Failure Point (MCP)**
   ```python
   # Use MCP to go to the exact page
   mcp__playwright__playwright_navigate(
       url="https://www.toyota.com/dealers"
   )
   ```

3. **Investigate Selector**
   ```python
   # Run investigation script via MCP
   investigation = helper.investigate_selector_failure(
       session.session_id,
       failed_selector="#zip-input",
       page_url="https://www.toyota.com/dealers"
   )

   # MCP evaluates similarity search
   script = helper._generate_find_similar_script("#zip-input")
   similar = mcp__playwright__playwright_evaluate(script=script)
   ```

4. **Capture Debug Info**
   ```python
   # Screenshot
   mcp__playwright__playwright_screenshot(
       name=f"{session.session_id}_failure",
       savePng=True
   )

   # Console logs
   logs = mcp__playwright__playwright_console_logs(type="all")

   # HTML for inspection
   html = mcp__playwright__playwright_get_visible_html()
   ```

5. **Fix and Update**
   ```python
   # Use suggested selector
   working_selector = "[data-dealer-search-input]"

   # Update selector database
   helper.resolve_session(
       session.session_id,
       resolution="Updated to data attribute",
       working_selector=working_selector
   )
   ```

### Workflow 3: Generate Test Suite from Recordings

**Scenario**: Create comprehensive tests for multiple user flows

**Steps**:

1. **Record Multiple Sessions**
   ```python
   sessions = []

   # Record session 1: Homepage navigation
   # Record session 2: Vehicle browsing
   # Record session 3: Build & Price flow
   # Record session 4: Dealer search

   # Each session captures actions
   ```

2. **Generate Complete Suite**
   ```python
   generator = AITestGenerator()

   test_suite = generator.create_test_suite_from_mcp_sessions(
       sessions=[
           {
               'test_name': 'test_homepage_navigation',
               'description': 'Navigate main menu and verify sections',
               'actions': homepage_actions
           },
           {
               'test_name': 'test_vehicle_browsing',
               'description': 'Browse vehicles and filter by type',
               'actions': vehicle_actions
           },
           # ... more sessions
       ],
       suite_name="comprehensive_toyota_tests"
   )

   # Save all tests
   for test_name, test_code in test_suite.items():
       generator.save_generated_test(test_code, test_name)
   ```

3. **Run Complete Suite**
   ```bash
   pytest tests/ai_generated/ -v --html=reports/suite_report.html
   ```

---

## API Reference

### MCPSelectorDiscovery

#### `generate_mcp_discovery_script() -> str`
Generates JavaScript to discover selectors via MCP evaluate().

**Returns**: JavaScript code to execute in browser

#### `parse_mcp_discovery_results(mcp_results: Dict) -> List[DiscoveredSelector]`
Parses results from MCP selector discovery.

**Args**:
- `mcp_results`: Results from MCP evaluate()

**Returns**: List of discovered selectors with metadata

#### `categorize_selectors(selectors: List) -> Dict`
Categorizes selectors by type (navigation, buttons, links, etc.)

#### `merge_with_database(new_selectors: Dict) -> Dict`
Merges discoveries with existing selector database.

**Returns**: Updated selector database

---

### MCPCodegenWorkflow

#### `start_recording_session(session_name: str) -> CodegenSession`
Starts a new MCP codegen recording session.

**Args**:
- `session_name`: Unique name for the session
- `test_name_prefix`: Prefix for generated test

**Returns**: CodegenSession object

#### `enhance_with_ai(generated_test_path: str, enhancement_options: Dict) -> str`
Enhances MCP-generated test with AI features.

**Args**:
- `generated_test_path`: Path to MCP-generated test
- `enhancement_options`: Dict with enhancement settings

**Returns**: Path to enhanced test

---

### MCPDebugHelper

#### `start_debug_session(test_name: str, failure_type: str, failure_message: str) -> DebugSession`
Starts automated debugging session.

**Returns**: DebugSession object

#### `investigate_selector_failure(session_id: str, failed_selector: str, page_url: str) -> Dict`
Investigates why a selector failed.

**Returns**: Investigation results with suggestions

#### `save_debug_report(session_id: str) -> str`
Saves complete debug report with all artifacts.

**Returns**: Path to saved report

---

### AITestGenerator (Enhanced)

#### `enhance_mcp_recording(recorded_test_path: str, flow_description: str, enhancement_level: str) -> str`
Enhances MCP-recorded test with AI-generated assertions.

**Args**:
- `recorded_test_path`: Path to recorded test
- `flow_description`: What the test does
- `enhancement_level`: "minimal" | "moderate" | "full"

**Returns**: Enhanced test code

#### `generate_from_mcp_actions(actions: List[Dict], test_name: str, flow_description: str) -> str`
Generates pytest from list of recorded actions.

**Returns**: Generated test code

#### `suggest_assertions_for_recording(recorded_actions: List[Dict], page_url: str) -> List[Dict]`
AI suggests assertions for recorded actions.

**Returns**: List of suggested assertions with placement info

---

## Examples

### Example 1: Complete Flow - Discover, Record, Enhance

```python
from src.mcp.selector_discovery import MCPSelectorDiscovery
from src.mcp.codegen_workflow import MCPCodegenWorkflow
from src.ai.test_generator import AITestGenerator

# 1. Discover selectors
discovery = MCPSelectorDiscovery()

# Navigate via MCP
# mcp__playwright__playwright_navigate(url="https://www.toyota.com/rav4")

# Discover
script = discovery.generate_mcp_discovery_script()
# results = mcp__playwright__playwright_evaluate(script=script)

selectors = discovery.parse_mcp_discovery_results(results)
discovery.merge_with_database(discovery.categorize_selectors(selectors))

# 2. Record user flow
workflow = MCPCodegenWorkflow()
session = workflow.start_recording_session("rav4_features")

# Use MCP to record interactions:
# - Click features tab
# - View 360 gallery
# - Check specifications
# - View available colors

# End recording
# mcp__playwright__end_codegen_session(sessionId=session_id)

# 3. Enhance with AI
generator = AITestGenerator()
enhanced_code = generator.enhance_mcp_recording(
    recorded_test_path=session.generated_test_path,
    flow_description="Explore RAV4 features, gallery, and specifications",
    enhancement_level="full"
)

# 4. Save and run
generator.save_generated_test(
    enhanced_code,
    "test_rav4_features_complete.py"
)
```

### Example 2: Debug and Fix Selector

```python
from src.mcp.debug_helper import MCPDebugHelper, MCPFailureAnalyzer

# Test failed
analyzer = MCPFailureAnalyzer()
analysis = analyzer.analyze_failure(
    test_name="test_build_price",
    error_type="TimeoutError",
    error_message="Locator('.color-selector') not found",
    traceback="..."
)

print(analysis['likely_cause'])
print(analysis['suggested_actions'])
print(analysis['mcp_debug_commands'])

# Start debugging
helper = MCPDebugHelper()
session = helper.start_debug_session(
    test_name="test_build_price",
    failure_type="selector_not_found",
    failure_message="Locator('.color-selector') not found"
)

# Navigate to page via MCP
# mcp__playwright__playwright_navigate(url="https://www.toyota.com/configurator")

# Investigate
investigation = helper.investigate_selector_failure(
    session.session_id,
    failed_selector=".color-selector",
    page_url="https://www.toyota.com/configurator"
)

# Capture artifacts
artifacts = helper.capture_debug_artifacts(
    session.session_id,
    page_url="https://www.toyota.com/configurator"
)

# Test suggested selectors via MCP
test_script = helper._generate_selector_test_script([
    "[data-color-select]",
    ".vehicle-color-picker",
    "#color-options"
])

# results = mcp__playwright__playwright_evaluate(script=test_script)

# Resolve with working selector
helper.resolve_session(
    session.session_id,
    resolution="Selector updated to data attribute",
    working_selector="[data-color-select]"
)

# Update self-healing database
from src.ai.self_healing import SelfHealingSelector
healer = SelfHealingSelector()
healer.update_selector_mapping(
    original=".color-selector",
    alternatives=["[data-color-select]", ".vehicle-color-picker"]
)
```

### Example 3: Generate Assertions from Recording

```python
from src.ai.test_generator import AITestGenerator

generator = AITestGenerator()

# Recorded actions from MCP session
recorded_actions = [
    {'type': 'navigate', 'url': 'https://www.toyota.com'},
    {'type': 'click', 'selector': 'button.vehicles-menu'},
    {'type': 'click', 'selector': 'a[href="/rav4"]'},
    {'type': 'click', 'selector': '.features-tab'},
    {'type': 'click', 'selector': '.gallery-360'}
]

# Get AI-suggested assertions
suggestions = generator.suggest_assertions_for_recording(
    recorded_actions=recorded_actions,
    page_url="https://www.toyota.com/rav4"
)

# Output:
# [
#   {
#     "after_action": 0,
#     "assertion_type": "expect_url",
#     "selector": "",
#     "description": "Verify homepage loaded",
#     "code": "expect(page).to_have_url('https://www.toyota.com')"
#   },
#   {
#     "after_action": 1,
#     "assertion_type": "expect_visible",
#     "selector": ".vehicle-dropdown",
#     "description": "Verify vehicles menu opened",
#     "code": "expect(page.locator('.vehicle-dropdown')).to_be_visible()"
#   },
#   ...
# ]

print(json.dumps(suggestions, indent=2))
```

---

## Troubleshooting

### Issue: MCP modules not found

**Error**: `ModuleNotFoundError: No module named 'src.mcp'`

**Solution**:
```bash
# Ensure you're in the project directory
cd /Users/oantazo/Desktop/AI_AugmentedE2E

# Verify MCP modules exist
ls -la src/mcp/

# Should show:
# selector_discovery.py
# codegen_workflow.py
# debug_helper.py
```

### Issue: Selectors not being discovered

**Symptom**: Empty results from selector discovery

**Solution**:
1. Check page loaded completely:
   ```python
   # Wait for network idle
   mcp__playwright__playwright_navigate(
       url="https://www.toyota.com",
       waitUntil="networkidle"
   )
   ```

2. Verify JavaScript execution:
   ```python
   # Test simple evaluation first
   result = mcp__playwright__playwright_evaluate(
       script="document.title"
   )
   print(result)  # Should show page title
   ```

3. Check selector discovery script:
   ```python
   # Run discovery script and check for errors
   discovery = MCPSelectorDiscovery()
   script = discovery.generate_mcp_discovery_script()
   print(script)  # Verify script is valid JavaScript
   ```

### Issue: Enhanced tests have syntax errors

**Symptom**: Generated Python code doesn't run

**Solution**:
```python
# Use code validation
def validate_python_code(code: str) -> bool:
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return False

# Before saving
if validate_python_code(enhanced_code):
    generator.save_generated_test(enhanced_code, filename)
else:
    print("Generated code has syntax errors, regenerating...")
```

### Issue: Debug session can't navigate to failure page

**Symptom**: MCP navigation fails

**Solution**:
1. Check URL is accessible:
   ```bash
   curl -I https://www.toyota.com/page
   ```

2. Use proper navigation options:
   ```python
   mcp__playwright__playwright_navigate(
       url="https://www.toyota.com/page",
       timeout=30000,  # 30 seconds
       waitUntil="domcontentloaded"
   )
   ```

3. Handle authentication if needed:
   ```python
   # Navigate to login first if required
   mcp__playwright__playwright_navigate(url="https://www.toyota.com/login")
   mcp__playwright__playwright_fill(selector="#username", value="user")
   mcp__playwright__playwright_fill(selector="#password", value="pass")
   mcp__playwright__playwright_click(selector="button[type='submit']")
   ```

---

## Best Practices

### 1. Selector Discovery

✅ **DO**:
- Run discovery on fully loaded pages
- Categorize selectors by page/feature
- Merge discoveries incrementally
- Review before committing to database

❌ **DON'T**:
- Discover selectors on dynamic/loading pages
- Overwrite existing working selectors
- Skip categorization step
- Commit untested selectors

### 2. Test Recording

✅ **DO**:
- Record complete user flows
- Include success and error paths
- Add descriptive session names
- Document the flow purpose

❌ **DON'T**:
- Record partial flows
- Skip error scenarios
- Use generic names like "test1"
- Record without context

### 3. AI Enhancement

✅ **DO**:
- Start with "moderate" enhancement
- Review generated assertions
- Test enhanced code before committing
- Adjust enhancement level per test type

❌ **DON'T**:
- Always use "full" (can be over-engineered)
- Skip code review
- Commit untested enhancements
- Use same level for all tests

### 4. Debugging

✅ **DO**:
- Capture all artifacts (screenshots, logs, HTML)
- Save debug reports
- Update selector database with fixes
- Document resolution steps

❌ **DON'T**:
- Skip artifact capture
- Delete debug sessions prematurely
- Manually fix without updating DB
- Leave debugging incomplete

---

## Integration Summary

You now have a complete MCP integration that enables:

1. ✅ **Live Selector Discovery** - Find and categorize selectors interactively
2. ✅ **Interactive Test Recording** - Record flows and generate pytest tests
3. ✅ **AI Enhancement** - Add assertions, validations, and checks automatically
4. ✅ **Automated Debugging** - Investigate failures with live browser control
5. ✅ **Hybrid Workflow** - Combine manual exploration with AI automation

### Next Steps

1. **Try the demo workflow** (Workflow 1 above)
2. **Record your first test** using MCP codegen
3. **Enhance with AI** using the test generator
4. **Run and iterate** based on results

### Getting Help

- Check existing tests in `tests/ai_generated/` for examples
- Review MCP documentation: https://modelcontextprotocol.io
- See Playwright API: https://playwright.dev/python/docs/api/class-page
- Consult the framework docs in `/docs`

---

**Generated**: 2025-11-02
**Version**: 1.0
**Framework**: AI-Augmented E2E Testing for toyota.com
