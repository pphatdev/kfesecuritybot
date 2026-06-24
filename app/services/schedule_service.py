import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from telegram.ext import Application
from app.services.db import get_db

logger = logging.getLogger(__name__)

async def load_scheduled_messages() -> list:
    try:
        async with await get_db() as db:
            async with db.execute("SELECT id, message, chat_ids, send_at, status, created_at, file_path, file_type, sent_at, results, error FROM scheduled_messages WHERE status = 'pending'") as cursor:
                rows = await cursor.fetchall()
                messages = []
                for row in rows:
                    messages.append({
                        "id": row[0],
                        "message": row[1],
                        "chatIds": json.loads(row[2]) if row[2] else [],
                        "sendAt": row[3],
                        "status": row[4],
                        "createdAt": row[5],
                        "file_path": row[6],
                        "file_type": row[7],
                        "sentAt": row[8],
                        "results": json.loads(row[9]) if row[9] else {},
                        "error": row[10]
                    })
                return messages
    except Exception as e:
        logger.error(f"Error loading scheduled messages: {e}")
        return []

async def save_scheduled_message(msg: dict):
    try:
        async with await get_db() as db:
            await db.execute('''
                UPDATE scheduled_messages 
                SET status = ?, 
                    sent_at = ?, 
                    results = ?, 
                    error = ?
                WHERE id = ?
            ''', (msg.get("status"), msg.get("sentAt"), json.dumps(msg.get("results", {})), msg.get("error"), msg.get("id")))
            await db.commit()
    except Exception as e:
        logger.error(f"Error saving scheduled message: {e}")

async def check_and_send_scheduled_messages(application: Application):
    messages = await load_scheduled_messages()
    now_utc = datetime.now(timezone.utc)
    
    for msg in messages:
        try:
            send_at_str = msg["sendAt"]
            if send_at_str.endswith("Z"):
                send_at_str = send_at_str[:-1] + "+00:00"
            send_at = datetime.fromisoformat(send_at_str)
        except Exception as e:
            logger.error(f"Invalid datetime format for message {msg.get('id')}: {e}")
            msg["status"] = "failed"
            msg["error"] = f"Invalid datetime format: {e}"
            await save_scheduled_message(msg)
            continue
            
        if send_at <= now_utc:
            logger.info(f"Sending scheduled message: {msg.get('id')}")
            msg["status"] = "sending"
            await save_scheduled_message(msg)
            
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
                await asyncio.sleep(0.1)
                
            msg["results"] = results
            msg["sentAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            
            if fail_count == 0:
                msg["status"] = "sent"
            elif success_count == 0:
                msg["status"] = "failed"
            else:
                msg["status"] = "partially_failed"
                
            await save_scheduled_message(msg)
            
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Failed to delete scheduled media file {file_path}: {e}")

async def run_scheduler(application: Application):
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
