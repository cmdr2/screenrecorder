import tkinter as tk
from tkinter import filedialog

from ... import theme, ui
from .resize_popup import ResizePopup
from .trim_popup import TrimPopup
from ...utils import copy_files_to_clipboard

SEPARATOR = {"name": "separator"}


class Toolbar:
    def __init__(self, parent, history, video_player, video_path, preview_window=None):
        self.parent = parent
        self.history = history
        self.video_player = video_player
        self.video_path = video_path
        self.preview_window = preview_window  # Reference to PreviewEditorWindow for toast messages
        self.video_history = [video_path]  # Track video versions for undo
        self.current_video_index = 0

        self.menu = [
            {
                "save": {"name": "Save", "icon": "save", "command": self.save_file},
                "copy": {"name": "Copy", "icon": "copy", "command": self.copy_to_clipboard},
                "undo": {"name": "Undo", "icon": "undo", "command": self.perform_undo, "disabled": True},
            },
            {
                "trim": {"name": "Trim", "icon": "cut", "command": self.open_trim_popup},
                "resize": {"name": "Resize", "icon": "expand-arrows-alt", "command": self.open_resize_popup},
            },
        ]

        # Create main toolbar frame
        toolbar_frame = tk.Frame(parent, bg=theme.COLOR_BG)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=theme.OVERLAY_PANEL_PADX, pady=theme.OVERLAY_PANEL_PADY)

        for group in self.menu:
            frame = tk.Frame(toolbar_frame, bg=theme.COLOR_BG)
            frame.pack(side=tk.LEFT, padx=(0, 20))

            for id, item in group.items():
                btn = ui.Button(
                    parent=frame,
                    text=item["name"],
                    icon_name=item["icon"],
                    command=item["command"],
                    hover_highlight=True,
                )
                if item.get("disabled", False):
                    btn.config(state=tk.DISABLED)

                btn.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

                item["button"] = btn  # Store button reference for state updates

        self.history.add_event_listener("change", self.update_undo_button_state)

    def save_file(self):
        """Save the current video to a file."""
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")], title="Save video as..."
        )
        if save_path:
            try:
                current_video = self.get_current_video_path()
                with open(current_video, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                self.show_success(f"Saved to {save_path}")
            except Exception as e:
                self.show_error(f"Failed to save: {e}")

    def copy_to_clipboard(self):
        """Copy the current video file to system clipboard."""
        try:
            current_video = self.get_current_video_path()
            copy_files_to_clipboard(current_video)
            self.show_success("Video copied to clipboard!")
        except Exception as e:
            self.show_error(f"Failed to copy: {e}")

    def perform_undo(self):
        self.history.undo()
        self.show_success("Undo successful!")

    def update_undo_button_state(self, new_value):
        button = self.menu[0]["undo"]["button"]
        if self.history.can_undo():
            button.config(state=tk.NORMAL)
        else:
            button.config(state=tk.DISABLED)

    def open_trim_popup(self):
        """Open the trim popup window."""
        popup = TrimPopup(self.parent, self)
        result = popup.show()
        # Popup handles the actual trimming and provides feedback

    def open_resize_popup(self):
        """Open the resize popup window."""
        popup = ResizePopup(self.parent, self)
        result = popup.show()
        # Popup handles the actual resizing and provides feedback

    def update_all_button_states(self):
        """Update visual state of all buttons."""
        # Update undo button state
        self.undo_tool.update_button_state(self.undo_button)

    def add_to_history(self, video_path):
        """Add a new video to the history (deprecated - use EditHistory instead)."""
        # This method is kept for backward compatibility
        # Remove any history after current index (if user undid and then made new changes)
        self.video_history = self.video_history[: self.current_video_index + 1]

        # Add new video
        self.video_history.append(video_path)
        self.current_video_index += 1

    def show_error(self, message):
        """Show error message to user."""
        if self.preview_window and hasattr(self.preview_window, "show_toast"):
            self.preview_window.show_toast(f"ERROR: {message}")
        else:
            print(f"Error: {message}")

    def show_success(self, message):
        """Show success message to user."""
        if self.preview_window and hasattr(self.preview_window, "show_toast"):
            self.preview_window.show_toast(f"SUCCESS: {message}")
        else:
            print(f"Success: {message}")

    def get_current_video_path(self):
        """Get the path of the currently active video."""
        return self.video_history[self.current_video_index]
