# AI-Augmented E2E Testing Framework - Setup Guide

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Node.js 18+ (for Playwright browsers)
- Git

### Installation

1. **Clone or navigate to the project**:
```bash
cd /Users/oantazo/Desktop/AI_AugmentedE2E
```

2. **Create and activate virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers**:
```bash
playwright install
```

5. **Configure environment variables**:
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```bash
# Required: Add your API keys
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Optional: Customize settings
BASE_URL=https://www.toyota.com
HEADLESS=true
ENABLE_SELF_HEALING=true
ENABLE_VISUAL_AI=true
ENABLE_ANOMALY_DETECTION=true
```

### Verify Installation

```bash
# Run a simple test to verify setup
pytest tests/test_homepage.py::test_homepage_loads_successfully -v
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_homepage.py

# Run tests with specific marker
pytest -m smoke
pytest -m regression
pytest -m visual

# Run tests in headed mode (see browser)
pytest --headed

# Run tests in parallel
pytest -n auto

# Run with detailed output
pytest -v -s
```

### Advanced Usage

```bash
# Run tests with coverage report
pytest --cov=src --cov-report=html

# Run specific browser
pytest --browser firefox
pytest --browser webkit

# Run with video recording
pytest --video=retain-on-failure

# Generate HTML report
pytest --html=reports/report.html
```

## AI Features Usage

### 1. AI Test Generation

Generate test cases from requirements:

```bash
# Generate test for specific page
python -m src.ai.test_generator --url /vehicles --flow "User browses vehicles and filters by SUV"

# Generate tests for entire sitemap
python -m src.ai.test_generator --sitemap --critical-only

# Suggest test scenarios
python -m src.ai.test_generator --feature "Vehicle Search"
```

### 2. Self-Healing Selectors

Self-healing is enabled by default when `ENABLE_SELF_HEALING=true` in `.env`.

Selectors automatically heal when they fail. Healed selectors are saved to `test_data/selectors.json`.

### 3. Visual Regression Testing

```bash
# Create visual baselines (first run)
pytest -m visual --update-baselines

# Run visual regression tests
pytest -m visual

# Update specific baseline
pytest tests/test_homepage.py::test_homepage_visual_regression --update-baselines
```

### 4. Anomaly Detection

Anomaly detection runs automatically during test execution when enabled.

View anomaly reports in `reports/anomaly_report_*.json`.

### 5. Coverage Analysis

```bash
# View coverage summary
python -m src.ai.coverage_analyzer

# Generate coverage report
python -m src.ai.coverage_analyzer --report

# View coverage gaps
python -m src.ai.coverage_analyzer --gaps

# Get AI suggestions for missing tests
python -m src.ai.coverage_analyzer --suggest-tests
```

## Project Structure

```
AI_AugmentedE2E/
├── src/                          # Source code
│   ├── ai/                       # AI modules
│   │   ├── test_generator.py    # AI test case generator
│   │   ├── self_healing.py      # Self-healing selectors
│   │   ├── visual_ai.py         # Visual regression with AI
│   │   ├── anomaly_detector.py  # Anomaly detection
│   │   └── coverage_analyzer.py # Coverage tracking
│   ├── core/                    # Core framework
│   │   ├── page_objects/        # Page object models
│   │   ├── fixtures/            # Pytest fixtures
│   │   └── utils/               # Utility functions
│   ├── config/                  # Configuration
│   │   ├── settings.py          # Settings management
│   │   └── constants.py         # Constants
│   └── mcp/                     # MCP integration
│       └── integration.py       # MCP client
├── tests/                        # Test cases
│   ├── test_homepage.py         # Homepage tests
│   ├── test_vehicles.py         # Vehicle tests
│   ├── test_ai_features.py      # AI features demo
│   └── ai_generated/            # AI-generated tests
├── test_data/                    # Test data
│   ├── visual_baselines/        # Visual regression baselines
│   ├── selectors.json           # Selector database
│   └── coverage.json            # Coverage database
├── reports/                      # Test reports
├── .env                          # Environment config
├── pytest.ini                    # Pytest configuration
├── pyproject.toml               # Python project config
└── requirements.txt             # Python dependencies
```

## Configuration

### Environment Variables

Key settings in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `BASE_URL` | Target website | https://www.toyota.com |
| `HEADLESS` | Run browser headless | true |
| `ENABLE_SELF_HEALING` | Enable self-healing selectors | true |
| `ENABLE_VISUAL_AI` | Enable AI visual comparison | true |
| `ENABLE_ANOMALY_DETECTION` | Enable anomaly detection | true |
| `ENABLE_AUTO_GENERATION` | Enable AI test generation | true |
| `VISUAL_DIFF_THRESHOLD` | Visual difference threshold | 0.1 (10%) |
| `MIN_COVERAGE_THRESHOLD` | Minimum coverage required | 80% |

### Pytest Configuration

Edit `pytest.ini` to customize:
- Test paths
- Markers
- Browser settings
- Report options

## Best Practices

### Writing Tests

1. **Use Page Objects**: Always use page objects for better maintainability
```python
def test_example(home_page: HomePage):
    home_page.open()
    home_page.verify_logo_visible()
```

2. **Use Markers**: Tag tests appropriately
```python
@pytest.mark.smoke
@pytest.mark.critical_path
def test_important_flow(page):
    pass
```

3. **Use AI Features**: Leverage AI capabilities
```python
def test_with_ai(home_page, visual_ai, anomaly_detector):
    home_page.open()

    # Visual regression with AI
    visual_ai.compare_visual(home_page.page, "homepage")

    # Performance monitoring
    anomaly_detector.collect_performance_metrics()
```

### Debugging

```bash
# Run in headed mode with debugging
pytest --headed --slowmo=500 tests/test_homepage.py -v

# Run with debugging on failure
pytest --pdb

# Run with trace
pytest --trace
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps
      - name: Run tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: pytest -m smoke -v
      - name: Upload reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-reports
          path: reports/
```

## Troubleshooting

### Common Issues

**1. Playwright not installed**
```bash
playwright install
```

**2. API keys not configured**
```bash
# Edit .env and add your API keys
ANTHROPIC_API_KEY=your_key_here
```

**3. Import errors**
```bash
# Ensure you're in virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**4. Tests timing out**
```bash
# Increase timeout in pytest.ini or use command line
pytest --timeout=60
```

**5. Visual regression failures**
```bash
# Update baselines
pytest -m visual --update-baselines
```

## Support & Documentation

- Framework README: `README.md`
- Toyota.com test standards: Defined in `src/config/constants.py`
- API Documentation: See docstrings in source code
- Example tests: `tests/test_ai_features.py`

## Next Steps

1. Review example tests in `tests/` directory
2. Create your own page objects in `src/core/page_objects/`
3. Write custom tests for your use cases
4. Use AI to generate additional test scenarios
5. Monitor coverage and fill gaps
6. Review anomaly reports to improve test quality

For questions or issues, refer to the main README.md or project documentation.
