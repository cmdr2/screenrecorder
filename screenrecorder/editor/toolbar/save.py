"""
Save module for saving video files.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from ... import theme


class Save:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.preview_window = toolbar.preview_window

    def create_button(self, parent):
        """Create the save button."""
        button = tk.Button(
            parent,
            text="Save",
            command=self.save_file,
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

    def save_file(self):
        """Save the current video to a file."""
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")], title="Save video as..."
        )
        if save_path:
            try:
                current_video = self.toolbar.get_current_video_path()
                with open(current_video, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                self.toolbar.show_success(f"Saved to {save_path}")
            except Exception as e:
                self.toolbar.show_error(f"Failed to save: {e}")
