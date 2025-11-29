#!/bin/bash
# Playwright Codegen Helper Script
# This opens an interactive browser for recording tests

cd "$(dirname "$0")/.."
source venv/bin/activate

echo "=========================================="
echo "Playwright Codegen - Interactive Test Recording"
echo "=========================================="
echo ""
echo "This will open a browser. Actions you perform will be recorded."
echo ""
echo "Instructions:"
echo "1. Browser will open showing the target site"
echo "2. Inspector window shows generated code in real-time"
echo "3. Interact with the site (click, type, navigate)"
echo "4. Copy the generated code or save it"
echo "5. Close browser when done"
echo ""
echo "Choose what to record:"
echo "  1) Homepage (navigation, logo, menu)"
echo "  2) Dealers (search with zip code)"
echo "  3) Vehicles (browse vehicle list)"
echo "  4) Custom URL"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "Recording Homepage test..."
        playwright codegen https://www.toyota.com \
            --target python-pytest \
            -o tests/recorded/test_homepage_recorded.py
        ;;
    2)
        echo "Recording Dealers test..."
        playwright codegen https://www.toyota.com/dealers \
            --target python-pytest \
            -o tests/recorded/test_dealers_recorded.py
        ;;
    3)
        echo "Recording Vehicles test..."
        playwright codegen https://www.toyota.com/vehicles \
            --target python-pytest \
            -o tests/recorded/test_vehicles_recorded.py
        ;;
    4)
        read -p "Enter URL: " url
        read -p "Enter output filename (e.g., test_custom.py): " filename
        echo "Recording custom test..."
        playwright codegen "$url" \
            --target python-pytest \
            -o "tests/recorded/$filename"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Recording complete!"
echo "Check tests/recorded/ for generated test"
echo "=========================================="
