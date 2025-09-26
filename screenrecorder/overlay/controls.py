"""
Controls panel for overlay recording.

This module provides the floating button panel that appears during
recording mode, containing record/stop, region selection, and close buttons.
"""

import tkinter as tk
from tkfontawesome import icon_to_image
from ..config import get_panel_position, set_panel_position
from .. import theme
from .. import ui

RECORD_LABEL = "Record"
STOP_LABEL = "Stop"
SELECT_LABEL = "Select region to capture"
CLOSE_LABEL = "Close"


class Controls:
    """Floating button panel for overlay recording controls."""

    def __init__(self, parent, on_record, on_select, on_close):
        """
        Initialize the UI button panel.

        Args:
            parent: Parent tkinter window
            on_record: Callback for record/stop button
            on_select: Callback for region selection button
            on_close: Callback for close button
        """
        self.drag_icon = icon_to_image(
            "grip-vertical", fill=theme.DRAG_ICON_COLOR, scale_to_width=theme.DRAG_ICON_SIZE // 2
        )
        self.rec_icon = icon_to_image("circle", fill=theme.RECORD_ICON_COLOR, scale_to_width=theme.ICON_SIZE)
        self.stop_icon = icon_to_image("stop", fill=theme.STOP_ICON_COLOR, scale_to_width=theme.ICON_SIZE)

        self._setup_window(parent)
        self._create_buttons(on_record, on_select, on_close)
        self._setup_drag_behavior()
        self.position = get_panel_position()

    def _setup_window(self, parent):
        """Configure the toplevel window for the button panel."""
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

    def _create_buttons(self, on_record, on_select, on_close):
        """Create all buttons using the button factory."""
        # Drag handle
        self.drag_icon = self.create_drag_handle(self.button_win)
        self.drag_icon.pack(side="left", pady=theme.DRAG_ICON_PADY)

        # Record button
        self.record_btn = ui.Button(
            self.button_win, RECORD_LABEL, command=on_record, icon_name="circle", icon_color=theme.RECORD_ICON_COLOR
        )
        self.record_btn.pack(side="left", padx=theme.BTN_PACK_PADX)

        # Region select button
        self.select_btn = ui.Button(
            self.button_win,
            SELECT_LABEL,
            command=on_select,
            icon_name="object-group",
            icon_color=theme.REGION_ICON_COLOR,
        )
        self.select_btn.pack(side="left", padx=theme.BTN_PACK_PADX)

        # Close button
        self.close_btn = ui.Button(
            self.button_win, CLOSE_LABEL, command=on_close, icon_name="times", icon_color=theme.RECORD_ICON_COLOR
        )
        self.close_btn.pack(side="left", padx=theme.BTN_PACK_PADX)

    def _setup_drag_behavior(self):
        """Setup drag and drop behavior for the panel."""
        self._drag_data = {"x": 0, "y": 0}

        # Bind drag events to the drag icon
        self.drag_icon.bind("<ButtonPress-1>", self._on_drag_start)
        self.drag_icon.bind("<B1-Motion>", self._on_drag_motion)
        self.drag_icon.bind("<ButtonRelease-1>", self._on_drag_end)

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
            self.record_btn.config(
                text=STOP_LABEL,
                image=self.stop_icon,
                bg="#27ae60",
                fg=theme.BTN_FG,
                activebackground="#2ecc71",
                activeforeground=theme.BTN_ACTIVE_FG,
                highlightbackground=theme.BTN_BORDER_COLOR,
                highlightcolor=theme.BTN_BORDER_COLOR,
                highlightthickness=theme.BTN_BORDER_WIDTH,
                state="normal",
            )
            self.record_btn.image = self.stop_icon
            # Disable other buttons while recording
            self.select_btn.config(state="disabled")
            self.close_btn.config(state="disabled")
        else:
            self.record_btn.config(
                text=RECORD_LABEL,
                image=self.rec_icon,
                bg=theme.BTN_BG,
                fg=theme.BTN_FG,
                activebackground=theme.BTN_ACTIVE_BG,
                activeforeground=theme.BTN_ACTIVE_FG,
                highlightbackground=theme.BTN_BORDER_COLOR,
                highlightcolor=theme.BTN_BORDER_COLOR,
                highlightthickness=theme.BTN_BORDER_WIDTH,
                state="normal",
            )
            self.record_btn.image = self.rec_icon
            # Re-enable other buttons when not recording
            self.select_btn.config(state="normal")
            self.close_btn.config(state="normal")

    def disable(self):
        self.record_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
        self.close_btn.config(state="disabled")

    def create_drag_handle(self, parent, **kwargs):
        """
        Create a drag handle icon for moveable panels.

        Args:
            parent: Parent widget
            **kwargs: Additional label configuration options

        Returns:
            tk.Label: Configured drag handle widget
        """

        default_config = {
            "image": self.drag_icon,
            "bg": theme.DRAG_ICON_BG,
            "width": 32,
            "height": 32,
            "bd": 0,
            "highlightbackground": theme.OVERLAY_PANEL_BORDER_COLOR,
            "highlightthickness": 0,
            "cursor": "fleur",
        }

        default_config.update(kwargs)

        drag_handle = tk.Label(parent, **default_config)
        drag_handle.image = self.drag_icon  # Keep reference

        return drag_handle
