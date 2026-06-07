from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class PaymentType(str, enum.Enum):
    CARD = "Card"
    CASH = "Cash"


class PaymentStatus(str, enum.Enum):
    COMPLETED = "Completed"
    REFUNDED = "Refunded"
    VOIDED = "Voided"


class OrderStatus(str, enum.Enum):
    COMPLETED = "Completed"
    PENDING = "Pending"
    CANCELLED = "Cancelled"


# ── Menu ─────────────────────────────────────────────────────────────────────

class Menu(Base):
    __tablename__ = "menus"

    menu_id   = Column(Integer, primary_key=True, index=True)
    menu_name = Column(String(100), nullable=False)

    categories = relationship("Category", back_populates="menu")


class Category(Base):
    __tablename__ = "categories"

    cat_id        = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), nullable=False)
    menu_id       = Column(Integer, ForeignKey("menus.menu_id"), nullable=False)

    menu  = relationship("Menu", back_populates="categories")
    items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"

    item_id   = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False)
    cat_id    = Column(Integer, ForeignKey("categories.cat_id"), nullable=False)
    menu_id   = Column(Integer, ForeignKey("menus.menu_id"), nullable=False)

    category    = relationship("Category", back_populates="items")
    menu        = relationship("Menu")
    sizes       = relationship("ItemSize", back_populates="item")
    order_items = relationship("OrderItem", back_populates="menu_item")


class ItemSize(Base):
    """Stores size variants for items that have Small / Large options."""
    __tablename__ = "item_sizes"

    id      = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("menu_items.item_id"), nullable=False)
    size    = Column(String(20), nullable=False)       # "Small" | "Large" | "Regular"
    price   = Column(Numeric(10, 4), nullable=False)

    item = relationship("MenuItem", back_populates="sizes")


# ── Orders ───────────────────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    order_id     = Column(Integer, primary_key=True, index=True)
    order_date   = Column(Date, nullable=False, index=True)        # ← index: filter by date
    order_status = Column(String(20), nullable=False, default="Completed", index=True)  # ← index: filter by status

    items    = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment",   back_populates="order")


class OrderItem(Base):
    """One row per item-line in an order — mirrors the Order History sheet."""
    __tablename__ = "order_items"

    id       = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False, index=True)  # ← index: join
    item_id  = Column(Integer, ForeignKey("menu_items.item_id"), nullable=False, index=True)
    size     = Column(String(20), nullable=True)           # NULL for fixed-price items
    price    = Column(Numeric(10, 4), nullable=False)      # price-at-time-of-order
    qty      = Column(Integer, nullable=False, default=1)
    total    = Column(Numeric(10, 4), nullable=False)      # price * qty, pre-computed

    order     = relationship("Order",    back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")


# ── Payments ─────────────────────────────────────────────────────────────────

class Payment(Base):
    __tablename__ = "payments"

    id             = Column(Integer, primary_key=True, index=True)
    payment_id     = Column(Integer, unique=True, nullable=False, index=True)
    payment_date   = Column(Date, nullable=False)
    order_id       = Column(Integer, ForeignKey("orders.order_id"), nullable=False, index=True)  # ← index: join
    amount_due     = Column(Numeric(10, 4), nullable=False)
    tips           = Column(Numeric(10, 4), nullable=False, default=0)
    discount       = Column(Numeric(10, 4), nullable=False, default=0)
    total_paid     = Column(Numeric(10, 4), nullable=False)
    payment_type   = Column(String(10), nullable=False)           # Card | Cash
    payment_status = Column(String(20), nullable=False, index=True)  # ← index: filter by status

    order = relationship("Order", back_populates="payments")


# ── Composite index: filter orders by date + status together ─────────────────
Index("ix_orders_date_status", Order.order_date, Order.order_status)
