import tkinter as tk
from tkinter_videoplayer import VideoPlayer

from .. import theme
from .toolbar import Toolbar
from .history import EditHistory


class EditorWindow:
    def __init__(self, video_path, parent=None):
        if parent is None:
            self.root = tk.Toplevel()
        else:
            self.root = parent
        self.root.title("Preview video")

        # Set window size
        window_width = 640
        window_height = 480

        # Calculate center position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set geometry with center position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg=theme.COLOR_BG)
        # Ensure window is focused and on top
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.after(500, lambda: self.root.attributes("-topmost", False))  # Remove topmost after focus

        # History
        self.history = EditHistory()
        self.history.add_event_listener("change", self.on_history_change)

        # Video player component (with controls, autoplay options)
        self.video_player = VideoPlayer(
            self.root, video_path=video_path, width=640, height=480, controls=True, autoplay=True
        )
        self.history.add(video_path)

        # Create toolbar above the video player
        self.toolbar = Toolbar(self.root, self)

        # Pack video player after toolbar
        self.video_player.frame.pack(fill=tk.BOTH, expand=True)
        self.filename = video_path

    def on_history_change(self, new_value):
        self.video_player.src = new_value

    def get_current_file(self):
        return self.history.get_current()

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

    def show_error(self, message):
        self.show_toast(f"ERROR: {message}")
        print(f"Error: {message}")

    def show_success(self, message):
        self.show_toast(f"SUCCESS: {message}")
        print(f"Success: {message}")

    def show_info(self, message):
        self.show_toast(message)
        print(f"Info: {message}")
