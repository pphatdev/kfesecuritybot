import os
import certifi
import httpx

# Built-in global SSL verification bypass to run flawlessly behind strict corporate firewalls
_orig_httpx_init = httpx.AsyncClient.__init__
def _patched_httpx_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _orig_httpx_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = _patched_httpx_init

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ChatMemberHandler, filters
from app.config import config
from app.handlers.commands import start_command, help_command
from app.handlers.messages import handle_message, handle_my_chat_member
from app.handlers.admin import adduser_command, removeuser_command
from app.services.schedule_service import run_scheduler
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def post_init(application: Application) -> None:
    """Run background scheduler task once the bot is initialized."""
    asyncio.create_task(run_scheduler(application))

def main() -> None:
    """Start the bot."""
    token = config.TELEGRAM_BOT_TOKEN
    
    if not token or token == "your_telegram_bot_token_here":
        logger.error("Please set your TELEGRAM_BOT_TOKEN in the .env file.")
        return

    # Ensure an event loop exists and is set for the current thread (Python 3.12+ / 3.14 compatibility)
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    application = Application.builder().token(token).post_init(post_init).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Admin commands (dashboard access management)
    application.add_handler(CommandHandler("adduser", adduser_command))
    application.add_handler(CommandHandler("removeuser", removeuser_command))

    # Message handlers — handle_message also handles mention replies internally
    application.add_handler(MessageHandler((filters.ALL | filters.UpdateType.CHANNEL_POST) & ~filters.COMMAND, handle_message))
    application.add_handler(ChatMemberHandler(handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    logger.info("Bot is starting. Press Ctrl+C to stop.")

    application.run_polling()

if __name__ == "__main__":
    main()
