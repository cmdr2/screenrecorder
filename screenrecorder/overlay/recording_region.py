"""
Recording Region Component

This component handles the drag and resize functionality for the recording region overlay.
It manages mouse interactions for resizing and dragging the recording area.
"""


class RecordingRegion:
    """
    Handles recording region manipulation including dragging and resizing.

    This component encapsulates all the logic for:
    - Detecting mouse position relative to region boundaries
    - Handling drag operations to move the region
    - Handling resize operations on region edges/corners
    - Updating mouse cursor based on current operation
    """

    def __init__(self, canvas, get_region_callback, set_region_callback, get_screen_size_callback):
        """
        Initialize the RecordingRegion component.

        Args:
            canvas: The tkinter Canvas where the region is displayed
            get_region_callback: Function that returns current region (x, y, w, h)
            set_region_callback: Function to update the region (x, y, w, h)
            get_screen_size_callback: Function that returns screen dimensions (width, height)
        """
        self.canvas = canvas
        self.get_region = get_region_callback
        self.set_region = set_region_callback
        self.get_screen_size = get_screen_size_callback

        # State variables for drag/resize operations
        self.dragging = False
        self.resizing = False
        self.resize_zone = None
        self.start_x = None
        self.start_y = None
        self.drag_offset_x = None
        self.drag_offset_y = None
        self.original_region = None

    def reset_state(self):
        """Reset all drag/resize state variables."""
        self.dragging = False
        self.resizing = False
        self.resize_zone = None
        self.start_x = None
        self.start_y = None
        self.drag_offset_x = None
        self.drag_offset_y = None
        self.original_region = None

    def is_point_in_region(self, x, y):
        """Check if a point is inside the current recording region."""
        region = self.get_region()
        if not region:
            return False
        rx, ry, rw, rh = region
        return rx <= x <= rx + rw and ry <= y <= ry + rh

    def get_resize_zone(self, x, y):
        """
        Determine which resize zone the mouse is in.
        Returns one of: 'n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw', 'inside', or None
        """
        region = self.get_region()
        if not region:
            return None

        rx, ry, rw, rh = region
        resize_margin = 8  # pixels from edge to consider as resize zone

        # Check if mouse is near the region
        if (
            x < rx - resize_margin
            or x > rx + rw + resize_margin
            or y < ry - resize_margin
            or y > ry + rh + resize_margin
        ):
            return None

        # Determine which zone
        near_left = abs(x - rx) <= resize_margin
        near_right = abs(x - (rx + rw)) <= resize_margin
        near_top = abs(y - ry) <= resize_margin
        near_bottom = abs(y - (ry + rh)) <= resize_margin

        # Corner checks first
        if near_top and near_left:
            return "nw"
        elif near_top and near_right:
            return "ne"
        elif near_bottom and near_left:
            return "sw"
        elif near_bottom and near_right:
            return "se"
        # Edge checks
        elif near_top:
            return "n"
        elif near_bottom:
            return "s"
        elif near_left:
            return "w"
        elif near_right:
            return "e"
        # Inside the region
        elif self.is_point_in_region(x, y):
            return "inside"

        return None

    def update_cursor(self, x, y):
        """Update cursor based on mouse position."""
        region = self.get_region()
        if region:
            resize_zone = self.get_resize_zone(x, y)

            if resize_zone == "n" or resize_zone == "s":
                self.canvas.config(cursor="sb_v_double_arrow")  # vertical resize cursor
            elif resize_zone == "e" or resize_zone == "w":
                self.canvas.config(cursor="sb_h_double_arrow")  # horizontal resize cursor
            elif resize_zone == "nw" or resize_zone == "se":
                self.canvas.config(cursor="size_nw_se")  # diagonal resize cursor
            elif resize_zone == "ne" or resize_zone == "sw":
                self.canvas.config(cursor="size_ne_sw")  # diagonal resize cursor
            elif resize_zone == "inside":
                self.canvas.config(cursor="fleur")  # drag cursor
            else:
                self.canvas.config(cursor="arrow")  # default cursor
        else:
            self.canvas.config(cursor="arrow")  # default cursor

    def start_drag(self, x, y):
        """Start dragging the region from the given position."""
        region = self.get_region()
        if not region:
            return False

        if self.get_resize_zone(x, y) == "inside":
            self.dragging = True
            self.resizing = False
            self.original_region = region
            rx, ry, rw, rh = region
            self.drag_offset_x = x - rx
            self.drag_offset_y = y - ry
            return True
        return False

    def start_resize(self, x, y):
        """Start resizing the region from the given position."""
        region = self.get_region()
        if not region:
            return False

        resize_zone = self.get_resize_zone(x, y)
        if resize_zone and resize_zone != "inside":
            self.resizing = True
            self.resize_zone = resize_zone
            self.dragging = False
            self.original_region = region
            self.start_x, self.start_y = x, y
            return True
        return False

    def handle_drag(self, x, y):
        """Handle dragging the region to a new position."""
        if not self.dragging or not self.original_region:
            return False

        new_x = x - self.drag_offset_x
        new_y = y - self.drag_offset_y

        # Constrain to screen boundaries
        sw, sh = self.get_screen_size()
        w, h = self.original_region[2], self.original_region[3]
        new_x = max(0, min(new_x, sw - w))
        new_y = max(0, min(new_y, sh - h))

        new_region = (new_x, new_y, w, h)
        self.set_region(new_region)
        return True

    def handle_resize(self, x, y):
        """Handle resizing the region based on the current resize zone."""
        if not self.resizing or not self.original_region or not self.resize_zone:
            return False

        rx, ry, rw, rh = self.original_region
        min_size = 20  # Minimum width/height
        sw, sh = self.get_screen_size()

        # Calculate deltas from start position
        dx = x - self.start_x
        dy = y - self.start_y

        new_x, new_y, new_w, new_h = rx, ry, rw, rh

        if "n" in self.resize_zone:  # Top edge
            new_y = max(0, ry + dy)
            new_h = max(min_size, rh - (new_y - ry))
            if new_h == min_size:
                new_y = ry + rh - min_size

        if "s" in self.resize_zone:  # Bottom edge
            new_h = max(min_size, rh + dy)
            new_h = min(new_h, sh - ry)

        if "w" in self.resize_zone:  # Left edge
            new_x = max(0, rx + dx)
            new_w = max(min_size, rw - (new_x - rx))
            if new_w == min_size:
                new_x = rx + rw - min_size

        if "e" in self.resize_zone:  # Right edge
            new_w = max(min_size, rw + dx)
            new_w = min(new_w, sw - rx)

        # Ensure region stays within screen bounds
        if new_x + new_w > sw:
            new_w = sw - new_x
        if new_y + new_h > sh:
            new_h = sh - new_y

        # round up to the nearest multiple of 2 for video compatibility
        new_w += 1 if new_w % 2 else 0
        new_h += 1 if new_h % 2 else 0

        new_region = (int(new_x), int(new_y), int(new_w), int(new_h))
        self.set_region(new_region)
        return True

    def draw(self, is_recording):
        x, y, w, h = self.get_region()

        if is_recording:
            border_offset = 3  # Border drawn 3 pixels outside recording area
            self.canvas.create_rectangle(
                x - border_offset,
                y - border_offset,
                x + w + border_offset,
                y + h + border_offset,
                outline="white",
                width=2,
                fill="grey",
            )
        else:
            # Use a semi-transparent fill that's not the transparent color to ensure mouse events work
            self.canvas.create_rectangle(x, y, x + w, y + h, fill="#404040", outline="white", width=2)

    def finish_operation(self):
        """Complete current drag or resize operation and reset state."""
        was_operating = self.dragging or self.resizing
        self.reset_state()
        return was_operating

    def is_operating(self):
        """Check if currently dragging or resizing."""
        return self.dragging or self.resizing
