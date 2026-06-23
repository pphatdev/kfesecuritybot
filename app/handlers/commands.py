from telegram import Update
from telegram.ext import ContextTypes
from app.services.users_db import track_user


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
    await update.message.reply_html(_bot_intro_html(user.mention_html()))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    user = update.effective_user
    track_user(user.id, user.username)
    await update.message.reply_html(
        "ℹ️ <b>Help</b>\n\n"
        "I monitor group messages and remove harmful content automatically based on patterns configured in the web dashboard.\n\n"
        "For more details, type /start."
    )
