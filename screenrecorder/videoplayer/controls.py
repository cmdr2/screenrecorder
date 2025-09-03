import tkinter as tk
from tkinter import Canvas
from tkfontawesome import icon_to_image
from screenrecorder import theme


class VideoPlayerControls:
    def __init__(self, parent, videoplayer):
        # Store reference to videoplayer
        self.videoplayer = videoplayer

        # Subscribe to video player events
        videoplayer.add_event_listener("play", self._on_video_event)
        videoplayer.add_event_listener("pause", self._on_video_event)
        videoplayer.add_event_listener("ended", self._on_video_event)

        self.frame = tk.Frame(parent, bg=theme.COLOR_BG)
        self.frame.pack(fill=tk.X, padx=10, pady=5)

        # Play/Pause Button (icon)
        self.is_playing = False
        self.play_icon = icon_to_image("play", fill=theme.BTN_FG, scale_to_width=22)
        self.pause_icon = icon_to_image("pause", fill=theme.BTN_FG, scale_to_width=22)
        self.play_pause_btn = tk.Button(
            self.frame,
            image=self.play_icon,
            bg=theme.BTN_BG,
            activebackground=theme.BTN_ACTIVE_BG,
            bd=0,
            command=self._toggle_play_pause,
        )
        self.play_pause_btn.image = self.play_icon
        self.play_pause_btn.pack(side=tk.LEFT, padx=8)

        # Time Counter
        self.time_label = tk.Label(
            self.frame, text="0:00 / 0:00", font=theme.BTN_FONT, bg=theme.COLOR_BG, fg=theme.COLOR_FG
        )
        self.time_label.pack(side=tk.LEFT, padx=8)

        # Custom Thin Slider
        self.slider_length = 220
        self.slider_height = 8
        self.slider_canvas = Canvas(
            self.frame, width=self.slider_length, height=self.slider_height, bg=theme.COLOR_BG, highlightthickness=0
        )
        self.slider_canvas.pack(side=tk.LEFT, padx=8)
        self.slider_canvas.bind("<Button-1>", self._on_slider_click)
        self.slider_canvas.bind("<B1-Motion>", self._on_slider_drag)
        self.slider_value = 0
        self.slider_max = 100

        self._draw_slider()

        # Start update timer for displaying current time
        self._start_timer()

    def _on_video_event(self, event_type, **kwargs):
        """Generic event handler for video player events"""
        if event_type == "play":
            self.is_playing = True
        elif event_type == "pause" or event_type == "ended":
            self.is_playing = False

        self._update_play_pause_button()

    def _start_timer(self):
        """Start a timer to update the time display and slider position"""
        self._update_display()
        self.frame.after(250, self._start_timer)

    def _update_display(self):
        """Update time display and slider position based on current video state"""
        try:
            if self.videoplayer.cap:
                # Get current time from frame position and FPS
                fps = self.videoplayer.cap.get(5) or 25
                current_time = self.videoplayer.frame_pos / fps

                # Get total duration from frame count and FPS
                frame_count = self.videoplayer.cap.get(7)
                total_time = frame_count / fps if frame_count else 0

                # Update time display
                self.update_time(current_time, total_time)

                # Update slider position
                if total_time > 0:
                    self.set_slider(current_time, total_time)
        except Exception:
            # Silently ignore errors in the timer
            pass

    def _toggle_play_pause(self):
        if self.is_playing:
            self.videoplayer.pause()
        else:
            self.videoplayer.play()

    def _update_play_pause_button(self):
        """Update the play/pause button icon based on current state"""
        if self.is_playing:
            self.play_pause_btn.config(image=self.pause_icon)
            self.play_pause_btn.image = self.pause_icon
        else:
            self.play_pause_btn.config(image=self.play_icon)
            self.play_pause_btn.image = self.play_icon

    def update_time(self, current, total):
        self.time_label.config(text=f"{self._format_time(current)} / {self._format_time(total)}")

    def _format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        return f"{m}:{s:02d}"

    def set_slider(self, value, max_value):
        self.slider_value = value
        self.slider_max = max_value
        self._draw_slider()

    def _draw_slider(self):
        self.slider_canvas.delete("all")
        # Draw background line
        self.slider_canvas.create_line(
            0, self.slider_height // 2, self.slider_length, self.slider_height // 2, fill=theme.COLOR_TERTIARY, width=3
        )
        # Draw progress line
        if self.slider_max > 0:
            progress = int((self.slider_value / self.slider_max) * self.slider_length)
        else:
            progress = 0
        self.slider_canvas.create_line(
            0, self.slider_height // 2, progress, self.slider_height // 2, fill=theme.COLOR_PRIMARY, width=3
        )
        # Draw draggable knob
        self.slider_canvas.create_oval(
            progress - 5,
            self.slider_height // 2 - 5,
            progress + 5,
            self.slider_height // 2 + 5,
            fill=theme.COLOR_PRIMARY,
            outline=theme.COLOR_PRIMARY,
        )

    def _on_slider_click(self, event):
        self._seek_to(event.x)

    def _on_slider_drag(self, event):
        self._seek_to(event.x)

    def _seek_to(self, x):
        value = int((x / self.slider_length) * self.slider_max)
        value = max(0, min(self.slider_max, value))
        self.set_slider(value, self.slider_max)

        # Calculate frame number from time value
        if self.videoplayer.cap:
            fps = self.videoplayer.cap.get(5) or 25
            frame_number = int(value * fps)
            self.videoplayer.seek(frame_number)
