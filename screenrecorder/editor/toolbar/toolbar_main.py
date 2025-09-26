import tkinter as tk
from tkinter import filedialog

from ... import theme, ui
from .resize_popup import ResizePopup
from .trim_popup import TrimPopup
from ...utils import copy_files_to_clipboard

SEPARATOR = {"name": "separator"}


class Toolbar:
    def __init__(self, parent, editor):
        self.parent = parent
        self.editor = editor

        self.menu = [
            {
                "save": {"name": "Save", "icon": "save", "command": self.save_file},
                "copy": {"name": "Copy", "icon": "copy", "command": self.copy_to_clipboard},
                "undo": {"name": "Undo", "icon": "undo", "command": self.perform_undo, "disabled": True},
            },
            {
                "trim": {"name": "Trim", "icon": "cut", "command": self.open_trim_popup},
                "resize": {"name": "Resize", "icon": "expand-arrows-alt", "command": self.open_resize_popup},
            },
        ]

        self.trim_popup = TrimPopup(self.parent, self.editor)
        self.resize_popup = ResizePopup(self.parent, self.editor)

        # Create main toolbar frame
        toolbar_frame = tk.Frame(parent, bg=theme.COLOR_BG)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=theme.OVERLAY_PANEL_PADX, pady=theme.OVERLAY_PANEL_PADY)

        for group in self.menu:
            frame = tk.Frame(toolbar_frame, bg=theme.COLOR_BG)
            frame.pack(side=tk.LEFT, padx=(0, 20))

            for id, item in group.items():
                btn = ui.Button(
                    parent=frame,
                    text=item["name"],
                    icon_name=item["icon"],
                    command=item["command"],
                    hover_highlight=True,
                )
                if item.get("disabled", False):
                    btn.config(state=tk.DISABLED)

                btn.pack(side=tk.LEFT, padx=(0, theme.BTN_PACK_PADX))

                item["button"] = btn  # Store button reference for state updates

        self.editor.history.add_event_listener("change", self.update_undo_button_state)

    def save_file(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")], title="Save video as..."
        )
        if save_path:
            try:
                current_file = self.editor.get_current_file()
                with open(current_file, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                self.editor.show_success(f"Saved to {save_path}")
            except Exception as e:
                self.editor.show_error(f"Failed to save: {e}")

    def copy_to_clipboard(self):
        try:
            current_file = self.editor.get_current_file()
            copy_files_to_clipboard(current_file)
            self.editor.show_success("Video copied to clipboard!")
        except Exception as e:
            self.editor.show_error(f"Failed to copy: {e}")

    def perform_undo(self):
        self.editor.history.undo()
        self.editor.show_success("Undo successful!")

    def update_undo_button_state(self, new_value):
        button = self.menu[0]["undo"]["button"]
        if self.editor.history.can_undo():
            button.config(state=tk.NORMAL)
        else:
            button.config(state=tk.DISABLED)

    def open_trim_popup(self):
        self.trim_popup.show()

    def open_resize_popup(self):
        self.resize_popup.show()
