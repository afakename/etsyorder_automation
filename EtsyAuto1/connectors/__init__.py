"""
connectors/
Normalized order data connectors for Etsy and Shopify.
Both connectors expose the same interface so workflow.py
doesn't need to know which platform it's talking to.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class NormalizedItem:
    """One line item from any platform, in a consistent format."""
    transaction_id: str
    sku: str
    title: str
    quantity: int
    price_usd: float
    variations: dict              # formatted_name -> formatted_value
    item_note: str = ''           # e.g. RR 'Message Box' — merged into order message


@dataclass
class NormalizedOrder:
    """One receipt/order from any platform, in a consistent format."""
    source: str           # 'etsy' or 'shopify'
    receipt_id: str
    customer_name: str
    buyer_email: str
    buyer_platform_id: str  # etsy_user_id or shopify_customer_id
    order_date: Optional[datetime]
    grandtotal_usd: float
    is_gift: bool
    message_from_buyer: str
    platform_status: str
    city: str
    state: str
    country: str
    items: list = field(default_factory=list)
