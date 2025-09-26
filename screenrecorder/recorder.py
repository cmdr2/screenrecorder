"""
Screen recording functionality using FFmpeg.

This module provides screen recording capabilities with support for:
- Full screen or region-based recording
- Cross-platform support (Windows/Linux)
- Hardware-accelerated video encoding
"""

import tempfile
import os
import subprocess
import platform
import signal


class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.region = None  # (x, y, w, h)
        self.temp_video_path = None
        self.ffmpeg_process = None

    def start(self):
        """
        Start screen recording.

        Creates a temporary file and starts FFmpeg process for recording.
        Supports full screen or region-based recording on Windows/Linux.
        """
        from .utils import get_ffmpeg_path

        if self.recording:
            return

        self.recording = True

        # Create temporary file for recording
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        self.temp_video_path = temp.name
        temp.close()

        # Build FFmpeg command
        ffmpeg_cmd = self._build_ffmpeg_command(get_ffmpeg_path())

        # Start FFmpeg process
        self.ffmpeg_process = self._start_ffmpeg_process(ffmpeg_cmd)

    def _build_ffmpeg_command(self, ffmpeg_path):
        """Build FFmpeg command based on platform and region settings."""
        system = platform.system()
        cmd = [ffmpeg_path, "-y", "-framerate", "30"]

        if system == "Windows":
            cmd.extend(["-f", "gdigrab"])
            if self.region:
                x, y, w, h = self.region
                cmd.extend(["-offset_x", str(x), "-offset_y", str(y), "-video_size", f"{w}x{h}"])
            cmd.extend(["-draw_mouse", "1", "-i", "desktop"])

        elif system == "Linux":
            cmd.extend(["-f", "x11grab"])
            display = os.environ.get("DISPLAY", ":0.0")
            if self.region:
                x, y, w, h = self.region
                cmd.extend(["-video_size", f"{w}x{h}", "-i", f"{display}+{x},{y}"])
            else:
                cmd.extend(["-i", display])
        else:
            raise RuntimeError(f"Unsupported OS for screen recording: {system}")

        # Add encoding options
        cmd.extend(["-vcodec", "libx264", "-pix_fmt", "yuv420p", self.temp_video_path])
        return cmd

    def _start_ffmpeg_process(self, cmd):
        """Start FFmpeg process with appropriate flags for the platform."""
        system = platform.system()
        creationflags = 0

        if system == "Windows":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        return subprocess.Popen(cmd, stdin=subprocess.PIPE, creationflags=creationflags)

    def stop(self):
        """
        Stop screen recording gracefully.

        Sends appropriate signals to FFmpeg process and waits for completion.
        """
        if not self.recording:
            return

        self.recording = False

        if self.ffmpeg_process:
            self._terminate_ffmpeg_process()
            self.ffmpeg_process = None

        if self.temp_video_path:
            print(f"Recording saved to: {self.temp_video_path}")

    def _terminate_ffmpeg_process(self):
        """Terminate FFmpeg process using platform-appropriate signals."""
        system = platform.system()

        try:
            if system == "Windows":
                # Send CTRL+BREAK signal to process group
                self.ffmpeg_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                # Send SIGINT to process group (Linux/macOS)
                self.ffmpeg_process.send_signal(signal.SIGINT)
        except Exception:
            # Fallback to forceful termination
            self.ffmpeg_process.terminate()
        finally:
            # Wait for process to finish
            self.ffmpeg_process.wait()
