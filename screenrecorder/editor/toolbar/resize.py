"""
Resize module for video resizing functionality.
"""

import tkinter as tk

from ... import theme


class Resize:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.preview_window = toolbar.preview_window

        # Initialize resize panel
        self.resize_panel = None

    def create_button(self, parent):
        """Create the resize button."""
        button = tk.Button(
            parent,
            text="Resize",
            command=self.toggle_panel,
            bg=theme.BTN_BG,
            fg=theme.BTN_FG,
            font=theme.BTN_FONT,
            relief=theme.BTN_RELIEF,
            bd=theme.BTN_BORDER_WIDTH,
            padx=theme.BTN_PADX,
            pady=theme.BTN_PADY,
            cursor="hand2",
        )

        # Hover effects
        def on_enter(e):
            if not self.is_active():
                button.config(bg=theme.BTN_ACTIVE_BG)

        def on_leave(e):
            if not self.is_active():
                button.config(bg=theme.BTN_BG)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    def is_active(self):
        """Check if this module is currently active."""
        return self.toolbar.active_panel == "resize"

    def update_button_state(self, button):
        """Update button visual state based on active status."""
        if self.is_active():
            button.config(bg=theme.BTN_ACTIVE_BG, fg=theme.BTN_ACTIVE_FG)
        else:
            button.config(bg=theme.BTN_BG, fg=theme.BTN_FG)

    def toggle_panel(self):
        """Toggle the resize panel visibility."""
        if self.is_active():
            # Close current panel
            self.toolbar.active_panel = None
            self.toolbar.show_panel(None)
        else:
            # Open resize panel
            self.toolbar.active_panel = "resize"
            self.toolbar.show_panel("resize")

        self.toolbar.update_all_button_states()

    def create_panel(self, parent):
        """Create the resize panel placeholder."""
        self.resize_panel = tk.Frame(
            parent,
            bg=theme.PANEL_BG,
            relief="solid",
            bd=theme.PANEL_BORDER_WIDTH,
            highlightbackground=theme.PANEL_BORDER_COLOR,
            highlightthickness=theme.PANEL_BORDER_WIDTH,
        )

        # Coming soon message
        message_frame = tk.Frame(self.resize_panel, bg=theme.PANEL_BG)
        message_frame.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=theme.PANEL_PADY)

        tk.Label(
            message_frame,
            text="🚧 Coming soon...",
            bg=theme.PANEL_BG,
            fg=theme.COLOR_TERTIARY,
            font=("Segoe UI", 12, "italic"),
        ).pack()

        return self.resize_panel
