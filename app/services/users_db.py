import logging
from app.services.db import get_db

logger = logging.getLogger(__name__)

async def track_user(user_id: int, username: str):
    """
    Store or update the user's information.
    """
    if not user_id:
        return
        
    username_val = username.strip().lower() if username else ""
    str_id = str(user_id)
    
    try:
        async with await get_db() as db:
            await db.execute('''
                INSERT INTO users (id, username)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username=excluded.username
            ''', (str_id, username_val))
            await db.commit()
    except Exception as e:
        logger.error(f"Error tracking user: {e}")
