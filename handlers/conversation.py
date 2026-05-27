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


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id

    USER_STATE[chat_id] = {
        "step": "source"
    }

    await update.message.reply_text(
        "🚌 Enter Source Location"
    )


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id

    text = update.message.text

    if chat_id not in USER_STATE:

        USER_STATE[chat_id] = {
            "step": "source"
        }

    step = USER_STATE[chat_id]["step"]

    # SOURCE FLOW

    if step == "source":

        results = search_place(text)

        if not results:

            await update.message.reply_text(
                "❌ No locations found"
            )

            return

        USER_STATE[chat_id]["source_results"] = results

        keyboard = []

        for index, item in enumerate(results):

            keyboard.append([
                InlineKeyboardButton(
                    item["display_name"][:50],
                    callback_data=f"source|{index}"
                )
            ])

        await update.message.reply_text(
            "📍 Select Source",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # DESTINATION FLOW

    elif step == "destination":

        results = search_place(text)

        if not results:

            await update.message.reply_text(
                "❌ No destinations found"
            )

            return

        USER_STATE[chat_id]["destination_results"] = results

        keyboard = []

        for index, item in enumerate(results):

            keyboard.append([
                InlineKeyboardButton(
                    item["display_name"][:50],
                    callback_data=f"destination|{index}"
                )
            ])

        await update.message.reply_text(
            "📍 Select Destination",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    chat_id = query.message.chat_id

    data = query.data

    # SOURCE SELECTED

    if data.startswith("source|"):

        index = int(data.split("|")[1])

        source = USER_STATE[chat_id]["source_results"][index]["display_name"]

        USER_STATE[chat_id]["source"] = source

        USER_STATE[chat_id]["step"] = "destination"

        await query.message.reply_text(
            "📍 Enter Destination"
        )

    # DESTINATION SELECTED

    elif data.startswith("destination|"):

        index = int(data.split("|")[1])

        destination = USER_STATE[chat_id]["destination_results"][index]["display_name"]

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

    # DATE SELECTED

    elif data in ["today", "tomorrow"]:

        USER_STATE[chat_id]["date"] = data

        buses = scrape_prices(
            USER_STATE[chat_id]["source"],
            USER_STATE[chat_id]["destination"],
            data
        )

        keyboard = []

        for index, bus in enumerate(buses):

            USER_STATE[chat_id][f"bus_{index}"] = bus

            keyboard.append([
                InlineKeyboardButton(
                    f"{bus['operator']} • ₹{bus['price']}",
                    callback_data=f"bus|{index}"
                )
            ])

        await query.message.reply_text(
            "🚌 Select Bus",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # BUS SELECTED

    elif data.startswith("bus|"):

        index = int(data.split("|")[1])

        bus = USER_STATE[chat_id][f"bus_{index}"]

        add_monitor(
            chat_id=chat_id,
            operator=bus["operator"],
            source=USER_STATE[chat_id]["source"],
            destination=USER_STATE[chat_id]["destination"],
            travel_date=USER_STATE[chat_id]["date"],
            current_price=int(bus["price"])
        )

        await query.message.reply_text(
            f"""
✅ Monitor Created

🚌 Operator:
{bus["operator"]}

💰 Current Fare:
₹{bus["price"]}

🔔 Monitoring started

⏱ Checking every minute
"""
        )
