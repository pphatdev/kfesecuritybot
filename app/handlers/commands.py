import logging

from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from app.services.users_db import track_user

logger = logging.getLogger(__name__)

ASK_QUESTION_CALLBACK = "ask_question"
# Older messages emitted a button with this callback_data. Keep matching it so
# users tapping pre-rename buttons still get a response.
LEGACY_WHAT_I_CAN_DO_CALLBACK = "what_i_can_do"

# Sent verbatim to the user after they tap "Ask Question". `handle_message`
# looks for this exact text in `reply_to_message.text` to route the follow-up
# reply through Gemini instead of the mention responder.
ASK_QUESTION_PROMPT = (
    "❓ Reply to this message with your question, and I'll ask Google for the answer."
)


def _intro_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard shown alongside the intro message."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="❓ Ask Question", callback_data=ASK_QUESTION_CALLBACK)]]
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


async def ask_question_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the 'Ask Question' inline button press.

    Two-step feedback so the user always sees *something*:
      1) Modal popup via `query.answer(show_alert=True)` — instant, works even
         if the bot has restricted send rights in the chat.
      2) A regular chat message with `ForceReply` so the user can type their
         question and `handle_message` routes it to Gemini.
    """
    query = update.callback_query
    if not query:
        logger.warning("ask_question_callback: update has no callback_query")
        return

    logger.info(
        f"ask_question_callback fired: data={query.data!r}, "
        f"from_user={query.from_user.id if query.from_user else None}, "
        f"chat_id={query.message.chat.id if query.message and query.message.chat else None}"
    )

    # Step 1: modal popup — guaranteed visible even in restricted groups.
    try:
        await query.answer(
            text="Reply to my next message with your question — I'll ask Google for you.",
            show_alert=True,
        )
    except Exception as e:
        logger.warning(f"ask_question_callback: query.answer() failed: {e}")

    # Step 2: send the follow-up message with ForceReply so the user's next
    # message becomes a reply we can identify in handle_message.
    chat_id = None
    if query.message and query.message.chat:
        chat_id = query.message.chat.id
    elif query.from_user:
        chat_id = query.from_user.id

    if chat_id is None:
        logger.error("ask_question_callback: no chat_id available, cannot send prompt")
        return

    # Flag this user so their next message in this chat is treated as their
    # question, even if they don't tap the reply UI.
    if query.from_user:
        try:
            from app.handlers.messages import mark_pending_question
            mark_pending_question(chat_id, query.from_user.id)
            logger.info(
                f"ask_question_callback: pending-question slot marked for "
                f"user={query.from_user.id} in chat={chat_id}"
            )
        except Exception as e:
            logger.warning(f"ask_question_callback: could not mark pending question: {e}")

    force_reply = ForceReply(selective=True, input_field_placeholder="Type your question…")

    try:
        sent = await context.bot.send_message(
            chat_id=chat_id,
            text=ASK_QUESTION_PROMPT,
            reply_markup=force_reply,
        )
        logger.info(
            f"ask_question_callback: prompt sent — chat_id={chat_id}, message_id={sent.message_id}"
        )
    except Exception as e:
        logger.error(f"ask_question_callback: send_message to {chat_id} failed: {e}")
