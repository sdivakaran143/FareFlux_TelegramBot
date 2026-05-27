
import requests

def search_place(query):

    url = "https://nominatim.openstreetmap.org/search"

    headers = {
        "User-Agent": "bus-fare-notifier"
    }

    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    data = response.json()

    if not data:
        return None

    return data[0]["display_name"]
