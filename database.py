
import sqlite3

conn = sqlite3.connect("monitors.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS monitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        monitor_name TEXT,
        operator TEXT,
        source TEXT,
        destination TEXT,
        travel_date TEXT,
        current_price INTEGER,
        booking_link TEXT
    )
    '''
)

conn.commit()

def add_monitor(
    chat_id,
    monitor_name,
    operator,
    source,
    destination,
    travel_date,
    current_price,
    booking_link
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
            booking_link
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            chat_id,
            monitor_name,
            operator,
            source,
            destination,
            travel_date,
            current_price,
            booking_link
        )
    )

    conn.commit()

def get_monitors(chat_id):

    cursor.execute(
        "SELECT * FROM monitors WHERE chat_id=?",
        (chat_id,)
    )

    return cursor.fetchall()

def delete_monitor(monitor_id):

    cursor.execute(
        "DELETE FROM monitors WHERE id=?",
        (monitor_id,)
    )

    conn.commit()
