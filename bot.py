import os
import logging

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from handlers.conversation import (
    start_command,
    message_handler,
    callback_handler
)

logging.basicConfig(level=logging.INFO)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(
    CommandHandler(
        "start",
        start_command
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler
    )
)

app.add_handler(
    CallbackQueryHandler(
        callback_handler
    )
)

print("Bot started...")

app.run_polling(
    drop_pending_updates=True
)
