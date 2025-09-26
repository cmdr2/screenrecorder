"""
Utility functions for screen recorder application.

This module provides platform-specific utilities for:
- Window transparency and click-through behavior
- File operations (copying to clipboard)
- FFmpeg executable location
"""

import platform
import sys
import os

# Constants
UNSUPPORTED_PLATFORM_ERROR = (
    "Easy Screen Recorder is currently only supported on Windows. "
    "Please visit https://github.com/cmdr2/screenrecorder"
)

# Windows-specific constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20

# Platform detection
OS_NAME = platform.system()

# Import Windows-specific modules only on Windows
if OS_NAME == "Windows":
    import ctypes

    user32 = ctypes.windll.user32
    GetWindowLong = user32.GetWindowLongW
    SetWindowLong = user32.SetWindowLongW
else:
    raise RuntimeError(UNSUPPORTED_PLATFORM_ERROR)


def passthrough_mouse_clicks(hwnd):
    """Enable click-through behavior for a window handle."""
    if OS_NAME != "Windows":
        raise RuntimeError(UNSUPPORTED_PLATFORM_ERROR)

    style = GetWindowLong(hwnd, GWL_EXSTYLE)
    SetWindowLong(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT)


def capture_mouse_clicks(hwnd):
    """Disable click-through behavior for a window handle."""
    if OS_NAME != "Windows":
        raise RuntimeError(UNSUPPORTED_PLATFORM_ERROR)

    style = GetWindowLong(hwnd, GWL_EXSTYLE)
    style &= ~WS_EX_TRANSPARENT  # Remove WS_EX_TRANSPARENT
    SetWindowLong(hwnd, GWL_EXSTYLE, style)


def copy_files_to_clipboard(file_paths):
    """Copy file paths to system clipboard (Windows only)."""
    if OS_NAME != "Windows":
        raise RuntimeError(UNSUPPORTED_PLATFORM_ERROR)

    if isinstance(file_paths, str):
        file_paths = [file_paths]

    _copy_files_to_clipboard_windows(file_paths)


def _copy_files_to_clipboard_windows(file_paths):
    import struct
    import ctypes
    import win32clipboard as wc
    import win32con

    # Memory flags
    GMEM_MOVEABLE = 0x0002
    GMEM_ZEROINIT = 0x0040
    GHND = GMEM_MOVEABLE | GMEM_ZEROINIT

    # Kernel32 with proper prototypes
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.restype = ctypes.c_int

    # Double-null-terminated UTF-16LE list
    file_list = ("\0".join(file_paths) + "\0\0").encode("utf-16le")

    # DROPFILES struct: pFiles=20, pt=(0,0), fNC=0, fWide=1
    dropfiles = struct.pack("<IiiiI", 20, 0, 0, 0, 1)
    data = dropfiles + file_list

    hglobal = kernel32.GlobalAlloc(GHND, len(data))
    if not hglobal:
        raise OSError("GlobalAlloc failed")

    ptr = kernel32.GlobalLock(hglobal)
    if not ptr:
        kernel32.GlobalFree(hglobal)
        raise OSError("GlobalLock failed")

    ctypes.memmove(ptr, data, len(data))
    kernel32.GlobalUnlock(hglobal)

    wc.OpenClipboard()
    try:
        wc.EmptyClipboard()
        wc.SetClipboardData(win32con.CF_HDROP, hglobal)
        hglobal = None  # system owns memory now
        print("Copied to clipboard")
    finally:
        wc.CloseClipboard()


def get_ffmpeg_path():
    """
    Locate FFmpeg executable in common installation locations.

    Returns:
        str: Path to FFmpeg executable

    Raises:
        FileNotFoundError: If FFmpeg executable is not found
    """
    exe_dir = os.path.dirname(sys.executable)
    module_dir = os.path.dirname(os.path.dirname(__file__))

    ffmpeg_candidates = [
        os.path.join(exe_dir, "bin", "ffmpeg.exe"),
        os.path.join(exe_dir, "bin", "ffmpeg"),
        os.path.join(module_dir, "bin", "ffmpeg.exe"),
        os.path.join(module_dir, "bin", "ffmpeg"),
    ]

    for candidate in ffmpeg_candidates:
        if os.path.exists(candidate):
            return candidate

    raise FileNotFoundError(
        "FFmpeg executable not found. Please ensure ffmpeg.exe is in the 'bin' "
        "folder next to the application or module directory."
    )
