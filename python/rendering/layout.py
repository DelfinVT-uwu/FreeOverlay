"""
Layout Engine Module.

Provides layout calculations for UI elements.
Abstracts away magic numbers for button positions, sizes, etc.
"""

from dataclasses import dataclass
from typing import List, Tuple
from core.constants import (
    OVERLAY_WIDTH,
    OVERLAY_HEIGHT,
    BUTTON_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_RADIUS,
    KEYBOARD_COLS,
    KEYBOARD_BTN_WIDTH,
    KEYBOARD_BTN_HEIGHT,
    CALENDAR_CELL_WIDTH,
    CALENDAR_CELL_HEIGHT,
    NAVBAR_HEIGHT,
    PANEL_BORDER_RADIUS,
)


@dataclass
class Rect:
    """Rectangle with position and size."""

    x: int
    y: int
    w: int
    h: int

    def contains(self, px: int, py: int) -> bool:
        """Check if point is inside rectangle."""
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def center(self) -> Tuple[int, int]:
        """Get center point of rectangle."""
        return (self.x + self.w // 2, self.y + self.h // 2)

    def as_coords(self) -> Tuple[int, int, int, int]:
        """Get as (x1, y1, x2, y2) for PIL."""
        return (self.x, self.y, self.x + self.w, self.y + self.h)


class LayoutEngine:
    """
    Calculates layout for UI elements.

    Centralized layout logic makes UI consistent and easy to modify.
    """

    # ═══════════════════════════════════════════════════════════════════════════════
    # Canvas and Panel Layout
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def get_canvas() -> Rect:
        """Get main canvas/viewport rectangle."""
        return Rect(0, 0, OVERLAY_WIDTH, OVERLAY_HEIGHT)

    @staticmethod
    def get_main_panel() -> Rect:
        """Get main content panel (excluding navbar)."""
        canvas = LayoutEngine.get_canvas()
        return Rect(10, 10, canvas.w - 20, canvas.h - 100)

    @staticmethod
    def get_navbar() -> Rect:
        """Get navigation bar at bottom."""
        return Rect(10, OVERLAY_HEIGHT - NAVBAR_HEIGHT - 10, OVERLAY_WIDTH - 20, NAVBAR_HEIGHT)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Button Layout
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def center_button(y: int) -> Rect:
        """Get centered button rectangle."""
        x = (OVERLAY_WIDTH - BUTTON_WIDTH) // 2
        return Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)

    @staticmethod
    def grid_button(row: int, col: int, row_count: int = 3, col_count: int = 3) -> Rect:
        """
        Get button in grid layout.

        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            row_count: Total rows
            col_count: Total columns

        Returns:
            Button rectangle
        """
        panel = LayoutEngine.get_main_panel()
        btn_w = (panel.w - 40) // col_count
        btn_h = (panel.h - 40) // row_count
        padding = 10

        x = panel.x + padding + col * (btn_w + padding)
        y = panel.y + padding + row * (btn_h + padding)

        return Rect(x, y, btn_w, btn_h)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Navbar Button Layout
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def navbar_buttons(button_count: int) -> List[Rect]:
        """
        Get list of button rectangles for navbar.

        Args:
            button_count: Number of buttons

        Returns:
            List of button rectangles arranged horizontally
        """
        navbar = LayoutEngine.get_navbar()
        total_width = navbar.w
        spacing = 6

        btn_w = (total_width - (button_count - 1) * spacing) // button_count
        btn_h = navbar.h

        buttons = []
        for i in range(button_count):
            x = navbar.x + i * (btn_w + spacing)
            y = navbar.y
            buttons.append(Rect(x, y, btn_w, btn_h))

        return buttons

    # ═══════════════════════════════════════════════════════════════════════════════
    # Keyboard Layout
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def keyboard_buttons(chars: str) -> List[Tuple[Rect, str]]:
        """
        Get keyboard button layout for text input.

        Args:
            chars: String of characters for keyboard

        Returns:
            List of (button_rect, character) tuples
        """
        buttons = []
        x_offset = 20
        y_offset = 175

        for i, char in enumerate(chars):
            col = i % KEYBOARD_COLS
            row = i // KEYBOARD_COLS

            x = x_offset + col * (KEYBOARD_BTN_WIDTH + 4)
            y = y_offset + row * (KEYBOARD_BTN_HEIGHT + 4)

            rect = Rect(x, y, KEYBOARD_BTN_WIDTH, KEYBOARD_BTN_HEIGHT)
            buttons.append((rect, char))

        return buttons

    # ═══════════════════════════════════════════════════════════════════════════════
    # Calendar Layout
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def calendar_cell(row: int, col: int) -> Rect:
        """
        Get calendar cell rectangle.

        Args:
            row: Row in calendar (0=Mon...6=Sun)
            col: Column/day

        Returns:
            Cell rectangle
        """
        x_offset = 65
        y_offset = 112

        x = x_offset + col * (CALENDAR_CELL_WIDTH + 4)
        y = y_offset + row * (CALENDAR_CELL_HEIGHT + 4)

        return Rect(x, y, CALENDAR_CELL_WIDTH, CALENDAR_CELL_HEIGHT)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Information Panels
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def info_panel(row: int, cols: int = 1) -> List[Rect]:
        """
        Get list of information display panels.

        Args:
            row: Panel row index
            cols: Number of columns

        Returns:
            List of panel rectangles
        """
        panel = LayoutEngine.get_main_panel()
        panel_h = (panel.h - 40) // 4

        x_start = panel.x + 10
        y = panel.y + 10 + row * (panel_h + 10)

        panels = []
        for col in range(cols):
            w = (panel.w - 20 - (cols - 1) * 10) // cols
            x = x_start + col * (w + 10)
            panels.append(Rect(x, y, w, panel_h))

        return panels

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Layout
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def list_items(start_y: int, item_height: int, max_items: int) -> List[Rect]:
        """
        Get list item layout.

        Args:
            start_y: Starting Y position
            item_height: Height of each item
            max_items: Maximum items to layout

        Returns:
            List of item rectangles
        """
        items = []
        spacing = 4
        x = 20

        for i in range(max_items):
            y = start_y + i * (item_height + spacing)
            if y + item_height > OVERLAY_HEIGHT - NAVBAR_HEIGHT - 20:
                break

            w = OVERLAY_WIDTH - 40
            items.append(Rect(x, y, w, item_height))

        return items

    # ═══════════════════════════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def center_horizontally(width: int, y: int, height: int) -> Rect:
        """
        Get centered horizontal rectangle.

        Args:
            width: Element width
            y: Y position
            height: Element height

        Returns:
            Centered rectangle
        """
        x = (OVERLAY_WIDTH - width) // 2
        return Rect(x, y, width, height)

    @staticmethod
    def center_vertically(x: int, height: int, width: int) -> Rect:
        """
        Get centered vertical rectangle.

        Args:
            x: X position
            height: Element height
            width: Element width

        Returns:
            Centered rectangle
        """
        y = (OVERLAY_HEIGHT - height) // 2
        return Rect(x, y, width, height)

    @staticmethod
    def center_in_canvas(width: int, height: int) -> Rect:
        """
        Get centered rectangle (both axes).

        Args:
            width: Element width
            height: Element height

        Returns:
            Centered rectangle
        """
        x = (OVERLAY_WIDTH - width) // 2
        y = (OVERLAY_HEIGHT - height) // 2
        return Rect(x, y, width, height)
