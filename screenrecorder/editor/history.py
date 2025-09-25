"""
History module for managing video editing operations with Apply/Undo functionality.
This module provides a shared history system that can be used by all toolbar tools.
"""

import tkinter as tk
from .. import theme


class EditHistory:
    """
    Manages the history of video edits for undo functionality.
    Each toolbar tool can use this to maintain a consistent undo system.
    """

    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.preview_window = toolbar.preview_window

    def add_to_history(self, video_path):
        """Add a new video to the history."""
        # Remove any history after current index (if user undid and then made new changes)
        self.toolbar.video_history = self.toolbar.video_history[: self.toolbar.current_video_index + 1]

        # Add new video
        self.toolbar.video_history.append(video_path)
        self.toolbar.current_video_index += 1

        # Update undo button state in toolbar
        if hasattr(self.toolbar, "undo_tool") and hasattr(self.toolbar, "undo_button"):
            self.toolbar.undo_tool.update_button_state(self.toolbar.undo_button)

    def can_undo(self):
        """Check if undo operation is possible."""
        return self.toolbar.current_video_index > 0

    def undo(self):
        """Undo the last operation."""
        if self.can_undo():
            self.toolbar.current_video_index -= 1
            previous_video = self.toolbar.video_history[self.toolbar.current_video_index]
            self.video_player.src = previous_video
            self.toolbar.show_success("Undo successful!")

            # Update undo button state in toolbar
            if hasattr(self.toolbar, "undo_tool") and hasattr(self.toolbar, "undo_button"):
                self.toolbar.undo_tool.update_button_state(self.toolbar.undo_button)

            return True
        return False

    def get_current_video_path(self):
        """Get the path of the currently active video."""
        return self.toolbar.video_history[self.toolbar.current_video_index]

    def create_undo_button(self, parent, command_callback=None):
        """
        Create a standardized undo button that can be used by any tool.

        Args:
            parent: The parent widget to attach the button to
            command_callback: Optional callback to run after undo (for tool-specific cleanup)
        """

        def undo_command():
            success = self.undo()
            if success and command_callback:
                command_callback()

        undo_button = tk.Button(
            parent,
            text="Undo",
            command=undo_command,
            bg=theme.COLOR_TERTIARY,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 10, "bold"),
            relief=theme.BTN_RELIEF,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
        )

        return undo_button

    def update_undo_button_state(self, button):
        """Enable/disable undo button based on history."""
        if button and button.winfo_exists():
            if self.can_undo():
                button.config(state=tk.NORMAL, bg=theme.COLOR_TERTIARY)
            else:
                button.config(state=tk.DISABLED, bg="#555")
