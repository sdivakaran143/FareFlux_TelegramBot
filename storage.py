import json
import os


MONITORS_FILE = "monitors.json"


def load_monitors():

    if not os.path.exists(
        MONITORS_FILE
    ):

        return []

    try:

        with open(
            MONITORS_FILE,
            "r"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_monitors(monitors):

    with open(
        MONITORS_FILE,
        "w"
    ) as file:

        json.dump(
            monitors,
            file,
            indent=4
        )


def add_monitor(monitor):

    monitors = load_monitors()

    monitors.append(monitor)

    save_monitors(monitors)


def remove_monitor(
    monitor_name
):

    monitors = load_monitors()

    monitors = [

        monitor

        for monitor in monitors

        if (
            monitor["monitor_name"]
            != monitor_name
        )
    ]

    save_monitors(monitors)
