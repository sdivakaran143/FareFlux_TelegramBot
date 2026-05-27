
import requests
import time
import json

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


session = requests.Session()

retry_strategy = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(
    max_retries=retry_strategy
)

session.mount(
    "https://",
    adapter
)


def scrape_prices(
    source_id,
    destination_id,
    date
):

    print("\n========================")
    print("SCRAPER START")
    print("========================")

    print("SOURCE:", source_id)
    print("DESTINATION:", destination_id)
    print("DATE:", date)

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
        "bT": 1,
        "clearLMBFilter": "undefined",
        "isFilterApplied": "false"
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
        "dpList": [],
        "CampaignFilter": [],
        "at": [],
        "persuasionList": [],
        "bpIdentifier": [],
        "dpIdentifier": [],
        "bcf": [],
        "opBusTypeFilterList": [],
        "priceRange": [],
        "RouteIds": [],
        "bpKeys": [],
        "dpKeys": [],
        "streaksFilter": [],
        "preRouteFilters": None
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Macintosh; Intel Mac OS X 10_15_7)"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://www.redbus.in",
        "Referer": "https://www.redbus.in/"
    }

    print("\nREQUEST PARAMS:")
    print(json.dumps(params, indent=2))

    response = session.post(
        url,
        params=params,
        headers=headers,
        json=payload,
        timeout=90
    )

    print("STATUS:", response.status_code)
    print("FINAL URL:", response.url)

    data = response.json()

    inventories = (
        data.get("data", {})
        .get("inventories", [])
    )

    print("INVENTORIES:", len(inventories))

    buses = []

    for bus in inventories:

        fares = bus.get("fareList", [])

        current_price = 0

        if fares:
            current_price = min(fares)

        parsed_bus = {

            "operator":
                bus.get("travelsName"),

            "price":
                current_price,

            "original_price":
                current_price,

            "offer":
                "",

            "available_seats":
                bus.get("availableSeats"),

            "departure":
                bus.get("departureTime"),

            "arrival":
                bus.get("arrivalTime"),

            "duration":
                bus.get("journeyDurationMin"),

            "rating":
                bus.get("totalRatings"),

            "bus_type":
                bus.get("busType")
        }

        print(json.dumps(parsed_bus, indent=2))

        buses.append(parsed_bus)

    buses = sorted(
        buses,
        key=lambda x: x["price"]
    )

    return buses
