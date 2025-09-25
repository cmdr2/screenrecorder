"""
UI component factory for creating consistent UI elements.

This module provides factory functions to create common UI components
with consistent styling and behavior, reducing code duplication.
"""

import tkinter as tk
from tkfontawesome import icon_to_image
from . import theme


class ButtonFactory:
    """Factory for creating styled buttons with consistent appearance."""

    @staticmethod
    def create_icon_button(parent, text, icon_name, command, **kwargs):
        """
        Create a button with icon and text using theme styling.

        Args:
            parent: Parent widget
            text: Button text
            icon_name: FontAwesome icon name
            command: Button callback function
            **kwargs: Additional button configuration options

        Returns:
            tk.Button: Configured button widget
        """
        # Create icon
        icon_color = kwargs.pop("icon_color", theme.BTN_FG)
        icon_size = kwargs.pop("icon_size", theme.ICON_SIZE)
        icon_img = icon_to_image(icon_name, fill=icon_color, scale_to_width=icon_size)

        # Default button configuration
        default_config = {
            "text": text,
            "image": icon_img,
            "compound": "left",
            "command": command,
            "font": theme.BTN_FONT,
            "bg": theme.BTN_BG,
            "fg": theme.BTN_FG,
            "activebackground": theme.BTN_ACTIVE_BG,
            "activeforeground": theme.BTN_ACTIVE_FG,
            "bd": theme.BTN_BORDER_WIDTH,
            "relief": theme.BTN_RELIEF,
            "highlightbackground": theme.BTN_BORDER_COLOR,
            "highlightcolor": theme.BTN_BORDER_COLOR,
            "highlightthickness": theme.BTN_BORDER_WIDTH,
            "padx": theme.BTN_PADX,
            "pady": theme.BTN_PADY,
            "cursor": "hand2",
        }

        # Override with provided kwargs
        default_config.update(kwargs)

        button = tk.Button(parent, **default_config)
        button.image = icon_img  # Keep reference to prevent garbage collection

        return button

    @staticmethod
    def create_drag_handle(parent, **kwargs):
        """
        Create a drag handle icon for moveable panels.

        Args:
            parent: Parent widget
            **kwargs: Additional label configuration options

        Returns:
            tk.Label: Configured drag handle widget
        """
        drag_img = icon_to_image("grip-vertical", fill=theme.DRAG_ICON_COLOR, scale_to_width=theme.DRAG_ICON_SIZE // 2)

        default_config = {
            "image": drag_img,
            "bg": theme.DRAG_ICON_BG,
            "width": 32,
            "height": 32,
            "bd": 0,
            "highlightbackground": theme.OVERLAY_PANEL_BORDER_COLOR,
            "highlightthickness": 0,
            "cursor": "fleur",
        }

        default_config.update(kwargs)

        drag_handle = tk.Label(parent, **default_config)
        drag_handle.image = drag_img  # Keep reference

        return drag_handle


class FrameFactory:
    """Factory for creating styled frames with consistent appearance."""

    @staticmethod
    def create_themed_frame(parent, **kwargs):
        """
        Create a frame with theme background color.

        Args:
            parent: Parent widget
            **kwargs: Additional frame configuration options

        Returns:
            tk.Frame: Configured frame widget
        """
        default_config = {"bg": theme.COLOR_BG}
        default_config.update(kwargs)

        return tk.Frame(parent, **default_config)
