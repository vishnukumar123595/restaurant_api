from fastapi import APIRouter, Depends, Query, HTTPException, Security
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from decimal import Decimal

from app.db.database import get_db
from app.models.models import Order, OrderItem, Payment, MenuItem, Category
from app.schemas.schemas import OrderDetailOut, OrderItemOut, PaymentOut, PaginatedOrdersOut
from app.security import require_api_key

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    # Security applied at router level — every route gets the lock icon in Swagger
    dependencies=[Security(require_api_key)],
)


# ── Helper ────────────────────────────────────────────────────────────────────

def _build_order_detail(order: Order) -> OrderDetailOut:
    """Convert an ORM Order into the full nested response schema."""

    items_out = [
        OrderItemOut(
            id=oi.id,
            item_id=oi.item_id,
            item_name=oi.menu_item.item_name,
            category=oi.menu_item.category.category_name,
            size=oi.size,
            unit_price=oi.price,
            qty=oi.qty,
            line_total=oi.total,
        )
        for oi in order.items
    ]

    payments_out = [
        PaymentOut(
            payment_id=p.payment_id,
            payment_date=p.payment_date,
            payment_type=p.payment_type,
            payment_status=p.payment_status,
            amount_due=p.amount_due,
            tips=p.tips,
            discount=p.discount,
            total_paid=p.total_paid,
        )
        for p in order.payments
    ]

    gross_total    = sum(Decimal(str(i.total))     for i in order.items)
    total_tips     = sum(Decimal(str(p.tips))      for p in order.payments)
    total_discount = sum(Decimal(str(p.discount))  for p in order.payments)
    total_paid     = sum(Decimal(str(p.total_paid)) for p in order.payments)

    # Human-readable payment summary
    types    = sorted({p.payment_type   for p in order.payments})
    statuses = {p.payment_status for p in order.payments}
    payment_summary = " + ".join(types)
    if len(order.payments) > 1:
        payment_summary += " (split)"
    if "Refunded" in statuses:
        payment_summary += " [Refunded]"

    is_fully_paid = (
        abs(total_paid - (gross_total + total_tips - total_discount)) < Decimal("0.05")
    )

    return OrderDetailOut(
        order_id=order.order_id,
        order_date=order.order_date,
        order_status=order.order_status,
        items=items_out,
        payments=payments_out,
        item_count=len(items_out),
        gross_total=round(gross_total, 4),
        total_tips=round(total_tips, 4),
        total_discount=round(total_discount, 4),
        total_paid=round(total_paid, 4),
        payment_summary=payment_summary,
        is_fully_paid=is_fully_paid,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=PaginatedOrdersOut,
    summary="List all orders",
    description="""
Returns a **paginated list of all orders**, each containing:

- 🧾 **Order info** — order ID, date, status
- 🍔 **Line items** — item name, category, size, unit price, quantity, line total
- 💳 **Payments** — payment ID, type (Card/Cash), status, tips, discounts, amount paid
- 📊 **Summary fields** — gross total, total paid, payment summary, reconciliation flag

### Filtering
Use `order_status` or `payment_status` query params to narrow results.

### Example
```
GET /orders/?page=1&page_size=5
GET /orders/?payment_status=Refunded
```

### Auth
Requires `X-API-Key` header. Click **Authorize** (top right) and enter the key.
    """,
    responses={
        200: {"description": "Successfully returned paginated orders"},
        401: {"description": "Missing or invalid API key"},
        422: {"description": "Invalid query parameters"},
    },
)
def list_orders(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of orders per page (max 100)"),
    order_status: Optional[str] = Query(
        None,
        description="Filter by order status. Example: `Completed`",
        examples=["Completed"],
    ),
    payment_status: Optional[str] = Query(
        None,
        description="Filter orders by payment status. Example: `Refunded`",
        examples=["Refunded"],
    ),
    db: Session = Depends(get_db),
):
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.menu_item).joinedload(MenuItem.category),
        joinedload(Order.payments),
    )

    if order_status:
        query = query.filter(func.lower(Order.order_status) == order_status.lower())

    if payment_status:
        query = query.join(Order.payments).filter(func.lower(Payment.payment_status) == payment_status.lower()).distinct()


    total = query.count()
    orders_page = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedOrdersOut(
        total=total,
        page=page,
        page_size=page_size,
        orders=[_build_order_detail(o) for o in orders_page],
    )


@router.get(
    "/{order_id}",
    response_model=OrderDetailOut,
    summary="Get a single order by ID",
    description="""
Returns **full details for one order** by its Order ID.

Includes all line items, payment records, and computed summary fields.

### Notable test cases
| Order ID | What it demonstrates |
|----------|----------------------|
| `10` | Simple single Card payment |
| `11` | Split payment — Cash + Card |
| `14` | Split payment, 8 line items, duplicate item (data anomaly) |
| `15` | **Refunded** payment |
| `19` | Largest order — 9 line items, Cash + Card split |

### Auth
Requires `X-API-Key` header. Click **Authorize** (top right) and enter the key.
    """,
    responses={
        200: {"description": "Order found and returned"},
        401: {"description": "Missing or invalid API key"},
        404: {"description": "Order not found"},
    },
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = (
        db.query(Order)
        .options(
            joinedload(Order.items).joinedload(OrderItem.menu_item).joinedload(MenuItem.category),
            joinedload(Order.payments),
        )
        .filter(Order.order_id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Not Found",
                "message": f"Order ID {order_id} does not exist.",
                "valid_order_ids": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            },
        )

    return _build_order_detail(order)
