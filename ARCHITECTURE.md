# AI-Augmented E2E Testing Framework - Architecture

## Overview

This framework is a comprehensive, AI-powered end-to-end testing solution designed specifically for toyota.com. It leverages cutting-edge AI capabilities to enhance test automation through intelligent test generation, self-healing selectors, visual regression analysis, and anomaly detection.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────-┐
│                     Test Execution Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │  Pytest      │  │  Playwright  │  │  Page Objects│            │
│  │  Framework   │──│  (Python)    │──│  (POM)       │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────-┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────-┐
│                      AI Enhancement Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ Test         │  │ Self-Healing │  │ Visual AI    │            │
│  │ Generator    │  │ Selectors    │  │ Comparison   │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│  ┌──────────────┐  ┌──────────────┐                              │
│  │ Anomaly      │  │ Coverage     │                              │
│  │ Detection    │  │ Analyzer     │                              │
│  └──────────────┘  └──────────────┘                              │
└─────────────────────────────────────────────────────────────────-┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────-┐
│                        AI Providers                              │
│  ┌──────────────┐              ┌──────────────┐                  │
│  │ Claude 3.5   │              │ GPT-4 Turbo  │                  │
│  │ Sonnet       │              │              │                  │
│  └──────────────┘              └──────────────┘                  │
└─────────────────────────────────────────────────────────────────-┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────-─┐
│                    Integration Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ MCP Client   │  │ CI/CD        │  │ Reporting    │            │
│  │ (Playwright) │  │ Integration  │  │ (HTML/JSON)  │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────-┘
```

## Core Components

### 1. Test Execution Layer

#### Pytest Framework
- Manages test discovery, execution, and reporting
- Provides fixtures for dependency injection
- Handles test lifecycle and hooks
- Supports parallel execution

#### Playwright (Python)
- Browser automation engine
- Multi-browser support (Chromium, Firefox, WebKit)
- Network interception and request mocking
- Screenshot and video capture
- Trace recording for debugging

#### Page Object Model (POM)
- `BasePage`: Common functionality for all pages
- `HomePage`: Toyota homepage interactions
- `VehiclesPage`: Vehicle browsing and filtering
- Extensible for additional pages

### 2. AI Enhancement Layer

#### Test Generator (`src/ai/test_generator.py`)
**Purpose**: Automatically generate test cases from requirements

**Features**:
- Generate tests from user flow descriptions
- Suggest test scenarios based on features
- Create comprehensive test suites from sitemaps
- Enhance existing tests with additional checks

**AI Models**: Claude 3.5 Sonnet / GPT-4 Turbo

**Usage**:
```python
generator = AITestGenerator(use_claude=True)
test_code = generator.generate_test_from_flow(
    page="/vehicles",
    user_flow="User filters vehicles by type and selects one",
    requirements=["Verify filtering", "Verify selection"]
)
```

#### Self-Healing Selectors (`src/ai/self_healing.py`)
**Purpose**: Automatically fix broken selectors when DOM changes

**Strategies**:
1. **Fallback Selectors**: Try known alternatives from history
2. **Semantic Selectors**: Use ARIA roles, labels, semantic HTML
3. **AI-Suggested Selectors**: Query AI for alternative selectors
4. **Fuzzy Text Matching**: Partial text and case-insensitive matching
5. **Position-Based**: Last resort using element position

**Database**: `test_data/selectors.json` stores successful selector mappings

**Usage**:
```python
healer = SelectorHealer(page)
element = healer.find_element("button.submit", auto_heal=True)
```

#### Visual AI (`src/ai/visual_ai.py`)
**Purpose**: Intelligent visual regression testing

**Comparison Algorithms**:
- **SSIM**: Structural Similarity Index
- **Perceptual Hash**: imagehash library
- **Pixel Difference**: OpenCV-based comparison

**AI Analysis**: Distinguishes between:
- Acceptable changes (dates, dynamic content, ads)
- Real regressions (layout shifts, missing elements)

**Usage**:
```python
visual_ai = VisualAI(use_claude=True)
result = visual_ai.compare_visual(
    page,
    screenshot_name="homepage",
    use_ai_analysis=True
)
```

#### Anomaly Detector (`src/ai/anomaly_detector.py`)
**Purpose**: Detect and analyze runtime anomalies

**Monitored Metrics**:
- Performance (FCP, LCP, TTFB, load time)
- Console errors and warnings
- Network request failures
- HTTP error responses (4xx, 5xx)
- Behavioral anomalies (missing elements)

**AI Analysis**: Correlates anomalies and suggests fixes

**Usage**:
```python
detector = AnomalyDetector(page)
metrics = detector.collect_performance_metrics()
analysis = detector.analyze_anomalies_with_ai()
```

#### Coverage Analyzer (`src/ai/coverage_analyzer.py`)
**Purpose**: Track test coverage and identify gaps

**Tracks**:
- Page coverage (which pages are tested)
- Feature coverage (which features are tested)
- User flow coverage (critical paths)
- Test execution history

**AI Suggestions**: Recommends missing test scenarios

**Usage**:
```python
analyzer = CoverageAnalyzer()
analyzer.record_test_execution(
    test_name="test_homepage",
    pages_visited=["/", "/vehicles"],
    features_used=["navigation", "search"]
)
gaps = analyzer.get_coverage_gaps()
suggestions = analyzer.suggest_tests_with_ai()
```

### 3. Integration Layer

#### MCP Client (`src/mcp/integration.py`)
**Purpose**: Integrate with Claude Code's Playwright MCP server

**Features**:
- Action recording and playback
- Live selector discovery
- Test code generation from recordings
- Real-time test execution

**Components**:
- `MCPClient`: Communicates with MCP server
- `ActionRecorder`: Records user interactions for test generation

#### Reporting System
**Formats**:
- **HTML**: Interactive report with screenshots and traces
- **JSON**: Machine-readable results for CI/CD
- **JUnit XML**: For CI/CD integration
- **AI Insights**: AI-analyzed issues and recommendations

**Reports**:
- Test execution report (Playwright HTML)
- Coverage report (Coverage Analyzer)
- Anomaly report (Anomaly Detector)
- Visual regression report (Visual AI)

### 4. Configuration Management

#### Settings (`src/config/settings.py`)
- Environment-based configuration using Pydantic
- Loads from `.env` file
- Type-safe settings with validation

#### Constants (`src/config/constants.py`)
- Toyota.com specific constants (pages, models)
- Test data templates
- Performance budgets (Web Vitals)
- Selector mappings
- AI prompts

## Data Flow

### Test Execution Flow

```
1. Pytest discovers tests
   ↓
