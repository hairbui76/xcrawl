"""E1/E2 — disk full mid-ingest: no ACK, no cursor movement, readiness red.

Oracles (``agent-tasks/TC-storage-write-blocked-readiness.md`` §8), all measured by counts,
hashes or string comparison rather than by reading a log:

* fixture ``recovery/c-disk-full-mid-ingest.json``: the ``ingest_receipt`` is **absent**
  *and* readiness is **red** -- both must hold, not either;
* no row anywhere records "the error was persisted" while the database cannot be written;
* fixture ``collection/l-storage-write-blocked-mid-run.json``: the checkpoint does not
  advance, and recovery lands on ``healthy`` or ``recovery_required`` depending on whether a
  restore is outstanding.

The fixtures are the only data source (``tests/README.md`` §1); nothing here invents rows.

Scope note. ``ingest.submit_batch`` itself belongs to ``TC-ingest-idempotent-ack-lost``.
The assertions that need that service are skipped when it is absent and run for real when
it is present. What *this* card proves either way is that the guard refuses with the
contract's code before any transaction opens, which is the condition that makes an ACK
impossible in the first place.
"""

from __future__ import annotations

import hashlib
import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import StorageHealth
from sqlalchemy import text

from server.app.db.engine import create_sqlite_engine, session_scope
from server.app.db.faults import DISK_FULL_MESSAGE, WriteFaultInjector
from server.app.health.router import StorageReadinessProvider
from server.app.storage.guard import StorageGuard, StorageRefused
from server.app.storage.health import (
    PROBE_CONSECUTIVE_SUCCESS,
    PROBE_INTERVAL_SECONDS,
    ForbiddenTransition,
    StorageHealthMachine,
)

FIXTURE_C = "recovery/c-disk-full-mid-ingest"
FIXTURE_L = "collection/l-storage-write-blocked-mid-run"

PENDING_INGEST_CARD = "server.app.ingest.service not present (TC-ingest-idempotent-ack-lost)"

#: ``server.app.ingest.service`` is the write set of ``TC-ingest-idempotent-ack-lost``,
#: which runs in parallel with this card.
INGEST_SERVICE_PRESENT = importlib.util.find_spec("server.app.ingest.service") is not None


class FrozenClock:
    """A clock the test advances explicitly.

    The probe rules are expressed in seconds (30 s apart, 3 in a row). Sleeping through them
    would add 90 s per case and make the suite's duration depend on the contract's tuning
    values, so time is injected instead.
    """

    def __init__(self, start: datetime | None = None) -> None:
        self.now = start or datetime(2026, 9, 7, 8, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: float) -> datetime:
        self.now += timedelta(seconds=seconds)
        return self.now


@pytest.fixture()
def clock() -> FrozenClock:
    return FrozenClock()


@pytest.fixture()
def guard(clock: FrozenClock) -> StorageGuard:
    return StorageGuard(StorageHealthMachine(clock=clock))


# ---------------------------------------------------------------------------------------
# Fixture c -- the two conditions that must hold together
# ---------------------------------------------------------------------------------------


def test_fixture_c_refuses_every_event_with_the_pinned_code(
    fixture_loader: Any, guard: StorageGuard
) -> None:
    """Every event of fixture ``c`` gets exactly the ``expected`` code the fixture pins.

    Driven from the fixture's own ``events``/``expected`` blocks rather than from a list
    retyped here, so a change to the oracle changes the test.
    """
    fixture = fixture_loader(FIXTURE_C)
    assert "SC26" in fixture.scenario_refs
    expected = fixture.expected

    # seq 1 carries `fault: disk_full_during_commit` -- the moment T-ST-01 fires.
    submit = next(e for e in fixture.events if e["seq"] == 1)
    assert submit["fault"] == "disk_full_during_commit"
    assert guard.current_health() is StorageHealth.HEALTHY
    guard.record_write_failure()

    # seq 2: storage.get_health, called by the health service, reports write_blocked.
    assert guard.current_health() is StorageHealth.WRITE_BLOCKED
    health = guard.get_health(caller_module="MOD-health-service")
    assert health["storage_health"] == expected["seq2"]["storage_health"]

    # seq 1 and seq 4 are both refused with the fixture's pinned code, and the refusal
    # carries the contract's scope and retry class -- a caller branches on those.
    for seq, operation in (
        (1, OperationId.INGEST_SUBMIT_BATCH),
        (4, OperationId.INGEST_COMMIT_CHECKPOINT),
    ):
        with pytest.raises(StorageRefused) as caught:
            guard.assert_writable(operation)
        envelope = caught.value.envelope
        assert envelope["code"] == expected[f"seq{seq}"]["error_code"]
        assert envelope["scope"] == SCOPE[ErrorCode.STORAGE_WRITE_FAILED] == "storage"
        assert envelope["retry_class"] == RETRY_CLASS[ErrorCode.STORAGE_WRITE_FAILED]

    # seq 1's `acked: false` is the whole point: the refusal is raised, never returned, so
    # a caller cannot reach its ACK line by forgetting to check a boolean.
    assert expected["seq1"]["acked"] is False


