import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from app.services.keywords import add_keyword, remove_keyword, get_custom_keywords

logger = logging.getLogger(__name__)


async def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the user who sent the command is a group admin or owner."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)


async def addword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /addword <toxic|spam> <keyword>
    Example: /addword toxic scammer
    """
    if not await _is_admin(update, context):
        await update.message.reply_text("⛔ Only group admins can use this command.")
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /addword <toxic|spam> <keyword>\n"
            "Example: /addword toxic scammer"
        )
        return

    category = args[0].lower()
    if category not in ("spam", "toxic"):
        await update.message.reply_text("❌ Category must be either `toxic` or `spam`.", parse_mode="Markdown")
        return

    keyword = " ".join(args[1:]).lower()
    added = add_keyword(keyword, category)

    if added:
        await update.message.reply_text(
            f"✅ Keyword `{keyword}` added to *{category}* list.", parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"⚠️ Keyword `{keyword}` already exists in the *{category}* list.", parse_mode="Markdown"
        )


async def removeword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /removeword <keyword>
    Example: /removeword scammer
    """
    if not await _is_admin(update, context):
        await update.message.reply_text("⛔ Only group admins can use this command.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /removeword <keyword>")
        return

    keyword = " ".join(args).lower()
    removed = remove_keyword(keyword)

    if removed:
        await update.message.reply_text(f"🗑️ Keyword `{keyword}` has been removed.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Keyword `{keyword}` was not found in the custom list.", parse_mode="Markdown")


async def listkeywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /keywords — List all admin-added custom keywords.
    """
    if not await _is_admin(update, context):
        await update.message.reply_text("⛔ Only group admins can use this command.")
        return

    custom = get_custom_keywords()
    spam_list = custom.get("spam", [])
    toxic_list = custom.get("toxic", [])

    spam_text = "\n".join(f"  • `{k}`" for k in spam_list) if spam_list else "  _(none)_"
    toxic_text = "\n".join(f"  • `{k}`" for k in toxic_list) if toxic_list else "  _(none)_"

    message = (
        "📋 *Custom Keyword List*\n\n"
        f"🚫 *Spam:*\n{spam_text}\n\n"
        f"☠️ *Toxic:*\n{toxic_text}"
    )
    await update.message.reply_text(message, parse_mode="Markdown")
