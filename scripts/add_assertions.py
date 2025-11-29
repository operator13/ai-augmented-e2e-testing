#!/usr/bin/env python3
"""
Add Assertions to Codegen Tests
Takes a codegen-recorded test and enhances it with AI-generated assertions
"""
import sys
import os
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.test_generator import AITestGenerator


def analyze_test_code(test_code: str) -> dict:
    """Analyze test code to identify assertion points"""
    lines = test_code.split('\n')

    actions = []
    for i, line in enumerate(lines):
        # Look for key actions where assertions should be added
        if 'page.goto(' in line:
            actions.append({
                'type': 'navigation',
                'line': i,
                'code': line.strip(),
                'suggestion': 'Add URL assertion after navigation'
            })
        elif '.click()' in line and 'get_by_role("link"' in line:
            actions.append({
                'type': 'link_click',
                'line': i,
                'code': line.strip(),
                'suggestion': 'Add page load assertion after navigation'
            })
        elif '.fill(' in line:
            actions.append({
                'type': 'form_fill',
                'line': i,
                'code': line.strip(),
                'suggestion': 'Add input value assertion'
            })
        elif 'get_by_role("button"' in line and '.click()' in line:
            actions.append({
                'type': 'button_click',
                'line': i,
                'code': line.strip(),
                'suggestion': 'Add state change assertion'
            })

    return {
        'total_actions': len(actions),
        'actions': actions
    }


def generate_assertions_prompt(test_code: str, analysis: dict) -> str:
    """Generate prompt for AI to add assertions"""
    return f"""
You are enhancing a Playwright test that was recorded using codegen.
The test currently only has ACTIONS (clicks, fills, navigation) but NO ASSERTIONS.

Your task: Add comprehensive assertions to verify the test is working correctly.

Original Test Code:
```python
{test_code}
```

Action Analysis:
- Total Actions: {analysis['total_actions']}
- Navigation Actions: {len([a for a in analysis['actions'] if a['type'] == 'navigation'])}
- Link Clicks: {len([a for a in analysis['actions'] if a['type'] == 'link_click'])}
- Form Fills: {len([a for a in analysis['actions'] if a['type'] == 'form_fill'])}
- Button Clicks: {len([a for a in analysis['actions'] if a['type'] == 'button_click'])}

Add Assertions For:
1. After page.goto() - verify URL loaded correctly
2. After link clicks - verify navigation occurred
3. After form fills - verify input accepted value
4. After button clicks - verify expected state change
5. Add visibility checks for key elements
6. Add page title/heading assertions

Requirements:
- Keep all original actions unchanged
- Add expect() assertions after key actions
- Use Playwright's expect() API
- Make assertions meaningful (not just "element exists")
- Add comments explaining what each assertion verifies
- Ensure all imports are included (re, expect)

Return ONLY the complete enhanced Python test code with assertions added.
"""


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/add_assertions.py <test_file>")
        print("")
        print("Example:")
        print("  python scripts/add_assertions.py tests/recorded/test_gnav.py")
        sys.exit(1)

    test_file = sys.argv[1]

    if not os.path.exists(test_file):
        print(f"❌ Error: File not found: {test_file}")
        sys.exit(1)

    print("=" * 70)
    print("🤖 AI ASSERTION GENERATOR")
    print("=" * 70)
    print(f"\n📁 Reading: {test_file}")

    # Read original test
    with open(test_file, 'r') as f:
        original_code = f.read()

    # Analyze test
    print("\n🔍 Analyzing test code...")
    analysis = analyze_test_code(original_code)
    print(f"   Found {analysis['total_actions']} actions that need assertions")

    # Generate enhanced test with AI
    print("\n🤖 Generating assertions with AI...")
    print("   (This may take 30-60 seconds)")

    generator = AITestGenerator(use_claude=True)  # Use Claude
    prompt = generate_assertions_prompt(original_code, analysis)

    try:
        enhanced_code = generator._call_ai(prompt)

        # Clean up the response
        enhanced_code = generator._clean_generated_code(enhanced_code)

        # Save enhanced version
        output_file = test_file.replace('.py', '_with_assertions.py')
        with open(output_file, 'w') as f:
            f.write(enhanced_code)

        print(f"\n✅ Success!")
        print(f"📝 Enhanced test saved to: {output_file}")
        print("\n" + "=" * 70)
        print("COMPARISON")
        print("=" * 70)
        print(f"Original:  {len(original_code.split(chr(10)))} lines")
        print(f"Enhanced:  {len(enhanced_code.split(chr(10)))} lines")
        print(f"Added:     {len(enhanced_code.split(chr(10))) - len(original_code.split(chr(10)))} lines of assertions")
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print(f"\n1. Review the enhanced test:")
        print(f"   cat {output_file}")
        print(f"\n2. Run the enhanced test:")
        print(f"   pytest {output_file} --headed --slowmo 500")
        print(f"\n3. If satisfied, replace original:")
        print(f"   mv {output_file} {test_file}")
        print("")

    except Exception as e:
        print(f"\n❌ Error generating assertions: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API keys in .env")
        print("2. Try running with --use-gpt flag")
        print("3. Ensure test file has valid Python syntax")
        sys.exit(1)


if __name__ == "__main__":
    main()
