import tkinter as tk
from .videoplayer import OpenCVVideoPlayer
from .controls import VideoPlayerControls
from .events import EventDispatcher

CONTROLS_BAR_HEIGHT_PX = 40


class VideoPlayerComponent(EventDispatcher):
    def __init__(self, parent, video_path=None, width=640, height=480, controls=True, autoplay=False, loop=False):
        super().__init__()
        self.parent = parent
        self._controls_enabled = controls
        self._autoplay = autoplay
        self._loop = loop
        self._src = video_path
        self.controls = None
        self.seek_slider = None

        # Create a dedicated frame for the component
        self.frame = tk.Frame(parent, width=width, height=height)
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.player = OpenCVVideoPlayer(self.frame, width=width, height=height)
        self.player.frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Bind events to the overall component frame
        self.player.frame.bind("<Enter>", self._show_controls)
        self.player.frame.bind("<Leave>", self._hide_controls)
        self.frame.bind("<Button-1>", self._toggle_playback)
        self.frame.bind("<Key-space>", self._toggle_playback)
        self.frame.bind("<Configure>", self._show_controls)
        self.frame.focus_set()  # Ensure frame can receive key events

        if self._controls_enabled:
            self.controls = VideoPlayerControls(self.player.frame, videoplayer=self.player)
            # Overlay controls at bottom, initially visible
            self.controls.frame.place(
                x=0,
                y=self.player.frame.winfo_height() - CONTROLS_BAR_HEIGHT_PX,
                relwidth=1,
                height=CONTROLS_BAR_HEIGHT_PX,
            )
            self.controls.frame.lift()
            self.seek_slider = self.controls.slider_canvas if hasattr(self.controls, "slider_canvas") else None

        # Forward video player events to component listeners
        self.player.add_event_listener("play", self._forward_event)
        self.player.add_event_listener("pause", self._forward_event)
        self.player.add_event_listener("ended", self._on_video_end)
        self.player.add_event_listener("load", self._forward_event)

        if self._src:
            self.player.load(self._src)
            if self._autoplay:
                self.player.play()

    def _forward_event(self, event_type, **kwargs):
        self.dispatch_event(event_type, **kwargs)

    def _show_controls(self, event=None):
        if self.controls and self.controls.frame:
            self.controls.frame.place(
                x=0,
                y=self.player.frame.winfo_height() - CONTROLS_BAR_HEIGHT_PX,
                relwidth=1,
                height=CONTROLS_BAR_HEIGHT_PX,
            )
            self.controls.frame.lift()

    def _hide_controls(self, event=None):
        # Only hide controls if video is playing
        if self.controls and self.controls.frame:
            if hasattr(self.player, "playing") and hasattr(self.player, "paused"):
                if self.player.playing and not self.player.paused:
                    self.controls.frame.place_forget()
            else:
                # Fallback: always show controls if state can't be determined
                pass

    def _on_video_end(self, event_type, **kwargs):
        if self._loop:
            self.player.seek(0)
            self.player.play()

    def _toggle_playback(self, event=None):
        was_playing = self.player.playing and not self.player.paused
        self.controls._toggle_play_pause()
        # If video was playing and is now paused, show controls
        if was_playing and self.player.paused:
            self._show_controls()

    @property
    def controls_enabled(self):
        return self._controls_enabled

    @controls_enabled.setter
    def controls_enabled(self, value):
        self._controls_enabled = bool(value)
        # Could add logic to show/hide controls dynamically

    @property
    def autoplay(self):
        return self._autoplay

    @autoplay.setter
    def autoplay(self, value):
        self._autoplay = bool(value)

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value):
        self._loop = bool(value)

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, video_path):
        self._src = video_path
        self.player.load(video_path)

    @property
    def is_playing(self):
        return self.player.playing

    @property
    def is_paused(self):
        return self.player.paused

    @property
    def currentTime(self):
        return self.player.currentTime

    @currentTime.setter
    def currentTime(self, seconds):
        try:
            self.player.currentTime = float(seconds)
        except Exception:
            pass

    @property
    def duration(self):
        return self.player.duration

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()
