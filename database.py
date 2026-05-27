
import sqlite3

conn = sqlite3.connect("monitors.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS monitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT,
    source TEXT,
    destination TEXT,
    travel_date TEXT,
    threshold INTEGER,
    frequency INTEGER,
    last_price INTEGER
)
''')

conn.commit()

def add_monitor(chat_id, source, destination, travel_date, threshold, frequency):
    cursor.execute(
        '''
        INSERT INTO monitors
        (chat_id, source, destination, travel_date, threshold, frequency, last_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (chat_id, source, destination, travel_date, threshold, frequency, 999999)
    )
    conn.commit()

def get_monitors():
    cursor.execute("SELECT * FROM monitors")
    return cursor.fetchall()

def update_price(monitor_id, price):
    cursor.execute(
        "UPDATE monitors SET last_price=? WHERE id=?",
        (price, monitor_id)
    )
    conn.commit()
