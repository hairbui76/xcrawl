"""Repository port for ``MOD-analysis-service``.

Scope of the port
-----------------
Five tables and no others: ``analysis``, ``analysis_attempt``, ``analysis_generation``,
``analysis_task`` (all ``owner_module: MOD-analysis-service`` in
``contracts/data/entities.yaml``) and ``assignment_lease``, which this module reads and
writes as the *holder* of an analysis claim while ``MOD-job-service`` owns the table
(``TC-scheduler-lease-claim``; see the header of
``server/migrations/versions/0006_tc_analysis_once_per_generation.py``).

Nothing here touches ``tag``, ``report``, ``report_item``, ``saved_item`` or
``saved_snapshot``. That is the point of the port, not an accident of what this card needed:
``contracts/modules.yaml`` FE-12/FE-13/FE-14 forbid the analysis side from reaching the tag,
report and Saved modules at all, and a repository that *could* write those tables would make
the denial a matter of discipline rather than of structure.

Every method takes an already-open :class:`~sqlalchemy.Connection` and never commits. The
transaction boundary is a contract fact (``TXN-analysis-accept``) and it lives in
``service.py``, where the commit point is named in the docstring of the function that owns
it.

SQLAlchemy 2 **Core** with explicit SQL, per ADR-0011: the DDL uses partial unique indexes
and multi-column CHECKs that an ORM mapping would hide.
"""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Connection, text

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def new_ulid() -> str:
    """A 26-character Crockford base32 ULID (``entities.yaml`` §conventions/id_type).

    Defined here rather than imported from ``server.app.ingest.repository``: that package is
    ``MOD-ingest-service``'s and the module registry grants no edge in this direction
    (ENF-import-rule). Timestamp-ordered, with an :func:`os.urandom` tail so two processes
    minting ids in the same millisecond do not collide.
    """
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def format_timestamp(moment: datetime) -> str:
    """RFC 3339 UTC with mandatory millisecond precision (``entities.yaml`` §conventions)."""
    return moment.astimezone(UTC).strftime(_TIMESTAMP_FORMAT)[:-3] + "Z"


def parse_timestamp(value: str) -> datetime:
    """Inverse of :func:`format_timestamp`."""
    return datetime.strptime(value, _TIMESTAMP_FORMAT + "Z").replace(tzinfo=UTC)


def json_text(value: Any) -> str:
    """Store a JSON document in a TEXT column, canonically.

    Canonical because ``analysis.payload_hash`` is ``sha256(JCS(payload))`` and a stored
    payload that re-serialises differently from the bytes that were hashed would make the
    hash unverifiable from the row.
    """
    from server.app.analysis.key import canonical_json

    return canonical_json(value)


# --------------------------------------------------------------------------------- rows


@dataclass(frozen=True)
class GenerationRow:
    """``ENT-analysis-generation`` -- one round of analysis for one target and one task."""

    id: str
    owner_id: str
    target_kind: str
    target_work_id: str | None
    target_post_id: str | None
    target_key: str
    task_type: str
    generation_number: int
    reason: str
    requested_at: str
    requested_by: str


@dataclass(frozen=True)
class TaskRow:
    """``ENT-analysis-task`` -- the queue entry. Never a result (I16)."""

    id: str
    owner_id: str
    analysis_generation_id: str
    target_key: str
    task_type: str
    state: str
    claimed_by_worker_identity: str | None
    claimed_lease_id: str | None
    claimed_at: str | None
    enqueued_at: str
    attempt_budget_remaining: int


@dataclass(frozen=True)
class AttemptRow:
    """``ENT-analysis-attempt`` -- every try, including the ones nobody knows the end of."""

    id: str
    owner_id: str
    analysis_generation_id: str
    attempt_number: int
    outcome: str
    error_code: str | None
    started_at: str
    ended_at: str | None
    worker_lease_id: str | None
    cost_uncertain: bool


@dataclass(frozen=True)
class LeaseRow:
    """``ENT-assignment-lease`` -- exclusive hold on one job, with a fencing epoch."""

    id: str
    owner_id: str
    run_id: str
    job_id: str
    worker_identity: str
    lease_epoch: int
    expires_at: str
    state: str


