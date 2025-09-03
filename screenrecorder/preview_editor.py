import tkinter as tk
from tkinter import filedialog
from tkinter import filedialog, messagebox
from .videoplayer.component import VideoPlayerComponent
from .videoplayer.videoplayer import OpenCVVideoPlayer


class PreviewEditorWindow:
    def __init__(self, video_path):
        self.root = tk.Toplevel()
        self.root.title("Preview video")
        self.root.geometry("640x480")

        # Video player component (with controls, autoplay options)
        self.video_player = VideoPlayerComponent(
            self.root, video_path=video_path, width=640, height=480, controls=True, autoplay=True
        )
        self.video_player.frame.pack(fill=tk.BOTH, expand=True)
        self.filename = video_path

    # No longer needed: set_filepath, set_video_panel, slider/progress logic

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

    # set_video_panel is not needed with ffplay/ffmpeg subprocess

    def play_video(self):
        self.video_player.play()

    # Pause not supported in ffplay subprocess, so omit

    def stop_video(self):
        self.video_player.stop()

    # Progress/seek not supported in ffplay subprocess, so omit


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    player = PreviewEditorWindow(root)
    root.mainloop()
