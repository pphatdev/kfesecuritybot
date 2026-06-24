import json
import logging
from typing import Dict, Any
from app.services.db import get_db

logger = logging.getLogger(__name__)

async def get_setting(key: str, default: Any = None) -> Any:
    """Convenience function to get a single setting."""
    try:
        async with await get_db() as db:
            async with db.execute('SELECT value FROM settings WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
    except Exception as e:
        logger.error(f"Error getting setting {key}: {e}")
    return default

async def get_group_delay(chat_id: int) -> int:
    """Get the message delay configured for a specific group."""
    delays = await get_setting("group_delays", {})
    return int(delays.get(str(chat_id), 0))
