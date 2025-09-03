import tkinter as tk
from tkinter import filedialog, messagebox
from .videoplayer.component import VideoPlayerComponent
from . import theme


class PreviewEditorWindow:
    def __init__(self, video_path, parent=None):
        if parent is None:
            self.root = tk.Toplevel()
        else:
            self.root = parent
        self.root.title("Preview video")
        self.root.geometry("640x480")

        # Video player component (with controls, autoplay options)
        self.video_player = VideoPlayerComponent(
            self.root, video_path=video_path, width=640, height=480, controls=True, autoplay=True
        )
        self.video_player.frame.pack(fill=tk.BOTH, expand=True)
        self.filename = video_path

    def copy_to_clipboard(self):
        from .utils import copy_files_to_clipboard

        try:
            copy_files_to_clipboard(self.filename)
            self.show_toast("Video copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Clipboard", f"Failed to copy: {e}")

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

    def save_file(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if save_path:
            try:
                with open(self.filename, "rb") as src, open(save_path, "wb") as dst:
                    dst.write(src.read())
                messagebox.showinfo("Save", f"Saved to {save_path}")
            except Exception as e:
                messagebox.showerror("Save", f"Failed to save: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        video_file = sys.argv[1]
    else:
        video_file = filedialog.askopenfilename(title="Select a video file", filetypes=[("MP4 files", "*.mp4")])
        if not video_file:
            print("No file selected. Exiting.")
            sys.exit(0)

    root = tk.Tk()
    root.geometry("800x600")
    player = PreviewEditorWindow(video_file, parent=root)
    root.mainloop()
