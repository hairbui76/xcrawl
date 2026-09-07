"""Alembic environment.

Two things are deliberate here:

1. **No URL in the repo.** The database URL comes from ``RR_DATABASE_URL``; there is no
   default that would silently write to a developer's real database.
2. **The same pragmas as the application.** Migrations run against a connection configured
   by ``server.app.db.create_sqlite_engine``, so a migration cannot succeed under different
   foreign-key or journal settings than the ones production uses.

No model metadata is registered yet: the schema is created by the Phase 1 cards
(``TC-ingest-idempotent-ack-lost``, ``TC-canonical-identity-merge``, ...) from
``contracts/data/entities.yaml``. ``target_metadata`` stays ``None`` until then, which
means autogenerate is not available -- that is intended: migrations are written from the
entity contract, not reverse-engineered from code.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from server.app.db.engine import create_sqlite_engine  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None

_ENV_VAR = "RR_DATABASE_URL"


def _database_path() -> str:
    url = os.environ.get(_ENV_VAR)
    if not url:
        raise RuntimeError(
            f"{_ENV_VAR} is not set. Alembic refuses to guess a database location; "
            f"set it explicitly, e.g. {_ENV_VAR}=./var/research-radar.db"
        )
    prefix = "sqlite+pysqlite:///"
    return url[len(prefix) :] if url.startswith(prefix) else url


def run_migrations_offline() -> None:
    context.configure(
        url=f"sqlite+pysqlite:///{_database_path()}",
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_sqlite_engine(_database_path())
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
