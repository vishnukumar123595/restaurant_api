# Restaurant Orders API

FastAPI + SQLAlchemy + SQLite assessment project.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed the database (creates restaurant.db)
python seed.py

# 3. Run the server
uvicorn main:app --reload

# 4. Open Swagger UI
# http://127.0.0.1:8000/docs
```

## Project Structure

```
restaurant_api/
├── main.py                          # App entry, middleware
├── seed.py                          # DB seeder (run once)
├── requirements.txt
├── Restaurant_Orders_API.postman_collection.json
└── app/
    ├── db/database.py               # Engine, session, Base
    ├── models/models.py             # SQLAlchemy ORM models
    ├── schemas/schemas.py           # Pydantic response schemas
    ├── routers/orders.py            # API endpoints
    └── security.py                  # API key auth
```

## Authentication

Every endpoint (except `/health`) requires:
```
X-API-Key: restaurant-secret-key-2025
```
Override in production via `API_KEY` env variable.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check, no auth |
| GET | `/orders/` | Paginated orders with full details |
| GET | `/orders/{order_id}` | Single order detail |
| GET | `/docs` | Swagger UI |

### Query Parameters for `/orders/`
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 10 | Results per page (max 100) |
| `order_status` | str | - | Filter e.g. `Completed` |
| `payment_status` | str | - | Filter e.g. `Refunded` |

## Database Schema

```
menus (menu_id, menu_name)
  └── categories (cat_id, category_name, menu_id)
        └── menu_items (item_id, item_name, cat_id, menu_id)
              ├── item_sizes (id, item_id, size, price)
              └── order_items (id, order_id, item_id, size, price, qty, total)
                    └── orders (order_id, order_date, order_status)
                          └── payments (id, payment_id, order_id, amount_due,
                                        tips, discount, total_paid,
                                        payment_type, payment_status)
```

## Key Design Decisions:

1. **price stored in order_items** — not FK to item_sizes.
   Orders capture price-at-time-of-order; menu prices can change.

2. **item_sizes table** — separated from menu_items because items can have
   0, 1 or 2 size variants. Avoids nullable columns on the main item row.

3. **NUMERIC(10,4)** for all money — avoids float rounding errors that exist
   in the raw data (e.g. 2.75636, 5.5131).

4. **Split payments** — the payments table has a many-to-one relationship
   with orders. payment_summary is computed at the API layer.

5. **joinedload()** — prevents N+1 query problem; all related data fetched
   in one round-trip.

6. **Pagination** — all list endpoints are paginated. No unbounded queries.

7. **GZip middleware** — compresses responses > 500 bytes automatically.

8. **X-Process-Time header** — visible in Postman, shows response latency.

## Data Anomalies Found (Task 1)

- Item5 (Soft Drinks category) mapped to Menu 1 (Food) — inconsistency
- Order 14, rows 18+20: Item1 Large appears twice with different prices
- Row ID 40 missing in Order History (deleted line item)
- Payment IDs 112-114, 117-118 missing (voided payments?)
- Price precision varies (2.75636 etc.) — should be normalised
- Menu prices ≠ order prices (expected — prices change over time)
- Order 15 payment is Refunded
