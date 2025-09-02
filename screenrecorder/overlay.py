import tkinter as tk
import ctypes
from .win32_utils import passthrough_mouse_clicks, capture_mouse_clicks
from .config import load_region, save_region


class OverlayApp:
    MODE_WAITING = "waiting"
    MODE_SELECTION = "selection"
    MODE_RECORDING = "recording"

    def __init__(self, recorder):
        self.recorder = recorder
        self.recorder.region = load_region()
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "grey")

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.canvas = tk.Canvas(self.root, width=sw, height=sh, bg="grey", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.button_win = tk.Toplevel(self.root)
        self.button_win.overrideredirect(True)
        self.button_win.attributes("-topmost", True)
        self.button_win.withdraw()

        self.record_btn = tk.Button(
            self.button_win, text="Record", command=self.toggle_recording, font=("Arial", 14), bg="red", fg="white"
        )
        self.select_btn = tk.Button(
            self.button_win,
            text="Select new region",
            command=self.enter_selection_mode,
            font=("Arial", 14),
            bg="blue",
            fg="white",
        )
        self.record_btn.pack(side="left", padx=10)
        self.select_btn.pack(side="left", padx=10)

        self.mode = self.MODE_WAITING
        self.selecting = False
        self.start_x = self.start_y = None
        self.rect_id = None
        self.msg_id = None

        self.root.bind("<Escape>", lambda e: self.enter_waiting_mode())
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)

        self.root.after(100, self._update_clickthrough)
        self.enter_waiting_mode()

    def _update_clickthrough(self):
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        if self.mode == self.MODE_SELECTION:
            capture_mouse_clicks(hwnd)
        else:
            passthrough_mouse_clicks(hwnd)

    def enter_waiting_mode(self):
        self.mode = self.MODE_WAITING
        self.selecting = False
        self.root.withdraw()
        self.button_win.withdraw()
        self.root.after(100, self._update_clickthrough)

    def enter_selection_mode(self):
        self.mode = self.MODE_SELECTION
        self.selecting = True
        self.start_x = self.start_y = None
        self.root.deiconify()
        self.root.lift()
        self.button_win.withdraw()
        self.show_message("Click-and-drag to select a region")
        self._redraw_overlay()
        self._update_clickthrough()

    def enter_recording_mode(self):
        self.mode = self.MODE_RECORDING
        self.selecting = False
        self.root.deiconify()
        self.root.lift()
        self.button_win.deiconify()
        self.button_win.lift()
        self.record_btn.config(text="Record", bg="red", state="normal")
        self.select_btn.config(state="normal")
        self._redraw_overlay()
        self._update_clickthrough()

    def toggle_recording(self):
        if self.recorder.recording:
            self.recorder.stop()
            self.record_btn.config(text="Record", bg="red")
            self.enter_waiting_mode()
        else:
            self.recorder.start()
            self.record_btn.config(text="Stop recording", bg="green")

    def _on_mouse_down(self, event):
        if self.mode != self.MODE_SELECTION:
            return
        self.start_x, self.start_y = event.x, event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None

    def _on_mouse_up(self, event):
        if self.mode != self.MODE_SELECTION or self.start_x is None:
            return
        x0, y0, x1, y1 = self.start_x, self.start_y, event.x, event.y
        x, y = min(x0, x1), min(y0, y1)
        w, h = abs(x1 - x0), abs(y1 - y0)
        if w > 10 and h > 10:
            self.recorder.region = (x, y, w, h)
            save_region(self.recorder.region)
            self.selecting = False
            self.start_x = self.start_y = None
            self.enter_recording_mode()
        else:
            self.show_message("Invalid region, try again")
            self.start_x = self.start_y = None

    def _on_mouse_drag(self, event):
        if self.mode != self.MODE_SELECTION or self.start_x is None:
            return
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="white", width=2
        )

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
            self.canvas.create_rectangle(0, 0, sw, sh, fill="black")
            x, y, w, h = self.recorder.region
            self.canvas.create_rectangle(x, y, x + w, y + h, fill="grey", outline="white", width=2)

        if self.mode == self.MODE_SELECTION:
            self.root.attributes("-alpha", 0.4)
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

    def run(self):
        self.root.mainloop()
