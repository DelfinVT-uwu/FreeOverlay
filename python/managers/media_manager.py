"""
Media Player Detection and Control Manager.

Monitors system media playback and provides playback control.
Runs as a background thread on Windows systems.
"""

import os
import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Optional
import pyautogui

from managers.base import Manager
from core.logger import get_logger, ErrorHandler
from core.constants import MEDIA_POLL_INTERVAL

logger = get_logger("MediaManager")


@dataclass
class MediaInfo:
    """Represents current media playback state."""

    title: str = ""
    artist: str = ""
    is_playing: bool = False
    source: str = ""


class MediaManager(Manager):
    """
    Detects and controls media playback on Windows.

    Features:
    - Polls Windows Media Control for current track info
    - Identifies media source (Spotify, Chrome, Firefox, etc)
    - Provides playback control (play/pause, next, previous, stop)
    - Thread-safe access to media info
    """

    def __init__(self):
        """Initialize media manager."""
        super().__init__("MediaManager")
        self.current = MediaInfo()
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start media polling (Windows only)."""
        if self._running:
            return

        if os.name != "nt":
            logger.info("Media detection only supported on Windows. Skipping.")
            return

        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info("Media manager started")

    def stop(self) -> None:
        """Stop media polling."""
        if not self._running:
            return

        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        logger.info("Media manager stopped")

    def on_error(self, error: Exception) -> None:
        """Handle media detection errors."""
        logger.warning(f"Media detection error: {error}")

    def _poll_loop(self) -> None:
        """Poll Windows Media Control for media info."""
        while self._running:
            try:
                self._update_media_info()
            except Exception as e:
                self.on_error(e)

            time.sleep(MEDIA_POLL_INTERVAL)

    def _update_media_info(self) -> None:
        """Query Windows Media Control and update current media info."""
        try:
            from winsdk.windows.media.control import (
                GlobalSystemMediaTransportControlsSessionManager as MM,
            )

            async def get_media():
                try:
                    mgr = await MM.request_async()
                    session = mgr.get_current_session()

                    if session:
                        props = await session.try_get_media_properties_async()
                        playback = session.get_playback_info()
                        app_id = (session.source_app_user_model_id or "").lower()

                        # Determine media source
                        source = "Media"
                        for app_name, app_key in [
                            ("Spotify", "spotify"),
                            ("Chrome", "chrome"),
                            ("Firefox", "firefox"),
                        ]:
                            if app_key in app_id:
                                source = app_name
                                break

                        # Extract media info
                        media_info = MediaInfo(
                            title=props.title or "",
                            artist=props.artist or "",
                            is_playing=(playback.playback_status == 4),
                            source=source,
                        )

                        with self._lock:
                            self.current = media_info
                    else:
                        with self._lock:
                            self.current = MediaInfo()

                except Exception as e:
                    logger.debug(f"WinSDK media query error: {e}")
                    with self._lock:
                        self.current = MediaInfo()

            # Create and run async event loop
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(get_media())
            finally:
                loop.close()

        except ImportError:
            # WinSDK not available
            logger.debug("WinSDK not available for media detection")

    def get(self) -> MediaInfo:
        """
        Get current media information.

        Returns:
            Copy of current MediaInfo (thread-safe)
        """
        with self._lock:
            return MediaInfo(
                title=self.current.title,
                artist=self.current.artist,
                is_playing=self.current.is_playing,
                source=self.current.source,
            )

    # ═══════════════════════════════════════════════════════════════════════════════
    # Playback Control
    # ═══════════════════════════════════════════════════════════════════════════════

    def play_pause(self) -> None:
        """Toggle play/pause."""
        try:
            pyautogui.press("playpause")
            logger.debug("Play/pause triggered")
        except Exception as e:
            self.on_error(e)

    def next_track(self) -> None:
        """Skip to next track."""
        try:
            pyautogui.press("nexttrack")
            logger.debug("Next track triggered")
        except Exception as e:
            self.on_error(e)

    def prev_track(self) -> None:
        """Go to previous track."""
        try:
            pyautogui.press("prevtrack")
            logger.debug("Previous track triggered")
        except Exception as e:
            self.on_error(e)
