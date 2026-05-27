from apscheduler.schedulers.background import (
    BackgroundScheduler
)

import asyncio

from services.scraper import (
    scrape_prices
)

from storage import (
    load_monitors,
    save_monitors
)


LAST_PRICES = {}


def start_scheduler(application):

    scheduler = BackgroundScheduler()

    async def send_alert(
        chat_id,
        text
    ):

        await application.bot.send_message(
            chat_id=chat_id,
            text=text
        )

    def check_prices():

        print("\n====================")
        print("CHECKING PRICES")
        print("====================")

        monitors = load_monitors()

        for monitor in monitors:

            try:

                buses = scrape_prices(

                    monitor["source_id"],

                    monitor["destination_id"],

                    monitor["date"]
                )

                target_bus = None

                for bus in buses:

                    if (
                        bus["operator"]
                        ==
                        monitor["bus_operator"]
                    ):

                        target_bus = bus

                        break

                if not target_bus:
                    continue

                current_price = (
                    target_bus["price"]
                )

                monitor_key = (
                    monitor["monitor_name"]
                )

                old_price = LAST_PRICES.get(
                    monitor_key
                )

                if old_price is None:

                    LAST_PRICES[
                        monitor_key
                    ] = current_price

                    continue

                if current_price != old_price:

                    direction = "⬆️ Increased"

                    if current_price < old_price:
                        direction = "⬇️ Dropped"

                    message = (
                        f"📢 Price Update\\n\\n"
                        f"🚌 {target_bus['operator']}\\n"
                        f"💰 Old: ₹{old_price}\\n"
                        f"💰 New: ₹{current_price}\\n"
                        f"{direction}"
                    )

                    asyncio.run(
                        send_alert(
                            monitor["chat_id"],
                            message
                        )
                    )

                    LAST_PRICES[
                        monitor_key
                    ] = current_price

            except Exception as e:

                print(
                    "SCHEDULER ERROR:"
                )

                print(str(e))

    scheduler.add_job(
        check_prices,
        "interval",
        minutes=1
    )

    scheduler.start()

    print(
        "Scheduler started"
    )
