import requests

def search_place(query):
    response = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": query, "format": "json", "limit": 5},
        headers={"User-Agent": "fareflux"},
        timeout=20
    )
    return response.json()
