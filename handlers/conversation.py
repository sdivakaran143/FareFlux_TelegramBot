from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)

from telegram.ext import (
    ContextTypes
)

from datetime import (
    datetime,
    timedelta
)

from services.scraper import (
    scrape_prices
)

from storage import (
    add_monitor,
    load_monitors,
    remove_monitor
)


USER_STATE = {}


def format_time(value):

    try:

        value = str(value)

        if "T" in value:

            dt = datetime.fromisoformat(
                value
            )

            return dt.strftime(
                "%I:%M %p"
            )

        return value

    except:

        return str(value)


def format_duration(minutes):

    try:

        minutes = int(minutes)

        hours = minutes // 60

        mins = minutes % 60

        return f"{hours}h {mins}m"

    except:

        return str(minutes)


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [

        [
            InlineKeyboardButton(
                "➕ Create Monitor",
                callback_data="create_monitor"
            )
        ],

        [
            InlineKeyboardButton(
                "📋 View Monitors",
                callback_data="view_monitors"
            )
        ]
    ]

    await update.message.reply_text(

        "🔥 DIVA'S FareFlux Bot",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    chat_id = update.effective_chat.id

    text = update.message.text.strip()

    print("\nMESSAGE RECEIVED:")
    print(text)

    if chat_id not in USER_STATE:
        return

    step = USER_STATE[chat_id].get(
        "step"
    )

    print("CURRENT STEP:", step)

    if step == "monitor_name":

        USER_STATE[chat_id][
            "monitor_name"
        ] = text

        USER_STATE[chat_id][
            "step"
        ] = "source"

        await update.message.reply_text(
            "📍 Enter Source"
        )

    elif step == "source":

        USER_STATE[chat_id][
            "source_name"
        ] = text

        USER_STATE[chat_id][
            "source_id"
        ] = 89782

        USER_STATE[chat_id][
            "step"
        ] = "destination"

        await update.message.reply_text(
            "📍 Enter Destination"
        )

    elif step == "destination":

        USER_STATE[chat_id][
            "destination_name"
        ] = text

        USER_STATE[chat_id][
            "destination_id"
        ] = 1042

        USER_STATE[chat_id][
            "step"
        ] = "date"

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

            "📅 Select Date",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )


