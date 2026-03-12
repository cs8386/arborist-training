"""Training model for tracking arboriculture trainings (sqlite3, no SQLAlchemy)."""


def row_to_dict(row) -> dict | None:
    """Convert sqlite3.Row to dict."""
    if row is None:
        return None
    d = {k: row[k] for k in row.keys()}
    topics = d.get("topics") or ""
    d["topics"] = [t.strip() for t in (topics or "").split(",") if t.strip()]
    return d


def get_all(conn, order_by=None):
    """Get all trainings, ordered by standard, category, title."""
    if order_by is None:
        order_by = "standard, category, title"
    cur = conn.execute(f"SELECT * FROM trainings ORDER BY {order_by}")
    return [row_to_dict(r) for r in cur.fetchall()]


def get_by_id(conn, training_id: int) -> dict | None:
    """Get a single training by ID."""
    cur = conn.execute("SELECT * FROM trainings WHERE id = ?", (training_id,))
    return row_to_dict(cur.fetchone())


def create(conn, title: str, description: str, standard: str, topics: str, category: str = "", format: str = "standard") -> dict:
    """Create a new training."""
    cur = conn.execute(
        """INSERT INTO trainings (title, description, standard, category, format, topics)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, description, standard, category or "", format or "standard", topics),
    )
    conn.commit()
    return get_by_id(conn, cur.lastrowid)


def update(conn, training_id: int, **kwargs) -> dict | None:
    """Update a training. Pass only fields to update: title=, description=, status=, covered_at=."""
    allowed = {"title", "description", "category", "format", "status", "slides_url", "slides_presentation_id", "covered_at"}
    nullable = {"covered_at"}  # these fields can be explicitly set to None
    updates = {k: v for k, v in kwargs.items() if k in allowed and (v is not None or k in nullable)}
    if not updates:
        return get_by_id(conn, training_id)
    sets = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [training_id]
    conn.execute(f"UPDATE trainings SET {sets}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", vals)
    conn.commit()
    return get_by_id(conn, training_id)


def delete(conn, training_id: int) -> bool:
    """Delete a training. Returns True if deleted."""
    cur = conn.execute("DELETE FROM trainings WHERE id = ?", (training_id,))
    conn.commit()
    return cur.rowcount > 0