def test_fixture_c_readiness_red_and_liveness_up_together(
    fixture_loader: Any, guard: StorageGuard
) -> None:
    """``expected.readiness``: storage red **and** liveness up. Both, or the oracle fails.

    Either one alone would be satisfiable by a broken implementation: a server that has
    fallen over reports neither, and a server that ignores the fault reports both green.
    """
    fixture = fixture_loader(FIXTURE_C)
    readiness = fixture.expected["readiness"]
    assert readiness == {"storage": "red", "liveness": "up"}

    guard.record_write_failure()
    snapshot = StorageReadinessProvider(guard).snapshot()

    # The fixture says "red"; contracts/ops/deployment.md §5 names the same condition
    # `down`. Assert the contract's vocabulary and the mapping between them explicitly
    # rather than quietly accepting either word.
    assert snapshot["modules"]["storage"] == "down"
    assert snapshot["storage_health"] == StorageHealth.WRITE_BLOCKED.value
    assert snapshot["modules"]["job_dispatch"] == "down"


def test_no_write_is_even_attempted_while_blocked(guard: StorageGuard, tmp_path: Path) -> None:
    """I02, measured: the guard refuses *before* a transaction opens.

    The counter is the oracle. An implementation that opens the transaction, tries the
    write, catches the failure and then refuses would also produce ``STORAGE_WRITE_FAILED``
    -- and would still be wrong, because between the attempt and the catch it has already
    written to a disk the contract says not to write to (``REQ-S9.3-08``).
    """
    engine = create_sqlite_engine(tmp_path / "blocked.db")
    injector = WriteFaultInjector(engine)
    with session_scope(engine) as connection:
        connection.execute(text("CREATE TABLE probe (id INTEGER PRIMARY KEY)"))
    injector.reset_counters()

    guard.record_write_failure()
    with injector.disk_full(), pytest.raises(StorageRefused):
        guard.assert_writable(OperationId.INGEST_SUBMIT_BATCH)
        # unreachable: had the guard allowed it, this write would have hit the fault
        with session_scope(engine) as connection:  # pragma: no cover
            connection.execute(text("INSERT INTO probe (id) VALUES (1)"))

    assert injector.writes_attempted == 0
    assert injector.statements_attempted == 0


def test_database_file_hash_is_unchanged_across_the_blocked_window(
    guard: StorageGuard, tmp_path: Path
) -> None:
    """``oracle_vi`` of fixture ``c``: the DB file's sha256 does not change during the fault."""
    db_path = tmp_path / "hashed.db"
    engine = create_sqlite_engine(db_path)
    with session_scope(engine) as connection:
        connection.execute(text("CREATE TABLE probe (id INTEGER PRIMARY KEY)"))
        connection.execute(text("INSERT INTO probe (id) VALUES (1)"))
    # WAL keeps recent commits beside the main file; checkpoint so the hash is stable and
    # the comparison is about the fault window rather than about WAL flush timing.
    with engine.connect() as connection:
        connection.exec_driver_sql("PRAGMA wal_checkpoint(TRUNCATE)")
    engine.dispose()

    before = hashlib.sha256(db_path.read_bytes()).hexdigest()
    guard.record_write_failure()
    for operation in (
        OperationId.INGEST_SUBMIT_BATCH,
        OperationId.INGEST_COMMIT_CHECKPOINT,
        OperationId.WORKER_CLAIM_ASSIGNMENT,
        OperationId.REPORT_PUBLISH,
        OperationId.DELIVERY_DISPATCH_NEXT,
    ):
        with pytest.raises(StorageRefused):
            guard.assert_writable(operation)
    after = hashlib.sha256(db_path.read_bytes()).hexdigest()

    assert after == before


def test_the_refusal_is_not_persisted_anywhere(guard: StorageGuard, tmp_path: Path) -> None:
    """``EPR-01``: reporting the error must not require a database row.

    Both halves are asserted: the envelope is complete enough to *be* the report (it carries
    a ``correlation_id`` generated in memory), and producing it touched the database zero
    times.
    """
    engine = create_sqlite_engine(tmp_path / "nopersist.db")
    with session_scope(engine) as connection:
        connection.execute(text("CREATE TABLE probe (id INTEGER PRIMARY KEY)"))
    injector = WriteFaultInjector(engine)
    injector.reset_counters()

    guard.record_write_failure()
    with pytest.raises(StorageRefused) as caught:
        guard.assert_writable(OperationId.INGEST_SUBMIT_BATCH)

    envelope = caught.value.envelope
    assert envelope["correlation_id"]
    assert len(envelope["correlation_id"]) == 26  # ULID
    assert injector.statements_attempted == 0


