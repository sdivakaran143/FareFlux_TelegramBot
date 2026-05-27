from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes

from services.redbus_locations import (
    search_redbus_locations
)

from services.scraper import scrape_prices

from database import (
    add_monitor,
    get_monitors,
    delete_monitor
)

USER_STATE = {}


async def start_command(update: Update, context):

    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Create Monitor",
                callback_data="create_monitor"
            )
        ],
        [
            InlineKeyboardButton(
                "📋 My Monitors",
                callback_data="my_monitors"
            )
        ]
    ]

    await update.message.reply_text(
        "🚌 FareFlux RedBus Live",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def message_handler(update: Update, context):

    chat_id = update.effective_chat.id
    text = update.message.text

    if chat_id not in USER_STATE:
        return

    step = USER_STATE[chat_id]["step"]

    if step == "monitor_name":

        USER_STATE[chat_id]["monitor_name"] = text
        USER_STATE[chat_id]["step"] = "source"

        await update.message.reply_text(
            "📍 Enter Source"
        )

    elif step == "source":

        results = search_redbus_locations(text)

        USER_STATE[chat_id]["source_results"] = results

        keyboard = []

        for index, item in enumerate(results):

            keyboard.append([
                InlineKeyboardButton(
                    item["name"],
                    callback_data=f"source|{index}"
                )
            ])

        await update.message.reply_text(
            "📍 Select Source",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif step == "destination":

        results = search_redbus_locations(text)

        USER_STATE[chat_id]["destination_results"] = results

        keyboard = []

        for index, item in enumerate(results):

            keyboard.append([
                InlineKeyboardButton(
                    item["name"],
                    callback_data=f"destination|{index}"
                )
            ])

        await update.message.reply_text(
            "📍 Select Destination",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def callback_handler(update: Update, context):

    query = update.callback_query

    await query.answer()

    chat_id = query.message.chat_id
    data = query.data

    if data == "create_monitor":

        USER_STATE[chat_id] = {
            "step": "monitor_name"
        }

        await query.message.reply_text(
            "📝 Enter Monitor Name"
        )

    elif data == "my_monitors":

        monitors = get_monitors(chat_id)

        if not monitors:

            await query.message.reply_text(
                "No monitors found"
            )

            return

        keyboard = []

        for monitor in monitors:

            keyboard.append([
                InlineKeyboardButton(
                    monitor[2],
                    callback_data=f"view|{monitor[0]}"
                )
            ])

        await query.message.reply_text(
            "📋 Your Monitors",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("source|"):

        index = int(data.split("|")[1])

        selected = USER_STATE[chat_id]["source_results"][index]

        USER_STATE[chat_id]["source"] = selected["name"]
        USER_STATE[chat_id]["source_id"] = selected["id"]
        USER_STATE[chat_id]["step"] = "destination"

        await query.message.reply_text(
            "📍 Enter Destination"
        )

    elif data.startswith("destination|"):

        index = int(data.split("|")[1])

        selected = USER_STATE[chat_id]["destination_results"][index]

        USER_STATE[chat_id]["destination"] = selected["name"]
        USER_STATE[chat_id]["destination_id"] = selected["id"]

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

        USER_STATE[chat_id]["date"] = "2026-05-28"

        buses = scrape_prices(
            USER_STATE[chat_id]["source_id"],
            USER_STATE[chat_id]["destination_id"],
            USER_STATE[chat_id]["date"]
        )

        USER_STATE[chat_id]["buses"] = buses

        keyboard = []

        for index, bus in enumerate(buses[:25]):

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

    elif data.startswith("bus|"):

        index = int(data.split("|")[1])

        bus = USER_STATE[chat_id]["buses"][index]

        add_monitor(
            chat_id=chat_id,
            monitor_name=USER_STATE[chat_id]["monitor_name"],
            operator=bus["operator"],
            source=USER_STATE[chat_id]["source"],
            destination=USER_STATE[chat_id]["destination"],
            travel_date=USER_STATE[chat_id]["date"],
            current_price=bus["price"],
            booking_link=bus["booking_link"]
        )

        await query.message.reply_text(
            f'''
✅ Monitor Created

📝 Name:
{USER_STATE[chat_id]["monitor_name"]}

🚌 Bus:
{bus["operator"]}

💰 Price:
₹{bus["price"]}

💺 Seats:
{bus["available_seats"]}

🔗 Booking:
{bus["booking_link"]}
'''
        )

    elif data.startswith("view|"):

        monitor_id = int(data.split("|")[1])

        monitors = get_monitors(chat_id)

        selected = None

        for item in monitors:

            if item[0] == monitor_id:
                selected = item

        if not selected:
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    "❌ Remove Monitor",
                    callback_data=f"delete|{monitor_id}"
                )
            ]
        ]

        await query.message.reply_text(
            f'''
📋 Monitor Status

📝 Name:
{selected[2]}

🚌 Bus:
{selected[3]}

📍 Route:
{selected[4]} → {selected[5]}

💰 Current Price:
₹{selected[7]}

🔗 Booking:
{selected[8]}
''',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("delete|"):

        monitor_id = int(data.split("|")[1])

        delete_monitor(monitor_id)

        await query.message.reply_text(
            "✅ Monitor Removed"
        )