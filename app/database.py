import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from app.logger import setup_logging

setup_logging()
logger=logging.getLogger(__name__)
DB_PATH=Path("data/orders.db")

def init_db():
    """جدول لازم در صورت نبود می سازد. باید در ابتدای main.py صدا زده شود"""
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_orders (
                order_id INTEGER PRIMARY KEY,
                status TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_status_at TEXT NOT NULL 
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


def get_seen_order_ids() -> set[int]:
    with get_connection() as conn:
        rows=conn.execute("SELECT order_id FROM seen_orders").fetchall()
    return {row[0] for row in rows}

def get_order_status(order_id: int) -> str | None:
    with get_connection() as conn:
        row=conn.execute("SELECT status FROM seen_orders WHERE order_id = ?",(order_id,)).fetchone()
    return row[0] if row else None

def mark_order_seen(order_id: int, status: str):
    """یک سفارش را جدید ثبت می کند یا وضعیتش را به روزرسانی می کند"""
    now=datetime.now().isoformat()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO seen_orders (order_id, status, first_seen_at, last_status_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                status=excluded.status,
                last_status_at=excluded.status
            """,
            (order_id, status, now, now),
        )