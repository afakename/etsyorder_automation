import sqlite3  # Import SQLite module

# Connect to SQLite database (creates file if it doesn't exist)
conn = sqlite3.connect("etsy_orders.db")

# Create a cursor to interact with the database
cursor = conn.cursor()

# Create a table for storing orders if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_name TEXT,
        formatted_name TEXT,
        formatted_value TEXT,
        created_at TEXT
    )
''')

# Save changes and close the connection
conn.commit()
conn.close()

print("Database setup complete.")
