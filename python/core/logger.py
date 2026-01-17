"""
Logging and Error Handling Module.

Replaces silent exception handling (except: pass) with proper logging.
Provides structured error reporting for debugging and monitoring.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Any
from core.constants import CONFIG_DIR, LOG_LEVEL, LOG_FORMAT

# Create logs directory
LOGS_DIR = CONFIG_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# Configure Root Logger
# ═══════════════════════════════════════════════════════════════════════════════

logger = logging.getLogger("FreeOverlay")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Console Handler (colored output)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter(LOG_FORMAT)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File Handler (persistent logging)
file_handler = logging.FileHandler(LOGS_DIR / "freevr_overlay.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(LOG_FORMAT)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# ═══════════════════════════════════════════════════════════════════════════════
# Module Loggers
# ═══════════════════════════════════════════════════════════════════════════════

def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module."""
    return logging.getLogger(f"FreeOverlay.{name}")


class ErrorHandler:
    """
    Handles errors gracefully with logging.
    Replaces the pattern: except: pass with proper error tracking.
    """

    @staticmethod
    def handle(
        error: Exception,
        context: str = "",
        severity: str = "WARNING",
        reraise: bool = False,
    ) -> Optional[Exception]:
        """
        Handle an exception with logging.

        Args:
            error: The exception to handle
            context: Contextual information about where the error occurred
            severity: Logging severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            reraise: Whether to re-raise the exception after logging

        Returns:
            The exception if not reraised, None otherwise

        Example:
            try:
                risky_operation()
            except Exception as e:
                ErrorHandler.handle(e, context="risky_operation", severity="ERROR")
        """
        log_func = getattr(logger, severity.lower(), logger.warning)

        if context:
            log_func(f"[{context}] {type(error).__name__}: {str(error)}", exc_info=True)
        else:
            log_func(f"{type(error).__name__}: {str(error)}", exc_info=True)

        if reraise:
            raise

        return error

    @staticmethod
    def safe_execute(
        func,
        *args,
        context: str = "",
        default_return: Any = None,
        severity: str = "WARNING",
        **kwargs,
    ) -> Any:
        """
        Execute a function and handle any exceptions.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            context: Contextual information
            default_return: Value to return if exception occurs
            severity: Logging severity
            **kwargs: Keyword arguments for func

        Returns:
            Result from func or default_return if exception occurs

        Example:
            result = ErrorHandler.safe_execute(
                risky_func,
                arg1, arg2,
                context="risky_func",
                default_return=None,
                severity="WARNING"
            )
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle(e, context=context, severity=severity)
            return default_return


# ═══════════════════════════════════════════════════════════════════════════════
# Quick Access Loggers
# ═══════════════════════════════════════════════════════════════════════════════

vr_logger = get_logger("VR")
rendering_logger = get_logger("Rendering")
manager_logger = get_logger("Manager")
ui_logger = get_logger("UI")
config_logger = get_logger("Config")
startup_logger = get_logger("Startup")

# ═══════════════════════════════════════════════════════════════════════════════
# Initialization Logging
# ═══════════════════════════════════════════════════════════════════════════════

startup_logger.info(f"Logging initialized to: {LOGS_DIR}")
startup_logger.info(f"Log level: {LOG_LEVEL}")
