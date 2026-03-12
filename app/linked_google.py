"""Store and retrieve linked Google credentials (server-side, encrypted)."""
import json
import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from app.config import DB_PATH, SECRET_KEY


def _get_fernet() -> Fernet:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"arborist_google", iterations=100_000)
    key = base64.urlsafe_b64encode(kdf.derive((SECRET_KEY or "dev").encode()))
    return Fernet(key)


def _get_conn():
    return sqlite3.connect(str(DB_PATH))


def init_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS linked_google (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            credentials_blob TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def save_credentials(creds_dict: dict) -> None:
    conn = _get_conn()
    try:
        init_table(conn)
        blob = _get_fernet().encrypt(json.dumps(creds_dict).encode()).decode()
        conn.execute(
            """INSERT INTO linked_google (id, credentials_blob, updated_at) VALUES (1, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(id) DO UPDATE SET credentials_blob = ?, updated_at = CURRENT_TIMESTAMP""",
            (blob, blob),
        )
        conn.commit()
    finally:
        conn.close()


def get_credentials() -> dict | None:
    conn = _get_conn()
    try:
        init_table(conn)
        cur = conn.execute("SELECT credentials_blob FROM linked_google WHERE id = 1")
        row = cur.fetchone()
        if not row:
            return None
        data = _get_fernet().decrypt(row[0].encode()).decode()
        return json.loads(data)
    except Exception:
        return None
    finally:
        conn.close()


def is_linked() -> bool:
    return get_credentials() is not None
