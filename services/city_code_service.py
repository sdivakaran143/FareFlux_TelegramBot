
import json

FILE_PATH = "data/city_codes.json"


def load_city_codes():

    with open(FILE_PATH, "r") as file:
        return json.load(file)


def find_city_code(city_name):

    data = load_city_codes()

    return data.get(city_name.lower())


def save_city_code(city_name, city_code):

    data = load_city_codes()

    data[city_name.lower()] = int(city_code)

    with open(FILE_PATH, "w") as file:

        json.dump(
            data,
            file,
            indent=2
        )
