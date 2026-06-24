import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from telegram.ext import Application

logger = logging.getLogger(__name__)

SCHEDULE_DB_FILE = os.path.join(os.path.dirname(__file__), '../../data/scheduled_messages.json')

def load_scheduled_messages() -> list:
    """Load all scheduled messages."""
    if not os.path.exists(SCHEDULE_DB_FILE):
        return []
    try:
        with open(SCHEDULE_DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading scheduled messages DB: {e}")
        return []

def save_scheduled_messages(messages: list):
    """Save the scheduled messages list atomically."""
    os.makedirs(os.path.dirname(SCHEDULE_DB_FILE), exist_ok=True)
    temp_path = SCHEDULE_DB_FILE + '.tmp'
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, SCHEDULE_DB_FILE)
    except Exception as e:
        logger.error(f"Error saving scheduled messages DB: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

async def check_and_send_scheduled_messages(application: Application):
    """Scan and broadcast scheduled messages that are due."""
    messages = load_scheduled_messages()
    now_utc = datetime.now(timezone.utc)
    
    modified = False
    for msg in messages:
        if msg.get("status") != "pending":
            continue
            
        try:
            send_at_str = msg["sendAt"]
            # Convert 'Z' to '+00:00' for compatibility with datetime.fromisoformat in older Pythons
            if send_at_str.endswith("Z"):
                send_at_str = send_at_str[:-1] + "+00:00"
            send_at = datetime.fromisoformat(send_at_str)
        except Exception as e:
            logger.error(f"Invalid datetime format for message {msg.get('id')}: {e}")
            msg["status"] = "failed"
            msg["error"] = f"Invalid datetime format: {e}"
            modified = True
            continue
            
        if send_at <= now_utc:
            logger.info(f"Sending scheduled message: {msg.get('id')}")
            msg["status"] = "sending"
            save_scheduled_messages(messages)
            
            chat_ids = msg.get("chatIds", [])
            text = msg.get("message", "")
            file_path = msg.get("file_path")
            file_type = msg.get("file_type")
            
            results = {}
            success_count = 0
            fail_count = 0
            
            for chat_id in chat_ids:
                try:
                    if file_path and os.path.exists(file_path):
                        with open(file_path, 'rb') as media_file:
                            if file_type == 'photo':
                                await application.bot.send_photo(chat_id=chat_id, photo=media_file, caption=text, parse_mode="HTML")
                            elif file_type == 'video':
                                await application.bot.send_video(chat_id=chat_id, video=media_file, caption=text, parse_mode="HTML")
                            else:
                                await application.bot.send_document(chat_id=chat_id, document=media_file, caption=text, parse_mode="HTML")
                    else:
                        await application.bot.send_message(
                            chat_id=chat_id,
                            text=text,
                            parse_mode="HTML"
                        )
                    results[str(chat_id)] = {"success": True}
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send scheduled message {msg.get('id')} to {chat_id}: {e}")
                    results[str(chat_id)] = {"success": False, "error": str(e)}
                    fail_count += 1
                # Small delay to avoid hitting rate limits
                await asyncio.sleep(0.1)
                
            msg["results"] = results
            msg["sentAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            
            if fail_count == 0:
                msg["status"] = "sent"
            elif success_count == 0:
                msg["status"] = "failed"
            else:
                msg["status"] = "partially_failed"
                
            # Reload in case something changed in the file during execution
            latest_messages = load_scheduled_messages()
            updated = False
            for m in latest_messages:
                if m.get("id") == msg.get("id"):
                    m.update(msg)
                    updated = True
            if not updated:
                latest_messages.append(msg)
            messages = latest_messages
            save_scheduled_messages(messages)
            modified = False
            
            # Clean up the file if it existed
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Failed to delete scheduled media file {file_path}: {e}")

    if modified:
        save_scheduled_messages(messages)

async def run_scheduler(application: Application):
    """Background loop to check and send messages periodically."""
    logger.info("Scheduled message background worker starting...")
    while True:
        try:
            await check_and_send_scheduled_messages(application)
        except asyncio.CancelledError:
            logger.info("Scheduled message worker cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in scheduled message worker loop: {e}", exc_info=True)
        await asyncio.sleep(10)
