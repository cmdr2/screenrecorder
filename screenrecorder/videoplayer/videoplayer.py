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
        self.label = tk.Label(self.frame, bg="black")
        self.label.pack(fill=tk.BOTH, expand=1)
        self.thread = None
        self.frame_pos = 0
        self.video_path = None

    def load(self, video_path):
        self.stop()
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)
        self.frame_pos = 0

    def play(self):
        if not self.cap and self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
        if self.playing:
            self.paused = False
            return
        self.playing = True
        self.paused = False
        self.thread = threading.Thread(target=self._play_loop, daemon=True)
        self.thread.start()

    def pause(self):
        self.paused = True

    def stop(self):
        self.playing = False
        self.paused = False
        if self.cap:
            self.cap.release()
            self.cap = None
        # Only update label if it still exists
        if self.label.winfo_exists():
            self.label.config(image="")

    def seek(self, frame_number):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.frame_pos = frame_number

    def _play_loop(self):
        while self.playing and self.cap and self.cap.isOpened():
            if self.paused:
                time.sleep(0.05)
                continue
            ret, frame = self.cap.read()
            if not ret:
                # End of video
                if hasattr(self, "on_video_end") and callable(self.on_video_end):
                    self.on_video_end()
                break
            self.frame_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            # Only update label if it still exists
            if self.label.winfo_exists():
                self.label.imgtk = imgtk
                self.label.config(image=imgtk)
            else:
                # If label is gone, stop playback
                self.playing = False
                break
            time.sleep(1 / max(self.cap.get(cv2.CAP_PROP_FPS), 25))
        self.stop()

    def set_on_video_end(self, callback):
        self.on_video_end = callback
