import os
import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from app.services.allowed_users import add_allowed_user, remove_allowed_user, is_user_allowed

logger = logging.getLogger(__name__)


async def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the user who sent the command is a group admin or owner."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)







async def _is_caller_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the caller is an env-configured admin or a group admin."""
    user = update.effective_user
    chat = update.effective_chat
    
    admin_usernames = [u.strip().lower() for u in (os.getenv("DASHBOARD_ADMINS") or "").split(",") if u.strip()]
    admin_ids = [i.strip() for i in (os.getenv("DASHBOARD_ADMIN_IDS") or "").split(",") if i.strip()]
    
    if str(user.id) in admin_ids or (user.username and user.username.lower() in admin_usernames):
        return True
        
    if chat.type != "private":
        if await _is_admin(update, context):
            return True
            
    return False


async def adduser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /adduser <username|user_id>
    Example: /adduser @another_admin
    """
    if not await _is_caller_admin(update, context):
        await update.message.reply_text("⛔ Only bot creators or group admins can add dashboard users.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /adduser <username|user_id>\nExample: /adduser @another_admin")
        return
        
    target = args[0]
    added = add_allowed_user(target)
    if added:
        await update.message.reply_text(f"✅ User `{target}` is now authorized to access the dashboard.")
    else:
        await update.message.reply_text(f"⚠️ User `{target}` is already authorized or invalid.")


async def removeuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /removeuser <username|user_id>
    Example: /removeuser @another_admin
    """
    if not await _is_caller_admin(update, context):
        await update.message.reply_text("⛔ Only bot creators or group admins can remove dashboard users.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /removeuser <username|user_id>\nExample: /removeuser @another_admin")
        return
        
    target = args[0]
    removed = remove_allowed_user(target)
    if removed:
        await update.message.reply_text(f"🗑️ User `{target}` has been removed from authorized dashboard users.")
    else:
        await update.message.reply_text(f"❌ User `{target}` was not found in the custom allowed list.")