@dataclass(frozen=True)
class AnalysisRow:
    """``ENT-analysis`` -- a committed result. Immutable after commit."""

    id: str
    owner_id: str
    analysis_generation_id: str
    target_kind: str
    target_work_id: str | None
    target_post_id: str | None
    target_key: str
    task_type: str
    source_fingerprint: str
    prompt_version: str
    schema_version: str
    generation_number: int
    status: str
    payload: str
    payload_hash: str
    evidence_level: str
    provider_name: str
    model_name: str
    usage_tokens_in: int | None
    usage_tokens_out: int | None
    analyzed_at: str
    accepted_from_attempt_id: str


_GENERATION_COLUMNS = (
    "id, owner_id, target_kind, target_work_id, target_post_id, target_key, task_type, "
    "generation_number, reason, requested_at, requested_by"
)
_TASK_COLUMNS = (
    "id, owner_id, analysis_generation_id, target_key, task_type, state, "
    "claimed_by_worker_identity, claimed_lease_id, claimed_at, enqueued_at, "
    "attempt_budget_remaining"
)
_ATTEMPT_COLUMNS = (
    "id, owner_id, analysis_generation_id, attempt_number, outcome, error_code, "
    "started_at, ended_at, worker_lease_id, cost_uncertain"
)
_LEASE_COLUMNS = "id, owner_id, run_id, job_id, worker_identity, lease_epoch, expires_at, state"
_ANALYSIS_COLUMNS = (
    "id, owner_id, analysis_generation_id, target_kind, target_work_id, target_post_id, "
    "target_key, task_type, source_fingerprint, prompt_version, schema_version, "
    "generation_number, status, payload, payload_hash, evidence_level, provider_name, "
    "model_name, usage_tokens_in, usage_tokens_out, analyzed_at, accepted_from_attempt_id"
)


