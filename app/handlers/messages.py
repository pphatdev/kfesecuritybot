import logging
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden
from app.services.keywords import pre_check
from app.handlers.commands import _bot_intro_html
from app.services.stats import increment_scanned, log_violation, get_user_strikes

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages. Handles mentions, keyword filter, and AI detection."""
    message = update.message
    
    # Extract text from normal messages, captions, or sticker emojis
    text = message.text or message.caption or ""
    if message.sticker:
        # Exception: Do NOT block the sticker if its emoji is 🙂
        if message.sticker.emoji and "🙂" in message.sticker.emoji:
            pass # Safe sticker, ignore its set_name and emoji
        else:
            if message.sticker.emoji:
                text += f" {message.sticker.emoji}"
            if message.sticker.set_name:
                text += f" {message.sticker.set_name}"
        
    text = text.strip()

    if not text:
        return

    # Increment real-time scanned count
    increment_scanned()

    username = message.from_user.username or message.from_user.first_name
    logger.info(f"Received message from @{username}: {text[:80]}")

    # --- Step 0: Check if the bot is mentioned or greeted ---
    bot_username = context.bot.username or ""
    text_lower = text.lower().strip()
    
    # It counts as a "mention" if:
    # 1. The bot's username is in the text
    # 2. The user is replying directly to one of the bot's messages
    # 3. The message is just a simple greeting like "hi", "hello", "yoo"
    is_mentioned = False
    if bot_username and f"@{bot_username}".lower() in text_lower:
        is_mentioned = True
    elif message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
        is_mentioned = True
    elif text_lower in ["hi", "hello", "yoo", "hey", "សួស្តី", "សួរស្ដី"]:
        is_mentioned = True

    if is_mentioned:
        logger.info(f"Bot mentioned/greeted by {username}, replying.")
        await _reply_mention(message)
        return

    # --- Step 1: Keyword pre-check against built-in + custom admin list ---
    pre_result = pre_check(text)

    if pre_result:
        match_type, custom_reason = pre_result if isinstance(pre_result, tuple) else (pre_result, None)
        logger.info(f"Keyword matched: {match_type} — deleting message")
        
        # Categorize based on the result from pre_check
        if match_type == "Toxic":
            category = "toxic"
            display_reason = "Toxic Content"
        elif match_type == "Pattern":
            category = "spam"
            display_reason = custom_reason or "Sensitive pattern or restricted content detected"
        else:
            # Both "Spam" and "Pattern" map to the "spam" category for strike tracking
            category = "spam"
            display_reason = "Spam Content"
        
        await _delete_and_notify(message, display_reason, source="keyword filter", category=category)
        return

    # Non-matching messages are silently ignored


# Keep handle_mention as a stub for backward compatibility (no longer used as a separate handler)
async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def _reply_mention(message):
    """Reply to the user who mentioned the bot — same message as /start."""
    user = message.from_user
    try:
        await message.reply_html(_bot_intro_html(user.mention_html()))
        logger.info(f"Mention reply sent to {user.first_name}.")
    except Exception as e:
        logger.error(f"Failed to send mention reply to {user.first_name}: {e}")


async def _delete_and_notify(message, reason: str, source: str, category: str = "spam"):
    """Delete the message and notify the group with a warning."""
    user = message.from_user
    user_id = user.id
    
    # Log to real-time dashboard (this also increments the strikes in JSON)
    log_violation(user_id, user.username or user.first_name, reason, category, message.text or "Sticker/Media")
    
    current_strikes = get_user_strikes(user_id)
    
    await message.chat.send_action(action="typing")

    # Try to delete the offending message
    try:
        await message.delete()
        logger.info(f"Deleted harmful message (source: {source})")
    except (BadRequest, Forbidden) as e:
        logger.warning(f"Could not delete message: {e}")

    # Notify the chat
    user_mention = user.mention_html()
    
    if current_strikes >= 4:
        text = (
            f"🚨 {user_mention} <b>ជោរម្លេះ?</b>\n\n"
            f"A message was <b>automatically removed</b> (Warning #{current_strikes}).\n\n"
            f"📋 <b>Reason:</b> {reason}"
        )
    else:
        text = (
            f"🚨 A message from {user_mention} was <b>automatically removed</b>.\n\n"
            f"📋 <b>Reason:</b> {reason}"
        )

    await message.chat.send_message(
        text=text,
        parse_mode="HTML"
    )
