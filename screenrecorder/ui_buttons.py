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
