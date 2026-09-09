"""E1/E2 — an attempt is never a result (I16, I14, I10).

Driven by ``acceptance/fixtures/ai/i-crash-after-provider-completion.json``, which is the
only oracle (SRC-PLAN §15). Its ``events`` are executed through the real service layer, its
``expected.rows`` row is compared column by column, its ``expected.counts`` are counted, and
its ``forbidden_effects`` are asserted **absent** rather than assumed absent.

Scenario anchor: SC28. Evidence level: E1 for the row/count oracles, E2 for the fault
injection at the end (``server/app/db/faults.py``).

The thing being defended
------------------------
The tempting bug is small and reasonable-looking: the worker died after the model answered,
so the answer existed; recover it from somewhere and write it down. Every step of that is
wrong under I16, and the system's honest position is narrower and more useful -- it does not
know whether the model ran, it will not claim no cost was incurred, and it will not turn a
record of a try into a record of a result.
"""

from __future__ import annotations

import copy
import os
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from server.app.analysis.repository import AnalysisRepository, new_ulid
from server.app.analysis.service import (
    LEASE_TTL_ANALYSIS_SECONDS,
    AnalysisContext,
    AnalysisError,
    ProviderChoice,
    TargetRequest,
    TaskSource,
    auto_rerun_unknown_attempt,
    claim_task,
    derived_source_fingerprint,
    enqueue_tasks,
    get_task_input,
    ledger_state,
    reap_expired_leases,
    report_attempt_unknown,
    submit_result,
    verify_task_lease,
)
from server.app.db import create_sqlite_engine
from server.app.db.faults import WriteFaultInjector

REPO_ROOT = Path(__file__).resolve().parents[2]

OWNER_ID = "01JW0WNER00000000000000000"
WORK_ID = "01JWRKA1000000000000000000"
WORK_VERSION_SOURCE_ID = "work_version:01JWVRA1000000000000000000"
GENERATION_ID = "01JAGENA100000000000000000"
ATTEMPT_ID = "01JATTA1000000000000000000"
LEASE_ID = "01JASGNA100000000000000000"
TASK_ID = "01JATASKA10000000000000000"
RUN_ID = "01JRUNA1000000000000000000"

#: Fixture ``i``'s timeline: claim at 18:00, provider answers at 18:01, worker dies at
#: 18:01:30, and the unknown outcome is filed at 18:20 -- after the lease has run out.
T_CLAIM = datetime(2026, 9, 6, 18, 0, 0, tzinfo=UTC)


# ------------------------------------------------------------------------------ harness


def _migrate(db_path: Path) -> None:
    """Run the real Alembic upgrade to ``head`` -- the migration IS the test's schema."""
    from alembic import command
    from alembic.config import Config

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(db_path)
    try:
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


class Clock:
    """A clock the test moves on purpose.

    Lease expiry is a *time* fact, and a test that could not move time would have to assert
    it by reaching into the row -- which would prove the assertion and not the behaviour.
    """

    def __init__(self, start: datetime) -> None:
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: int) -> None:
        self.now = self.now + timedelta(seconds=seconds)


class FakeProviderConfig:
    def __init__(self, *, enabled: bool = True) -> None:
        self.enabled = enabled

    def provider_for(self, task_type: str) -> ProviderChoice | None:
        return ProviderChoice(
            task_type=task_type,
            auth_family="api_key",
            provider_name="example-vendor-api",
            model_name="m-1",
            enabled=self.enabled,
        )


class FakeTaskInput:
    def sources_for(self, *, target_key: str) -> Sequence[TaskSource]:
        return [
            TaskSource(
                source_id=WORK_VERSION_SOURCE_ID,
                kind="work_version",
                text="Abstract nêu bộ dữ liệu là ImageNet-1k.",
                source_hash="sha256:" + "c" * 64,
                retrieved_at="2026-09-06T17:00:00.000Z",
            )
        ]


