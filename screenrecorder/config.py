import json
import os

CONFIG_FILE = os.path.join(os.getcwd(), "config.json")


def load_region():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "region" in data:
                    return tuple(data["region"])
        except Exception:
            pass
    return None


def save_region(region):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"region": region}, f)
    except Exception as e:
        print(f"Failed to save config: {e}")
