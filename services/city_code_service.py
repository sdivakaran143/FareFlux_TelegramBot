import json
import os

CITY_FILE = "data/city_codes.json"


def load_city_codes():

    if not os.path.exists(CITY_FILE):
        return {}

    with open(CITY_FILE, "r") as file:
        return json.load(file)


def save_city_code(city_name, city_id):

    data = load_city_codes()

    data[city_name.lower()] = int(city_id)

    with open(CITY_FILE, "w") as file:

        json.dump(
            data,
            file,
            indent=2
        )


def find_city_code(city_name):

    data = load_city_codes()

    return data.get(city_name.lower())