def _ids(*values: str) -> Any:
    from server.app.analysis.repository import new_ulid

    pending = list(values)

    def factory() -> str:
        return pending.pop(0) if pending else new_ulid()

    return factory


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    db_path = tmp_path / "rr.db"
    _migrate(db_path)
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at, failed_login_count) VALUES (:id, 1, 'owner', "
                "'Asia/Ho_Chi_Minh', '2026-09-01T00:00:00.000Z', 0)"
            ),
            {"id": OWNER_ID},
        )
        connection.execute(
            text(
                "INSERT INTO work (id, owner_id, metadata_state, identity_state, "
                "first_discovered_at, ingest_sequence, content_state, created_at) "
                "VALUES (:id, :owner_id, 'complete', 'active', "
                "'2026-09-05T00:00:00.000Z', 1, 'present', '2026-09-05T00:00:00.000Z')"
            ),
            {"id": WORK_ID, "owner_id": OWNER_ID},
        )
    yield engine
    engine.dispose()


@pytest.fixture
def clock() -> Clock:
    return Clock(T_CLAIM)


@pytest.fixture
def ctx(engine: Engine, clock: Clock) -> AnalysisContext:
    return AnalysisContext(
        engine=engine,
        owner_id=OWNER_ID,
        provider_config=FakeProviderConfig(),
        task_input=FakeTaskInput(),
        run_id=RUN_ID,
        clock=clock,
        id_factory=_ids(GENERATION_ID, TASK_ID, LEASE_ID, ATTEMPT_ID),
    )


def _derived_fingerprint() -> str:
    """What the server computes from ``FakeTaskInput``'s one source (``CR-TC-adapter-10``)."""
    return derived_source_fingerprint(list(FakeTaskInput().sources_for(target_key="")))


def _target() -> TargetRequest:
    """No fingerprint and no versions: the server derives all three (ADR-0008)."""
    return TargetRequest(target_kind="work", target_id=WORK_ID, task_type="summary")


def _document(ctx: AnalysisContext, task: dict[str, Any], fixture_loader) -> dict[str, Any]:
    """Fixture ``j``'s result, keyed with the key the **server** issued for this task.

    A worker cannot build the key -- four of its seven components exist only server-side --
    so it echoes the one ``analysis.get_task_input`` returned. That is what makes SV-01 a real
    comparison rather than a check of the worker against itself (``CR-TC-adapter-10``).
    """
    document = copy.deepcopy(
        fixture_loader("ai/j-same-key-resubmitted-one-result").expected["analysis_result"]
    )
    document["analysis_key"] = get_task_input(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
    )["analysis_key"]
    return document


def _claim(ctx: AnalysisContext, *, worker: str = "worker-1", request_id: str) -> dict[str, Any]:
    claimed = claim_task(
        ctx, worker_identity=worker, claim_request_id=request_id, task_types=["summary"]
    )
    assert claimed["task"] is not None, claimed
    task: dict[str, Any] = claimed["task"]
    return task


def _attempt_rows(engine: Engine) -> list[dict[str, Any]]:
    with engine.connect() as connection:
        return [
            dict(row)
            for row in connection.execute(
                text(
                    "SELECT id, owner_id, analysis_generation_id, attempt_number, outcome, "
                    "error_code, started_at, ended_at, worker_lease_id, cost_uncertain "
                    "FROM analysis_attempt ORDER BY attempt_number"
                )
            ).mappings()
        ]


def _valid_count(engine: Engine) -> int:
    with engine.connect() as connection:
        return AnalysisRepository().count_valid(connection, owner_id=OWNER_ID)


def _task_state(engine: Engine) -> str:
    with engine.connect() as connection:
        return str(connection.execute(text("SELECT state FROM analysis_task")).scalar_one())


