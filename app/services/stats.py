import logging
from datetime import datetime
from app.services.db import get_db

logger = logging.getLogger(__name__)

async def increment_scanned():
    try:
        async with await get_db() as db:
            await db.execute('''
                INSERT INTO stats (id, total_messages_scanned, spam_toxic_blocked)
                VALUES (1, 1, 0)
                ON CONFLICT(id) DO UPDATE SET
                    total_messages_scanned = total_messages_scanned + 1
            ''')
            await db.commit()
    except Exception as e:
        logger.error(f"Error incrementing scanned: {e}")

async def log_violation(user_id: int, username: str, reason: str, category: str, text: str):
    try:
        async with await get_db() as db:
            await db.execute('''
                INSERT INTO stats (id, total_messages_scanned, spam_toxic_blocked)
                VALUES (1, 0, 1)
                ON CONFLICT(id) DO UPDATE SET
                    spam_toxic_blocked = spam_toxic_blocked + 1
            ''')
            
            now_str = datetime.now().strftime("%I:%M %p")
            await db.execute('''
                INSERT INTO activity_logs (time, type, text, username)
                VALUES (?, ?, ?, ?)
            ''', (now_str, category, f"Deleted message from <b>@{username}</b> (Reason: {reason})", username))
            
            str_user_id = str(user_id)
            last_violation = f"Today, {now_str} ({category.capitalize()})"
            await db.execute('''
                INSERT INTO user_violations (user_id, username, strikes, last_violation)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    strikes = strikes + 1,
                    last_violation = excluded.last_violation
            ''', (str_user_id, username, last_violation))
            
            await db.commit()
    except Exception as e:
        logger.error(f"Error logging violation: {e}")

async def log_system_action(text: str):
    try:
        async with await get_db() as db:
            now_str = datetime.now().strftime("%I:%M %p")
            await db.execute('''
                INSERT INTO activity_logs (time, type, text, username)
                VALUES (?, ?, ?, ?)
            ''', (now_str, "action", text, "System"))
            await db.commit()
    except Exception as e:
        logger.error(f"Error logging system action: {e}")

async def get_user_strikes(user_id: int) -> int:
    try:
        async with await get_db() as db:
            async with db.execute('SELECT strikes FROM user_violations WHERE user_id = ?', (str(user_id),)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    except Exception as e:
        logger.error(f"Error getting user strikes: {e}")
        return 0
