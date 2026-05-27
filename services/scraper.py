import requests

def scrape_prices(source_id, destination_id, date):

    url = "https://www.redbus.in/rpw/api/searchResults"

    params = {
        "fromCity": source_id,
        "toCity": destination_id,
        "DOJ": date,
        "limit": 50,
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

    response = requests.get(url, params=params)

    print("REQUEST:", response.url)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text[:1000])

    return []