def _crash_after_provider(ctx: AnalysisContext, clock: Clock) -> dict[str, Any]:
    """Fixture ``i`` events 1-3: claim, provider answers, worker dies before submitting.

    Nothing is written for events 2 and 3 on purpose. The provider call happens on the
    personal machine and the crash is the absence of the next call -- so the durable state
    after them is whatever the claim left behind, which is exactly what the fixture's
    ``timeline_ref`` (t2) says.
    """
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx, request_id="claim-1")
    clock.advance(90)  # 18:01:30 -- the worker dies here
    return task


# ------------------------------------------------------- fixture i: the unknown attempt


def test_a_crash_after_the_provider_ran_records_an_unknown_attempt(
    ctx, engine, clock, fixture_loader
) -> None:
    """Fixture ``i`` -- the expected row, column by column, and both counts.

    ``ended_at`` is ``NULL`` and ``cost_uncertain`` is ``true``: the system records what it
    does not know instead of guessing either way.
    """
    fixture = fixture_loader("ai/i-crash-after-provider-completion")
    expected = fixture.rows("analysis_attempt", block="expected")[0]

    task = _crash_after_provider(ctx, clock)
    # 18:20 -- past `expires_at` + `heartbeat_grace`, which is why the worker (restarted, or
    # its supervisor) is the one filing this.
    clock.advance(LEASE_TTL_ANALYSIS_SECONDS + 120)
    answer = report_attempt_unknown(
        ctx,
        task_id=task["task_id"],
        attempt_id=task["attempt_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
    )
    assert answer["state"] == "unknown_attempt"
    assert answer["cost_uncertain"] is True

    rows = _attempt_rows(engine)
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == expected["id"] == ATTEMPT_ID
    assert row["owner_id"] == expected["owner_id"]
    assert row["analysis_generation_id"] == expected["analysis_generation_id"]
    assert row["attempt_number"] == expected["attempt_number"]
    assert row["outcome"] == expected["outcome"]
    assert row["error_code"] == expected["error_code"]
    assert row["started_at"] == expected["started_at"]
    assert row["ended_at"] is expected["ended_at"] is None
    assert row["worker_lease_id"] == expected["worker_lease_id"]
    assert bool(row["cost_uncertain"]) is expected["cost_uncertain"] is True

    counts = fixture.expected["counts"]
    assert _valid_count(engine) == counts["analysis[status='valid']"]
    with engine.connect() as connection:
        uncertain = AnalysisRepository().count_cost_uncertain_attempts(
            connection, owner_id=OWNER_ID
        )
    assert uncertain == counts["analysis_attempt[cost_uncertain=true]"]
    assert _task_state(engine) == "unknown_attempt"


def test_the_query_for_a_result_never_returns_an_attempt(ctx, engine, clock) -> None:
    """I16, as the query the rest of the system actually runs.

    "Kết quả phân tích của target X" reads ``analysis WHERE status='valid'`` and nothing
    else. With one unknown attempt on the books, that query is empty -- and the attempt table
    is not.
    """
    task = _crash_after_provider(ctx, clock)
    clock.advance(LEASE_TTL_ANALYSIS_SECONDS + 120)
    report_attempt_unknown(
        ctx,
        task_id=task["task_id"],
        attempt_id=task["attempt_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
    )
    with engine.connect() as connection:
        repository = AnalysisRepository()
        found = repository.find_valid_by_key(
            connection,
            owner_id=OWNER_ID,
            target_key=f"work:{WORK_ID}",
            task_type="summary",
            source_fingerprint=_derived_fingerprint(),
            prompt_version="1.0.0",
            schema_version="0.1.0",
            generation_number=1,
        )
        attempts = repository.count_attempts(connection, owner_id=OWNER_ID)
    assert found is None
    assert attempts == 1
    assert _valid_count(engine) == 0


def test_a_late_submit_after_an_unknown_outcome_writes_no_result(
    ctx, engine, clock, fixture_loader
) -> None:
    """``forbidden_transitions`` row 1: ``unknown_attempt -> valid`` in every case.

    The fixture's ``forbidden_effects`` name the shape of the bug directly -- "khôi phục kết
    quả từ log của worker rồi ghi thành valid". Here the old worker comes back and submits a
    perfectly well-formed result; it is refused on the lease, and no row appears.
    """
    task = _crash_after_provider(ctx, clock)
    document = _document(ctx, task, fixture_loader)
    clock.advance(LEASE_TTL_ANALYSIS_SECONDS + 120)
    report_attempt_unknown(
        ctx,
        task_id=task["task_id"],
        attempt_id=task["attempt_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
    )

    with pytest.raises(AnalysisError) as raised:
        submit_result(
            ctx,
            task_id=task["task_id"],
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"],
            result=document,
        )
    assert raised.value.code is ErrorCode.WORKER_LEASE_EXPIRED
    assert raised.value.http_status == 412
    assert _valid_count(engine) == 0
    assert _task_state(engine) == "unknown_attempt"


def test_one_automatic_rerun_writes_a_new_attempt_and_edits_no_old_one(ctx, engine, clock) -> None:
    """T-AN-09 -- exactly one, and the evidence of the first try is left alone.

    ``analysis_unknown_attempt_auto_rerun`` is 1 and it **consumes** a unit of
    ``analysis_attempts_per_item``, so the total number of model calls for one
    ``(key, generation)`` still cannot exceed 2 (RPC-08). The first attempt keeps
    ``cost_uncertain = true`` for good: the money may have been spent whatever happens next.
    """
    task = _crash_after_provider(ctx, clock)
    clock.advance(LEASE_TTL_ANALYSIS_SECONDS + 120)
    report_attempt_unknown(
        ctx,
        task_id=task["task_id"],
        attempt_id=task["attempt_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
    )
    assert auto_rerun_unknown_attempt(ctx, task_id=task["task_id"]) == "pending"

    second = _claim(ctx, request_id="claim-2")
    rows = _attempt_rows(engine)
    assert [row["attempt_number"] for row in rows] == [1, 2]
    assert rows[0]["id"] == ATTEMPT_ID
    assert rows[0]["outcome"] == "timeout_unknown"
    assert bool(rows[0]["cost_uncertain"]) is True
    assert rows[0]["ended_at"] is None
    assert rows[1]["id"] == second["attempt_id"] != ATTEMPT_ID
    assert _valid_count(engine) == 0


def test_a_second_unknown_outcome_fails_the_item_instead_of_running_again(
    ctx, engine, clock
) -> None:
    """T-AN-10 -- after the one automatic re-run, only the Owner may spend more.

    ``failed`` here means "this item has no analysis", which I13 keeps distinct from "this
    item has no research". A second automatic re-run would spend money on a loop nobody
    asked for.
    """
    task = _crash_after_provider(ctx, clock)
    clock.advance(LEASE_TTL_ANALYSIS_SECONDS + 120)
    report_attempt_unknown(
        ctx,
        task_id=task["task_id"],
        attempt_id=task["attempt_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
    )
    auto_rerun_unknown_attempt(ctx, task_id=task["task_id"])
    second = _claim(ctx, request_id="claim-2")

    clock.advance(LEASE_TTL_ANALYSIS_SECONDS + 120)
    report_attempt_unknown(
        ctx,
        task_id=second["task_id"],
        attempt_id=second["attempt_id"],
        lease_id=second["lease_id"],
        lease_epoch=second["lease_epoch"],
    )
    assert auto_rerun_unknown_attempt(ctx, task_id=task["task_id"]) == "failed"
    assert _task_state(engine) == "failed"
    assert len(_attempt_rows(engine)) == 2  # never more than the budget allows
    assert _valid_count(engine) == 0


def _seed_coverage_window(engine: Engine, fixture_loader) -> str:
    """Insert fixture ``reporting/e``'s own ``coverage_window`` row and return its id.

    ``EngineBoundPendingLedger`` anchors every pending row to a coverage window and raises
    rather than inventing one, so a ledger test needs a real window. It is taken from the
    fixture that states the pending/late-discovery case rather than made up here.
    """
    window = fixture_loader("reporting/e-late-analysis-pending-then-late-discovery").rows(
        "coverage_window"
    )[0]
    with engine.begin() as connection:
        connection.execute(
            text(
                'INSERT INTO coverage_window (id, owner_id, "sequence", window_from, '
                "window_to, ingest_sequence_from, ingest_sequence_to, "
                "predecessor_window_id, report_id, advanced_at) "
                "VALUES (:id, :owner_id, :seq, :window_from, :window_to, :seq_from, "
                ":seq_to, NULL, NULL, :window_to)"
            ),
            {
                "id": window["id"],
                "owner_id": OWNER_ID,
                "seq": window["sequence"],
                "window_from": window["window_from"],
                "window_to": window["window_to"],
                "seq_from": window["ingest_sequence_from"],
                "seq_to": window["ingest_sequence_to"],
            },
        )
    return str(window["id"])


def _wire_real_ledger(ctx: AnalysisContext, engine: Engine, *, busy_timeout_ms: int = 5000):  # type: ignore[no-untyped-def]
    """Attach ``MOD-report-service``'s real ``PendingLedgerPort`` implementation.

    W4B's ``EngineBoundPendingLedger``, not a double: the point of these two tests is the
    seam between the two modules, and a stub would only prove the stub works.

    The adapter gets an engine of its own so a test can give it a short ``busy_timeout_ms``.
    Nothing needs that today -- ``_fail_task`` hands the port its own connection
    (``CR-TC-BACKFILL-02b``), so no second connection contends for the write lock -- but the
    knob stays: it is what turned "the ledger write hangs" from a five-second stall into a
    fifth-of-a-second measurement while the port was still connection-less, and a future
    caller that forgets to pass a connection deserves to find out quickly rather than slowly.
    """
    from sqlalchemy import event

    from server.app.report.pending import EngineBoundPendingLedger, current_window_provider

    ledger_engine = create_sqlite_engine(engine.url.database or ":memory:")

    @event.listens_for(ledger_engine, "connect")
    def _short_busy_timeout(dbapi_connection, _record):  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute(f"PRAGMA busy_timeout={busy_timeout_ms}")
        finally:
            cursor.close()

    ctx.pending_ledger = EngineBoundPendingLedger(
        engine=ledger_engine,
        owner_id=OWNER_ID,
        window_provider=current_window_provider(ledger_engine, OWNER_ID),
        id_factory=new_ulid,
    )
    return ledger_engine


def test_the_pending_ledger_port_is_wired_and_speaks_this_card_s_vocabulary(
    ctx, engine, fixture_loader
) -> None:
    """B04/B17 — the half of the obligation that W4A/W4B made real.

    ``pending_item_ledger`` now exists (revision ``0010_tc_report_coverage_publish_cas``) and
    ``server.app.report.pending`` implements the ``PendingLedgerPort`` this service has been
    carrying as ``None`` since Phase 3. Two things are checked here and neither is a stub:

    * :func:`ledger_state` stops reporting the port as unwired — the honest signal it was
      built to give, now flipping the other way;
    * the two ``reason`` values this card produces, ``analysis_failed`` (budget spent on
      invalid output, T-AN-07) and ``analysis_unknown`` (budget spent on outcomes nobody
      knows, T-AN-10), are both members of the closed enum W4B enforces. Two modules agreeing
      on a vocabulary is exactly the kind of thing that is true today and quietly false after
      one refactor, so it is asserted rather than assumed.

    The row that comes back carries the contract's shape: ``state = 'pending'`` (not resolved,
    not abandoned — §5.3 reserves abandonment for an explicit Owner act) and
    ``first_pending_window_id`` pinned to the window that *first* missed the item, which is
    what the "phát hiện muộn, thuộc kỳ #N" label renders. A second call for the same target is
    idempotent through ``ux_pending_owner_target_open``.
    """
    from server.app.report.pending import REASONS

    window_id = _seed_coverage_window(engine, fixture_loader)
    _wire_real_ledger(ctx, engine)
    assert ledger_state(ctx)["pending_ledger_wired"] is True
    assert {"analysis_failed", "analysis_unknown"} <= REASONS

    target_key = f"work:{WORK_ID}"
    ctx.pending_ledger.record_pending(target_key=target_key, reason="analysis_unknown")
    ctx.pending_ledger.record_pending(target_key=target_key, reason="analysis_unknown")

    with engine.connect() as connection:
        rows = (
            connection.execute(
                text(
                    "SELECT target_key, reason, state, first_pending_window_id "
                    "FROM pending_item_ledger WHERE owner_id = :owner_id"
                ),
                {"owner_id": OWNER_ID},
            )
            .mappings()
            .all()
        )
    assert len(rows) == 1, "ux_pending_owner_target_open should make the second call a no-op"
    assert rows[0]["target_key"] == target_key
    assert rows[0]["reason"] == "analysis_unknown"
    assert rows[0]["state"] == "pending"
    assert rows[0]["first_pending_window_id"] == window_id


def test_a_failed_item_is_recorded_in_the_pending_item_ledger(
    ctx, engine, clock, fixture_loader
) -> None:
    """B04/B17 / I06 — a budget-exhausted item must not simply vanish from the report.

    The whole obligation, end to end and now really asserted: two unknown outcomes exhaust
    ``analysis_attempts_per_item``, ``auto_rerun_unknown_attempt`` moves the task to
    ``failed``, and ``_fail_task`` puts the item in ``pending_item_ledger`` so period N+1 can
    still carry it even though its ``discovered_at`` has fallen behind the cursor. Without the
    ledger row the item is unreachable the moment coverage advances, which is the I06 failure
    arriving quietly rather than loudly.

    This was ``xfail(strict=True, run=True, raises=OperationalError)`` for one packet, pinned
    to a *measured* failure: the port took no connection, so W4B's adapter opened a second one
    and deadlocked against the write lock ``_fail_task`` already held. ``CR-TC-BACKFILL-02b``
    gave the port an optional ``connection``, ``_fail_task`` now passes its own, and the
    assertion below is the ordinary one. Pinning the failure mode is what made the flip
    visible: a plain ``xfail`` would have gone green on its own and told nobody.

    The row lands **inside the same transaction** as the ``failed`` state that caused it, so
    there is no window in which an item is marked failed with nothing in the ledger.
    """
    _seed_coverage_window(engine, fixture_loader)
    _wire_real_ledger(ctx, engine)

    task = _crash_after_provider(ctx, clock)
    clock.advance(LEASE_TTL_ANALYSIS_SECONDS + 120)
    report_attempt_unknown(
        ctx,
        task_id=task["task_id"],
        attempt_id=task["attempt_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
    )
    auto_rerun_unknown_attempt(ctx, task_id=task["task_id"])
    second = _claim(ctx, request_id="claim-2")
    clock.advance(LEASE_TTL_ANALYSIS_SECONDS + 120)
    report_attempt_unknown(
        ctx,
        task_id=second["task_id"],
        attempt_id=second["attempt_id"],
        lease_id=second["lease_id"],
        lease_epoch=second["lease_epoch"],
    )

    # `_fail_task` reaches the ledger on its own connection, so this commits as one unit.
    assert auto_rerun_unknown_attempt(ctx, task_id=task["task_id"]) == "failed"
    assert _task_state(engine) == "failed"

    with engine.connect() as connection:
        pending = (
            connection.execute(
                text(
                    "SELECT target_key, reason, state FROM pending_item_ledger "
                    "WHERE owner_id = :owner_id"
                ),
                {"owner_id": OWNER_ID},
            )
            .mappings()
            .all()
        )
    assert len(pending) == 1
    assert pending[0]["target_key"] == f"work:{WORK_ID}"
    assert pending[0]["reason"] == "analysis_unknown"
    assert pending[0]["state"] == "pending"


# --------------------------------------------------------------- I10: the stale worker


def test_a_worker_whose_lease_was_swept_commits_nothing(ctx, engine, clock, fixture_loader) -> None:
    """T-AN-11 / I10 -- the epoch is the fence, and the old attempt is kept as evidence.

    The old worker may well have called the provider. What it loses is the right to commit;
    what it does not lose is the record that it tried, because that record is the only
    evidence that money may have been spent.
    """
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    first = _claim(ctx, worker="worker-1", request_id="claim-1")
    # Built while the first lease is still live: the old worker really did get a task input,
    # which is what makes its later submit a stale-lease refusal and not a malformed request.
    document = _document(ctx, first, fixture_loader)

    clock.advance(LEASE_TTL_ANALYSIS_SECONDS + 120)
    assert reap_expired_leases(ctx) == [first["task_id"]]
    assert _task_state(engine) == "pending"

    second = _claim(ctx, worker="worker-2", request_id="claim-2")
    assert second["lease_epoch"] == first["lease_epoch"] + 1

    with pytest.raises(AnalysisError) as raised:
        submit_result(
            ctx,
            task_id=first["task_id"],
            lease_id=first["lease_id"],
            lease_epoch=first["lease_epoch"],
            result=document,
        )
    assert raised.value.code is ErrorCode.STALE_LEASE
    assert raised.value.http_status == 409
    assert _valid_count(engine) == 0

    rows = _attempt_rows(engine)
    assert rows[0]["outcome"] == "cancelled_stale_lease"
    assert rows[0]["error_code"] == ErrorCode.WORKER_LEASE_EXPIRED.value
    assert bool(rows[0]["cost_uncertain"]) is True  # kept: the cost may be real


def test_a_credential_is_refused_to_a_worker_that_does_not_hold_the_lease(
    ctx, engine, clock
) -> None:
    """ISO-05 / ADR-0010 §1 -- ``secret.issue_task_credential`` asks, and the answer is no.

    The secret service does not own the lease, so it consults the module that does. Three
    refusals are asserted here because each is a different way in: the wrong worker, a stale
    epoch, and a provider whose isolation has not been verified. The positive case is scoped
    to one task and one provider, and there is no argument that widens it.
    """
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx, worker="worker-1", request_id="claim-1")

    scope = verify_task_lease(
        ctx,
        task_id=task["task_id"],
        attempt_id=task["attempt_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        worker_identity="worker-1",
    )
    assert scope.task_id == task["task_id"]
    assert scope.provider_name == "example-vendor-api"

    with pytest.raises(AnalysisError) as wrong_worker:
        verify_task_lease(
            ctx,
            task_id=task["task_id"],
            attempt_id=task["attempt_id"],
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"],
            worker_identity="worker-2",
        )
    assert wrong_worker.value.code is ErrorCode.STALE_LEASE

    with pytest.raises(AnalysisError) as stale_epoch:
        verify_task_lease(
            ctx,
            task_id=task["task_id"],
            attempt_id=task["attempt_id"],
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"] - 1,
            worker_identity="worker-1",
        )
    assert stale_epoch.value.code is ErrorCode.STALE_LEASE

    # B13/ADR-0010 §3: an adapter whose isolation is unverified stays disabled, and a
    # disabled adapter is never handed a credential -- the default, not a punishment.
    ctx.provider_config = FakeProviderConfig(enabled=False)
    with pytest.raises(AnalysisError) as disabled:
        verify_task_lease(
            ctx,
            task_id=task["task_id"],
            attempt_id=task["attempt_id"],
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"],
            worker_identity="worker-1",
        )
    assert disabled.value.code is ErrorCode.AI_PROVIDER_UNAVAILABLE


# -------------------------------------------------- a rejected result is still not a result


def test_a_semantically_invalid_result_becomes_an_attempt_not_a_row(
    ctx, engine, clock, fixture_loader
) -> None:
    """T-AN-04 and the forbidden transition ``running -> valid`` on a schema-only pass.

    The document below passes ``analysis-result.schema.json`` in full and fails SV-02: it
    cites a source that was never granted for this run. "Valid JSON" is explicitly not the
    whole contract, so the result is refused, the try is recorded as ``schema_invalid``, and
    ``analysis`` stays empty.
    """
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx, request_id="claim-1")
    document = _document(ctx, task, fixture_loader)
    document["result"]["statements"][0]["citation_refs"] = [
        "work_version:01JWVRZZZZ000000000000000Z"
    ]

    with pytest.raises(AnalysisError) as raised:
        submit_result(
            ctx,
            task_id=task["task_id"],
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"],
            result=document,
        )
    assert raised.value.code is ErrorCode.AI_OUTPUT_INVALID
    assert raised.value.http_status == 422
    assert raised.value.details_safe is not None
    assert raised.value.details_safe["validation_failure_kind"] == "citation_unknown_source"
    # The envelope carries a category, never the offending text (errors.yaml §redaction).
    assert "01JWVRZZZZ" not in str(raised.value.details_safe)

    assert _valid_count(engine) == 0
    rows = _attempt_rows(engine)
    assert rows[0]["outcome"] == "schema_invalid"
    assert rows[0]["error_code"] == ErrorCode.AI_OUTPUT_INVALID.value
    assert bool(rows[0]["cost_uncertain"]) is False  # a wrong answer is a KNOWN outcome
    assert _task_state(engine) == "retry_wait"


def test_usage_is_never_written_as_zero_when_it_is_unknown(ctx, engine, fixture_loader) -> None:
    """I14 -- the CLI path reports no token counts, and that is legitimate (REQ-D44).

    Two halves: ``unknown = true`` stores ``NULL`` (not ``0``), and the one shape that could
    produce a stand-in zero -- ``unknown = false`` with a count missing -- is refused.
    """
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx, request_id="claim-1")
    document = _document(ctx, task, fixture_loader)
    document["usage"] = {
        "unknown": True,
        "tokens_in": None,
        "tokens_out": None,
        "cost_micro_usd": None,
    }
    submit_result(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        result=document,
    )
    with engine.connect() as connection:
        row = (
            connection.execute(text("SELECT usage_tokens_in, usage_tokens_out FROM analysis"))
            .mappings()
            .one()
        )
    assert row["usage_tokens_in"] is None
    assert row["usage_tokens_out"] is None


# --------------------------------------------------------------------------- E2: storage


def test_a_full_disk_during_submit_acknowledges_nothing(ctx, engine, fixture_loader) -> None:
    """E2 -- ``STORAGE_WRITE_FAILED`` means nothing was persisted and nothing was ACKed.

    Injected through ``server/app/db/faults.py``. The claim happens before the fault is
    armed; the submit happens inside it. Afterwards the fault is lifted and the row counts
    are read back: a transaction that rolled back must leave the same numbers behind, and the
    task must still be claimable rather than stranded.
    """
    enqueue_tasks(ctx, [_target()], caller_module="MOD-report-service")
    task = _claim(ctx, request_id="claim-1")
    document = _document(ctx, task, fixture_loader)

    injector = WriteFaultInjector(engine)
    with injector.disk_full(), pytest.raises(AnalysisError) as raised:
        submit_result(
            ctx,
            task_id=task["task_id"],
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"],
            result=document,
        )
    assert raised.value.code is ErrorCode.STORAGE_WRITE_FAILED
    assert raised.value.http_status == 503

    assert _valid_count(engine) == 0
    assert _task_state(engine) == "running"  # still held, not stranded and not finished
    rows = _attempt_rows(engine)
    assert len(rows) == 1
    assert rows[0]["outcome"] == "timeout_unknown"  # never concluded, so never `accepted`

    # And once the disk is back, the same submit commits -- the failure was transient and the
    # server did not poison the task on its way out.
    receipt = submit_result(
        ctx,
        task_id=task["task_id"],
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        result=document,
    )
    assert receipt["status"] == "committed"
    assert _valid_count(engine) == 1
