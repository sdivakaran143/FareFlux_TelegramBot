import requests
import json


def scrape_prices(
    source_id,
    destination_id,
    date
):

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
            (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64)"
            ),

        "Accept":
            "application/json, text/plain, */*",

        "Referer":
            "https://www.redbus.in/",

        "Origin":
            "https://www.redbus.in"
    }

    try:

        print("\\n========================")
        print("REDBUS REQUEST START")
        print("========================")

        print("\\nURL:")
        print(url)

        print("\\nPARAMS:")
        print(json.dumps(params, indent=2))

        print("\\nHEADERS:")
        print(json.dumps(headers, indent=2))

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )

        print("\\nSTATUS CODE:")
        print(response.status_code)

        print("\\nFINAL REQUEST URL:")
        print(response.url)

        print("\\nRAW RESPONSE PREVIEW:")
        print(response.text[:3000])

        print("\\n========================")
        print("REDBUS RESPONSE END")
        print("========================\\n")

        data = response.json()

        inventories = (
            data.get("data", {})
                .get("inventories", [])
        )

        print("\\nINVENTORY COUNT:")
        print(len(inventories))

        buses = []

        for bus in inventories:

            fares = bus.get("fareList", [])

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

                "route_id":
                    bus.get("routeId"),

                "service_id":
                    bus.get("serviceId"),

                "booking_link":
                    (
                        f"https://www.redbus.in/booking/"
                        f"{bus.get('routeId')}"
                    )
            }

            print("\\nPARSED BUS:")
            print(json.dumps(parsed_bus, indent=2))

            buses.append(parsed_bus)

        print("\\nTOTAL PARSED BUSES:")
        print(len(buses))

        return buses

    except Exception as e:

        print("\\n========================")
        print("SCRAPER ERROR")
        print("========================")

        print(str(e))

        return []
