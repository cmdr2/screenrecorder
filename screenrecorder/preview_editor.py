import tkinter as tk
from tkinter import filedialog
import vlc
import sys
from tkinter import filedialog, messagebox


class PreviewEditorWindow:
    def __init__(self, video_path):
        self.root = tk.Toplevel()
        self.root.title("Preview")
        self.root.geometry("640x480")
        self.root.title("Preview video")

        # self.pack(expand=True, fill="both")

        # Create a VLC instance and media player.
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Create the video panel where the video will be displayed.
        self.video_panel = tk.Frame(self.root, bg="black")
        self.video_panel.pack(fill=tk.BOTH, expand=1)

        # Create a progress frame that holds the progress slider.
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)

        # Create the progress slider.
        # This slider's range will be updated dynamically to match the video's duration.
        self.progress_slider = tk.Scale(
            self.progress_frame, from_=0, to=100, orient=tk.HORIZONTAL, showvalue=0, length=600
        )
        self.progress_slider.pack(fill=tk.X)
        self.progress_slider.bind("<ButtonPress-1>", self.on_slider_press)
        self.progress_slider.bind("<ButtonRelease-1>", self.on_slider_release)
        self.slider_dragging = False

        # Create the control panel with playback buttons and volume control.
        self.controls = tk.Frame(self.root)
        self.controls.pack(fill=tk.X, padx=10, pady=5)

        # Save button.
        self.save_button = tk.Button(self.controls, text="Save", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Copy button.
        self.copy_button = tk.Button(self.controls, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        # Play button.
        self.play_button = tk.Button(self.controls, text="Play", command=self.play_video)
        self.play_button.pack(side=tk.LEFT, padx=5)

        # Pause button.
        self.pause_button = tk.Button(self.controls, text="Pause", command=self.pause_video)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        # Stop button.
        self.stop_button = tk.Button(self.controls, text="Stop", command=self.stop_video)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.set_filepath(video_path)

        # Begin updating the progress slider periodically.
        self.update_progress()

    def set_filepath(self, video_path):
        self.filename = video_path
        media = self.instance.media_new(self.filename)
        self.player.set_media(media)
        self.set_video_panel()

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

    def set_video_panel(self):
        """
        This function embeds the VLC player's video output into the Tkinter video panel.
        It retrieves the window ID of the video panel and then assigns it to the VLC media player
        using platform-specific methods:
          - On Linux, it uses set_xwindow.
          - On Windows, it uses set_hwnd.
          - On macOS, it uses set_nsobject.
        This ensures that the video is rendered within the Tkinter frame regardless of the OS.
        """
        if sys.platform.startswith("linux"):
            self.player.set_xwindow(self.video_panel.winfo_id())
        elif sys.platform == "win32":
            self.player.set_hwnd(self.video_panel.winfo_id())
        elif sys.platform == "darwin":
            self.player.set_nsobject(self.video_panel.winfo_id())

    def play_video(self):
        """
        Once the media is loaded via the open_file function, clicking the Play button
        will trigger this function to begin playback.
        """
        self.player.play()

    def pause_video(self):
        """
        The pause_video function toggles the current playback state. If the video is playing,
        it pauses the playback; if it's paused, it resumes playing.
        """
        self.player.pause()

    def stop_video(self):
        """
        The stop_video function stops the video playback completely and resets the playback state.
        """
        self.player.stop()

    def on_slider_press(self, event):
        """
        Triggered when the user begins dragging the progress slider.
        This sets a flag indicating manual adjustment is in progress,
        preventing automatic updates from interfering.
        """
        self.slider_dragging = True

    def on_slider_release(self, event):
        """
        Triggered when the user releases the progress slider.
        It resets the dragging flag and seeks the video to the slider's position.
        """
        self.slider_dragging = False
        self.seek_video()

    def seek_video(self):
        """
        Seeks the video to a new position based on the slider's value.
        The slider's value represents the time in milliseconds.
        """
        slider_value = self.progress_slider.get()
        self.player.set_time(int(slider_value))

    def update_progress(self):
        """
        Updates the progress slider to reflect the current playback time.
        If the slider is not being manually adjusted by the user,
        this function retrieves the current playback time and the video's total length,
        updates the slider's range if necessary, and sets the slider to the current time.
        This function is called repeatedly every 500 milliseconds.
        """
        if not self.slider_dragging:
            current_time = self.player.get_time()  # Current time in milliseconds.
            duration = self.player.get_length()  # Total duration in milliseconds.
            if duration > 0:
                self.progress_slider.config(to=duration)
                self.progress_slider.set(current_time)
        self.root.after(500, self.update_progress)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    player = PreviewEditorWindow(root)
    root.mainloop()
