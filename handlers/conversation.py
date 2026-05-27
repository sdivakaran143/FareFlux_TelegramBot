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

        if ":" in value:

            parts = value.split(":")

            if len(parts) >= 2:

                hour = int(parts[0])
                minute = int(parts[1])

                suffix = "AM"

                if hour >= 12:
                    suffix = "PM"

                if hour > 12:
                    hour -= 12

                if hour == 0:
                    hour = 12

                return (
                    f"{hour:02d}:{minute:02d} "
                    f"{suffix}"
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

    if chat_id not in USER_STATE:
        return

    step = USER_STATE[chat_id].get(
        "step"
    )

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

    if data == "create_monitor":

        USER_STATE[chat_id] = {

            "step": "monitor_name"
        }

        await query.message.reply_text(
            "📝 Enter Monitor Name"
        )

    elif data == "today":

        doj = datetime.now().strftime(
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

        USER_STATE[chat_id]["buses"] = buses

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

        await query.message.reply_text(

            f"🚌 {len(buses)} buses found\n"
            f"📅 Date: {doj}",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    elif data == "tomorrow":

        doj = (
            datetime.now()
            + timedelta(days=1)
        ).strftime(
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

        USER_STATE[chat_id]["buses"] = buses

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

        await query.message.reply_text(

            f"🚌 {len(buses)} buses found\n"
            f"📅 Date: {doj}",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    elif data.startswith("bus|"):

        bus_index = int(
            data.split("|")[1]
        )

        bus = USER_STATE[chat_id]["buses"][bus_index]

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
                USER_STATE[chat_id]["source_id"],

            "destination_id":
                USER_STATE[chat_id]["destination_id"],

            "date":
                USER_STATE[chat_id]["date"],

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
            f"💰 ₹{bus['price']}\n"
            f"⭐ {bus['rating']}\n"
            f"💺 Seats: "
            f"{bus['available_seats']}"
        )
