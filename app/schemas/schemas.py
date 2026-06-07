from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from decimal import Decimal


# ── Menu Schemas ─────────────────────────────────────────────────────────────

class ItemSizeOut(BaseModel):
    size: str
    price: Decimal

    class Config:
        from_attributes = True


class MenuItemOut(BaseModel):
    item_id: int
    item_name: str
    category: str
    menu: str
    sizes: List[ItemSizeOut] = []

    class Config:
        from_attributes = True


# ── Order Schemas ─────────────────────────────────────────────────────────────

class OrderItemOut(BaseModel):
    id: int
    item_id: int
    item_name: str
    category: str
    size: Optional[str] = None
    unit_price: Decimal
    qty: int
    line_total: Decimal

    class Config:
        from_attributes = True


class PaymentOut(BaseModel):
    payment_id: int
    payment_date: date
    payment_type: str
    payment_status: str
    amount_due: Decimal
    tips: Decimal
    discount: Decimal
    total_paid: Decimal

    class Config:
        from_attributes = True


class OrderDetailOut(BaseModel):
    order_id: int
    order_date: date
    order_status: str
    items: List[OrderItemOut]
    payments: List[PaymentOut]

    # Computed summary fields
    item_count: int = Field(..., description="Total number of item lines")
    gross_total: Decimal = Field(..., description="Sum of all order item totals")
    total_tips: Decimal
    total_discount: Decimal
    total_paid: Decimal
    payment_summary: str = Field(..., description="e.g. Card + Cash (split)")
    is_fully_paid: bool

    class Config:
        from_attributes = True


class PaginatedOrdersOut(BaseModel):
    total: int
    page: int
    page_size: int
    orders: List[OrderDetailOut]
