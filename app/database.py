import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from app.logger import setup_logging
from app.processor import Order
from decimal import Decimal

setup_logging()
logger=logging.getLogger(__name__)
DB_PATH=Path("data/orders.db")

def init_db():
    """جدول لازم در صورت نبود می سازد. باید در ابتدای main.py صدا زده شود"""
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                shipping_address TEXT NOT NULL,
                product TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total TEXT NOT NULL,
                status TEXT NOT NULL,
                order_date TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_updated_at TEXT NOT NULL
            )
            """
        )
    logger.info(f"Database initialized at {DB_PATH}")

@contextmanager
def get_connection():
    conn=sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# def get_seen_order_ids() -> set[int]:
#     with get_connection() as conn:
#         rows=conn.execute("SELECT order_id FROM seen_orders").fetchall()
#     return {row[0] for row in rows}

def get_order_status(order_id: int) -> str | None:
    with get_connection() as conn:
        row=conn.execute("SELECT status FROM orders WHERE id = ?",(order_id,)).fetchone()
    return row[0] if row else None

# def mark_order_seen(order_id: int, status: str):
#     """یک سفارش را جدید ثبت می کند یا وضعیتش را به روزرسانی می کند"""
#     now=datetime.now().isoformat()

#     with get_connection() as conn:
#         conn.execute(
#             """
#             INSERT INTO seen_orders (order_id, status, first_seen_at, last_status_at)
#             VALUES (?, ?, ?, ?)
#             ON CONFLICT(order_id) DO UPDATE SET
#                 status=excluded.status,
#                 last_status_at=excluded.status
#             """,
#             (order_id, status, now, now),
#         )

def upsert_order(order:Order):
    now=datetime.now().isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO orders (
            id, customer, customer_email, shipping_address,
            product, product_id, quantity, total, status,
            order_date, first_seen_at, last_updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                status = excluded.status,
                quantity = excluded.quantity,
                total = excluded.total,
                last_updated_at = excluded.last_updated_at
            """,
            (
                order.id,
                order.customer,
                order.customer_email,
                order.shipping_address,
                order.product,
                order.product_id,
                order.quantity,
                str(order.total),
                order.status.value,
                order.date.isoformat(),
                now,
                now,
            )
        )

def get_orders_count() -> int:

    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) FROM orders").fetchone()
    return row[0]

def get_total_sales() -> Decimal:

    with get_connection() as conn:
        row= conn.execute(
            "SELECT total FROM orders WHERE  status != 'cancelled'"
        ).fetchall()
    return sum((Decimal(r[0]) for r in row),Decimal("0"))