# theme.py
# Centralized styling constants for the screenrecorder app

# Common Colors
COLOR_BG = "#23272f"  # Main background
COLOR_FG = "#fff"  # Main foreground/text
COLOR_BORDER = "#3a3f4b"  # Border color
COLOR_PRIMARY = "#3498db"  # Primary accent (blue)
COLOR_SECONDARY = "#e74c3c"  # Secondary accent (red)
COLOR_TERTIARY = "#888"  # Tertiary accent (gray)

FONT_NAME = "Segoe UI"
FONT_SIZE = 10
FONT_NORMAL = (FONT_NAME, FONT_SIZE, "normal")
FONT_BOLD = (FONT_NAME, FONT_SIZE, "bold")
FONT_ITALIC = (FONT_NAME, FONT_SIZE, "italic")

# Panel
PANEL_BG = COLOR_BG
PANEL_BORDER_COLOR = COLOR_BORDER
PANEL_BORDER_WIDTH = 1
PANEL_PADX = 10
PANEL_PADY = 5

# Drag Icon
DRAG_ICON_COLOR = COLOR_TERTIARY
DRAG_ICON_SIZE = 22
DRAG_ICON_BG = COLOR_BG
DRAG_ICON_PADX = (8, 0)
DRAG_ICON_PADY = 6

# Button
BTN_BG = "#2c313c"  # Slightly different for button background
BTN_FG = COLOR_FG
BTN_ACTIVE_BG = "#404d66"  # More prominent active state
BTN_ACTIVE_FG = COLOR_FG
BTN_HOVER_BG = "#374151"  # Subtle hover state
BTN_BORDER_COLOR = COLOR_BORDER
BTN_BORDER_WIDTH = 0
BTN_PADX = 12
BTN_PADY = 6
BTN_FONT = ("Segoe UI", 12, "normal")  # Slightly smaller, cleaner font
BTN_RELIEF = "flat"

# Icon Colors
RECORD_ICON_COLOR = COLOR_SECONDARY
STOP_ICON_COLOR = COLOR_SECONDARY
REGION_ICON_COLOR = COLOR_PRIMARY
ICON_SIZE = 18
BTN_PACK_PADX = 8

# Toast styling
TOAST_BG = COLOR_BG
TOAST_FG = COLOR_FG
TOAST_FONT = ("Segoe UI", 12)
TOAST_BORDER_COLOR = COLOR_BORDER
TOAST_BORDER_WIDTH = 1
TOAST_PADX = 16
TOAST_PADY = 8
