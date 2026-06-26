import json
import os
import logging
import time

logger = logging.getLogger(__name__)

USERS_DB_FILE = os.path.join(os.path.dirname(__file__), '../../data/users.json')

def load_users() -> dict:
    """Load the mapping of user_id (string) to user data."""
    if not os.path.exists(USERS_DB_FILE):
        return {}
    try:
        with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading users DB file: {e}")
        return {}

def save_users(data: dict):
    """Save the users DB data."""
    os.makedirs(os.path.dirname(USERS_DB_FILE), exist_ok=True)
    try:
        with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving users DB file: {e}")

def track_user(user_id: int, username: str):
    """
    Store or update the user's information.
    Saves a mapping like:
    {
      "12345": {
        "username": "pphat"
      }
    }
    """
    if not user_id:
        return
        
    data = load_users()
    str_id = str(user_id)
    
    # We only care about tracking if they have a username we might want to look up
    username_val = username.strip().lower() if username else ""
    
    current_data = data.get(str_id, {})
    
    if current_data.get("username") != username_val:
        current_data["username"] = username_val
        data[str_id] = current_data
        save_users(data)

def record_user_mention_or_reply(user_id: int, username: str):
    """Flag that a user has had a bot mention or reply and record timestamp."""
    if not user_id:
        return
    data = load_users()
    str_id = str(user_id)
    username_val = username.strip().lower() if username else ""
    
    current_data = data.get(str_id, {})
    current_data["username"] = username_val
    current_data["has_mention_or_reply"] = True
    current_data["last_mention_or_reply_at"] = int(time.time())
    data[str_id] = current_data
    save_users(data)

