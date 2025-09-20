import requests
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("211518821.c2XsJUUB_bzR2K0lR1QFBRCA4mY68ZIuCQ7As1slABGssnFZEm0uFTb9vmmwuNmUnEDPFChUHhR6ZSYpLLPaRZnht3")  # <-- Replace with your Etsy Access Token
CLIENT_ID = "1bsfw0s4klwjm2hvie9zb4cr"  # <-- your Etsy Keystring

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "x-api-key": CLIENT_ID
}

def get_shop_id():
    url = "https://api.etsy.com/v3/application/shop"
    response = requests.get(url, headers=headers)

    print("Status Code:", response.status_code)
    print("Response:")
    print(response.json())

if __name__ == "__main__":
    get_shop_id()
