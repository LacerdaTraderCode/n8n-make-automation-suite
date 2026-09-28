"""Business logic behind the /api/changes/check endpoint.

n8n polls a page on a schedule and forwards its raw content here. A no-code
tool can fetch a page easily, but deciding "did this meaningfully change
since last time" needs state across runs — that is the part that actually
needs real code instead of a node's configuration.
"""

import hashlib
import sqlite3
from datetime import datetime, timezone


def check_for_change(connection: sqlite3.Connection, source_id: str, content: str) -> dict:
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    checked_at = datetime.now(timezone.utc).isoformat()

    existing = connection.execute(
        "SELECT content_hash FROM watched_sources WHERE source_id = ?", (source_id,)
    ).fetchone()

    changed = existing is None or existing["content_hash"] != content_hash

    connection.execute(
        """
        INSERT INTO watched_sources (source_id, content_hash, checked_at)
        VALUES (?, ?, ?)
        ON CONFLICT(source_id) DO UPDATE SET
            content_hash = excluded.content_hash,
            checked_at = excluded.checked_at
        """,
        (source_id, content_hash, checked_at),
    )
    connection.commit()

    return {
        "source_id": source_id,
        "changed": changed,
        "checked_at": checked_at,
        "content_length": len(content),
    }
