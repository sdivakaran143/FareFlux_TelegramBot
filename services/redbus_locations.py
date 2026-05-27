import requests


def search_redbus_locations(query):

    url = (
        "https://www.redbus.in/rbapi/autocomplete/v1/places"
    )

    params = {
        "query": query
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Origin": "https://www.redbus.in",
        "Referer": "https://www.redbus.in/"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=30
    )

    if response.status_code != 200:
        return []

    data = response.json()

    results = []

    places = data.get("data", [])

    for item in places:

        results.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "city_name": item.get("cityName"),
            "state_name": item.get("stateName"),
            "type": item.get("type")
        })

    return results