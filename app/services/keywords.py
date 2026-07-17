import json
import logging
import re
import time
from pathlib import Path

# Cache for sticker set unique file IDs: set_name -> (timestamp, [unique_ids])
_sticker_set_cache = {}
STICKER_CACHE_TTL = 3600  # 1 hour

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data"
KEYWORDS_FILE = DATA_DIR / "custom_keywords.json"

# --- Default built-in keywords (written to file on first run) ---
_DEFAULT_SPAM = [
    # Crypto / investment scams
    "crypto", "cryptocurrency", "bitcoin", "btc", "eth", "usdt", "nft",
    "crypto investment", "invest now", "trading signal", "forex",
    "profit guaranteed", "guaranteed profit", "guaranteed return",
    "1000%", "500%", "100% profit", "daily profit", "passive income",
    # Promotion / spam phrases
    "click here", "buy now", "earn money", "make money fast",
    "get rich", "free gift", "you are a winner", "free money",
    "dm me", "message me", "contact me for", "join now", "sign up now",
    "limited offer", "exclusive offer", "act now", "don't miss",
    # Gambling
    "casino", "online betting", "lottery", "jackpot", "bet now", "slots",
    # Adult content
    "adult", "18+", "xxx", "porn", "nude", "sex",
    # Scam patterns
    "scam link", "phishing", "giveaway", "airdrop", "double your",
    # Khmer spam
    "ចុចនៅទីនេះ", "ចុចត្រង់នេះ", "ទទួលបានប្រាក់", "វិនិយោគ",
    "កាស៊ីណូ", "ឈ្នះប្រាក់", "ផ្សងសំណាង", "ចូលរួមឥឡូវ",
    "ឈ្នះរង្វាន់", "រកប្រាក់", "អាសអាភាស", "ភាពយន្ដក្ដៅ",
]

_DEFAULT_TOXIC = [
    # English toxic
    "kill yourself", "kys", "go die", "i hate you", "you are worthless",
    "kill", "murder", "die", "threat", "attack",
    "idiot", "moron", "stupid", "loser", "retard", "shut up",
    "motherfucker", "fuck you", "piece of shit", "bitch", "asshole",
    "bastard", "damn you", "curse",
    # Khmer toxic
    "គួរតែស្លាប់", "ឆ្កែ", "ល្ងង់", "ជើងអំបាញ់",
    "ខ្ញុំស្អប់", "ទ្រុំ", "ក្មេងកាច", "ស្អាប",
    "ចោរ", "ក្រអឺតក្រទម", "ឯងហ្នឹង",
]

_DEFAULT_PATTERN = []

_DEFAULT_STICKER = []

_DEFAULT_FILE_EXT = [".exe", ".apk", ".bat", ".scr", ".vbs"]


def _load_all() -> dict:
    """
    Load keyword lists from JSON file.
    If the file doesn't exist, initialize it with the built-in defaults.
    """
    if not KEYWORDS_FILE.exists():
        data = {"spam": _DEFAULT_SPAM.copy(), "toxic": _DEFAULT_TOXIC.copy(), "pattern": _DEFAULT_PATTERN.copy(), "sticker": _DEFAULT_STICKER.copy(), "file_ext": _DEFAULT_FILE_EXT.copy()}
        _save(data)
        logger.info("Initialized keywords.json with built-in defaults.")
        return data

    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "pattern" not in data:
                data["pattern"] = _DEFAULT_PATTERN.copy()
            if "sticker" not in data:
                data["sticker"] = _DEFAULT_STICKER.copy()
            if "file_ext" not in data:
                data["file_ext"] = _DEFAULT_FILE_EXT.copy()
            return data
    except Exception as e:
        logger.error(f"Failed to load keywords.json: {e}")
        return {"spam": _DEFAULT_SPAM.copy(), "toxic": _DEFAULT_TOXIC.copy(), "pattern": _DEFAULT_PATTERN.copy(), "sticker": _DEFAULT_STICKER.copy(), "file_ext": _DEFAULT_FILE_EXT.copy()}


