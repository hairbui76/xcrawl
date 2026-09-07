"""Deterministic SQLite write-failure injection for the E2 tests.

Why this exists rather than a real full disk
--------------------------------------------
The behaviour under test is "the database refuses to accept a write". Reproducing that by
actually filling a filesystem would make the suite depend on the host's free space, run
slowly, and risk leaving the machine wedged if a test aborted mid-way. This module produces
the same *observable* condition -- the exact ``sqlite3.OperationalError`` SQLite raises when
it cannot write -- with no filesystem side effects at all, which is what
``agent-tasks/TC-storage-write-blocked-readiness.md`` §8 means by "fault injection is
enough; no live requirement".

What it does and does not prove
-------------------------------
It proves the *server's* reaction: the guard refuses, nothing is ACKed, no row count moves,
and the health channel still answers. It does **not** prove SQLite's own behaviour on a
genuinely full volume -- notably that the file is not corrupted (``REQ-S9.3-08``). That
belongs to a live drill and stays ``NOT_RUN``.

Usage::

    injector = WriteFaultInjector(engine)
    with injector.disk_full():
        ...                       # every INSERT/UPDATE/DELETE/COMMIT raises
    assert injector.statements_attempted == 0   # or however many the test expects
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import Engine, event

#: The message SQLite itself produces when the volume is full. Matched verbatim so a caller
#: that inspects the error string sees what production would show it.
DISK_FULL_MESSAGE = "database or disk is full"

#: Statement prefixes treated as writes. ``BEGIN`` is excluded on purpose: opening a
#: transaction succeeds on a full disk, and the failure appears at the first write or at
#: COMMIT. Failing earlier would make the test easier to pass than reality.
_WRITE_PREFIXES: tuple[str, ...] = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "REPLACE",
    "CREATE",
    "DROP",
    "ALTER",
    "COMMIT",
    "VACUUM",
    "PRAGMA WAL_CHECKPOINT",
)


def _is_write(statement: str) -> bool:
    normalised = " ".join(statement.strip().upper().split())
    return normalised.startswith(_WRITE_PREFIXES)


class WriteFaultInjector:
    """Arms an :class:`~sqlalchemy.Engine` to fail writes on demand, and counts traffic.

    The counter matters as much as the fault. Several oracles in this card are of the form
    "no write was even attempted" -- the guard is supposed to refuse *before* the service
    layer opens a transaction, so a test that only checks "the write failed" would also pass
    for an implementation that tries the write and catches the error, which is the
    implementation ``I02`` forbids.
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._armed = False
        self.statements_attempted = 0
        self.writes_attempted = 0
        event.listen(engine, "before_cursor_execute", self._before_cursor_execute)

    def _before_cursor_execute(
        self,
        _conn: Any,
        _cursor: Any,
        statement: str,
        _parameters: Any,
        _context: Any,
        _executemany: bool,
    ) -> None:
        self.statements_attempted += 1
        if _is_write(statement):
            self.writes_attempted += 1
            if self._armed:
                raise sqlite3.OperationalError(DISK_FULL_MESSAGE)

    def reset_counters(self) -> None:
        self.statements_attempted = 0
        self.writes_attempted = 0

    @property
    def armed(self) -> bool:
        return self._armed

    @contextmanager
    def disk_full(self) -> Iterator[WriteFaultInjector]:
        """Arm the fault for the duration of the block.

        Reads keep working inside the block, which is the point: ``write_blocked`` in
        ``contracts/state/storage.yaml`` says already-committed data stays readable and only
        the *write* path is closed. A test that could not read during the fault could not
        assert that row counts stayed put.
        """
        self._armed = True
        try:
            yield self
        finally:
            self._armed = False
