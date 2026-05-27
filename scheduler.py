
from apscheduler.schedulers.background import BackgroundScheduler

from database import (
    get_all_monitors,
    update_price
)

from services.scraper import scrape_prices


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

        monitors = get_all_monitors()

        for monitor in monitors:

            monitor_id = monitor[0]
            chat_id = monitor[1]
            operator = monitor[3]
            travel_date = monitor[6]
            old_price = monitor[7]
            booking_link = monitor[8]
            source_id = monitor[9]
            destination_id = monitor[10]

            buses = scrape_prices(
                source_id,
                destination_id,
                travel_date
            )

            for bus in buses:

                if operator.lower() in bus["operator"].lower():

                    new_price = bus["price"]

                    if new_price != old_price:

                        change_type = "📉 PRICE DROP" if new_price < old_price else "📈 PRICE HIKE"

                        text = f'''
{change_type}

🚌 {operator}

Old Price: ₹{old_price}
New Price: ₹{new_price}

🔗 {booking_link}
'''

                        application.create_task(
                            send_alert(
                                chat_id,
                                text
                            )
                        )

                        update_price(
                            monitor_id,
                            new_price
                        )

    scheduler.add_job(
        check_prices,
        "interval",
        minutes=1
    )

    scheduler.start()
