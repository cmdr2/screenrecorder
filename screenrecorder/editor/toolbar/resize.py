"""
Resize module for video resizing functionality.
"""

import tkinter as tk
import os
import subprocess
import tempfile
import cv2

from ... import theme
from ...utils import get_ffmpeg_path
from ..history import EditHistory
from .button_utils import StylizedButton


class Resize:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.preview_window = toolbar.preview_window
        self.history = EditHistory(toolbar)

        # Initialize resize panel
        self.resize_panel = None
        self.width_var = None
        self.height_var = None
        self.width_entry = None
        self.height_entry = None
        self.apply_button = None
        self.cancel_button = None

        # Video dimensions cache
        self.original_width = None
        self.original_height = None
        self.aspect_ratio = None
        self._updating_dimensions = False  # Flag to prevent infinite loops

    def create_button(self, parent):
        """Create the resize button with FontAwesome icon."""
        return StylizedButton.create_button(
            parent=parent,
            text="Resize",
            icon_name="expand-arrows-alt",
            command=self.toggle_panel,
            active=self.is_active(),
        )

    def is_active(self):
        """Check if this module is currently active."""
        return self.toolbar.active_panel == "resize"

    def update_button_state(self, button):
        """Update button visual state based on active status."""
        StylizedButton.update_button_state(button, self.is_active())

    def toggle_panel(self):
        """Toggle the resize panel visibility."""
        if self.is_active():
            # Close current panel
            self.toolbar.active_panel = None
            self.toolbar.show_panel(None)
        else:
            # Open resize panel
            self.toolbar.active_panel = "resize"
            self.toolbar.show_panel("resize")

        self.toolbar.update_all_button_states()

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

    def create_panel(self, parent):
        """Create the resize panel with controls."""
        self.resize_panel = tk.Frame(
            parent,
            bg=theme.PANEL_BG,
            relief="solid",
            bd=theme.PANEL_BORDER_WIDTH,
            highlightbackground=theme.PANEL_BORDER_COLOR,
            highlightthickness=theme.PANEL_BORDER_WIDTH,
        )

        # Get original video dimensions
        self.original_width, self.original_height = self._get_video_dimensions()

        if self.original_width is None or self.original_height is None:
            # Fallback message if we can't get dimensions
            message_frame = tk.Frame(self.resize_panel, bg=theme.PANEL_BG)
            message_frame.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=theme.PANEL_PADY)

            tk.Label(
                message_frame,
                text="⚠️ Could not get video dimensions",
                bg=theme.PANEL_BG,
                fg=theme.COLOR_TERTIARY,
                font=("Segoe UI", 12, "italic"),
            ).pack()

            return self.resize_panel

        # Calculate aspect ratio
        self.aspect_ratio = self.original_width / self.original_height

        # Controls frame
        controls_frame = tk.Frame(self.resize_panel, bg=theme.PANEL_BG)
        controls_frame.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=theme.PANEL_PADY)

        # Original size label
        original_label = tk.Label(
            controls_frame,
            text=f"Original: {self.original_width} x {self.original_height}",
            bg=theme.PANEL_BG,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 10),
        )
        original_label.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 20))

        # New size frame
        new_size_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        new_size_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            new_size_frame,
            text="New Size:",
            bg=theme.PANEL_BG,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 10),
        ).pack(anchor=tk.W)

        # Dimension inputs
        dimensions_frame = tk.Frame(new_size_frame, bg=theme.PANEL_BG)
        dimensions_frame.pack(anchor=tk.W, pady=(2, 0))

        # Width entry
        self.width_var = tk.StringVar(value=str(self.original_width))
        self.width_entry = tk.Entry(
            dimensions_frame, textvariable=self.width_var, width=6, font=("Segoe UI", 10), justify="center"
        )
        self.width_entry.pack(side=tk.LEFT)

        # X label
        tk.Label(
            dimensions_frame,
            text="×",
            bg=theme.PANEL_BG,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 12, "bold"),
        ).pack(side=tk.LEFT, padx=(5, 5))

        # Height entry
        self.height_var = tk.StringVar(value=str(self.original_height))
        self.height_entry = tk.Entry(
            dimensions_frame, textvariable=self.height_var, width=6, font=("Segoe UI", 10), justify="center"
        )
        self.height_entry.pack(side=tk.LEFT)

        # Buttons frame
        buttons_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        buttons_frame.pack(side=tk.LEFT)

        # Cancel button
        self.cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self.toggle_panel,
            bg=theme.COLOR_TERTIARY,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 10, "bold"),
            relief=theme.BTN_RELIEF,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 8))

        # Resize button
        self.apply_button = tk.Button(
            buttons_frame,
            text="Resize",
            command=self.apply_resize,
            bg=theme.COLOR_PRIMARY,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 10, "bold"),
            relief=theme.BTN_RELIEF,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        self.apply_button.pack(side=tk.LEFT)

        # Bind focus out events for aspect ratio locking and rounding
        self.width_entry.bind("<FocusOut>", self._on_width_focus_out)
        self.height_entry.bind("<FocusOut>", self._on_height_focus_out)

        return self.resize_panel

    def apply_resize(self):
        """Apply video resizing using ffmpeg."""
        try:
            width_str = self.width_var.get().strip()
            height_str = self.height_var.get().strip()

            if not width_str or not height_str:
                self.toolbar.show_error("Please enter valid width and height values")
                return

            new_width = int(width_str)
            new_height = int(height_str)

            # Ensure dimensions are multiples of 2
            new_width = self._ensure_multiple_of_2(new_width)
            new_height = self._ensure_multiple_of_2(new_height)

            # Check if dimensions have actually changed
            if new_width == self.original_width and new_height == self.original_height:
                self.toolbar.show_error("No resize needed - dimensions are the same")
                return

            # Validate minimum dimensions
            if new_width < 2 or new_height < 2:
                self.toolbar.show_error("Dimensions must be at least 2 pixels")
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
                self.toolbar.show_success(f"Video resized to {new_width}x{new_height}")

                # Update original dimensions for further operations
                self.original_width, self.original_height = self._get_video_dimensions()
                self.aspect_ratio = self.original_width / self.original_height

                # Reset inputs to new dimensions
                self.width_var.set(str(self.original_width))
                self.height_var.set(str(self.original_height))
            else:
                self.toolbar.show_error(f"Resize failed: {process.stderr}")
                # Clean up temp file on failure
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except ValueError:
            self.toolbar.show_error("Please enter valid numeric values for dimensions")
        except Exception as e:
            self.toolbar.show_error(f"An error occurred: {str(e)}")
