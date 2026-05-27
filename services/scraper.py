
import requests


def scrape_prices(
    source_id,
    destination_id,
    date
):

    url = "https://www.redbus.in/rpw/api/searchResults"

    params = {
        "fromCity": source_id,
        "toCity": destination_id,
        "DOJ": date,
        "limit": 50,
        "offset": 0,
        "meta": "true",
        "groupId": 0,
        "sectionId": 0,
        "sort": 0,
        "sortOrder": 0,
        "from": "initialLoad",
        "getUuid": "true",
        "bT": 1,
        "clearLMBFilter": "undefined",
        "isFilterApplied": "false"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.redbus.in/"
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=20
        )

        print("REQUEST URL:", response.url)
        print("STATUS:", response.status_code)

        data = response.json()

        inventories = (
            data.get("data", {})
            .get("inventories", [])
        )

        buses = []

        for bus in inventories:

            fares = bus.get("fareList", [])

            price = min(fares) if fares else 0

            buses.append({
                "operator": bus.get("travelsName", "Unknown"),
                "price": price,
                "available_seats": bus.get("availableSeats", 0),
                "booking_link": "https://www.redbus.in/"
            })

        return buses

    except Exception as e:

        print("SCRAPER ERROR:", str(e))

        return []
