
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def generate_travel_date(selection):

    current_time = datetime.now(IST)

    print("\nCURRENT IST TIME:")
    print(current_time)

    if selection == "today":
        travel_date = current_time
    else:
        travel_date = current_time + timedelta(days=1)

    formatted_date = (
        travel_date.strftime("%d-%b-%Y")
    )

    print("\nGENERATED DOJ:")
    print(formatted_date)

    return formatted_date
