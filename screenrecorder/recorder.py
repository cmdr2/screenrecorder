import tempfile
import os
import subprocess
import platform


class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.thread = None
        self.region = None  # (x, y, w, h)
        self.temp_video_path = None
        self.ffmpeg_process = None

    def start(self):
        from .utils import get_ffmpeg_path

        if self.recording:
            return

        self.recording = True
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        self.temp_video_path = temp.name
        temp.close()

        ffmpeg_path = get_ffmpeg_path()
        system = platform.system()
        ffmpeg_cmd = [ffmpeg_path, "-y"]

        if system == "Windows":
            ffmpeg_cmd += ["-f", "gdigrab", "-framerate", "30"]
            if self.region:
                x, y, w, h = self.region
                ffmpeg_cmd += ["-offset_x", str(x), "-offset_y", str(y), "-video_size", f"{w}x{h}"]
            ffmpeg_cmd += ["-draw_mouse", "1", "-i", "desktop"]
        elif system == "Linux":
            ffmpeg_cmd += ["-f", "x11grab", "-framerate", "30"]
            display = os.environ.get("DISPLAY", ":0.0")
            if self.region:
                x, y, w, h = self.region
                ffmpeg_cmd += ["-video_size", f"{w}x{h}", "-i", f"{display}+{x},{y}"]
            else:
                ffmpeg_cmd += ["-i", display]
        else:
            raise RuntimeError(f"Unsupported OS for screen recording: {system}")

        ffmpeg_cmd += ["-vcodec", "libx264", "-pix_fmt", "yuv420p", self.temp_video_path]
        # Start ffmpeg in a new process group for signal handling
        creationflags = 0
        if system == "Windows":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, creationflags=creationflags)

    def stop(self):
        if not self.recording:
            return

        self.recording = False
        if self.ffmpeg_process:
            system = platform.system()
            try:
                if system == "Windows":
                    # Send CTRL+C to the process group
                    import signal

                    self.ffmpeg_process.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    # Send SIGINT to the process group
                    self.ffmpeg_process.send_signal(subprocess.signal.SIGINT)
            except Exception:
                # Fallback to terminate
                self.ffmpeg_process.terminate()
            self.ffmpeg_process.wait()
            self.ffmpeg_process = None

        print(f"Saved to {self.temp_video_path}")
