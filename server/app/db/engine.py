"""SQLite engine factory.

Every connection this factory hands out is configured identically, because the guarantees
the contracts rely on are per-connection settings in SQLite:

``journal_mode=WAL``
    Required by ``contracts/ops/backup-restore.md`` / AMD-B11: the consistent-snapshot
    backup (SQLite Online Backup API or ``VACUUM INTO``) is only WAL-safe if the database
    is actually in WAL mode. A plain file copy of a WAL database is the defect that fixture
    ``acceptance/fixtures/recovery/d-wal-unsafe-copy-detected.json`` exists to catch.

``foreign_keys=ON``
    SQLite disables foreign keys per connection by default. The entity model in
    ``contracts/data/entities.yaml`` is full of referential constraints that are simply not
    enforced without this pragma, so leaving it off would let the database accept rows the
    contract forbids.

``busy_timeout``
    Two writers (scheduler loop and an HTTP request) will contend. Without a busy timeout
    SQLite raises ``database is locked`` immediately, which would surface as a spurious
    error rather than a short wait. 5000 ms is a conservative default; it is a Phase 0
    engineering value, not a contract number, and any card that needs a different value
    passes it explicitly.

``synchronous=NORMAL``
    The documented safe pairing with WAL: durable across application crashes, and the
    write path stays fast enough for the ingest batch sizes in
    ``contracts/schemas/ingest-batch.schema.json``. A power-loss window remains, which is
    why the backup contract exists.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, Engine, create_engine, event, text

#: Applied to EVERY connection, in this order.
SQLITE_PRAGMAS: tuple[tuple[str, str], ...] = (
    ("journal_mode", "WAL"),
    ("foreign_keys", "ON"),
    ("busy_timeout", "5000"),
    ("synchronous", "NORMAL"),
)


def _apply_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    try:
        for name, value in SQLITE_PRAGMAS:
            cursor.execute(f"PRAGMA {name}={value}")
    finally:
        cursor.close()


def create_sqlite_engine(db_path: str | Path, *, echo: bool = False) -> Engine:
    """Return an :class:`~sqlalchemy.Engine` for ``db_path`` with the pragmas above applied.

    ``db_path`` may be ``":memory:"`` for tests. Directories are not created here: a card
    that owns storage placement decides where the file lives
    (``contracts/ops/deployment.md``).
    """
    url = f"sqlite+pysqlite:///{db_path}"
    engine = create_engine(url, future=True, echo=echo)
    event.listen(engine, "connect", _apply_pragmas)
    return engine


def read_pragmas(connection: Connection) -> dict[str, object]:
    """Read back the pragmas this factory sets. Used by the smoke test as its oracle."""
    return {
        name.lower(): connection.execute(text(f"PRAGMA {name}")).scalar()
        for name, _ in SQLITE_PRAGMAS
    }


@contextmanager
def session_scope(engine: Engine) -> Iterator[Connection]:
    """A transactional Core connection.

    Commits on clean exit, rolls back on exception. Cards implementing a ``TXN-*`` use this
    as the transaction boundary rather than opening connections ad hoc, so that "one
    transaction" in a contract means one transaction in the code.
    """
    with engine.begin() as connection:
        yield connection


def sqlite_library_version() -> str:
    """The SQLite library version actually linked into this interpreter."""
    return sqlite3.sqlite_version
