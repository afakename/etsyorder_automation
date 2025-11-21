# shopify_api_connector.py
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

class ShopifyAPIConnector:
    """Handles Shopify API interactions"""
    
    def __init__(self, shop_url: str, access_token: str):
        """
        Initialize Shopify API connector
        
        Args:
            shop_url: Your Shopify shop URL (e.g., 'your-store.myshopify.com')
            access_token: Your Shopify Admin API access token
        """
        self.shop_url = shop_url.rstrip('/')
        self.access_token = access_token
        self.base_url = f"https://{self.shop_url}/admin/api/2024-10"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger("shopify_api")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Shopify API request failed: {e}")
            raise
    
    def get_recent_orders(self, days_back: int = 30, status: str = "any") -> List[Dict]:
        """
        Get recent orders from Shopify
        
        Args:
            days_back: Number of days to look back
            status: Order status filter (any, open, closed, cancelled)
        
        Returns:
            List of order dictionaries
        """
        created_at_min = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        params = {
            "status": status,
            "created_at_min": created_at_min,
            "limit": 250  # Shopify max per request
        }
        
        all_orders = []
        
        self.logger.info(f"Fetching Shopify orders (last {days_back} days, status: {status})")
        
        try:
            response = self._make_request("orders.json", params)
            orders = response.get("orders", [])
            
            self.logger.info(f"Retrieved {len(orders)} orders from Shopify")
            
            # Transform to match Etsy format for consistency
            for order in orders:
                transformed = self._transform_order(order)
                all_orders.append(transformed)
            
            return all_orders
            
        except Exception as e:
            self.logger.error(f"Error fetching Shopify orders: {e}")
            return []
    
    def get_open_orders(self, days_back: int = 90) -> List[Dict]:
        """
        Get only open/unfulfilled orders
        
        Args:
            days_back: Number of days to look back
        
        Returns:
            List of open order dictionaries
        """
        return self.get_recent_orders(days_back=days_back, status="open")
    
    def _transform_order(self, shopify_order: Dict) -> Dict:
        """
        Transform Shopify order to match Etsy format
        
        This makes it easier to process both platforms with the same logic
        """
        # Extract customer name
        customer_name = "Unknown Customer"
        if shopify_order.get("customer"):
            first = shopify_order["customer"].get("first_name", "")
            last = shopify_order["customer"].get("last_name", "")
            customer_name = f"{first} {last}".strip() or "Unknown Customer"
        
        # Transform line items to match Etsy transaction format
        transactions = []
        for item in shopify_order.get("line_items", []):
            transaction = {
                "sku": item.get("sku", ""),
                "title": item.get("title", ""),
                "quantity": item.get("quantity", 1),
                "price": {
                    "amount": float(item.get("price", 0)) * 100,  # Convert to cents
                    "divisor": 100
                },
                "variations": self._extract_variations(item),
                "product_id": item.get("product_id"),
                "variant_id": item.get("variant_id")
            }
            transactions.append(transaction)
        
        # Check fulfillment status
        fulfillment_status = shopify_order.get("fulfillment_status")
        financial_status = shopify_order.get("financial_status")
        
        # Determine if order is "complete"
        is_complete = (fulfillment_status == "fulfilled" and 
                      financial_status in ["paid", "refunded"])
        
        return {
            "receipt_id": str(shopify_order.get("id", "")),
            "order_number": shopify_order.get("order_number"),
            "name": customer_name,
            "email": shopify_order.get("email", ""),
            "message_from_buyer": shopify_order.get("note", ""),
            "transactions": transactions,
            "created_timestamp": shopify_order.get("created_at"),
            "fulfillment_status": fulfillment_status,
            "financial_status": financial_status,
            "is_complete": is_complete,
            "platform": "shopify",  # Mark platform origin
            "tags": shopify_order.get("tags", "").split(", ")
        }
    
    def _extract_variations(self, line_item: Dict) -> List[Dict]:
        """
        Extract product variations/options from Shopify line item
        
        Returns:
            List of variation dictionaries matching Etsy format
        """
        variations = []
        
        # Shopify stores variants as properties
        for i in range(1, 4):  # Shopify supports up to 3 options
            option_name = line_item.get(f"variant_title")
            if option_name and option_name != "Default Title":
                # Try to parse option name if it's in "Name: Value" format
                if ":" in str(option_name):
                    parts = option_name.split(":", 1)
                    variations.append({
                        "formatted_name": parts[0].strip(),
                        "formatted_value": parts[1].strip()
                    })
                else:
                    variations.append({
                        "formatted_name": f"Option {i}",
                        "formatted_value": str(option_name)
                    })
        
        # Also check for custom properties (personalization)
        if line_item.get("properties"):
            for prop in line_item["properties"]:
                if prop.get("name") and prop.get("value"):
                    variations.append({
                        "formatted_name": prop["name"],
                        "formatted_value": prop["value"]
                    })
        
        return variations
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """Get a specific order by ID"""
        try:
            response = self._make_request(f"orders/{order_id}.json")
            order = response.get("order")
            if order:
                return self._transform_order(order)
            return None
        except Exception as e:
            self.logger.error(f"Error fetching order {order_id}: {e}")
            return None