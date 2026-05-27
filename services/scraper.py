import random


def scrape_prices(source, destination, date):

    base = random.randint(650, 1200)

    return [
        {
            "operator": "KPN Travels",
            "price": base,
            "departure": "10:00 PM"
        },
        {
            "operator": "YBM Travels",
            "price": base - 80,
            "departure": "11:00 PM"
        },
        {
            "operator": "Parveen Travels",
            "price": base + 120,
            "departure": "09:30 PM"
        }
    ]