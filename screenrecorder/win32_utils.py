import ctypes

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20

user32 = ctypes.windll.user32
GetWindowLong = user32.GetWindowLongW
SetWindowLong = user32.SetWindowLongW


def passthrough_mouse_clicks(hwnd):
    style = GetWindowLong(hwnd, GWL_EXSTYLE)
    SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)


def capture_mouse_clicks(hwnd):
    style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    style &= ~WS_EX_TRANSPARENT  # Remove WS_EX_TRANSPARENT
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
