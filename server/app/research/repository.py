"""``source_fetch_log`` -- the only table ``MOD-research-connector`` owns.

``contracts/data/entities.yaml`` → ``source_fetch_log`` (``ENT-source-fetch-log``,
``owner_module: MOD-research-connector``). Its stated purpose is two things at once:

* **provenance** -- ``identity_alias.evidence_ref`` carries a ``response_hash`` key and
  ``contracts/data/identity.md`` §7 says that key points at *this* table's ``response_hash``
  column. Without a row here, an alias asserted from an API answer has no evidence trail.
* **rate-limit evidence** -- REQ-A6 asks the connector to respect a call rate. A rate you
  cannot count is a rate you cannot prove you respected, so a row is written for **every**
  outbound call, including the ones that failed (card §6: "Hàng ``source_fetch_log`` được
  ghi cho **cả** lời gọi thất bại").

What this module deliberately does not do
-----------------------------------------
It writes no ``work``, no ``work_version``, no ``identity_alias``. ``DC-RC-03`` of
``contracts/capabilities.yaml`` denies the connector the capability to author identity, and
card §4 restates it: the connector *returns* metadata and ``MOD-identity-service`` decides
what to persist. The only INSERT in this file targets ``source_fetch_log``.
"""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from sqlalchemy import Engine, text

_CROCKFORD: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: ``source_fetch_log.outcome`` closes over exactly these five values (entities.yaml).
#: ``timeout_unknown`` is not a synonym for ``error``: a transport timeout is an UNKNOWN
#: outcome (retry-policy RP-01), and recording it as ``error`` would assert the source
#: answered when nobody knows whether it did.
OUTCOMES: Final[frozenset[str]] = frozenset(
    {"ok", "not_found", "rate_limited", "error", "timeout_unknown"}
)

#: ``source_fetch_log.source_type`` closes over exactly these two values (entities.yaml).
SOURCE_TYPES: Final[frozenset[str]] = frozenset({"arxiv_api", "openalex_api"})


def new_ulid() -> str:
    """A 26-character Crockford base32 ULID (``entities.yaml`` §conventions ``id_type``).

    Time-ordered, so ``ORDER BY id`` on the fetch log is chronological without a second
    column; the random tail comes from :func:`os.urandom` so two rows minted in the same
    millisecond do not collide.
    """
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


@dataclass(frozen=True)
class SourceFetchLogRow:
    """One row of ``source_fetch_log``, in the eight columns the contract declares."""

    id: str
    owner_id: str
    source_type: str
    endpoint: str
    requested_at: str
    outcome: str
    response_hash: str | None
    work_id: str | None


class SourceFetchLogRepository:
    """Insert and read back ``source_fetch_log``.

    One statement per call and no transaction spanning a network request: an open
    transaction held across an outbound HTTP call would keep a SQLite write lock for the
    duration of somebody else's outage (SRC-PLAN §5.1 forbids network calls inside a
    transaction).
    """

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def insert(self, row: SourceFetchLogRow) -> None:
        """Write one row. Raises whatever the driver raises -- failures are not swallowed.

        A provenance record that silently did not get written is worse than a loud failure:
        the alias that cites it would point at nothing. See the handoff (``CR-TC-research-02``)
        for the missing contract code covering "the connector's own log could not be written".
        """
        if row.source_type not in SOURCE_TYPES:
            raise ValueError(f"source_type {row.source_type!r} is not in {sorted(SOURCE_TYPES)}")
        if row.outcome not in OUTCOMES:
            raise ValueError(f"outcome {row.outcome!r} is not in {sorted(OUTCOMES)}")
        with self._engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO source_fetch_log
                        (id, owner_id, source_type, endpoint, requested_at,
                         outcome, response_hash, work_id)
                    VALUES
                        (:id, :owner_id, :source_type, :endpoint, :requested_at,
                         :outcome, :response_hash, :work_id)
                    """
                ),
                {
                    "id": row.id,
                    "owner_id": row.owner_id,
                    "source_type": row.source_type,
                    "endpoint": row.endpoint,
                    "requested_at": row.requested_at,
                    "outcome": row.outcome,
                    "response_hash": row.response_hash,
                    "work_id": row.work_id,
                },
            )

    def list_for_owner(self, owner_id: str, *, limit: int = 100) -> Sequence[SourceFetchLogRow]:
        """Read the most recent rows, newest first. Used by tests and by an operator dump."""
        with self._engine.begin() as connection:
            result = connection.execute(
                text(
                    """
                    SELECT id, owner_id, source_type, endpoint, requested_at,
                           outcome, response_hash, work_id
                      FROM source_fetch_log
                     WHERE owner_id = :owner_id
                     ORDER BY id DESC
                     LIMIT :limit
                    """
                ),
                {"owner_id": owner_id, "limit": limit},
            )
            return [SourceFetchLogRow(*row) for row in result.fetchall()]

    def count(self) -> int:
        with self._engine.begin() as connection:
            value = connection.execute(text("SELECT COUNT(*) FROM source_fetch_log")).scalar()
        return int(value or 0)
