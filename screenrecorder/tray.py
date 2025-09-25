"""
System tray integration for screen recorder application.

This module provides system tray icon functionality with context menu
for quick access to recording features and application controls.
"""

import webbrowser
import pystray
from PIL import Image, ImageDraw


def create_tray_icon(overlay_app):
    """
    Create system tray icon with context menu.

    Args:
        overlay_app: Reference to the overlay window application

    Returns:
        pystray.Icon: Configured tray icon instance
    """

    def quit_app(icon, item):
        """Quit the application cleanly."""
        icon.stop()
        overlay_app.root.after(0, overlay_app.root.quit)

    def open_project_homepage(icon, item):
        """Open project homepage in default browser."""
        webbrowser.open("https://github.com/cmdr2/screenrecorder/")

    # Create simple red square icon
    image = _create_tray_image()

    # Build context menu
    menu = pystray.Menu(
        pystray.MenuItem("Record (Alt+S)", lambda icon, item: overlay_app.show(), default=True),
        pystray.MenuItem("About", open_project_homepage),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app),
    )

    return pystray.Icon("recorder", image, "Screen Recorder", menu)


def _create_tray_image():
    """
    Create a simple icon image for the system tray.

    Returns:
        PIL.Image: Icon image (red square on black background)
    """
    image = Image.new("RGB", (64, 64), (0, 0, 0))  # Black background
    draw = ImageDraw.Draw(image)
    draw.rectangle([16, 16, 48, 48], fill=(255, 0, 0))  # Red square
    return image
