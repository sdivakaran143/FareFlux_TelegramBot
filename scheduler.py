from apscheduler.schedulers.background import BackgroundScheduler

        from database import (
            get_monitors,
            update_price
        )

        from services.scraper import scrape_prices

        scheduler = BackgroundScheduler()


        async def check_monitor(bot, monitor):

            (
                monitor_id,
                chat_id,
                operator,
                source,
                destination,
                travel_date,
                current_price
            ) = monitor

            buses = scrape_prices(
                source,
                destination,
                travel_date
            )

            for bus in buses:

                if bus["operator"] == operator:

                    latest_price = bus["price"]

                    if latest_price < current_price:

                        await bot.send_message(
                            chat_id=chat_id,
                            text=f"""
🔥 Fare Dropped

🚌 Operator:
{operator}

📍 Route:
{source}
→
{destination}

💰 Old Fare:
₹{current_price}

💸 New Fare:
₹{latest_price}
"""
                        )

                        update_price(
                            monitor_id,
                            latest_price
                        )


        def start_scheduler(bot):

            monitors = get_monitors()

            for monitor in monitors:

                scheduler.add_job(
                    check_monitor,
                    "interval",
                    minutes=1,
                    args=[bot, monitor],
                    id=str(monitor[0]),
                    replace_existing=True
                )

            scheduler.start()