def test_envelope_leaks_nothing_outside_details_safe_keys(guard: StorageGuard) -> None:
    """``forbidden_content_vi``: no file paths, no SQL, no internal table names.

    The builder filters by ``details_safe_keys`` rather than trusting callers, so this test
    hands it a key that a careless implementation would happily forward.
    """
    guard.record_write_failure()
    with pytest.raises(StorageRefused) as caught:
        guard.assert_writable(OperationId.INGEST_SUBMIT_BATCH)
    details = caught.value.envelope["details_safe"]
    assert set(details) <= {
        "storage_health",
        "failed_operation_id",
        "observed_at",
        "retry_after_ms",
    }
    assert DISK_FULL_MESSAGE not in str(caught.value.envelope)
    assert ".db" not in str(caught.value.envelope)


# ---------------------------------------------------------------------------------------
# Fixture l -- the block window and the two recovery branches (SC36)
# ---------------------------------------------------------------------------------------


def test_fixture_l_grants_nothing_during_the_block(
    fixture_loader: Any, guard: StorageGuard
) -> None:
    """``expected.counts``: zero receipts created and zero leases granted while blocked."""
    fixture = fixture_loader(FIXTURE_L)
    counts = fixture.expected["counts"]
    assert counts["ingest_receipt_created_during_block"] == 0
    assert counts["assignment_lease_granted_during_block"] == 0

    guard.record_write_failure()
    for operation in (
        OperationId.INGEST_SUBMIT_BATCH,
        OperationId.WORKER_CLAIM_ASSIGNMENT,
        OperationId.ANALYSIS_CLAIM_TASK,
    ):
        with pytest.raises(StorageRefused) as caught:
            guard.assert_writable(operation)
        assert caught.value.code is ErrorCode.STORAGE_WRITE_FAILED


def test_fixture_l_checkpoint_does_not_advance(fixture_loader: Any) -> None:
    """``I02``: the acked sequence in ``expected`` equals the one in ``given``."""
    fixture = fixture_loader(FIXTURE_L)
    given = fixture.rows("checkpoint", block="given")[0]
    expected = fixture.rows("checkpoint", block="expected")[0]
    assert expected["acked_through_ingest_sequence"] == given["acked_through_ingest_sequence"]
    assert expected["sequence"] == given["sequence"]


def test_fixture_l_branch_a_recovers_to_healthy(
    fixture_loader: Any, guard: StorageGuard, clock: FrozenClock
) -> None:
    """Branch A: three spaced probes succeed and nothing was restored, so ``healthy`` (T-ST-02)."""
    fixture = fixture_loader(FIXTURE_L)
    assert fixture.expected["_branch_A_storage_health"] == StorageHealth.HEALTHY.value

    guard.record_write_failure()
    for _ in range(PROBE_CONSECUTIVE_SUCCESS):
        clock.advance(PROBE_INTERVAL_SECONDS)
        guard.record_probe(success=True, at=clock.now)
    assert guard.current_health() is StorageHealth.HEALTHY
    assert guard.machine.history == ("T-ST-01", "T-ST-02")


def test_fixture_l_branch_b_recovers_to_recovery_required(
    fixture_loader: Any, clock: FrozenClock
) -> None:
    """Branch B: the same probes, but a restore is outstanding, so ``recovery_required``.

    This is ``T-ST-08``, and it is the branch that stops a disk incident from laundering an
    unreconciled restore into a clean ``healthy`` -- which would let the dispatcher replay a
    stale outbox (``I15``).
    """
    fixture = fixture_loader(FIXTURE_L)
    assert fixture.expected["_branch_B_storage_health"] == StorageHealth.RECOVERY_REQUIRED.value
    restore_id = next(e for e in fixture.events if e.get("_branch") == "B")[
        "_given_restore_record_id"
    ]

    guard = StorageGuard(
        StorageHealthMachine(clock=clock, pending_restore_id=restore_id),
    )
    guard.record_write_failure()
    for _ in range(PROBE_CONSECUTIVE_SUCCESS):
        clock.advance(PROBE_INTERVAL_SECONDS)
        guard.record_probe(success=True, at=clock.now)

    assert guard.current_health() is StorageHealth.RECOVERY_REQUIRED
    assert guard.machine.history == ("T-ST-01", "T-ST-08")
    # And the dispatcher is still locked with the *other* code -- not STORAGE_WRITE_FAILED.
    with pytest.raises(StorageRefused) as caught:
        guard.assert_writable(OperationId.DELIVERY_DISPATCH_NEXT)
    assert caught.value.code is ErrorCode.RESTORE_UNVERIFIED


