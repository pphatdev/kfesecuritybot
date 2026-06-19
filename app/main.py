import os
import certifi
import httpx

# Dirty hack to disable SSL verification globally for httpx
_orig_httpx_init = httpx.AsyncClient.__init__
def _patched_httpx_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _orig_httpx_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = _patched_httpx_init

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.config import config
from app.handlers.commands import start_command, help_command
from app.handlers.messages import handle_message
from app.handlers.admin import addword_command, removeword_command, listkeywords_command

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    token = config.TELEGRAM_BOT_TOKEN
    
    if not token or token == "your_telegram_bot_token_here":
        logger.error("Please set your TELEGRAM_BOT_TOKEN in the .env file.")
        return

    application = Application.builder().token(token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # Admin-only keyword management commands
    application.add_handler(CommandHandler("addword", addword_command))
    application.add_handler(CommandHandler("removeword", removeword_command))
    application.add_handler(CommandHandler("keywords", listkeywords_command))

    # Message handlers — handle_message also handles mention replies internally
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting. Press Ctrl+C to stop.")
    
    # Fix for Python 3.11+ asyncio get_event_loop() RuntimeError
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    application.run_polling()

if __name__ == "__main__":
    main()
