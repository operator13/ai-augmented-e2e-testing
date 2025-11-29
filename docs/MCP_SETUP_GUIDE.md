# Playwright MCP Configuration Guide

## Current Status

✅ **mcp-server-playwright is running** (found multiple instances)
❌ **Not configured in Claude Code** (only Selenium MCP is configured)

## Step 1: Add Playwright MCP to Claude Code

Edit your Claude Code MCP configuration file:

```bash
# Open the config file
code ~/.config/claude-code/mcp_config.json
# OR
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Add Playwright MCP to the config:**

```json
{
  "mcpServers": {
    "selenium": {
      "command": "npx",
      "args": ["-y", "@angiejones/mcp-selenium"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "mcp-server-playwright"]
    }
  }
}
```

**Save and restart Claude Code.**

## Step 2: Test MCP Connection

After restarting Claude Code, test if Playwright MCP is available:

```bash
# In Claude Code, ask:
"Can you use Playwright MCP to navigate to https://www.toyota.com and click the Vehicles button?"
```

If it works, MCP is properly configured!

## Step 3: Configure Framework to Use MCP

Update your `.env` file to enable MCP:

```bash
# MCP Configuration
MCP_ENABLED=true
MCP_SERVER_URL=stdio  # MCP uses stdio, not HTTP
```

## Step 4: Use MCP in Your Tests

### Option A: Use Claude Code's MCP Directly

In Claude Code chat:
```
"Use Playwright MCP to:
1. Navigate to https://www.toyota.com
2. Click on Vehicles menu
3. Click on Crossovers & SUVs
4. Click on Corolla Cross
Generate test code from these actions"
```

### Option B: Use MCP Python Client

Create a test that uses MCP:

```python
# tests/mcp/test_with_mcp.py
import pytest
from playwright.sync_api import Page
from src.mcp.integration import MCPClient

def test_using_mcp(page: Page):
    """Test that uses MCP for enhanced recording"""

    mcp = MCPClient()

    # Check if MCP is available
    if not mcp.health_check():
        pytest.skip("MCP server not available")

    # Execute action through MCP
    result = mcp.execute_action(page, "navigate", {
        "url": "https://www.toyota.com"
    })

    assert result.get("success"), "Navigation failed"
```

## MCP vs Codegen: What's the Difference?

| Feature | Codegen (What We've Been Using) | MCP Integration |
|---------|--------------------------------|-----------------|
| **How it works** | Opens browser, you interact, generates code | Programmatic API to Playwright |
| **Best for** | Recording real user flows | Automated test generation |
| **Output** | Python test code | JSON actions + test code |
| **Integration** | Standalone tool | Integrated with Claude Code |
| **Use case** | Manual exploration | Automated workflows |

## Current Recommendation

**Keep using Codegen for now** because:
1. ✅ It's working perfectly (we recorded GNAV test successfully)
2. ✅ Generates clean, readable test code
3. ✅ No additional setup needed
4. ✅ You can see exactly what you're recording

**Use MCP later for:**
- Automated test generation at scale
- Integration with CI/CD
- Programmatic test creation
- API-driven test generation

## Quick Start: Continue with Codegen

Since codegen is working well:

```bash
# Record new tests
./scripts/record_test.sh

# Add assertions with Claude
python scripts/add_assertions.py tests/recorded/test_name.py

# Run with slow motion
python -m pytest tests/recorded/test_name.py --headed --slowmo 2000
```

## If You Still Want MCP

1. **Add to Claude config** (see Step 1)
2. **Restart Claude Code**
3. **Ask Claude Code to use Playwright MCP**
4. **Generate tests through chat interface**

## MCP Commands (Once Configured)

In Claude Code chat, you can ask:

```
"Use Playwright MCP to record a test for toyota.com dealer search"
"Use Playwright MCP to generate a test that clicks through the vehicles menu"
"Use Playwright MCP to verify all navigation links work"
```

Claude will use MCP to execute Playwright commands and generate test code automatically.

## Summary

**Current Setup:**
- ✅ Playwright codegen working perfectly
- ✅ Can record tests manually
- ✅ Claude Sonnet 4.5 adds assertions
- ✅ Tests run with visual browser
- ⚠️ MCP available but not integrated

**Recommendation:**
Stick with codegen workflow - it's simpler and working great! Add MCP later if you need automation.
