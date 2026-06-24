import logging
import time
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden
from app.services.keywords import pre_check
from app.handlers.commands import _bot_intro_html
from app.services.stats import increment_scanned, log_violation, get_user_strikes
from app.services.users_db import track_user
from app.services.groups_db import track_group
from app.services.settings_db import get_setting, get_group_delay

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
            await track_group(chat.id, chat.title)
        elif status in ['left', 'kicked']:
            logger.info(f"Bot removed from group: {chat.title} ({chat.id})")
            # Optionally, you could untrack the group, but keeping it is fine.

# In-memory dictionary to track user's last message time per chat
# Format: {(chat_id, user_id): timestamp_in_seconds}
user_last_message = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process incoming messages. Handles mentions, keyword filter, and AI detection."""
    message = update.message or update.channel_post
    
    if not message:
        return
        
    # --- 1. Extract Text First ---
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

    bot_username = context.bot.username or ""
    text_lower = text.lower().strip()
    normalized_text = " ".join(text_lower.split())

    # --- 2. Check Admin Commands (Bypasses slow mode) ---
    if message.reply_to_message and bot_username and (
        normalized_text == f"@{bot_username.lower()} delete this" or 
        normalized_text == f"@{bot_username.lower()} remove this"
    ):
        from app.handlers.admin import _is_caller_admin
        if await _is_caller_admin(update, context):
            try:
                await message.reply_to_message.delete()
                await message.delete()
                logger.info("Message deleted by admin command")
            except Exception as e:
                logger.warning(f"Failed to delete message via command: {e}")
        else:
            await message.reply_text("⛔ You are not authorized to use this command.")
        return

    # --- 3. Track User & Group ---
    if message.from_user:
        await track_user(message.from_user.id, message.from_user.username)

    if message.chat and message.chat.type == "private":
        from app.services.private_chats_db import log_private_chat
        await log_private_chat(
            user_id=message.from_user.id if message.from_user else message.chat.id,
            username=message.from_user.username or message.from_user.first_name if message.from_user else "Unknown",
            message=text
        )
        
    if message.chat and message.chat.type != "private":
        await track_group(message.chat.id, message.chat.title)
        
        # --- 4. Enforce Slow Mode ---
        if message.from_user:
            delay = await get_group_delay(message.chat.id)
            if delay > 0:
                chat_id = message.chat.id
                user_id = message.from_user.id
                now = time.time()
                last_time = user_last_message.get((chat_id, user_id), 0)
                
                if now - last_time < delay:
                    try:
                        await message.delete()
                        logger.info(f"Deleted fast message from {user_id} in {chat_id} (enforcing {delay}s delay)")
                    except Exception as e:
                        logger.warning(f"Could not delete fast message: {e}")
                    return
                
                # Record the valid message time
                user_last_message[(chat_id, user_id)] = now

    # --- 5. Increment Stats & Log ---
    await increment_scanned()

    if message.from_user:
        username = message.from_user.username or message.from_user.first_name
    elif message.sender_chat:
        username = message.sender_chat.title
    else:
        username = "Unknown"
        
    logger.info(f"Received message from @{username}: {text[:80]}")

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
    pre_result = await pre_check(text, sticker=message.sticker)

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
    await log_violation(user_id, user_name, reason, category, message.text or "Sticker/Media")
    
    current_strikes = await get_user_strikes(user_id)
    
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
