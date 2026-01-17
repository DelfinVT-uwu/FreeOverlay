"""
Constants and Magic Numbers extracted from the monolithic application.
Centralized configuration for easy tweaking without touching business logic.
"""

from pathlib import Path
from typing import Dict, Tuple

# ═══════════════════════════════════════════════════════════════════════════════
# Application Metadata
# ═══════════════════════════════════════════════════════════════════════════════

APP_NAME = "FreeOverlay"
APP_VERSION = "9.0.0"
APP_AUTHOR = "Dolphin Engineering"
APP_DESCRIPTION = "OpenGL-based VR Overlay with system monitoring, calendar, media control"

# ═══════════════════════════════════════════════════════════════════════════════
# File System
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_DIR = Path.home() / ".freevr_overlay"
CONFIG_FILE = CONFIG_DIR / "config.json"
NOTIFICATIONS_FILE = CONFIG_DIR / "notifs.json"
CALENDAR_FILE = CONFIG_DIR / "calendar.json"

# ═══════════════════════════════════════════════════════════════════════════════
# Overlay UI Dimensions
# ═══════════════════════════════════════════════════════════════════════════════

# Main overlay viewport
OVERLAY_WIDTH = 600
OVERLAY_HEIGHT = 400
OVERLAY_DEPTH_M = 0.20  # Size in meters for 3D positioning

# Popup overlay viewport
POPUP_WIDTH = 700
POPUP_HEIGHT = 550
POPUP_DEPTH_M = 0.55

# Pointer (cursor) overlay
POINTER_WIDTH = 64
POINTER_HEIGHT = 64
POINTER_DEPTH_M = 0.012

# Screen capture overlay
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_DEPTH_M = 1.2

# ═══════════════════════════════════════════════════════════════════════════════
# VR Positioning and Transform
# ═══════════════════════════════════════════════════════════════════════════════

# Main overlay position offset (x, y, z in meters)
MAIN_POSITION_X = 0.0
MAIN_POSITION_Y = 0.05
MAIN_POSITION_Z = 0.02

# Popup overlay position offset (z distance from viewer)
POPUP_POSITION_Z = -0.45

# Screen overlay position offset (further away for context)
SCREEN_POSITION_Z = -1.2

# Overlay sort order (rendering layer)
OVERLAY_MAIN_ORDER = 1
OVERLAY_POPUP_ORDER = 2
OVERLAY_SCREEN_ORDER = 3
OVERLAY_POINTER_ORDER = 100

# ═══════════════════════════════════════════════════════════════════════════════
# Update Intervals (timings in seconds)
# ═══════════════════════════════════════════════════════════════════════════════

# Main state update frequency (system stats, time, etc)
STATE_UPDATE_INTERVAL = 0.1

# Main overlay render frequency
RENDER_UPDATE_INTERVAL = 0.5

# Popup render frequency (high FPS for smoothness)
POPUP_UPDATE_INTERVAL = 0.033  # ~30 FPS

# Screen capture update frequency
SCREEN_UPDATE_INTERVAL = 0.066  # ~15 FPS

# Media detection polling interval
MEDIA_POLL_INTERVAL = 1.5

# Calendar reminder check interval
CALENDAR_REMINDER_INTERVAL = 30

# GPU utilization check interval (nvidia-smi is slow)
GPU_CHECK_INTERVAL = 5

# Main application loop frame rate
APP_LOOP_FRAME_TIME = 0.004  # ~250 FPS internally

# ═══════════════════════════════════════════════════════════════════════════════
# UI Element Sizes
# ═══════════════════════════════════════════════════════════════════════════════

# Button dimensions
BUTTON_WIDTH = 125
BUTTON_HEIGHT = 48
BUTTON_RADIUS = 10

# Keyboard button grid
KEYBOARD_COLS = 10
KEYBOARD_BTN_WIDTH = 52
KEYBOARD_BTN_HEIGHT = 40

# Calendar cell dimensions
CALENDAR_CELL_WIDTH = 90
CALENDAR_CELL_HEIGHT = 55

# Status bar height
NAVBAR_HEIGHT = 65

# Panel border width
PANEL_BORDER_WIDTH = 2
PANEL_BORDER_RADIUS = 18

# ═══════════════════════════════════════════════════════════════════════════════
# Font Sizes
# ═══════════════════════════════════════════════════════════════════════════════

FONT_TITLE_SIZE = 70
FONT_HEADER_SIZE = 16
FONT_LARGE_SIZE = 15
FONT_NORMAL_SIZE = 13
FONT_SMALL_SIZE = 11
FONT_TINY_SIZE = 9
FONT_EMOJI_SIZE = 14

# ═══════════════════════════════════════════════════════════════════════════════
# Text Truncation
# ═══════════════════════════════════════════════════════════════════════════════

MEDIA_TITLE_MAX = 26
MEDIA_ARTIST_MAX = 30
NOTIFICATION_TITLE_MAX = 28
NOTIFICATION_MESSAGE_MAX = 45

# ═══════════════════════════════════════════════════════════════════════════════
# Data Limits
# ═══════════════════════════════════════════════════════════════════════════════

MAX_NOTIFICATIONS = 50
MAX_NOTIFICATIONS_PERSIST = 30
MAX_CALENDAR_EVENTS_DISPLAY = 10
MAX_RECENT_NOTIFS_MAIN = 3
MAX_RECENT_NOTIFS_VIEW = 6
MAX_UPCOMING_EVENTS = 7

# ═══════════════════════════════════════════════════════════════════════════════
# Screen Capture Settings
# ═══════════════════════════════════════════════════════════════════════════════

SCREEN_CAPTURE_WIDTH = 1280
SCREEN_CAPTURE_HEIGHT = 720

