"""
Constants for toyota.com E2E testing
"""
from enum import Enum


class ToyotaPages(Enum):
    """Toyota.com page URLs and identifiers"""

    HOMEPAGE = "/"
    VEHICLES = "/vehicles"
    CARS = "/cars"
    TRUCKS = "/trucks"
    SUVS = "/suvs"
    HYBRIDS = "/hybrid-cars"
    ELECTRIC = "/bz4x"
    BUILD_AND_PRICE = "/configurator"
    DEALERS = "/dealers"
    OWNERS = "/owners"
    SHOPPING_TOOLS = "/shopping-tools"
    SPECIAL_OFFERS = "/special-offers"
    FINANCE = "/finance"


class VehicleModels(Enum):
    """Popular Toyota vehicle models"""

    CAMRY = "camry"
    COROLLA = "corolla"
    RAV4 = "rav4"
    HIGHLANDER = "highlander"
    TACOMA = "tacoma"
    TUNDRA = "tundra"
    SIENNA = "sienna"
    PRIUS = "prius"
    BZ4X = "bz4x"
    CROWN = "crown"
    GRAND_HIGHLANDER = "grandhighlander"
    SEQUOIA = "sequoia"


class TestPriority(Enum):
    """Test priority levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SelectorStrategy(Enum):
    """Selector strategies for self-healing"""

    ID = "id"
    NAME = "name"
    CLASS = "class"
    TEXT = "text"
    XPATH = "xpath"
    CSS = "css"
    ROLE = "role"
    DATA_TESTID = "data-testid"
    PLACEHOLDER = "placeholder"


class AnomalyType(Enum):
    """Types of anomalies to detect"""

    PERFORMANCE = "performance"
    CONSOLE_ERROR = "console_error"
    NETWORK_ERROR = "network_error"
    VISUAL_REGRESSION = "visual_regression"
    BEHAVIORAL = "behavioral"
    ACCESSIBILITY = "accessibility"


# Timeouts (in milliseconds)
TIMEOUT_SHORT = 5000
TIMEOUT_MEDIUM = 10000
TIMEOUT_LONG = 30000
TIMEOUT_PAGE_LOAD = 60000

# Visual regression thresholds
VISUAL_PIXEL_DIFF_THRESHOLD = 0.1  # 10% difference allowed
VISUAL_LAYOUT_SHIFT_THRESHOLD = 0.05  # 5% layout shift allowed

# Performance budgets (Web Vitals)
PERFORMANCE_BUDGETS = {
    "LCP": 2500,  # Largest Contentful Paint (ms)
    "FID": 100,  # First Input Delay (ms)
    "CLS": 0.1,  # Cumulative Layout Shift
    "FCP": 1800,  # First Contentful Paint (ms)
    "TTFB": 800,  # Time to First Byte (ms)
    "TBT": 200,  # Total Blocking Time (ms)
}

# Critical CSS selectors for toyota.com
TOYOTA_SELECTORS = {
    # Homepage
    "homepage_hero": "[data-testid='hero-carousel']",
    "homepage_nav": "nav.primary-navigation",
    "homepage_logo": "a.toyota-logo",
    # Vehicle browsing
    "vehicle_grid": "[data-testid='vehicle-grid']",
    "vehicle_card": ".vehicle-card",
    "vehicle_filter": "[data-testid='vehicle-filter']",
    # Build & Price
    "configurator": "#toyota-configurator",
    "color_selector": "[data-testid='color-selector']",
    "trim_selector": "[data-testid='trim-selector']",
    "package_selector": "[data-testid='package-selector']",
    # Dealer locator
    "dealer_search": "[data-testid='dealer-search-input']",
    "dealer_results": "[data-testid='dealer-results']",
    "dealer_map": "#dealer-map",
    # Navigation
    "main_nav": "nav[role='navigation']",
    "search_button": "[data-testid='search-button']",
    "menu_button": "[data-testid='menu-button']",
}

# AI Prompts for test generation
AI_PROMPTS = {
    "generate_test": """
    Generate comprehensive E2E test cases for the following scenario:

    Page: {page}
    User Flow: {flow}
    Requirements: {requirements}

    Generate Python pytest test cases using Playwright that cover:
    1. Happy path scenarios
    2. Edge cases and error handling
    3. Accessibility checks
    4. Performance validation
    5. Visual regression checkpoints

    Format the output as valid Python code with proper assertions and page object pattern.
    """,
    "analyze_failure": """
    Analyze the following test failure and provide insights:

    Test Name: {test_name}
    Error: {error}
    Screenshot: {screenshot_path}
    Trace: {trace}

    Provide:
    1. Root cause analysis
    2. Suggested fixes
    3. Whether this is a real bug or test flakiness
    4. Recommendations for test improvement
    """,
    "suggest_selectors": """
    The current selector failed: {failed_selector}

    Page HTML context:
    {html_context}

    Suggest alternative selectors that would be more resilient, considering:
    1. Semantic HTML
    2. ARIA roles
    3. Data attributes
    4. Stable text content

    Return top 3 alternatives in order of reliability.
    """,
}

# Test data templates
TEST_DATA_TEMPLATES = {
    "user_info": {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "phone": "555-123-4567",
        "zip_code": "90210",
    },
    "vehicle_preferences": {
        "body_type": ["SUV", "Sedan", "Truck"],
        "price_range": ["Under $30K", "$30K-$40K", "$40K-$50K", "Over $50K"],
        "fuel_type": ["Gasoline", "Hybrid", "Electric"],
    },
}
