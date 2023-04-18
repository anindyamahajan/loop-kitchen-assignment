import csv
import datetime
import sqlite3
import os


def create_database():
    """Create an SQLite database if it doesn't exist."""
    conn = sqlite3.connect('base.db')
    conn.close()


def create_reports_table():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS reports
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            report_id TEXT);''')
    conn.commit()


def load_store_poll_data():
    """Load data from CSV to store_poll_data table."""
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    # Create the store_poll_data table
    cursor.execute('''CREATE TABLE IF NOT EXISTS store_poll_data
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  store_id TEXT,
                  status TEXT,
                  timestamp_utc TIMESTAMP);''')

    # Create an index on the timestamp_utc column
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_timestamp_utc
                 ON store_poll_data (timestamp_utc);''')
    # Create an index on store_id column
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_store_id ON store_poll_data (store_id)")

    # Commit the changes and close the cursor
    conn.commit()
    cursor.close()

    # Load data from the CSV file in batches
    batch_size = 100000  # Number of rows to load in each batch
    with open('load_data/store_poll_data.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()

        rows = []
        for row in reader:
            # Extract data from the row
            store_id = row[0]
            status = row[1]
            timestamp_utc = row[2]

            # Convert the timestamp to SQLite timestamp format
            try:
                # Try parsing with decimal seconds
                dt1 = datetime.datetime.strptime(timestamp_utc, '%Y-%m-%d %H:%M:%S.%f %Z')
                timestamp_utc = dt1.strftime('%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                # If parsing with decimal seconds fails, try parsing without decimal seconds
                dt1 = datetime.datetime.strptime(timestamp_utc, '%Y-%m-%d %H:%M:%S %Z')
                timestamp_utc = dt1.strftime('%Y-%m-%d %H:%M:%S')

            # Append the row data to the list of rows
            rows.append((store_id, status, timestamp_utc))

            # Load the rows in batches
            if len(rows) >= batch_size:
                cursor.executemany('''INSERT INTO store_poll_data (store_id, status, timestamp_utc)
                                 VALUES (?, ?, ?);''', rows)
                rows = []

        # Load any remaining rows
        if len(rows) > 0:
            cursor.executemany('''INSERT INTO store_poll_data (store_id, status, timestamp_utc)
                             VALUES (?, ?, ?);''', rows)

        # Commit the changes and close the cursor
        conn.commit()
        cursor.close()

    print("Data loaded successfully into store_poll_data!")


def load_store_business_hours():
    """Load data from CSV to store_business_hours table."""
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    # Create store_business_hours table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS store_business_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id TEXT,
            day_of_week TINYINT,
            start_time_local TIMESTAMP,
            end_time_local TIMESTAMP
        )
    ''')

    # Load data from CSV
    with open('load_data/store_business_hours.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Skip header row
        next(csv_reader)
        for row in csv_reader:
            store_id = row[0]
            day_of_week = int(row[1])
            start_time_local = row[2]
            end_time_local = row[3]
            cursor.execute('''
                INSERT INTO store_business_hours (store_id, day_of_week, start_time_local, end_time_local)
                VALUES (?, ?, ?, ?)
            ''', (store_id, day_of_week, start_time_local, end_time_local))

    # Commit changes and close database connection
    conn.commit()
    conn.close()

    print("Data loaded successfully into store_business_hours!")


def load_store_timezone():
    """Load data from CSV to store_timezone table."""
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    # Create store_timezone table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS store_timezone (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id TEXT,
            timezone TEXT
        )
    ''')

    # Load data from CSV
    with open('load_data/store_timezone.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # Skip header row
        next(csv_reader)
        for row in csv_reader:
            store_id = row[0]
            timezone = row[1]
            cursor.execute('''
                INSERT INTO store_timezone (store_id, timezone)
                VALUES (?, ?)
            ''', (store_id, timezone))

    # Commit changes and close database connection
    conn.commit()
    conn.close()

    print("Data loaded successfully into store_timezone!")


# singular function to load all data
def load_all_data():
    # Load data if the base.db doesn't exist in the current folder
    if not os.path.exists('base.db'):
        create_database()
        create_reports_table()
        load_store_poll_data()
        load_store_business_hours()
        load_store_timezone()
