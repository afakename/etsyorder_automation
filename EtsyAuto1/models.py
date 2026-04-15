"""
models.py
SQLAlchemy ORM models for the Etsy/Shopify Production Workflow Dashboard.
"""
from datetime import datetime
from database import db

# Valid workflow stages (ordered)
VALID_STAGES = [
    'new',
    'needs_design',
    'needs_update',
    'in_progress',
    'preview_sent',
    'awaiting_approval',
    'approved',
    'ready_to_print',
    'in_slicer',
    'printed',
    'packaged',
    'complete',
]

STAGE_LABELS = {
    'new': 'New',
    'needs_design': 'Needs Design',
    'needs_update': 'Needs Update',
    'in_progress': 'In Progress',
    'preview_sent': 'Preview Sent',
    'awaiting_approval': 'Awaiting Approval',
    'approved': 'Approved',
    'ready_to_print': 'Ready to Print',
    'in_slicer': 'In Slicer',
    'printed': 'Printed',
    'packaged': 'Packaged',
    'complete': 'Complete',
}

STAGE_COLORS = {
    'new': 'gray',
    'needs_design': 'red',
    'needs_update': 'orange',
    'in_progress': 'yellow',
    'preview_sent': 'purple',
    'awaiting_approval': 'purple',
    'approved': 'blue',
    'ready_to_print': 'blue',
    'in_slicer': 'teal',
    'printed': 'green',
    'packaged': 'green',
    'complete': 'gray',
}


class Customer(db.Model):
    """
    Deduplicated customer record. One customer may have both Etsy and Shopify
    orders. Email is the primary deduplication key.
    """
    __tablename__ = 'customers'

    id              = db.Column(db.Integer, primary_key=True)
    etsy_user_id    = db.Column(db.String(50), unique=True, nullable=True, index=True)
    shopify_id      = db.Column(db.String(50), unique=True, nullable=True, index=True)
    name            = db.Column(db.String(200), nullable=False)
    email           = db.Column(db.String(200), unique=True, nullable=True, index=True)
    city            = db.Column(db.String(100))
    state           = db.Column(db.String(100))
    country         = db.Column(db.String(10))
    order_count     = db.Column(db.Integer, default=0)
    lifetime_value  = db.Column(db.Float, default=0.0)
    notes           = db.Column(db.Text)
    first_order_at  = db.Column(db.DateTime)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = db.relationship('Order', backref='customer', lazy='dynamic')

    def __repr__(self):
        return f'<Customer {self.name} ({self.email})>'


class Order(db.Model):
    """
    One Etsy receipt or Shopify order. May contain multiple OrderItems (line items).
    This is the grouping unit in the dashboard.
    """
    __tablename__ = 'orders'

    id                  = db.Column(db.Integer, primary_key=True)
    source              = db.Column(db.String(20), nullable=False, default='etsy')  # 'etsy' or 'shopify'
    receipt_id          = db.Column(db.String(50), nullable=False, index=True)
    customer_id         = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    customer_name       = db.Column(db.String(200), nullable=False)  # denormalized for speed
    buyer_email         = db.Column(db.String(200))
    order_date          = db.Column(db.DateTime)
    grandtotal_usd      = db.Column(db.Float)
    is_gift             = db.Column(db.Boolean, default=False)
    message_from_buyer  = db.Column(db.Text)
    platform_status     = db.Column(db.String(50))  # "Paid", "Shipped", etc. from platform
    is_priority         = db.Column(db.Boolean, default=False)
    city                = db.Column(db.String(100))
    state               = db.Column(db.String(100))
    country             = db.Column(db.String(10))
    first_seen_at       = db.Column(db.DateTime, default=datetime.utcnow)
    last_synced_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy='dynamic',
                            cascade='all, delete-orphan',
                            order_by='OrderItem.personalization_name')

    __table_args__ = (
        db.UniqueConstraint('source', 'receipt_id', name='uq_order_source_receipt'),
    )

    @property
    def item_count(self):
        return self.items.count()

    @property
    def ready_count(self):
        """Number of items in ready_to_print, approved, or further stages."""
        advanced = {'approved', 'ready_to_print', 'in_slicer', 'printed', 'packaged', 'complete'}
        return sum(1 for item in self.items if item.stage in advanced)

    @property
    def all_complete(self):
        return self.item_count > 0 and all(i.stage == 'complete' for i in self.items)

    def __repr__(self):
        return f'<Order {self.source}#{self.receipt_id} {self.customer_name}>'


