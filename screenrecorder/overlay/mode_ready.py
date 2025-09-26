from .mode import Mode


class ReadyMode(Mode):
    def __init__(self, overlay):
        super().__init__(overlay)

    def enter(self):
        self.overlay.selecting = False
        self.overlay.recording_region.reset_state()
        self.overlay.root.deiconify()
        self.overlay.root.lift()
        self.overlay.ui_panel.show()
        self.overlay.root.after(0, lambda: self.overlay.ui_panel.set_recording_state(False))
        self.overlay._redraw_overlay()
        self.overlay.root.after(10, lambda: self.overlay.ui_panel.button_win.lift())
        self._ensure_ui_panel_on_top()
        self.overlay._update_clickthrough()

    def handle_mouse_down(self, event):
        self.overlay.ui_panel.button_win.lift()
        if self.overlay.recorder.region:
            if not self.overlay.recording_region.start_resize(event.x, event.y):
                self.overlay.recording_region.start_drag(event.x, event.y)

    def handle_mouse_drag(self, event):
        if self.overlay.recording_region.is_operating():
            self._handle_region_manipulation(event)

    def handle_mouse_up(self, event):
        if self.overlay.recording_region.is_operating():
            self._complete_region_operation()

    def handle_mouse_motion(self, event):
        self.overlay.recording_region.update_cursor(event.x, event.y)

    def _handle_region_manipulation(self, event):
        region_changed = self.overlay.recording_region.handle_drag(
            event.x, event.y
        ) or self.overlay.recording_region.handle_resize(event.x, event.y)
        if region_changed:
            self.overlay._redraw_overlay()
            self.overlay.ui_panel.button_win.lift()

    def _complete_region_operation(self):
        if self.overlay.recorder.region:
            from ..config import set_region

            set_region(self.overlay.recorder.region)
        self.overlay.recording_region.finish_operation()

    def _ensure_ui_panel_on_top(self):
        self.overlay.ui_panel.button_win.lift()
        self.overlay.root.after(500, self._ensure_ui_panel_on_top)

    def toggle_recording(self):
        self._start_recording()

    def _start_recording(self):
        self.overlay.recorder.start()
        self.overlay.ui_panel.set_recording_state(True)
        self.overlay.enter_recording_mode()

    def draw_overlay(self):
        sw, sh = self.overlay.root.winfo_screenwidth(), self.overlay.root.winfo_screenheight()
        self.overlay.canvas.create_rectangle(0, 0, sw, sh, fill="black")
        if self.overlay.recorder.region:
            self.overlay.recording_region.draw(False)  # Not recording yet

    def get_transparency(self):
        return 0.3

    def should_capture_clicks(self):
        return True
