from .editor import EditorWindow

if __name__ == "__main__":
    import sys
    import tkinter as tk
    from tkinter import filedialog

    if len(sys.argv) > 1:
        video_file = sys.argv[1]
    else:
        video_file = filedialog.askopenfilename(title="Select a video file", filetypes=[("MP4 files", "*.mp4")])
        if not video_file:
            print("No file selected. Exiting.")
            sys.exit(0)

    root = tk.Tk()
    root.geometry("800x600")
    player = EditorWindow(video_file, parent=root)
    root.mainloop()
