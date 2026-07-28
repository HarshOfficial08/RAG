"""SQLite persistence for users, document metadata, and the audit log.

A plain in-memory dict doesn't survive a process restart — which uvicorn's
--reload flag triggers on every code change — so anything meant to look like
a working app needs this on disk, not just held in Python module state.
Vector data itself lives in Qdrant (a separate, already-persistent service);
this module only covers the bookkeeping around it.
"""

import sqlite3
from pathlib import Path

from app.config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    user_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    tenant_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin',
    name TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    pii_masked INTEGER NOT NULL,
    failure_reason TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    question TEXT NOT NULL,
    masking_triggered INTEGER NOT NULL,
    timestamp TEXT NOT NULL
);
"""


def _migrate(conn: sqlite3.Connection) -> None:
    # CREATE TABLE IF NOT EXISTS doesn't retroactively add columns to a
    # database file created before this column existed — add it if missing.
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)")}
    if "role" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'admin'")
        conn.commit()
    if "name" not in columns:
        # Can't express "email's local-part" as a column DEFAULT, so add the
        # column empty and backfill it in a second pass — same effect as if
        # every pre-existing account had signed up without giving a name.
        conn.execute("ALTER TABLE users ADD COLUMN name TEXT NOT NULL DEFAULT ''")
        conn.execute(
            "UPDATE users SET name = substr(email, 1, instr(email, '@') - 1) WHERE name = ''"
        )
        conn.commit()


def get_connection() -> sqlite3.Connection:
    path = settings.database_path
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    _migrate(conn)
    return conn
