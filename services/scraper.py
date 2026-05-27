import requests


def scrape_prices(
    source_id,
    destination_id,
    date
):

    url = (
        "https://www.redbus.in/rpw/api/searchResults"
    )

    params = {
        "fromCity": source_id,
        "toCity": destination_id,
        "DOJ": date,
        "limit": 100,
        "offset": 0,
        "meta": "true",
        "groupId": 0,
        "sectionId": 0,
        "sort": 0,
        "sortOrder": 0,
        "from": "initialLoad",
        "getUuid": "true",
        "bT": 1
    }

    payload = {
        "appliedFilterCount": 0,
        "onlyShow": [],
        "dt": [],
        "SeaterType": [],
        "AcType": [],
        "travelsList": [],
        "amtList": [],
        "bpList": [],
        "dpList": []
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Origin": "https://www.redbus.in",
        "Referer": "https://www.redbus.in/"
    }

    response = requests.post(
        url,
        params=params,
        json=payload,
        headers=headers,
        timeout=60
    )

    data = response.json()

    inventories = data["data"]["inventories"]

    buses = []

    for bus in inventories:

        buses.append({
            "operator": bus.get("travelsName"),
            "price": min(bus.get("fareList", [0])),
            "available_seats": bus.get("availableSeats"),
            "departure": bus.get("departureTime"),
            "bus_type": bus.get("busType"),
            "route_id": bus.get("routeId"),
            "service_id": bus.get("serviceId"),
            "booking_link": (
                f"https://www.redbus.in/booking/"
                f"{bus.get('routeId')}"
            )
        })

    return buses