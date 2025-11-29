"""
Configuration management for AI-Augmented E2E Testing Framework
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # AI Configuration
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    ai_model: str = Field(default="gpt-4-turbo-preview", alias="AI_MODEL")
    claude_model: str = Field(default="claude-3-5-sonnet-20241022", alias="CLAUDE_MODEL")

    # Test Configuration
    base_url: str = Field(default="https://www.toyota.com", alias="BASE_URL")
    headless: bool = Field(default=True, alias="HEADLESS")
    browser: str = Field(default="chromium", alias="BROWSER")
    slow_mo: int = Field(default=0, alias="SLOW_MO")

    # AI Features
    enable_self_healing: bool = Field(default=True, alias="ENABLE_SELF_HEALING")
    enable_visual_ai: bool = Field(default=True, alias="ENABLE_VISUAL_AI")
    enable_anomaly_detection: bool = Field(default=True, alias="ENABLE_ANOMALY_DETECTION")
    enable_auto_generation: bool = Field(default=True, alias="ENABLE_AUTO_GENERATION")

    # Visual Regression
    visual_diff_threshold: float = Field(default=0.1, alias="VISUAL_DIFF_THRESHOLD")
    visual_baseline_dir: Path = Field(
        default=PROJECT_ROOT / "test_data" / "visual_baselines",
        alias="VISUAL_BASELINE_DIR",
    )

    # Coverage Tracking
    min_coverage_threshold: int = Field(default=80, alias="MIN_COVERAGE_THRESHOLD")

    # Reporting
    slack_webhook_url: Optional[str] = Field(default=None, alias="SLACK_WEBHOOK_URL")
    email_notifications: bool = Field(default=False, alias="EMAIL_NOTIFICATIONS")
    report_dir: Path = Field(default=PROJECT_ROOT / "reports", alias="REPORT_DIR")

    # MCP Configuration
    mcp_enabled: bool = Field(default=True, alias="MCP_ENABLED")
    mcp_server_url: str = Field(default="localhost:3000", alias="MCP_SERVER_URL")

    # Performance Thresholds (in milliseconds)
    max_page_load_time: int = Field(default=5000, alias="MAX_PAGE_LOAD_TIME")
    max_time_to_interactive: int = Field(default=3000, alias="MAX_TIME_TO_INTERACTIVE")
    max_first_contentful_paint: int = Field(default=2000, alias="MAX_FIRST_CONTENTFUL_PAINT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        populate_by_name = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.visual_baseline_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings
