#!/bin/bash

# AI-Augmented E2E Testing Framework - Quick Setup Script
# This script automates the initial setup process

set -e  # Exit on error

echo "======================================================================"
echo "AI-Augmented E2E Testing Framework for Toyota.com"
echo "Quick Setup Script"
echo "======================================================================"
echo ""

# Check Python version
echo "[1/7] Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    echo "✓ Python 3 found: $(python3 --version)"
else
    echo "✗ Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "[2/7] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "[3/7] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install Python dependencies
echo ""
echo "[4/7] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Install Playwright browsers
echo ""
echo "[5/7] Installing Playwright browsers..."
playwright install
echo "✓ Playwright browsers installed"

# Create .env file if it doesn't exist
echo ""
echo "[6/7] Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your API keys:"
    echo "   - ANTHROPIC_API_KEY (for Claude)"
    echo "   - OPENAI_API_KEY (for GPT)"
    echo ""
    echo "   You need at least one API key for AI features to work."
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo ""
echo "[7/7] Creating project directories..."
mkdir -p test_data/visual_baselines
mkdir -p reports
mkdir -p logs
mkdir -p screenshots
touch test_data/visual_baselines/.gitkeep
echo "✓ Project directories created"

# Verify installation
echo ""
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file and add your API keys:"
echo "   nano .env"
echo ""
echo "2. Run a test to verify setup:"
echo "   source venv/bin/activate"
echo "   pytest tests/test_homepage.py::test_homepage_loads_successfully -v"
echo ""
echo "3. Run all smoke tests:"
echo "   pytest -m smoke -v"
echo ""
echo "4. Generate coverage report:"
echo "   python -m src.ai.coverage_analyzer --report"
echo ""
echo "5. Generate AI test scenarios:"
echo "   python -m src.ai.test_generator --sitemap --critical-only"
echo ""
echo "For more information, see:"
echo "  - README.md for overview"
echo "  - SETUP.md for detailed setup guide"
echo ""
echo "======================================================================"
