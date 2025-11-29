"""
Simple conftest - No AI dependencies
"""
import pytest


# Simple configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "smoke: Smoke tests")
