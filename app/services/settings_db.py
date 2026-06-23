import json
import os
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path(__file__).parent.parent.parent / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "group_delays": {} # Format: {"chat_id_str": delay_seconds}
}

def load_settings() -> Dict[str, Any]:
    """Load settings from settings.json."""
    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Merge with defaults to ensure all keys exist
            settings = DEFAULT_SETTINGS.copy()
            settings.update(data)
            # Ensure group_delays is a dict
            if not isinstance(settings.get("group_delays"), dict):
                settings["group_delays"] = {}
            return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to settings.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

def get_setting(key: str, default: Any = None) -> Any:
    """Convenience function to get a single setting."""
    settings = load_settings()
    return settings.get(key, default)

def get_group_delay(chat_id: int) -> int:
    """Get the message delay configured for a specific group."""
    settings = load_settings()
    delays = settings.get("group_delays", {})
    return int(delays.get(str(chat_id), 0))
