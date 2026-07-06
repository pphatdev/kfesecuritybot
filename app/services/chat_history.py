import json
import os
import logging
import time
from datetime import datetime
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '../../data/chat_history.json')

def load_history() -> dict:
    """Load all chat histories from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading chat history file: {e}")
        return {}

def save_history(data: dict):
    """Save the chat history database atomically using a temporary file."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    temp_file = HISTORY_FILE + '.tmp'
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, HISTORY_FILE)
    except Exception as e:
        logger.error(f"Error saving chat history file: {e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

def log_message(chat_id: int, message_id: int, sender_id: int, sender: str, text: str, is_bot: bool = False, sticker_id: str = None, media_type: str = None, media_name: str = None, buttons: list = None):
    """Append a message details entry to the chat's list, keeping only the last 100 entries."""
    if not chat_id:
        return
    data = load_history()
    str_chat_id = str(chat_id)
    
    chat_list = data.get(str_chat_id, [])
    now_str = datetime.now(ZoneInfo('Asia/Phnom_Penh')).strftime("%H:%M")
    
    msg_entry = {
        "message_id": message_id,
        "sender_id": sender_id,
        "sender": sender,
        "text": text,
        "timestamp": int(time.time()),
        "time": now_str,
        "is_bot": is_bot,
        "sticker_id": sticker_id,
        "media_type": media_type,
        "media_name": media_name,
        "buttons": buttons,
        "is_deleted": False,
        "delete_reason": None
    }
    
    # Filter out if already exists, then append
    chat_list = [m for m in chat_list if m.get("message_id") != message_id]
    chat_list.append(msg_entry)
    
    data[str_chat_id] = chat_list[-100:]
    save_history(data)

def mark_message_deleted(chat_id: int, message_id: int, reason: str):
    """Flag a specific message as deleted and state the reason."""
    if not chat_id:
        return
    data = load_history()
    str_chat_id = str(chat_id)
    if str_chat_id not in data:
        return
    
    chat_list = data[str_chat_id]
    for msg in chat_list:
        if msg.get("message_id") == message_id:
            msg["is_deleted"] = True
            msg["delete_reason"] = reason
            break
            
    data[str_chat_id] = chat_list
    save_history(data)
