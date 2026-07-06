import json
import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

STATS_FILE = os.path.join(os.path.dirname(__file__), '../../data/dashboard_stats.json')

# Default empty state
DEFAULT_STATS = {
    "total_messages_scanned": 0,
    "spam_toxic_blocked": 0,
    "recent_activity": [],
    "violations": {}
}

def load_stats() -> dict:
    if not os.path.exists(STATS_FILE):
        return DEFAULT_STATS.copy()
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading stats file: {e}")
        return DEFAULT_STATS.copy()

def save_stats(data: dict):
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving stats file: {e}")

def increment_scanned():
    data = load_stats()
    data['total_messages_scanned'] = data.get('total_messages_scanned', 0) + 1
    save_stats(data)

def log_violation(user_id: int, username: str, reason: str, category: str, text: str):
    data = load_stats()
    
    # Update global counts
    data['spam_toxic_blocked'] = data.get('spam_toxic_blocked', 0) + 1
    
    # Get current time
    now_str = datetime.now(ZoneInfo('Asia/Phnom_Penh')).strftime("%H:%M")
    
    # Update recent activity (keep last 50)
    activity = {
        "time": now_str,
        "type": category, # "toxic" or "spam" or "action"
        "text": f"Deleted message from <b>@{username}</b> (Reason: {reason})",
        "username": username
    }
    activities = data.get('recent_activity', [])
    activities.insert(0, activity)
    data['recent_activity'] = activities[:50]
    
    # Update user violations
    violations = data.get('violations', {})
    str_user_id = str(user_id)
    
    user_data = violations.get(str_user_id, {
        "username": username,
        "strikes": 0,
        "last_violation": ""
    })
    
    user_data["strikes"] += 1
    user_data["last_violation"] = f"Today, {now_str} ({category.capitalize()})"
    # Keep the username fresh
    user_data["username"] = username
    
    violations[str_user_id] = user_data
    data['violations'] = violations
    
    save_stats(data)

def log_system_action(text: str):
    data = load_stats()
    now_str = datetime.now(ZoneInfo('Asia/Phnom_Penh')).strftime("%H:%M")
    
    activity = {
        "time": now_str,
        "type": "action",
        "text": text,
        "username": "System"
    }
    
    activities = data.get('recent_activity', [])
    activities.insert(0, activity)
    data['recent_activity'] = activities[:50]
    
    save_stats(data)

def get_user_strikes(user_id: int) -> int:
    data = load_stats()
    violations = data.get('violations', {})
    user_data = violations.get(str(user_id), {})
    return user_data.get("strikes", 0)
