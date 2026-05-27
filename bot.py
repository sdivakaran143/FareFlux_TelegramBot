
import os

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from handlers.conversation import (
    start,
    source,
    destination,
    date,
    threshold,
    frequency,
    SOURCE,
    DESTINATION,
    DATE,
    THRESHOLD
)

from scheduler import start_scheduler

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SOURCE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                source
            )
        ],
        DESTINATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                destination
            )
        ],
        DATE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                date
            )
        ],
        THRESHOLD: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                threshold
            )
        ]
    },
    fallbacks=[]
)

app.add_handler(conv_handler)

app.add_handler(
    CallbackQueryHandler(frequency)
)

start_scheduler(app.bot)

print("Bot started...")

app.run_polling()