async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    chat_id = update.effective_chat.id

    print("\nCALLBACK DATA:")
    print(data)

    if data == "create_monitor":

        USER_STATE[chat_id] = {

            "step": "monitor_name"
        }

        await query.message.reply_text(
            "📝 Enter Monitor Name"
        )

    elif data == "view_monitors":

        monitors = load_monitors()

        user_monitors = [

            monitor

            for monitor in monitors

            if monitor["chat_id"] == chat_id
        ]

        if not user_monitors:

            await query.message.reply_text(
                "❌ No monitors found"
            )

            return

        keyboard = []

        for monitor in user_monitors:

            keyboard.append([

                InlineKeyboardButton(

                    monitor["monitor_name"],

                    callback_data=
                    f"monitor|"
                    f"{monitor['monitor_name']}"
                )
            ])

        await query.message.reply_text(

            "📋 Your Monitors",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    elif data == "today":

        today = datetime.now()

        doj = today.strftime(
            "%d-%b-%Y"
        )

        USER_STATE[chat_id][
            "date"
        ] = doj

        buses = scrape_prices(

            USER_STATE[chat_id][
                "source_id"
            ],

            USER_STATE[chat_id][
                "destination_id"
            ],

            doj
        )

        USER_STATE[chat_id][
            "buses"
        ] = buses

        keyboard = []

        for index, bus in enumerate(
            buses[:25]
        ):

            keyboard.append([

                InlineKeyboardButton(

                    (
                        f"{bus['operator']} "
                        f"• ₹{bus['price']}"
                    ),

                    callback_data=f"bus|{index}"
                )
            ])

            keyboard.append([

                InlineKeyboardButton(

                    (
                        f"💺 {bus['bus_type']} | "
                        f"🕒 "
                        f"{format_time(bus['departure'])}"
                        f" → "
                        f"{format_time(bus['arrival'])}"
                    ),

                    callback_data="ignore"
                )
            ])

            keyboard.append([

                InlineKeyboardButton(

                    (
                        f"⌛ "
                        f"{format_duration(bus['duration'])} | "
                        f"⭐ {bus['rating']} | "
                        f"💺 Seats "
                        f"{bus['available_seats']}"
                    ),

                    callback_data="ignore"
                )
            ])

        await query.message.reply_text(

            f"🚌 {len(buses)} buses found",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    elif data == "tomorrow":

        tomorrow = (
            datetime.now()
            + timedelta(days=1)
        )

        doj = tomorrow.strftime(
            "%d-%b-%Y"
        )

        USER_STATE[chat_id][
            "date"
        ] = doj

        buses = scrape_prices(

            USER_STATE[chat_id][
                "source_id"
            ],

            USER_STATE[chat_id][
                "destination_id"
            ],

            doj
        )

        USER_STATE[chat_id][
            "buses"
        ] = buses

        keyboard = []

        for index, bus in enumerate(
            buses[:25]
        ):

            keyboard.append([

                InlineKeyboardButton(

                    (
                        f"{bus['operator']} "
                        f"• ₹{bus['price']}"
                    ),

                    callback_data=f"bus|{index}"
                )
            ])

            keyboard.append([

                InlineKeyboardButton(

                    (
                        f"💺 {bus['bus_type']} | "
                        f"🕒 "
                        f"{format_time(bus['departure'])}"
                        f" → "
                        f"{format_time(bus['arrival'])}"
                    ),

                    callback_data="ignore"
                )
            ])

            keyboard.append([

                InlineKeyboardButton(

                    (
                        f"⌛ "
                        f"{format_duration(bus['duration'])} | "
                        f"⭐ {bus['rating']} | "
                        f"💺 Seats "
                        f"{bus['available_seats']}"
                    ),

                    callback_data="ignore"
                )
            ])

        await query.message.reply_text(

            f"🚌 {len(buses)} buses found",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    elif data.startswith("bus|"):

        bus_index = int(
            data.split("|")[1]
        )

        bus = USER_STATE[
            chat_id
        ]["buses"][bus_index]

        monitor_name = (

            f"{USER_STATE[chat_id]['monitor_name']} "

            f"- "

            f"{bus['operator']}"
        )

        add_monitor({

            "monitor_name":
                monitor_name,

            "chat_id":
                chat_id,

            "source_id":
                USER_STATE[chat_id][
                    "source_id"
                ],

            "destination_id":
                USER_STATE[chat_id][
                    "destination_id"
                ],

            "date":
                USER_STATE[chat_id][
                    "date"
                ],

            "bus_operator":
                bus["operator"]
        })

        await query.message.reply_text(

            f"✅ Monitor Created\n\n"

            f"📋 {monitor_name}\n\n"

            f"🚌 {bus['operator']}\n"

            f"💺 {bus['bus_type']}\n"

            f"🕒 "
            f"{format_time(bus['departure'])} "
            f"→ "
            f"{format_time(bus['arrival'])}\n"

            f"⌛ "
            f"{format_duration(bus['duration'])}\n"

            f"💰 ₹{bus['price']} "
            f"(₹{bus['original_price']})\n"

            f"🎁 {bus['offer']}\n"

            f"⭐ {bus['rating']}\n"

            f"💺 Seats: "
            f"{bus['available_seats']}"
        )

    elif data.startswith("monitor|"):

        monitor_name = data.split("|")[1]

        monitors = load_monitors()

        target = None

        for monitor in monitors:

            if (
                monitor["monitor_name"]
                == monitor_name
            ):

                target = monitor

                break

        if not target:
            return

        keyboard = [

            [
                InlineKeyboardButton(
                    "❌ Remove Monitor",
                    callback_data=
                    f"remove|{monitor_name}"
                )
            ]
        ]

        await query.message.reply_text(

            f"📋 {monitor_name}",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    elif data.startswith("remove|"):

        monitor_name = data.split("|")[1]

        remove_monitor(
            monitor_name
        )

        await query.message.reply_text(
            "✅ Monitor Removed"
        )
