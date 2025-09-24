"""
Copy to Clipboard module for copying video files to system clipboard.
"""

import tkinter as tk

from ... import theme
from ...utils import copy_files_to_clipboard


class CopyToClipboard:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.preview_window = toolbar.preview_window

    def create_button(self, parent):
        """Create the copy to clipboard button."""
        button = tk.Button(
            parent,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard,
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
            button.config(bg=theme.BTN_ACTIVE_BG)

        def on_leave(e):
            button.config(bg=theme.BTN_BG)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    def copy_to_clipboard(self):
        """Copy the current video file to system clipboard."""
        try:
            current_video = self.toolbar.get_current_video_path()
            copy_files_to_clipboard(current_video)
            self.toolbar.show_success("Video copied to clipboard!")
        except Exception as e:
            self.toolbar.show_error(f"Failed to copy: {e}")
