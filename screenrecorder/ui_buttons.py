import tkinter as tk
from .config import get_panel_position, set_panel_position


class UIButtonPanel:
    def __init__(self, parent, on_record, on_select):
        self.button_win = tk.Toplevel(parent)
        self.button_win.overrideredirect(True)
        self.button_win.attributes("-topmost", True)
        self.button_win.withdraw()

        self.record_btn = tk.Button(
            self.button_win, text="Record", command=on_record, font=("Arial", 14), bg="red", fg="white"
        )
        self.select_btn = tk.Button(
            self.button_win,
            text="Select new region",
            command=on_select,
            font=("Arial", 14),
            bg="blue",
            fg="white",
        )
        self.record_btn.pack(side="left", padx=10)
        self.select_btn.pack(side="left", padx=10)

        self._drag_data = {"x": 0, "y": 0}
        self.button_win.bind("<ButtonPress-1>", self._on_drag_start)
        self.button_win.bind("<B1-Motion>", self._on_drag_motion)
        self.button_win.bind("<ButtonRelease-1>", self._on_drag_end)

        self.position = get_panel_position()

    def show(self):
        self.button_win.update_idletasks()
        parent = self.button_win.master
        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()
        win_w = self.button_win.winfo_width()
        win_h = self.button_win.winfo_height()
        if win_w <= 1:
            win_w = self.record_btn.winfo_reqwidth() + self.select_btn.winfo_reqwidth() + 40
        if win_h <= 1:
            win_h = max(self.record_btn.winfo_reqheight(), self.select_btn.winfo_reqheight()) + 20
        if self.position:
            x, y = self.position
        else:
            x = (sw - win_w) // 2
            y = int(sh * 0.9 - win_h // 2)
        self.button_win.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.button_win.deiconify()
        self.button_win.lift()

    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        x = self.button_win.winfo_x() + event.x - self._drag_data["x"]
        y = self.button_win.winfo_y() + event.y - self._drag_data["y"]
        self.button_win.geometry(f"+{x}+{y}")

    def _on_drag_end(self, event):
        x = self.button_win.winfo_x()
        y = self.button_win.winfo_y()
        self.position = (x, y)
        set_panel_position((x, y))

    def hide(self):
        self.button_win.withdraw()

    def set_recording_state(self, recording):
        if recording:
            self.record_btn.config(text="Stop recording", bg="green")
        else:
            self.record_btn.config(text="Record", bg="red")
            self.record_btn.config(state="normal")
            self.select_btn.config(state="normal")

    def disable(self):
        self.record_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
