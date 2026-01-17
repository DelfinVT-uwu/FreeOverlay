"""
Configuration Management Module.

Handles application configuration persistence and retrieval.
Decoupled from themes and other concerns.
"""

import json
from pathlib import Path
from typing import Optional, Any, Dict
from core.constants import CONFIG_DIR, CONFIG_FILE, DEFAULT_THEME
from core.logger import get_logger, ErrorHandler
from core.themes import ThemeManager

logger = get_logger("Config")


class ConfigManager:
    """
    Manages application configuration.

    Responsibilities:
    - Load/save configuration from disk
    - Manage theme selection
    - Provide configuration defaults
    - Validate configuration

    Design:
    - Single configuration file (config.json)
    - Theme management delegated to ThemeManager
    - Type-safe property access
    """

    def __init__(self, config_path: Path = CONFIG_FILE):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.theme_manager = ThemeManager()

        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load or create configuration
        self.config_data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load configuration from disk."""
        if not self.config_path.exists():
            logger.info("Config file not found. Creating with defaults.")
            self._create_defaults()
            self._save()
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.config_data = loaded or {}
            logger.info(f"Configuration loaded from {self.config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            self._create_defaults()
        except Exception as e:
            ErrorHandler.handle(e, context="config_load", severity="ERROR")
            self._create_defaults()

    def _create_defaults(self) -> None:
        """Initialize configuration with defaults."""
        self.config_data = {
            "theme": DEFAULT_THEME,
            "version": "1.0",
        }
        logger.info("Default configuration created")

    def _save(self) -> None:
        """Save configuration to disk."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Configuration saved to {self.config_path}")
        except Exception as e:
            ErrorHandler.handle(e, context="config_save", severity="ERROR")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Theme Management
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_theme_name(self) -> str:
        """Get current theme name."""
        return self.config_data.get("theme", DEFAULT_THEME)

    def set_theme(self, theme_name: str) -> bool:
        """
        Set the current theme.

        Args:
            theme_name: Name of theme to set

        Returns:
            True if successful, False otherwise
        """
        if not self.theme_manager.set_theme(theme_name):
            logger.warning(f"Theme '{theme_name}' not found")
            return False

        self.config_data["theme"] = theme_name
        self._save()
        logger.info(f"Theme set to: {theme_name}")
        return True

    def next_theme(self) -> str:
        """
        Switch to next theme in cycle.

        Returns:
            Name of the new theme
        """
        theme_name = self.theme_manager.next_theme()
        self.config_data["theme"] = theme_name
        self._save()
        return theme_name

    def get_theme_manager(self) -> ThemeManager:
        """Get the theme manager instance."""
        return self.theme_manager

    # ═══════════════════════════════════════════════════════════════════════════════
    # Generic Configuration Access
    # ═══════════════════════════════════════════════════════════════════════════════

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config_data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config_data[key] = value
        self._save()
        logger.debug(f"Config: {key} = {value}")

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return dict(self.config_data)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Validation
    # ═══════════════════════════════════════════════════════════════════════════════

    def validate(self) -> bool:
        """Validate configuration integrity."""
        # Check theme is valid
        if self.config_data.get("theme") not in self.theme_manager.list_themes():
            logger.warning("Current theme is invalid. Resetting to default.")
            self.set_theme(DEFAULT_THEME)
            return False

        return True

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self._create_defaults()
        self._save()
        logger.info("Configuration reset to defaults")
