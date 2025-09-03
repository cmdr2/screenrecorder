import tkinter as tk
from tkinter import filedialog
from tkinter import filedialog, messagebox
from .videoplayer.component import VideoPlayerComponent


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
            messagebox.showinfo(
                "Clipboard", "Video file path copied to clipboard. You can now paste it as an attachment."
            )
        except Exception as e:
            messagebox.showerror("Clipboard", f"Failed to copy: {e}")

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
