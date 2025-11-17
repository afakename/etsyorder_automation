#!/usr/bin/env python3
"""
Debug script to find a specific order and understand why it's not appearing in sheets
"""
import sys
sys.path.insert(0, '/home/user/etsyorder_automation/EtsyAuto1')

from etsy_api_connector import EtsyAPIConnector
from datetime import datetime

def debug_order(order_id):
    """Debug why a specific order isn't appearing"""
    print(f"\n{'='*60}")
    print(f"DEBUGGING ORDER: {order_id}")
    print(f"{'='*60}\n")

    etsy = EtsyAPIConnector()

    if not etsy.test_connection():
        print("❌ Failed to connect to Etsy API")
        return

    print("✓ Connected to Etsy API\n")

    # Try to get the specific order
    print(f"1. Checking if order {order_id} exists...")
    order_details = etsy.get_order_details(order_id)

    if not order_details:
        print(f"❌ Could not fetch order {order_id}")
        print("   Possible reasons:")
        print("   - Order ID is incorrect")
        print("   - Order is too old or deleted")
        print("   - API permissions issue")
        return

    print(f"✓ Order {order_id} found!\n")

    # Check order status
    status = order_details.get('status', 'Unknown')
    print(f"2. Order Status: {status}")

    if status.lower() in ['complete', 'completed']:
        print(f"   ⚠️  Order is CLOSED (status = {status})")
        print(f"   This is why it's not appearing - the script runs in 'open_only' mode")
        print(f"   Only orders with status != 'Complete' are fetched\n")
    else:
        print(f"   ✓ Order is OPEN (status = {status})")
        print(f"   This order SHOULD be fetched by the automation\n")

    # Check order date
    created = order_details.get('created_timestamp')
    if created:
        order_date = datetime.fromtimestamp(created)
        days_old = (datetime.now() - order_date).days
        print(f"3. Order Date: {order_date.strftime('%Y-%m-%d')} ({days_old} days ago)")

        if days_old > 90:
            print(f"   ⚠️  Order is older than 90 days!")
            print(f"   Default days_back is 90 - this order might not be fetched")
            print(f"   Run with: python main.py --days {days_old + 10}\n")
        else:
            print(f"   ✓ Order is within the 90-day window\n")

    # Check transactions and SKUs
    print(f"4. Order Items:")
    transactions = order_details.get('transactions', [])

    if not transactions:
        print("   ❌ No transactions found in order!")
        return

    from config import Config

    PEACE_LOVE_HOPE_SKUS = {
        'FckFlkEarring-RR-01', 'FuckFlkOrn-Mirr-03', 'FuckFlkOrn-Mirr-04',
        'FuckFlkOrn-Mirr-05', 'FuckFlkOrn-RR-01', 'FuckFlkOrn-RR-02',
        'HopeFlkOrn-Mirr-01', 'HopeFlkOrn-RR-01', 'LoveFlkOrn-Mirr-01',
        'LoveFlkOrn-RR-01', 'PeaceFlkOrn-Mirr-01', 'PeaceFlkOrn-RR-01',
        'PeacLovHopeFlkOrn-Mirr-02', 'PeacLovHopeFlkOrn-RR-01', 'SnoFlkEarring-01'
    }

    OTHER_ORDERS_SKUS = {
        'CandyHeartEarring-Dangle-02', 'CandyHeartEarring-Studs-01',
        'MMEarHld-01', 'PersPhotoMag-01', 'PersPhotoMag-02',
        'ThermPrntStand-3D-01', 'USMC-AAV-01', 'USMC-AAVPen-02'
    }

    has_categorized_sku = False

    for idx, trans in enumerate(transactions, 1):
        title = trans.get('title', 'Unknown')
        sku = trans.get('sku', '')
        qty = trans.get('quantity', 1)

        print(f"   Item {idx}: {title}")
        print(f"           SKU: {sku}")
        print(f"           Qty: {qty}")

        # Check categorization
        if sku in Config.WORKFLOW_SKUS:
            print(f"           ✓ Category: WORKFLOW (MS/RR)")
            has_categorized_sku = True
        elif sku in PEACE_LOVE_HOPE_SKUS:
            print(f"           ✓ Category: Peace/Love/Hope")
            has_categorized_sku = True
        elif sku in OTHER_ORDERS_SKUS:
            print(f"           ✓ Category: Other Orders")
            has_categorized_sku = True
        else:
            print(f"           ❌ Category: NOT CATEGORIZED")
            print(f"           This SKU is not in any category!")

        # Show variations
        variations = trans.get('variations', [])
        if variations:
            print(f"           Variations:")
            for var in variations:
                print(f"             - {var.get('formatted_name', '')}: {var.get('formatted_value', '')}")

        print()

    # Summary
    print(f"5. DIAGNOSIS:")
    print(f"{'='*60}")

    if status.lower() in ['complete', 'completed']:
        print("❌ ISSUE FOUND: Order is CLOSED in Etsy")
        print("   Solution: Order is complete, so it won't appear in open orders")
    elif days_old > 90:
        print("❌ ISSUE FOUND: Order is older than 90 days")
        print(f"   Solution: Run with --days {days_old + 10}")
    elif not has_categorized_sku:
        print("❌ ISSUE FOUND: Order has no categorized SKUs")
        print("   The order won't appear because none of its SKUs match")
        print("   the known categories (Workflow, Peace/Love/Hope, Other)")
    else:
        print("✓ NO ISSUES FOUND")
        print("   This order SHOULD appear in the automation sheets")
        print("   Try running the automation again to see if it appears")

    print(f"{'='*60}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_order.py <order_id>")
        print("Example: python debug_order.py 3849790237")
        sys.exit(1)

    order_id = sys.argv[1]
    debug_order(order_id)
