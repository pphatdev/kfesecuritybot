import logging
from app.services.db import get_db

logger = logging.getLogger(__name__)

async def track_group(chat_id: int, title: str):
    """
    Store or update the group's information.
    """
    if not chat_id:
        return
        
    str_id = str(chat_id)
    title_val = title.strip() if title else f"Group {str_id}"
    
    try:
        async with await get_db() as db:
            await db.execute('''
                INSERT INTO groups (id, title)
                VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title
            ''', (str_id, title_val))
            await db.commit()
    except Exception as e:
        logger.error(f"Error tracking group: {e}")
