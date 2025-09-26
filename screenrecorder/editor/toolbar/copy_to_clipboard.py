"""
Copy to Clipboard module for copying video files to system clipboard.
"""

from ... import ui
from ...utils import copy_files_to_clipboard


class CopyToClipboard:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.preview_window = toolbar.preview_window

    def create_button(self, parent):
        """Create the copy to clipboard button with FontAwesome icon."""
        return ui.Button(
            parent=parent, text="Copy", icon_name="copy", command=self.copy_to_clipboard, hover_highlight=True
        )

    def copy_to_clipboard(self):
        """Copy the current video file to system clipboard."""
        try:
            current_video = self.toolbar.get_current_video_path()
            copy_files_to_clipboard(current_video)
            self.toolbar.show_success("Video copied to clipboard!")
        except Exception as e:
            self.toolbar.show_error(f"Failed to copy: {e}")
