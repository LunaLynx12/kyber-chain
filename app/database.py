from typing import Optional
import sqlite3
import hashlib

DATABASE = "../database.db"


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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS miners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            FOREIGN KEY(user_name) REFERENCES users(name) ON DELETE CASCADE
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



def add_miner(user_name: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Check if user exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE name = ?", (user_name,))
    if cursor.fetchone()[0] == 0:
        raise ValueError("User does not exist")
    # Check if user is already a miner
    cursor.execute("SELECT COUNT(*) FROM miners WHERE user_name = ?", (user_name,))
    if cursor.fetchone()[0] > 0:
        raise ValueError("User is already a miner")
    cursor.execute("INSERT INTO miners (user_name) VALUES (?)", (user_name,))
    conn.commit()
    conn.close()

def get_all_miners() -> list:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_name FROM miners")
    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]