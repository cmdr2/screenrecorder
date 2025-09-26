"""
Undo module for global undo functionality across all video editing operations.
"""

import tkinter as tk
from ... import theme, ui
from ..history import EditHistory


class Undo:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.preview_window = toolbar.preview_window
        self.history = EditHistory(toolbar)

    def create_button(self, parent):
        """Create the undo button with FontAwesome icon."""
        button = ui.Button(
            parent=parent, text="Undo", icon_name="undo", command=self.perform_undo, hover_highlight=True
        )

        # Update button state based on history
        self.update_button_state(button)
        return button

    def update_button_state(self, button):
        """Enable/disable undo button based on history."""
        if button and button.winfo_exists():
            if self.history.can_undo():
                button.config(state=tk.NORMAL, bg=theme.BTN_BG, fg=theme.BTN_FG)
            else:
                button.config(state=tk.DISABLED, bg=theme.BTN_BG, fg=theme.BTN_FG)

    def perform_undo(self):
        """Perform undo operation."""
        success = self.history.undo()
        if success:
            # Update button state after undo
            # This will be called by the toolbar to update all relevant UI
            pass
