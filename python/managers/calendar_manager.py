"""
Calendar and Event Management Module.

Manages events, reminders, and recurring events.
Handles automatic reminders via background thread.
"""

import json
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from managers.base import Manager
from managers.notification_manager import NotificationManager
from core.logger import get_logger, ErrorHandler
from core.constants import (
    CALENDAR_FILE,
    CALENDAR_REMINDER_INTERVAL,
    CALENDAR_REMINDER_TIME_DEFAULT,
    CALENDAR_DATE_FORMAT,
    DEFAULT_CALENDAR_EVENTS,
)

logger = get_logger("CalendarManager")


@dataclass
class Event:
    """Represents a calendar event."""

    id: str
    title: str
    date: str  # Format: YYYY-MM-DD
    time_str: str = ""  # Format: HH:MM
    yearly: bool = False
    reminded: bool = False


class CalendarManager(Manager):
    """
    Manages calendar events and reminders.

    Features:
    - Create and manage events
    - Filter events by date
    - Recurring/yearly events
    - Automatic reminders via background thread
    - Persistence to JSON
    - Thread-safe access
    """

    def __init__(
        self,
        notif_manager: NotificationManager,
        calendar_file: Path = CALENDAR_FILE,
    ):
        """
        Initialize calendar manager.

        Args:
            notif_manager: NotificationManager for sending reminders
            calendar_file: Path to calendar JSON file
        """
        super().__init__("CalendarManager")
        self.notif_manager = notif_manager
        self.calendar_file = calendar_file
        self.events: List[Event] = []
        self._lock = threading.Lock()
        self._reminder_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start calendar manager (load from disk and start reminders)."""
        if self._running:
            return

        self._running = True
        self._load()
        self._reminder_thread = threading.Thread(
            target=self._reminder_loop, daemon=True
        )
        self._reminder_thread.start()
        logger.info("Calendar manager started")

    def stop(self) -> None:
        """Stop calendar manager."""
        self._running = False
        if self._reminder_thread and self._reminder_thread.is_alive():
            self._reminder_thread.join(timeout=2)
        logger.info("Calendar manager stopped")

    def on_error(self, error: Exception) -> None:
        """Handle calendar manager errors."""
        logger.warning(f"Calendar error: {error}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Event Management
    # ═══════════════════════════════════════════════════════════════════════════════

    def add_event(
        self,
        title: str,
        date: str,
        time_str: str = "",
        yearly: bool = False,
    ) -> Event:
        """
        Add a new event.

        Args:
            title: Event title
            date: Event date (YYYY-MM-DD)
            time_str: Event time (HH:MM) or empty for all-day
            yearly: Whether this is a recurring yearly event

        Returns:
            The created Event
        """
        event = Event(
            id=f"ev_{time.time()}",
            title=title,
            date=date,
            time_str=time_str,
            yearly=yearly,
            reminded=False,
        )

        with self._lock:
            self.events.append(event)
            self._save()

        logger.info(f"Event added: {title} on {date}")
        return event

    def get_events_for_date(self, date: str) -> List[Event]:
        """
        Get events for a specific date.

        Args:
            date: Date to query (YYYY-MM-DD)

        Returns:
            List of events on that date (including yearly recurring)
        """
        with self._lock:
            month_day = date[5:]  # Extract MM-DD for yearly comparison
            return [
                e
                for e in self.events
                if e.date == date or (e.yearly and e.date[5:] == month_day)
            ]

    def get_upcoming(self, days: int = 7) -> List[Event]:
        """
        Get upcoming events.

        Args:
            days: Number of days to look ahead

        Returns:
            Sorted list of upcoming events (max 10)
        """
        today = datetime.now()
        result = []

        with self._lock:
            for event in self.events:
                try:
                    event_date = datetime.strptime(event.date, CALENDAR_DATE_FORMAT)

                    if event.yearly:
                        # Adjust year for recurring events
                        event_date = event_date.replace(year=today.year)
                        if event_date < today - timedelta(days=1):
                            event_date = event_date.replace(year=today.year + 1)

                    # Check if event is in the upcoming range
                    if today - timedelta(days=1) <= event_date <= today + timedelta(
                        days=days
                    ):
                        result.append(event)

                except ValueError as e:
                    logger.warning(f"Invalid event date format: {event.date} ({e})")

        return sorted(result, key=lambda x: x.date)[:10]

    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event.

        Args:
            event_id: ID of event to delete

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            original_len = len(self.events)
            self.events = [e for e in self.events if e.id != event_id]

            if len(self.events) < original_len:
                self._save()
                logger.info(f"Event deleted: {event_id}")
                return True

        return False

    def get_event(self, event_id: str) -> Optional[Event]:
        """Get a specific event by ID."""
        with self._lock:
            for e in self.events:
                if e.id == event_id:
                    return Event(**asdict(e))
        return None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Reminders
    # ═══════════════════════════════════════════════════════════════════════════════

    def _reminder_loop(self) -> None:
        """Background thread that sends reminders for upcoming events."""
        while self._running:
            try:
                self._check_reminders()
            except Exception as e:
                self.on_error(e)

            time.sleep(CALENDAR_REMINDER_INTERVAL)

    def _check_reminders(self) -> None:
        """Check if any events need reminders."""
        now = datetime.now()
        today_str = now.strftime(CALENDAR_DATE_FORMAT)
        current_time = now.strftime("%H:%M")

        with self._lock:
            for event in self.events:
                if event.reminded:
                    continue

                # Determine event date (handle yearly events)
                event_date = event.date
                if event.yearly:
                    event_date = f"{now.year}-{event.date[5:]}"

                # Check if event is today
                if event_date != today_str:
                    continue

                # Check time or use default reminder time
                reminder_time = event.time_str or CALENDAR_REMINDER_TIME_DEFAULT

                if current_time == reminder_time:
                    self._send_reminder(event)
                    event.reminded = True
                    self._save()

    def _send_reminder(self, event: Event) -> None:
        """Send a reminder notification for an event."""
        time_str = event.time_str or "Todo el día"
        self.notif_manager.add_simple(
            "📅",
            f"¡Es hora! {event.title}",
            f"Evento: {time_str}",
        )
        logger.info(f"Reminder sent for event: {event.title}")

    def reset_reminders(self) -> None:
        """Reset all reminder flags (for testing or manual reset)."""
        with self._lock:
            for event in self.events:
                event.reminded = False
            self._save()
        logger.info("Reminder flags reset")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Persistence
    # ═══════════════════════════════════════════════════════════════════════════════

    def _save(self) -> None:
        """Save events to disk."""
        try:
            self.calendar_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.calendar_file, "w", encoding="utf-8") as f:
                json.dump([asdict(e) for e in self.events], f, ensure_ascii=False)

            logger.debug(f"Saved {len(self.events)} calendar events to disk")
        except Exception as e:
            ErrorHandler.handle(e, context="calendar_save", severity="ERROR")

    def _load(self) -> None:
        """Load events from disk."""
        if not self.calendar_file.exists():
            logger.debug(f"Calendar file not found: {self.calendar_file}")
            self._create_defaults()
            return

        try:
            with open(self.calendar_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for e_dict in data:
                    try:
                        event = Event(**e_dict)
                        self.events.append(event)
                    except Exception as e:
                        logger.warning(f"Failed to parse event: {e}")

            logger.info(f"Loaded {len(self.events)} calendar events from disk")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid calendar JSON: {e}")
            self._create_defaults()
        except Exception as e:
            ErrorHandler.handle(e, context="calendar_load", severity="ERROR")
            self._create_defaults()

    def _create_defaults(self) -> None:
        """Create default calendar events."""
        try:
            now = datetime.now()
            for event_dict in DEFAULT_CALENDAR_EVENTS:
                event_dict["date"] = event_dict["date"].format(year=now.year)
                event = Event(**event_dict)
                self.events.append(event)

            self._save()
            logger.info("Default calendar events created")
        except Exception as e:
            ErrorHandler.handle(e, context="calendar_defaults", severity="ERROR")