def _save(data: dict):
    """Save keyword lists to the JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_keyword(word: str, category: str, response: str = "") -> bool:
    """Add a keyword. Returns True if added, False if already exists."""
    word = word.strip() if category == "pattern" else word.strip().lower()
    data = _load_all()
    
    if category == "pattern":
        exists = any(item.get("word") == word if isinstance(item, dict) else item == word for item in data.get("pattern", []))
        if exists:
            return False
        data["pattern"].append({"word": word, "response": response})
    else:
        if word in data.get(category, []):
            return False
        data[category].append(word)
        
    _save(data)
    logger.info(f"Added {category} keyword: {word}")
    return True


def remove_keyword(word: str) -> bool:
    """Remove a keyword from any category. Returns True if found and removed."""
    word = word.strip()
    data = _load_all()
    removed = False
    
    for cat in ("spam", "toxic", "sticker", "file_ext"):
        target_word = word.lower()
        if target_word in data.get(cat, []):
            data[cat].remove(target_word)
            removed = True
            
    # Handle pattern category which might contain dictionaries
    if "pattern" in data:
        original_len = len(data["pattern"])
        data["pattern"] = [
            item for item in data["pattern"]
            if (item.get("word") if isinstance(item, dict) else item) != word
        ]
        if len(data["pattern"]) < original_len:
            removed = True

    if removed:
        _save(data)
        logger.info(f"Removed keyword: {word}")
    return removed


def get_custom_keywords() -> dict:
    """Return current keyword dict {spam: [...], toxic: [...]}."""
    return _load_all()


async def get_sticker_index(sticker, bot) -> int:
    """Get the 0-based index of a sticker within its sticker pack (set). Cached for 1 hour."""
    if not sticker or not sticker.set_name or not bot:
        return -1
    
    set_name = sticker.set_name
    now = time.time()
    
    # Check cache
    if set_name in _sticker_set_cache:
        timestamp, unique_ids = _sticker_set_cache[set_name]
        if now - timestamp < STICKER_CACHE_TTL:
            try:
                return unique_ids.index(sticker.file_unique_id)
            except ValueError:
                return -1
                
    # Fetch from Telegram API
    try:
        sticker_set = await bot.get_sticker_set(set_name)
        unique_ids = [s.file_unique_id for s in sticker_set.stickers]
        _sticker_set_cache[set_name] = (now, unique_ids)
        try:
            return unique_ids.index(sticker.file_unique_id)
        except ValueError:
            return -1
    except Exception as e:
        logger.error(f"Error fetching sticker set {set_name}: {e}")
        return -1


async def pre_check(text: str, sticker=None, bot=None, document_name: str = None) -> tuple[str, str | None] | None:
    """
    Check text against keyword lists.
    All keywords are read from the JSON file on every call — no restart needed.
    Returns ('Spam', None), ('Toxic', None), ('Pattern', custom_response), ('FileExt', custom_response) or None.
    """
    lower = text.lower()
    data = _load_all()

    if document_name:
        doc_lower = document_name.lower()
        for ext in data.get("file_ext", []):
            ext_str = ext.strip().lower()
            if ext_str and doc_lower.endswith(ext_str):
                return ("FileExt", f"Banned File Extension ({ext_str})")

    for kw in data.get("spam", []):
        if kw.lower() in lower:
            return ("Spam", None)

    for kw in data.get("toxic", []):
        if kw.lower() in lower:
            return ("Toxic", None)

    if sticker:
        logger.info(f"[Sticker Check] Checking sticker. set_name={sticker.set_name}, emoji={sticker.emoji}, file_unique_id={sticker.file_unique_id}")
        for kw in data.get("sticker", []):
            kw_str = kw.strip()
            kw_lower = kw_str.lower()
            logger.info(f"[Sticker Check] Comparing against rule: {kw_str}")
            if kw_lower.startswith("pack:"):
                # kw_str can be "pack:name", "pack:name:emoji", or "pack:name:index"
                parts = kw_str[5:].split(":", 1)
                target_pack = parts[0].strip()
                
                if sticker.set_name and target_pack.lower() == sticker.set_name.lower():
                    if len(parts) == 1:
                        # Ban entire pack
                        return ("Sticker", f"Banned Sticker Pack ({sticker.set_name})")
                    else:
                        sub_target = parts[1].strip()
                        if sub_target.isdigit():
                            target_index = int(sub_target)
                            sticker_idx = await get_sticker_index(sticker, bot)
                            if sticker_idx == target_index:
                                return ("Sticker", f"Banned Sticker in Pack {sticker.set_name} at index {target_index}")
                        else:
                            if sticker.emoji and sub_target == sticker.emoji:
                                return ("Sticker", f"Banned Sticker Emoji ({sticker.emoji}) in Pack ({sticker.set_name})")
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
