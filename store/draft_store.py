import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


MAX_STATE_BYTES = 128 * 1024
MAX_REVISIONS_PER_DRAFT = 20


def _db_path():
    configured = os.environ.get("DRAFT_DB_PATH")
    if configured:
        path = Path(configured)
    else:
        path = Path(__file__).resolve().parent / "instance" / "editor-drafts.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect():
    connection = sqlite3.connect(str(_db_path()), timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def init_draft_store():
    with _connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS editor_drafts (
                order_id TEXT NOT NULL,
                slug TEXT NOT NULL,
                revision INTEGER NOT NULL,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (order_id, slug)
            );

            CREATE TABLE IF NOT EXISTS editor_draft_revisions (
                order_id TEXT NOT NULL,
                slug TEXT NOT NULL,
                revision INTEGER NOT NULL,
                state_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (order_id, slug, revision)
            );
            """
        )


def _serialize_state(state):
    if not isinstance(state, dict):
        raise ValueError("Editor state must be an object")
    encoded = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > MAX_STATE_BYTES:
        raise ValueError("Editor state is too large")
    return encoded


def load_draft(order_id, slug):
    init_draft_store()
    with _connect() as db:
        row = db.execute(
            "SELECT revision, state_json, updated_at FROM editor_drafts WHERE order_id = ? AND slug = ?",
            (str(order_id), str(slug)),
        ).fetchone()
    if row is None:
        return None
    return {
        "revision": int(row["revision"]),
        "state": json.loads(row["state_json"]),
        "updated_at": row["updated_at"],
    }


def save_draft(order_id, slug, state):
    init_draft_store()
    order_id = str(order_id)
    slug = str(slug)
    encoded = _serialize_state(state)
    now = datetime.now(timezone.utc).isoformat()

    with _connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT revision FROM editor_drafts WHERE order_id = ? AND slug = ?",
            (order_id, slug),
        ).fetchone()
        revision = (int(row["revision"]) if row else 0) + 1

        db.execute(
            """
            INSERT INTO editor_drafts(order_id, slug, revision, state_json, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(order_id, slug) DO UPDATE SET
                revision = excluded.revision,
                state_json = excluded.state_json,
                updated_at = excluded.updated_at
            """,
            (order_id, slug, revision, encoded, now),
        )
        db.execute(
            """
            INSERT INTO editor_draft_revisions(order_id, slug, revision, state_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, slug, revision, encoded, now),
        )
        db.execute(
            """
            DELETE FROM editor_draft_revisions
            WHERE order_id = ? AND slug = ? AND revision NOT IN (
                SELECT revision FROM editor_draft_revisions
                WHERE order_id = ? AND slug = ?
                ORDER BY revision DESC
                LIMIT ?
            )
            """,
            (order_id, slug, order_id, slug, MAX_REVISIONS_PER_DRAFT),
        )
        db.commit()

    return {"revision": revision, "updated_at": now}


def list_draft_revisions(order_id, slug):
    init_draft_store()
    with _connect() as db:
        rows = db.execute(
            """
            SELECT revision, created_at
            FROM editor_draft_revisions
            WHERE order_id = ? AND slug = ?
            ORDER BY revision DESC
            """,
            (str(order_id), str(slug)),
        ).fetchall()
    return [
        {"revision": int(row["revision"]), "created_at": row["created_at"]}
        for row in rows
    ]


def restore_draft_revision(order_id, slug, revision):
    init_draft_store()
    with _connect() as db:
        row = db.execute(
            """
            SELECT state_json FROM editor_draft_revisions
            WHERE order_id = ? AND slug = ? AND revision = ?
            """,
            (str(order_id), str(slug), int(revision)),
        ).fetchone()
    if row is None:
        return None
    state = json.loads(row["state_json"])
    saved = save_draft(order_id, slug, state)
    return {"state": state, **saved}
