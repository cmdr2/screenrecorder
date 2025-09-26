class Mode:
    def __init__(self, overlay):
        self.overlay = overlay

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_mouse_down(self, event):
        pass

    def handle_mouse_drag(self, event):
        pass

    def handle_mouse_up(self, event):
        pass

    def handle_mouse_motion(self, event):
        pass

    def draw_overlay(self):
        pass

    def get_transparency(self):
        return 0.3  # Default transparency

    def should_capture_clicks(self):
        raise NotImplementedError("Subclasses must implement should_capture_clicks()")
