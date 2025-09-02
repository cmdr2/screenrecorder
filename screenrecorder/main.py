import threading
import keyboard
from .recorder import ScreenRecorder
from .window import ScreenRecorderWindow
from .tray import create_tray_icon


# Periodic no-op to keep event loop responsive to signals
def keep_alive():
    window.root.after(1000, keep_alive)


if __name__ == "__main__":
    recorder = ScreenRecorder()
    window = ScreenRecorderWindow(recorder)

    tray_icon = create_tray_icon(window)
    threading.Thread(target=tray_icon.run, daemon=True).start()

    keyboard.add_hotkey("alt+s", window.show)
    keyboard.add_hotkey("esc", window.hide)

    try:
        keep_alive()
        window.mainloop()
    except KeyboardInterrupt:
        print("Exiting...")
