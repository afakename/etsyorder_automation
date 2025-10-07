from etsy_api_connector import EtsyAPIConnector
import json

etsy = EtsyAPIConnector()

from etsy_api_connector import EtsyAPIConnector
import json

etsy = EtsyAPIConnector()

# Get recent orders
orders = etsy.get_recent_orders(days_back=30, limit=5)

if orders:
    print("Status fields in your orders:\n")
    print("="*60)
    
    for i, order in enumerate(orders[:3]):
        print(f"\nOrder {i+1} - Receipt ID: {order['receipt_id']}")
        print(f"Customer: {order.get('name', 'Unknown')}")
        print("-"*60)
        
        # Print all status-related fields
        status_fields = [
            'was_paid', 'was_shipped', 'was_delivered', 
            'is_gift', 'needs_gift_wrap', 'is_dead',
            'status', 'shipment_status'
        ]
        
        for field in status_fields:
            if field in order:
                print(f"  {field}: {order[field]}")
        
        print("\n  All fields:")
        for key in sorted(order.keys()):
            print(f"    {key}")
        
        print("="*60)
    
    with open('order_sample.json', 'w') as f:
        json.dump(orders[0], f, indent=2)
    
    print("\nFull order saved to 'order_sample.json'")# Get recent orders
orders = etsy.get_recent_orders(days_back=30, limit=5)

if orders:
    print("Status fields in your orders:\n")
    print("="*60)
    
    for i, order in enumerate(orders[:3]):  # Check first 3 orders
        print(f"\nOrder {i+1} - Receipt ID: {order['receipt_id']}")
        print(f"Customer: {order.get('name', 'Unknown')}")
        print("-"*60)
        
        # Print all status-related fields
        status_fields = [
            'was_paid', 'was_shipped', 'was_delivered', 
            'is_gift', 'needs_gift_wrap', 'is_dead',
            'status', 'shipment_status', 'shipping_upgrade'
        ]
        
        for field in status_fields:
            if field in order:
                print(f"  {field}: {order[field]}")
        
        # Print ALL fields to see what else exists
        print("\n  All available fields:")
        for key in sorted(order.keys()):
            print(f"    {key}")
        
        print("="*60)
    
    # Save full order data to file for inspection
    with open('order_sample.json', 'w') as f:
        json.dump(orders[0], f, indent=2)
    
    print("\nFull order data saved to 'order_sample.json'")
    print("Check this file to see all available fields!")
else:
    print("No orders found")
