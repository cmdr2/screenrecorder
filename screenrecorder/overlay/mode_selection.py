from .mode import Mode


class SelectionMode(Mode):
    def __init__(self, overlay):
        super().__init__(overlay)

        self.selecting = False
        self.start_x = None
        self.start_y = None
        self.rect_id = None

    def enter(self):
        self.selecting = True
        self.start_x = self.start_y = None
        self.overlay.recording_region.reset_state()
        self.overlay.root.deiconify()
        self.overlay.root.lift()
        self.overlay.ui_panel.hide()
        self.overlay.show_message("Click-and-drag to select a region")
        self.overlay._redraw_overlay()
        self.overlay._update_clickthrough()

    def exit(self):
        self.selecting = False
        self.start_x = self.start_y = None
        if self.rect_id:
            self.overlay.canvas.delete(self.rect_id)
            self.rect_id = None

    def handle_mouse_down(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect_id:
            self.overlay.canvas.delete(self.rect_id)
            self.rect_id = None

    def handle_mouse_drag(self, event):
        if self.start_x is not None and not self.overlay.recording_region.is_operating():
            self._draw_selection_rectangle(event)

    def handle_mouse_up(self, event):
        if self.start_x is not None and not self.overlay.recording_region.is_operating():
            self._complete_region_selection(event)

    def handle_mouse_motion(self, event):
        self.overlay.canvas.config(cursor="crosshair")

    def _draw_selection_rectangle(self, event):
        if self.rect_id:
            self.overlay.canvas.delete(self.rect_id)
        self.rect_id = self.overlay.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="white", width=2
        )

    def _complete_region_selection(self, event):
        x0, y0, x1, y1 = self.start_x, self.start_y, event.x, event.y
        x, y = min(x0, x1), min(y0, y1)
        w, h = abs(x1 - x0), abs(y1 - y0)

        # Ensure dimensions are multiples of 2 for video encoding
        w += 1 if w % 2 else 0
        h += 1 if h % 2 else 0

        if w > 10 and h > 10:
            self.overlay.recorder.region = (x, y, w, h)
            from ..config import set_region

            set_region(self.overlay.recorder.region)
            self.selecting = False
            self.start_x = self.start_y = None
            self.overlay.enter_ready_mode()
        else:
            self.overlay.show_message("Invalid region, try again")
            self.start_x = self.start_y = None

    def draw_overlay(self):
        sw, sh = self.overlay.root.winfo_screenwidth(), self.overlay.root.winfo_screenheight()
        self.overlay.canvas.create_rectangle(0, 0, sw, sh, fill="black")
        self.overlay.show_message("Click-and-drag to select a region")

    def get_transparency(self):
        return 0.4

    def should_capture_clicks(self):
        return True
