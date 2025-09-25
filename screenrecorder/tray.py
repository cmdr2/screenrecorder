import pystray
from PIL import Image, ImageDraw


def create_tray_icon(overlay_app):
    def quit_app(icon, item):
        icon.stop()
        overlay_app.root.after(0, overlay_app.root.quit)

    def open_project_homepage(icon, item):
        import webbrowser

        webbrowser.open("https://github.com/cmdr2/screenrecorder/")

    image = Image.new("RGB", (64, 64), (0, 0, 0))
    d = ImageDraw.Draw(image)
    d.rectangle([16, 16, 48, 48], fill=(255, 0, 0))

    menu = pystray.Menu(
        pystray.MenuItem("About", open_project_homepage),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app),
    )

    return pystray.Icon("recorder", image, "Recorder", menu)
