"""
seed.py — Populates the DB with data from the assessment spreadsheet.
Run once: python seed.py
"""

from datetime import date
from app.db.database import engine, SessionLocal
from app.models.models import Base, Menu, Category, MenuItem, ItemSize, Order, OrderItem, Payment


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── Menus ──────────────────────────────────────────────────────────
        menus = [
            Menu(menu_id=1, menu_name="Food"),
            Menu(menu_id=2, menu_name="Drinks"),
        ]
        db.add_all(menus)

        # ── Categories ─────────────────────────────────────────────────────
        # NOTE: Cat 2 (Soft Drinks) belongs to Menu 2 but Item5 under it
        # is mapped to Menu 1 in the source data — flagged as an anomaly.
        categories = [
            Category(cat_id=1, category_name="Starters",   menu_id=1),
            Category(cat_id=2, category_name="Soft Drinks", menu_id=2),
            Category(cat_id=3, category_name="Mains",      menu_id=1),
            Category(cat_id=4, category_name="Desserts",   menu_id=2),
            Category(cat_id=5, category_name="Hot Drinks", menu_id=2),
        ]
        db.add_all(categories)

        # ── Menu Items ─────────────────────────────────────────────────────
        items = [
            MenuItem(item_id=1,  item_name="Item1",  cat_id=1, menu_id=1),
            MenuItem(item_id=2,  item_name="Item2",  cat_id=1, menu_id=1),
            MenuItem(item_id=3,  item_name="Item3",  cat_id=2, menu_id=2),
            MenuItem(item_id=4,  item_name="Item4",  cat_id=2, menu_id=2),
            MenuItem(item_id=5,  item_name="Item5",  cat_id=2, menu_id=1),  # anomaly: Soft Drinks in Food menu
            MenuItem(item_id=6,  item_name="Item6",  cat_id=3, menu_id=1),
            MenuItem(item_id=7,  item_name="Item7",  cat_id=3, menu_id=1),
            MenuItem(item_id=8,  item_name="Item8",  cat_id=4, menu_id=2),
            MenuItem(item_id=9,  item_name="Item9",  cat_id=4, menu_id=2),
            MenuItem(item_id=10, item_name="Item10", cat_id=5, menu_id=2),
        ]
        db.add_all(items)

        # ── Item Sizes (only for sized items: 1, 6, 8) ─────────────────────
        sizes = [
            ItemSize(item_id=1, size="Small", price=1.50),
            ItemSize(item_id=1, size="Large", price=2.50),
            ItemSize(item_id=2, size="Regular", price=3.00),   # no size = single-size
            ItemSize(item_id=3, size="Regular", price=2.50),
            ItemSize(item_id=4, size="Regular", price=1.50),
            ItemSize(item_id=5, size="Regular", price=1.00),
            ItemSize(item_id=6, size="Small",   price=2.50),
            ItemSize(item_id=6, size="Large",   price=3.60),
            ItemSize(item_id=7, size="Regular", price=2.50),
            ItemSize(item_id=8, size="Small",   price=3.75),
            ItemSize(item_id=8, size="Large",   price=6.50),
            ItemSize(item_id=9, size="Regular", price=1.50),
            ItemSize(item_id=10, size="Regular", price=2.00),
        ]
        db.add_all(sizes)

        # ── Orders ─────────────────────────────────────────────────────────
        orders = [
            Order(order_id=10, order_date=date(2025, 10, 1), order_status="Completed"),
            Order(order_id=11, order_date=date(2025, 10, 1), order_status="Completed"),
            Order(order_id=12, order_date=date(2025, 10, 1), order_status="Completed"),
            Order(order_id=13, order_date=date(2025, 10, 1), order_status="Completed"),
            Order(order_id=14, order_date=date(2025, 10, 1), order_status="Completed"),
            Order(order_id=15, order_date=date(2025, 10, 2), order_status="Completed"),
            Order(order_id=16, order_date=date(2025, 10, 3), order_status="Completed"),
            Order(order_id=17, order_date=date(2025, 10, 1), order_status="Completed"),
            Order(order_id=18, order_date=date(2025, 10, 5), order_status="Completed"),
            Order(order_id=19, order_date=date(2025, 10, 1), order_status="Completed"),
            Order(order_id=20, order_date=date(2025, 10, 1), order_status="Completed"),
        ]
        db.add_all(orders)

        # ── Order Items (from Order History sheet) ──────────────────────────
        order_items = [
            # Order 10
            OrderItem(id=1,  order_id=10, item_id=2,  size=None,    price=2.5,      qty=1, total=2.5),
            OrderItem(id=2,  order_id=10, item_id=3,  size=None,    price=1.5,      qty=2, total=3.0),
            OrderItem(id=3,  order_id=10, item_id=1,  size="Small", price=3.75,     qty=1, total=3.75),
            # Order 11
            OrderItem(id=4,  order_id=11, item_id=5,  size=None,    price=2.75,     qty=1, total=2.75),
            OrderItem(id=5,  order_id=11, item_id=6,  size=None,    price=1.75,     qty=2, total=3.5),
            OrderItem(id=6,  order_id=11, item_id=2,  size=None,    price=2.5,      qty=1, total=2.5),
            OrderItem(id=7,  order_id=11, item_id=3,  size=None,    price=3.5,      qty=1, total=3.5),
            OrderItem(id=8,  order_id=11, item_id=4,  size=None,    price=3.75,     qty=2, total=7.5),
            OrderItem(id=9,  order_id=11, item_id=5,  size=None,    price=1.5,      qty=1, total=1.5),
            # Order 12
            OrderItem(id=10, order_id=12, item_id=6,  size="Large", price=5.5,      qty=2, total=11.0),
            OrderItem(id=11, order_id=12, item_id=7,  size=None,    price=2.5,      qty=1, total=2.5),
            OrderItem(id=12, order_id=12, item_id=1,  size="Large", price=3.5,      qty=1, total=3.5),
            # Order 13
            OrderItem(id=13, order_id=13, item_id=1,  size="Small", price=2.75,     qty=2, total=5.5),
            OrderItem(id=14, order_id=13, item_id=6,  size="Small", price=1.5,      qty=1, total=1.5),
            OrderItem(id=15, order_id=13, item_id=8,  size="Small", price=3.5,      qty=1, total=3.5),
            OrderItem(id=16, order_id=13, item_id=1,  size="Small", price=2.5,      qty=2, total=5.0),
            # Order 14
            OrderItem(id=17, order_id=14, item_id=6,  size="Large", price=2.75,     qty=1, total=2.75),
            OrderItem(id=18, order_id=14, item_id=1,  size="Large", price=2.75655,  qty=2, total=5.5131),
            OrderItem(id=19, order_id=14, item_id=8,  size="Large", price=2.75,     qty=2, total=5.5),
            OrderItem(id=20, order_id=14, item_id=1,  size="Large", price=2.7556,   qty=2, total=5.5112),  # duplicate item_id — data anomaly
            OrderItem(id=21, order_id=14, item_id=4,  size=None,    price=5.5,      qty=1, total=5.5),
            OrderItem(id=22, order_id=14, item_id=3,  size=None,    price=2.75,     qty=2, total=5.5),
            OrderItem(id=23, order_id=14, item_id=2,  size=None,    price=3.5,      qty=1, total=3.5),
            OrderItem(id=24, order_id=14, item_id=6,  size="Large", price=3.015,    qty=3, total=9.045),
            # Order 15
            OrderItem(id=25, order_id=15, item_id=2,  size=None,    price=2.568,    qty=2, total=5.136),
            # Order 16
            OrderItem(id=26, order_id=16, item_id=6,  size="Large", price=6.586,    qty=3, total=19.758),
            # Order 17
            OrderItem(id=27, order_id=17, item_id=10, size=None,    price=2.5,      qty=1, total=2.5),
            OrderItem(id=28, order_id=17, item_id=9,  size=None,    price=2.75636,  qty=1, total=2.75636),
            OrderItem(id=29, order_id=17, item_id=7,  size=None,    price=5.63982,  qty=1, total=5.63982),
            # Order 18
            OrderItem(id=30, order_id=18, item_id=1,  size="Small", price=2.5698,   qty=2, total=5.1396),
            OrderItem(id=31, order_id=18, item_id=6,  size="Small", price=5.36245,  qty=2, total=10.7249),
            OrderItem(id=32, order_id=18, item_id=8,  size="Small", price=5.23569,  qty=2, total=10.47138),
            # Order 19
            OrderItem(id=33, order_id=19, item_id=2,  size=None,    price=2.75698,  qty=1, total=2.75698),
            OrderItem(id=34, order_id=19, item_id=4,  size=None,    price=2.3561,   qty=1, total=2.356),
            OrderItem(id=35, order_id=19, item_id=5,  size=None,    price=2.457,    qty=2, total=4.914),
            OrderItem(id=36, order_id=19, item_id=7,  size=None,    price=2.6359,   qty=1, total=2.6359),
            OrderItem(id=37, order_id=19, item_id=9,  size=None,    price=6.523,    qty=1, total=6.523),
            OrderItem(id=38, order_id=19, item_id=10, size=None,    price=8.5412,   qty=3, total=25.6236),
            OrderItem(id=39, order_id=19, item_id=6,  size="Large", price=5.683,    qty=2, total=11.366),
            # id=40 missing in source data (deleted row)
            OrderItem(id=41, order_id=19, item_id=2,  size=None,    price=6.3564,   qty=1, total=6.3564),
            OrderItem(id=42, order_id=19, item_id=5,  size=None,    price=7.235,    qty=1, total=7.235),
            OrderItem(id=43, order_id=19, item_id=7,  size=None,    price=2.365,    qty=1, total=2.365),
            # Order 20
            OrderItem(id=44, order_id=20, item_id=1,  size="Large", price=2.3658,   qty=1, total=2.3658),
            OrderItem(id=45, order_id=20, item_id=3,  size=None,    price=2.356,    qty=1, total=2.356),
            OrderItem(id=46, order_id=20, item_id=6,  size="Large", price=1.256,    qty=1, total=1.256),
            OrderItem(id=47, order_id=20, item_id=4,  size=None,    price=2.635,    qty=1, total=2.635),
            OrderItem(id=48, order_id=20, item_id=5,  size=None,    price=5.21,     qty=1, total=5.21),
            OrderItem(id=49, order_id=20, item_id=7,  size=None,    price=6.325,    qty=2, total=12.65),
            OrderItem(id=50, order_id=20, item_id=8,  size="Small", price=7.2514,   qty=1, total=7.2514),
            OrderItem(id=51, order_id=20, item_id=9,  size=None,    price=2.3999,   qty=1, total=2.3999),
            OrderItem(id=52, order_id=20, item_id=4,  size=None,    price=2.356,    qty=3, total=7.068),
            OrderItem(id=53, order_id=20, item_id=6,  size="Small", price=4.5326,   qty=2, total=9.0652),
        ]
        db.add_all(order_items)

        # ── Payments ───────────────────────────────────────────────────────
        payments = [
            Payment(id=1,  payment_id=100, payment_date=date(2025,10,1), order_id=10, amount_due=9.25,     tips=0, discount=0, total_paid=9.25,  payment_type="Card", payment_status="Completed"),
            Payment(id=2,  payment_id=101, payment_date=date(2025,10,1), order_id=11, amount_due=21.25,    tips=0, discount=0, total_paid=10.0,  payment_type="Cash", payment_status="Completed"),
            Payment(id=3,  payment_id=102, payment_date=date(2025,10,1), order_id=11, amount_due=21.25,    tips=0, discount=0, total_paid=11.25, payment_type="Card", payment_status="Completed"),
            Payment(id=4,  payment_id=103, payment_date=date(2025,10,2), order_id=12, amount_due=17.0,     tips=3, discount=4, total_paid=16.0,  payment_type="Card", payment_status="Completed"),
            Payment(id=5,  payment_id=104, payment_date=date(2025,10,3), order_id=13, amount_due=15.5,     tips=0, discount=2, total_paid=13.5,  payment_type="Card", payment_status="Completed"),
            Payment(id=6,  payment_id=105, payment_date=date(2025,10,1), order_id=14, amount_due=42.8193,  tips=0, discount=0, total_paid=20.0,  payment_type="Cash", payment_status="Completed"),
            Payment(id=7,  payment_id=106, payment_date=date(2025,10,1), order_id=14, amount_due=42.8193,  tips=0, discount=0, total_paid=22.82, payment_type="Card", payment_status="Completed"),
            Payment(id=8,  payment_id=107, payment_date=date(2025,10,2), order_id=15, amount_due=5.136,    tips=0, discount=0, total_paid=5.14,  payment_type="Card", payment_status="Refunded"),
            Payment(id=9,  payment_id=108, payment_date=date(2025,10,3), order_id=16, amount_due=19.758,   tips=0, discount=0, total_paid=10.0,  payment_type="Cash", payment_status="Completed"),
            Payment(id=10, payment_id=109, payment_date=date(2025,10,3), order_id=16, amount_due=19.758,   tips=0, discount=0, total_paid=9.76,  payment_type="Card", payment_status="Completed"),
            Payment(id=11, payment_id=110, payment_date=date(2025,10,1), order_id=17, amount_due=10.8918,  tips=0, discount=0, total_paid=10.9,  payment_type="Card", payment_status="Completed"),
            Payment(id=12, payment_id=111, payment_date=date(2025,10,5), order_id=18, amount_due=26.33588, tips=2, discount=0, total_paid=25.0,  payment_type="Cash", payment_status="Completed"),
            Payment(id=13, payment_id=115, payment_date=date(2025,10,5), order_id=18, amount_due=26.33588, tips=0, discount=0, total_paid=3.34,  payment_type="Card", payment_status="Completed"),
            Payment(id=14, payment_id=116, payment_date=date(2025,10,1), order_id=19, amount_due=72.13188, tips=0, discount=0, total_paid=50.0,  payment_type="Cash", payment_status="Completed"),
            Payment(id=15, payment_id=119, payment_date=date(2025,10,1), order_id=19, amount_due=72.13188, tips=0, discount=0, total_paid=22.13, payment_type="Card", payment_status="Completed"),
            Payment(id=16, payment_id=120, payment_date=date(2025,10,1), order_id=20, amount_due=52.2573,  tips=0, discount=0, total_paid=25.0,  payment_type="Cash", payment_status="Completed"),
            Payment(id=17, payment_id=121, payment_date=date(2025,10,1), order_id=20, amount_due=52.2573,  tips=0, discount=0, total_paid=27.28, payment_type="Card", payment_status="Completed"),
        ]
        db.add_all(payments)

        db.commit()
        print("✅ Database seeded successfully.")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    seed()
