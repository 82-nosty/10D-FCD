# -*- coding: utf-8 -*-
"""
10D FCD - Persistent Settings Manager (%APPDATA%/10D_FCD/settings.json)
Saves & restores IP, COM port, Language, Media source, and HUD tuning across restarts.
"""
import json
from config import SETTINGS_FILE, DEFAULT_TARGET_FPS, DEFAULT_JPEG_QUALITY


DEFAULT_SETTINGS = {
    "lang": "KO",
    "com_port": "",
    "target_ip": "",
    "wifi_ssid": "",
    "wifi_pw": "",
    "media_mode": "DEMO",
    "media_path": "",
    "show_cpu": True,
    "show_ram": True,
    "show_time": True,
    "show_fps": True,
    "hud_on_media": False,
    "fps": DEFAULT_TARGET_FPS,
    "quality": 85,
}


class SettingsManager:
    @staticmethod
    def load() -> dict:
        data = dict(DEFAULT_SETTINGS)
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    data.update(loaded)
            except Exception:
                pass
        return data

    @staticmethod
    def save(data: dict):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

