import tkinter as tk
from tkinter import Canvas
from tkfontawesome import icon_to_image
from screenrecorder import theme


class VideoPlayerControls:
    def __init__(self, parent, videoplayer):
        # Store reference to videoplayer
        self.videoplayer = videoplayer
        self._slider_dragging = False  # Track if slider is being dragged

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
        self.slider_height = 8  # Visual height of the slider line
        self.slider_clickable_height = 28  # Height of the clickable area (matches font size)
        self.slider_canvas = Canvas(
            self.frame,
            height=self.slider_clickable_height,
            bg=theme.COLOR_BG,
            highlightthickness=0,
        )
        self.slider_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.slider_canvas.bind("<Button-1>", self._on_slider_click)
        self.slider_canvas.bind("<B1-Motion>", self._on_slider_drag)
        self.slider_canvas.bind("<ButtonRelease-1>", self._on_slider_release)
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

        # Always update button to match the current state
        self._update_play_pause_button()

    def _start_timer(self):
        """Start a timer to update the time display and slider position"""
        # Check if the frame still exists before scheduling the next update
        if not self.frame.winfo_exists():
            return  # Frame was destroyed, don't schedule any more updates

        self._update_display()
        self.frame.after(250, self._start_timer)

    def _update_display(self):
        """Update time display and slider position based on current video state"""
        try:
            # First check if our widgets still exist before updating
            if not self.frame.winfo_exists():
                return

            # Ensure button state matches videoplayer state
            # This ensures UI stays in sync even if events are missed
            if hasattr(self, "videoplayer"):
                playing_state = self.videoplayer.playing and not self.videoplayer.paused
                if self.is_playing != playing_state:
                    self.is_playing = playing_state
                    self._update_play_pause_button()

            current_time = self.videoplayer.currentTime
            total_time = self.videoplayer.duration

            # Update time display
            self.update_time(current_time, total_time)

            # Update slider position only if not dragging
            if not self._slider_dragging and total_time > 0:
                self.set_slider(current_time, total_time)
        except Exception as e:
            # Print errors to debug
            print(f"Error updating display: {e}")
            # Silently continue
            pass

    def _toggle_play_pause(self):
        if self.is_playing:
            self.videoplayer.pause()
        else:
            self.videoplayer.play()

    def _update_play_pause_button(self):
        """Update the play/pause button icon based on current state"""
        # Check if the button still exists before trying to update it
        if not hasattr(self, "play_pause_btn") or not self.play_pause_btn.winfo_exists():
            return

        if self.is_playing:
            self.play_pause_btn.config(image=self.pause_icon)
            self.play_pause_btn.image = self.pause_icon
        else:
            self.play_pause_btn.config(image=self.play_icon)
            self.play_pause_btn.image = self.play_icon

    def update_time(self, current, total):
        # Check if label still exists before updating
        if hasattr(self, "time_label") and self.time_label.winfo_exists():
            self.time_label.config(text=f"{self._format_time(current)} / {self._format_time(total)}")

    def _format_time(self, seconds):
        m, s = divmod(int(seconds), 60)
        return f"{m}:{s:02d}"

    def set_slider(self, value, max_value):
        self.slider_value = value
        self.slider_max = max_value
        self._draw_slider()

    def _draw_slider(self):
        # Check if slider canvas still exists
        if not hasattr(self, "slider_canvas") or not self.slider_canvas.winfo_exists():
            return

        self.slider_canvas.delete("all")
        # Get current width dynamically
        slider_length = self.slider_canvas.winfo_width()
        center_y = self.slider_clickable_height // 2
        # Draw background line (thin)
        self.slider_canvas.create_line(0, center_y, slider_length, center_y, fill=theme.COLOR_TERTIARY, width=3)
        # Draw progress line
        if self.slider_max > 0:
            progress = int((self.slider_value / self.slider_max) * slider_length)
        else:
            progress = 0
        self.slider_canvas.create_line(0, center_y, progress, center_y, fill=theme.COLOR_PRIMARY, width=3)
        # Draw draggable knob (thin, centered)
        self.slider_canvas.create_oval(
            progress - 5,
            center_y - 5,
            progress + 5,
            center_y + 5,
            fill=theme.COLOR_PRIMARY,
            outline=theme.COLOR_PRIMARY,
        )

    def _on_slider_click(self, event):
        self._seek_to(event.x, immediate=True)

    def _on_slider_drag(self, event):
        self._slider_dragging = True
        # Update slider visually, but don't seek immediately during drag
        self._seek_to(event.x, immediate=False)

    def _on_slider_release(self, event):
        # Perform the actual seek when the slider is released
        self._seek_to(event.x, immediate=True)
        self._slider_dragging = False

    def _seek_to(self, x, immediate=True):
        # Use current slider width for calculation
        slider_length = self.slider_canvas.winfo_width()
        value = (x / slider_length) * self.slider_max
        value = max(0, min(self.slider_max, value))
        self.set_slider(value, self.slider_max)

        if immediate:
            self.videoplayer.currentTime = value
