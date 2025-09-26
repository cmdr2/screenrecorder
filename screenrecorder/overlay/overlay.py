"""
Main overlay window for screen recording interface.

This module provides the transparent overlay window that handles:
- Region selection for recording area
- Recording controls and state management
- Mouse interaction and click-through behavior
"""

import tkinter as tk
import ctypes

from ..utils import passthrough_mouse_clicks, capture_mouse_clicks
from ..config import get_region
from .controls import Controls
from .recording_region import RecordingRegion
from .mode_selection import SelectionMode
from .mode_recording import RecordingMode
from .mode_ready import ReadyMode
from .mode_waiting import WaitingMode


class OverlayWindow:
    def __init__(self, recorder):
        self.recorder = recorder
        self.recorder.region = get_region()

        # Initialize mode handlers
        self.selection_mode = SelectionMode(self)
        self.ready_mode = ReadyMode(self)
        self.recording_mode = RecordingMode(self)
        self.waiting_mode = WaitingMode(self)
        self.current_mode = self.waiting_mode

        self._setup_window()
        self._setup_ui_components()
        self._setup_event_handlers()

        # Initialize state variables
        self.selecting = False
        self.start_x = self.start_y = None
        self.rect_id = None
        self.msg_id = None

        # Start in waiting mode
        self.root.after(100, self._update_clickthrough)
        self.enter_waiting_mode()

    def _setup_window(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "grey")

        # Create full-screen canvas
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.canvas = tk.Canvas(self.root, width=sw, height=sh, bg="grey", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def _setup_ui_components(self):
        self.controls = Controls(
            self.root,
            on_record=self.toggle_recording,
            on_select=self.enter_selection_mode,
            on_close=self.enter_waiting_mode,
        )

        # Initialize recording region component
        self.recording_region = RecordingRegion(
            canvas=self.canvas,
            get_region_callback=lambda: self.recorder.region,
            set_region_callback=lambda region: setattr(self.recorder, "region", region),
            get_screen_size_callback=lambda: (self.root.winfo_screenwidth(), self.root.winfo_screenheight()),
        )

    def _setup_event_handlers(self):
        self.root.bind("<Escape>", lambda e: self.enter_waiting_mode())
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Motion>", self._on_mouse_motion)

    def _update_clickthrough(self):
        """Update window click-through behavior based on current mode."""
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())

        if self.current_mode.should_capture_clicks():
            capture_mouse_clicks(hwnd)
        else:
            passthrough_mouse_clicks(hwnd)

    def enter_waiting_mode(self):
        self.current_mode.exit()
        self.current_mode = self.waiting_mode
        self.current_mode.enter()

    def enter_selection_mode(self):
        self.current_mode.exit()
        self.current_mode = self.selection_mode
        self.current_mode.enter()

    def enter_ready_mode(self):
        self.current_mode.exit()
        self.current_mode = self.ready_mode
        self.current_mode.enter()

    def enter_recording_mode(self):
        self.current_mode.exit()
        self.current_mode = self.recording_mode
        self.current_mode.enter()

    def toggle_recording(self):
        if hasattr(self.current_mode, "toggle_recording"):
            self.current_mode.toggle_recording()

    def _on_mouse_down(self, event):
        self.current_mode.handle_mouse_down(event)

    def _on_mouse_up(self, event):
        self.current_mode.handle_mouse_up(event)

    def _on_mouse_motion(self, event):
        self.current_mode.handle_mouse_motion(event)

    def _on_mouse_drag(self, event):
        self.current_mode.handle_mouse_drag(event)

    def show_message(self, text):
        if self.msg_id:
            self.canvas.delete(self.msg_id)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.msg_id = self.canvas.create_text(
            sw // 2, sh // 2, text=text, fill="white", font=("Arial", 20), tags="message"
        )

    def _redraw_overlay(self):
        self.canvas.delete("all")
        self.current_mode.draw_overlay()
        self._update_transparency()

    def _update_transparency(self):
        alpha = self.current_mode.get_transparency()
        self.root.attributes("-alpha", alpha)

        # Keep UI panel on top for ready mode
        if self.current_mode == self.ready_mode:
            self.root.after(1, lambda: self.controls.button_win.lift())

    def show(self):
        if self.recorder.region:
            self.enter_ready_mode()
        else:
            self.enter_selection_mode()

    def hide(self):
        self.recorder.stop()
        self.enter_waiting_mode()

    def mainloop(self):
        self.root.mainloop()
