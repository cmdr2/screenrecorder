import tkinter as tk

from ... import theme
from .save import Save
from .copy_to_clipboard import CopyToClipboard
from .undo import Undo
from .resize_popup import ResizePopup
from .trim_popup import TrimPopup
from .button_utils import StylizedButton


class Toolbar:
    def __init__(self, parent, video_player, video_path, preview_window=None):
        self.parent = parent
        self.video_player = video_player
        self.video_path = video_path
        self.preview_window = preview_window  # Reference to PreviewEditorWindow for toast messages
        self.video_history = [video_path]  # Track video versions for undo
        self.current_video_index = 0

        # Initialize tools
        self.save_tool = Save(self)
        self.copy_tool = CopyToClipboard(self)
        self.undo_tool = Undo(self)

        # Create main toolbar frame
        self.toolbar_frame = tk.Frame(parent, bg=theme.COLOR_BG)
        self.toolbar_frame.pack(fill=tk.X, padx=0, pady=0)

        # Create buttons frame
        self.buttons_frame = tk.Frame(self.toolbar_frame, bg=theme.COLOR_BG)
        self.buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=theme.OVERLAY_PANEL_PADX, pady=theme.OVERLAY_PANEL_PADY)

        # Create operations buttons (Save, Copy to Clipboard, Undo)
        self.operations_frame = tk.Frame(self.buttons_frame, bg=theme.COLOR_BG)
        self.operations_frame.pack(side=tk.LEFT, padx=(0, 20))

        self.save_button = self.save_tool.create_button(self.operations_frame)
        self.save_button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        self.copy_button = self.copy_tool.create_button(self.operations_frame)
        self.copy_button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        self.undo_button = self.undo_tool.create_button(self.operations_frame)
        self.undo_button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        # Create modifiers buttons (Trim, Resize) - now use popups
        self.modifiers_frame = tk.Frame(self.buttons_frame, bg=theme.COLOR_BG)
        self.modifiers_frame.pack(side=tk.LEFT)

        # Create trim button
        self.trim_button = StylizedButton.create_button(
            parent=self.modifiers_frame,
            text="Trim",
            icon_name="cut",
            command=self.open_trim_popup,
            active=False,
        )
        self.trim_button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        # Create resize button
        self.resize_button = StylizedButton.create_button(
            parent=self.modifiers_frame,
            text="Resize",
            icon_name="expand-arrows-alt",
            command=self.open_resize_popup,
            active=False,
        )
        self.resize_button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        # Initialize button states
        self.update_all_button_states()

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
