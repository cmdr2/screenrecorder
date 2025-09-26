from .mode import Mode


class WaitingMode(Mode):
    def __init__(self, overlay):
        super().__init__(overlay)

    def enter(self):
        self.overlay.selecting = False
        self.overlay.recording_region.reset_state()
        self.overlay.root.withdraw()
        self.overlay.controls.hide()
        self.overlay.root.after(100, self.overlay._update_clickthrough)

    def get_transparency(self):
        return 0.7

    def should_capture_clicks(self):
        return False
