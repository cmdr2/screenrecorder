"""
UI components for creating consistent UI elements.
"""

import tkinter as tk
from tkfontawesome import icon_to_image
from . import theme


class Button(tk.Button):
    def __init__(self, parent, text, command=None, icon_name=None, hover_highlight=False, **kwargs):
        if icon_name:
            icon_color = kwargs.pop("icon_color", theme.BTN_FG)
            icon_size = kwargs.pop("icon_size", theme.ICON_SIZE)
            icon_img = icon_to_image(icon_name, fill=icon_color, scale_to_width=icon_size)

        config = {
            "text": text,
            "command": command,
            "font": theme.BTN_FONT,
            "bg": theme.BTN_BG,
            "fg": theme.BTN_FG,
            "activebackground": theme.BTN_ACTIVE_BG,
            "activeforeground": theme.BTN_ACTIVE_FG,
            "bd": theme.BTN_BORDER_WIDTH,
            "relief": theme.BTN_RELIEF,
            "highlightbackground": theme.BTN_BORDER_COLOR,
            "highlightcolor": theme.BTN_BORDER_COLOR,
            "highlightthickness": theme.BTN_BORDER_WIDTH,
            "padx": theme.BTN_PADX,
            "pady": theme.BTN_PADY,
        }
        if icon_name:
            config["image"] = icon_img
            config["compound"] = "left"
            self.icon_img = icon_img  # Keep reference to prevent garbage collection

        self.hover_bg = theme.BTN_HOVER_BG if hover_highlight else None
        self.orig_bg = config["bg"]

        config.update(kwargs)
        super().__init__(parent, **config)

        if self.hover_bg:
            self.bind("<Enter>", self.on_enter)
            self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(bg=self.hover_bg)

    def on_leave(self, event):
        self.config(bg=self.orig_bg)


class Label(tk.Label):
    def __init__(self, parent, text, font=theme.FONT_NORMAL, bg=theme.COLOR_BG, fg=theme.COLOR_FG, **kwargs):
        super().__init__(parent, text=text, font=font, bg=bg, fg=fg, **kwargs)


class PrimaryButton(Button):
    def __init__(self, parent, text, command=None, icon_name=None, **kwargs):
        super().__init__(parent, text, command, icon_name, bg=theme.COLOR_PRIMARY, fg=theme.COLOR_FG, **kwargs)


class SecondaryButton(Button):
    def __init__(self, parent, text, command=None, icon_name=None, **kwargs):
        super().__init__(parent, text, command, icon_name, bg=theme.COLOR_SECONDARY, fg=theme.COLOR_FG, **kwargs)


class TertiaryButton(Button):
    def __init__(self, parent, text, command=None, icon_name=None, **kwargs):
        super().__init__(parent, text, command, icon_name, bg=theme.COLOR_TERTIARY, fg=theme.COLOR_FG, **kwargs)


class Textbox(tk.Entry):
    def __init__(self, parent, textvariable=None, width=10, **kwargs):
        config = {
            "textvariable": textvariable,
            "width": width,
            "font": theme.TEXTBOX_FONT,
            "justify": "center",
            "relief": "flat",
            "highlightthickness": theme.TEXTBOX_BORDER_WIDTH,
            "highlightbackground": theme.TEXTBOX_BORDER_COLOR,
            "highlightcolor": theme.TEXTBOX_HIGHLIGHT_COLOR,
            "bg": theme.TEXTBOX_BG,
            "fg": theme.TEXTBOX_FG,
            "insertbackground": theme.TEXTBOX_FG,
        }
        config.update(kwargs)
        # Remove None values (e.g., if textvariable is not provided)
        config = {k: v for k, v in config.items() if v is not None}
        super().__init__(parent, **config)
