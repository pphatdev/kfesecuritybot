import logging
import os
from app.services.db import get_db

logger = logging.getLogger(__name__)

async def add_allowed_user(username_or_id: str) -> bool:
    val = username_or_id.strip().lower().replace('@', '')
    if not val:
        return False
        
    type_val = "id" if val.isdigit() else "username"
    try:
        async with await get_db() as db:
            async with db.execute('SELECT id FROM allowed_users WHERE type = ? AND value = ?', (type_val, val)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return False
            await db.execute('INSERT INTO allowed_users (type, value) VALUES (?, ?)', (type_val, val))
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Error adding allowed user: {e}")
        return False

async def remove_allowed_user(username_or_id: str) -> bool:
    val = username_or_id.strip().lower().replace('@', '')
    if not val:
        return False
        
    type_val = "id" if val.isdigit() else "username"
    try:
        async with await get_db() as db:
            cursor = await db.execute('DELETE FROM allowed_users WHERE type = ? AND value = ?', (type_val, val))
            await db.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error removing allowed user: {e}")
        return False

async def is_user_allowed(user_id: int, username: str) -> bool:
    admin_usernames = [u.strip().lower() for u in (os.getenv("DASHBOARD_ADMINS") or "").split(",") if u.strip()]
    admin_ids = [i.strip() for i in (os.getenv("DASHBOARD_ADMIN_IDS") or "").split(",") if i.strip()]
    
    if str(user_id) in admin_ids or (username and username.lower() in admin_usernames):
        return True
        
    try:
        async with await get_db() as db:
            async with db.execute('SELECT value FROM allowed_users WHERE type = "id"') as cursor:
                allowed_ids = [row[0] for row in await cursor.fetchall()]
            if str(user_id) in allowed_ids:
                return True
                
            async with db.execute('SELECT value FROM allowed_users WHERE type = "username"') as cursor:
                allowed_usernames = [row[0].lower() for row in await cursor.fetchall()]
            if username and username.lower() in allowed_usernames:
                return True
    except Exception as e:
        logger.error(f"Error checking allowed user: {e}")
        
    return False
