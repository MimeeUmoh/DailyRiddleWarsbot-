import sqlite3
from contextlib import closing

DB_PATH = "app_data.db"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    chat_id INTEGER NOT NULL,
                    email TEXT,
                    premium INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    reference TEXT PRIMARY KEY,
                    user_id INTEGER,
                    amount INTEGER,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

def add_user(user_id, chat_id, email=None):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("""
                INSERT OR IGNORE INTO users (user_id, chat_id, email) VALUES (?, ?, ?)
            """, (user_id, chat_id, email))

def set_user_premium(user_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("UPDATE users SET premium=1 WHERE user_id=?", (user_id,))

def get_user(user_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id, chat_id, email, premium FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        if row:
            return {
                "user_id": row[0],
                "chat_id": row[1],
                "email": row[2],
                "premium": bool(row[3]),
            }
        return None

def add_payment(reference, user_id, amount, status):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("""
                INSERT OR IGNORE INTO payments (reference, user_id, amount, status) VALUES (?, ?, ?, ?)
            """, (reference, user_id, amount, status))
