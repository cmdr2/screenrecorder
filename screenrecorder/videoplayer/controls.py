import tkinter as tk


class VideoPlayerControls:
    def __init__(self, parent, play_callback, pause_callback, stop_callback, seek_callback):
        self.frame = tk.Frame(parent)
        self.frame.pack(fill=tk.X, padx=10, pady=5)
        self.play_button = tk.Button(self.frame, text="Play", command=play_callback)
        self.play_button.pack(side=tk.LEFT, padx=5)
        self.pause_button = tk.Button(self.frame, text="Pause", command=pause_callback)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(self.frame, text="Stop", command=stop_callback)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.seek_slider = tk.Scale(
            self.frame, from_=0, to=100, orient=tk.HORIZONTAL, showvalue=0, length=200, command=seek_callback
        )
        self.seek_slider.pack(side=tk.LEFT, padx=5)
