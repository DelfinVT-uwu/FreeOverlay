"""
Text Processing Utilities Module.

Provides text formatting, truncation, and manipulation functions.
"""


def trunc(text: str, max_length: int) -> str:
    """
    Truncate text to maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length (including ellipsis)

    Returns:
        Truncated text or original if shorter
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 2] + ".."


def capitalize_words(text: str) -> str:
    """Capitalize first letter of each word."""
    return " ".join(word.capitalize() for word in text.split())


def safe_str(value: any, default: str = "N/A") -> str:
    """
    Safely convert value to string.

    Args:
        value: Value to convert
        default: Default string if conversion fails

    Returns:
        String representation or default
    """
    try:
        return str(value)
    except Exception:
        return default


def format_percentage(value: float, decimals: int = 0) -> str:
    """
    Format value as percentage.

    Args:
        value: Value (0-100)
        decimals: Decimal places

    Returns:
        Formatted percentage string
    """
    format_str = f"{{:.{decimals}f}}%"
    return format_str.format(max(0, min(100, value)))


def format_time(seconds: float) -> str:
    """
    Format seconds as HH:MM:SS.

    Args:
        seconds: Number of seconds

    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
