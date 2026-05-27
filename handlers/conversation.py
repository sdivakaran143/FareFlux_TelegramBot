from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes

from services.location_service import search_place
from services.scraper import scrape_prices
from database import add_monitor

USER_STATE = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    USER_STATE[chat_id] = {
        "step": "source"
    }

    print("START:", USER_STATE)

    await update.message.reply_text(
        "🚌 Enter Source Location"
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    text = update.message.text

    print("MESSAGE:", text)

    if chat_id not in USER_STATE:

        USER_STATE[chat_id] = {
            "step": "source"
        }

    step = USER_STATE[chat_id]["step"]

    print("STEP:", step)

    if step == "source":

        results = search_place(text)

        print("SOURCE RESULTS:", results)

        if not results:

            await update.message.reply_text(
                "❌ No locations found"
            )

            return

        keyboard = []

        for item in results:

            keyboard.append([
                InlineKeyboardButton(
                    item["display_name"][:50],
                    callback_data=f"source|{item['display_name']}"
                )
            ])

        await update.message.reply_text(
            "📍 Select Source",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif step == "destination":

        results = search_place(text)

        print("DEST RESULTS:", results)

        if not results:

            await update.message.reply_text(
                "❌ No destinations found"
            )

            return

        keyboard = []

        for item in results:

            keyboard.append([
                InlineKeyboardButton(
                    item["display_name"][:50],
                    callback_data=f"destination|{item['display_name']}"
                )
            ])

        await update.message.reply_text(
            "📍 Select Destination",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    chat_id = query.message.chat_id

    data = query.data

    print("CALLBACK:", data)

    if data.startswith("source|"):

        source = data.split("|", 1)[1]

        USER_STATE[chat_id]["source"] = source
        USER_STATE[chat_id]["step"] = "destination"

        await query.message.reply_text(
            "📍 Enter Destination"
        )

    elif data.startswith("destination|"):

        destination = data.split("|", 1)[1]

        USER_STATE[chat_id]["destination"] = destination
        USER_STATE[chat_id]["step"] = "date"

        keyboard = [
            [
                InlineKeyboardButton(
                    "Today",
                    callback_data="today"
                )
            ],
            [
                InlineKeyboardButton(
                    "Tomorrow",
                    callback_data="tomorrow"
                )
            ]
        ]

        await query.message.reply_text(
            "📅 Select Travel Date",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data in ["today", "tomorrow"]:

        USER_STATE[chat_id]["date"] = data

        buses = scrape_prices(
            USER_STATE[chat_id]["source"],
            USER_STATE[chat_id]["destination"],
            data
        )

        keyboard = []

        for bus in buses:

            keyboard.append([
                InlineKeyboardButton(
                    f"{bus['operator']} • ₹{bus['price']}",
                    callback_data=f"bus|{bus['operator']}|{bus['price']}"
                )
            ])

        await query.message.reply_text(
            "🚌 Select Bus",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("bus|"):

        _, operator, price = data.split("|")

        add_monitor(
            chat_id=chat_id,
            operator=operator,
            source=USER_STATE[chat_id]["source"],
            destination=USER_STATE[chat_id]["destination"],
            travel_date=USER_STATE[chat_id]["date"],
            current_price=int(price)
        )

        await query.message.reply_text(
            f"""
✅ Monitor Created

🚌 {operator}

💰 Fare:
₹{price}

🔔 Monitoring started
"""
        )
