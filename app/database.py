from typing import Optional
import sqlite3
import hashlib

DATABASE = "users.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            name TEXT PRIMARY KEY,
            public_key BLOB NOT NULL,
            private_key BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_user(name: str, public_key: bytes, private_key: bytes):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, public_key, private_key) VALUES (?, ?, ?)",
            (name, public_key, private_key)
        )
        conn.commit()
    finally:
        conn.close()

def get_user_keys(name: str) -> Optional[dict]:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT public_key, private_key FROM users WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    public_key, private_key = row
    return {
        "public_key": public_key,
        "private_key": private_key
    }

def get_all_users() -> list:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users")
    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]

def get_user_by_address(address: str) -> Optional[dict]:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, public_key FROM users")
    rows = cursor.fetchall()
    conn.close()

    for name, public_key in rows:
        # Derive address from public_key
        public_key_hash = hashlib.sha256(public_key).digest()
        user_address = "0x" + public_key_hash.hex()[-40:]
        if user_address == address:
            return {
                "name": name,
                "public_key": public_key
            }

    return None