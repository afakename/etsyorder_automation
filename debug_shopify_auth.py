# debug_shopify_auth.py
"""
Debug script to test Shopify authentication
"""
import requests
from config import Config
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    shop_url = Config.SHOPIFY_SHOP_URL
    access_token = Config.SHOPIFY_ACCESS_TOKEN
    
    print("="*60)
    print("SHOPIFY AUTHENTICATION DEBUG")
    print("="*60)
    print(f"Shop URL: {shop_url}")
    print(f"Token (first 20 chars): {access_token[:20] if access_token else 'NOT SET'}...")
    print()
    
    # Test 1: Try shop endpoint (basic auth test)
    print("TEST 1: Basic Shop Info (tests authentication)")
    print("-"*60)
    
    url = f"https://{shop_url}/admin/api/2024-10/shop.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Authentication successful!")
            shop_data = response.json().get('shop', {})
            print(f"  Shop Name: {shop_data.get('name')}")
            print(f"  Shop Owner: {shop_data.get('shop_owner')}")
            print(f"  Email: {shop_data.get('email')}")
            print(f"  Domain: {shop_data.get('domain')}")
        elif response.status_code == 401:
            print("✗ Authentication failed - Invalid access token")
            print("  → Check your SHOPIFY_ACCESS_TOKEN in .env")
        elif response.status_code == 404:
            print("✗ 404 Not Found - Wrong shop URL or API not enabled")
            print("  → Check your SHOPIFY_SHOP_URL in .env")
        else:
            print(f"✗ Unexpected error: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Connection error: {e}")
    
    print()
    
    # Test 2: Try orders endpoint with simple query
    print("TEST 2: Orders Endpoint (minimal query)")
    print("-"*60)
    
    url = f"https://{shop_url}/admin/api/2024-10/orders.json"
    params = {"limit": 1}  # Just get 1 order
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            orders = response.json().get('orders', [])
            print(f"✓ Orders endpoint accessible!")
            print(f"  Orders returned: {len(orders)}")
            if orders:
                print(f"  Sample order ID: {orders[0].get('id')}")
        elif response.status_code == 401:
            print("✗ Authentication failed")
        elif response.status_code == 403:
            print("✗ Forbidden - App doesn't have read_orders permission")
            print("  → Check API scopes in your custom app")
        elif response.status_code == 404:
            print("✗ 404 Not Found")
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"✗ Connection error: {e}")
    
    print()
    
    # Test 3: List all available API versions
    print("TEST 3: Check API Access")
    print("-"*60)
    
    # Try without version (gets latest)
    url = f"https://{shop_url}/admin/api/shop.json"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Default API Status: {response.status_code}")
        if response.status_code == 200:
            print("✓ API access working")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    print("="*60)
    print("RECOMMENDATIONS:")
    print("="*60)
    
    if access_token and access_token.startswith('shpat_'):
        print("✓ Token format looks correct (starts with shpat_)")
    else:
        print("✗ Token may be invalid - should start with 'shpat_'")
        print("  → Get a new token from your custom app")
    
    print("\nIf tests failed, try these steps:")
    print("1. Go to Shopify Admin → Settings → Apps and sales channels")
    print("2. Click 'Develop apps' → Your app name")
    print("3. Click 'API credentials' tab")
    print("4. In 'Access tokens' section, click 'Install app' (or reinstall)")
    print("5. Copy the NEW Admin API access token")
    print("6. Update SHOPIFY_ACCESS_TOKEN in your .env file")
    print("7. Run this test again")

if __name__ == "__main__":
    test_connection()