from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    ContextTypes,
    ConversationHandler
)

from services.location_service import search_place
from services.scraper import scrape_prices

from database import add_monitor

SOURCE = 1
DESTINATION = 2
DATE = 3

async def start(update: Update, context):

    await update.message.reply_text(
        "Type source location"
    )

    return SOURCE


async def source(update: Update, context):

    results = search_place(
        update.message.text
    )

    keyboard = []

    for item in results:

        keyboard.append([
            InlineKeyboardButton(
                item["display_name"][:50],
                callback_data=f'source|{item["display_name"]}'
            )
        ])

    reply_markup = InlineKeyboardMarkup(
        keyboard
    )

    await update.message.reply_text(
        "Choose Source",
        reply_markup=reply_markup
    )


async def source_selected(update: Update, context):

    query = update.callback_query

    await query.answer()

    value = query.data.split("|", 1)[1]

    context.user_data["source"] = value

    await query.message.reply_text(
        "Type destination"
    )

    return DESTINATION


async def destination(update: Update, context):

    results = search_place(
        update.message.text
    )

    keyboard = []

    for item in results:

        keyboard.append([
            InlineKeyboardButton(
                item["display_name"][:50],
                callback_data=f'destination|{item["display_name"]}'
            )
        ])

    reply_markup = InlineKeyboardMarkup(
        keyboard
    )

    await update.message.reply_text(
        "Choose Destination",
        reply_markup=reply_markup
    )


async def destination_selected(update: Update, context):

    query = update.callback_query

    await query.answer()

    value = query.data.split("|", 1)[1]

    context.user_data["destination"] = value

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
        "Choose Date",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return DATE


async def date_selected(update: Update, context):

    query = update.callback_query

    await query.answer()

    context.user_data["date"] = query.data

    buses = scrape_prices(
        context.user_data["source"],
        context.user_data["destination"],
        context.user_data["date"]
    )

    keyboard = []

    for bus in buses:

        keyboard.append([
            InlineKeyboardButton(
                f'{bus["operator"]} - ₹{bus["price"]}',
                callback_data=f'bus|{bus["operator"]}|{bus["price"]}'
            )
        ])

    await query.message.reply_text(
        "Select Bus To Monitor",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def bus_selected(update: Update, context):

    query = update.callback_query

    await query.answer()

    _, operator, price = query.data.split("|")

    add_monitor(
        chat_id=query.message.chat_id,
        operator=operator,
        source=context.user_data["source"],
        destination=context.user_data["destination"],
        travel_date=context.user_data["date"],
        current_price=int(price)
    )

    await query.edit_message_text(
        f'''
✅ Monitor Created

Bus:
{operator}

Current Fare:
₹{price}

Monitoring:
Every 1 minute

Alert:
Immediate on fare drop
'''
    )
