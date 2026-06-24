import logging
from datetime import datetime
from app.services.db import get_db

logger = logging.getLogger(__name__)

async def log_private_chat(user_id: int, username: str, message: str) -> None:
    """Log a private chat message to the database."""
    try:
        async with await get_db() as db:
            timestamp = datetime.now().isoformat()
            await db.execute(
                'INSERT INTO private_chats (user_id, username, message, timestamp) VALUES (?, ?, ?, ?)',
                (str(user_id), username, message, timestamp)
            )
            await db.commit()
    except Exception as e:
        logger.error(f"Error logging private chat: {e}")
