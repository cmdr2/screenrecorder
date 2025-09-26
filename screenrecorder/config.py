"""
Configuration management for screen recorder application.

This module handles persistent storage and retrieval of application settings
including recording region coordinates and UI panel positions.
"""

import json
import os

CONFIG_FILE = os.path.join(os.getcwd(), "config.json")

CAPTURE_REGION = "capture_region"
MAIN_PANEL_POSITION = "main_panel_position"


def _load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def _save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save config: {e}")


def get_region():
    """
    Get the saved recording region coordinates.

    Returns:
        tuple: (x, y, width, height) or None if not set
    """
    data = _load_config()
    region = data.get(CAPTURE_REGION)
    if region and isinstance(region, list) and len(region) == 4:
        return tuple(region)
    return None


def set_region(region):
    """
    Save recording region coordinates.

    Args:
        region (tuple): (x, y, width, height) coordinates
    """
    data = _load_config()
    data[CAPTURE_REGION] = list(region)
    _save_config(data)


def get_panel_position():
    """
    Get the saved UI panel position.

    Returns:
        tuple: (x, y) position or None if not set
    """
    data = _load_config()
    pos = data.get(MAIN_PANEL_POSITION)
    if pos and isinstance(pos, list) and len(pos) == 2:
        return tuple(pos)
    return None


def set_panel_position(position):
    """
    Save UI panel position.

    Args:
        position (tuple): (x, y) position coordinates
    """
    data = _load_config()
    data[MAIN_PANEL_POSITION] = list(position)
    _save_config(data)
