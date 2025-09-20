import pandas as pd
import os
import sqlite3
import glob

# === Paths ===
CSV_FOLDER = "C:/1.Automations/EtsyOrderItems"
CSV_FILE = max(glob.glob(os.path.join(CSV_FOLDER, "*.csv")), key=os.path.getctime)
from datetime import datetime
today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE = f"C:/1.Automations/ProcessedOrders_{today}.csv"
DB_FILE = "C:/1.Automations/etsy_orders.db"

# === Load CSV ===
def load_orders(file_path):
    try:
        return pd.read_csv(file_path, usecols=["Sale Date", "Item Name", "Buyer", "Quantity", "Variations", "Order ID"], dtype=str)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

# === Extract Filename Logic ===
def extract_filename(row):
    variations = str(row["Variations"]).strip() if pd.notna(row["Variations"]) else ""
    listing_title = str(row["Item Name"]).strip() if pd.notna(row["Item Name"]) else ""
    
    name = ""
    design = ""
    year = ""

    for part in variations.split(","):
        key_value = part.split(":", 1)
        if len(key_value) == 2:
            key, value = key_value
            key, value = key.strip(), value.strip().lower()
            if key == "Personalization":
                name = value.capitalize()
            elif key == "Choose the Center Piece":
                if "flake" in value:
                    design = "Flake"
                elif "star" in value:
                    design = "Star"
                else:
                    year = value
            elif key == "Year or No Year":
                year = value if value != "no year" else ""

    ms_prefix = "Ms" if "(MS)" in listing_title else ""
    if not design and year:
        design = year
        year = ""

    filename_parts = [name, ms_prefix, design, year]
    return " ".join(filter(None, filename_parts)) or "No Variations"

# === Setup DB ===
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS processed_orders (
            order_id TEXT PRIMARY KEY,
            filename TEXT,
            processed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn, c

# === Process Orders ===
def process_orders():
    df = load_orders(CSV_FILE)
    if df is None:
        return

    conn, c = init_db()

    new_rows = []
    for _, row in df.iterrows():
        order_id = row["Order ID"]
        c.execute("SELECT 1 FROM processed_orders WHERE order_id = ?", (order_id,))
        if c.fetchone():
            continue  # Skip already processed orders

        filename = extract_filename(row)
        row["Filename"] = filename
        new_rows.append(row)
        c.execute("INSERT OR IGNORE INTO processed_orders (order_id, filename) VALUES (?, ?)", (order_id, filename))

    conn.commit()
    conn.close()

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        new_df.to_csv(OUTPUT_FILE, index=False)
        print(f"{len(new_rows)} new orders processed and saved to {OUTPUT_FILE}")
    else:
        print("No new orders found. All are already processed.")

# === Run ===
if __name__ == "__main__":
    process_orders()
