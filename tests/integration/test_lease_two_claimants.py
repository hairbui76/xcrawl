"""E1/E2 — SC20/SC35: two claimants, one winner; a stale epoch writes nothing; cancel from anywhere.

Card §12 gives the reviewer one question: *"có đường nào để worker epoch cũ ghi được dữ liệu
không"* — is there any path by which a worker holding an old epoch can write? This file is the
answer, and it tries to find one from four directions:

1. through the service, at the epoch check
   (:func:`test_a_stale_heartbeat_is_refused_and_renews_nothing`);
2. through HTTP, so the router does not open a second path
   (:func:`test_a_stale_heartbeat_over_http_is_refused_with_the_registered_envelope`);
3. around the service entirely, straight into SQLite, where
   ``ux_assignment_lease_one_held`` has to refuse it
   (:func:`test_the_database_itself_refuses_a_second_held_lease`);
4. after the fact, by checking that a refused call left every byte of the two tables alone.

Fixtures used as oracles:

``collection/f-two-workers-claim-same-assignment.json``  A's beat and A's batch after B wins
``collection/g-schedule-due-claim.json``                 registration grants no lease; the
                                                        second claim is ``no_work``, not an error
``collection/k-cancel-from-every-non-terminal.json``     cancel from all five non-terminal states
``recovery/b-post-restore-stale-lease-rejected.json``    every lease is stale after a restore
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError

from server.app.auth.middleware import PrincipalKind, TokenRegistry
from server.app.db import create_sqlite_engine
from server.app.jobs.lease import (
    HEARTBEAT_GRACE_SECONDS,
    LEASE_TTL_COLLECTOR_SECONDS,
    JobError,
)
from server.app.jobs.service import (
    JobContext,
    cancel_run,
    claim_assignment,
    heartbeat,
    register_capabilities,
    release_assignment,
    report_stop,
    resume_run,
    run_now,
    sweep_expired_leases,
)
from server.app.main import create_app
from server.app.scheduler.evaluator import ScheduleSettings

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "acceptance" / "fixtures"

OWNER_ID = "01JW0WNER00000000000000000"
COLLECTOR_TOKEN = "collector-token-for-tests"
WORKER_A = "01JWORKERA0000000000000000"
WORKER_B = "01JWORKERB0000000000000000"
WIRE_HEADERS = {
    "X-Schema-Version": CONTRACT_SCHEMA_VERSION,
    "X-Request-Id": "01J0000000000000000000000Z",
}
CAPABILITIES = {
    "collector_online": True,
    "chrome_profile_ready": True,
    "x_session_state": "ok",
}


# --- harness ----------------------------------------------------------------------------------


def _upgrade(db_path: Path) -> None:
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


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    db_path = tmp_path / "radar.db"
    _upgrade(db_path)
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at, password_hash, password_updated_at, failed_login_count, "
                "locked_until) VALUES (:id, 1, 'owner', 'Asia/Ho_Chi_Minh', "
                "'2026-09-01T00:00:00.000Z', 'x', '2026-09-01T00:00:00.000Z', 0, NULL)"
            ),
            {"id": OWNER_ID},
        )
    try:
        yield engine
    finally:
        engine.dispose()


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **delta: float) -> None:
        self.now = self.now + timedelta(**delta)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 9, 7, 8, 0, tzinfo=UTC))


@pytest.fixture
def ctx(engine: Engine, clock: FakeClock) -> JobContext:
    counter = {"n": 0}

    def ids() -> str:
        counter["n"] += 1
        return f"01JTEST{counter['n']:019d}"[:26]

    return JobContext(
        engine=engine,
        owner_id=OWNER_ID,
        settings=ScheduleSettings(slots_local=("08:00", "20:00"), timezone_iana="Asia/Ho_Chi_Minh"),
        clock=clock,
        id_factory=ids,
    )


def load(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURE_ROOT / f"{name}.json").read_text(encoding="utf-8"))
    return data


def rows(engine: Engine, sql: str, **params: Any) -> list[tuple[Any, ...]]:
    with engine.connect() as connection:
        return [tuple(row) for row in connection.execute(text(sql), params)]


def count(engine: Engine, sql: str, **params: Any) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql), params).scalar_one())


def held_leases(engine: Engine) -> int:
    return count(
        engine,
        "SELECT COUNT(*) FROM assignment_lease WHERE owner_id = :o AND state = 'held'",
        o=OWNER_ID,
    )


def lease_snapshot(engine: Engine) -> list[tuple[Any, ...]]:
    """Every column of every lease. "Nothing changed" is measured, not inferred."""
    return rows(
        engine,
        "SELECT id, run_id, job_id, worker_identity, lease_epoch, expires_at, state "
        "FROM assignment_lease ORDER BY id",
    )


def claim_body(worker: str, key: str) -> dict[str, Any]:
    return {
        "claim_request": {
            "request_id": "01JREQ0000000000000000000A",
            "schema_version": "0.1.0",
            "claim_request_id": key,
            "worker_instance_id": worker,
            "worker_kind": "collector",
            "capabilities": CAPABILITIES,
            "max_assignments": 1,
        }
    }


def start_run(ctx: JobContext) -> str:
    return str(run_now(ctx, request_id="01JREQ0000000000000000000A")["run_id"])


# --- registration grants nothing (LM-01) ------------------------------------------------------


def test_registration_grants_no_lease(ctx, engine) -> None:
    """Fixture ``collection/g`` event 1 pins ``lease_granted: false`` as an explicit field.

    ``contracts/ops/deployment.md`` §7 step 6: registration is not work. If it granted a lease,
    a worker could start on its own and I10's single-writer guarantee would begin at the wrong
    moment.
    """
    fixture = load("collection/g-schedule-due-claim")
    pinned = next(
        event["response_body"]
        for event in fixture["events"]
        if event["operation"] == "worker.register_capabilities"
    )
    assert pinned["lease_granted"] is False

    answer = register_capabilities(
        ctx,
        {
            "worker_instance_id": WORKER_A,
            "worker_kind": "collector",
            "registration_seq": 7,
            "capabilities": CAPABILITIES,
        },
    )

    assert answer["lease_granted"] is False
    assert answer["heartbeat_interval_s"] == pinned["heartbeat_interval_s"] == 30
    assert held_leases(engine) == 0
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM assignment_lease",
        )
        == 0
    )


def test_a_lower_registration_sequence_is_ignored_not_rejected(ctx, engine) -> None:
    """``ports.yaml``: "seq lùi bị bỏ qua".

    Out-of-order registrations over a flaky link are normal; answering 409 would make the
    worker retry a message that is genuinely obsolete. The stored row keeps the higher seq.
    """
    register_capabilities(
        ctx,
        {
            "worker_instance_id": WORKER_A,
            "worker_kind": "collector",
            "registration_seq": 7,
            "capabilities": {**CAPABILITIES, "x_session_state": "ok"},
        },
    )
    answer = register_capabilities(
        ctx,
        {
            "worker_instance_id": WORKER_A,
            "worker_kind": "collector",
            "registration_seq": 3,
            "capabilities": {**CAPABILITIES, "x_session_state": "expired"},
        },
    )

    assert answer.get("superseded") is True
    stored = json.loads(
        rows(
            engine,
            "SELECT capabilities FROM worker_registration WHERE worker_identity = :w",
            w=WORKER_A,
        )[0][0]
    )
    assert stored["registration_seq"] == 7
    assert stored["x_session_state"] == "ok", "the stale registration overwrote the fresh one"


def test_a_worker_never_declares_embedding(ctx, engine) -> None:
    """D50/B12: "Worker **không bao giờ** khai ``embedding``" (``ports.yaml``, worker health).

    Dropped rather than rejected: the claim is meaningless, not malicious, and a 400 would stop
    a worker registering at all over a field nobody reads.
    """
    register_capabilities(
        ctx,
        {
            "worker_instance_id": WORKER_A,
            "worker_kind": "collector",
            "registration_seq": 1,
            "capabilities": {**CAPABILITIES, "embedding": True, "embedding_supported": True},
        },
    )
    stored = json.loads(
        rows(
            engine,
            "SELECT capabilities FROM worker_registration WHERE worker_identity = :w",
            w=WORKER_A,
        )[0][0]
    )
    assert "embedding" not in stored
    assert "embedding_supported" not in stored


# --- SC20: two claimants ----------------------------------------------------------------------


def test_the_second_claimant_gets_no_work_not_an_error(ctx, engine) -> None:
    """Fixture ``collection/g`` event 3: 200 with ``assignment_already_held``.

    A ``no_work`` answer, not a failure. A worker polling every 45 s must not report "somebody
    else has the job" as an error, and the wire schema has a reason for exactly this case.
    """
    start_run(ctx)
    first = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    assert "assignment" in first

    second = claim_assignment(ctx, claim_body(WORKER_B, "claim-b"))

    assert "no_work" in second
    assert second["no_work"]["reason"] == "assignment_already_held"
    assert second["no_work"]["retry_after_ms"] == 45000
    assert held_leases(engine) == 1


def test_after_the_first_lease_expires_the_second_claimant_wins_at_a_higher_epoch(
    ctx, engine, clock
) -> None:
    """Fixture ``collection/f`` event 1: *"server tăng epoch 1→2 và cấp lease mới."*

    The clock is moved past ``expires_at + heartbeat_grace`` — the grace is part of the
    definition (LM-05), so moving only to ``expires_at`` must **not** be enough, and the first
    half of this test asserts that too.
    """
    start_run(ctx)
    first = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    assert first["assignment"]["lease"]["lease_epoch"] == 1

    clock.advance(seconds=LEASE_TTL_COLLECTOR_SECONDS + 1)
    too_early = claim_assignment(ctx, claim_body(WORKER_B, "claim-b"))
    assert "no_work" in too_early, "the grace period was not honoured"

    clock.advance(seconds=HEARTBEAT_GRACE_SECONDS + 1)
    second = claim_assignment(ctx, claim_body(WORKER_B, "claim-b"))

    assert second["assignment"]["lease"]["lease_epoch"] == 2
    assert held_leases(engine) == 1
    states = dict(rows(engine, "SELECT lease_epoch, state FROM assignment_lease"))
    assert states == {1: "expired", 2: "held"}


def test_a_stale_heartbeat_is_refused_and_renews_nothing(ctx, engine, clock) -> None:
    """Fixture ``collection/f`` event 2: 409 ``STALE_LEASE``, *"KHÔNG gia hạn lease, KHÔNG đổi
    dữ liệu."*

    Both halves are asserted. The code alone would be satisfied by an implementation that
    renewed the lease and then raised; the byte-for-byte comparison of the whole
    ``assignment_lease`` table is what rules that out.
    """
    start_run(ctx)
    first = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    old_lease = first["assignment"]["lease"]

    clock.advance(seconds=LEASE_TTL_COLLECTOR_SECONDS + HEARTBEAT_GRACE_SECONDS + 2)
    claim_assignment(ctx, claim_body(WORKER_B, "claim-b"))
    before = lease_snapshot(engine)

    with pytest.raises(JobError) as raised:
        heartbeat(
            ctx,
            {
                "heartbeat_request": {
                    "lease_id": old_lease["lease_id"],
                    "lease_epoch": old_lease["lease_epoch"],
                }
            },
        )

    assert raised.value.code is ErrorCode.STALE_LEASE
    assert lease_snapshot(engine) == before
    assert held_leases(engine) == 1


def test_the_stale_lease_envelope_is_the_registered_one(ctx) -> None:
    """Card §7 and ``contracts/errors.yaml``: the seven fields, and only safe details.

    ``details_safe_keys`` for ``STALE_LEASE`` are ``job_id``, ``lease_epoch_seen`` and
    ``lease_epoch_current`` — not the shorter names a reader might expect — so the envelope is
    asserted against the registry rather than against intuition.
    """
    start_run(ctx)
    first = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    lease = first["assignment"]["lease"]

    with pytest.raises(JobError) as raised:
        heartbeat(
            ctx,
            {"heartbeat_request": {"lease_id": lease["lease_id"], "lease_epoch": 999}},
        )

    envelope = raised.value.envelope("01J0000000000000000000000Z")
    assert envelope["code"] == ErrorCode.STALE_LEASE.value
    assert envelope["scope"] == SCOPE[ErrorCode.STALE_LEASE]
    assert envelope["retry_class"] == RETRY_CLASS[ErrorCode.STALE_LEASE]
    assert set(envelope["details_safe"]) <= {"job_id", "lease_epoch_seen", "lease_epoch_current"}
    assert envelope["details_safe"]["lease_epoch_seen"] == 999
    assert envelope["details_safe"]["lease_epoch_current"] == 1
    assert raised.value.http_status == 409
    # SRC-PLAN §5.1: no transcript, no key, no cookie anywhere in the envelope.
    serialised = json.dumps(envelope)
    for forbidden in ("token", "cookie", "password", "secret"):
        assert forbidden not in serialised.lower()


def test_a_stale_heartbeat_over_http_is_refused_with_the_registered_envelope(engine, clock) -> None:
    """The same refusal through the router, so HTTP is not a second path around the check.

    Card §12's question has to be answered at every layer that can write, and the router is one
    of them. The collector already posts to this exact path
    (``collector/app/client.py``), so this is also the integration point with that card.
    """
    counter = {"n": 0}

    def ids() -> str:
        counter["n"] += 1
        return f"01JTEST{counter['n']:019d}"[:26]

    app = create_app()
    app.state.engine = engine
    app.state.token_registry = TokenRegistry({COLLECTOR_TOKEN: PrincipalKind.COLLECTOR})
    app.state.job_context = JobContext(
        engine=engine,
        owner_id=OWNER_ID,
        settings=ScheduleSettings(slots_local=("08:00", "20:00"), timezone_iana="Asia/Ho_Chi_Minh"),
        clock=clock,
        id_factory=ids,
    )
    ctx = app.state.job_context
    start_run(ctx)
    claimed = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    lease = claimed["assignment"]["lease"]
    assignment_id = claimed["assignment"]["assignment_id"]
    before = lease_snapshot(engine)

    with TestClient(app) as client:
        response = client.post(
            f"/v1/workers/assignments/{assignment_id}/heartbeat",
            headers={**WIRE_HEADERS, "Authorization": f"Bearer {COLLECTOR_TOKEN}"},
            json={
                "heartbeat_request": {
                    "lease_id": lease["lease_id"],
                    "lease_epoch": lease["lease_epoch"] - 1,
                }
            },
        )

    assert response.status_code == 409
    body = response.json()
    assert body["code"] == ErrorCode.STALE_LEASE.value
    assert body["correlation_id"]
    assert lease_snapshot(engine) == before


def test_the_database_itself_refuses_a_second_held_lease(ctx, engine) -> None:
    """Around the service entirely: raw SQL, and ``ux_assignment_lease_one_held`` refuses.

    Fixture ``collection/f`` lists "Cấp hai lease ``held`` cho cùng job" as a forbidden effect.
    This is what makes "exactly one winner" a property of the schema rather than of the order
    two transactions happened to run in — the index this card's migration added to the
    custodian table (LM-02).
    """
    start_run(ctx)
    claimed = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    job_id = claimed["assignment"]["assignment_id"]
    run_id = claimed["assignment"]["run_id"]

    with pytest.raises(IntegrityError) as raised, engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO assignment_lease (id, owner_id, run_id, job_id, worker_identity, "
                "lease_epoch, expires_at, state) VALUES ('01JSNEAK000000000000000000', :o, "
                ":r, :j, 'sneaky', 99, '2026-09-07T09:00:00.000Z', 'held')"
            ),
            {"o": OWNER_ID, "r": run_id, "j": job_id},
        )
    assert "UNIQUE constraint failed" in str(raised.value)
    assert held_leases(engine) == 1


def test_a_worker_missing_a_capability_is_not_given_work(ctx, engine) -> None:
    """``ports.yaml``: "server chỉ giao assignment mà worker khai đủ capability".

    ``x_session_state`` must be the literal ``"ok"``: ``unknown`` is not "probably fine". I13's
    three-way distinction applies to a session as much as to a display.
    """
    start_run(ctx)
    body = claim_body(WORKER_A, "claim-a")
    body["claim_request"]["capabilities"] = {**CAPABILITIES, "x_session_state": "unknown"}

    answer = claim_assignment(ctx, body)

    assert answer["no_work"]["reason"] == "capability_not_met"
    assert held_leases(engine) == 0


def test_a_run_waiting_for_the_owner_is_not_claimable(ctx, engine) -> None:
    """``no_work`` reasons ``run_needs_user`` / ``run_blocked``.

    The worker must not pick up a run the Owner has to act on — that is T-RUN-11 seen from the
    worker's side, and claiming it would silently clear a challenge nobody resolved.
    """
    run_id = start_run(ctx)
    for status, reason in (("needs_user", "run_needs_user"), ("blocked", "run_blocked")):
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE run SET status = :s, unblock_condition_vi = :u WHERE id = :id"),
                {"s": status, "u": "owner must act" if status == "blocked" else None, "id": run_id},
            )
        answer = claim_assignment(ctx, claim_body(WORKER_A, f"claim-{status}"))
        assert answer["no_work"]["reason"] == reason, status
        assert held_leases(engine) == 0


# --- LM-08: after a restore, every lease is stale ----------------------------------------------


def test_every_lease_is_stale_after_a_restore_until_reconciliation(ctx, engine) -> None:
    """Fixture ``recovery/b`` + LM-08 + NC-10.

    The epoch still matches and the TTL has not run out, and the lease is refused anyway: the
    clock jumped and the worker that held it may no longer exist. Only
    ``backup.reconcile_after_restore`` clears the flag, which is ``TC-backup-restore-drill``'s
    to implement — this card provides the flag and honours it.
    """
    start_run(ctx)
    claimed = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    lease = claimed["assignment"]["lease"]
    before = lease_snapshot(engine)

    ctx.restore_pending = True

    with pytest.raises(JobError) as beat:
        heartbeat(
            ctx,
            {
                "heartbeat_request": {
                    "lease_id": lease["lease_id"],
                    "lease_epoch": lease["lease_epoch"],
                }
            },
        )
    assert beat.value.code is ErrorCode.STALE_LEASE

    with pytest.raises(JobError) as claim:
        claim_assignment(ctx, claim_body(WORKER_B, "claim-b"))
    assert claim.value.code is ErrorCode.RESTORE_UNVERIFIED

    assert lease_snapshot(engine) == before


# --- the sweep: T-RUN-14, T-RUN-15, T-RUN-20 ---------------------------------------------------


def test_an_expired_lease_returns_the_run_to_queued(ctx, engine, clock) -> None:
    """T-RUN-14 / T-RUN-20: no heartbeat within TTL + grace ⇒ ``queued``, ``worker_lost``."""
    start_run(ctx)
    claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    clock.advance(seconds=LEASE_TTL_COLLECTOR_SECONDS + HEARTBEAT_GRACE_SECONDS + 1)

    result = sweep_expired_leases(ctx)

    assert result == {"leases_expired": 1, "runs_requeued": 1}
    assert held_leases(engine) == 0
    status, stop_reason = rows(engine, "SELECT status, stop_reason FROM run")[0]
    assert (status, stop_reason) == ("queued", "worker_lost")


def test_an_expired_lease_does_not_erase_a_stored_needs_user(ctx, engine, clock) -> None:
    """T-RUN-15 — the exception that matters most.

    ``worker.report_stop`` committed ``needs_user`` **before** the lease lapsed, so the sweep
    must keep it. Returning the run to ``queued`` here would silently discard a challenge the
    Owner still has to clear, and the run would be picked up again by a worker that cannot get
    past it. Card §6: "không reset ``needs_user`` đã lưu".
    """
    start_run(ctx)
    claimed = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    lease = claimed["assignment"]["lease"]
    report_stop(
        ctx,
        {
            "lease_id": lease["lease_id"],
            "lease_epoch": lease["lease_epoch"],
            "stop_reason": "challenge_required",
        },
    )
    assert rows(engine, "SELECT status, stop_reason FROM run")[0] == ("needs_user", "captcha")

    clock.advance(seconds=LEASE_TTL_COLLECTOR_SECONDS + HEARTBEAT_GRACE_SECONDS + 1)
    result = sweep_expired_leases(ctx)

    assert result["leases_expired"] == 1
    assert result["runs_requeued"] == 0
    assert rows(engine, "SELECT status, stop_reason FROM run")[0] == ("needs_user", "captcha")


def test_source_blocked_records_an_unblock_condition_and_rotates_nothing(ctx, engine) -> None:
    """T-RUN-16/24: ``blocked`` with a stored condition, and **no** account rotation.

    ``ports.yaml`` says "không luân chuyển account/proxy" in as many words, and there is
    nothing in this package that could — no HTTP client, no credential store. The positive
    assertion is the stored sentence the Owner needs in order to act.
    """
    start_run(ctx)
    claimed = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    lease = claimed["assignment"]["lease"]

    answer = report_stop(
        ctx,
        {
            "lease_id": lease["lease_id"],
            "lease_epoch": lease["lease_epoch"],
            "stop_reason": "source_blocked",
        },
    )

    assert answer["run_status"] == "blocked"
    status, reason, unblock = rows(
        engine, "SELECT status, stop_reason, unblock_condition_vi FROM run"
    )[0]
    assert (status, reason) == ("blocked", "source_blocked")
    assert unblock, "a blocked run with no unblock condition cannot be acted on"


# --- SC35: cancel from every non-terminal status -----------------------------------------------


def test_cancel_works_from_every_non_terminal_status_and_deletes_nothing(ctx, engine) -> None:
    """Fixture ``collection/k``: five runs, five statuses, ``run_cancelled: 5``,
    ``post_deleted: 0``, ``assignment_lease_held: 0``.

    The five statuses are driven one at a time through the same context, because the service
    keeps one active run per owner. What the fixture pins and this asserts is that **every**
    non-terminal status is an exit, that no committed row is removed, and that no lease is left
    ``held``.
    """
    fixture = load("collection/k-cancel-from-every-non-terminal")
    expected = fixture["expected"]["counts"]
    assert expected["run_cancelled"] == 5
    assert expected["assignment_lease_held"] == 0
    assert expected["post_deleted"] == 0

    statuses = ("queued", "running", "waiting_retry", "needs_user", "blocked")
    cancelled: list[str] = []
    for status in statuses:
        run_id = start_run(ctx)
        if status == "running":
            claim_assignment(ctx, claim_body(WORKER_A, f"claim-{status}"))
        else:
            _force_status(engine, run_id, status)
        answer = cancel_run(ctx, run_id=run_id)
        assert answer["status"] == "cancelled", status
        assert answer["outcome"] == "cancelled", status
        cancelled.append(run_id)

    assert len(cancelled) == 5
    assert count(engine, "SELECT COUNT(*) FROM run WHERE status = 'cancelled'") == 5
    assert count(engine, "SELECT COUNT(*) FROM run WHERE outcome IS NULL") == 0
    assert held_leases(engine) == 0
    assert count(engine, "SELECT COUNT(*) FROM post") == 0
    assert (
        count(engine, "SELECT COUNT(*) FROM assignment WHERE state IN ('available','claimed')") == 0
    )


def _force_status(engine: Engine, run_id: str, status: str) -> None:
    """Put a run into one non-terminal status directly.

    A shortcut for *setup*, never for an assertion: reaching ``waiting_retry`` legitimately
    needs a retryable failure and reaching ``blocked`` needs a collector report, and neither is
    what this test is about. Every column the CHECK constraints tie to the status is filled, so
    the row is one the state machine could really produce.
    """
    extras = {
        "waiting_retry": ("next_attempt_at", "2026-09-07T09:00:00.000Z"),
        "blocked": ("unblock_condition_vi", "owner must confirm the source is reachable"),
    }
    column, value = extras.get(status, (None, None))
    with engine.begin() as connection:
        connection.execute(
            text(
                f"UPDATE run SET status = :s{f', {column} = :v' if column else ''} WHERE id = :id"
            ),
            {"s": status, "id": run_id, **({"v": value} if column else {})},
        )


def test_cancelling_twice_is_idempotent(ctx, engine) -> None:
    """``ports.yaml``: "Hủy lại run đã cancelled trả kết quả idempotent"."""
    run_id = start_run(ctx)
    first = cancel_run(ctx, run_id=run_id)
    before = rows(
        engine, "SELECT status, outcome, current_lease_epoch FROM run WHERE id = :id", id=run_id
    )

    second = cancel_run(ctx, run_id=run_id)

    assert first["already_cancelled"] is False
    assert second["already_cancelled"] is True
    assert (
        rows(
            engine, "SELECT status, outcome, current_lease_epoch FROM run WHERE id = :id", id=run_id
        )
        == before
    )


def test_a_cancelled_run_tells_its_worker_to_stop_on_the_next_beat(ctx, engine) -> None:
    """``run.cancel`` cannot stop a process; the directive is how T-RUN-17b reaches the worker.

    The lease is revoked, so the *next* beat carries the old epoch — but the run is cancelled,
    and the collector needs to be told to stop rather than to re-claim. The heartbeat therefore
    answers ``stop_cancelled`` for the holder whose epoch still matches at the moment of the
    beat.
    """
    start_run(ctx)
    claimed = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    lease = claimed["assignment"]["lease"]
    run_id = claimed["assignment"]["run_id"]
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE run SET status = 'cancelled', outcome = 'cancelled' WHERE id = :id"),
            {"id": run_id},
        )

    answer = heartbeat(
        ctx,
        {"heartbeat_request": {"lease_id": lease["lease_id"], "lease_epoch": lease["lease_epoch"]}},
    )

    assert answer["heartbeat_response"]["directive"] == "stop_cancelled"
    assert answer["heartbeat_response"]["lease_valid"] is False
    assert "lease_expires_at" not in answer["heartbeat_response"]


# --- resume: T-RUN-10 and T-RUN-23, and LM-07 --------------------------------------------------


def test_resume_from_needs_user_issues_a_new_lease_epoch(ctx, engine) -> None:
    """LM-07: *"Resume LUÔN cấp lease mới khi worker claim lại."*

    The old lease is revoked and the epoch moves, so a worker that survived the pause cannot
    continue on the lease it still holds — it has to claim again. That is the difference
    between resuming a run and resuming a writer.
    """
    start_run(ctx)
    claimed = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    lease = claimed["assignment"]["lease"]
    report_stop(
        ctx,
        {
            "lease_id": lease["lease_id"],
            "lease_epoch": lease["lease_epoch"],
            "stop_reason": "session_expired",
        },
    )

    answer = resume_run(ctx, run_id=claimed["assignment"]["run_id"])

    assert answer["status"] == "queued"
    assert answer["current_lease_epoch"] > lease["lease_epoch"]
    assert held_leases(engine) == 0
    with pytest.raises(JobError) as raised:
        heartbeat(
            ctx,
            {
                "heartbeat_request": {
                    "lease_id": lease["lease_id"],
                    "lease_epoch": lease["lease_epoch"],
                }
            },
        )
    assert raised.value.code is ErrorCode.STALE_LEASE


def test_resume_from_blocked_requires_an_unblock_reason(ctx, engine) -> None:
    """T-RUN-23 exists, and it is not free.

    Card §10 ``SG-01`` says nothing but ``run.cancel`` may leave ``blocked``; the pinned
    ``contracts/state/run.yaml`` disagrees (T-RUN-23) and ``ports.yaml`` ``run.resume``
    documents the mandatory ``unblock_reason``. The Coordinator ruled the contract wins
    (``CR-TC-SCHED-02``). The Owner is declaring a fact about the outside world, so an empty
    declaration is refused: without it a blocked run could loop forever with nothing recorded
    about why anyone expected a different outcome.
    """
    run_id = start_run(ctx)
    _force_status(engine, run_id, "blocked")

    with pytest.raises(JobError) as raised:
        resume_run(ctx, run_id=run_id)
    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert rows(engine, "SELECT status FROM run WHERE id = :id", id=run_id)[0][0] == "blocked"

    answer = resume_run(ctx, run_id=run_id, unblock_reason="the source is reachable again")

    assert answer["status"] == "queued"
    assert (
        rows(engine, "SELECT unblock_condition_vi FROM run WHERE id = :id", id=run_id)[0][0] is None
    )


def test_resume_from_a_status_that_is_not_waiting_is_a_conflict(ctx, engine) -> None:
    """``run.resume`` from ``queued`` or ``running`` has nothing to resume (``CONFLICT``)."""
    run_id = start_run(ctx)
    with pytest.raises(JobError) as raised:
        resume_run(ctx, run_id=run_id)
    assert raised.value.code is ErrorCode.CONFLICT


# --- release ------------------------------------------------------------------------------------


def test_release_revokes_the_lease_and_bumps_the_epoch(ctx, engine) -> None:
    """LM-06. Releasing twice does not change state after the first (``ports.yaml``)."""
    start_run(ctx)
    claimed = claim_assignment(ctx, claim_body(WORKER_A, "claim-a"))
    lease = claimed["assignment"]["lease"]

    first = release_assignment(
        ctx,
        {
            "release_request": {
                "lease_id": lease["lease_id"],
                "lease_epoch": lease["lease_epoch"],
                "release_reason": "completed_phase",
            }
        },
    )
    after = lease_snapshot(engine)
    second = release_assignment(
        ctx,
        {
            "release_request": {
                "lease_id": lease["lease_id"],
                "lease_epoch": lease["lease_epoch"],
                "release_reason": "completed_phase",
            }
        },
    )

    assert first["released"] is True
    assert first["lease_epoch"] == lease["lease_epoch"] + 1
    assert second["released"] is False
    assert lease_snapshot(engine) == after
    assert held_leases(engine) == 0


# --- the migration graph -------------------------------------------------------------------------


def test_the_migration_graph_has_exactly_one_head() -> None:
    """Structural, never against a literal revision id.

    Two cards landed a revision on ``0009`` in this wave and a merge point joins them; a third
    would add another. A test naming the expected head would have to be edited by each of
    them, which is how a second head gets committed with a green suite.
    """
    from alembic.script import ScriptDirectory

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert len(heads) == 1, heads


def test_the_custodian_lease_table_was_extended_not_recreated() -> None:
    """``CR-TC-ANALYSIS-01``: exactly one ``CREATE TABLE assignment_lease`` in the whole tree.

    The scheduler card was told to extend the custodian revision. "Extend" is checkable: the
    string appears once across every migration, and the index this card added is in a
    different file from the one that created the table.
    """
    versions = sorted((REPO_ROOT / "server" / "migrations" / "versions").glob("*.py"))
    creators = [path.name for path in versions if "CREATE TABLE assignment_lease" in _code_of(path)]
    assert creators == ["0006_tc_analysis_once_per_generation.py"], creators

    extender = REPO_ROOT / "server" / "migrations" / "versions" / "0010_tc_scheduler_lease_claim.py"
    assert "CREATE TABLE assignment_lease" not in _code_of(extender)
    # The phrase *is* in that file's prose, where it explains the rule it is following. That is
    # exactly why this test reads the code and not the bytes: a migration is allowed to talk
    # about a CREATE TABLE it must not issue.
    assert "CREATE TABLE assignment_lease" in extender.read_text(encoding="utf-8")
    assert "ux_assignment_lease_one_held" in _code_of(extender)


def _code_of(path: Path) -> str:
    """A module's source with its docstring removed.

    Searching raw bytes would count a docstring that *quotes* a statement as if the module
    issued it, which is the difference between explaining a rule and breaking it.
    """
    import ast

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    docstring = ast.get_docstring(tree, clean=False)
    return source.replace(docstring, "", 1) if docstring else source


def test_the_lease_run_id_is_still_not_null_as_the_contract_declares(engine) -> None:
    """``CR-TC-SCHED-01``: the packet allowed relaxing it *only if* ``entities.yaml`` permits.

    It does not — ``ENT-assignment-lease`` declares ``run_id`` ``nullable: false`` — so the
    column is unchanged and the analysis-claim mismatch stays a contract question. Asserted
    here so that a later "helpful" migration cannot quietly relax it.
    """
    import sqlite3

    import yaml

    entities = yaml.safe_load(
        (REPO_ROOT / "contracts" / "data" / "entities.yaml").read_text("utf-8")
    )
    declared = next(
        field
        for entity in entities["entities"]
        if entity["name"] == "assignment_lease"
        for field in entity["fields"]
        if field["name"] == "run_id"
    )
    assert declared["nullable"] is False

    with engine.connect() as connection:
        raw = connection.connection.dbapi_connection
        assert isinstance(raw, sqlite3.Connection)
        columns = {
            row[1]: bool(row[3]) for row in raw.execute("PRAGMA table_info('assignment_lease')")
        }
    assert columns["run_id"] is True
