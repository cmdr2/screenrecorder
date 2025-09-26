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
from ..config import get_region, set_region
from .ui_buttons import UIButtonPanel
from .recording_region import RecordingRegion
from .mode_manager import ModeManager
from ..editor import EditorWindow as PreviewEditorWindow


class OverlayWindow:
    """
    Main overlay window providing screen recording interface.

    Manages transparent overlay with region selection, recording controls,
    and mouse interaction handling.
    """

    def __init__(self, recorder):
        self.recorder = recorder
        self.recorder.region = get_region()

        self.mode_manager = ModeManager(self)

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
        self.mode_manager.enter_waiting_mode()

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
        self.ui_panel = UIButtonPanel(
            self.root,
            on_record=self.toggle_recording,
            on_select=self.mode_manager.enter_selection_mode,
            on_close=self.mode_manager.enter_waiting_mode,
        )

        # Initialize recording region component
        self.recording_region = RecordingRegion(
            canvas=self.canvas,
            get_region_callback=lambda: self.recorder.region,
            set_region_callback=lambda region: setattr(self.recorder, "region", region),
            get_screen_size_callback=lambda: (self.root.winfo_screenwidth(), self.root.winfo_screenheight()),
        )

    def _setup_event_handlers(self):
        self.root.bind("<Escape>", lambda e: self.mode_manager.enter_waiting_mode())
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Motion>", self._on_mouse_motion)

    def _update_clickthrough(self):
        """Update window click-through behavior based on current mode."""
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())

        if self.mode_manager.is_selecting():
            capture_mouse_clicks(hwnd)  # Capture clicks for region selection
        elif self.mode_manager.is_recording() and not self.recorder.recording:
            capture_mouse_clicks(hwnd)  # Capture clicks for region manipulation
        elif self.mode_manager.is_recording() and self.recorder.recording:
            passthrough_mouse_clicks(hwnd)  # Pass through clicks while recording
        else:
            passthrough_mouse_clicks(hwnd)  # Default pass-through behavior

    def _ensure_ui_panel_on_top(self):
        """Periodically ensure UI panel stays on top while in recording mode"""
        if self.mode_manager.is_recording() and not self.recorder.recording:
            self.ui_panel.button_win.lift()
            # Check again after 500ms
            self.root.after(500, self._ensure_ui_panel_on_top)

    def toggle_recording(self):
        """Toggle between start and stop recording states."""
        if self.recorder.recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _stop_recording(self):
        """Stop recording and handle post-recording actions."""
        self.recorder.stop()
        self.ui_panel.set_recording_state(False)
        self._redraw_overlay()
        self._update_clickthrough()
        self.mode_manager.enter_waiting_mode()

        # Handle recorded video
        if self.recorder.temp_video_path:
            self._handle_recorded_video()

    def _start_recording(self):
        """Start recording and update UI state."""
        self.recorder.start()
        self.ui_panel.set_recording_state(True)
        self._redraw_overlay()
        self._update_clickthrough()

    def _handle_recorded_video(self):
        """Handle the recorded video file - copy to clipboard and show preview."""
        from ..utils import copy_files_to_clipboard

        try:
            copy_files_to_clipboard(self.recorder.temp_video_path)
            preview = PreviewEditorWindow(self.recorder.temp_video_path)
            preview.show_toast("Video copied to clipboard!")
        except Exception as e:
            print(f"Failed to copy video to clipboard: {e}")

    def _on_mouse_down(self, event):
        """Handle mouse button press events."""
        # Keep UI panel on top during interactions
        if self.mode_manager.is_recording() and not self.recorder.recording:
            self.ui_panel.button_win.lift()

        if self.mode_manager.is_selecting():
            # Start new region selection
            self.start_x, self.start_y = event.x, event.y
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None
        elif self.mode_manager.is_recording() and not self.recorder.recording and self.recorder.region:
            # Try resize first, then drag if not resizing
            if not self.recording_region.start_resize(event.x, event.y):
                self.recording_region.start_drag(event.x, event.y)

    def _on_mouse_up(self, event):
        """Handle mouse button release events."""
        if self.mode_manager.is_selecting() and self.start_x is not None and not self.recording_region.is_operating():
            self._complete_region_selection(event)
        elif self.recording_region.is_operating():
            self._complete_region_operation()

    def _complete_region_selection(self, event):
        """Complete region selection and transition to recording mode."""
        x0, y0, x1, y1 = self.start_x, self.start_y, event.x, event.y
        x, y = min(x0, x1), min(y0, y1)
        w, h = abs(x1 - x0), abs(y1 - y0)

        # Ensure dimensions are multiples of 2 for video encoding
        w += 1 if w % 2 else 0
        h += 1 if h % 2 else 0

        if w > 10 and h > 10:
            self.recorder.region = (x, y, w, h)
            set_region(self.recorder.region)
            self.selecting = False
            self.start_x = self.start_y = None
            self.mode_manager.enter_recording_mode()
        else:
            self.show_message("Invalid region, try again")
            self.start_x = self.start_y = None

    def _complete_region_operation(self):
        """Complete region drag/resize operation and save settings."""
        if self.recorder.region:
            set_region(self.recorder.region)
        self.recording_region.finish_operation()

    def _on_mouse_motion(self, event):
        """Handle mouse motion for cursor updates."""
        if self.mode_manager.is_recording() and not self.recorder.recording:
            self.recording_region.update_cursor(event.x, event.y)
        else:
            self.canvas.config(cursor="arrow")

    def _on_mouse_drag(self, event):
        """Handle mouse drag events for selection and region manipulation."""
        if self.mode_manager.is_selecting() and self.start_x is not None and not self.recording_region.is_operating():
            self._draw_selection_rectangle(event)
        elif self.recording_region.is_operating():
            self._handle_region_manipulation(event)

    def _draw_selection_rectangle(self, event):
        """Draw selection rectangle during region selection."""
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="white", width=2
        )

    def _handle_region_manipulation(self, event):
        """Handle dragging or resizing of recording region."""
        region_changed = self.recording_region.handle_drag(event.x, event.y) or self.recording_region.handle_resize(
            event.x, event.y
        )
        if region_changed:
            self._redraw_overlay()
            self.ui_panel.button_win.lift()  # Keep UI panel on top

    def show_message(self, text):
        """Display a message in the center of the overlay."""
        if self.msg_id:
            self.canvas.delete(self.msg_id)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.msg_id = self.canvas.create_text(
            sw // 2, sh // 2, text=text, fill="white", font=("Arial", 20), tags="message"
        )

    def _redraw_overlay(self):
        """Redraw the overlay based on current mode and state."""
        self.canvas.delete("all")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        # Create black background
        self.canvas.create_rectangle(0, 0, sw, sh, fill="black")

        # Mode-specific drawing
        if self.mode_manager.is_selecting():
            self.show_message("Click-and-drag to select a region")
        elif self.mode_manager.is_recording() and self.recorder.region:
            self.recording_region.draw(self.recorder.recording)

        # Set transparency based on mode
        self._update_transparency()

    def _update_transparency(self):
        """Update window transparency based on current mode."""
        if self.mode_manager.is_selecting():
            self.root.attributes("-alpha", 0.4)
        elif self.mode_manager.is_recording():
            if self.recorder.recording:
                self.root.attributes("-alpha", 0.7)
            else:
                self.root.attributes("-alpha", 0.3)
                # Keep UI panel on top after redraw
                self.root.after(1, lambda: self.ui_panel.button_win.lift())
        else:
            self.root.attributes("-alpha", 0.7)

    def show(self):
        if self.recorder.region:
            self.mode_manager.enter_recording_mode()
        else:
            self.mode_manager.enter_selection_mode()

    def hide(self):
        self.recorder.stop()
        self.mode_manager.enter_waiting_mode()

    def mainloop(self):
        self.root.mainloop()
