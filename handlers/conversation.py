
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from services.city_code_service import (
    find_city_code,
    save_city_code
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
        "🚌 DIVA'S FareFlux Bot",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def message_handler(update: Update, context):

    chat_id = update.effective_chat.id
    text = update.message.text.strip()

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

        city_code = find_city_code(text)

        if city_code:

            USER_STATE[chat_id]["source"] = text
            USER_STATE[chat_id]["source_id"] = city_code
            USER_STATE[chat_id]["step"] = "destination"

            await update.message.reply_text(
                "📍 Enter Destination"
            )

        else:

            USER_STATE[chat_id]["pending_source"] = text
            USER_STATE[chat_id]["step"] = "source_code"

            await update.message.reply_text(
                "Enter source city code"
            )

    elif step == "source_code":

        save_city_code(
            USER_STATE[chat_id]["pending_source"],
            int(text)
        )

        USER_STATE[chat_id]["source"] = USER_STATE[chat_id]["pending_source"]
        USER_STATE[chat_id]["source_id"] = int(text)
        USER_STATE[chat_id]["step"] = "destination"

        await update.message.reply_text(
            "📍 Enter Destination"
        )

    elif step == "destination":

        city_code = find_city_code(text)

        if city_code:

            USER_STATE[chat_id]["destination"] = text
            USER_STATE[chat_id]["destination_id"] = city_code

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

            await update.message.reply_text(
                "📅 Select Travel Date",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        else:

            USER_STATE[chat_id]["pending_destination"] = text
            USER_STATE[chat_id]["step"] = "destination_code"

            await update.message.reply_text(
                "Enter destination city code"
            )

    elif step == "destination_code":

        save_city_code(
            USER_STATE[chat_id]["pending_destination"],
            int(text)
        )

        USER_STATE[chat_id]["destination"] = USER_STATE[chat_id]["pending_destination"]
        USER_STATE[chat_id]["destination_id"] = int(text)

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

        await update.message.reply_text(
            "📅 Select Travel Date",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def callback_handler(update: Update, context):

    query = update.callback_query

    if not query:
        return

    data = query.data
    chat_id = query.message.chat_id

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

    elif data in ["today", "tomorrow"]:

        if data == "today":
            travel_date = datetime.now()
        else:
            travel_date = datetime.now() + timedelta(days=1)

        formatted_date = travel_date.strftime("%d-%b-%Y")

        USER_STATE[chat_id]["date"] = formatted_date

        await query.message.reply_text(
            "🔍 Fetching buses..."
        )

        buses = scrape_prices(
            USER_STATE[chat_id]["source_id"],
            USER_STATE[chat_id]["destination_id"],
            formatted_date
        )

        if not buses:

            await query.message.reply_text(
                "❌ No buses found"
            )

            return

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
            chat_id,
            USER_STATE[chat_id]["monitor_name"],
            bus["operator"],
            USER_STATE[chat_id]["source"],
            USER_STATE[chat_id]["destination"],
            USER_STATE[chat_id]["date"],
            bus["price"],
            bus["booking_link"],
            USER_STATE[chat_id]["source_id"],
            USER_STATE[chat_id]["destination_id"]
        )

        await query.message.reply_text(
            f'''
✅ Monitor Created

🚌 {bus["operator"]}
💰 Current Price: ₹{bus["price"]}

You will now receive:
📉 Price Drop Alerts
📈 Price Hike Alerts
'''
        )

    elif data.startswith("view|"):

        monitor_id = int(data.split("|")[1])

        monitors = get_monitors(chat_id)

        selected = None

        for monitor in monitors:

            if monitor[0] == monitor_id:
                selected = monitor

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
📋 Monitor

📝 {selected[2]}
🚌 {selected[3]}
💰 ₹{selected[7]}

🔗 {selected[8]}
''',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("delete|"):

        monitor_id = int(data.split("|")[1])

        delete_monitor(monitor_id)

        await query.message.reply_text(
            "✅ Monitor Removed"
        )
