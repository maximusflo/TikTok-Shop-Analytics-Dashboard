import sqlite3

def get_conection():
    return sqlite3.connect('data.db')

def initialize_database(connection):
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_stats (
        date TEXT PRIMARY KEY,
        commission REAL NOT NULL,
        gmv REAL NOT NULL,
        items_sold INTEGER NOT NULL,
        videos INTEGER NOT NULL,
        views INTEGER NOT NULL
    )
    ''')
    connection.commit()