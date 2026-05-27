
        from playwright.sync_api import sync_playwright
        import random
        import time

        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        ]

        def scrape_prices(source, destination, date):

            buses = []

            with sync_playwright() as p:

                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage"
                    ]
                )

                context = browser.new_context(
                    user_agent=random.choice(USER_AGENTS),
                    viewport={"width": 1280, "height": 720},
                    locale="en-IN"
                )

                page = context.new_page()

                page.add_init_script("""
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});
""")

                url = (
                    f"https://www.redbus.in/bus-tickets/"
                    f"{source.lower().replace(' ', '-')}"
                    f"-to-"
                    f"{destination.lower().replace(' ', '-')}"
                    f"?date={date}"
                )

                page.goto(url, timeout=120000)

                time.sleep(random.randint(5, 9))

                cards = page.locator("div.ticket").all()

                for card in cards:

                    try:

                        operator = card.locator(".travels").inner_text()

                        price = card.locator(
                            ".fare .f-bold"
                        ).inner_text()

                        price = int(
                            price.replace("₹", "")
                                 .replace(",", "")
                        )

                        buses.append({
                            "operator": operator,
                            "price": price
                        })

                    except:
                        pass

                browser.close()

            return buses
