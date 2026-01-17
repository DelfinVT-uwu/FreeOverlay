"""
Screen Capture Manager Module.

Handles capturing and resizing screen content for display in VR.
"""

from typing import Optional, List
from PIL import Image

from managers.base import Manager
from core.logger import get_logger, ErrorHandler
from core.constants import SCREEN_CAPTURE_WIDTH, SCREEN_CAPTURE_HEIGHT

logger = get_logger("ScreenCaptureManager")


class ScreenCaptureManager(Manager):
    """
    Captures screen content for display in VR overlay.

    Features:
    - Detect available monitors
    - Capture screen to PIL Image
    - Resize to standard dimensions
    - Thread-safe operation
    """

    def __init__(self):
        """Initialize screen capture manager."""
        super().__init__("ScreenCaptureManager")
        self.monitors: List = []
        self._mss = None

    def start(self) -> None:
        """Initialize mss library and detect monitors."""
        if self._running:
            return

        self._running = True
        self._detect_monitors()
        logger.info(f"Screen capture manager started ({len(self.monitors)} monitors)")

    def stop(self) -> None:
        """Clean up screen capture resources."""
        self._running = False
        if self._mss:
            self._mss.close()
        logger.info("Screen capture manager stopped")

    def on_error(self, error: Exception) -> None:
        """Handle screen capture errors."""
        logger.error(f"Screen capture error: {error}")

    def _detect_monitors(self) -> None:
        """Detect available monitors."""
        try:
            import mss

            with mss.mss() as sct:
                # Skip primary display (index 0), use actual monitors
                self.monitors = sct.monitors[1:]
                logger.info(f"Detected {len(self.monitors)} monitor(s)")
        except Exception as e:
            ErrorHandler.handle(e, context="detect_monitors", severity="WARNING")
            self.monitors = []

    def get_monitor_count(self) -> int:
        """Get number of available monitors."""
        return len(self.monitors)

    def capture(self, monitor_idx: int = 0) -> Optional[Image.Image]:
        """
        Capture a monitor and return as PIL Image.

        Args:
            monitor_idx: Index of monitor to capture (0-based)

        Returns:
            PIL Image or None if capture failed
        """
        if not self._running:
            logger.warning("Capture requested but manager not running")
            return None

        if monitor_idx >= len(self.monitors):
            logger.warning(f"Monitor index {monitor_idx} out of range")
            return None

        try:
            import mss

            with mss.mss() as sct:
                # Get the monitor at actual index (mss uses 1-based for monitors)
                monitor_info = sct.monitors[monitor_idx + 1]
                screenshot = sct.grab(monitor_info)

                # Convert to PIL Image
                img = Image.frombytes(
                    "RGB",
                    screenshot.size,
                    screenshot.bgra,
                    "raw",
                    "BGRX",
                )

                # Resize to standard dimensions
                img = img.resize(
                    (SCREEN_CAPTURE_WIDTH, SCREEN_CAPTURE_HEIGHT),
                    Image.Resampling.LANCZOS,
                )

                # Convert to RGBA for consistency
                img = img.convert("RGBA")

                logger.debug(f"Screen capture successful (monitor {monitor_idx})")
                return img

        except Exception as e:
            ErrorHandler.handle(
                e,
                context=f"screen_capture_monitor_{monitor_idx}",
                severity="WARNING",
            )
            return None

    def get_monitor_info(self, idx: int) -> Optional[dict]:
        """
        Get information about a monitor.

        Args:
            idx: Monitor index

        Returns:
            Dictionary with monitor info or None
        """
        if idx >= len(self.monitors):
            return None

        monitor = self.monitors[idx]
        return {
            "index": idx,
            "x": monitor.get("left", 0),
            "y": monitor.get("top", 0),
            "width": monitor.get("width", 0),
            "height": monitor.get("height", 0),
        }
