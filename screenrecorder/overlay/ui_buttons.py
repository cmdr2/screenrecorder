import tkinter as tk


from tkfontawesome import icon_to_image
from ..config import get_panel_position, set_panel_position
from .. import theme


class UIButtonPanel:
    def __init__(self, parent, on_record, on_select):
        self.button_win = tk.Toplevel(parent)
        self.button_win.overrideredirect(True)
        self.button_win.attributes("-topmost", True)
        self.button_win.withdraw()
        self.button_win.configure(
            bg=theme.OVERLAY_PANEL_BG,
            bd=theme.OVERLAY_PANEL_BORDER_WIDTH,
            highlightbackground=theme.OVERLAY_PANEL_BORDER_COLOR,
            highlightcolor=theme.OVERLAY_PANEL_BORDER_COLOR,
            highlightthickness=theme.OVERLAY_PANEL_BORDER_WIDTH,
            padx=theme.OVERLAY_PANEL_PADX,
            pady=theme.OVERLAY_PANEL_PADY,
        )

        # Drag icon (FontAwesome)
        drag_img = icon_to_image("grip-vertical", fill=theme.DRAG_ICON_COLOR, scale_to_width=theme.DRAG_ICON_SIZE / 2)
        self.drag_icon = tk.Label(
            self.button_win,
            image=drag_img,
            bg=theme.DRAG_ICON_BG,
            width=32,
            height=32,
            bd=0,
            highlightbackground=theme.OVERLAY_PANEL_BORDER_COLOR,
            highlightthickness=0,
        )
        self.drag_icon.image = drag_img
        self.drag_icon.pack(side="left", padx=theme.DRAG_ICON_PADX, pady=theme.DRAG_ICON_PADY)

        # Record button with icon
        rec_icon = icon_to_image("circle", fill=theme.RECORD_ICON_COLOR, scale_to_width=theme.ICON_SIZE)
        self.record_btn = tk.Button(
            self.button_win,
            text=" Record",
            image=rec_icon,
            compound="left",
            command=on_record,
            font=theme.BTN_FONT,
            bg=theme.BTN_BG,
            fg=theme.BTN_FG,
            activebackground=theme.BTN_ACTIVE_BG,
            activeforeground=theme.BTN_ACTIVE_FG,
            bd=theme.BTN_BORDER_WIDTH,
            relief=theme.BTN_RELIEF,
            highlightbackground=theme.BTN_BORDER_COLOR,
            highlightcolor=theme.BTN_BORDER_COLOR,
            highlightthickness=theme.BTN_BORDER_WIDTH,
            padx=theme.BTN_PADX,
            pady=theme.BTN_PADY,
        )
        self.record_btn.image = rec_icon
        self.record_btn.pack(side="left", padx=theme.BTN_PACK_PADX)

        # Region select button with icon
        region_icon = icon_to_image("object-group", fill=theme.REGION_ICON_COLOR, scale_to_width=theme.ICON_SIZE)
        self.select_btn = tk.Button(
            self.button_win,
            text="Select region to capture",
            image=region_icon,
            compound="left",
            command=on_select,
            font=theme.BTN_FONT,
            bg=theme.BTN_BG,
            fg=theme.BTN_FG,
            activebackground=theme.BTN_ACTIVE_BG,
            activeforeground=theme.BTN_ACTIVE_FG,
            bd=theme.BTN_BORDER_WIDTH,
            relief=theme.BTN_RELIEF,
            highlightbackground=theme.BTN_BORDER_COLOR,
            highlightcolor=theme.BTN_BORDER_COLOR,
            highlightthickness=theme.BTN_BORDER_WIDTH,
            padx=theme.BTN_PADX,
            pady=theme.BTN_PADY,
        )
        self.select_btn.image = region_icon
        self.select_btn.pack(side="left", padx=theme.BTN_PACK_PADX)

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
            stop_icon = icon_to_image("stop", fill=theme.STOP_ICON_COLOR, scale_to_width=theme.ICON_SIZE)
            self.record_btn.config(
                text=" Stop",
                image=stop_icon,
                bg="#27ae60",
                fg=theme.BTN_FG,
                activebackground="#2ecc71",
                activeforeground=theme.BTN_ACTIVE_FG,
                highlightbackground=theme.BTN_BORDER_COLOR,
                highlightcolor=theme.BTN_BORDER_COLOR,
                highlightthickness=theme.BTN_BORDER_WIDTH,
            )
            self.record_btn.image = stop_icon
        else:
            rec_icon = icon_to_image("circle", fill=theme.RECORD_ICON_COLOR, scale_to_width=theme.ICON_SIZE)
            self.record_btn.config(
                text=" Record",
                image=rec_icon,
                bg=theme.BTN_BG,
                fg=theme.BTN_FG,
                activebackground=theme.BTN_ACTIVE_BG,
                activeforeground=theme.BTN_ACTIVE_FG,
                highlightbackground=theme.BTN_BORDER_COLOR,
                highlightcolor=theme.BTN_BORDER_COLOR,
                highlightthickness=theme.BTN_BORDER_WIDTH,
            )
            self.record_btn.image = rec_icon
            self.record_btn.config(state="normal")
            self.select_btn.config(state="normal")

    def disable(self):
        self.record_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
