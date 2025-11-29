#!/bin/bash
# Interactive Test Recording Script
# Record Playwright tests with custom names

cd "$(dirname "$0")/.."
source venv/bin/activate

echo "=========================================="
echo "🎬 PLAYWRIGHT TEST RECORDER"
echo "=========================================="
echo ""
echo "This will open a browser to record your test."
echo ""

# Get test name from user
read -p "Test name (e.g., gnav, checkout, login): " test_name

# Validate test name
if [ -z "$test_name" ]; then
    echo "❌ Error: Test name cannot be empty"
    exit 1
fi

# Create filename
output_file="tests/recorded/test_${test_name}.py"

# Check if file exists
if [ -f "$output_file" ]; then
    echo ""
    echo "⚠️  Warning: $output_file already exists"
    read -p "Overwrite? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "❌ Recording cancelled"
        exit 0
    fi
fi

# Get URL from user
read -p "Starting URL (default: https://www.toyota.com): " url
url=${url:-https://www.toyota.com}

echo ""
echo "=========================================="
echo "🎬 Recording Test: $test_name"
echo "📝 Output: $output_file"
echo "🌐 URL: $url"
echo "=========================================="
echo ""
echo "Instructions:"
echo "1. Browser will open with Playwright Inspector"
echo "2. Perform your test actions in the browser"
echo "3. Inspector shows generated code in real-time"
echo "4. Close browser when done"
echo ""
read -p "Press Enter to start recording..."

# Start codegen with custom name
playwright codegen "$url" \
    --target python-pytest \
    -o "$output_file"

echo ""
echo "=========================================="
echo "✅ Recording Complete!"
echo "=========================================="
echo ""
echo "📁 Saved to: $output_file"
echo ""
echo "Next steps:"
echo "1. Review the recorded test:"
echo "   cat $output_file"
echo ""
echo "2. Run the test (headless):"
echo "   pytest $output_file"
echo ""
echo "3. Run the test (visible browser):"
echo "   pytest $output_file --headed"
echo ""
echo "4. Run in slow motion:"
echo "   pytest $output_file --headed --slowmo 1000"
echo ""
echo "5. Add assertions with AI:"
echo "   # Open the file and ask Claude/GPT to add assertions"
echo ""
