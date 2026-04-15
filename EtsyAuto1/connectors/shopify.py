"""
connectors/shopify.py
Shopify Orders API connector.
Uses the same NormalizedOrder / NormalizedItem interface as etsy.py
so workflow.py treats both sources identically.

Shopify REST Admin API: GET /admin/api/2024-01/orders.json
Auth: X-Shopify-Access-Token header (Private App token or Custom App)
"""
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from connectors import NormalizedOrder, NormalizedItem
from config import Config

logger = logging.getLogger('shopify_connector')

# Map Shopify line item properties to variation keys used by FilenameGenerator.
# Shopify personalizations typically come in as line item "properties".
# Adjust these if the Shopify product is set up differently.
SHOPIFY_PROPERTY_MAP = {
    # --- MS product (GloboProduct option set 1252196) ---
    'text-1': 'Personalization',                # Customer name
    'Center Design': 'Choose the Center Piece', # Star Design / custom
    'Year or No Year': 'Year or No Year',

    # --- RR product (GloboProduct option set 388199) ---
    'Personalization feature text': 'Personalization',  # Customer name
    'Center Piece': 'Choose the Center Piece',          # Current Year / Let the design...
    'Message Box': 'message_from_buyer',                # Gift / custom message

    # Legacy / fallback names
    'Personalization': 'Personalization',
    'Choose the Center Piece': 'Choose the Center Piece',
    'Current Year or Star Design': 'Current Year or Star Design',
}

# GloboProduct internal fields — not customer-facing, always skip
SHOPIFY_SKIP_PROPERTIES = {'_has_gpo'}


class ShopifyConnector:
    """
    Fetches Shopify orders and normalizes them into NormalizedOrder objects.
    Requires SHOPIFY_DOMAIN and SHOPIFY_ACCESS_TOKEN in environment / config.
    """

    API_VERSION = '2024-01'

    def __init__(self):
        self.domain = Config.SHOPIFY_DOMAIN
        self.token = Config.SHOPIFY_ACCESS_TOKEN
        self._configured = bool(self.domain and self.token)

    def is_configured(self) -> bool:
        return self._configured

    def get_recent_orders(self, days_back: int = 7, limit: int = 250) -> list[NormalizedOrder]:
        """
        Fetch recent Shopify orders, filter for WORKFLOW_SKUS, normalize.
        Returns empty list if Shopify is not configured.
        """
        if not self._configured:
            logger.info("Shopify connector not configured — skipping.")
            return []

        since = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%dT%H:%M:%SZ')
        url = f"https://{self.domain}/admin/api/{self.API_VERSION}/orders.json"
        headers = {'X-Shopify-Access-Token': self.token}
        params = {
            'status': 'open',
            'created_at_min': since,
            'limit': limit,
            'fields': 'id,name,email,customer,billing_address,created_at,total_price,'
                      'note,note_attributes,financial_status,fulfillment_status,line_items',
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            orders_raw = response.json().get('orders', [])
        except Exception as e:
            logger.error(f"Shopify API error: {e}")
            return []

        normalized = []
        for raw in orders_raw:
            order = self._normalize_order(raw)
            if order and order.items:
                normalized.append(order)

        logger.info(f"Shopify: fetched {len(orders_raw)} orders, {len(normalized)} with workflow items")
        return normalized

    def _normalize_order(self, raw: dict) -> NormalizedOrder | None:
        """Convert a raw Shopify order dict into a NormalizedOrder."""
        try:
            customer = raw.get('customer', {}) or {}
            address = raw.get('billing_address', {}) or {}

            customer_name = (
                f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                or raw.get('email', 'Unknown')
            )

            order_date_str = raw.get('created_at', '')
            order_date = None
            if order_date_str:
                try:
                    order_date = datetime.fromisoformat(order_date_str.replace('Z', '+00:00'))
                except ValueError:
                    pass

            try:
                total_usd = float(raw.get('total_price', 0))
            except (ValueError, TypeError):
                total_usd = 0.0

            # Filter line items to workflow SKUs
            workflow_items = []
            for line_item in raw.get('line_items', []):
                if line_item.get('sku', '') in Config.WORKFLOW_SKUS:
                    item = self._normalize_line_item(line_item)
                    if item:
                        workflow_items.append(item)

            if not workflow_items:
                return None

            # Note from buyer: Shopify uses 'note' field
            note = raw.get('note') or ''
            for attr in raw.get('note_attributes', []):
                note += f"\n{attr.get('name', '')}: {attr.get('value', '')}"
            # Merge any per-item notes (e.g. RR 'Message Box') into the order note
            for item in workflow_items:
                if item.item_note:
                    note += f"\n{item.item_note}"

            return NormalizedOrder(
                source='shopify',
                receipt_id=str(raw.get('id', '')),
                customer_name=customer_name,
                buyer_email=raw.get('email', ''),
                buyer_platform_id=str(customer.get('id', '')),
                order_date=order_date,
                grandtotal_usd=round(total_usd, 2),
                is_gift=False,  # Shopify doesn't have a universal gift flag
                message_from_buyer=note.strip(),
                platform_status=raw.get('financial_status', ''),
                city=address.get('city', ''),
                state=address.get('province', ''),
                country=address.get('country_code', ''),
                items=workflow_items,
            )
        except Exception as e:
            logger.warning(f"Failed to normalize Shopify order: {e}")
            return None

    def _normalize_line_item(self, line_item: dict) -> NormalizedItem | None:
        """Convert a Shopify line item into a NormalizedItem."""
        try:
            # Shopify personalizations come in as 'properties' array
            variations = {}
            extra_message = None
            for prop in line_item.get('properties', []):
                raw_name = prop.get('name', '')
                value = prop.get('value', '')
                if raw_name in SHOPIFY_SKIP_PROPERTIES or not value:
                    continue
                mapped_name = SHOPIFY_PROPERTY_MAP.get(raw_name, raw_name)
                if mapped_name == 'message_from_buyer':
                    extra_message = value  # bubble up to order note
                elif mapped_name:
                    variations[mapped_name] = value

            try:
                price_usd = float(line_item.get('price', 0))
            except (ValueError, TypeError):
                price_usd = 0.0

            return NormalizedItem(
                transaction_id=str(line_item.get('id', '')),
                sku=line_item.get('sku', ''),
                title=line_item.get('title', ''),
                quantity=int(line_item.get('quantity', 1)),
                price_usd=round(price_usd, 2),
                variations=variations,
                item_note=extra_message or '',
            )
        except Exception as e:
            logger.warning(f"Failed to normalize Shopify line item: {e}")
            return None
