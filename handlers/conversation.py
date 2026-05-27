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
from database import add_monitor

SOURCE = 1
DESTINATION = 2
DATE = 3
THRESHOLD = 4


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Enter Source Location"
    )

    return SOURCE


async def source(update: Update, context):

    place = search_place(update.message.text)

    if not place:

        await update.message.reply_text(
            "Invalid source."
        )

        return SOURCE

    context.user_data["source"] = update.message.text

    await update.message.reply_text(
        "Enter Destination"
    )

    return DESTINATION


async def destination(update: Update, context):

    place = search_place(update.message.text)

    if not place:

        await update.message.reply_text(
            "Invalid destination."
        )

        return DESTINATION

    context.user_data["destination"] = update.message.text

    await update.message.reply_text(
        "Enter Travel Date (YYYY-MM-DD)"
    )

    return DATE


async def date(update: Update, context):

    context.user_data["date"] = update.message.text

    await update.message.reply_text(
        "Enter Threshold Fare"
    )

    return THRESHOLD


async def threshold(update: Update, context):

    context.user_data["threshold"] = int(
        update.message.text
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "5 Min",
                callback_data="5"
            )
        ],
        [
            InlineKeyboardButton(
                "15 Min",
                callback_data="15"
            )
        ],
        [
            InlineKeyboardButton(
                "60 Min",
                callback_data="60"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(
        keyboard
    )

    await update.message.reply_text(
        "Select Monitoring Frequency",
        reply_markup=reply_markup
    )

    return ConversationHandler.END


async def frequency(update: Update, context):

    query = update.callback_query

    await query.answer()

    frequency_value = int(query.data)

    add_monitor(
        chat_id=query.message.chat_id,
        source=context.user_data["source"],
        destination=context.user_data["destination"],
        travel_date=context.user_data["date"],
        threshold=context.user_data["threshold"],
        frequency=frequency_value
    )

    await query.edit_message_text(
        f"""
✅ Monitor Created

Route:
{context.user_data["source"]}
→
{context.user_data["destination"]}

Frequency:
Every {frequency_value} minutes
"""
    )
