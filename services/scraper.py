
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
            50,

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

    headers = {

        "User-Agent":
            "Mozilla/5.0",

        "Accept":
            "application/json",

        "Referer":
            "https://www.redbus.in/"
    }

    print("\nREQUEST URL:")
    print(url)

    print("\nREQUEST PARAMS:")
    print(json.dumps(params, indent=2))

    print("\nREQUEST HEADERS:")
    print(json.dumps(headers, indent=2))

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )

        print("\nSTATUS CODE:")
        print(response.status_code)

        print("\nFINAL URL:")
        print(response.url)

        print("\nRAW RESPONSE:")
        print(response.text[:5000])

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

                "booking_link":
                    "https://www.redbus.in/"
            }

            print("\nBUS FOUND:")
            print(json.dumps(parsed_bus, indent=2))

            buses.append(parsed_bus)

        print("\nTOTAL BUSES:")
        print(len(buses))

        print("\n========================")
        print("SCRAPER END")
        print("========================\n")

        return buses

    except Exception as e:

        print("\n========================")
        print("SCRAPER ERROR")
        print("========================")

        print(str(e))

        return []
