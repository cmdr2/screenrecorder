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
from ... import ui
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
        self.start_time_entry = ui.Textbox(start_row, textvariable=self.start_time_var, width=10)
        self.start_time_entry.pack(side=tk.LEFT, padx=(10, 0))

        # Clamp value on unfocus
        self.start_time_entry.bind("<FocusOut>", lambda e: self.clamp_time_entries())

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
        self.end_time_entry = ui.Textbox(end_row, textvariable=self.end_time_var, width=10)
        self.end_time_entry.pack(side=tk.LEFT, padx=(10, 0))

        # Clamp value on unfocus
        self.end_time_entry.bind("<FocusOut>", lambda e: self.clamp_time_entries())

    def clamp_time_entries(self):
        """Clamp start and end time entry values to [0, duration]."""
        video_duration = self._get_video_duration()
        try:
            start_time = float(self.start_time_var.get().strip())
        except ValueError:
            start_time = 0.0
        try:
            end_time = float(self.end_time_var.get().strip())
        except ValueError:
            end_time = video_duration

        start_time = max(0.0, min(start_time, video_duration))
        end_time = max(0.0, min(end_time, video_duration))

        # If start >= end, keep as is (let apply_action handle it)
        self.start_time_var.set(f"{start_time:.1f}")
        self.end_time_var.set(f"{end_time:.1f}")

    def _get_video_duration(self):
        """Get the duration of the current video."""
        try:
            return round(self.video_player.duration, 1)
        except:
            return 0.0

    def apply_action(self):
        """Apply video trimming using ffmpeg, clamping times to [0, duration]."""
        try:
            start_time_str = self.start_time_var.get().strip()
            end_time_str = self.end_time_var.get().strip()

            video_duration = self._get_video_duration()

            # Parse and clamp times
            try:
                start_time = float(start_time_str)
            except ValueError:
                start_time = 0.0
            try:
                end_time = float(end_time_str)
            except ValueError:
                end_time = video_duration

            # Clamp to [0, video_duration]
            start_time = max(0.0, min(start_time, video_duration))
            end_time = max(0.0, min(end_time, video_duration))

            # Ensure start < end, else swap
            if start_time >= end_time:
                # If both are equal, do nothing; if swapped, fix
                if start_time == end_time:
                    # Nothing to trim
                    self.close_with_result(None)
                    return
                start_time, end_time = min(start_time, end_time), max(start_time, end_time)

            # If trimming is not needed (full video), just close
            if start_time == 0 and end_time >= video_duration:
                self.close_with_result(None)
                return

            # Update entry fields to reflect clamped values
            self.start_time_var.set(f"{start_time:.1f}")
            self.end_time_var.set(f"{end_time:.1f}")

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
                self.close_with_result("success")
            else:
                # Clean up temp file on failure
                try:
                    os.unlink(temp_path)
                except:
                    pass
                self.close_with_result(None)
        except Exception:
            self.close_with_result(None)
