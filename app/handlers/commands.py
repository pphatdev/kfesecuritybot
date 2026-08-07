import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.users_db import track_user

logger = logging.getLogger(__name__)

WHAT_I_CAN_DO_CALLBACK = "what_i_can_do"


def _intro_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard shown alongside the intro message."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="ℹ️ What I can do", callback_data=WHAT_I_CAN_DO_CALLBACK)]]
    )


def _requires_mention_in_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """In groups, only reply if the bot was explicitly mentioned.

    Why: avoid noisy responses when other bots or users type generic
    commands like `/hi` or `/hello` in a shared chat.
    """
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat or chat.type == "private":
        return True
    bot_username = (context.bot.username or "").lower()
    if not bot_username:
        return False
    text = (message.text or message.caption or "").lower()
    return f"@{bot_username}" in text


def _bot_intro_html(user_mention: str) -> str:
    """Shared intro message used by /start and @mention replies."""
    return (
        f"👋 Hi {user_mention}! I am a message moderation bot.\n\n"
        "🤖 <b>What I do:</b>\n"
        "I silently monitor messages and automatically <b>delete</b> Spam or Toxic content.\n\n"
        "💡 <b>How it works:</b>\n"
        "Messages are instantly checked against a custom keyword list managed via the web dashboard."
    )


def _what_i_can_do_html() -> str:
    """Detailed capability list shown when the 'What I can do' button is pressed."""
    return (
        "🤖 <b>What I can do</b>\n\n"
        "• 🛡️ Auto-delete <b>spam</b>, <b>toxic</b>, and pattern-matched messages\n"
        "• 🚫 Block banned <b>stickers</b> and sticker packs\n"
        "• ⏱️ Enforce per-group <b>slow mode</b>\n"
        "• 📊 Track violations and user <b>strikes</b>\n"
        "• 📣 Deliver scheduled <b>broadcasts</b> from the dashboard\n\n"
        "Type /help for a shorter summary or /start to see the intro again."
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    track_user(user.id, user.username)
    await update.message.reply_html(
        _bot_intro_html(user.mention_html()),
        reply_markup=_intro_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    if not _requires_mention_in_group(update, context):
        return
    user = update.effective_user
    track_user(user.id, user.username)
    await update.message.reply_html(
        "ℹ️ <b>Help</b>\n\n"
        "I monitor group messages and remove harmful content automatically based on patterns configured in the web dashboard.\n\n"
        "For more details, type /start.",
        reply_markup=_intro_keyboard(),
    )


async def hi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hi and /hello — same reply as /start."""
    chat = update.effective_chat
    chat_type = chat.type if chat else "unknown"
    logger.info(f"hi_command fired: chat_type={chat_type}, text={(update.message.text or '')!r}")
    if not _requires_mention_in_group(update, context):
        logger.info("hi_command: skipped — bot not mentioned in group")
        return
    user = update.effective_user
    track_user(user.id, user.username)
    await update.message.reply_html(
        _bot_intro_html(user.mention_html()),
        reply_markup=_intro_keyboard(),
    )


async def what_i_can_do_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the 'What I can do' inline button press."""
    query = update.callback_query
    logger.info(f"what_i_can_do_callback fired: data={query.data if query else None!r}")
    if not query:
        return
    await query.answer()
    try:
        await query.message.reply_html(_what_i_can_do_html())
    except Exception as e:
        logger.warning(f"what_i_can_do_callback: reply_html failed ({e}), falling back to edit")
        try:
            await query.edit_message_text(
                text=_what_i_can_do_html(),
                parse_mode="HTML",
            )
        except Exception as e2:
            logger.error(f"what_i_can_do_callback: edit fallback also failed: {e2}")
