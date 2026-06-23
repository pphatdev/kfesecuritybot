import logging
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden
from app.services.keywords import pre_check
from app.handlers.commands import _bot_intro_html
from app.services.stats import increment_scanned, log_violation, get_user_strikes
from app.services.users_db import track_user
from app.services.groups_db import track_group

logger = logging.getLogger(__name__)

async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the bot being added or removed from a group."""
    result = update.my_chat_member
    if not result:
        return
        
    chat = result.chat
    if chat.type != "private":
        status = result.new_chat_member.status
        if status in ['member', 'administrator']:
            logger.info(f"Bot added to group: {chat.title} ({chat.id})")
            track_group(chat.id, chat.title)
        elif status in ['left', 'kicked']:
            logger.info(f"Bot removed from group: {chat.title} ({chat.id})")
            # Optionally, you could untrack the group, but keeping it is fine.

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages. Handles mentions, keyword filter, and AI detection."""
    message = update.message or update.channel_post
    
    if not message:
        return
        
    # Track the user who sent the message
    if message.from_user:
        track_user(message.from_user.id, message.from_user.username)
    # Track the group if it's not a private chat
    if message.chat and message.chat.type != "private":
        track_group(message.chat.id, message.chat.title)
        
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

    if message.from_user:
        username = message.from_user.username or message.from_user.first_name
    elif message.sender_chat:
        username = message.sender_chat.title
    else:
        username = "Unknown"
        
    logger.info(f"Received message from @{username}: {text[:80]}")

    # --- Step 0: Check if the bot is mentioned or greeted ---
    bot_username = context.bot.username or ""
    text_lower = text.lower().strip()
    
    # Check for "delete this" command
    if message.reply_to_message and bot_username and text_lower == f"@{bot_username.lower()} delete this":
        from app.handlers.admin import _is_caller_admin
        if await _is_caller_admin(update, context):
            try:
                await message.reply_to_message.delete()
                await message.delete()
                logger.info(f"Message deleted by admin command: {username}")
            except Exception as e:
                logger.warning(f"Failed to delete message via command: {e}")
        else:
            await message.reply_text("⛔ You are not authorized to use this command.")
        return

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
    pre_result = pre_check(text, sticker=message.sticker)

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
        elif match_type == "Sticker":
            category = "spam"
            display_reason = custom_reason or "Banned Sticker Pack"
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
    if not message.from_user:
        return
    user = message.from_user
    try:
        await message.reply_html(_bot_intro_html(user.mention_html()))
        logger.info(f"Mention reply sent to {user.first_name}.")
    except Exception as e:
        logger.error(f"Failed to send mention reply to {user.first_name}: {e}")


async def _delete_and_notify(message, reason: str, source: str, category: str = "spam"):
    """Delete the message and notify the group with a warning."""
    if message.from_user:
        user = message.from_user
        user_id = user.id
        user_name = user.username or user.first_name
        user_mention = user.mention_html()
    elif message.sender_chat:
        user_id = message.sender_chat.id
        user_name = message.sender_chat.title
        user_mention = f"<b>{user_name}</b>"
    else:
        user_id = 0
        user_name = "Unknown"
        user_mention = "<b>Unknown</b>"
    
    # Log to real-time dashboard (this also increments the strikes in JSON)
    log_violation(user_id, user_name, reason, category, message.text or "Sticker/Media")
    
    current_strikes = get_user_strikes(user_id)
    
    await message.chat.send_action(action="typing")

    # Try to delete the offending message
    try:
        await message.delete()
        logger.info(f"Deleted harmful message (source: {source})")
    except (BadRequest, Forbidden) as e:
        logger.warning(f"Could not delete message: {e}")

    # Notify the chat
    
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
