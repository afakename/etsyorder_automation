import requests
import os
import json
import http.server
import socketserver
import webbrowser
import secrets
import hashlib
import base64
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CONFIGURATION ===
CLIENT_ID = os.getenv("ETSY_CLIENT_ID", "1bsfw0s4klwjm2hvie9zb4cr")  # Your keystring
CLIENT_SECRET = os.getenv("ETSY_CLIENT_SECRET")  # Add this to your .env file
REDIRECT_URI = "http://localhost:8080"
TOKEN_FILE = "etsy_tokens.json"

class EtsyAPIConnector:
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
                    print("Loaded existing tokens from file")
            except Exception as e:
                print(f"Error loading tokens: {e}")

    def save_tokens(self):
        """Save tokens to file"""
        tokens = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'shop_id': self.shop_id,
            'updated_at': datetime.now().isoformat()
        }
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        print(f"Tokens saved to {TOKEN_FILE}")

    def format_price(self, price_data):
        """Convert Etsy price format to readable dollar amount"""
        if isinstance(price_data, dict):
            amount = price_data.get('amount', 0)
            divisor = price_data.get('divisor', 100)
            currency = price_data.get('currency_code', 'USD')
            return f"${amount / divisor:.2f} {currency}"
        return str(price_data)

    def generate_pkce_pair(self):
        """Generate PKCE code_verifier and code_challenge for OAuth"""
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode("utf-8")
        return code_verifier, code_challenge

    def get_auth_url(self):
        """Generate the authorization URL"""
        self.code_verifier, code_challenge = self.generate_pkce_pair()
        self.state = secrets.token_urlsafe(16)
        
        auth_url = (
            f"https://www.etsy.com/oauth/connect"
            f"?response_type=code"
            f"&client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&scope=transactions_r listings_r profile_r email_r shops_r"
            f"&state={self.state}"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
        )
        return auth_url

    def handle_oauth_callback(self):
        """Handle the OAuth callback and get authorization code"""
        auth_code = None
        
        class OAuthHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(handler_self):
                nonlocal auth_code
                try:
                    parsed_url = urlparse(handler_self.path)
                    query = parse_qs(parsed_url.query)

                    if "error" in query:
                        handler_self.send_response(400)
                        handler_self.send_header('Content-type', 'text/html')
                        handler_self.end_headers()
                        handler_self.wfile.write(b"<h2>Authorization failed.</h2>")
                        print("OAuth Error:", query.get("error_description", ["Unknown error"])[0])
                        return

                    if query.get("state", [None])[0] != self.state:
                        handler_self.send_response(400)
                        handler_self.send_header('Content-type', 'text/html')
                        handler_self.end_headers()
                        handler_self.wfile.write(b"<h2>Invalid state. Aborting for security.</h2>")
                        print("Invalid state received.")
                        return

                    code = query.get("code", [None])[0]
                    if not code:
                        handler_self.send_response(400)
                        handler_self.send_header('Content-type', 'text/html')
                        handler_self.end_headers()
                        handler_self.wfile.write(b"<h2>Authorization code missing.</h2>")
                        return

                    handler_self.send_response(200)
                    handler_self.send_header('Content-type', 'text/html')
                    handler_self.end_headers()
                    success_page = b"""
                    <html>
                    <body>
                    <h2>Authorization successful!</h2>
                    <p>You can close this window and return to your terminal.</p>
                    <script>setTimeout(function(){ window.close(); }, 3000);</script>
                    </body>
                    </html>
                    """
                    handler_self.wfile.write(success_page)
                    print(f"\nAuthorization code received successfully!")
                    auth_code = code
                    
                except Exception as e:
                    print(f"Error in OAuth handler: {e}")

            def log_message(self, format, *args):
                # Suppress default server logs
                pass

        print("Opening Etsy authorization in your browser...")
        auth_url = self.get_auth_url()
        print(f"If browser doesn't open, go to: {auth_url}")
        webbrowser.open(auth_url)
        
        try:
            with socketserver.TCPServer(("localhost", 8080), OAuthHandler) as httpd:
                print("Waiting for authorization... Complete the login in your browser.")
                httpd.timeout = 30  # 30 second timeout
                httpd.handle_request()
                return auth_code
        except Exception as e:
            print(f"Server error: {e}")
            print("\nManual fallback - please copy the authorization code from your browser URL")
            print("The URL should look like: localhost:8080/?code=LONG_CODE_HERE&state=...")
            print("Copy just the code part (everything after 'code=' and before '&'):")
            return input("Enter authorization code: ").strip()

    def exchange_code_for_tokens(self, auth_code):
        """Exchange authorization code for access token"""
        token_url = "https://api.etsy.com/v3/public/oauth/token"
        
        data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": auth_code,
            "code_verifier": self.code_verifier
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        print("Exchanging authorization code for access token...")
        response = requests.post(token_url, data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token')
            print("Access token obtained successfully!")
            self.save_tokens()
            return True
        else:
            print(f"Token exchange failed: {response.status_code}")
            print(response.text)
            return False

    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            print("No refresh token available. Need to re-authenticate.")
            return False
            
        token_url = "https://api.etsy.com/v3/public/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": self.refresh_token
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.save_tokens()
            print("Access token refreshed successfully!")
            return True
        else:
            print(f"Token refresh failed: {response.status_code}")
            return False

    def get_shop_info(self):
        """Get shop information to find your shop ID"""
        if not self.access_token:
            print("No access token. Please authenticate first.")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": CLIENT_ID
        }
        
        # Get user info first
        user_url = "https://api.etsy.com/v3/application/users/me"
        response = requests.get(user_url, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data['user_id']
            print(f"User ID: {user_id}")
            
            # Get shops for this user
            shops_url = f"https://api.etsy.com/v3/application/users/{user_id}/shops"
            response = requests.get(shops_url, headers=headers)
            
            if response.status_code == 200:
                shops_data = response.json()
                print(f"Shops API response: {shops_data}")  # Debug line
                
                # Handle different response formats
                shops = shops_data.get('results', [])
                if not shops and 'shop_id' in shops_data:
                    # Sometimes the response is direct shop info
                    shops = [shops_data]
                
                if shops:
                    shop = shops[0]  # Get first shop
                    self.shop_id = shop['shop_id']
                    print(f"Shop ID: {self.shop_id}")
                    print(f"Shop Name: {shop.get('shop_name', 'Unknown')}")
                    self.save_tokens()
                    return shop
                else:
                    print("No shops found for this user")
                    print(f"Raw response: {shops_data}")
            else:
                print(f"Failed to get shops: {response.status_code}")
                print(response.text)
        else:
            print(f"Failed to get user info: {response.status_code}")
            print(response.text)
        
        return None

    def authenticate(self):
        """Complete authentication flow"""
        if not CLIENT_SECRET:
            print("ERROR: ETSY_CLIENT_SECRET not found in environment variables!")
            print("Please add ETSY_CLIENT_SECRET to your .env file")
            return False
            
        auth_code = self.handle_oauth_callback()
        if auth_code:
            if self.exchange_code_for_tokens(auth_code):
                self.get_shop_info()
                return True
        return False

    def test_connection(self):
        """Test the API connection"""
        if not self.access_token:
            print("Not authenticated. Please run authenticate() first.")
            return False
            
        # If we have a token but no shop_id, try to get it
        if not self.shop_id:
            print("No shop ID found. Attempting to retrieve...")
            if not self.get_shop_info():
                print("Failed to get shop information.")
                return False
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": CLIENT_ID
        }
        
        # Test with a simple shop info request
        url = f"https://api.etsy.com/v3/application/shops/{self.shop_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            shop_data = response.json()
            print(f"Connection successful!")
            print(f"Shop: {shop_data['shop_name']}")
            print(f"Shop ID: {shop_data['shop_id']}")
            return True
        elif response.status_code == 401:
            print("Token expired, trying to refresh...")
            if self.refresh_access_token():
                return self.test_connection()  # Try again with new token
            else:
                print("Token refresh failed. Please re-authenticate.")
                return False
        else:
            print(f"Connection test failed: {response.status_code}")
            print(response.text)
            return False

    def get_recent_orders(self, days_back=7, limit=25):
        """Get recent orders from your shop"""
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
            'includes': 'transactions'
        }
        
        print(f"Fetching orders from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # DEBUG: Print all fields from first order
            if data.get('results'):
                print("\n" + "="*60)
                print("ETSY ORDER FIELDS (First Order):")
                print("="*60)
                sample = data['results'][0]
                for key in sorted(sample.keys()):
                    value = sample[key]
                    # Truncate long values for readability
                    if isinstance(value, (list, dict)):
                        if len(str(value)) > 100:
                            print(f"{key}: [truncated - type: {type(value).__name__}]")
                        else:
                            print(f"{key}: {value}")
                    else:
                        print(f"{key}: {value}")
                print("="*60 + "\n")
            
            print(f"Found {len(data['results'])} orders")
            return data['results']
        else:
            print(f"Failed to get orders: {response.status_code}")
            print(response.text)
            return None

    def get_filtered_orders(self, 
                          days_back=7, 
                          limit=100,
                          min_amount=None, 
                          max_amount=None,
                          customer_email=None,
                          buyer_user_id=None,
                          product_title_contains=None,
                          was_paid=None,
                          was_shipped=None):
        """Get orders with specific filters"""
        
        orders = self.get_recent_orders(days_back=days_back, limit=limit)
        if not orders:
            return []
        
        filtered_orders = []
        
        for order in orders:
            # Convert price to float for comparison
            order_total = order['grandtotal']['amount'] / order['grandtotal']['divisor']
            
            # Apply filters
            if min_amount and order_total < min_amount:
                continue
            if max_amount and order_total > max_amount:
                continue
            if customer_email and order.get('buyer_email', '').lower() != customer_email.lower():
                continue
            if buyer_user_id and order.get('buyer_user_id') != buyer_user_id:
                continue
            if was_paid is not None and order.get('was_paid') != was_paid:
                continue
            if was_shipped is not None and order.get('was_shipped') != was_shipped:
                continue
            
            # Check product titles if specified
            if product_title_contains:
                found_product = False
                if 'Transactions' in order:
                    for transaction in order['Transactions']:
                        if product_title_contains.lower() in transaction.get('title', '').lower():
                            found_product = True
                            break
                if not found_product:
                    continue
            
            filtered_orders.append(order)
        
        print(f"Filtered to {len(filtered_orders)} orders matching criteria")
        return filtered_orders

    def extract_order_data(self, orders, fields=None):
        """Extract specific fields from orders into a clean format"""
        if fields is None:
            # Default fields to extract
            fields = [
                'receipt_id', 'buyer_user_id', 'buyer_email', 'name', 
                'first_line', 'city', 'state', 'zip', 'country_iso',
                'grandtotal', 'created_timestamp', 'was_paid', 'was_shipped',
                'items'  # Special field for transaction items
            ]
        
        extracted_data = []
        
        for order in orders:
            order_data = {}
            
            for field in fields:
                if field == 'items':
                    # Extract item information
                    items = []
                    if 'Transactions' in order:
                        for transaction in order['Transactions']:
                            items.append({
                                'title': transaction.get('title', ''),
                                'quantity': transaction.get('quantity', 1),
                                'price': self.format_price(transaction.get('price', {})),
                                'listing_id': transaction.get('listing_id'),
                                'product_id': transaction.get('product_id'),
                                'sku': transaction.get('sku', ''),
                                'variations': transaction.get('variations', [])
                            })
                    order_data['items'] = items
                elif field == 'grandtotal':
                    order_data[field] = self.format_price(order.get(field, {}))
                elif field == 'created_timestamp':
                    timestamp = order.get(field)
                    if timestamp:
                        order_data['order_date'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        order_data['created_timestamp'] = timestamp
                    else:
                        order_data['order_date'] = None
                        order_data['created_timestamp'] = None
                else:
                    order_data[field] = order.get(field, None)
            
            extracted_data.append(order_data)
        
        return extracted_data

    def get_orders_by_customer(self, buyer_user_id):
        """Get all orders from a specific customer"""
        return self.get_filtered_orders(
            days_back=365,  # Look back a full year
            limit=100,
            buyer_user_id=buyer_user_id
        )

    def get_high_value_orders(self, min_amount=50.00, days_back=30):
        """Get orders above a certain dollar amount"""
        return self.get_filtered_orders(
            days_back=days_back,
            min_amount=min_amount,
            limit=100
        )

    def get_orders_with_product(self, product_name_contains, days_back=90):
        """Get orders containing specific products"""
        return self.get_filtered_orders(
            days_back=days_back,
            product_title_contains=product_name_contains,
            limit=100
        )

    def get_unpaid_orders(self, days_back=14):
        """Get orders that haven't been paid yet"""
        return self.get_filtered_orders(
            days_back=days_back,
            was_paid=False,
            limit=100
        )

    def get_unshipped_orders(self, days_back=30):
        """Get paid orders that haven't been shipped"""
        return self.get_filtered_orders(
            days_back=days_back,
            was_paid=True,
            was_shipped=False,
            limit=100
        )
    
    def get_open_orders(self, days_back=90, limit=250):
        """Get orders that are not yet complete (status != Complete)"""
        orders = self.get_recent_orders(days_back=days_back, limit=limit)
        if not orders:
            return []
        
        open_orders = []
        for order in orders:
            # Filter for orders that are NOT complete
            # Status will be "Paid", "Processing", etc. for open orders
            # and "Complete" or "Completed" for finished orders
            order_status = order.get('status', '').lower()
            if order_status != 'complete' and order_status != 'completed':
                open_orders.append(order)
        
        print(f"Filtered to {len(open_orders)} open orders (status != Complete)")
        return open_orders

    def get_order_details(self, receipt_id):
        """Get detailed information about a specific order"""
        if not self.test_connection():
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": CLIENT_ID
        }
        
        url = f"https://api.etsy.com/v3/application/shops/{self.shop_id}/receipts/{receipt_id}"
        params = {
            'includes': 'Transactions'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get order {receipt_id}: {response.status_code}")
            return None

    def get_listings(self, state='active', limit=25):
        """Get shop listings"""
        if not self.test_connection():
            return None
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "x-api-key": CLIENT_ID
        }
        
        url = f"https://api.etsy.com/v3/application/shops/{self.shop_id}/listings"
        params = {
            'state': state,
            'limit': limit
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['results'])} {state} listings")
            return data['results']
        else:
            print(f"Failed to get listings: {response.status_code}")
            print(response.text)
            return None