class OrderItem(db.Model):
    """
    One line item within an order — the primary workflow unit.
    Everything tracked at the individual design level goes here.
    """
    __tablename__ = 'order_items'

    id                      = db.Column(db.Integer, primary_key=True)
    order_id                = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    # Etsy / Shopify transaction data
    transaction_id          = db.Column(db.String(50), unique=True, nullable=False, index=True)
    sku                     = db.Column(db.String(100), nullable=False, index=True)
    product_type            = db.Column(db.String(10))           # 'MS' or 'RR'
    personalization_name    = db.Column(db.String(200))          # e.g. "Blake" (the name on the ornament)
    design_name             = db.Column(db.String(100))          # e.g. "Star", "Flk"
    year_value              = db.Column(db.String(20))           # e.g. "2024", "Star", ""
    quantity                = db.Column(db.Integer, default=1)
    price_usd               = db.Column(db.Float)
    title                   = db.Column(db.String(500))
    variations_raw          = db.Column(db.Text)                 # JSON blob of raw variations

    # Generated filename and file resolution
    generated_filename      = db.Column(db.String(300))          # what we expect on disk
    match_type              = db.Column(db.String(10))           # 'exact' | 'fuzzy' | 'none'
    matched_filename        = db.Column(db.String(300))          # actual filename found (may differ)
    svg_path                = db.Column(db.String(600))          # absolute path to SVG (null if not found)
    svg_found_at            = db.Column(db.DateTime)
    stl_path                = db.Column(db.String(600))          # absolute path to STL (null if not found)
    stl_found_at            = db.Column(db.DateTime)
    png_cache_path          = db.Column(db.String(600))          # path to cached preview PNG

    # Workflow stage
    stage                   = db.Column(db.String(30), nullable=False, default='new', index=True)
    stage_updated_at        = db.Column(db.DateTime, default=datetime.utcnow)
    stage_updated_by        = db.Column(db.String(100), default='system')  # 'system' or 'user'

    # Preview tracking
    preview_requested       = db.Column(db.Boolean, default=False)
    preview_sent            = db.Column(db.Boolean, default=False)
    preview_sent_at         = db.Column(db.DateTime)
    preview_approved        = db.Column(db.Boolean, default=False)
    preview_approved_at     = db.Column(db.DateTime)

    # Display / production settings
    flip_horizontal         = db.Column(db.Boolean, default=False)  # auto True for RR
    bg_color                = db.Column(db.String(20), default='#ffffff')
    notes                   = db.Column(db.Text)
    is_priority             = db.Column(db.Boolean, default=False)

    created_at              = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at              = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def stage_label(self):
        return STAGE_LABELS.get(self.stage, self.stage)

    @property
    def stage_color(self):
        return STAGE_COLORS.get(self.stage, 'gray')

    @property
    def has_file(self):
        return self.svg_path is not None

    @property
    def has_stl(self):
        return self.stl_path is not None

    @property
    def display_name(self):
        """Short display name for UI cards."""
        return self.generated_filename or self.personalization_name or self.title or 'Unknown'

    def set_stage(self, new_stage, updated_by='user'):
        """Set stage and record who/when changed it."""
        if new_stage in VALID_STAGES:
            self.stage = new_stage
            self.stage_updated_at = datetime.utcnow()
            self.stage_updated_by = updated_by

    def __repr__(self):
        return f'<OrderItem {self.generated_filename} [{self.stage}]>'


class PollLog(db.Model):
    """Record of each automatic or manual poll run."""
    __tablename__ = 'poll_log'

    id                  = db.Column(db.Integer, primary_key=True)
    source              = db.Column(db.String(20), default='all')  # 'etsy', 'shopify', 'all', 'rescan'
    started_at          = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at        = db.Column(db.DateTime)
    status              = db.Column(db.String(20))   # 'success', 'error', 'no_orders'
    new_items_count     = db.Column(db.Integer, default=0)
    updated_count       = db.Column(db.Integer, default=0)
    advanced_count      = db.Column(db.Integer, default=0)  # items auto-advanced by rescan
    error_message       = db.Column(db.Text)
    days_polled         = db.Column(db.Integer, default=7)

    def __repr__(self):
        return f'<PollLog {self.source} {self.started_at} [{self.status}]>'


class AppSetting(db.Model):
    """Key-value configuration table for runtime settings."""
    __tablename__ = 'app_settings'

    key         = db.Column(db.String(100), primary_key=True)
    value       = db.Column(db.Text)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get(cls, key, default=None):
        row = cls.query.get(key)
        return row.value if row else default

    @classmethod
    def set(cls, key, value):
        row = cls.query.get(key)
        if row:
            row.value = str(value)
        else:
            row = cls(key=key, value=str(value))
            db.session.add(row)
        db.session.commit()

    def __repr__(self):
        return f'<AppSetting {self.key}={self.value}>'
