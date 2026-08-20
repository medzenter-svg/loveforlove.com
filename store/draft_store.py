import json
import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, text


MAX_STATE_BYTES = 128 * 1024
MAX_REVISIONS_PER_DRAFT = 20
_ENGINE_CACHE = {}
DRAFT_REVISION_KEY = "__draft_expected_revision"


class DraftConflictError(ValueError):
    def __init__(self, current_revision):
        self.current_revision = int(current_revision)
        super().__init__(
            f"A newer saved version exists (version {self.current_revision}). Reload the latest version before saving again."
        )


def _database_url():
    raw = str(os.environ.get("DATABASE_URL") or "").strip()
    if raw:
        if raw.startswith("postgres://"):
            raw = "postgresql+psycopg://" + raw[len("postgres://"):]
        elif raw.startswith("postgresql://"):
            raw = "postgresql+psycopg://" + raw[len("postgresql://"):]
        return raw

    configured = os.environ.get("DRAFT_DB_PATH")
    if configured:
        path = Path(configured)
    else:
        path = Path(__file__).resolve().parent / "instance" / "editor-drafts.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    return "sqlite+pysqlite:///" + str(path)


def draft_storage_mode():
    url = _database_url()
    if url.startswith("postgresql+"):
        return "postgresql"
    if url.startswith("sqlite+"):
        return "sqlite"
    return "other"


def production_draft_storage_ready():
    return draft_storage_mode() == "postgresql" and bool(os.environ.get("DATABASE_URL"))


def _engine():
    url = _database_url()
    engine = _ENGINE_CACHE.get(url)
    if engine is None:
        kwargs = {"pool_pre_ping": True}
        if url.startswith("sqlite+"):
            kwargs["connect_args"] = {"check_same_thread": False, "timeout": 10}
        engine = create_engine(url, future=True, **kwargs)
        _ENGINE_CACHE[url] = engine
    return engine


def init_draft_store():
    statements = [
        """
        CREATE TABLE IF NOT EXISTS editor_drafts (
            order_id TEXT NOT NULL,
            slug TEXT NOT NULL,
            revision INTEGER NOT NULL,
            state_json TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (order_id, slug)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS editor_draft_revisions (
            order_id TEXT NOT NULL,
            slug TEXT NOT NULL,
            revision INTEGER NOT NULL,
            state_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (order_id, slug, revision)
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_editor_draft_revisions_lookup
        ON editor_draft_revisions(order_id, slug, revision DESC)
        """,
    ]
    with _engine().begin() as db:
        for statement in statements:
            db.execute(text(statement))


def draft_store_healthcheck():
    init_draft_store()
    with _engine().connect() as db:
        db.execute(text("SELECT 1"))
    return {"ok": True, "mode": draft_storage_mode()}


def _prepare_state(state):
    if not isinstance(state, dict):
        raise ValueError("Editor state must be an object")
    cleaned = dict(state)
    expected_revision = cleaned.pop(DRAFT_REVISION_KEY, None)
    if expected_revision in ("", None):
        expected_revision = None
    else:
        try:
            expected_revision = int(expected_revision)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid draft revision") from exc
        if expected_revision < 0:
            raise ValueError("Invalid draft revision")
    return cleaned, expected_revision


def _serialize_state(state):
    encoded = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > MAX_STATE_BYTES:
        raise ValueError("Editor state is too large")
    return encoded


def load_draft(order_id, slug):
    init_draft_store()
    with _engine().connect() as db:
        row = db.execute(
            text(
                "SELECT revision, state_json, updated_at "
                "FROM editor_drafts WHERE order_id = :order_id AND slug = :slug"
            ),
            {"order_id": str(order_id), "slug": str(slug)},
        ).mappings().first()
    if row is None:
        return None
    return {
        "revision": int(row["revision"]),
        "state": json.loads(row["state_json"]),
        "updated_at": row["updated_at"],
    }


def _lock_order_draft(db, order_id, slug):
    if db.dialect.name == "postgresql":
        db.execute(
            text("SELECT pg_advisory_xact_lock(hashtext(:lock_key))"),
            {"lock_key": f"loveforlove-draft:{order_id}:{slug}"},
        )


def save_draft(order_id, slug, state):
    init_draft_store()
    order_id = str(order_id)
    slug = str(slug)
    cleaned_state, expected_revision = _prepare_state(state)
    encoded = _serialize_state(cleaned_state)
    now = datetime.now(timezone.utc).isoformat()

    with _engine().begin() as db:
        _lock_order_draft(db, order_id, slug)
        row = db.execute(
            text(
                "SELECT revision FROM editor_drafts "
                "WHERE order_id = :order_id AND slug = :slug"
            ),
            {"order_id": order_id, "slug": slug},
        ).mappings().first()
        current_revision = int(row["revision"]) if row else 0

        if expected_revision is not None and expected_revision != current_revision:
            raise DraftConflictError(current_revision)

        revision = current_revision + 1
        if row:
            db.execute(
                text(
                    "UPDATE editor_drafts SET revision = :revision, state_json = :state_json, "
                    "updated_at = :updated_at WHERE order_id = :order_id AND slug = :slug"
                ),
                {
                    "revision": revision,
                    "state_json": encoded,
                    "updated_at": now,
                    "order_id": order_id,
                    "slug": slug,
                },
            )
        else:
            db.execute(
                text(
                    "INSERT INTO editor_drafts(order_id, slug, revision, state_json, updated_at) "
                    "VALUES (:order_id, :slug, :revision, :state_json, :updated_at)"
                ),
                {
                    "order_id": order_id,
                    "slug": slug,
                    "revision": revision,
                    "state_json": encoded,
                    "updated_at": now,
                },
            )

        db.execute(
            text(
                "INSERT INTO editor_draft_revisions(order_id, slug, revision, state_json, created_at) "
                "VALUES (:order_id, :slug, :revision, :state_json, :created_at)"
            ),
            {
                "order_id": order_id,
                "slug": slug,
                "revision": revision,
                "state_json": encoded,
                "created_at": now,
            },
        )

        cutoff = revision - MAX_REVISIONS_PER_DRAFT
        if cutoff > 0:
            db.execute(
                text(
                    "DELETE FROM editor_draft_revisions "
                    "WHERE order_id = :order_id AND slug = :slug AND revision <= :cutoff"
                ),
                {"order_id": order_id, "slug": slug, "cutoff": cutoff},
            )

    return {"revision": revision, "updated_at": now}


def list_draft_revisions(order_id, slug):
    init_draft_store()
    with _engine().connect() as db:
        rows = db.execute(
            text(
                "SELECT revision, created_at FROM editor_draft_revisions "
                "WHERE order_id = :order_id AND slug = :slug ORDER BY revision DESC"
            ),
            {"order_id": str(order_id), "slug": str(slug)},
        ).mappings().all()
    return [
        {"revision": int(row["revision"]), "created_at": row["created_at"]}
        for row in rows
    ]


def restore_draft_revision(order_id, slug, revision):
    init_draft_store()
    with _engine().connect() as db:
        row = db.execute(
            text(
                "SELECT state_json FROM editor_draft_revisions "
                "WHERE order_id = :order_id AND slug = :slug AND revision = :revision"
            ),
            {
                "order_id": str(order_id),
                "slug": str(slug),
                "revision": int(revision),
            },
        ).mappings().first()
    if row is None:
        return None
    state = json.loads(row["state_json"])
    saved = save_draft(order_id, slug, state)
    return {"state": state, **saved}
