"""
Screen recorder application entry point.

This module initializes and runs the screen recording application with:
- System tray integration
- Global keyboard shortcuts (Alt+S to show, Esc to hide)
- Overlay window for screen region selection and recording controls
"""

import threading
import keyboard
from .recorder import ScreenRecorder
from .overlay import OverlayWindow
from .tray import create_tray_icon

# Global reference to overlay window for keep_alive function
overlay_window = None


def keep_alive():
    """Periodic no-op to keep tkinter event loop responsive to signals."""
    if overlay_window and overlay_window.root:
        overlay_window.root.after(1000, keep_alive)


def main():
    global overlay_window

    recorder = ScreenRecorder()
    overlay_window = OverlayWindow(recorder)

    # Set up system tray
    tray_icon = create_tray_icon(overlay_window)
    threading.Thread(target=tray_icon.run, daemon=True).start()

    # Set up global keyboard shortcuts
    keyboard.add_hotkey("alt+s", overlay_window.show)
    keyboard.add_hotkey("esc", overlay_window.hide)

    try:
        keep_alive()
        overlay_window.mainloop()
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
