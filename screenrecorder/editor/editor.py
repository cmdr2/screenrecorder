import tkinter as tk
from tkinter_videoplayer import VideoPlayer

from .. import theme
from .toolbar import Toolbar


class EditorWindow:
    def __init__(self, video_path, parent=None):
        if parent is None:
            self.root = tk.Toplevel()
        else:
            self.root = parent
        self.root.title("Preview video")
        self.root.geometry("640x480")
        self.root.configure(bg=theme.COLOR_BG)
        # Ensure window is focused and on top
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.after(500, lambda: self.root.attributes("-topmost", False))  # Remove topmost after focus

        # Video player component (with controls, autoplay options)
        self.video_player = VideoPlayer(
            self.root, video_path=video_path, width=640, height=480, controls=True, autoplay=True
        )

        # Create toolbar above the video player
        self.toolbar = Toolbar(self.root, self.video_player, video_path, self)

        # Pack video player after toolbar
        self.video_player.frame.pack(fill=tk.BOTH, expand=True)
        self.filename = video_path

    def show_toast(self, message):
        # Create a small label overlay in the window
        toast = tk.Label(
            self.root,
            text=message,
            bg=theme.TOAST_BG,
            fg=theme.TOAST_FG,
            font=theme.TOAST_FONT,
            padx=theme.TOAST_PADX,
            pady=theme.TOAST_PADY,
            bd=theme.TOAST_BORDER_WIDTH,
            relief="solid",
            highlightbackground=theme.TOAST_BORDER_COLOR,
            highlightcolor=theme.TOAST_BORDER_COLOR,
            highlightthickness=theme.TOAST_BORDER_WIDTH,
        )
        # Place at bottom right corner
        self.root.update_idletasks()
        x = self.root.winfo_width() - toast.winfo_reqwidth() - 20
        y = self.root.winfo_height() - toast.winfo_reqheight() - 20
        toast.place(x=x, y=y)
        # Remove after 3 seconds
        self.root.after(3000, toast.destroy)
