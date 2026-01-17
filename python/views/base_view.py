"""
Base View Class.

Defines the interface that all UI views should implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from PIL import Image

from core.logger import get_logger
from views import View

logger = get_logger("Views")


class BaseView(ABC):
    """
    Abstract base class for all UI views.

    A View is a screen/page in the overlay that:
    - Renders to a PIL Image
    - Handles user input (clicks)
    - Manages view-specific state
    - Can transition to other views

    All views should inherit from this class and implement:
    - render(): Return PIL Image of the view
    - handle_click(): Process user input and optionally return next view

    Example:
        class MainView(BaseView):
            def render(self) -> Image.Image:
                img = Image.new('RGBA', (600, 400), (0,0,0,0))
                # ... draw content
                return img

            def handle_click(self, x: int, y: int) -> Optional[View]:
                if self._is_in_button(x, y):
                    return View.NOTIFICATIONS
                return None
    """

    def __init__(self, view_type: View):
        """
        Initialize view.

        Args:
            view_type: The View enum value for this view
        """
        self.view_type = view_type
        logger.debug(f"View initialized: {view_type}")

    @abstractmethod
    def render(self) -> Image.Image:
        """
        Render the view to an image.

        Returns:
            PIL Image in RGBA mode

        This method should:
        - Create a new RGBA image
        - Draw all UI elements
        - Return the rendered image

        Must be efficient and safe to call frequently.
        """
        pass

    @abstractmethod
    def handle_click(self, x: int, y: int) -> Optional[View]:
        """
        Process a click at coordinates (x, y).

        Args:
            x: X coordinate (0 to view width)
            y: Y coordinate (0 to view height)

        Returns:
            Next view to transition to, or None to stay in current view

        This method should:
        - Check if click is within any interactive elements
        - Perform associated actions (callbacks)
        - Return next view if navigation requested
        - Return None if click was handled but no navigation
        """
        pass

    def get_state(self) -> Dict[str, Any]:
        """
        Get view state for debugging/persistence.

        Returns:
            Dictionary representing view state

        Override this if the view has state to track.
        """
        return {"view": self.view_type.name}

    def update(self, delta_time: float) -> None:
        """
        Update view state (called each frame).

        Args:
            delta_time: Seconds since last update

        Override this if the view needs to update state each frame
        (e.g., timer ticking, animations).
        """
        pass

    def on_enter(self) -> None:
        """
        Called when transitioning to this view.

        Override this to perform initialization when entering the view.
        """
        logger.debug(f"Entering view: {self.view_type}")

    def on_exit(self) -> None:
        """
        Called when transitioning away from this view.

        Override this to perform cleanup when leaving the view.
        """
        logger.debug(f"Exiting view: {self.view_type}")

    def __str__(self) -> str:
        return f"View({self.view_type.name})"
