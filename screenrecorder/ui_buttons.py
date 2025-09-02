import tkinter as tk


class UIButtonPanel:
    def __init__(self, parent, on_record, on_select):
        self.button_win = tk.Toplevel(parent)
        self.button_win.overrideredirect(True)
        self.button_win.attributes("-topmost", True)
        self.button_win.withdraw()

        self.record_btn = tk.Button(
            self.button_win, text="Record", command=on_record, font=("Arial", 14), bg="red", fg="white"
        )
        self.select_btn = tk.Button(
            self.button_win,
            text="Select new region",
            command=on_select,
            font=("Arial", 14),
            bg="blue",
            fg="white",
        )
        self.record_btn.pack(side="left", padx=10)
        self.select_btn.pack(side="left", padx=10)

    def show(self):
        self.button_win.update_idletasks()
        parent = self.button_win.master
        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()
        win_w = self.button_win.winfo_width()
        win_h = self.button_win.winfo_height()
        # If width/height are 1 (not yet rendered), estimate from buttons
        if win_w <= 1:
            win_w = self.record_btn.winfo_reqwidth() + self.select_btn.winfo_reqwidth() + 40
        if win_h <= 1:
            win_h = max(self.record_btn.winfo_reqheight(), self.select_btn.winfo_reqheight()) + 20
        x = (sw - win_w) // 2
        y = int(sh * 0.9 - win_h // 2)
        self.button_win.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.button_win.deiconify()
        self.button_win.lift()

    def hide(self):
        self.button_win.withdraw()

    def set_recording_state(self, recording):
        if recording:
            self.record_btn.config(text="Stop recording", bg="green")
        else:
            self.record_btn.config(text="Record", bg="red")
            self.record_btn.config(state="normal")
            self.select_btn.config(state="normal")

    def disable(self):
        self.record_btn.config(state="disabled")
        self.select_btn.config(state="disabled")
