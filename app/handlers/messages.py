import logging
import time
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest, Forbidden
from app.services.keywords import pre_check
from app.handlers.commands import _bot_intro_html, _intro_keyboard, ASK_QUESTION_PROMPT
from app.services.qa_service import ask_gemini
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
            track_group(chat.id, chat.title)
        elif status in ['left', 'kicked']:
            logger.info(f"Bot removed from group: {chat.title} ({chat.id})")
            # Optionally, you could untrack the group, but keeping it is fine.

# In-memory dictionary to track user's last message time per chat
# Format: {(chat_id, user_id): timestamp_in_seconds}
user_last_message = {}

# Tracks users who tapped "Ask Question" — the next message from that user
# (in the same chat) within the TTL is treated as their question.
# Format: {(chat_id, user_id): expiry_timestamp}
pending_questions: dict[tuple[int, int], float] = {}
PENDING_QUESTION_TTL_SECONDS = 300  # 5 minutes


def mark_pending_question(chat_id: int, user_id: int) -> None:
    pending_questions[(chat_id, user_id)] = time.time() + PENDING_QUESTION_TTL_SECONDS


def _consume_pending_question(chat_id: int, user_id: int) -> bool:
    """Return True (and clear the flag) if this user has an active pending-question slot."""
    key = (chat_id, user_id)
    expiry = pending_questions.get(key)
    if not expiry:
        return False
    if expiry < time.time():
        pending_questions.pop(key, None)
        return False
    pending_questions.pop(key, None)
    return True

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

    # Log incoming message to chat history
    try:
        sender_id = message.from_user.id if message.from_user else None
        if message.from_user:
            sender = message.from_user.username or message.from_user.first_name
        elif message.sender_chat:
            sender = message.sender_chat.title
        else:
            sender = "System"
            
        sticker_id = message.sticker.file_id if message.sticker else None
        media_type = None
        media_name = None
        if message.photo:
            media_type = "photo"
            media_name = "Photo"
        elif message.video:
            media_type = "video"
            media_name = getattr(message.video, "file_name", "Video")
        elif message.document:
            media_type = "document"
            media_name = getattr(message.document, "file_name", "Document")
            
        from app.services.chat_history import log_message
        log_message(
            chat_id=message.chat.id,
            message_id=message.message_id,
            sender_id=sender_id,
            sender=sender,
            text=text or (f"[{media_name}]" if media_name else ""),
            is_bot=False,
            sticker_id=sticker_id,
            media_type=media_type,
            media_name=media_name
        )
    except Exception as e:
        logger.error(f"Error logging chat history: {e}")

    if not text and not media_name and not message.sticker:
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
        track_user(message.from_user.id, message.from_user.username)
        
    if message.chat and message.chat.type != "private":
        track_group(message.chat.id, message.chat.title)
        
        # --- 4. Enforce Slow Mode ---
        if message.from_user:
            delay = get_group_delay(message.chat.id)
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
    increment_scanned()

    if message.from_user:
        username = message.from_user.username or message.from_user.first_name
    elif message.sender_chat:
        username = message.sender_chat.title
    else:
        username = "Unknown"
        
    logger.info(f"Received message from @{username}: {text[:80]}")

    # --- 6a. Ask Question flow ---
    # Route to Gemini if either:
    #   (a) the user is explicitly replying to our "Ask Question" prompt, or
    #   (b) the user tapped "Ask Question" recently and this is their next
    #       message in the same chat (pending_questions bookkeeping).
    is_ask_reply = bool(
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == context.bot.id
        and (message.reply_to_message.text or "").strip() == ASK_QUESTION_PROMPT
    )
    has_pending = bool(
        message.from_user
        and message.chat
        and _consume_pending_question(message.chat.id, message.from_user.id)
    )
    if is_ask_reply or has_pending:
        question = text
        logger.info(
            f"Ask-Question from @{username} "
            f"(via {'reply' if is_ask_reply else 'pending-slot'}): {question[:120]}"
        )
        await message.chat.send_action(action="typing")
        answer = await ask_gemini(question)
        try:
            await message.reply_text(answer, disable_web_page_preview=True)
        except Exception as e:
            logger.error(f"Failed to send Q&A answer: {e}")
        return

    # It counts as a "mention" if:
    # 1. The bot's username is in the text
    # 2. The user is replying directly to one of the bot's messages
    # 3. The message is a bare greeting AND we're in a private chat
    #    (bare greetings in groups/channels are ignored to avoid noise)
    is_private_chat = bool(message.chat and message.chat.type == "private")
    is_mentioned = False
    if bot_username and f"@{bot_username}".lower() in text_lower:
        is_mentioned = True
    elif message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == context.bot.id:
        is_mentioned = True
    elif is_private_chat and text_lower in ["hi", "hello", "yoo", "hey", "សួស្តី", "សួរស្ដី"]:
        is_mentioned = True

    if is_mentioned:
        logger.info(f"Bot mentioned/greeted by {username}, replying.")
        # Log the mention or reply to appropriate DB
        if message.chat and message.chat.type != "private":
            from app.services.groups_db import record_group_mention_or_reply
            record_group_mention_or_reply(message.chat.id, message.chat.title)
        elif message.from_user:
            from app.services.users_db import record_user_mention_or_reply
            record_user_mention_or_reply(message.from_user.id, message.from_user.username)
            
        await _reply_mention(message)
        return

    # --- Step 1: Keyword pre-check against built-in + custom admin list ---
    pre_result = await pre_check(text, sticker=message.sticker, bot=context.bot, document_name=media_name)

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
        elif match_type == "FileExt":
            category = "spam"
            display_reason = custom_reason or "Banned File Extension"
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
        reply_html_content = _bot_intro_html(user.mention_html())
        sent_message = await message.reply_html(
            reply_html_content,
            reply_markup=_intro_keyboard(),
        )
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
        try:
            from app.services.chat_history import mark_message_deleted
            mark_message_deleted(message.chat.id, message.message_id, reason)
        except Exception as he:
            logger.error(f"Error marking message as deleted in history: {he}")
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

    sent_warning = await message.chat.send_message(
        text=text,
        parse_mode="HTML"
    )
