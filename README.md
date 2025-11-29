# AI-Augmented E2E Testing Framework for Toyota.com

An intelligent end-to-end testing framework powered by AI, built with Playwright and Python for comprehensive automated testing of toyota.com.

## Features

### Core Testing Capabilities
- **Multi-Browser Support**: Chromium, Firefox, WebKit, and mobile browsers
- **Parallel Execution**: Fast test execution with pytest-xdist
- **Rich Reporting**: HTML reports, JSON exports, and AI-powered insights
- **Screenshot & Video**: Automatic capture on failures for debugging

### AI-Powered Features

#### 1. Intelligent Test Generation
- Automatically generate test cases from user flows and requirements
- Leverage Claude/GPT models to create comprehensive test scenarios
- Integration with Playwright MCP for real-time test creation

#### 2. Self-Healing Selectors
- AI-powered selector healing when DOM structure changes
- Multiple fallback strategies (ID, class, text, position)
- Automatic selector optimization and learning

#### 3. Visual Regression with AI
- Smart visual comparison that ignores acceptable changes
- AI-driven analysis of visual differences
- Context-aware comparison (dates, dynamic content, ads)

#### 4. Anomaly Detection
- Performance monitoring and regression detection
- Console error tracking and classification
- Behavioral anomaly identification
- Network request analysis

#### 5. Automated Coverage Analysis
- Track which pages and features are tested
- Identify gaps in test coverage
- Suggest missing test scenarios using AI

## Project Structure

```
AI_AugmentedE2E/
├── src/
│   ├── ai/
│   │   ├── test_generator.py          # AI test case generator
│   │   ├── self_healing.py            # Self-healing selectors
│   │   ├── visual_ai.py               # AI visual comparison
│   │   ├── anomaly_detector.py        # Anomaly detection engine
│   │   └── coverage_analyzer.py       # Coverage tracking
│   ├── core/
│   │   ├── page_objects/              # Page object models
│   │   ├── fixtures/                  # Pytest fixtures
│   │   └── utils/                     # Utility functions
│   ├── config/
│   │   ├── settings.py                # Configuration management
│   │   └── constants.py               # Test constants
│   └── mcp/
│       └── integration.py             # MCP client integration
├── tests/
│   ├── test_homepage.py               # Homepage tests
│   ├── test_vehicles.py               # Vehicle browsing tests
│   ├── test_dealers.py                # Dealer locator tests
│   ├── test_build_price.py            # Build & Price flow
│   └── ai_generated/                  # AI-generated tests
├── test_data/
│   ├── visual_baselines/              # Visual regression baselines
│   ├── test_data.json                 # Test data files
│   └── selectors.json                 # Selector repository
├── reports/                            # Test reports and artifacts
├── .env                                # Environment configuration
├── pytest.ini                          # Pytest configuration
├── pyproject.toml                      # Python project config
└── requirements.txt                    # Python dependencies

```

## Installation

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ (for Playwright browsers)

### Setup

1. Clone the repository:
```bash
cd /Users/oantazo/Desktop/AI_AugmentedE2E
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

**Important**: You must add your own API keys to the `.env` file:
- `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys
- `ANTHROPIC_API_KEY`: Get from https://console.anthropic.com/settings/keys

**Security Note**: Never commit your `.env` file to git. It's already in `.gitignore` to protect your API keys.

## Usage

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_homepage.py

# Run with specific browser
pytest --browser firefox

# Run in headed mode (see browser)
pytest --headed

# Run smoke tests only
pytest -m smoke

# Run tests in parallel
pytest -n auto

# Generate coverage report
pytest --cov=src --cov-report=html
```

### AI Test Generation

```bash
# Generate test cases from requirements
python -m src.ai.test_generator --url https://www.toyota.com --flow "vehicle browsing"

# Generate tests for entire site
python -m src.ai.test_generator --site-map --ai-analyze
```

### Coverage Analysis

```bash
# Analyze current test coverage
python -m src.ai.coverage_analyzer

# Generate coverage report with AI suggestions
python -m src.ai.coverage_analyzer --suggest-tests
```

### Visual Regression Testing

```bash
# Update visual baselines
pytest --update-baselines -m visual

# Run visual regression tests
pytest -m visual
```

## Configuration

### Environment Variables

See `.env.example` for all configuration options.

Key settings:
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`: AI API keys
- `BASE_URL`: Target website URL
- `ENABLE_SELF_HEALING`: Enable/disable self-healing selectors
- `ENABLE_VISUAL_AI`: Enable/disable AI visual comparison
- `ENABLE_ANOMALY_DETECTION`: Enable/disable anomaly detection

### Pytest Markers

- `@pytest.mark.smoke`: Critical smoke tests
- `@pytest.mark.regression`: Full regression suite
- `@pytest.mark.visual`: Visual regression tests
- `@pytest.mark.ai_generated`: AI-generated test cases
- `@pytest.mark.critical_path`: Critical user journeys
- `@pytest.mark.performance`: Performance tests

## Toyota.com Test Standards

### Critical User Flows
1. Homepage navigation and hero carousel
2. Vehicle browsing and filtering
3. Build & Price configuration
4. Dealer locator and appointment scheduling
5. Owner's portal access
6. Special offers and incentives

### Test Coverage Requirements
- Minimum 80% page coverage
- All critical paths must have smoke tests
- Visual regression for key components
- Performance baselines for page loads

### Accessibility Standards
- WCAG 2.1 Level AA compliance
- Keyboard navigation testing
- Screen reader compatibility

## MCP Integration

This framework integrates with Claude Code's Playwright MCP server for:
- Real-time test execution and debugging
- Live selector discovery
- Interactive test generation
- Visual validation

## Reporting

Test reports are generated in multiple formats:
- **HTML**: Interactive report at `reports/report.html`
- **JSON**: Machine-readable results at `reports/results.json`
- **AI Insights**: AI-analyzed issues at `reports/ai-insights.json`

## Contributing

1. Follow PEP 8 style guide
2. Use Black for code formatting
3. Add type hints to all functions
4. Write docstrings for classes and functions
5. Include tests for new features

## License

MIT License
