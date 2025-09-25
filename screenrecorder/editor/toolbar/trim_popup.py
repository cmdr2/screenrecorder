"""
Trim popup window for video trimming functionality.
"""

import tkinter as tk
import os
import subprocess
import tempfile

from ... import theme
from ...utils import get_ffmpeg_path
from ..history import EditHistory
from .popup_base import ToolPopup


class TrimPopup(ToolPopup):
    """Popup window for trimming videos."""

    def __init__(self, parent, toolbar):
        """Initialize the trim popup."""
        super().__init__(parent, "Trim Video", "Trim")
        self.toolbar = toolbar
        self.video_player = toolbar.video_player
        self.history = EditHistory(toolbar)

        # UI components
        self.start_time_var = None
        self.start_time_entry = None
        self.end_time_var = None
        self.end_time_entry = None

    def create_content(self):
        """Create the trim popup content."""
        # Get video duration
        video_duration = self._get_video_duration()

        # Instructions
        instructions_label = tk.Label(
            self.content_frame,
            text="Set the start and end times to trim your video (in seconds)",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_FG,
            font=theme.FONT_NORMAL,
        )
        instructions_label.pack(pady=(0, 15))

        # Time inputs frame
        times_frame = tk.Frame(self.content_frame, bg=theme.COLOR_BG)
        times_frame.pack(fill=tk.X, pady=(0, 10))

        # Start time (single row)
        start_row = tk.Frame(times_frame, bg=theme.COLOR_BG)
        start_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            start_row,
            text="Start Time",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_FG,
            font=theme.FONT_BOLD,
            width=12,
            anchor="w",
        ).pack(side=tk.LEFT)

        self.start_time_var = tk.StringVar(value="0.0")
        self.start_time_entry = tk.Entry(
            start_row, textvariable=self.start_time_var, width=10, font=theme.FONT_NORMAL, justify="center"
        )
        self.start_time_entry.pack(side=tk.LEFT, padx=(10, 0))

        tk.Label(
            start_row,
            text="sec",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_TERTIARY,
            font=theme.FONT_NORMAL,
        ).pack(side=tk.LEFT, padx=(5, 0))

        # End time (single row)
        end_row = tk.Frame(times_frame, bg=theme.COLOR_BG)
        end_row.pack(fill=tk.X)

        tk.Label(
            end_row,
            text="End Time",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_FG,
            font=theme.FONT_BOLD,
            width=12,
            anchor="w",
        ).pack(side=tk.LEFT)

        self.end_time_var = tk.StringVar(value=f"{video_duration:.1f}")
        self.end_time_entry = tk.Entry(
            end_row, textvariable=self.end_time_var, width=10, font=theme.FONT_NORMAL, justify="center"
        )
        self.end_time_entry.pack(side=tk.LEFT, padx=(10, 0))

        tk.Label(
            end_row,
            text="sec",
            bg=theme.COLOR_BG,
            fg=theme.COLOR_TERTIARY,
            font=theme.FONT_NORMAL,
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Set focus to start time entry
        self.start_time_entry.focus_set()

        # Select all text in start time entry for easy editing
        self.start_time_entry.select_range(0, tk.END)

    def _get_video_duration(self):
        """Get the duration of the current video."""
        try:
            return round(self.video_player.duration, 1)
        except:
            return 0.0

    def apply_action(self):
        """Apply video trimming using ffmpeg."""
        try:
            start_time_str = self.start_time_var.get().strip()
            end_time_str = self.end_time_var.get().strip()

            if not start_time_str or not end_time_str:
                self.show_error("Please enter valid start and end times")
                return

            start_time = float(start_time_str)
            end_time = float(end_time_str)

            if start_time >= end_time:
                self.show_error("Start time must be less than end time")
                return

            if start_time < 0:
                self.show_error("Start time must be positive")
                return

            video_duration = self._get_video_duration()
            if end_time > video_duration:
                self.show_error(f"End time cannot exceed video duration ({video_duration:.1f}s)")
                return

            # Check if trimming is actually needed
            if start_time == 0 and end_time >= video_duration:
                self.show_error("No trimming needed - you've selected the entire video")
                return

            # Create temporary file for trimmed video
            temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4")
            os.close(temp_fd)

            # Build ffmpeg command
            current_video = self.history.get_current_video_path()
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
                self.history.add_to_history(temp_path)
                self.video_player.src = temp_path
                self.toolbar.show_success(f"Video trimmed from {start_time}s to {end_time}s")

                # Close popup with success result
                self.close_with_result("success")
            else:
                self.show_error(f"Trimming failed: {process.stderr}")
                # Clean up temp file on failure
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except ValueError:
            self.show_error("Please enter valid numeric values for times")
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")
