"""
Theme Management Module.

Handles color themes and visual styling.
Decoupled from Config for flexibility and reusability.
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from core.constants import THEMES, DEFAULT_THEME
from core.logger import get_logger

logger = get_logger("Themes")

ColorTuple = Tuple[int, ...]
ThemeDict = Dict[str, any]


@dataclass
class Theme:
    """Represents a visual theme with colors and styling."""

    name: str
    primary: ColorTuple
    secondary: ColorTuple
    accent: ColorTuple
    success: ColorTuple
    warning: ColorTuple
    error: ColorTuple
    text: ColorTuple
    text_dim: ColorTuple
    panel: ColorTuple
    btn: ColorTuple

    def get_color(self, key: str, default: ColorTuple = (128, 128, 128)) -> ColorTuple:
        """Get a color from the theme."""
        return getattr(self, key, default)

    @classmethod
    def from_dict(cls, theme_dict: ThemeDict) -> "Theme":
        """Create a Theme from a dictionary."""
        return cls(
            name=theme_dict.get("name", "Unknown"),
            primary=tuple(theme_dict.get("primary", (128, 128, 128))),
            secondary=tuple(theme_dict.get("secondary", (128, 128, 128))),
            accent=tuple(theme_dict.get("accent", (128, 128, 128))),
            success=tuple(theme_dict.get("success", (128, 128, 128))),
            warning=tuple(theme_dict.get("warning", (128, 128, 128))),
            error=tuple(theme_dict.get("error", (128, 128, 128))),
            text=tuple(theme_dict.get("text", (255, 255, 255))),
            text_dim=tuple(theme_dict.get("text_dim", (128, 128, 128))),
            panel=tuple(theme_dict.get("panel", (50, 50, 50, 200))),
            btn=tuple(theme_dict.get("btn", (100, 100, 100))),
        )


class ThemeManager:
    """
    Manages available themes and current theme selection.

    Provides:
    - Theme loading and validation
    - Theme switching
    - Color retrieval
    - Theme listing
    """

    def __init__(self, initial_theme: Optional[str] = None):
        """
        Initialize theme manager.

        Args:
            initial_theme: Initial theme name. Defaults to DEFAULT_THEME.
        """
        self.available_themes: Dict[str, Theme] = {}
        self.current_theme_name: str = initial_theme or DEFAULT_THEME

        # Load all available themes
        self._load_themes()

        # Validate current theme exists
        if self.current_theme_name not in self.available_themes:
            logger.warning(
                f"Theme '{self.current_theme_name}' not found. "
                f"Falling back to '{DEFAULT_THEME}'"
            )
            self.current_theme_name = DEFAULT_THEME

    def _load_themes(self) -> None:
        """Load all themes from constants."""
        for theme_name, theme_dict in THEMES.items():
            try:
                self.available_themes[theme_name] = Theme.from_dict(theme_dict)
                logger.debug(f"Loaded theme: {theme_name}")
            except Exception as e:
                logger.error(f"Failed to load theme '{theme_name}': {e}")

    def get_current_theme(self) -> Theme:
        """Get the currently active theme."""
        return self.available_themes.get(
            self.current_theme_name,
            self.available_themes[DEFAULT_THEME],
        )

    def get_theme(self, name: str) -> Optional[Theme]:
        """Get a specific theme by name."""
        return self.available_themes.get(name)

    def get_color(self, key: str, default: ColorTuple = (128, 128, 128)) -> ColorTuple:
        """Get a color from the current theme."""
        theme = self.get_current_theme()
        return theme.get_color(key, default)

    def set_theme(self, name: str) -> bool:
        """
        Switch to a different theme.

        Args:
            name: Theme name to switch to

        Returns:
            True if successful, False if theme not found
        """
        if name not in self.available_themes:
            logger.warning(f"Theme '{name}' not found")
            return False

        self.current_theme_name = name
        logger.info(f"Theme switched to: {name}")
        return True

    def next_theme(self) -> str:
        """
        Switch to the next theme in the cycle.

        Returns:
            Name of the new theme
        """
        theme_names = list(self.available_themes.keys())
        if not theme_names:
            logger.error("No themes available")
            return self.current_theme_name

        current_index = theme_names.index(self.current_theme_name)
        next_index = (current_index + 1) % len(theme_names)
        next_theme = theme_names[next_index]

        self.set_theme(next_theme)
        return next_theme

    def list_themes(self) -> list:
        """Get list of available theme names."""
        return list(self.available_themes.keys())

    def get_theme_info(self, name: str) -> Optional[Dict]:
        """Get detailed info about a theme."""
        theme = self.get_theme(name)
        if not theme:
            return None

        return {
            "name": theme.name,
            "id": name,
            "colors": {
                "primary": theme.primary,
                "secondary": theme.secondary,
                "accent": theme.accent,
                "success": theme.success,
                "warning": theme.warning,
                "error": theme.error,
                "text": theme.text,
                "text_dim": theme.text_dim,
                "panel": theme.panel,
                "btn": theme.btn,
            },
        }
