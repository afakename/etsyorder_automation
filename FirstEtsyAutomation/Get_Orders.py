import requests
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("11518821.Y1BCcq1sIK5zRhz4lQb5d8KX7scis12m_EE9qgdL1THLCjT07iRh8cuC9GGdd2gkoG2U3ogQiATfjWnhCd3Fmy7kzs")
CLIENT_ID = "1bsfw0s4klwjm2hvie9zb4cr"  # <-- Replace with your Etsy Keystring
SHOP_ID = "hoveydesignshop"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "x-api-key": CLIENT_ID
}

def get_recent_orders():
    url = f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/shop-transactions?limit=10&sort_on=created&sort_order=desc&includes=MainImage,Listings,Variations"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        for order in data.get("results", []):
            print(order)
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    get_recent_orders()
