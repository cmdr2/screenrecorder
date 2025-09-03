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

    def seek(self, frame_number):
        if self.cap:
            # Temporarily pause playback to avoid thread conflicts during seeking
            was_playing = self.playing and not self.paused
            if was_playing:
                self.paused = True
                # Small delay to ensure the playback thread recognizes the pause
                time.sleep(0.1)

            # Now safe to seek
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.frame_pos = frame_number

            # Resume playback if it was playing before
            if was_playing:
                self.paused = False

            self.dispatch_event("seek", frame_number=frame_number)

    def _play_loop(self):
        while self.playing and self.cap and self.cap.isOpened():
            if self.paused:
                time.sleep(0.05)
                continue
            ret, frame = self.cap.read()
            if not ret:
                # End of video
                self.dispatch_event("ended")
                break
            self.frame_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            # Only update label if it still exists
            if self.video_img.winfo_exists():
                self.video_img.imgtk = imgtk
                self.video_img.config(image=imgtk)
            else:
                # If label is gone, stop playback
                self.playing = False
                break
            time.sleep(1 / max(self.cap.get(cv2.CAP_PROP_FPS), 25))
        self.stop()

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
