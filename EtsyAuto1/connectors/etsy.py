"""
connectors/etsy.py
Thin wrapper around the existing EtsyAPIConnector that normalizes
raw Etsy API responses into NormalizedOrder / NormalizedItem objects.
"""
import sys
import os
from datetime import datetime
from pathlib import Path

# Ensure project root is on path so we can import existing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from connectors import NormalizedOrder, NormalizedItem
from etsy_api_connector import EtsyAPIConnector
from config import Config


class EtsyConnector:
    """
    Fetches Etsy orders and normalizes them.
    Only returns receipts that contain at least one WORKFLOW_SKU item.
    """

    def __init__(self):
        self._api = EtsyAPIConnector()

    def get_recent_orders(self, days_back: int = 7, limit: int = 100) -> list[NormalizedOrder]:
        """
        Fetch recent Etsy receipts, filter for WORKFLOW_SKUS, and normalize.
        Returns list of NormalizedOrder (each containing only workflow items).
        """
        raw_receipts = self._api.get_recent_orders(days_back=days_back, limit=limit)
        if not raw_receipts:
            return []

        normalized = []
        for receipt in raw_receipts:
            order = self._normalize_receipt(receipt)
            if order and order.items:
                normalized.append(order)

        return normalized

    def _normalize_receipt(self, receipt: dict) -> NormalizedOrder | None:
        """Convert a raw Etsy receipt dict into a NormalizedOrder."""
        try:
            # Etsy returns 'Transactions' with capital T
            transactions = receipt.get('Transactions', receipt.get('transactions', []))

            # Filter to only WORKFLOW_SKU items
            workflow_items = []
            for txn in transactions:
                sku = txn.get('sku', '')
                if sku in Config.WORKFLOW_SKUS:
                    item = self._normalize_transaction(txn)
                    if item:
                        workflow_items.append(item)

            if not workflow_items:
                return None

            # Parse price
            grand = receipt.get('grandtotal', {})
            total_usd = grand.get('amount', 0) / max(grand.get('divisor', 100), 1)

            # Parse date
            ts = receipt.get('created_timestamp')
            order_date = datetime.fromtimestamp(ts) if ts else None

            return NormalizedOrder(
                source='etsy',
                receipt_id=str(receipt.get('receipt_id', '')),
                customer_name=receipt.get('name', 'Unknown'),
                buyer_email=receipt.get('buyer_email', ''),
                buyer_platform_id=str(receipt.get('buyer_user_id', '')),
                order_date=order_date,
                grandtotal_usd=round(total_usd, 2),
                is_gift=bool(receipt.get('is_gift', False)),
                message_from_buyer=receipt.get('message_from_buyer') or '',
                platform_status=receipt.get('status', ''),
                city=receipt.get('city', ''),
                state=receipt.get('state', ''),
                country=receipt.get('country_iso', ''),
                items=workflow_items,
            )
        except Exception as e:
            import logging
            logging.getLogger('etsy_connector').warning(f"Failed to normalize receipt: {e}")
            return None

    def _normalize_transaction(self, txn: dict) -> NormalizedItem | None:
        """Convert a raw Etsy transaction into a NormalizedItem."""
        try:
            price_data = txn.get('price', {})
            price_usd = price_data.get('amount', 0) / max(price_data.get('divisor', 100), 1)

            # Convert variations list to dict: formatted_name -> formatted_value
            variations = {}
            for var in txn.get('variations', []):
                name = var.get('formatted_name', '')
                value = var.get('formatted_value', '')
                if name:
                    variations[name] = value

            return NormalizedItem(
                transaction_id=str(txn.get('transaction_id', '')),
                sku=txn.get('sku', ''),
                title=txn.get('title', ''),
                quantity=int(txn.get('quantity', 1)),
                price_usd=round(price_usd, 2),
                variations=variations,
            )
        except Exception as e:
            import logging
            logging.getLogger('etsy_connector').warning(f"Failed to normalize transaction: {e}")
            return None

    def is_authenticated(self) -> bool:
        """Check whether valid tokens exist."""
        return bool(self._api.access_token)

    def trigger_reauth(self) -> bool:
        """Trigger interactive OAuth re-authentication."""
        return self._api.authenticate()
