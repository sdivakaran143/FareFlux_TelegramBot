import requests
import json


def scrape_prices(
    source_id,
    destination_id,
    date
):

    print("\n========================")
    print("SCRAPER START")
    print("========================")

    print("SOURCE ID:", source_id)
    print("DESTINATION ID:", destination_id)
    print("DATE:", date)

    url = (
        "https://www.redbus.in/rpw/api/searchResults"
    )

    params = {

        "fromCity":
            source_id,

        "toCity":
            destination_id,

        "DOJ":
            date,

        "limit":
            100,

        "offset":
            0,

        "meta":
            "true",

        "groupId":
            0,

        "sectionId":
            0,

        "sort":
            0,

        "sortOrder":
            0,

        "from":
            "initialLoad",

        "getUuid":
            "true",

        "bT":
            1,

        "clearLMBFilter":
            "undefined",

        "isFilterApplied":
            "false"
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

        "User-Agent":
            (
                "Mozilla/5.0 "
                "(Macintosh; Intel Mac OS X 10_15_7)"
            ),

        "Accept":
            "*/*",

        "Accept-Language":
            "en-US,en;q=0.9",

        "Content-Type":
            "application/json",

        "Origin":
            "https://www.redbus.in",

        "Referer":
            "https://www.redbus.in/"
    }

    print("\n========================")
    print("REQUEST")
    print("========================")

    print("\nURL:")
    print(url)

    print("\nPARAMS:")
    print(
        json.dumps(
            params,
            indent=2
        )
    )

    print("\nPAYLOAD:")
    print(
        json.dumps(
            payload,
            indent=2
        )
    )

    print("\nHEADERS:")
    print(
        json.dumps(
            headers,
            indent=2
        )
    )

    curl_command = f'''
curl "{url}" \\
-X POST \\
-H "User-Agent: {headers["User-Agent"]}" \\
-H "Content-Type: application/json" \\
-H "Origin: https://www.redbus.in" \\
-H "Referer: https://www.redbus.in/" \\
--data-raw '{json.dumps(payload)}'
'''

    print("\nCURL:")
    print(curl_command)

    try:

        response = requests.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=30
        )

        print("\n========================")
        print("RESPONSE")
        print("========================")

        print("\nSTATUS CODE:")
        print(response.status_code)

        print("\nFINAL URL:")
        print(response.url)

        print("\nRESPONSE HEADERS:")
        print(
            dict(response.headers)
        )

        print("\nRAW RESPONSE:")
        print(response.text[:10000])

        if response.status_code != 200:

            print("\nINVALID STATUS CODE")

            return []

        data = response.json()

        inventories = (
            data.get("data", {})
                .get("inventories", [])
        )

        print("\nINVENTORY COUNT:")
        print(len(inventories))

        buses = []

        for bus in inventories:

            fares = bus.get(
                "fareList",
                []
            )

            price = 0

            if fares:
                price = min(fares)

            parsed_bus = {

                "operator":
                    bus.get("travelsName"),

                "price":
                    price,

                "available_seats":
                    bus.get("availableSeats"),

                "departure":
                    bus.get("departureTime"),

                "bus_type":
                    bus.get("busType"),

                "booking_link":
                    "https://www.redbus.in/"
            }

            print("\nBUS:")
            print(
                json.dumps(
                    parsed_bus,
                    indent=2
                )
            )

            buses.append(parsed_bus)

        print("\nTOTAL BUSES:")
        print(len(buses))

        print("\n========================")
        print("SCRAPER END")
        print("========================")

        return buses

    except Exception as e:

        print("\n========================")
        print("SCRAPER ERROR")
        print("========================")

        print(str(e))

        return []
