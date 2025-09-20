import os
import sqlite3
import re

# Path to the folder containing PNG files
FOLDER_PATH = "C:\\Snowflakes\\2024 snowflakes"  # <-- UPDATE THIS

# Connect to SQLite database (or create it)
conn = sqlite3.connect("etsy_orders.db")
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT UNIQUE,
        name TEXT,
        variation TEXT,
        year TEXT
    )
''')
conn.commit()

# Function to extract name, variation, and year
def parse_filename(filename):
    filename = filename.lower().replace(".png", "")  # Remove .png extension
    match = re.match(r"(.+?)\s*(\d{4}|star|flk|flake|ms star|ms flk)?\s*(\d{4})?", filename)
    
    if match:
        name = match.group(1).strip() if match.group(1) else None
        variation = match.group(2).strip() if match.group(2) else None
        year = match.group(3).strip() if match.group(3) else None
        return name, variation, year
    return None, None, None

# Scan folder and store filenames in database
for file in os.listdir(FOLDER_PATH):
    if file.lower().endswith(".png"):
        name, variation, year = parse_filename(file)

        try:
            cursor.execute("INSERT INTO files (filename, name, variation, year) VALUES (?, ?, ?, ?)", 
                           (file, name, variation, year))
            print(f"Stored: {file}")
        except sqlite3.IntegrityError:
            print(f"Skipped (already exists): {file}")

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Total files scanned: {scanned_count}")
print(f"Total files stored: {stored_count}")
print(f"Database updated successfully!")
