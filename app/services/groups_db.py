import json
import os
import logging

logger = logging.getLogger(__name__)

GROUPS_DB_FILE = os.path.join(os.path.dirname(__file__), '../../data/groups.json')

def load_groups() -> dict:
    """Load the mapping of chat_id (string) to group data."""
    if not os.path.exists(GROUPS_DB_FILE):
        return {}
    try:
        with open(GROUPS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading groups DB file: {e}")
        return {}

def save_groups(data: dict):
    """Save the groups DB data."""
    os.makedirs(os.path.dirname(GROUPS_DB_FILE), exist_ok=True)
    try:
        with open(GROUPS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving groups DB file: {e}")

def track_group(chat_id: int, title: str):
    """
    Store or update the group's information.
    Saves a mapping like:
    {
      "-100123456789": {
        "title": "My Awesome Group"
      }
    }
    """
    if not chat_id:
        return
        
    data = load_groups()
    str_id = str(chat_id)
    title_val = title.strip() if title else f"Group {str_id}"
    
    current_data = data.get(str_id, {})
    
    if current_data.get("title") != title_val:
        data[str_id] = {
            "title": title_val
        }
        save_groups(data)
