#!/usr/bin/env python3
"""
Diagnostic script to check order status fields and identify stuck orders
"""

from etsy_api_connector import EtsyAPIConnector
from datetime import datetime
import json

def diagnose_orders():
    """Check what status fields are available in orders"""
    etsy = EtsyAPIConnector()

    if not etsy.test_connection():
        print("Failed to connect to Etsy API")
        return

    print("\n" + "="*70)
    print("DIAGNOSTIC: Checking Order Status Fields")
    print("="*70)

    # Get recent orders (including ALL statuses)
    print("\nFetching recent orders (last 120 days, all statuses)...")
    all_orders = etsy.get_recent_orders(days_back=120, limit=100)

    if not all_orders:
        print("No orders found")
        return

    print(f"\nFound {len(all_orders)} total orders\n")

    # Analyze each order
    status_fields_found = set()
    order_statuses = {}

    print("="*70)
    print("ORDER ANALYSIS:")
    print("="*70)

    for i, order in enumerate(all_orders, 1):
        receipt_id = order.get('receipt_id', 'Unknown')
        customer_name = order.get('name', 'Unknown')

        # Check what status-related fields exist
        status_info = {}
        for key in order.keys():
            if 'status' in key.lower() or 'state' in key.lower() or 'complete' in key.lower():
                status_fields_found.add(key)
                status_info[key] = order[key]

        # Also check common fields
        for key in ['was_paid', 'was_shipped', 'is_gift', 'shipped_timestamp', 'status']:
            if key in order:
                status_info[key] = order[key]

        # Track unique status combinations
        status_key = str(sorted(status_info.items()))
        if status_key not in order_statuses:
            order_statuses[status_key] = []
        order_statuses[status_key].append(receipt_id)

        # Print first 10 orders in detail
        if i <= 10:
            print(f"\nOrder #{i}: {receipt_id} - {customer_name}")
            print("-" * 70)
            for key, value in sorted(status_info.items()):
                print(f"  {key}: {value}")

            # Check if this order has transactions
            if 'transactions' in order and order['transactions']:
                print(f"  Transactions: {len(order['transactions'])} items")

    print("\n" + "="*70)
    print("SUMMARY OF STATUS FIELDS FOUND:")
    print("="*70)
    for field in sorted(status_fields_found):
        print(f"  - {field}")

    print("\n" + "="*70)
    print("UNIQUE STATUS COMBINATIONS:")
    print("="*70)
    for i, (status_combo, receipt_ids) in enumerate(order_statuses.items(), 1):
        print(f"\nCombination #{i} ({len(receipt_ids)} orders):")
        # Parse back the status info
        try:
            status_dict = dict(eval(status_combo))
            for key, value in sorted(status_dict.items()):
                print(f"  {key}: {value}")
        except:
            print(f"  {status_combo}")
        print(f"  Order IDs: {', '.join(map(str, receipt_ids[:5]))}{' ...' if len(receipt_ids) > 5 else ''}")

    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    print("Look at the status fields above to determine which field(s)")
    print("indicate if an order is complete or canceled.")
    print("\nIf you see a specific stuck order ID, look for what makes it")
    print("different from orders that should be filtered out.")
    print("="*70)

if __name__ == "__main__":
    diagnose_orders()
