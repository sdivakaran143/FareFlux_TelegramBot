import os

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

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

print("TOKEN LOADED:", BOT_TOKEN[:10])

app = Application.builder().token(BOT_TOKEN).build()


async def ping(update, context):

    await update.message.reply_text(
        "pong"
    )


app.add_handler(
    CommandHandler(
        "ping",
        ping
    )
)

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
    drop_pending_updates=True,
    allowed_updates=[
        "message",
        "callback_query"
    ],
    poll_interval=2
)
