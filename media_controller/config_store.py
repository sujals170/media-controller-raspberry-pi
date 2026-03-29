import json
import os

from .constants import CONFIG_FILE


def get_config():
    default = {"photo_interval": 5}
    if not os.path.exists(CONFIG_FILE):
        return default

    try:
        with open(CONFIG_FILE, encoding="utf-8") as handle:
            data = json.load(handle)
        interval = int(data.get("photo_interval", default["photo_interval"]))
        return {"photo_interval": max(1, interval)}
    except Exception:
        return default


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as handle:
        json.dump(config, handle)
