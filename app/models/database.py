"""Database setup using built-in sqlite3 (Python 3.14 compatible)."""
import sqlite3
from app.config import DB_PATH


def get_connection():
    """Get a new connection (check_same_thread=False for FastAPI async/threading)."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create database tables and seed pre-built trainings if empty."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                name TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trainings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                standard TEXT NOT NULL,
                category TEXT DEFAULT '',
                format TEXT DEFAULT 'standard',
                topics TEXT DEFAULT '',
                status TEXT DEFAULT 'planned',
                slides_url TEXT DEFAULT '',
                slides_presentation_id TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        # Add user_id to existing trainings if missing (migration)
        try:
            conn.execute("ALTER TABLE trainings ADD COLUMN user_id INTEGER REFERENCES users(id)")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE trainings ADD COLUMN category TEXT DEFAULT ''")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE trainings ADD COLUMN format TEXT DEFAULT 'standard'")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE trainings ADD COLUMN covered_at TEXT DEFAULT NULL")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        from app.seed_trainings import seed_trainings
        seed_trainings(conn)
    finally:
        conn.close()


def get_db():
    """FastAPI dependency - provide database connection."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
