"""User model - lookup and upsert by Google ID."""


def row_to_dict(row) -> dict | None:
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


def get_by_google_id(conn, google_id: str) -> dict | None:
    cur = conn.execute("SELECT * FROM users WHERE google_id = ?", (google_id,))
    return row_to_dict(cur.fetchone())


def get_by_id(conn, user_id: int) -> dict | None:
    cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return row_to_dict(cur.fetchone())


def upsert(conn, google_id: str, email: str, name: str = "") -> dict:
    """Create or update user by Google ID. Returns user dict."""
    existing = get_by_google_id(conn, google_id)
    if existing:
        conn.execute(
            "UPDATE users SET email = ?, name = ?, created_at = created_at WHERE id = ?",
            (email, name or "", existing["id"]),
        )
        conn.commit()
        return get_by_id(conn, existing["id"])
    cur = conn.execute(
        "INSERT INTO users (google_id, email, name) VALUES (?, ?, ?)",
        (google_id, email, name or ""),
    )
    conn.commit()
    return get_by_id(conn, cur.lastrowid)