# ═══════════════════════════════════════════════════════════════════════════════
# System Monitoring
# ═══════════════════════════════════════════════════════════════════════════════

CPU_USAGE_POLL_INTERVAL = None  # Non-blocking (None means don't wait)
RAM_CHECK_INTERVAL = 1.0
GPU_LOW_THRESHOLD = 10
GPU_HIGH_THRESHOLD = 80
BATTERY_CRITICAL_THRESHOLD = 25

# ═══════════════════════════════════════════════════════════════════════════════
# Paths for Fonts (Platform specific)
# ═══════════════════════════════════════════════════════════════════════════════

FONT_NAME_REGULAR = "arial.ttf"
FONT_NAME_BOLD = "arialbd.ttf"
FONT_NAME_EMOJI = "seguiemj.ttf"

FONT_PATH_LINUX = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ═══════════════════════════════════════════════════════════════════════════════
# GPU Detection Command
# ═══════════════════════════════════════════════════════════════════════════════

GPU_DETECTION_CMD = ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits']
GPU_DETECTION_TIMEOUT = 0.5

# ═══════════════════════════════════════════════════════════════════════════════
# Keyboard for Text Input
# ═══════════════════════════════════════════════════════════════════════════════

KEYBOARD_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ⌫"

# ═══════════════════════════════════════════════════════════════════════════════
# Calendar
# ═══════════════════════════════════════════════════════════════════════════════

CALENDAR_REMINDER_TIME_DEFAULT = "09:00"
CALENDAR_REMINDER_TIME_FORMAT = "%H:%M"
CALENDAR_DATE_FORMAT = "%Y-%m-%d"

# Default calendar event (birthday)
DEFAULT_CALENDAR_EVENTS = [
    {
        "id": "e1",
        "title": "🎂 Cumpleaños",
        "date": "{year}-06-15",  # Will be replaced with current year
        "time_str": "",
        "yearly": True,
        "reminded": False,
    }
]

# ═══════════════════════════════════════════════════════════════════════════════
# Color Themes (Theme definitions)
# ═══════════════════════════════════════════════════════════════════════════════

THEMES: Dict[str, Dict[str, any]] = {
    "cyberpunk": {
        "name": "Cyberpunk",
        "primary": (138, 43, 226),
        "secondary": (0, 191, 255),
        "accent": (255, 0, 128),
        "success": (0, 255, 136),
        "warning": (255, 193, 7),
        "error": (255, 61, 87),
        "text": (255, 255, 255),
        "text_dim": (150, 150, 170),
        "panel": (20, 16, 35, 230),
        "btn": (45, 38, 70),
    },
    "dark": {
        "name": "Oscuro",
        "primary": (100, 100, 100),
        "secondary": (80, 80, 80),
        "accent": (120, 120, 120),
        "success": (100, 200, 100),
        "warning": (200, 180, 80),
        "error": (200, 80, 80),
        "text": (220, 220, 220),
        "text_dim": (120, 120, 120),
        "panel": (15, 15, 15, 245),
        "btn": (35, 35, 35),
    },
    "light": {
        "name": "Claro",
        "primary": (70, 130, 180),
        "secondary": (100, 149, 237),
        "accent": (255, 105, 180),
        "success": (60, 179, 113),
        "warning": (255, 165, 0),
        "error": (220, 20, 60),
        "text": (30, 30, 30),
        "text_dim": (100, 100, 100),
        "panel": (245, 245, 250, 240),
        "btn": (220, 220, 230),
    },
    "neon": {
        "name": "Neon",
        "primary": (255, 0, 255),
        "secondary": (0, 255, 255),
        "accent": (255, 255, 0),
        "success": (0, 255, 0),
        "warning": (255, 165, 0),
        "error": (255, 0, 0),
        "text": (255, 255, 255),
        "text_dim": (200, 200, 200),
        "panel": (10, 0, 20, 220),
        "btn": (30, 0, 50),
    },
    "cyan": {
        "name": "Cyan",
        "primary": (0, 255, 255),
        "secondary": (0, 200, 200),
        "accent": (0, 150, 150),
        "success": (0, 255, 200),
        "warning": (255, 200, 0),
        "error": (255, 100, 100),
        "text": (255, 255, 255),
        "text_dim": (150, 200, 200),
        "panel": (0, 30, 40, 235),
        "btn": (0, 50, 60),
    },
    "matrix": {
        "name": "Matrix",
        "primary": (0, 255, 65),
        "secondary": (0, 200, 50),
        "accent": (0, 150, 40),
        "success": (0, 255, 100),
        "warning": (200, 255, 0),
        "error": (255, 50, 50),
        "text": (0, 255, 65),
        "text_dim": (0, 150, 40),
        "panel": (0, 10, 0, 240),
        "btn": (0, 30, 0),
    },
}

# Default theme on startup
DEFAULT_THEME = "cyberpunk"

# ═══════════════════════════════════════════════════════════════════════════════
# UI View Names (for identification)
# ═══════════════════════════════════════════════════════════════════════════════

VIEW_NAMES = {
    0: "MAIN",
    1: "NOTIFICATIONS",
    2: "CALENDAR",
    3: "SCREENS",
    4: "TIMER",
    5: "CALCULATOR",
    6: "SETTINGS",
    7: "ADD_EVENT",
}

# ═══════════════════════════════════════════════════════════════════════════════
# OpenGL Configuration
# ═══════════════════════════════════════════════════════════════════════════════

GL_WINDOW_WIDTH = 1
GL_WINDOW_HEIGHT = 1
GL_WINDOW_VISIBLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# Logging
# ═══════════════════════════════════════════════════════════════════════════════

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