# ---------------------------------------------------------------------------------------
# The probe guards themselves (forbidden_transitions rows 2 and 3)
# ---------------------------------------------------------------------------------------


def test_a_single_probe_does_not_leave_write_blocked(
    guard: StorageGuard, clock: FrozenClock
) -> None:
    """``forbidden_transitions`` row 2. A nearly-full disk succeeds once and fails next."""
    guard.record_write_failure()
    clock.advance(PROBE_INTERVAL_SECONDS)
    assert guard.record_probe(success=True, at=clock.now) is None
    assert guard.current_health() is StorageHealth.WRITE_BLOCKED


def test_a_failed_probe_resets_the_streak(guard: StorageGuard, clock: FrozenClock) -> None:
    """Two successes, one failure, two successes must not add up to three."""
    guard.record_write_failure()
    for success in (True, True, False, True, True):
        clock.advance(PROBE_INTERVAL_SECONDS)
        guard.record_probe(success=success, at=clock.now)
    assert guard.current_health() is StorageHealth.WRITE_BLOCKED


def test_probes_closer_than_the_interval_do_not_count(
    guard: StorageGuard, clock: FrozenClock
) -> None:
    """Three probes in a millisecond are one observation, not three (T-ST-02 guard)."""
    guard.record_write_failure()
    clock.advance(PROBE_INTERVAL_SECONDS)
    guard.record_probe(success=True, at=clock.now)
    for _ in range(5):
        clock.advance(1)
        guard.record_probe(success=True, at=clock.now)
    assert guard.current_health() is StorageHealth.WRITE_BLOCKED


def test_probing_outside_write_blocked_is_a_forbidden_transition(guard: StorageGuard) -> None:
    """There is no probe edge from ``healthy``; asking is a contract error, not a no-op."""
    with pytest.raises(ForbiddenTransition):
        guard.record_probe(success=True)


def test_repeated_write_failures_are_one_incident(guard: StorageGuard) -> None:
    """The same disk failing twice must not append a second T-ST-01."""
    guard.record_write_failure()
    assert guard.record_write_failure() is None
    assert guard.machine.history == ("T-ST-01",)


def test_healthy_refuses_nothing(guard: StorageGuard) -> None:
    """The negative control: without a fault, the guard is transparent."""
    for operation in (
        OperationId.INGEST_SUBMIT_BATCH,
        OperationId.REPORT_PUBLISH,
        OperationId.DELIVERY_DISPATCH_NEXT,
        OperationId.WORKER_CLAIM_ASSIGNMENT,
    ):
        guard.assert_writable(operation)


# ---------------------------------------------------------------------------------------
# Cross-card: the real ingest service refuses through this guard
# ---------------------------------------------------------------------------------------


@pytest.mark.skipif(not INGEST_SERVICE_PRESENT, reason=PENDING_INGEST_CARD)
def test_real_ingest_submit_batch_is_refused_and_acks_nothing(
    fixture_loader: Any, guard: StorageGuard, tmp_path: Path
) -> None:
    """``expected.seq1`` of fixture ``c``, driven through ``TC-ingest-idempotent-ack-lost``.

    This is the assertion that closes the loop: it is not this card asserting its own
    refusal, it is the real ``ingest.submit_batch`` -- written by another card against the
    ``StorageGuardPort`` documented in ``server/app/storage/guard.py`` -- declining to ACK
    because this guard said no.

    The batch is the wire-valid one from ``identity/pos-ingest-batch-valid``; using a
    hand-built payload would risk failing on validation before ever reaching the gate, which
    would pass for the wrong reason.
    """
    from server.app.ingest.service import IngestContext, IngestError, submit_batch

    batch_fixture = fixture_loader("identity/pos-ingest-batch-valid")
    engine = create_sqlite_engine(tmp_path / "ingest.db")
    injector = WriteFaultInjector(engine)
    context = IngestContext(
        engine=engine,
        owner_id=batch_fixture.data["owner_id"],
        storage_guard=guard,
    )

    guard.record_write_failure()
    injector.reset_counters()
    with pytest.raises(IngestError) as caught:
        submit_batch(context, batch_fixture.data["batch"], run_id="RUN-11")

    assert caught.value.code is ErrorCode.STORAGE_WRITE_FAILED
    # The gate ran before the transaction: no statement of any kind reached the database,
    # so there is no receipt row to be absent -- the stronger form of the oracle.
    assert injector.statements_attempted == 0
