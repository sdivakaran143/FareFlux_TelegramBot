import os

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

from handlers.conversation import (
    start,
    source,
    destination,
    source_selected,
    destination_selected,
    date_selected,
    bus_selected,
    SOURCE,
    DESTINATION,
    DATE
)

from scheduler import start_scheduler

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(BOT_TOKEN).build()

conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", start)
    ],
    states={

        SOURCE: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                source
            ),

            CallbackQueryHandler(
                source_selected,
                pattern=r"^source\|"
            )
        ],

        DESTINATION: [

            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                destination
            ),

            CallbackQueryHandler(
                destination_selected,
                pattern=r"^destination\|"
            )
        ],

        DATE: [

            CallbackQueryHandler(
                date_selected,
                pattern=r"^(today|tomorrow)$"
            ),

            CallbackQueryHandler(
                bus_selected,
                pattern=r"^bus\|"
            )
        ]
    },
    fallbacks=[]
)

app.add_handler(conversation_handler)

start_scheduler(app.bot)

print("Bot started...")

app.run_polling(
    drop_pending_updates=True,
    close_loop=False
)
