import json
import logging
import re
from app.services.db import get_db

logger = logging.getLogger(__name__)

async def _load_all() -> dict:
    """Load keyword lists from DB."""
    data = {"spam": [], "toxic": [], "pattern": [], "sticker": []}
    try:
        async with await get_db() as db:
            async with db.execute('SELECT word, category, response FROM keywords') as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    word, category, response = row[0], row[1], row[2]
                    if category == "pattern":
                        data["pattern"].append({"word": word, "response": response})
                    elif category in data:
                        data[category].append(word)
    except Exception as e:
        logger.error(f"Failed to load keywords from DB: {e}")
    return data

async def add_keyword(word: str, category: str, response: str = "") -> bool:
    """Add a keyword. Returns True if added, False if already exists."""
    word = word.strip() if category == "pattern" else word.strip().lower()
    
    try:
        async with await get_db() as db:
            async with db.execute('SELECT id FROM keywords WHERE word = ? AND category = ?', (word, category)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return False
            await db.execute('INSERT INTO keywords (word, category, response) VALUES (?, ?, ?)', (word, category, response))
            await db.commit()
            logger.info(f"Added {category} keyword: {word}")
            return True
    except Exception as e:
        logger.error(f"Error adding keyword: {e}")
        return False

async def remove_keyword(word: str) -> bool:
    """Remove a keyword from any category. Returns True if found and removed."""
    word = word.strip()
    try:
        async with await get_db() as db:
            cursor = await db.execute('DELETE FROM keywords WHERE word = ? OR word = ?', (word, word.lower()))
            await db.commit()
            if cursor.rowcount > 0:
                logger.info(f"Removed keyword: {word}")
                return True
    except Exception as e:
        logger.error(f"Error removing keyword: {e}")
    return False

async def get_custom_keywords() -> dict:
    """Return current keyword dict {spam: [...], toxic: [...]}."""
    return await _load_all()

async def pre_check(text: str, sticker=None) -> tuple[str, str | None] | None:
    """
    Check text against keyword lists.
    Returns ('Spam', None), ('Toxic', None), ('Pattern', custom_response) or None.
    """
    lower = text.lower()
    data = await _load_all()

    for kw in data.get("spam", []):
        if kw.lower() in lower:
            return ("Spam", None)

    for kw in data.get("toxic", []):
        if kw.lower() in lower:
            return ("Toxic", None)

    if sticker:
        for kw in data.get("sticker", []):
            kw_str = kw.strip()
            kw_lower = kw_str.lower()
            if kw_lower.startswith("pack:"):
                target = kw_str[5:]
                if sticker.set_name and target.lower() == sticker.set_name.lower():
                    return ("Sticker", f"Banned Sticker Pack ({sticker.set_name})")
            elif kw_lower.startswith("emoji:"):
                target = kw_str[6:]
                if sticker.emoji and target == sticker.emoji:
                    return ("Sticker", f"Banned Sticker Emoji ({sticker.emoji})")
            elif kw_lower.startswith("id:"):
                target = kw_str[3:]
                if sticker.file_unique_id and target == sticker.file_unique_id:
                    return ("Sticker", f"Banned Sticker ID ({sticker.file_unique_id})")
            else:
                # Default to pack matching for backwards compatibility
                if sticker.set_name and kw_str.lower() == sticker.set_name.lower():
                    return ("Sticker", f"Banned Sticker Pack ({sticker.set_name})")

    for item in data.get("pattern", []):
        if isinstance(item, dict):
            pat = item.get("word", "")
            response = item.get("response", None)
            if not response:
                response = None
        else:
            pat = item
            response = None
            
        try:
            if re.search(pat, text, re.IGNORECASE):
                return ("Pattern", response)
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pat}': {e}")
            continue

    return None