# === USAGE FUNCTIONS ===
def main():
    """Main function to test the connection"""
    etsy = EtsyAPIConnector()
    
    # Check if we have tokens
    if not etsy.access_token:
        print("No existing tokens found. Starting authentication...")
        if not etsy.authenticate():
            print("Authentication failed!")
            return
    
    # Test connection
    if etsy.test_connection():
        print("\n" + "="*50)
        print("Etsy API connection is working!")
        print("="*50)
        
        # Example 1: Get high-value orders (over $30)
        print("\nHIGH-VALUE ORDERS (>$30):")
        high_value_orders = etsy.get_high_value_orders(min_amount=30.00, days_back=30)
        if high_value_orders:
            clean_data = etsy.extract_order_data(high_value_orders, 
                fields=['receipt_id', 'name', 'grandtotal', 'order_date', 'buyer_email', 'items'])
            
            for order in clean_data[:3]:  # Show first 3
                print(f"Order: {order['receipt_id']} | Customer: {order['name']} | Total: {order['grandtotal']}")
                print(f"  Email: {order['buyer_email']} | Date: {order['order_date']}")
                for item in order['items'][:2]:  # Show first 2 items
                    print(f"  - {item['title']} (Qty: {item['quantity']}) - {item['price']}")
                print()
        
        # Example 2: Get orders from specific customer
        print("\nORDERS FROM SPECIFIC CUSTOMER:")
        customer_orders = etsy.get_orders_by_customer(buyer_user_id=65944010)  # From your sample data
        if customer_orders:
            print(f"Found {len(customer_orders)} orders from this customer")
            
        # Example 3: Get unshipped orders (needs attention)
        print("\nUNSHIPPED ORDERS (Need Action):")
        unshipped = etsy.get_unshipped_orders(days_back=14)
        if unshipped:
            urgent_data = etsy.extract_order_data(unshipped, 
                fields=['receipt_id', 'name', 'city', 'state', 'grandtotal', 'order_date'])
            
            for order in urgent_data:
                print(f"Order {order['receipt_id']} - {order['name']} ({order['city']}, {order['state']}) - {order['grandtotal']}")
        
        print("\n" + "="*50)
        print("AVAILABLE FILTERING METHODS:")
        print("- etsy.get_high_value_orders(min_amount=50.00)")
        print("- etsy.get_orders_by_customer(buyer_user_id=12345)")  
        print("- etsy.get_orders_with_product('mug')")
        print("- etsy.get_unpaid_orders()")
        print("- etsy.get_unshipped_orders()")
        print("- etsy.get_filtered_orders(min_amount=20, was_shipped=False)")
        print("\nCUSTOM DATA EXTRACTION:")
        print("- etsy.extract_order_data(orders, fields=['receipt_id', 'name', 'buyer_email'])")
    else:
        print("Connection failed!")

if __name__ == "__main__":
    main()