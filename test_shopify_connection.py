# test_shopify_connection.py
"""
Test script to connect to Shopify and examine the actual data structure
"""
import json
from shopify_api_connector import ShopifyAPIConnector
from config import Config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("="*60)
    print("SHOPIFY CONNECTION TEST")
    print("="*60)
    
    # Initialize connector
    try:
        shopify = ShopifyAPIConnector(
            shop_url=Config.SHOPIFY_SHOP_URL,
            access_token=Config.SHOPIFY_ACCESS_TOKEN
        )
        print(f"✓ Connected to: {Config.SHOPIFY_SHOP_URL}\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return
    
    # Test 1: Get recent orders (any status, last 90 days)
    print("-" * 60)
    print("TEST 1: Fetching recent orders (last 90 days, any status)")
    print("-" * 60)
    
    try:
        orders = shopify.get_recent_orders(days_back=90, status="any")
        print(f"Found {len(orders)} total orders\n")
        
        if orders:
            # Show first order in detail
            print("FIRST ORDER SAMPLE:")
            print(json.dumps(orders[0], indent=2, default=str))
            print("\n")
            
            # Summary of all orders
            print("="*60)
            print("ORDER SUMMARY:")
            print("="*60)
            for i, order in enumerate(orders, 1):
                print(f"\nOrder {i}:")
                print(f"  Order ID: {order.get('receipt_id')}")
                print(f"  Order Number: {order.get('order_number')}")
                print(f"  Customer: {order.get('name')}")
                print(f"  Platform: {order.get('platform')}")
                print(f"  Fulfillment Status: {order.get('fulfillment_status')}")
                print(f"  Financial Status: {order.get('financial_status')}")
                print(f"  Is Complete: {order.get('is_complete')}")
                print(f"  Created: {order.get('created_timestamp')}")
                print(f"  Message: {order.get('message_from_buyer', 'None')[:50]}")
                
                print(f"  Items ({len(order.get('transactions', []))}):")
                for j, item in enumerate(order.get('transactions', []), 1):
                    sku = item.get('sku', 'NO SKU')
                    title = item.get('title', 'Unknown')
                    qty = item.get('quantity', 1)
                    print(f"    {j}. SKU: {sku} | {title} (Qty: {qty})")
                    
                    # Show variations/personalization
                    variations = item.get('variations', [])
                    if variations:
                        print(f"       Variations:")
                        for var in variations:
                            name = var.get('formatted_name', 'Unknown')
                            value = var.get('formatted_value', 'Unknown')
                            print(f"         - {name}: {value}")
        else:
            print("No orders found in the last 90 days")
    
    except Exception as e:
        print(f"✗ Error fetching orders: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Try different time ranges
    print("\n" + "="*60)
    print("TEST 2: Order counts by time range")
    print("="*60)
    
    time_ranges = [7, 30, 60, 90, 180, 365]
    for days in time_ranges:
        try:
            orders = shopify.get_recent_orders(days_back=days, status="any")
            print(f"Last {days:3d} days: {len(orders):3d} orders")
        except Exception as e:
            print(f"Last {days:3d} days: Error - {e}")
    
    # Test 3: Check open orders specifically
    print("\n" + "="*60)
    print("TEST 3: Open/unfulfilled orders only")
    print("="*60)
    
    try:
        open_orders = shopify.get_open_orders(days_back=90)
        print(f"Found {len(open_orders)} open orders\n")
        
        if open_orders:
            for i, order in enumerate(open_orders, 1):
                print(f"Open Order {i}:")
                print(f"  Order ID: {order.get('receipt_id')}")
                print(f"  Customer: {order.get('name')}")
                print(f"  Fulfillment: {order.get('fulfillment_status')}")
                print(f"  Financial: {order.get('financial_status')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Export sample data to JSON for inspection
    print("\n" + "="*60)
    print("TEST 4: Exporting sample data")
    print("="*60)
    
    try:
        orders = shopify.get_recent_orders(days_back=90, status="any")
        if orders:
            output_file = "shopify_sample_data.json"
            with open(output_file, 'w') as f:
                json.dump(orders, f, indent=2, default=str)
            print(f"✓ Sample data exported to: {output_file}")
            print(f"  Review this file to see the exact structure")
        else:
            print("No data to export")
    except Exception as e:
        print(f"✗ Export failed: {e}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()