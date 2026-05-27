import requests

def search_place(query):

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": query,
        "format": "json",
        "limit": 5
    }

    headers = {
        "User-Agent": "farepilot"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers
    )

    return response.json()
