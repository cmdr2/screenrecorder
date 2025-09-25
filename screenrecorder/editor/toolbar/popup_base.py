"""
Base popup window component for toolbar tools.
Provides a reusable popup window with common layout and button handling.
"""

import tkinter as tk
from tkinter import ttk
from ... import theme


class ToolPopup:
    """Base class for tool popup windows."""

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
        self.result = None  # To store the result when popup is closed

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
        self.popup_window.protocol("WM_DELETE_WINDOW", self.cancel)

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
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        # Center the buttons in the frame
        buttons_frame.grid_columnconfigure(0, weight=1)
        btns_inner = tk.Frame(buttons_frame, bg=theme.COLOR_BG)
        btns_inner.grid(row=0, column=0)

        # Action button
        self.action_button = tk.Button(
            btns_inner,
            text=self.action_text,
            command=self.apply_action,
            bg=theme.COLOR_PRIMARY,
            fg=theme.COLOR_FG,
            font=theme.FONT_BOLD,
            relief=theme.BTN_RELIEF,
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        self.action_button.pack(side=tk.LEFT, padx=(0, 10))

        # Cancel button
        self.cancel_button = tk.Button(
            btns_inner,
            text="Cancel",
            command=self.cancel,
            bg=theme.COLOR_TERTIARY,
            fg=theme.COLOR_FG,
            font=theme.FONT_BOLD,
            relief=theme.BTN_RELIEF,
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
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
        self.popup_window.bind("<Return>", lambda e: self.apply_action())
        self.popup_window.bind("<Escape>", lambda e: self.cancel())

        # Wait for window to close
        self.popup_window.wait_window()

        return self.result

    def _center_on_parent(self):
        """Center the popup window on the parent window."""
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

    def apply_action(self):
        """Override this method in subclasses to handle the action button."""
        raise NotImplementedError("Subclasses must implement apply_action()")

    def cancel(self):
        """Handle cancel button or window close."""
        self.result = None
        self.popup_window.destroy()

    def close_with_result(self, result):
        """Close the popup with a result."""
        self.result = result
        self.popup_window.destroy()

    def show_error(self, message):
        """Show error message in the popup."""
        # Create a temporary label to show error
        if hasattr(self, "error_label"):
            self.error_label.destroy()

        self.error_label = tk.Label(
            self.content_frame,
            text=f"⚠️ {message}",
            bg=theme.COLOR_BG,
            fg="#ff6b6b",  # Red color for errors
            font=theme.FONT_ITALIC,
            wraplength=300,
        )
        self.error_label.pack(pady=(5, 0))

        # Auto-hide error after 3 seconds
        self.popup_window.after(3000, self._hide_error)

    def _hide_error(self):
        """Hide the error message."""
        if hasattr(self, "error_label"):
            self.error_label.destroy()
            delattr(self, "error_label")
