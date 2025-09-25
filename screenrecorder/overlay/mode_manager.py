"""
Mode management for overlay window states.

This module handles the different operational modes of the overlay window:
- Waiting: Hidden, not active
- Selection: Visible for region selection
- Recording: Visible with controls for recording
"""

from enum import Enum


class OverlayMode(Enum):
    """Enumeration of overlay window modes."""

    WAITING = "waiting"
    SELECTION = "selection"
    RECORDING = "recording"


class ModeManager:
    """Manages overlay window mode transitions and behaviors."""

    def __init__(self, overlay_window):
        """
        Initialize mode manager.

        Args:
            overlay_window: Reference to the main overlay window
        """
        self.overlay = overlay_window
        self.current_mode = OverlayMode.WAITING

    def enter_waiting_mode(self):
        """Enter waiting mode - hide overlay and UI panel."""
        self.current_mode = OverlayMode.WAITING
        self.overlay.selecting = False
        self.overlay.recording_region.reset_state()
        self.overlay.root.withdraw()
        self.overlay.ui_panel.hide()
        self.overlay.root.after(100, self.overlay._update_clickthrough)

    def enter_selection_mode(self):
        """Enter selection mode - show overlay for region drawing."""
        self.current_mode = OverlayMode.SELECTION
        self.overlay.selecting = True
        self.overlay.recording_region.reset_state()
        self.overlay.start_x = self.overlay.start_y = None
        self.overlay.root.deiconify()
        self.overlay.root.lift()
        self.overlay.ui_panel.hide()
        self.overlay.show_message("Click-and-drag to select a region")
        self.overlay._redraw_overlay()
        self.overlay._update_clickthrough()

    def enter_recording_mode(self):
        """Enter recording mode - show overlay with control panel."""
        self.current_mode = OverlayMode.RECORDING
        self.overlay.selecting = False
        self.overlay.recording_region.reset_state()
        self.overlay.root.deiconify()
        self.overlay.root.lift()
        self.overlay.ui_panel.show()
        self.overlay.root.after(0, lambda: self.overlay.ui_panel.set_recording_state(False))
        self.overlay._redraw_overlay()
        # Ensure UI panel stays on top
        self.overlay.root.after(10, lambda: self.overlay.ui_panel.button_win.lift())
        self.overlay._ensure_ui_panel_on_top()
        self.overlay._update_clickthrough()

    @property
    def mode(self):
        """Get current mode."""
        return self.current_mode

    def is_waiting(self):
        """Check if in waiting mode."""
        return self.current_mode == OverlayMode.WAITING

    def is_selecting(self):
        """Check if in selection mode."""
        return self.current_mode == OverlayMode.SELECTION

    def is_recording(self):
        """Check if in recording mode."""
        return self.current_mode == OverlayMode.RECORDING
