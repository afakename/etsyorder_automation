import pandas as pd
import os

# File paths (update these as needed)
CSV_FILE = "C:/1.Automations/EtsyOrderItems/EtsySoldOrderItems2024-12.csv"
OUTPUT_FILE = "C:/1.Automations/ProcessedOrders.csv"

# Load CSV safely
def load_orders(file_path):
    try:
        df = pd.read_csv(file_path, usecols=["Sale Date", "Item Name", "Buyer", "Quantity", "Variations"], dtype=str)
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

# Extract filename from variations
def extract_filename(row):
    variations = str(row["Variations"]).strip() if pd.notna(row["Variations"]) else ""  # Convert to string, handle NaN
    listing_title = str(row["Item Name"]).strip() if pd.notna(row["Item Name"]) else ""  # Convert to string for MS check
    
    # Default values
    name = ""
    design = ""
    year = ""

    # Extract values from variations
    for part in variations.split(","):
        key_value = part.split(":", 1)
        if len(key_value) == 2:
            key, value = key_value
            key, value = key.strip(), value.strip().lower()  # Convert value to lowercase for consistent matching

            if key == "Personalization":
                name = value.capitalize()  # Preserve capitalization for names
            elif key == "Choose the Center Piece":
                if "flake" in value:  # Match case-insensitively
                    design = "Flake"
                elif "star" in value:
                    design = "Star"
                else:
                    year = value  # If it's not Flake or Star, assume it's a Year
            elif key == "Year or No Year":
                year = value if value != "no year" else ""

    # Check if "Ms" should be included
    ms_prefix = "Ms" if "(MS)" in listing_title else ""

    # If there's no "Flake/Star" but "Choose the Center Piece" contains a year, use the year as design
    if not design and year:
        design = year
        year = ""  # Since we already used it

    # Construct filename
    filename_parts = [name, ms_prefix, design, year]
    filename = " ".join(filter(None, filename_parts))  # Remove empty values

    return filename if filename else "No Variations"



# Process orders and check for duplicates
def process_orders():
    df = load_orders(CSV_FILE)
    if df is None:
        return
    
    df["Filename"] = df.apply(extract_filename, axis=1)
    df.drop_duplicates(subset=["Filename"], keep="first", inplace=True)
    
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Processed orders saved to {OUTPUT_FILE}")

# Run the process
if __name__ == "__main__":
    process_orders()
