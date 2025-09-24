"""
Trim module for video trimming functionality.
"""

import tkinter as tk
import os
import subprocess
import tempfile

from ... import theme
from ...utils import get_ffmpeg_path


class Trim:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.preview_window = toolbar.preview_window

        # Initialize trim panel
        self.trim_panel = None
        self.start_time_var = None
        self.start_time_entry = None
        self.end_time_var = None
        self.end_time_entry = None
        self.apply_button = None
        self.undo_button = None

    def create_button(self, parent):
        """Create the trim button."""
        button = tk.Button(
            parent,
            text="Trim",
            command=self.toggle_panel,
            bg=theme.BTN_BG,
            fg=theme.BTN_FG,
            font=theme.BTN_FONT,
            relief=theme.BTN_RELIEF,
            bd=theme.BTN_BORDER_WIDTH,
            padx=theme.BTN_PADX,
            pady=theme.BTN_PADY,
            cursor="hand2",
        )

        # Hover effects
        def on_enter(e):
            if not self.is_active():
                button.config(bg=theme.BTN_ACTIVE_BG)

        def on_leave(e):
            if not self.is_active():
                button.config(bg=theme.BTN_BG)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

        return button

    def is_active(self):
        """Check if this module is currently active."""
        return self.toolbar.active_panel == "trim"

    def update_button_state(self, button):
        """Update button visual state based on active status."""
        if self.is_active():
            button.config(bg=theme.BTN_ACTIVE_BG, fg=theme.BTN_ACTIVE_FG)
        else:
            button.config(bg=theme.BTN_BG, fg=theme.BTN_FG)

    def toggle_panel(self):
        """Toggle the trim panel visibility."""
        if self.is_active():
            # Close current panel
            self.toolbar.active_panel = None
            self.toolbar.show_panel(None)
        else:
            # Open trim panel
            self.toolbar.active_panel = "trim"
            self.toolbar.show_panel("trim")

        self.toolbar.update_all_button_states()

    def create_panel(self, parent):
        """Create the trim panel with controls."""
        self.trim_panel = tk.Frame(
            parent,
            bg=theme.PANEL_BG,
            relief="solid",
            bd=theme.PANEL_BORDER_WIDTH,
            highlightbackground=theme.PANEL_BORDER_COLOR,
            highlightthickness=theme.PANEL_BORDER_WIDTH,
        )

        # Controls frame
        controls_frame = tk.Frame(self.trim_panel, bg=theme.PANEL_BG)
        controls_frame.pack(fill=tk.X, padx=theme.PANEL_PADX, pady=theme.PANEL_PADY)

        # Start time controls
        start_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        start_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            start_frame, text="Start Time (sec):", bg=theme.PANEL_BG, fg=theme.COLOR_FG, font=("Segoe UI", 10)
        ).pack(anchor=tk.W)

        self.start_time_var = tk.StringVar(value="0")
        self.start_time_entry = tk.Entry(start_frame, textvariable=self.start_time_var, width=8, font=("Segoe UI", 10))
        self.start_time_entry.pack(anchor=tk.W, pady=(2, 0))

        # End time controls
        end_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        end_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(end_frame, text="End Time (sec):", bg=theme.PANEL_BG, fg=theme.COLOR_FG, font=("Segoe UI", 10)).pack(
            anchor=tk.W
        )

        # Set end time to current video duration by default
        initial_end_time = self._get_video_duration_str()
        self.end_time_var = tk.StringVar(value=initial_end_time)
        self.end_time_entry = tk.Entry(end_frame, textvariable=self.end_time_var, width=8, font=("Segoe UI", 10))
        self.end_time_entry.pack(anchor=tk.W, pady=(2, 0))

        # Buttons frame
        buttons_frame = tk.Frame(controls_frame, bg=theme.PANEL_BG)
        buttons_frame.pack(side=tk.LEFT)

        # Apply button
        self.apply_button = tk.Button(
            buttons_frame,
            text="Trim",
            command=self.apply_trim,
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

        # Undo button
        self.undo_button = tk.Button(
            buttons_frame,
            text="Undo",
            command=self.undo_trim,
            bg=theme.COLOR_TERTIARY,
            fg=theme.COLOR_FG,
            font=("Segoe UI", 10, "bold"),
            relief=theme.BTN_RELIEF,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
        )
        self.undo_button.pack(side=tk.LEFT)

        # Update undo button state
        self.update_undo_button_state()

        return self.trim_panel

    def apply_trim(self):
        """Apply video trimming using ffmpeg."""
        try:
            start_time = float(self.start_time_var.get() or "0")
            end_time_str = self.end_time_var.get().strip()

            if not end_time_str:
                self.toolbar.show_error("Please enter an end time.")
                return

            end_time = float(end_time_str)

            if start_time >= end_time:
                self.toolbar.show_error("Start time must be less than end time.")
                return

            if start_time < 0:
                self.toolbar.show_error("Start time must be positive.")
                return

            # Create temporary file for trimmed video
            temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
            os.close(temp_fd)

            # Build ffmpeg command
            current_video = self.toolbar.video_history[self.toolbar.current_video_index]
            ffmpeg_path = get_ffmpeg_path()

            duration = end_time - start_time

            cmd = [
                ffmpeg_path,
                "-ss",
                str(start_time),
                "-i",
                current_video,
                "-c",
                "copy",
                "-t",
                str(duration),
                "-y",  # Overwrite output file
                temp_path,
            ]

            # Execute ffmpeg command
            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode == 0:
                # Success - update video player and history
                self.toolbar.add_to_history(temp_path)
                print(temp_path)
                self.video_player.src = temp_path
                self.toolbar.show_success("Video trimmed successfully!")

                # Reset form
                self.start_time_var.set("0")
                # Update end time to new duration
                self.end_time_var.set(self._get_video_duration_str())

                # Update undo button state
                self.update_undo_button_state()
            else:
                self.toolbar.show_error(f"Trimming failed: {process.stderr}")
                # Clean up temp file on failure
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except ValueError:
            self.toolbar.show_error("Please enter valid numeric values for times.")
        except Exception as e:
            self.toolbar.show_error(f"An error occurred: {str(e)}")

    def undo_trim(self):
        """Undo the last trim operation."""
        if self.toolbar.current_video_index > 0:
            self.toolbar.current_video_index -= 1
            previous_video = self.toolbar.video_history[self.toolbar.current_video_index]
            self.video_player.src = previous_video
            # Update end time to previous video's duration
            self.end_time_var.set(self._get_video_duration_str())
            self.toolbar.show_success("Undo successful!")
            self.update_undo_button_state()

    def update_undo_button_state(self):
        """Enable/disable undo button based on history."""
        if hasattr(self, "undo_button") and self.undo_button:
            if self.toolbar.current_video_index > 0:
                self.undo_button.config(state=tk.NORMAL, bg=theme.COLOR_TERTIARY)
            else:
                self.undo_button.config(state=tk.DISABLED, bg="#555")

    def _get_video_duration_str(self):
        """Get the duration of the current video as a string."""
        return str(round(self.video_player.duration, 1))
