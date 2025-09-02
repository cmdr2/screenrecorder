import threading
import keyboard
from .recorder import ScreenRecorder
from .overlay import OverlayApp
from .tray import create_tray_icon


# Periodic no-op to keep event loop responsive to signals
def keep_alive():
    overlay.root.after(1000, keep_alive)


if __name__ == "__main__":
    recorder = ScreenRecorder()
    overlay = OverlayApp(recorder)

    tray_icon = create_tray_icon(overlay)
    threading.Thread(target=tray_icon.run, daemon=True).start()

    keyboard.add_hotkey("alt+s", overlay.show)
    keyboard.add_hotkey("esc", overlay.hide)

    try:
        keep_alive()
        overlay.run()
    except KeyboardInterrupt:
        print("Exiting...")
