import threading
import keyboard
from .recorder import ScreenRecorder
from .overlay import OverlayApp
from .tray import create_tray_icon

if __name__ == "__main__":
    recorder = ScreenRecorder()
    overlay = OverlayApp(recorder)

    tray_icon = create_tray_icon(overlay)
    threading.Thread(target=tray_icon.run, daemon=True).start()

    keyboard.add_hotkey("alt+s", overlay.show)
    keyboard.add_hotkey("esc", overlay.hide)

    try:
        overlay.run()
    except KeyboardInterrupt:
        print("Exiting...")
