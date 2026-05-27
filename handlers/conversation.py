from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from services.location_service import search_place
from services.scraper import scrape_prices
from database import add_monitor

SOURCE = 1
DESTINATION = 2
DATE = 3
BUS = 4


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚌 Enter Source Location")
    return SOURCE


async def source(update: Update, context: ContextTypes.DEFAULT_TYPE):

    results = search_place(update.message.text)

    if not results:
        await update.message.reply_text("No source suggestions found.")
        return SOURCE

    keyboard = []

    for item in results:
        keyboard.append([
            InlineKeyboardButton(
                item["display_name"][:60],
                callback_data=f"source|{item['display_name']}"
            )
        ])

    await update.message.reply_text(
        "📍 Select Source",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return SOURCE


async def source_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    context.user_data["source"] = query.data.split("|", 1)[1]

    await query.message.reply_text("📍 Enter Destination")

    return DESTINATION


async def destination(update: Update, context: ContextTypes.DEFAULT_TYPE):

    results = search_place(update.message.text)

    if not results:
        await update.message.reply_text("No destination suggestions found.")
        return DESTINATION

    keyboard = []

    for item in results:
        keyboard.append([
            InlineKeyboardButton(
                item["display_name"][:60],
                callback_data=f"destination|{item['display_name']}"
            )
        ])

    await update.message.reply_text(
        "📍 Select Destination",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return DESTINATION


async def destination_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    context.user_data["destination"] = query.data.split("|", 1)[1]

    keyboard = [
        [InlineKeyboardButton("Today", callback_data="today")],
        [InlineKeyboardButton("Tomorrow", callback_data="tomorrow")]
    ]

    await query.message.reply_text(
        "📅 Select Travel Date",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return DATE


async def date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
                f"{bus['operator']} • ₹{bus['price']} • {bus['departure']}",
                callback_data=f"bus|{bus['operator']}|{bus['price']}"
            )
        ])

    await query.message.reply_text(
        "🚌 Select Bus To Monitor",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return BUS


async def bus_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
        f"""✅ Monitor Created

🚌 Operator:
{operator}

💰 Current Fare:
₹{price}

⏱ Checking:
Every 1 minute

🔔 Alert:
Immediate when fare drops"""
    )

    return ConversationHandler.END
