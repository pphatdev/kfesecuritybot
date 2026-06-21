import json
import os
import logging

logger = logging.getLogger(__name__)

ALLOWED_USERS_FILE = os.path.join(os.path.dirname(__file__), '../../data/allowed_users.json')

def load_allowed_users() -> dict:
    """Load allowed users from data/allowed_users.json."""
    if not os.path.exists(ALLOWED_USERS_FILE):
        return {"usernames": [], "user_ids": []}
    try:
        with open(ALLOWED_USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading allowed users file: {e}")
        return {"usernames": [], "user_ids": []}

def save_allowed_users(data: dict):
    """Save allowed users data."""
    os.makedirs(os.path.dirname(ALLOWED_USERS_FILE), exist_ok=True)
    try:
        with open(ALLOWED_USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving allowed users file: {e}")

def add_allowed_user(username_or_id: str) -> bool:
    """Add a username or ID to the allowed list. Returns True if added."""
    data = load_allowed_users()
    val = username_or_id.strip().lower().replace('@', '')
    
    if not val:
        return False
        
    if val.isdigit():
        if "user_ids" not in data:
            data["user_ids"] = []
        if val not in data["user_ids"]:
            data["user_ids"].append(val)
            save_allowed_users(data)
            return True
    else:
        if "usernames" not in data:
            data["usernames"] = []
        if val not in data["usernames"]:
            data["usernames"].append(val)
            save_allowed_users(data)
            return True
            
    return False

def remove_allowed_user(username_or_id: str) -> bool:
    """Remove a username or ID from the allowed list. Returns True if removed."""
    data = load_allowed_users()
    val = username_or_id.strip().lower().replace('@', '')
    
    if not val:
        return False
        
    if val.isdigit():
        if "user_ids" in data and val in data["user_ids"]:
            data["user_ids"].remove(val)
            save_allowed_users(data)
            return True
    else:
        if "usernames" in data and val in data["usernames"]:
            data["usernames"].remove(val)
            save_allowed_users(data)
            return True
            
    return False

def is_user_allowed(user_id: int, username: str) -> bool:
    """Check if a user (by ID or username) is authorized in env or JSON list."""
    # Check parent .env
    admin_usernames = [u.strip().lower() for u in (os.getenv("DASHBOARD_ADMINS") or "").split(",") if u.strip()]
    admin_ids = [i.strip() for i in (os.getenv("DASHBOARD_ADMIN_IDS") or "").split(",") if i.strip()]
    
    if str(user_id) in admin_ids or (username and username.lower() in admin_usernames):
        return True
        
    # Check JSON database
    data = load_allowed_users()
    if str(user_id) in data.get("user_ids", []):
        return True
    if username and username.lower() in data.get("usernames", []):
        return True
        
    return False
