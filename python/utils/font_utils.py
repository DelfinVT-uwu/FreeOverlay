"""
Font Management Utilities Module.

Provides font loading and caching for PIL image drawing.
"""

import os
from typing import Optional, Tuple, Dict
from PIL import ImageFont

from core.logger import get_logger, ErrorHandler
from core.constants import (
    FONT_NAME_REGULAR,
    FONT_NAME_BOLD,
    FONT_NAME_EMOJI,
    FONT_PATH_LINUX,
)

logger = get_logger("FontUtils")

# Font cache to avoid reloading the same font multiple times
_font_cache: Dict[Tuple, Optional[ImageFont.FreeTypeFont]] = {}


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """
    Get a font at specified size with caching.

    Args:
        size: Font size in pixels
        bold: Whether to use bold variant

    Returns:
        PIL ImageFont object (cached)
    """
    cache_key = (size, bold)

    if cache_key in _font_cache:
        return _font_cache[cache_key]

    font = _load_font(size, bold)
    _font_cache[cache_key] = font
    return font


def get_emoji_font(size: int) -> ImageFont.FreeTypeFont:
    """
    Get emoji font at specified size with caching.

    Args:
        size: Font size in pixels

    Returns:
        PIL ImageFont object for emoji (cached)
    """
    cache_key = ("emoji", size)

    if cache_key in _font_cache:
        return _font_cache[cache_key]

    font = _load_emoji_font(size)
    _font_cache[cache_key] = font
    return font


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a TrueType font from disk."""
    font_name = FONT_NAME_BOLD if bold else FONT_NAME_REGULAR

    # Try Windows fonts first
    if os.name == "nt":
        try:
            font_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", font_name)
            font = ImageFont.truetype(font_path, size)
            logger.debug(f"Loaded font from Windows: {font_name}")
            return font
        except Exception as e:
            logger.debug(f"Failed to load Windows font: {e}")

    # Try Linux fonts
    try:
        font = ImageFont.truetype(FONT_PATH_LINUX, size)
        logger.debug(f"Loaded font from Linux: {FONT_PATH_LINUX}")
        return font
    except Exception as e:
        logger.debug(f"Failed to load Linux font: {e}")

    # Fallback to default
    logger.warning(f"Using default font (could not load {font_name})")
    return ImageFont.load_default()


def _load_emoji_font(size: int) -> ImageFont.FreeTypeFont:
    """Load emoji font from disk."""
    # Try Windows emoji font first
    if os.name == "nt":
        try:
            font_path = os.path.join(
                os.environ.get("WINDIR", "C:\\Windows"),
                "Fonts",
                FONT_NAME_EMOJI,
            )
            font = ImageFont.truetype(font_path, size)
            logger.debug(f"Loaded emoji font from Windows: {FONT_NAME_EMOJI}")
            return font
        except Exception as e:
            logger.debug(f"Failed to load emoji font: {e}")

    # Fallback to regular font (which usually has emoji support)
    logger.warning("Using regular font for emoji (emoji font not found)")
    return get_font(size)


def clear_font_cache() -> None:
    """Clear the font cache (useful for testing or cleanup)."""
    _font_cache.clear()
    logger.debug("Font cache cleared")


def get_font_cache_size() -> int:
    """Get the number of cached fonts."""
    return len(_font_cache)
