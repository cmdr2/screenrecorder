import pystray
from PIL import Image, ImageDraw


def create_tray_icon(overlay_app):
    def quit_app(icon, item):
        icon.stop()
        overlay_app.root.after(0, overlay_app.root.quit)

    image = Image.new("RGB", (64, 64), (0, 0, 0))
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill=(255, 0, 0))

    menu = pystray.Menu(pystray.MenuItem("Quit", quit_app))

    return pystray.Icon("recorder", image, "Recorder", menu)