2. Fixtures initialize (page objects, AI services)
   ↓
3. Test executes using page objects
   ↓
4. AI services monitor in background:
   - Self-healing fixes broken selectors
   - Anomaly detector tracks performance
   - Visual AI captures screenshots
   ↓
5. Test completes
   ↓
6. Coverage analyzer records execution
   ↓
7. Reports generated (HTML, JSON, AI insights)
```

### AI Test Generation Flow

```
1. User provides requirement/user flow
   ↓
2. AI Test Generator creates prompt
   ↓
3. Claude/GPT generates test code
   ↓
4. Framework validates and formats code
   ↓
5. Test saved to tests/ai_generated/
   ↓
6. Developer reviews and adjusts
   ↓
7. Test added to test suite
```

### Self-Healing Flow

```
1. Test attempts to find element
   ↓
2. Selector fails (timeout)
   ↓
3. Self-healing triggered
   ↓
4. Try fallback selectors
   ↓ (if fail)
5. Try semantic selectors
   ↓ (if fail)
6. Query AI for alternatives
   ↓ (if fail)
7. Try fuzzy matching
   ↓
8. If healed: save to selector database
   ↓
9. Test continues with working selector
```

## Design Patterns

### 1. Page Object Model (POM)
- Encapsulates page interactions
- Improves maintainability
- Reduces code duplication

### 2. Fixture Pattern
- Dependency injection via pytest fixtures
- Manages object lifecycle
- Enables test isolation

### 3. Strategy Pattern
- Multiple selector healing strategies
- Fallback chain for resilience

### 4. Observer Pattern
- Event listeners for console/network
- Real-time anomaly detection

### 5. Factory Pattern
- AI client initialization
- Page object creation

## Technology Stack

### Core Framework
- **Python 3.11+**: Programming language
- **Pytest**: Test framework
- **Playwright**: Browser automation

### AI & Machine Learning
- **Claude 3.5 Sonnet**: Primary AI model
- **GPT-4 Turbo**: Alternative AI model
- **OpenCV**: Image processing
- **imagehash**: Perceptual hashing

### Data Processing
- **Pydantic**: Settings validation
- **Pandas**: Data analysis
- **NumPy**: Numerical operations

### Utilities
- **python-dotenv**: Environment management
- **requests**: HTTP client
- **Pillow**: Image manipulation

## Extensibility

### Adding New Page Objects

```python
from src.core.page_objects.base_page import BasePage

class NewPage(BasePage):
    # Define selectors
    ELEMENT = "selector"

    def custom_action(self):
        self.click(self.ELEMENT)
```

### Adding New AI Capabilities

```python
class CustomAIFeature:
    def __init__(self, use_claude=True):
        # Initialize AI client
        pass

    def analyze(self, data):
        # Custom AI analysis
        pass
```

### Adding New Test Types

```python
@pytest.mark.custom_type
def test_new_feature(page):
    # Custom test logic
    pass
```

## Performance Considerations

### Optimization Strategies
1. **Parallel Execution**: pytest-xdist for parallel tests
2. **Selective AI**: AI features only when needed
3. **Caching**: Selector database, visual baselines
4. **Lazy Loading**: AI clients initialized on demand

### Resource Usage
- **Memory**: ~200MB base + ~100MB per browser
- **CPU**: Scales with parallel workers
- **Storage**: Visual baselines, reports, traces

## Security Considerations

1. **API Keys**: Stored in `.env`, not committed to git
2. **Test Data**: No real user credentials
3. **Network**: Tests against public toyota.com
4. **AI Queries**: No sensitive data sent to AI providers

## Future Enhancements

### Planned Features
1. **Mobile Testing**: Expanded mobile device coverage
2. **Accessibility**: WCAG 2.1 Level AA compliance checking
3. **API Testing**: Backend API validation
4. **Load Testing**: Performance under load
5. **Cross-Browser**: Enhanced multi-browser support
6. **AI Insights**: Deeper AI analysis and recommendations

### Scalability
- Containerization (Docker)
- Cloud execution (BrowserStack, Sauce Labs)
- Distributed test execution
- Real-time dashboards

## Conclusion

This AI-augmented framework represents a modern approach to E2E testing, combining traditional test automation with cutting-edge AI capabilities. It provides:

- **Resilience**: Self-healing selectors adapt to changes
- **Intelligence**: AI-powered test generation and analysis
- **Insights**: Comprehensive anomaly detection and reporting
- **Coverage**: Automated coverage tracking and gap identification
- **Maintainability**: Page object pattern and modular design

The framework is designed to evolve with toyota.com while maintaining high test reliability and providing actionable insights for continuous improvement.
