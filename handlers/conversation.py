from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import ContextTypes

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
        "🚌 FareFlux Final",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def message_handler(update: Update, context):

    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if chat_id not in USER_STATE:
        return

    step = USER_STATE[chat_id]["step"]

    # MONITOR NAME

    if step == "monitor_name":

        USER_STATE[chat_id]["monitor_name"] = text
        USER_STATE[chat_id]["step"] = "source"

        await update.message.reply_text(
            "📍 Enter Source"
        )

    # SOURCE

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
                "❌ Source city not found.\n\nEnter RedBus source city code."
            )

    # SOURCE CODE

    elif step == "source_code":

        try:

            source_code = int(text)

        except:

            await update.message.reply_text(
                "❌ Invalid source city code."
            )

            return

        city_name = USER_STATE[chat_id]["pending_source"]

        save_city_code(
            city_name,
            source_code
        )

        USER_STATE[chat_id]["source"] = city_name
        USER_STATE[chat_id]["source_id"] = source_code
        USER_STATE[chat_id]["step"] = "destination"

        await update.message.reply_text(
            "✅ Source saved.\n\n📍 Enter Destination"
        )

    # DESTINATION

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
                "❌ Destination city not found.\n\nEnter RedBus destination city code."
            )

    # DESTINATION CODE

    elif step == "destination_code":

        try:

            destination_code = int(text)

        except:

            await update.message.reply_text(
                "❌ Invalid destination city code."
            )

            return

        city_name = USER_STATE[chat_id]["pending_destination"]

        save_city_code(
            city_name,
            destination_code
        )

        USER_STATE[chat_id]["destination"] = city_name
        USER_STATE[chat_id]["destination_id"] = destination_code

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

    try:

        await query.answer()

    except Exception as e:

        print("CALLBACK ANSWER ERROR:", e)

    chat_id = query.message.chat_id
    data = query.data

    # CREATE MONITOR

    if data == "create_monitor":

        USER_STATE[chat_id] = {
            "step": "monitor_name"
        }

        await query.message.reply_text(
            "📝 Enter Monitor Name"
        )

    # MY MONITORS

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

    # DATE SELECTED

    elif data in ["today", "tomorrow"]:

        try:

            if data == "today":

                travel_date = datetime.now()

            else:

                travel_date = (
                    datetime.now() + timedelta(days=1)
                )

            USER_STATE[chat_id]["date"] = (
                travel_date.strftime("%Y-%m-%d")
            )

            if "source_id" not in USER_STATE[chat_id]:

                await query.message.reply_text(
                    "❌ Source city missing. Restart with /start"
                )

                return

            if "destination_id" not in USER_STATE[chat_id]:

                await query.message.reply_text(
                    "❌ Destination city missing. Restart with /start"
                )

                return

            await query.message.reply_text(
                "🔍 Fetching live buses..."
            )

            buses = scrape_prices(
                USER_STATE[chat_id]["source_id"],
                USER_STATE[chat_id]["destination_id"],
                USER_STATE[chat_id]["date"]
            )

            print("BUSES:", buses)

            if not buses:

                await query.message.reply_text(
                    "❌ No buses found."
                )

                return

            USER_STATE[chat_id]["buses"] = buses

            keyboard = []

            for index, bus in enumerate(buses[:25]):

                operator = bus.get(
                    "operator",
                    "Unknown"
                )

                price = bus.get(
                    "price",
                    0
                )

                keyboard.append([
                    InlineKeyboardButton(
                        f"{operator} • ₹{price}",
                        callback_data=f"bus|{index}"
                    )
                ])

            await query.message.reply_text(
                "🚌 Select Bus",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:

            print("DATE CALLBACK ERROR:", e)

            await query.message.reply_text(
                f"❌ Failed to fetch buses.\n\n{str(e)}"
            )

    # BUS SELECTED

    elif data.startswith("bus|"):

        try:

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
                f"""
✅ Monitor Created

📝 Name:
{USER_STATE[chat_id]["monitor_name"]}

🚌 Bus:
{bus["operator"]}

💰 Price:
₹{bus["price"]}

💺 Seats:
{bus.get("available_seats", 0)}

🔗 Booking:
{bus["booking_link"]}
"""
            )

        except Exception as e:

            print("BUS SELECT ERROR:", e)

            await query.message.reply_text(
                "❌ Failed to create monitor."
            )

    # VIEW MONITOR

    elif data.startswith("view|"):

        try:

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
                f"""
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
""",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        except Exception as e:

            print("VIEW MONITOR ERROR:", e)

            await query.message.reply_text(
                "❌ Failed to load monitor."
            )

    # DELETE MONITOR

    elif data.startswith("delete|"):

        try:

            monitor_id = int(data.split("|")[1])

            delete_monitor(monitor_id)

            await query.message.reply_text(
                "✅ Monitor Removed"
            )

        except Exception as e:

            print("DELETE MONITOR ERROR:", e)

            await query.message.reply_text(
                "❌ Failed to remove monitor."
            )
