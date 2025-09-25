"""
Centralized theme and styling constants for the screenrecorder application.

This module defines all visual styling including colors, fonts, spacing,
and component-specific styling to ensure consistent appearance across
all UI elements.
"""

# Base Color Palette
COLOR_BG = "#23272f"  # Main background - dark blue-gray
COLOR_FG = "#ffffff"  # Main foreground/text - white
COLOR_BORDER = "#3a3f4b"  # Border color - medium gray
COLOR_PRIMARY = "#3498db"  # Primary accent - blue
COLOR_SECONDARY = "#e74c3c"  # Secondary accent - red
COLOR_TERTIARY = "#888888"  # Tertiary accent - gray
INPUT_COLOR_BG = "#2c313c"  # Input background - slightly lighter than main bg
INPUT_COLOR_FG = COLOR_FG  # Input text color

# Typography
FONT_FAMILY = "Segoe UI"
FONT_SIZE_NORMAL = 10
FONT_SIZE_BUTTON = 12

# Font tuples for tkinter
FONT_NORMAL = (FONT_FAMILY, FONT_SIZE_NORMAL, "normal")
FONT_BOLD = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_ITALIC = (FONT_FAMILY, FONT_SIZE_NORMAL, "italic")

# Overlay Panel
OVERLAY_PANEL_BG = COLOR_BG
OVERLAY_PANEL_BORDER_COLOR = COLOR_BORDER
OVERLAY_PANEL_BORDER_WIDTH = 1
OVERLAY_PANEL_PADX = 10
OVERLAY_PANEL_PADY = 5

# Drag Icon
DRAG_ICON_COLOR = COLOR_TERTIARY
DRAG_ICON_SIZE = 22
DRAG_ICON_BG = COLOR_BG
DRAG_ICON_PADX = (8, 0)
DRAG_ICON_PADY = 6

# Button Styling
BTN_BG = INPUT_COLOR_BG
BTN_FG = INPUT_COLOR_FG
BTN_ACTIVE_BG = "#404d66"  # Active button background
BTN_ACTIVE_FG = COLOR_FG  # Active button text
BTN_HOVER_BG = "#374151"  # Hover button background
BTN_BORDER_COLOR = COLOR_BORDER
BTN_BORDER_WIDTH = 0
BTN_PADX = 12
BTN_PADY = 6
BTN_FONT = (FONT_FAMILY, FONT_SIZE_BUTTON, "normal")
BTN_RELIEF = "flat"
BTN_PACK_PADX = 8

# Textbox Styling
TEXTBOX_BG = INPUT_COLOR_BG
TEXTBOX_FG = INPUT_COLOR_FG
TEXTBOX_FONT = FONT_NORMAL
TEXTBOX_BORDER_COLOR = COLOR_BORDER
TEXTBOX_BORDER_WIDTH = 1
TEXTBOX_HIGHLIGHT_COLOR = COLOR_PRIMARY

# Icon Styling
RECORD_ICON_COLOR = COLOR_SECONDARY  # Red for recording
STOP_ICON_COLOR = COLOR_SECONDARY  # Red for stop
REGION_ICON_COLOR = COLOR_PRIMARY  # Blue for region selection
ICON_SIZE = 18

# Toast styling
TOAST_BG = COLOR_BG
TOAST_FG = COLOR_FG
TOAST_FONT = ("Segoe UI", 12)
TOAST_BORDER_COLOR = COLOR_BORDER
TOAST_BORDER_WIDTH = 1
TOAST_PADX = 16
TOAST_PADY = 8
