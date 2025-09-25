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
        self.percentage_var = None
        self.percentage_scale = None
        self.resolution_label = None
        self.apply_button = None
        self.undo_button = None

        # Video dimensions cache
        self.original_width = None
        self.original_height = None

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

    def _calculate_new_dimensions(self, percentage):
        """Calculate new dimensions based on percentage, ensuring multiples of 2."""
        if self.original_width is None or self.original_height is None:
            return None, None

        new_width = int(self.original_width * percentage / 100)
        new_height = int(self.original_height * percentage / 100)

        # Ensure dimensions are multiples of 2
        new_width = new_width + (new_width % 2)
        new_height = new_height + (new_height % 2)

        return new_width, new_height

    def _update_resolution_preview(self, percentage=None):
        """Update the resolution preview label."""
        if percentage is None:
            percentage = self.percentage_var.get()

        new_width, new_height = self._calculate_new_dimensions(percentage)

        if new_width and new_height and self.resolution_label:
            text = f"New resolution: {new_width} x {new_height} ({percentage}%)"
            self.resolution_label.config(text=text)

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

        # Controls frame
        controls_frame = tk.Frame(self.resize_panel, bg=theme.PANEL_BG)
        controls_frame.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=theme.PANEL_PADY)

        # Top info frame for original size and preview
        info_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        info_frame.pack(fill=tk.X, padx=(0, 0), pady=(0, 8))

        original_label = tk.Label(
            info_frame,
            text=f"Original: {self.original_width} x {self.original_height}",
            bg=theme.PANEL_BG,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 10),
        )
        original_label.pack(side=tk.LEFT, anchor=tk.N)

        self.resolution_label = tk.Label(
            info_frame,
            text="New resolution: calculating...",
            bg=theme.PANEL_BG,
            fg=theme.COLOR_PRIMARY,
            font=("Segoe UI", 10, "bold"),
        )
        self.resolution_label.pack(side=tk.LEFT, anchor=tk.N, padx=(16, 0))

        # Percentage slider
        slider_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        slider_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            slider_frame, text="Resize percentage:", bg=theme.PANEL_BG, fg=theme.COLOR_FG, font=("Segoe UI", 10)
        ).pack(anchor=tk.W, pady=(5, 0))

        # Percentage variable and slider
        self.percentage_var = tk.IntVar(value=100)
        self.percentage_scale = tk.Scale(
            slider_frame,
            from_=10,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.percentage_var,
            command=lambda val: self._update_resolution_preview(),
            bg=theme.PANEL_BG,
            fg=theme.COLOR_FG,
            highlightbackground=theme.PANEL_BG,
            troughcolor=theme.COLOR_TERTIARY,
            activebackground=theme.COLOR_PRIMARY,
            length=200,
            font=("Segoe UI", 9),
        )
        self.percentage_scale.pack(anchor=tk.W, pady=(2, 0))

        # Buttons frame
        buttons_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        buttons_frame.pack(side=tk.LEFT)

        # Apply button
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
        self.apply_button.pack(side=tk.LEFT, padx=(0, 8))

        # Undo button using history module
        self.undo_button = self.history.create_undo_button(buttons_frame, command_callback=self._after_undo)
        self.undo_button.pack(side=tk.LEFT)

        # Initialize the resolution preview
        self._update_resolution_preview()

        # Update undo button state
        self.history.update_undo_button_state(self.undo_button)

        return self.resize_panel

    def apply_resize(self):
        """Apply video resizing using ffmpeg."""
        try:
            percentage = self.percentage_var.get()

            if percentage == 100:
                self.toolbar.show_error("No resize needed - already at 100%")
                return

            new_width, new_height = self._calculate_new_dimensions(percentage)

            if not new_width or not new_height:
                self.toolbar.show_error("Could not calculate new dimensions")
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
                self.toolbar.show_success(f"Video resized to {new_width}x{new_height} ({percentage}%)")

                # Update original dimensions for further operations
                self.original_width, self.original_height = self._get_video_dimensions()

                # Reset slider to 100% and update preview
                self.percentage_var.set(100)
                self._update_resolution_preview()

                # Update undo button state
                self.history.update_undo_button_state(self.undo_button)
            else:
                self.toolbar.show_error(f"Resize failed: {process.stderr}")
                # Clean up temp file on failure
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except Exception as e:
            self.toolbar.show_error(f"An error occurred: {str(e)}")

    def _after_undo(self):
        """Callback after undo operation - update UI state."""
        # Update original dimensions after undo
        self.original_width, self.original_height = self._get_video_dimensions()

        # Reset slider to 100% and update preview
        if self.percentage_var:
            self.percentage_var.set(100)
            self._update_resolution_preview()

        # Update undo button state
        if self.undo_button:
            self.history.update_undo_button_state(self.undo_button)
