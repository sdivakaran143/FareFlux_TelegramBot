import requests


def search_place(query):

    url = "https://nominatim.openstreetmap.org/search"

    headers = {
        "User-Agent": "farepilot"
    }

    params = {
        "q": query,
        "format": "json",
        "limit": 5
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=20
    )

    return response.json()