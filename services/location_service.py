
import requests

def search_place(query):

    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": 5
        },
        headers={
            "User-Agent": "fareflux"
        },
        timeout=20
    )

    data = response.json()

    results = []

    for item in data:

        address = item.get("address", {})

        name = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or item.get("display_name", "").split(",")[0]
        )

        results.append({
            "name": name
        })

    return results
