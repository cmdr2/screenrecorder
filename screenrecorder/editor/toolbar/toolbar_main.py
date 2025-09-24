import tkinter as tk

from ... import theme
from .trim import Trim
from .resize import Resize
from .save import Save
from .copy_to_clipboard import CopyToClipboard


class Toolbar:
    def __init__(self, parent, video_player, video_path, preview_window=None):
        self.parent = parent
        self.video_player = video_player
        self.video_path = video_path
        self.preview_window = preview_window  # Reference to PreviewEditorWindow for toast messages
        self.video_history = [video_path]  # Track video versions for undo
        self.current_video_index = 0

        # State tracking
        self.active_panel = None  # 'trim' or 'resize'

        # Initialize tools
        self.trim_tool = Trim(self)
        self.resize_tool = Resize(self)
        self.save_tool = Save(self)
        self.copy_tool = CopyToClipboard(self)

        # Create main toolbar frame
        self.toolbar_frame = tk.Frame(parent, bg=theme.COLOR_BG)
        self.toolbar_frame.pack(fill=tk.X, padx=0, pady=0)

        # Create buttons frame
        self.buttons_frame = tk.Frame(self.toolbar_frame, bg=theme.COLOR_BG)
        self.buttons_frame.pack(side=tk.TOP, fill=tk.X, padx=theme.PANEL_PADX, pady=theme.PANEL_PADY)

        # Create operations buttons (Save, Copy to Clipboard)
        self.operations_frame = tk.Frame(self.buttons_frame, bg=theme.COLOR_BG)
        self.operations_frame.pack(side=tk.LEFT, padx=(0, 20))

        self.save_button = self.save_tool.create_button(self.operations_frame)
        self.save_button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        self.copy_button = self.copy_tool.create_button(self.operations_frame)
        self.copy_button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        # Create modifiers buttons (Trim, Resize)
        self.modifiers_frame = tk.Frame(self.buttons_frame, bg=theme.COLOR_BG)
        self.modifiers_frame.pack(side=tk.LEFT)

        self.trim_button = self.trim_tool.create_button(self.modifiers_frame)
        self.trim_button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        self.resize_button = self.resize_tool.create_button(self.modifiers_frame)
        self.resize_button.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

        # Create panels frame (hidden by default)
        self.panels_frame = tk.Frame(self.toolbar_frame, bg=theme.COLOR_BG)

        # Initialize panels
        self.trim_panel = self.trim_tool.create_panel(self.panels_frame)
        self.resize_panel = self.resize_tool.create_panel(self.panels_frame)

        # Store button references for state updates
        self.tool_buttons = {
            "trim": self.trim_button,
            "resize": self.resize_button,
        }

    def show_panel(self, panel_name):
        """Show specified panel and hide others."""
        # Hide all panels first
        self.trim_panel.pack_forget()
        self.resize_panel.pack_forget()

        # Show requested panel
        if panel_name == "trim":
            self.trim_panel.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=(0, theme.PANEL_PADY))
        elif panel_name == "resize":
            self.resize_panel.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=(0, theme.PANEL_PADY))

        # Show panels frame if a panel is active
        if panel_name:
            self.panels_frame.pack(fill=tk.X, after=self.buttons_frame)
        else:
            self.panels_frame.pack_forget()

    def update_all_button_states(self):
        """Update visual state of all buttons."""
        # Update modifier buttons based on active panel
        self.trim_tool.update_button_state(self.trim_button)
        self.resize_tool.update_button_state(self.resize_button)

    def add_to_history(self, video_path):
        """Add a new video to the history."""
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
