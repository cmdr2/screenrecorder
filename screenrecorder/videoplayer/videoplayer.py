"""
OpenCVVideoPlayer: Tkinter-embedded video player with play, pause, load APIs.
"""

import cv2
from PIL import Image, ImageTk
import tkinter as tk
import time

from .events import EventDispatcher


class OpenCVVideoPlayer(EventDispatcher):
    def __init__(self, parent, width=640, height=480):
        super().__init__()
        self.parent = parent
        self.width = width
        self.height = height
        self.cap = None
        self.playing = False
        self.paused = False
        self.frame = tk.Frame(parent, width=width, height=height, bg="black")
        self.frame.pack_propagate(False)
        self.video_img = tk.Label(self.frame, bg="black")
        self.video_img.pack(fill=tk.BOTH, expand=1)
        self.thread = None
        self.frame_pos = 0
        self.video_path = None

        def bubble_event_to_top(event, event_type):
            # Find the topmost frame (component frame)
            top = self.frame
            while hasattr(top, "master") and isinstance(top.master, tk.Frame):
                top = top.master
            top.event_generate(event_type, x=event.x, y=event.y)

        for btn in ("<Button-1>", "<Button-2>", "<Enter>", "<Leave>", "<Key-space>"):
            self.video_img.bind(btn, lambda e, btn=btn: bubble_event_to_top(e, btn))

        # Bind resize event
        self.frame.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        # Pause video if playing during resize to prevent crash
        was_playing = self.playing and not self.paused
        if was_playing:
            self.paused = True
            time.sleep(0.1)  # Allow play thread to pause
        new_w, new_h = event.width, event.height
        if new_w != self.width or new_h != self.height:
            self.width, self.height = new_w, new_h
            self._display_current_frame()
        # Resume video if it was playing before resize
        if was_playing:
            self.paused = False

    def load(self, video_path):
        self.stop()
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)
        self.frame_pos = 0
        self.dispatch_event("load", path=video_path)

    def play(self):
        if not self.cap and self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)

        # Handle resuming from pause state
        if self.playing and self.paused:
            self.paused = False
            self.dispatch_event("play")
            return

        # If already playing and not paused, nothing to do
        if self.playing and not self.paused:
            return

        # Start a new playback
        self.playing = True
        self.paused = False
        self._play_loop_tk()
        self.dispatch_event("play")

    def pause(self):
        self.paused = True
        self.dispatch_event("pause")

    def stop(self):
        self.playing = False
        self.paused = False
        if self.cap:
            self.cap.release()
            self.cap = None
        # Only update label if it still exists
        if self.video_img.winfo_exists():
            self.video_img.config(image="")
        # Trigger pause event when stopping
        self.dispatch_event("pause")

    @property
    def currentTime(self):
        """Get or set the current playback time in seconds."""
        if not self.cap:
            return 0.0
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        return frame / fps if fps > 0 else 0.0

    @currentTime.setter
    def currentTime(self, seconds):
        if not self.cap:
            return
        was_playing = self.playing and not self.paused
        if was_playing:
            self.paused = True
            time.sleep(0.1)  # Allow thread to pause
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(seconds * fps) if fps > 0 else 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.frame_pos = frame_number
        # If paused, display the frame immediately
        if not was_playing or self.paused:
            self._display_current_frame()
        if was_playing:
            self.paused = False

    @property
    def duration(self):
        """Get the duration of the video in seconds."""
        if not self.cap:
            return 0.0
        frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        return frame_count / fps if fps > 0 else 0.0

    def _play_loop_tk(self):
        if not self.playing or not self.cap or not self.cap.isOpened():
            self.stop()
            return
        if self.paused:
            self.parent.after(50, self._play_loop_tk)
            return
        self._display_current_frame(advance=True)
        # Schedule next frame update
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / max(fps, 25))
        self.parent.after(delay, self._play_loop_tk)

    def _display_current_frame(self, advance=False):
        """
        Optimized: Use OpenCV for resizing and minimize conversions to PIL for lower memory and latency.
        """
        if not self.cap:
            return
        if advance:
            ret, frame = self.cap.read()
            if not ret:
                self.playing = False
                self.paused = False
                self.dispatch_event("ended")
                return
            self.frame_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        else:
            pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            ret, frame = self.cap.read()
            if not ret:
                return
            if int(pos) != self.frame_pos:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_pos)
                ret, frame = self.cap.read()
                if not ret:
                    return

        # Calculate aspect ratio preserving size
        orig_h, orig_w = frame.shape[:2]
        target_w, target_h = self.width, self.height
        scale = min(target_w / orig_w, target_h / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        # Use OpenCV for resizing (faster than PIL)
        frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Create black background and paste resized image centered
        bg = cv2.cvtColor(
            cv2.copyMakeBorder(
                frame_resized,
                top=(target_h - new_h) // 2,
                bottom=(target_h - new_h + 1) // 2,
                left=(target_w - new_w) // 2,
                right=(target_w - new_w + 1) // 2,
                borderType=cv2.BORDER_CONSTANT,
                value=[0, 0, 0],
            ),
            cv2.COLOR_BGR2RGB,
        )

        # Convert to PIL only for final display
        img = Image.fromarray(bg)
        imgtk = ImageTk.PhotoImage(image=img)

        if self.video_img.winfo_exists():
            self.video_img.imgtk = imgtk
            self.video_img.config(image=imgtk)
