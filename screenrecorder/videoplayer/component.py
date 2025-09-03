from .videoplayer import OpenCVVideoPlayer
from .controls import VideoPlayerControls

CONTROLS_BAR_HEIGHT_PX = 40


class VideoPlayerComponent:
    def __init__(self, parent, video_path=None, width=640, height=480, controls=True, autoplay=False, loop=False):
        self.parent = parent
        self._controls_enabled = controls
        self._autoplay = autoplay
        self._loop = loop
        self._src = video_path
        self.controls = None
        self.seek_slider = None

        self.player = OpenCVVideoPlayer(parent, width=width, height=height)
        self.player.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.player.add_event_listener("ended", self._on_video_end)

        # Bind mouse events only to the overall frame
        self.player.frame.bind("<Enter>", self._show_controls)
        self.player.frame.bind("<Leave>", self._hide_controls)
        self.player.frame.bind("<Button-1>", self._toggle_playback)
        self.player.frame.bind("<Key-space>", self._toggle_playback)
        self.player.frame.focus_set()  # Ensure frame can receive key events

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

        if video_path:
            self.player.load(video_path)
            if autoplay:
                self.player.play()

    @property
    def frame(self):
        return self.player.frame

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
        if self.controls and self.controls.frame:
            self.controls.frame.place_forget()

    def _on_video_end(self, event_type, **kwargs):
        if self._loop:
            self.player.seek(0)
            self.player.play()

    def _toggle_playback(self, event=None):
        self.controls._toggle_play_pause()

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
