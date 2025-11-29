"""
Utility Helper Functions

Common utility functions used across the test framework.
"""
import json
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def generate_random_string(length: int = 10) -> str:
    """
    Generate a random string

    Args:
        length: Length of string to generate

    Returns:
        Random string
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_email() -> str:
    """
    Generate a random email address

    Returns:
        Random email address
    """
    return f"test_{generate_random_string(8)}@example.com"


def generate_timestamp() -> str:
    """
    Generate timestamp string

    Returns:
        Timestamp in ISO format
    """
    return datetime.now().isoformat()


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON file

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with open(file_path, "r") as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], file_path: Path):
    """
    Save data to JSON file

    Args:
        data: Data to save
        file_path: Output file path
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def wait_for_condition(
    condition_func, timeout: int = 10, interval: float = 0.5
) -> bool:
    """
    Wait for a condition to be true

    Args:
        condition_func: Function that returns boolean
        timeout: Timeout in seconds
        interval: Check interval in seconds

    Returns:
        True if condition met, False if timeout
    """
    import time

    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename


def format_currency(amount: float) -> str:
    """
    Format amount as currency

    Args:
        amount: Dollar amount

    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def parse_currency(currency_string: str) -> float:
    """
    Parse currency string to float

    Args:
        currency_string: Currency string like "$1,234.56"

    Returns:
        Float value
    """
    # Remove $ and commas
    cleaned = currency_string.replace("$", "").replace(",", "")
    return float(cleaned)


def create_directory_if_not_exists(directory: Path):
    """
    Create directory if it doesn't exist

    Args:
        directory: Directory path
    """
    directory.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """
    Get project root directory

    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent.parent.parent


def retry_on_exception(max_attempts: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on exception

    Args:
        max_attempts: Maximum retry attempts
        delay: Delay between retries in seconds

    Returns:
        Decorated function
    """
    import functools
    import time

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    print(f"Attempt {attempts} failed: {e}. Retrying...")
                    time.sleep(delay)

        return wrapper

    return decorator


def take_screenshot_on_failure(page, test_name: str) -> Optional[Path]:
    """
    Take screenshot on test failure

    Args:
        page: Playwright page object
        test_name: Test name

    Returns:
        Screenshot path or None
    """
    try:
        screenshot_dir = get_project_root() / "screenshots" / "failures"
        create_directory_if_not_exists(screenshot_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{sanitize_filename(test_name)}_{timestamp}.png"
        screenshot_path = screenshot_dir / filename

        page.screenshot(path=str(screenshot_path))
        return screenshot_path
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return None


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks

    Args:
        lst: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries

    Args:
        dict1: First dictionary
        dict2: Second dictionary

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result
