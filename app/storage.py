"""SQLite-backed storage for change-detection state."""

import sqlite3


def get_connection(database_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS watched_sources (
            source_id TEXT PRIMARY KEY,
            content_hash TEXT NOT NULL,
            checked_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
