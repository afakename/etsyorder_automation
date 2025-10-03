import requests
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pprint

# Load environment variables
load_dotenv()

# === CONFIGURATION ===
CLIENT_ID = os.getenv("ETSY_CLIENT_ID", "1bsfw0s4klwjm2hvie9zb4cr")
CLIENT_SECRET = os.getenv("ETSY_CLIENT_SECRET")
TOKEN_FILE = "etsy_tokens.json"

class EtsyDataExplorer:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.shop_id = None
        self.load_tokens()

    def load_tokens(self):
        """Load tokens from file if they exist"""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, 'r') as f:
                    tokens = json.load(f)
                    self.access_token = tokens.get('access_token')
                    self.refresh_token = tokens.get('refresh_token')
                    self.shop_id = tokens.get('shop_id')
                    print("✅ Loaded existing tokens from file")
            except Exception as e:
                print(f"❌ Error loading tokens: {e}")

    def test_connection(self):
        """Quick connection test"""
        if not self.access_token or not self.shop_id:
            print("❌ Missing access token or shop ID")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": CLIENT_ID
        }
        
        url = f"https://api.etsy.com/v3/application/shops/{self.shop_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return False

    def get_raw_order_data(self, days_back=30, limit=5):
        """Get raw order data to explore structure"""
        if not self.test_connection():
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": CLIENT_ID
        }
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        url = f"https://api.etsy.com/v3/application/shops/{self.shop_id}/receipts"
        params = {
            'limit': limit,
            'min_created': int(start_date.timestamp()),
            'max_created': int(end_date.timestamp()),
            'includes': 'Transactions'
        }
        
        print(f"🔍 Fetching {limit} orders from last {days_back} days...")
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['results'])} orders")
            return data['results']
        else:
            print(f"❌ Failed to get orders: {response.status_code}")
            print(response.text)
            return None

    def explore_order_structure(self, orders):
        """Analyze the structure of order data"""
        if not orders:
            print("❌ No orders to analyze")
            return
            
        print("\n" + "="*60)
        print("📊 ORDER DATA STRUCTURE ANALYSIS")
        print("="*60)
        
        # Look at first order
        first_order = orders[0]
        
        print("\n🔍 TOP-LEVEL ORDER FIELDS:")
        print("-" * 30)
        for key, value in first_order.items():
            if key != 'Transactions':  # We'll handle transactions separately
                value_type = type(value).__name__
                if isinstance(value, str) and len(value) > 50:
                    preview = value[:50] + "..."
                else:
                    preview = value
                print(f"{key:20} | {value_type:10} | {preview}")
        
        # Analyze transactions (the items in the order)
        if 'Transactions' in first_order:
            print("\n🛍️ TRANSACTION (ITEM) STRUCTURE:")
            print("-" * 40)
            
            for i, transaction in enumerate(first_order['Transactions']):
                print(f"\n--- ITEM #{i+1} ---")
                for key, value in transaction.items():
                    value_type = type(value).__name__
                    if isinstance(value, str) and len(value) > 50:
                        preview = value[:50] + "..."
                    else:
                        preview = value
                    print(f"{key:25} | {value_type:10} | {preview}")

    def deep_dive_variations(self, orders):
        """Focus specifically on variation and personalization data"""
        if not orders:
            return
            
        print("\n" + "="*60)
        print("🎨 VARIATION & PERSONALIZATION DEEP DIVE")
        print("="*60)
        
        for order_idx, order in enumerate(orders):
            if 'Transactions' not in order:
                continue
                
            print(f"\n📦 ORDER #{order['receipt_id']} - Customer: {order.get('name', 'Unknown')}")
            print("-" * 50)
            
            for item_idx, transaction in enumerate(order['Transactions']):
                print(f"\n  🛍️ ITEM #{item_idx + 1}: {transaction.get('title', 'No title')}")
                
                # Look for variations
                if 'variations' in transaction:
                    print("    🎯 VARIATIONS:")
                    variations = transaction['variations']
                    if isinstance(variations, list):
                        for var in variations:
                            print(f"      - {var}")
                    else:
                        print(f"      - {variations}")
                else:
                    print("    ❌ No 'variations' field found")
                
                # Look for personalization - check multiple possible fields
                personalization_fields = [
                    'personalization_value', 'personalization', 'custom_personalization',
                    'buyer_personalization', 'personalized_value', 'custom_text'
                ]
                
                print("    📝 PERSONALIZATION SEARCH:")
                found_personalization = False
                for field in personalization_fields:
                    if field in transaction and transaction[field]:
                        print(f"      ✅ {field}: '{transaction[field]}'")
                        found_personalization = True
                
                if not found_personalization:
                    print("      ❌ No personalization fields found in expected locations")
                    
                # Show ALL fields for this transaction to help us find hidden data
                print("    🔍 ALL TRANSACTION FIELDS:")
                for key, value in transaction.items():
                    if key not in ['title', 'variations']:  # Already showed these
                        if isinstance(value, str) and len(value) > 40:
                            preview = value[:40] + "..."
                        else:
                            preview = value
                        print(f"      {key}: {preview}")

    def save_sample_data(self, orders, filename="sample_order_data.json"):
        """Save raw order data to file for further analysis"""
        if orders:
            with open(filename, 'w') as f:
                json.dump(orders, f, indent=2)
            print(f"\n💾 Raw data saved to {filename}")

def main():
    """Main exploration function"""
    explorer = EtsyDataExplorer()
    
    if not explorer.access_token:
        print("❌ No tokens found. Run the main connector script first to authenticate.")
        return
    
    print("🚀 Starting Etsy API Data Exploration")
    print("="*50)
    
    # Get raw order data
    raw_orders = explorer.get_raw_order_data(days_back=60, limit=3)  # Get 3 recent orders
    
    if raw_orders:
        # Analyze overall structure
        explorer.explore_order_structure(raw_orders)
        
        # Deep dive into variations and personalization
        explorer.deep_dive_variations(raw_orders)
        
        # Save data for manual inspection
        explorer.save_sample_data(raw_orders)
        
        print("\n" + "="*60)
        print("✅ EXPLORATION COMPLETE!")
        print("="*60)
        print("📋 Next steps:")
        print("1. Review the output above to understand data structure")
        print("2. Check 'sample_order_data.json' for raw data")
        print("3. Identify where personalization and variations are stored")
        print("4. Plan the extraction methods based on findings")
        
    else:
        print("❌ No order data retrieved. Check your API connection.")

if __name__ == "__main__":
    main()