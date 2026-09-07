"""Database access for the server (SQLAlchemy 2 Core over SQLite).

ADR-0011: SQLAlchemy 2 **Core**, no ORM magic -- the ``TXN-*`` transactions in
``contracts/data/entities.yaml`` need explicit SQL, and partial indexes and generated
columns need control at Core level.
"""

from server.app.db.engine import (
    SQLITE_PRAGMAS,
    create_sqlite_engine,
    session_scope,
)

__all__ = ["SQLITE_PRAGMAS", "create_sqlite_engine", "session_scope"]
