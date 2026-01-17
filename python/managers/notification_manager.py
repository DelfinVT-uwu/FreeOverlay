"""
Notification Management Module.

Handles notification creation, storage, and persistence.
Thread-safe with automatic persistence to JSON.
"""

import json
import threading
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

from managers.base import Manager
from core.logger import get_logger, ErrorHandler
from core.constants import (
    CONFIG_DIR,
    NOTIFICATIONS_FILE,
    MAX_NOTIFICATIONS,
    MAX_NOTIFICATIONS_PERSIST,
)

logger = get_logger("NotificationManager")


@dataclass
class Notification:
    """Represents a single notification."""

    id: str
    icon: str
    title: str
    message: str
    app: str = ""
    time: float = field(default_factory=time.time)
    read: bool = False


class NotificationManager(Manager):
    """
    Manages notifications with persistence.

    Features:
    - Add, retrieve, and clear notifications
    - Track read/unread status
    - Persist to JSON file
    - Thread-safe access
    - Automatic pruning of old notifications
    """

    def __init__(self, notif_file: Path = NOTIFICATIONS_FILE):
        """
        Initialize notification manager.

        Args:
            notif_file: Path to notifications JSON file
        """
        super().__init__("NotificationManager")
        self.notif_file = notif_file
        self.items: List[Notification] = []
        self._lock = threading.Lock()
        self._running = True

    def start(self) -> None:
        """Start notification manager (load from disk)."""
        if self._running:
            return

        self._running = True
        self._load()
        logger.info("Notification manager started")

    def stop(self) -> None:
        """Stop notification manager."""
        self._running = False
        logger.info("Notification manager stopped")

    def on_error(self, error: Exception) -> None:
        """Handle notification manager errors."""
        logger.error(f"Notification manager error: {error}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Notification Operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def add(self, notification: Notification) -> None:
        """
        Add a notification.

        Args:
            notification: Notification to add

        Automatically:
        - Prevents duplicates (by ID)
        - Prunes old notifications if limit exceeded
        - Persists to disk
        """
        with self._lock:
            # Prevent duplicates
            if any(n.id == notification.id for n in self.items):
                logger.debug(f"Notification already exists: {notification.id}")
                return

            self.items.insert(0, notification)
            self.items = self.items[:MAX_NOTIFICATIONS]
            self._save()
            logger.debug(f"Notification added: {notification.title}")

    def add_simple(self, icon: str, title: str, message: str, app: str = "") -> None:
        """
        Add a simple notification (auto-generated ID).

        Args:
            icon: Emoji or icon string
            title: Notification title
            message: Notification message
            app: Source application
        """
        notification = Notification(
            id=f"n_{time.time()}",
            icon=icon,
            title=title,
            message=message,
            app=app,
        )
        self.add(notification)

    def get_unread(self) -> int:
        """Get count of unread notifications."""
        with self._lock:
            return sum(1 for n in self.items if not n.read)

    def get_recent(self, count: int = 10) -> List[Notification]:
        """
        Get most recent notifications.

        Args:
            count: Number of notifications to return

        Returns:
            List of recent notifications (copies)
        """
        with self._lock:
            return [
                Notification(**asdict(n)) for n in self.items[:count]
            ]

    def mark_all_read(self) -> None:
        """Mark all notifications as read."""
        with self._lock:
            for n in self.items:
                n.read = True
            self._save()
            logger.debug("All notifications marked as read")

    def clear(self) -> None:
        """Clear all notifications."""
        with self._lock:
            self.items.clear()
            self._save()
            logger.info("Notifications cleared")

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """
        Get a specific notification by ID.

        Args:
            notification_id: ID of notification to retrieve

        Returns:
            Notification or None if not found
        """
        with self._lock:
            for n in self.items:
                if n.id == notification_id:
                    return Notification(**asdict(n))
        return None

    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.

        Args:
            notification_id: ID of notification to mark

        Returns:
            True if found and marked, False otherwise
        """
        with self._lock:
            for n in self.items:
                if n.id == notification_id and not n.read:
                    n.read = True
                    self._save()
                    return True
        return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Persistence
    # ═══════════════════════════════════════════════════════════════════════════════

    def _save(self) -> None:
        """Save notifications to disk."""
        try:
            self.notif_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.notif_file, "w", encoding="utf-8") as f:
                # Only persist the most recent notifications
                to_persist = self.items[:MAX_NOTIFICATIONS_PERSIST]
                json.dump([asdict(n) for n in to_persist], f, ensure_ascii=False)

            logger.debug(f"Saved {len(to_persist)} notifications to disk")
        except Exception as e:
            ErrorHandler.handle(e, context="notifications_save", severity="ERROR")

    def _load(self) -> None:
        """Load notifications from disk."""
        if not self.notif_file.exists():
            logger.debug(f"Notifications file not found: {self.notif_file}")
            return

        try:
            with open(self.notif_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for n_dict in data:
                    try:
                        notification = Notification(**n_dict)
                        self.items.append(notification)
                    except Exception as e:
                        logger.warning(f"Failed to parse notification: {e}")

            logger.info(f"Loaded {len(self.items)} notifications from disk")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid notifications JSON: {e}")
        except Exception as e:
            ErrorHandler.handle(e, context="notifications_load", severity="ERROR")