class AnalysisRepository:
    """Table-scoped data access for the analysis domain."""

    # ------------------------------------------------------------------ generations

    def insert_generation(self, connection: Connection, row: GenerationRow) -> None:
        connection.execute(
            text(
                f"INSERT INTO analysis_generation ({_GENERATION_COLUMNS}) VALUES "
                "(:id, :owner_id, :target_kind, :target_work_id, :target_post_id, "
                ":target_key, :task_type, :generation_number, :reason, :requested_at, "
                ":requested_by)"
            ),
            vars(row),
        )

    def generation_by_id(self, connection: Connection, generation_id: str) -> GenerationRow | None:
        row = (
            connection.execute(
                text(f"SELECT {_GENERATION_COLUMNS} FROM analysis_generation WHERE id = :id"),
                {"id": generation_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else GenerationRow(**dict(row))

    def find_generation(
        self,
        connection: Connection,
        *,
        owner_id: str,
        target_key: str,
        task_type: str,
        generation_number: int,
    ) -> GenerationRow | None:
        row = (
            connection.execute(
                text(
                    f"SELECT {_GENERATION_COLUMNS} FROM analysis_generation "
                    "WHERE owner_id = :owner_id AND target_key = :target_key "
                    "AND task_type = :task_type AND generation_number = :generation_number"
                ),
                {
                    "owner_id": owner_id,
                    "target_key": target_key,
                    "task_type": task_type,
                    "generation_number": generation_number,
                },
            )
            .mappings()
            .first()
        )
        return None if row is None else GenerationRow(**dict(row))

    def max_generation_number(
        self, connection: Connection, *, owner_id: str, target_key: str, task_type: str
    ) -> int:
        """0 when the target has never been analysed for this task type."""
        value = connection.execute(
            text(
                "SELECT COALESCE(MAX(generation_number), 0) FROM analysis_generation "
                "WHERE owner_id = :owner_id AND target_key = :target_key "
                "AND task_type = :task_type"
            ),
            {"owner_id": owner_id, "target_key": target_key, "task_type": task_type},
        ).scalar_one()
        return int(value)

    def count_generations(self, connection: Connection, *, owner_id: str) -> int:
        """Oracle for AC-06: re-adding a tag must not move this number."""
        return int(
            connection.execute(
                text("SELECT COUNT(*) FROM analysis_generation WHERE owner_id = :owner_id"),
                {"owner_id": owner_id},
            ).scalar_one()
        )

    # ------------------------------------------------------------------------ tasks

    def insert_task(self, connection: Connection, row: TaskRow) -> None:
        connection.execute(
            text(
                f"INSERT INTO analysis_task ({_TASK_COLUMNS}) VALUES "
                "(:id, :owner_id, :analysis_generation_id, :target_key, :task_type, :state, "
                ":claimed_by_worker_identity, :claimed_lease_id, :claimed_at, :enqueued_at, "
                ":attempt_budget_remaining)"
            ),
            vars(row),
        )

    def task_by_id(self, connection: Connection, task_id: str) -> TaskRow | None:
        row = (
            connection.execute(
                text(f"SELECT {_TASK_COLUMNS} FROM analysis_task WHERE id = :id"),
                {"id": task_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else TaskRow(**dict(row))

    def open_task_for_generation(
        self, connection: Connection, *, owner_id: str, analysis_generation_id: str
    ) -> TaskRow | None:
        """The one task that ``ux_analysis_task_open`` allows to be open for a generation."""
        row = (
            connection.execute(
                text(
                    f"SELECT {_TASK_COLUMNS} FROM analysis_task "
                    "WHERE owner_id = :owner_id "
                    "AND analysis_generation_id = :analysis_generation_id "
                    "AND state NOT IN ('valid', 'failed')"
                ),
                {"owner_id": owner_id, "analysis_generation_id": analysis_generation_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else TaskRow(**dict(row))

    def next_pending_task(
        self, connection: Connection, *, owner_id: str, task_types: Sequence[str]
    ) -> TaskRow | None:
        """Oldest ``pending`` task whose type the worker declared a capability for.

        Ordered by ``enqueued_at`` then ``id``: ULIDs are timestamp-ordered, so the pair is a
        total order and two workers polling at the same moment see the same candidate. Which
        of them gets it is settled by the lease insert, not by the read.
        """
        if not task_types:
            return None
        placeholders = ", ".join(f":t{index}" for index in range(len(task_types)))
        parameters: dict[str, Any] = {"owner_id": owner_id}
        parameters.update({f"t{index}": value for index, value in enumerate(task_types)})
        row = (
            connection.execute(
                text(
                    f"SELECT {_TASK_COLUMNS} FROM analysis_task "
                    "WHERE owner_id = :owner_id AND state = 'pending' "
                    f"AND task_type IN ({placeholders}) "
                    "ORDER BY enqueued_at, id LIMIT 1"
                ),
                parameters,
            )
            .mappings()
            .first()
        )
        return None if row is None else TaskRow(**dict(row))

    def mark_task_running(
        self,
        connection: Connection,
        *,
        task_id: str,
        worker_identity: str,
        lease_id: str,
        claimed_at: str,
    ) -> int:
        """Set the claim pointer set atomically with the state.

        The ``WHERE state = 'pending'`` clause is the concurrency control: two workers that
        both read the same pending row race here, and the loser updates zero rows and is told
        to poll again. Returns the number of rows updated.
        """
        result = connection.execute(
            text(
                "UPDATE analysis_task SET state = 'running', "
                "claimed_by_worker_identity = :worker_identity, "
                "claimed_lease_id = :lease_id, claimed_at = :claimed_at "
                "WHERE id = :task_id AND state = 'pending'"
            ),
            {
                "task_id": task_id,
                "worker_identity": worker_identity,
                "lease_id": lease_id,
                "claimed_at": claimed_at,
            },
        )
        return int(result.rowcount)

    def release_task(self, connection: Connection, *, task_id: str, state: str) -> None:
        """Move a task out of ``running`` and clear all three claim columns together.

        The three CHECKs on the table make "state is not running" and "no claim pointer"
        the same fact, so they are written in one statement and cannot drift.
        """
        connection.execute(
            text(
                "UPDATE analysis_task SET state = :state, "
                "claimed_by_worker_identity = NULL, claimed_lease_id = NULL, "
                "claimed_at = NULL WHERE id = :task_id"
            ),
            {"task_id": task_id, "state": state},
        )

    def spend_attempt_budget(self, connection: Connection, *, task_id: str) -> int:
        """Decrement the budget, never below zero. Returns the remaining value."""
        connection.execute(
            text(
                "UPDATE analysis_task "
                "SET attempt_budget_remaining = MAX(attempt_budget_remaining - 1, 0) "
                "WHERE id = :task_id"
            ),
            {"task_id": task_id},
        )
        return int(
            connection.execute(
                text("SELECT attempt_budget_remaining FROM analysis_task WHERE id = :task_id"),
                {"task_id": task_id},
            ).scalar_one()
        )

    # --------------------------------------------------------------------- attempts

    def insert_attempt(self, connection: Connection, row: AttemptRow) -> None:
        values = dict(vars(row))
        values["cost_uncertain"] = int(row.cost_uncertain)
        connection.execute(
            text(
                f"INSERT INTO analysis_attempt ({_ATTEMPT_COLUMNS}) VALUES "
                "(:id, :owner_id, :analysis_generation_id, :attempt_number, :outcome, "
                ":error_code, :started_at, :ended_at, :worker_lease_id, :cost_uncertain)"
            ),
            values,
        )

    def attempt_by_id(self, connection: Connection, attempt_id: str) -> AttemptRow | None:
        row = (
            connection.execute(
                text(f"SELECT {_ATTEMPT_COLUMNS} FROM analysis_attempt WHERE id = :id"),
                {"id": attempt_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else self._attempt(row)

    def attempts_for_generation(
        self, connection: Connection, *, owner_id: str, analysis_generation_id: str
    ) -> list[AttemptRow]:
        rows = connection.execute(
            text(
                f"SELECT {_ATTEMPT_COLUMNS} FROM analysis_attempt "
                "WHERE owner_id = :owner_id "
                "AND analysis_generation_id = :analysis_generation_id "
                "ORDER BY attempt_number"
            ),
            {"owner_id": owner_id, "analysis_generation_id": analysis_generation_id},
        ).mappings()
        return [self._attempt(row) for row in rows]

    def next_attempt_number(
        self, connection: Connection, *, owner_id: str, analysis_generation_id: str
    ) -> int:
        value = connection.execute(
            text(
                "SELECT COALESCE(MAX(attempt_number), 0) + 1 FROM analysis_attempt "
                "WHERE owner_id = :owner_id "
                "AND analysis_generation_id = :analysis_generation_id"
            ),
            {"owner_id": owner_id, "analysis_generation_id": analysis_generation_id},
        ).scalar_one()
        return int(value)

    def close_attempt(
        self,
        connection: Connection,
        *,
        attempt_id: str,
        outcome: str,
        error_code: str | None,
        ended_at: str | None,
        cost_uncertain: bool,
    ) -> None:
        """Write the ending of an attempt that was opened at claim time.

        ``cost_uncertain`` is set, not merged. An attempt row starts life as
        ``timeout_unknown`` with ``cost_uncertain = 1`` -- the honest state while the server
        does not yet know whether the model ran -- and this is where it becomes known. An
        attempt that ends ``accepted`` has a known cost; one that ends ``timeout_unknown``
        does not, and the CHECK on the table refuses to record that outcome as certain.

        "``cost_uncertain = true`` is kept for good" (T-AN-08 ``effects_vi``) is about the
        *row*, not about later attempts: a re-run writes a NEW attempt and never edits this
        one. The service enforces that by refusing every mutation from a lease that is no
        longer current, so a concluded unknown attempt has no path back to ``accepted``.
        """
        connection.execute(
            text(
                "UPDATE analysis_attempt SET outcome = :outcome, error_code = :error_code, "
                "ended_at = :ended_at, cost_uncertain = :cost_uncertain "
                "WHERE id = :attempt_id"
            ),
            {
                "attempt_id": attempt_id,
                "outcome": outcome,
                "error_code": error_code,
                "ended_at": ended_at,
                "cost_uncertain": int(cost_uncertain),
            },
        )

    def count_attempts(self, connection: Connection, *, owner_id: str) -> int:
        return int(
            connection.execute(
                text("SELECT COUNT(*) FROM analysis_attempt WHERE owner_id = :owner_id"),
                {"owner_id": owner_id},
            ).scalar_one()
        )

    def count_cost_uncertain_attempts(self, connection: Connection, *, owner_id: str) -> int:
        return int(
            connection.execute(
                text(
                    "SELECT COUNT(*) FROM analysis_attempt "
                    "WHERE owner_id = :owner_id AND cost_uncertain = 1"
                ),
                {"owner_id": owner_id},
            ).scalar_one()
        )

    @staticmethod
    def _attempt(row: Any) -> AttemptRow:
        values = dict(row)
        values["cost_uncertain"] = bool(values["cost_uncertain"])
        return AttemptRow(**values)

    # ----------------------------------------------------------------------- leases

    def insert_lease(self, connection: Connection, row: LeaseRow) -> None:
        connection.execute(
            text(
                f"INSERT INTO assignment_lease ({_LEASE_COLUMNS}) VALUES "
                "(:id, :owner_id, :run_id, :job_id, :worker_identity, :lease_epoch, "
                ":expires_at, :state)"
            ),
            vars(row),
        )

    def lease_by_id(self, connection: Connection, lease_id: str) -> LeaseRow | None:
        row = (
            connection.execute(
                text(f"SELECT {_LEASE_COLUMNS} FROM assignment_lease WHERE id = :id"),
                {"id": lease_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else LeaseRow(**dict(row))

    def max_lease_epoch(self, connection: Connection, *, owner_id: str, job_id: str) -> int:
        value = connection.execute(
            text(
                "SELECT COALESCE(MAX(lease_epoch), 0) FROM assignment_lease "
                "WHERE owner_id = :owner_id AND job_id = :job_id"
            ),
            {"owner_id": owner_id, "job_id": job_id},
        ).scalar_one()
        return int(value)

    def set_lease_state(self, connection: Connection, *, lease_id: str, state: str) -> None:
        connection.execute(
            text("UPDATE assignment_lease SET state = :state WHERE id = :lease_id"),
            {"lease_id": lease_id, "state": state},
        )

    def extend_lease(self, connection: Connection, *, lease_id: str, expires_at: str) -> None:
        connection.execute(
            text("UPDATE assignment_lease SET expires_at = :expires_at WHERE id = :lease_id"),
            {"lease_id": lease_id, "expires_at": expires_at},
        )

    # --------------------------------------------------------------------- analysis

    def insert_analysis(self, connection: Connection, row: AnalysisRow) -> None:
        """Insert a result row. ``target_key`` is omitted: it is a generated column."""
        values = dict(vars(row))
        del values["target_key"]
        columns = _ANALYSIS_COLUMNS.replace("target_key, ", "")
        binds = ", ".join(f":{name}" for name in columns.replace(" ", "").split(","))
        connection.execute(text(f"INSERT INTO analysis ({columns}) VALUES ({binds})"), values)

    def find_valid_by_key(
        self,
        connection: Connection,
        *,
        owner_id: str,
        target_key: str,
        task_type: str,
        source_fingerprint: str,
        prompt_version: str,
        schema_version: str,
        generation_number: int,
    ) -> AnalysisRow | None:
        """The at-most-one row ``ux_analysis_valid_key`` permits for a key.

        This read is the whole of "has this already been analysed?" -- and it reads
        ``analysis`` only. There is no branch anywhere in this module that falls back to
        ``analysis_attempt`` when it comes back empty, because an attempt is not a result
        (I16, ``ENT-analysis-attempt.statement``).
        """
        row = (
            connection.execute(
                text(
                    f"SELECT {_ANALYSIS_COLUMNS} FROM analysis "
                    "WHERE owner_id = :owner_id AND target_key = :target_key "
                    "AND task_type = :task_type AND source_fingerprint = :source_fingerprint "
                    "AND prompt_version = :prompt_version AND schema_version = :schema_version "
                    "AND generation_number = :generation_number AND status = 'valid'"
                ),
                {
                    "owner_id": owner_id,
                    "target_key": target_key,
                    "task_type": task_type,
                    "source_fingerprint": source_fingerprint,
                    "prompt_version": prompt_version,
                    "schema_version": schema_version,
                    "generation_number": generation_number,
                },
            )
            .mappings()
            .first()
        )
        return None if row is None else AnalysisRow(**dict(row))

    def count_valid(
        self, connection: Connection, *, owner_id: str, target_key: str | None = None
    ) -> int:
        """``COUNT(analysis WHERE status='valid')`` -- the §8 oracle, as SQL."""
        clause = "" if target_key is None else " AND target_key = :target_key"
        parameters: dict[str, Any] = {"owner_id": owner_id}
        if target_key is not None:
            parameters["target_key"] = target_key
        return int(
            connection.execute(
                text(
                    "SELECT COUNT(*) FROM analysis "
                    f"WHERE owner_id = :owner_id AND status = 'valid'{clause}"
                ),
                parameters,
            ).scalar_one()
        )


__all__ = [
    "AnalysisRepository",
    "AnalysisRow",
    "AttemptRow",
    "GenerationRow",
    "LeaseRow",
    "TaskRow",
    "format_timestamp",
    "json_text",
    "new_ulid",
    "parse_timestamp",
]
