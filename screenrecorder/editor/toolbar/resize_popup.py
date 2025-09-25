"""
Resize popup window for video resizing functionality.
"""

import tkinter as tk
import os
import subprocess
import tempfile
import cv2

from ... import theme
from ... import ui_factory
from ...utils import get_ffmpeg_path
from ..history import EditHistory
from .popup_base import ToolPopup


class ResizePopup(ToolPopup):
    """Popup window for resizing videos."""

    def __init__(self, parent, toolbar):
        """Initialize the resize popup."""
        super().__init__(parent, "Resize Video", "Resize")
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.history = EditHistory(toolbar)

        # UI components
        self.width_var = None
        self.height_var = None
        self.width_entry = None
        self.height_entry = None

        # Video dimensions cache
        self.original_width = None
        self.original_height = None
        self.aspect_ratio = None
        self._updating_dimensions = False  # Flag to prevent infinite loops

    def create_content(self):
        """Create the resize popup content."""
        # Get original video dimensions
        self.original_width, self.original_height = self._get_video_dimensions()

        if self.original_width is None or self.original_height is None:
            # Show error message if we can't get dimensions
            error_label = tk.Label(
                self.content_frame,
                text="⚠️ Could not get video dimensions",
                bg=theme.COLOR_BG,
                fg=theme.COLOR_TERTIARY,
                font=theme.FONT_ITALIC,
            )
            error_label.pack(pady=20)

            # Disable action button
            self.action_button.config(state="disabled")
            return

        # Calculate aspect ratio
        self.aspect_ratio = self.original_width / self.original_height

        # Original size display
        original_frame = tk.Frame(self.content_frame, bg=theme.COLOR_BG)
        original_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            original_frame,
            text="Original Size:",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_FG,
            font=theme.FONT_BOLD,
        ).pack(side=tk.LEFT)

        tk.Label(
            original_frame,
            text=f"{self.original_width} × {self.original_height}",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_FG,
            font=theme.FONT_NORMAL,
        ).pack(side=tk.LEFT, padx=(10, 0))

        # New size frame
        new_size_frame = tk.Frame(self.content_frame, bg=theme.COLOR_BG)
        new_size_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            new_size_frame,
            text="New Size:",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_FG,
            font=theme.FONT_BOLD,
        ).pack(anchor=tk.W)

        # Dimension inputs frame
        dimensions_frame = tk.Frame(new_size_frame, bg=theme.COLOR_BG)
        dimensions_frame.pack(anchor=tk.W, pady=(5, 0))

        # Width entry
        tk.Label(
            dimensions_frame,
            text="Width:",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_FG,
            font=theme.FONT_NORMAL,
        ).pack(side=tk.LEFT)

        self.width_var = tk.StringVar(value=str(self.original_width))
        self.width_entry = ui_factory.Textbox(dimensions_frame, textvariable=self.width_var, width=8)
        self.width_entry.pack(side=tk.LEFT, padx=(5, 15))

        # X label
        tk.Label(
            dimensions_frame,
            text="×",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_FG,
            font=theme.FONT_BOLD,
        ).pack(side=tk.LEFT, padx=(0, 15))

        # Height entry
        tk.Label(
            dimensions_frame,
            text="Height:",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_FG,
            font=theme.FONT_NORMAL,
        ).pack(side=tk.LEFT)

        self.height_var = tk.StringVar(value=str(self.original_height))
        self.height_entry = ui_factory.Textbox(dimensions_frame, textvariable=self.height_var, width=8)
        self.height_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Bind focus out events for aspect ratio locking and rounding
        self.width_entry.bind("<FocusOut>", self._on_width_focus_out)
        self.height_entry.bind("<FocusOut>", self._on_height_focus_out)

        # Set focus to width entry
        self.width_entry.focus_set()

    def _get_video_dimensions(self):
        """Get the original video dimensions using OpenCV."""
        try:
            current_video = self.history.get_current_video_path()
            cap = cv2.VideoCapture(current_video)

            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()

                # Ensure dimensions are multiples of 2
                width = width + (width % 2)
                height = height + (height % 2)

                return width, height
            else:
                cap.release()
                return None, None
        except Exception as e:
            print(f"Error getting video dimensions: {e}")
            return None, None

    def _ensure_multiple_of_2(self, value):
        """Ensure a value is a multiple of 2."""
        return value + (value % 2)

    def _update_width_from_height(self, height):
        """Update width based on height while maintaining aspect ratio."""
        if self.aspect_ratio and not self._updating_dimensions:
            self._updating_dimensions = True
            new_width = self._ensure_multiple_of_2(int(height * self.aspect_ratio))
            self.width_var.set(str(new_width))
            self._updating_dimensions = False

    def _update_height_from_width(self, width):
        """Update height based on width while maintaining aspect ratio."""
        if self.aspect_ratio and not self._updating_dimensions:
            self._updating_dimensions = True
            new_height = self._ensure_multiple_of_2(int(width / self.aspect_ratio))
            self.height_var.set(str(new_height))
            self._updating_dimensions = False

    def _on_width_focus_out(self, event):
        """Handle width entry losing focus - apply rounding and aspect ratio locking."""
        try:
            if self._updating_dimensions:
                return
            width_str = self.width_var.get().strip()
            if width_str:
                width = int(width_str)
                # Ensure multiple of 2
                width = self._ensure_multiple_of_2(width)
                self.width_var.set(str(width))
                # Update height proportionally
                self._update_height_from_width(width)
        except ValueError:
            # Reset to original width if invalid input
            self.width_var.set(str(self.original_width))

    def _on_height_focus_out(self, event):
        """Handle height entry losing focus - apply rounding and aspect ratio locking."""
        try:
            if self._updating_dimensions:
                return
            height_str = self.height_var.get().strip()
            if height_str:
                height = int(height_str)
                # Ensure multiple of 2
                height = self._ensure_multiple_of_2(height)
                self.height_var.set(str(height))
                # Update width proportionally
                self._update_width_from_height(height)
        except ValueError:
            # Reset to original height if invalid input
            self.height_var.set(str(self.original_height))

    def apply_action(self):
        """Apply video resizing using ffmpeg."""
        try:
            width_str = self.width_var.get().strip()
            height_str = self.height_var.get().strip()

            if not width_str or not height_str:
                self.show_error("Please enter valid width and height values")
                return

            new_width = int(width_str)
            new_height = int(height_str)

            # Ensure dimensions are multiples of 2
            new_width = self._ensure_multiple_of_2(new_width)
            new_height = self._ensure_multiple_of_2(new_height)

            # Check if dimensions have actually changed
            if new_width == self.original_width and new_height == self.original_height:
                self.show_error("No resize needed - dimensions are the same")
                return

            # Validate minimum dimensions
            if new_width < 2 or new_height < 2:
                self.show_error("Dimensions must be at least 2 pixels")
                return

            # Create temporary file for resized video
            temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
            os.close(temp_fd)

            # Build ffmpeg command
            current_video = self.history.get_current_video_path()
            ffmpeg_path = get_ffmpeg_path()

            cmd = [
                ffmpeg_path,
                "-i",
                current_video,
                "-vf",
                f"scale={new_width}:{new_height}",
                "-c:a",
                "copy",  # Copy audio without re-encoding
                "-y",  # Overwrite output file
                temp_path,
            ]

            # Execute ffmpeg command
            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode == 0:
                # Success - update video player and history
                self.history.add_to_history(temp_path)
                self.video_player.src = temp_path
                self.toolbar.show_success(f"Video resized to {new_width}×{new_height}")

                # Close popup with success result
                self.close_with_result("success")
            else:
                self.show_error(f"Resize failed: {process.stderr}")
                # Clean up temp file on failure
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except ValueError:
            self.show_error("Please enter valid numeric values for dimensions")
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")
