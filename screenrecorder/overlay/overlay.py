import tkinter as tk

import ctypes
from ..utils import passthrough_mouse_clicks, capture_mouse_clicks
from ..config import get_region, set_region
from .ui_buttons import UIButtonPanel
from ..editor import EditorWindow as PreviewEditorWindow


class OverlayWindow:
    MODE_WAITING = "waiting"
    MODE_SELECTION = "selection"
    MODE_RECORDING = "recording"

    def __init__(self, recorder):
        self.recorder = recorder
        self.recorder.region = get_region()
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "grey")

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.canvas = tk.Canvas(self.root, width=sw, height=sh, bg="grey", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.ui_panel = UIButtonPanel(self.root, on_record=self.toggle_recording, on_select=self.enter_selection_mode)

        self.mode = self.MODE_WAITING
        self.selecting = False
        self.dragging = False
        self.start_x = self.start_y = None
        self.drag_offset_x = self.drag_offset_y = None
        self.original_region = None
        self.rect_id = None
        self.msg_id = None

        self.root.bind("<Escape>", lambda e: self.enter_waiting_mode())
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<Motion>", self._on_mouse_motion)

        self.root.after(100, self._update_clickthrough)
        self.enter_waiting_mode()

    def _update_clickthrough(self):
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        if self.mode == self.MODE_SELECTION:
            # Selection mode: capture clicks for drawing
            capture_mouse_clicks(hwnd)
        elif self.mode == self.MODE_RECORDING and not self.recorder.recording:
            # Recording mode but not actively recording: capture clicks for dragging
            capture_mouse_clicks(hwnd)
        elif self.mode == self.MODE_RECORDING and self.recorder.recording:
            # Actively recording: pass through ALL clicks, show only border outline
            passthrough_mouse_clicks(hwnd)
        else:
            # Pass through clicks in waiting mode
            passthrough_mouse_clicks(hwnd)

    def _is_point_in_region(self, x, y):
        """Check if a point is inside the current recording region."""
        if not self.recorder.region:
            return False
        rx, ry, rw, rh = self.recorder.region
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def _update_cursor(self, x, y):
        """Update cursor based on mouse position."""
        if (
            self.mode == self.MODE_RECORDING
            and not self.recorder.recording
            and self.recorder.region
            and self._is_point_in_region(x, y)
        ):
            self.canvas.config(cursor="fleur")  # drag cursor (only when not actively recording)
        else:
            self.canvas.config(cursor="arrow")  # default cursor

    def enter_waiting_mode(self):
        self.mode = self.MODE_WAITING
        self.selecting = False
        self.dragging = False
        self.root.withdraw()
        self.ui_panel.hide()
        self.root.after(100, self._update_clickthrough)

    def enter_selection_mode(self):
        self.mode = self.MODE_SELECTION
        self.selecting = True
        self.dragging = False
        self.start_x = self.start_y = None
        self.root.deiconify()
        self.root.lift()
        self.ui_panel.hide()
        self.show_message("Click-and-drag to select a region")
        self._redraw_overlay()
        self._update_clickthrough()

    def enter_recording_mode(self):
        self.mode = self.MODE_RECORDING
        self.selecting = False
        self.dragging = False
        self.root.deiconify()
        self.root.lift()
        self.ui_panel.show()
        self.root.after(0, lambda: self.ui_panel.set_recording_state(False))
        self._redraw_overlay()
        # Ensure UI panel stays on top after overlay changes
        self.root.after(10, lambda: self.ui_panel.button_win.lift())
        # Keep checking UI panel stays on top while in recording mode
        self._ensure_ui_panel_on_top()
        self._update_clickthrough()

    def _ensure_ui_panel_on_top(self):
        """Periodically ensure UI panel stays on top while in recording mode"""
        if self.mode == self.MODE_RECORDING and not self.recorder.recording:
            self.ui_panel.button_win.lift()
            # Check again after 500ms
            self.root.after(500, self._ensure_ui_panel_on_top)

    def toggle_recording(self):
        if self.recorder.recording:
            self.recorder.stop()
            self.ui_panel.set_recording_state(False)
            # Redraw overlay to show full region again after stopping recording
            self._redraw_overlay()
            self._update_clickthrough()
            self.enter_waiting_mode()

            if self.recorder.temp_video_path:
                from ..utils import copy_files_to_clipboard

                try:
                    copy_files_to_clipboard(self.recorder.temp_video_path)
                except Exception as e:
                    print(f"Failed to copy video to clipboard: {e}")

                preview = PreviewEditorWindow(self.recorder.temp_video_path)

                preview.show_toast("Video copied to clipboard!")
        else:
            self.recorder.start()
            self.ui_panel.set_recording_state(True)
            # Redraw overlay to show only border and pass through clicks when recording starts
            self._redraw_overlay()
            self._update_clickthrough()

    def _on_mouse_down(self, event):
        # Ensure UI panel stays on top after any mouse interaction
        if self.mode == self.MODE_RECORDING and not self.recorder.recording:
            self.ui_panel.button_win.lift()

        if self.mode == self.MODE_SELECTION:
            # Selection mode - start new selection
            self.start_x, self.start_y = event.x, event.y
            self.dragging = False
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None
        elif (
            self.mode == self.MODE_RECORDING
            and not self.recorder.recording
            and self.recorder.region
            and self._is_point_in_region(event.x, event.y)
        ):
            # Recording mode but not actively recording - start dragging existing region
            self.dragging = True
            self.original_region = self.recorder.region
            rx, ry, rw, rh = self.recorder.region
            self.drag_offset_x = event.x - rx
            self.drag_offset_y = event.y - ry

    def _on_mouse_up(self, event):
        if self.mode == self.MODE_SELECTION and self.start_x is not None and not self.dragging:
            # Complete selection
            x0, y0, x1, y1 = self.start_x, self.start_y, event.x, event.y
            x, y = min(x0, x1), min(y0, y1)
            w, h = abs(x1 - x0), abs(y1 - y0)

            # round up to the nearest multiple of 2
            w += 1 if w % 2 else 0
            h += 1 if h % 2 else 0

            if w > 10 and h > 10:
                self.recorder.region = (x, y, w, h)
                set_region(self.recorder.region)
                self.selecting = False
                self.start_x = self.start_y = None
                self.enter_recording_mode()
            else:
                self.show_message("Invalid region, try again")
                self.start_x = self.start_y = None
        elif self.dragging:
            # Complete dragging - save new region position
            if self.recorder.region:
                set_region(self.recorder.region)
            self.dragging = False
            self.drag_offset_x = self.drag_offset_y = None
            self.original_region = None

    def _on_mouse_motion(self, event):
        """Handle mouse motion for cursor updates."""
        self._update_cursor(event.x, event.y)

    def _on_mouse_drag(self, event):
        if self.mode == self.MODE_SELECTION and self.start_x is not None and not self.dragging:
            # Selection mode - draw selection rectangle
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y, outline="white", width=2
            )
        elif self.dragging and self.original_region:
            # Dragging mode - move the existing region
            new_x = event.x - self.drag_offset_x
            new_y = event.y - self.drag_offset_y

            # Constrain to screen boundaries
            sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            w, h = self.original_region[2], self.original_region[3]
            new_x = max(0, min(new_x, sw - w))
            new_y = max(0, min(new_y, sh - h))

            new_region = (new_x, new_y, w, h)
            self.recorder.region = new_region
            self._redraw_overlay()
            # Keep UI panel on top during dragging
            self.ui_panel.button_win.lift()

    def show_message(self, text):
        if self.msg_id:
            self.canvas.delete(self.msg_id)
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.msg_id = self.canvas.create_text(
            sw // 2, sh // 2, text=text, fill="white", font=("Arial", 20), tags="message"
        )

    def _redraw_overlay(self):
        self.canvas.delete("all")
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        if self.mode == self.MODE_SELECTION:
            self.canvas.create_rectangle(0, 0, sw, sh, fill="black")
            self.show_message("Click-and-drag to select a region")
        elif self.mode == self.MODE_RECORDING and self.recorder.region:
            if self.recorder.recording:
                # During recording: only show white border outside the recording region
                self.canvas.create_rectangle(0, 0, sw, sh, fill="black")
                x, y, w, h = self.recorder.region
                border_offset = 3  # Border drawn 3 pixels outside recording area
                self.canvas.create_rectangle(
                    x - border_offset,
                    y - border_offset,
                    x + w + border_offset,
                    y + h + border_offset,
                    outline="white",
                    width=2,
                    fill="grey",
                )
            else:
                # Not recording: show full overlay with region
                self.canvas.create_rectangle(0, 0, sw, sh, fill="black")
                x, y, w, h = self.recorder.region
                # Use a semi-transparent fill that's not the transparent color to ensure mouse events work
                self.canvas.create_rectangle(x, y, x + w, y + h, fill="#404040", outline="white", width=2)

        if self.mode == self.MODE_SELECTION:
            self.root.attributes("-alpha", 0.4)
        elif self.mode == self.MODE_RECORDING:
            if self.recorder.recording:
                self.root.attributes("-alpha", 0.7)
            else:
                self.root.attributes("-alpha", 0.3)
                # Ensure UI panel stays on top after redraw
                self.root.after(1, lambda: self.ui_panel.button_win.lift())
        else:
            self.root.attributes("-alpha", 0.7)

    def show(self):
        if self.recorder.region:
            self.enter_recording_mode()
        else:
            self.enter_selection_mode()

    def hide(self):
        self.recorder.stop()
        self.enter_waiting_mode()

    def mainloop(self):
        self.root.mainloop()
