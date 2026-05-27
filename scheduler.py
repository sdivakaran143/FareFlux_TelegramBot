
        from apscheduler.schedulers.background import BackgroundScheduler
        from database import get_monitors, update_price
        from services.scraper import scrape_prices

        scheduler = BackgroundScheduler()

        async def check_monitor(bot, monitor):

            monitor_id, chat_id, source, destination, travel_date, threshold, frequency, last_price = monitor

            buses = scrape_prices(
                source,
                destination,
                travel_date
            )

            if not buses:
                return

            cheapest = min([x["price"] for x in buses])

            if cheapest < last_price:

                await bot.send_message(
                    chat_id=chat_id,
                    text=f'''
🚌 Fare Dropped

Route:
{source} → {destination}

Old Price:
₹{last_price}

New Price:
₹{cheapest}
'''
                )

                update_price(monitor_id, cheapest)

        def start_scheduler(bot):

            monitors = get_monitors()

            for monitor in monitors:

                scheduler.add_job(
                    check_monitor,
                    "interval",
                    minutes=monitor[6],
                    args=[bot, monitor],
                    id=str(monitor[0]),
                    replace_existing=True
                )

            scheduler.start()
