import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from app.config import config


def _ensure_db_dir():
    db_dir = os.path.dirname(config.DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)


@contextmanager
def get_conn():
    _ensure_db_dir()
    conn = sqlite3.connect(config.DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone_number)"
        )
        conn.commit()


def save_message(phone_number: str, role: str, content: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (phone_number, role, content, created_at) VALUES (?, ?, ?, ?)",
            (phone_number, role, content, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()


def get_history(phone_number: str, limit: int = 20):
    with get_conn() as conn:
        cursor = conn.execute(
            """
            SELECT role, content FROM messages
            WHERE phone_number = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (phone_number, limit),
        )
        rows = cursor.fetchall()
    return list(reversed(rows))
