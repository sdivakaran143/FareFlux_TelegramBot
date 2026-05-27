import requests
import time

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


session = requests.Session()

retry_strategy = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("https://", adapter)


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

    all_inventories = []
    offset = 0

    while True:

        params["offset"] = offset

        response = session.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=90
        )

        if response.status_code != 200:
            break

        data = response.json()

        inventories = (
            data.get("data", {})
            .get("inventories", [])
        )

        if not inventories:
            break

        all_inventories.extend(
            inventories
        )

        offset += 100

    buses = []

    for bus in all_inventories:

        fares = bus.get("fareList", [])

        current_price = 0

        if fares:
            current_price = min(fares)

        original_price = current_price

        offer = ""

        try:

            campaign = bus.get(
                "operatorOfferCampaign",
                {}
            )

            if campaign:

                cmpg = campaign.get(
                    "CmpgList",
                    []
                )

                if cmpg:

                    first = cmpg[0]

                    offer = first.get(
                        "CampaignDesc",
                        ""
                    )

                    original_prices = first.get(
                        "OriginalPrices",
                        []
                    )

                    discounted_prices = first.get(
                        "DiscountedPrices",
                        []
                    )

                    if original_prices:
                        original_price = min(
                            original_prices
                        )

                    if discounted_prices:
                        current_price = min(
                            discounted_prices
                        )

        except Exception:
            pass

        parsed_bus = {

            "operator":
                bus.get("travelsName"),

            "price":
                current_price,

            "original_price":
                original_price,

            "offer":
                offer,

            "available_seats":
                bus.get("availableSeats"),

            "departure":
                bus.get("departureTime"),

            "arrival":
                bus.get("arrivalTime"),

            "duration":
                bus.get(
                    "journeyDurationMin"
                ),

            "rating":
                bus.get(
                    "totalRatings"
                ),

            "bus_type":
                bus.get("busType"),

            "boarding_point":
                bus.get(
                    "standardBpName"
                ),

            "dropping_point":
                bus.get(
                    "standardDpName"
                ),

            "booking_link":
                "https://www.redbus.in/"
        }

        buses.append(parsed_bus)

    buses = sorted(
        buses,
        key=lambda x: x["price"]
    )

    return buses
