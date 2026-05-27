import sqlite3

conn = sqlite3.connect("monitors.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS monitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        operator TEXT,
        source TEXT,
        destination TEXT,
        travel_date TEXT,
        current_price INTEGER
    )
    '''
)

conn.commit()


def add_monitor(
    chat_id,
    operator,
    source,
    destination,
    travel_date,
    current_price
):

    cursor.execute(
        '''
        INSERT INTO monitors (
            chat_id,
            operator,
            source,
            destination,
            travel_date,
            current_price
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            chat_id,
            operator,
            source,
            destination,
            travel_date,
            current_price
        )
    )

    conn.commit()


def get_monitors():

    cursor.execute(
        "SELECT * FROM monitors"
    )

    return cursor.fetchall()


def update_price(monitor_id, price):

    cursor.execute(
        "UPDATE monitors SET current_price=? WHERE id=?",
        (price, monitor_id)
    )

    conn.commit()