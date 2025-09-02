import tkinter as tk

from tkfontawesome import icon_to_image
from .config import get_panel_position, set_panel_position

# --- Style Constants ---
PANEL_BG = "#23272f"
PANEL_BORDER_COLOR = "#3a3f4b"
PANEL_BORDER_WIDTH = 1
PANEL_PADX = 10
PANEL_PADY = 5

DRAG_ICON_COLOR = "#888"
DRAG_ICON_SIZE = 22
DRAG_ICON_BG = PANEL_BG
DRAG_ICON_PADX = (8, 0)
DRAG_ICON_PADY = 6

BTN_BG = "#2c313c"
BTN_FG = "#fff"
BTN_ACTIVE_BG = "#344055"
BTN_ACTIVE_FG = "#fff"
BTN_BORDER_COLOR = "#3a3f4b"
BTN_BORDER_WIDTH = 2
BTN_PADX = 12
BTN_PADY = 6
BTN_FONT = ("Segoe UI", 13, "bold")
BTN_RELIEF = "flat"

RECORD_ICON_COLOR = "#e74c3c"
STOP_ICON_COLOR = "#e74c3c"
REGION_ICON_COLOR = "#3498db"
ICON_SIZE = 18
BTN_PACK_PADX = 8


class UIButtonPanel:
    def __init__(self, parent, on_record, on_select):

        # Stylish dark panel
        self.button_win = tk.Toplevel(parent)
        self.button_win.overrideredirect(True)
        self.button_win.attributes("-topmost", True)
        self.button_win.withdraw()
        self.button_win.configure(
            bg=PANEL_BG,
            bd=PANEL_BORDER_WIDTH,
            highlightbackground=PANEL_BORDER_COLOR,
            highlightcolor=PANEL_BORDER_COLOR,
            highlightthickness=PANEL_BORDER_WIDTH,
            padx=PANEL_PADX,
            pady=PANEL_PADY,
        )

        # Drag icon (FontAwesome)
        drag_img = icon_to_image("grip-vertical", fill=DRAG_ICON_COLOR, scale_to_width=DRAG_ICON_SIZE / 2)
        self.drag_icon = tk.Label(
            self.button_win,
            image=drag_img,
            bg=DRAG_ICON_BG,
            width=32,
            height=32,
            bd=0,
            highlightbackground=PANEL_BORDER_COLOR,
            highlightthickness=0,
        )
        self.drag_icon.image = drag_img
        self.drag_icon.pack(side="left", padx=DRAG_ICON_PADX, pady=DRAG_ICON_PADY)

        # Record button with icon
        rec_icon = icon_to_image("circle", fill=RECORD_ICON_COLOR, scale_to_width=ICON_SIZE)
        self.record_btn = tk.Button(
            self.button_win,
            text=" Record",
            image=rec_icon,
            compound="left",
            command=on_record,
            font=BTN_FONT,
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_ACTIVE_BG,
            activeforeground=BTN_ACTIVE_FG,
            bd=BTN_BORDER_WIDTH,
            relief=BTN_RELIEF,
            highlightbackground=BTN_BORDER_COLOR,
            highlightcolor=BTN_BORDER_COLOR,
            highlightthickness=BTN_BORDER_WIDTH,
            padx=BTN_PADX,
            pady=BTN_PADY,
        )
        self.record_btn.image = rec_icon
        self.record_btn.pack(side="left", padx=BTN_PACK_PADX)

        # Region select button with icon
        region_icon = icon_to_image("object-group", fill=REGION_ICON_COLOR, scale_to_width=ICON_SIZE)
        self.select_btn = tk.Button(
            self.button_win,
            text="Select region to capture",
            image=region_icon,
            compound="left",
            command=on_select,
            font=BTN_FONT,
            bg=BTN_BG,
            fg=BTN_FG,
            activebackground=BTN_ACTIVE_BG,
            activeforeground=BTN_ACTIVE_FG,
            bd=BTN_BORDER_WIDTH,
            relief=BTN_RELIEF,
            highlightbackground=BTN_BORDER_COLOR,
            highlightcolor=BTN_BORDER_COLOR,
            highlightthickness=BTN_BORDER_WIDTH,
            padx=BTN_PADX,
            pady=BTN_PADY,
        )
        self.select_btn.image = region_icon
        self.select_btn.pack(side="left", padx=BTN_PACK_PADX)

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
            stop_icon = icon_to_image("stop", fill=STOP_ICON_COLOR, scale_to_width=ICON_SIZE)
            self.record_btn.config(
                text=" Stop",
                image=stop_icon,
                bg="#27ae60",
                fg=BTN_FG,
                activebackground="#2ecc71",
                activeforeground=BTN_ACTIVE_FG,
                highlightbackground=BTN_BORDER_COLOR,
                highlightcolor=BTN_BORDER_COLOR,
                highlightthickness=BTN_BORDER_WIDTH,
            )
            self.record_btn.image = stop_icon
        else:
            rec_icon = icon_to_image("circle", fill=RECORD_ICON_COLOR, scale_to_width=ICON_SIZE)
            self.record_btn.config(
                text=" Record",
                image=rec_icon,
                bg=BTN_BG,
                fg=BTN_FG,
                activebackground=BTN_ACTIVE_BG,
                activeforeground=BTN_ACTIVE_FG,
                highlightbackground=BTN_BORDER_COLOR,
                highlightcolor=BTN_BORDER_COLOR,
                highlightthickness=BTN_BORDER_WIDTH,
            )
            self.record_btn.image = rec_icon
            self.record_btn.config(state="normal")
            self.select_btn.config(state="normal")

    def disable(self):
        self.record_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
