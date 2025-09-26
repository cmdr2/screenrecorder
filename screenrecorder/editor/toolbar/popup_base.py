"""
Base popup window component for toolbar tools.
Provides a reusable popup window with common layout and button handling.
"""

import tkinter as tk
import traceback
from ... import theme
from ... import ui


class ToolPopup:
    def __init__(self, parent, title, action_text="Apply"):
        """
        Initialize the popup window.

        Args:
            parent: Parent window
            title: Window title
            action_text: Text for the action button (e.g., "Resize", "Trim")
        """
        self.parent = parent
        self.title = title
        self.action_text = action_text
        self.popup_window = None

        # Content frame to be populated by subclasses
        self.content_frame = None

    def show(self):
        """Show the popup window centered on the parent."""
        # Create toplevel window
        self.popup_window = tk.Toplevel(self.parent)
        self.popup_window.title(self.title)
        self.popup_window.resizable(False, False)

        # Hide window initially to prevent flickering during positioning
        self.popup_window.withdraw()

        # Configure window styling
        self.popup_window.configure(bg=theme.COLOR_BG)

        # Make window modal
        self.popup_window.transient(self.parent)

        # Handle window close
        self.popup_window.protocol("WM_DELETE_WINDOW", self.close)

        # Create main frame
        main_frame = tk.Frame(self.popup_window, bg=theme.COLOR_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create content frame for subclass to populate
        self.content_frame = tk.Frame(main_frame, bg=theme.COLOR_BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Let subclass populate content
        self.create_content()

        # Create buttons frame
        buttons_frame = tk.Frame(main_frame, bg=theme.COLOR_BG)
        buttons_frame.pack(fill=tk.X)

        # Center the buttons in the frame
        buttons_frame.grid_columnconfigure(0, weight=1)
        btns_inner = tk.Frame(buttons_frame, bg=theme.COLOR_BG)
        btns_inner.grid(row=0, column=0)

        # Action button
        self.action_button = ui.PrimaryButton(
            btns_inner,
            text=self.action_text,
            command=self.do_apply_action,
            font=theme.FONT_BOLD,
            padx=theme.POPUP_BTN_PADX,
            pady=theme.POPUP_BTN_PADY,
        )
        self.action_button.pack(side=tk.LEFT, padx=(0, 10))

        # Cancel button
        self.cancel_button = ui.TertiaryButton(
            btns_inner,
            text="Cancel",
            command=self.close,
            font=theme.FONT_BOLD,
            padx=theme.POPUP_BTN_PADX,
            pady=theme.POPUP_BTN_PADY,
        )
        self.cancel_button.pack(side=tk.LEFT)

        # Center the window on parent
        self._center_on_parent()

        # Now show the window at the correct position
        self.popup_window.deiconify()

        # Set grab and focus after window is visible
        self.popup_window.grab_set()
        self.popup_window.focus_set()

        # Bind Enter and Escape keys
        self.popup_window.bind("<Return>", self.do_apply_action)
        self.popup_window.bind("<Escape>", self.close)

        # Wait for window to close
        self.popup_window.wait_window()

    def close(self):
        """Close the popup window."""
        self.popup_window.destroy()
        self.popup_window = None

    def _center_on_parent(self):
        # Update window to get accurate sizing
        self.popup_window.update_idletasks()

        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        # Get popup window size
        popup_width = self.popup_window.winfo_reqwidth()
        popup_height = self.popup_window.winfo_reqheight()

        # Calculate centered position
        x = parent_x + (parent_width - popup_width) // 2
        y = parent_y + (parent_height - popup_height) // 2

        # Ensure window is not off-screen
        x = max(0, x)
        y = max(0, y)

        self.popup_window.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

    def create_content(self):
        """Override this method in subclasses to create the popup content."""
        raise NotImplementedError("Subclasses must implement create_content()")

    def do_apply_action(self, event=None):
        try:
            self.apply_action()
        except Exception as e:
            traceback.print_exc()
            self.editor.show_error(f"An error occurred: {str(e)}")

        self.close()
