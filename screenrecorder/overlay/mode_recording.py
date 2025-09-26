class RecordingMode:
    def __init__(self, overlay):
        self.overlay = overlay

    def enter(self):
        # Recording mode assumes we're already recording
        self.overlay.selecting = False
        self.overlay.recording_region.reset_state()
        self.overlay.root.deiconify()
        self.overlay.root.lift()
        self.overlay.ui_panel.show()
        self.overlay._redraw_overlay()
        self.overlay._update_clickthrough()

    def exit(self):
        pass

    def handle_mouse_down(self, event):
        # No interaction allowed during recording
        pass

    def handle_mouse_drag(self, event):
        # No interaction allowed during recording
        pass

    def handle_mouse_up(self, event):
        # No interaction allowed during recording
        pass

    def handle_mouse_motion(self, event):
        # Fixed cursor during recording
        self.overlay.canvas.config(cursor="arrow")

    def toggle_recording(self):
        # Only stop recording is allowed
        self._stop_recording()

    def _stop_recording(self):
        self.overlay.recorder.stop()
        self.overlay.ui_panel.set_recording_state(False)
        self.overlay.enter_waiting_mode()

        if self.overlay.recorder.temp_video_path:
            self._handle_recorded_video()

    def _handle_recorded_video(self):
        from ..utils import copy_files_to_clipboard
        from ..editor import EditorWindow as PreviewEditorWindow

        try:
            copy_files_to_clipboard(self.overlay.recorder.temp_video_path)
            preview = PreviewEditorWindow(self.overlay.recorder.temp_video_path)
            preview.show_toast("Video copied to clipboard!")
        except Exception as e:
            print(f"Failed to copy video to clipboard: {e}")

    def draw_overlay(self):
        sw, sh = self.overlay.root.winfo_screenwidth(), self.overlay.root.winfo_screenheight()
        self.overlay.canvas.create_rectangle(0, 0, sw, sh, fill="black")
        if self.overlay.recorder.region:
            self.overlay.recording_region.draw(True)  # Always recording in this mode

    def get_transparency(self):
        return 0.7

    def should_capture_clicks(self):
        return False  # Mouse passthrough during recording
