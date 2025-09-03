import threading
import keyboard
from .recorder import ScreenRecorder
from .overlay import OverlayWindow
from .tray import create_tray_icon


# Periodic no-op to keep event loop responsive to signals
def keep_alive():
    overlay_window.root.after(1000, keep_alive)


if __name__ == "__main__":
    recorder = ScreenRecorder()
    overlay_window = OverlayWindow(recorder)

    tray_icon = create_tray_icon(overlay_window)
    threading.Thread(target=tray_icon.run, daemon=True).start()

    keyboard.add_hotkey("alt+s", overlay_window.show)
    keyboard.add_hotkey("esc", overlay_window.hide)

    try:
        keep_alive()
        overlay_window.mainloop()
    except KeyboardInterrupt:
        print("Exiting...")
