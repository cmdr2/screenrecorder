"""
Enhanced button utilities for creating stylish toolbar buttons with FontAwesome icons.
"""

import tkinter as tk
from tkfontawesome import icon_to_image
from ... import theme


class StylizedButton:
    """Factory for creating stylized buttons with FontAwesome icons and rounded appearance."""

    @staticmethod
    def create_button(parent, text, icon_name, command, active=False):
        """
        Create a stylized button with FontAwesome icon.

        Args:
            parent: Parent widget
            text: Button text
            icon_name: FontAwesome icon name (e.g., 'save', 'copy', 'cut', 'expand-arrows-alt')
            command: Callback function
            active: Whether button is in active state

        Returns:
            tk.Button: Configured button widget
        """
        # Create icon
        icon_color = theme.BTN_FG if not active else theme.COLOR_PRIMARY
        icon_img = icon_to_image(icon_name, fill=icon_color, scale_to_width=16)

        # Create button with enhanced styling for rounded appearance
        button = tk.Button(
            parent,
            text=text,
            image=icon_img,
            compound="left",
            command=command,
            bg=theme.BTN_ACTIVE_BG if active else theme.BTN_BG,
            fg=theme.BTN_ACTIVE_FG if active else theme.BTN_FG,
            font=theme.BTN_FONT,
            relief="flat",
            bd=0,
            padx=theme.BTN_PADX,
            pady=theme.BTN_PADY,
            cursor="hand2",
            # Enhanced styling for modern appearance
            highlightcolor=theme.COLOR_PRIMARY,
            highlightbackground=theme.BTN_BG,
            borderwidth=0,
        )

        # Store icon reference to prevent garbage collection
        button.image = icon_img
        button.icon_name = icon_name  # Store for later updates

        # Enhanced hover effects with smooth transitions and modern styling
        def on_enter(e):
            if not getattr(button, "_active_state", False):
                button.config(bg=theme.BTN_HOVER_BG, relief="flat", highlightbackground=theme.COLOR_PRIMARY)
                # Update icon color on hover
                hover_icon = icon_to_image(icon_name, fill=theme.COLOR_PRIMARY, scale_to_width=16)
                button.config(image=hover_icon)
                button.image = hover_icon

        def on_leave(e):
            if not getattr(button, "_active_state", False):
                button.config(bg=theme.BTN_BG, relief="flat", highlightbackground=theme.BTN_BG)
                # Restore original icon color
                normal_icon = icon_to_image(icon_name, fill=theme.BTN_FG, scale_to_width=16)
                button.config(image=normal_icon)
                button.image = normal_icon

        def on_press(e):
            button.config(bg=theme.BTN_ACTIVE_BG, relief="flat")

        def on_release(e):
            if not getattr(button, "_active_state", False):
                button.config(bg=theme.BTN_HOVER_BG)
            else:
                button.config(bg=theme.BTN_ACTIVE_BG)

        # Bind hover and press events
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<Button-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)

        return button

    @staticmethod
    def update_button_state(button, active=False):
        """
        Update button visual state.

        Args:
            button: Button widget to update
            active: Whether button should be in active state
        """
        button._active_state = active
        icon_name = getattr(button, "icon_name", "circle")

        if active:
            button.config(bg=theme.BTN_ACTIVE_BG, fg=theme.BTN_ACTIVE_FG, relief="flat")
            # Active icon with primary color
            active_icon = icon_to_image(icon_name, fill=theme.COLOR_PRIMARY, scale_to_width=16)
            button.config(image=active_icon)
            button.image = active_icon
        else:
            button.config(bg=theme.BTN_BG, fg=theme.BTN_FG, relief="flat")
            # Normal icon
            normal_icon = icon_to_image(icon_name, fill=theme.BTN_FG, scale_to_width=16)
            button.config(image=normal_icon)
            button.image = normal_icon


# Icon mappings for toolbar buttons
ICON_MAP = {
    "save": "save",  # FontAwesome save icon
    "copy": "copy",  # FontAwesome copy icon
    "trim": "cut",  # FontAwesome scissors/cut icon
    "resize": "expand-arrows-alt",  # FontAwesome expand arrows icon
}
