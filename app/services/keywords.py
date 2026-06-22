import json
import logging
import re
from pathlib import Path

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


def _load_all() -> dict:
    """
    Load keyword lists from JSON file.
    If the file doesn't exist, initialize it with the built-in defaults.
    """
    if not KEYWORDS_FILE.exists():
        data = {"spam": _DEFAULT_SPAM.copy(), "toxic": _DEFAULT_TOXIC.copy(), "pattern": _DEFAULT_PATTERN.copy(), "sticker": _DEFAULT_STICKER.copy()}
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
            return data
    except Exception as e:
        logger.error(f"Failed to load keywords.json: {e}")
        return {"spam": _DEFAULT_SPAM.copy(), "toxic": _DEFAULT_TOXIC.copy(), "pattern": _DEFAULT_PATTERN.copy(), "sticker": _DEFAULT_STICKER.copy()}


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
    
    for cat in ("spam", "toxic", "sticker"):
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


def pre_check(text: str, sticker=None) -> tuple[str, str | None] | None:
    """
    Check text against keyword lists.
    All keywords are read from the JSON file on every call — no restart needed.
    Returns ('Spam', None), ('Toxic', None), ('Pattern', custom_response) or None.
    """
    lower = text.lower()
    data = _load_all()

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
