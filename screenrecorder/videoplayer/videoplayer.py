"""
OpenCVVideoPlayer: Tkinter-embedded video player with play, pause, seek, load APIs.
"""

import cv2
import threading
from PIL import Image, ImageTk
import tkinter as tk
import time


class OpenCVVideoPlayer:
    def __init__(self, parent, width=640, height=480):
        self.parent = parent
        self.width = width
        self.height = height
        self.cap = None
        self.playing = False
        self.paused = False
        self.frame = tk.Frame(parent, width=width, height=height)
        self.frame.pack_propagate(False)
        self.video_img = tk.Label(self.frame, bg="black")
        self.video_img.pack(fill=tk.BOTH, expand=1)
        self.thread = None
        self.frame_pos = 0
        self.video_path = None

        # Event system
        self._event_handlers = {"play": [], "pause": [], "ended": [], "seek": [], "load": []}

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
        self.thread = threading.Thread(target=self._play_loop, daemon=True)
        self.thread.start()
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

    def _play_loop(self):
        while self.playing and self.cap and self.cap.isOpened():
            if self.paused:
                time.sleep(0.05)
                continue
            self._display_current_frame(advance=True)
            time.sleep(1 / max(self.cap.get(cv2.CAP_PROP_FPS), 25))
        self.stop()

    def _display_current_frame(self, advance=False):
        """
        Display the current frame in the video_img label.
        If advance=True, read the next frame; otherwise, show the current frame.
        """
        if not self.cap:
            return
        if advance:
            ret, frame = self.cap.read()
            if not ret:
                self.dispatch_event("ended")
                return
            self.frame_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        else:
            # Grab the frame at the current position
            pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            ret, frame = self.cap.read()
            if not ret:
                return
            # If the frame position changed, seek back
            if int(pos) != self.frame_pos:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_pos)
                ret, frame = self.cap.read()
                if not ret:
                    return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        imgtk = ImageTk.PhotoImage(image=img)
        if self.video_img.winfo_exists():
            self.video_img.imgtk = imgtk
            self.video_img.config(image=imgtk)

    # Event system methods
    def add_event_listener(self, event_type, callback):
        """Add an event listener for the specified event type

        Args:
            event_type: String representing the event ('play', 'pause', 'ended', etc)
            callback: Function to call when the event is triggered. The callback will
                      receive the event_type and any additional parameters as kwargs.
        """
        if event_type in self._event_handlers:
            if callback not in self._event_handlers[event_type]:
                self._event_handlers[event_type].append(callback)
        else:
            self._event_handlers[event_type] = [callback]

    def remove_event_listener(self, event_type, callback):
        """Remove an event listener for the specified event type"""
        if event_type in self._event_handlers and callback in self._event_handlers[event_type]:
            self._event_handlers[event_type].remove(callback)

    def dispatch_event(self, event_type, **kwargs):
        """Dispatch an event of the specified type with optional parameters"""
        if event_type in self._event_handlers:
            for callback in self._event_handlers[event_type]:
                try:
                    callback(event_type=event_type, **kwargs)
                except Exception as e:
                    print(f"Error in event listener: {e}")
