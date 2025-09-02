import tkinter as tk
from tkfontawesome import icon_to_image
from .config import get_panel_position, set_panel_position


class UIButtonPanel:
    def __init__(self, parent, on_record, on_select):

        # Stylish dark panel
        self.button_win = tk.Toplevel(parent)
        self.button_win.overrideredirect(True)
        self.button_win.attributes("-topmost", True)
        self.button_win.withdraw()
        self.button_win.configure(bg="#23272f", bd=0, highlightthickness=0)

        # Drag icon (FontAwesome)
        drag_img = icon_to_image("grip-lines", fill="#888", scale_to_width=22)
        self.drag_icon = tk.Label(self.button_win, image=drag_img, bg="#23272f", width=32, height=32, bd=0)
        self.drag_icon.image = drag_img
        self.drag_icon.pack(side="left", padx=(8, 0), pady=6)

        # Record button with icon
        rec_icon = icon_to_image("circle", fill="#e74c3c", scale_to_width=18)
        self.record_btn = tk.Button(
            self.button_win,
            text=" Record",
            image=rec_icon,
            compound="left",
            command=on_record,
            font=("Segoe UI", 13, "bold"),
            bg="#2c313c",
            fg="#fff",
            activebackground="#344055",
            activeforeground="#fff",
            bd=0,
            relief="flat",
            highlightthickness=0,
            padx=12,
            pady=6,
        )
        self.record_btn.image = rec_icon
        self.record_btn.pack(side="left", padx=8)

        # Region select button with icon
        region_icon = icon_to_image("object-group", fill="#3498db", scale_to_width=18)
        self.select_btn = tk.Button(
            self.button_win,
            text=" Region",
            image=region_icon,
            compound="left",
            command=on_select,
            font=("Segoe UI", 13, "bold"),
            bg="#2c313c",
            fg="#fff",
            activebackground="#344055",
            activeforeground="#fff",
            bd=0,
            relief="flat",
            highlightthickness=0,
            padx=12,
            pady=6,
        )
        self.select_btn.image = region_icon
        self.select_btn.pack(side="left", padx=8)

        # Rounded corners for panel and buttons (simulate with padding and colors)
        self.button_win.update_idletasks()

        self._drag_data = {"x": 0, "y": 0}
        self.drag_icon.bind("<ButtonPress-1>", self._on_drag_start)
        self.drag_icon.bind("<B1-Motion>", self._on_drag_motion)
        self.drag_icon.bind("<ButtonRelease-1>", self._on_drag_end)

        self.position = get_panel_position()

        self._drag_data = {"x": 0, "y": 0}
        # Bind drag events only to the drag icon
        self.drag_icon.bind("<ButtonPress-1>", self._on_drag_start)
        self.drag_icon.bind("<B1-Motion>", self._on_drag_motion)
        self.drag_icon.bind("<ButtonRelease-1>", self._on_drag_end)

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
            stop_icon = icon_to_image("stop", fill="#e74c3c", scale_to_width=18)
            self.record_btn.config(text=" Stop", image=stop_icon, bg="#27ae60", fg="#fff", activebackground="#2ecc71")
            self.record_btn.image = stop_icon
        else:
            rec_icon = icon_to_image("circle", fill="#e74c3c", scale_to_width=18)
            self.record_btn.config(text=" Record", image=rec_icon, bg="#2c313c", fg="#fff", activebackground="#344055")
            self.record_btn.image = rec_icon
            self.record_btn.config(state="normal")
            self.select_btn.config(state="normal")

    def disable(self):
        self.record_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
