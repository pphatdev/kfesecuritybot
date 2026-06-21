import os
import logging
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from app.services.otp import generate_otp
from app.services.allowed_users import add_allowed_user, remove_allowed_user, is_user_allowed

logger = logging.getLogger(__name__)


async def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if the user who sent the command is a group admin or owner."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)





async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /login — Generate an OTP for dashboard login.
    """
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user is in authorized admins lists
    allowed = False
    
    if is_user_allowed(user.id, user.username):
        allowed = True
    elif chat.type != "private":
        # Fallback to group admin check if no lists are specified in .env and allowed_users.json
        from app.services.allowed_users import load_allowed_users
        allowed_data = load_allowed_users()
        admin_usernames = [u.strip().lower() for u in (os.getenv("DASHBOARD_ADMINS") or "").split(",") if u.strip()]
        admin_ids = [i.strip() for i in (os.getenv("DASHBOARD_ADMIN_IDS") or "").split(",") if i.strip()]
        has_any_explicit_admins = bool(admin_usernames or admin_ids or allowed_data.get("usernames") or allowed_data.get("user_ids"))
        
        if not has_any_explicit_admins:
            if await _is_admin(update, context):
                allowed = True
                
    if not allowed:
        from app.services.allowed_users import load_allowed_users
        allowed_data = load_allowed_users()
        admin_usernames = [u.strip().lower() for u in (os.getenv("DASHBOARD_ADMINS") or "").split(",") if u.strip()]
        admin_ids = [i.strip() for i in (os.getenv("DASHBOARD_ADMIN_IDS") or "").split(",") if i.strip()]
        has_any_explicit_admins = bool(admin_usernames or admin_ids or allowed_data.get("usernames") or allowed_data.get("user_ids"))
        
        if chat.type == "private" and not has_any_explicit_admins:
            await update.message.reply_text(
                "⛔ *Dashboard access is restricted.*\n\n"
                "No dashboard administrators are configured in the bot's `.env` file or allowed list.\n\n"
                "To authorize yourself, either:\n"
                "1. Run `/login` inside a Telegram group chat where you are an administrator.\n"
                "2. Add your Telegram username to `DASHBOARD_ADMINS` in the `.env` file (e.g., `DASHBOARD_ADMINS=your_username`) and restart the bot.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("⛔ You are not authorized to generate a login OTP.")
        return

    # Generate OTP
    otp = generate_otp(user.id, user.username)
    
    # Try sending via DM
    try:
        await context.bot.send_message(
            chat_id=user.id,
            text=(
                f"🔐 *BotControl Dashboard Login*\n\n"
                f"Your One-Time Password (OTP) is: `{otp}`\n"
                f"It is valid for 5 minutes.\n\n"
                f"Enter your Telegram Username (`{user.username or user.id}`) and this OTP on the dashboard login page."
            ),
            parse_mode="Markdown"
        )
        if chat.type != "private":
            await update.message.reply_text("🔐 I've sent your login OTP via private message.")
    except Exception as e:
        logger.warning(f"Failed to send DM to user {user.id}: {e}")
        if chat.type != "private":
            await update.message.reply_text(
                f"⛔ I couldn't send you the OTP via private message. "
                f"Please start a private chat with me first (click @{(await context.bot.get_me()).username}), then run `/login` again."
            )
        else:
            await update.message.reply_text("❌ Something went wrong while generating/sending the OTP. Please try again.")


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
