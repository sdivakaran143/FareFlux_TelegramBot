
import sqlite3

conn = sqlite3.connect("monitors.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS monitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT,
    monitor_name TEXT,
    operator TEXT,
    source TEXT,
    destination TEXT,
    travel_date TEXT,
    current_price INTEGER,
    booking_link TEXT,
    source_id INTEGER,
    destination_id INTEGER
)
''')

conn.commit()


def add_monitor(
    chat_id,
    monitor_name,
    operator,
    source,
    destination,
    travel_date,
    current_price,
    booking_link,
    source_id,
    destination_id
):

    cursor.execute(
        '''
        INSERT INTO monitors (
            chat_id,
            monitor_name,
            operator,
            source,
            destination,
            travel_date,
            current_price,
            booking_link,
            source_id,
            destination_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            chat_id,
            monitor_name,
            operator,
            source,
            destination,
            travel_date,
            current_price,
            booking_link,
            source_id,
            destination_id
        )
    )

    conn.commit()


def get_monitors(chat_id):

    cursor.execute(
        "SELECT * FROM monitors WHERE chat_id=?",
        (chat_id,)
    )

    return cursor.fetchall()


def get_all_monitors():

    cursor.execute("SELECT * FROM monitors")

    return cursor.fetchall()


def update_price(monitor_id, price):

    cursor.execute(
        "UPDATE monitors SET current_price=? WHERE id=?",
        (price, monitor_id)
    )

    conn.commit()


def delete_monitor(monitor_id):

    cursor.execute(
        "DELETE FROM monitors WHERE id=?",
        (monitor_id,)
    )

    conn.commit()
