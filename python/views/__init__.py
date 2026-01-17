"""FreeOverlay Views Module - UI view components"""

from enum import Enum


class View(Enum):
    """Enumeration of available UI views."""

    MAIN = 0
    NOTIFICATIONS = 1
    CALENDAR = 2
    SCREENS = 3
    TIMER = 4
    CALCULATOR = 5
    SETTINGS = 6
    ADD_EVENT = 7

    def __str__(self):
        return self.name.replace("_", " ")
