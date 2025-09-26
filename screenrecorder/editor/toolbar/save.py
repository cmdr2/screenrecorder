"""
Save module for saving video files.
"""

from tkinter import filedialog

from ... import ui


class Save:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.preview_window = toolbar.preview_window

    def create_button(self, parent):
        """Create the save button with FontAwesome icon."""
        return ui.Button(parent=parent, text="Save", icon_name="save", command=self.save_file, hover_highlight=True)

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
