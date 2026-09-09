"""E1/E2 — SC27 / SC42 / SC53: after a restore, nothing goes out until a person says so.

Four fixtures drive this file, and together they cover both signs of ``I15``:

``recovery/a-restore-old-outbox-nothing-sent``
    The dispatcher wakes up after the restore and must send **nothing**.
``recovery/b-post-restore-stale-lease-rejected``
    A worker that survived from before the backup is refused, twice, for two different
    reasons.
``recovery/j-restore-verification-incomplete-dispatch-locked``
    Integrity is fine and every count matches — and reconciliation is still incomplete, on
    clauses 4 and 7. This is the negative case that catches "integrity ok + counts match" being
    treated as sufficient.
``recovery/m-post-restore-reconciled-dispatch-reopens``
    The positive sign: once all seven clauses hold, dispatch reopens — and the old-generation
    intent *still* does not go out. Reopening the dispatcher is not the same thing as
    replaying history.

Plus ``recovery/e-saved-snapshot-hash-preserved``: the Saved snapshot's ``content_hash`` is
identical before the backup and after the restore, asserted at every step below.

The counter is the oracle, and it is real
-----------------------------------------
"0 messages sent" is not asserted by reading a log. Every dispatch attempt goes through
``server.app.delivery.service.dispatch_next`` — the sibling card's actual dispatcher — and
:attr:`DispatchOutcome.outbound_calls` is its own count of how many times
``telegram.send_payload`` was invoked. A transport is wired in that records every call, so if
the dispatcher ever did send, both the outcome counter and the transport's list would say so.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import StorageHealth
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError

from server.app.backup import reconcile, verify
from server.app.backup.restore import (
    CONFIRMATION_PHRASE,
    record_integrity_outcome,
    restore_snapshot,
)
from server.app.backup.snapshot import BackupError, create_snapshot, new_ulid, utc_now_ms
from server.app.db import create_sqlite_engine
from server.app.storage.guard import StorageGuard, StorageRefused

REPO_ROOT = Path(__file__).resolve().parents[2]

OWNER_ID = "01J0WNER100000000000000000"
NOW = "2026-09-08T03:00:00.000Z"
SNAPSHOT_PAYLOAD = {"content_version": "0.1.0", "display_title": "Đã lưu trước khi backup"}


# --------------------------------------------------------------------------------------
# Harness
# --------------------------------------------------------------------------------------


@pytest.fixture()
def database(tmp_path: Path) -> Path:
    path = tmp_path / "research-radar.db"
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(path)
    try:
        config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
        config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous
    return path


@pytest.fixture()
def engine(database: Path) -> Iterator[Engine]:
    built = create_sqlite_engine(database)
    _seed(built)
    yield built
    built.dispose()


def _seed(engine: Engine) -> None:
    """The state fixtures ``a``/``b``/``m`` describe, in this schema's real columns.

    One Saved snapshot (the ``recovery/e`` hash oracle), one ``held`` assignment lease (the
    thing §5.2 must revoke), one ``ready`` outbox intent and one ``unknown`` delivery part
    (clauses 4 and 5).
    """
    from server.app.saved.snapshot import canonical_json, compute_content_hash

    payload = canonical_json(SNAPSHOT_PAYLOAD)
    content_hash = compute_content_hash(SNAPSHOT_PAYLOAD)
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at,"
            " failed_login_count) VALUES (?, 1, 'owner', 'Asia/Ho_Chi_Minh', ?, 0)",
            (OWNER_ID, NOW),
        )
        connection.exec_driver_sql(
            "INSERT INTO saved_snapshot (id, owner_id, target_kind, target_key_at_save,"
            " payload, content_hash, created_at)"
            " VALUES ('01JSNAP9000000000000000000', ?, 'work',"
            " 'work:01JW0RK9000000000000000000', ?, ?, ?)",
            (OWNER_ID, payload, content_hash, NOW),
        )
        connection.exec_driver_sql(
            "INSERT INTO assignment_lease (id, owner_id, run_id, job_id, worker_identity,"
            " lease_epoch, expires_at, state)"
            " VALUES ('01JLEASE900000000000000000', ?, '01JRUN09000000000000000000',"
            " '01JJOB09000000000000000000', 'collector-1', 3, ?, 'held')",
            (OWNER_ID, NOW),
        )
        connection.exec_driver_sql(
            "INSERT INTO outbox_intent (id, owner_id, intent_type, subject_ref,"
            " created_in_transaction_at, dispatch_state, restore_generation)"
            " VALUES ('01JOI0LD000000000000000000', ?, 'telegram_digest',"
            " '{\"report_id\":\"01JREP09000000000000000000\"}', ?, 'ready', 1)",
            (OWNER_ID, NOW),
        )
        connection.exec_driver_sql(
            "INSERT INTO delivery (id, owner_id, report_id, channel, state, attempt_count,"
            " telegram_link_generation, created_at, updated_at)"
            " VALUES ('01JDEL09000000000000000000', ?, '01JREP09000000000000000000',"
            " 'telegram', 'unknown', 1, 1, ?, ?)",
            (OWNER_ID, NOW, NOW),
        )
        connection.exec_driver_sql(
            "INSERT INTO delivery_part (id, owner_id, delivery_id, part_index, payload_hash,"
            " state, provider_message_id, created_at, updated_at)"
            " VALUES ('01JDP009000000000000000000', ?, '01JDEL09000000000000000000', 0, ?,"
            " 'unknown', NULL, ?, ?)",
            (OWNER_ID, "sha256:" + "e" * 64, NOW, NOW),
        )


def _guard(engine: Engine) -> StorageGuard:
    """The process guard, wired to this card's predicate — the seam ``WR`` left open."""
    return StorageGuard(
        reconciliation_check=reconcile.reconciliation_complete(engine, owner_id=OWNER_ID)
    )


class StubLinkPort:
    """The ``telegram_link`` view ``MOD-telegram-adapter`` owns.

    An *active* link on purpose: a cancelled link would make "nothing was sent" true for the
    wrong reason. The dispatcher must be able to get all the way to choosing an intent and
    still send nothing, because no intent is eligible.
    """

    def current_link(self, *, owner_id: str) -> Any:
        from server.app.delivery.service import LinkSnapshot

        return LinkSnapshot(chat_id="42", generation=1, active=True)


class StubReportPort:
    """The published-report view ``TC-report-coverage-publish-cas`` owns."""

    def published_digest(self, *, owner_id: str, report_id: str) -> Any:
        from server.app.delivery.service import PublishedDigest

        return PublishedDigest(
            report_id=report_id, content_hash="sha256:" + "f" * 64, blocks=("khối 1",)
        )


class RecordingTransport:
    """Counts every ``telegram.send_payload`` the dispatcher makes. It must stay empty."""

    def __init__(self) -> None:
        self.calls: list[Any] = []

    def send(self, **kwargs: Any) -> Any:  # pragma: no cover - must never be reached
        self.calls.append(kwargs)
        raise AssertionError("the dispatcher sent a message while side effects were locked")


def _delivery_context(engine: Engine, guard: StorageGuard, generation: int) -> Any:
    from server.app.delivery.service import DeliveryContext

    return DeliveryContext(
        engine=engine,
        storage=guard,
        transport=RecordingTransport(),
        link_port=StubLinkPort(),
        report_port=StubReportPort(),
        restore_generation=generation,
    )


def _dispatch(context: Any) -> Any:
    from server.app.delivery.service import DeliveryError, dispatch_next

    try:
        return dispatch_next(context, owner_id=OWNER_ID)
    except DeliveryError as refused:
        return refused


def _add_current_generation_intent(engine: Engine, generation: int) -> str:
    """An intent carrying the CURRENT generation — the shape fixture ``j`` depicts.

    Clause 4 is scoped to ``restore_generation == new_restore_generation``: an intent from an
    older generation can never be dispatched, so there is nothing left to decide about it and
    it does not hold the gate open. What does hold it open is an intent at the *current*
    generation that no operator has looked at — fixture ``j``'s ``OI-09`` carries generation
    6 while ``new_restore_generation`` is 6, and that is why its clause 4 is unmet.
    """
    intent_id = new_ulid()
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO outbox_intent (id, owner_id, intent_type, subject_ref,"
            " created_in_transaction_at, dispatch_state, restore_generation)"
            " VALUES (?, ?, 'telegram_digest', ?, ?, 'ready', ?)",
            (
                intent_id,
                OWNER_ID,
                '{"report_id":"01JREP10000000000000000000"}',
                NOW,
                generation,
            ),
        )
    return intent_id


def _snapshot_hash(engine: Engine) -> str:
    with engine.connect() as connection:
        return str(
            connection.exec_driver_sql(
                "SELECT content_hash FROM saved_snapshot WHERE owner_id = ?", (OWNER_ID,)
            ).scalar_one()
        )


@pytest.fixture()
def restored(engine: Engine, tmp_path: Path) -> dict[str, Any]:
    """Snapshot → verify → restore. Leaves the store in ``recovery_required``, as §5.1 says."""
    guard = _guard(engine)
    snapshot = create_snapshot(
        engine,
        owner_id=OWNER_ID,
        artifact_path=tmp_path / "artifact.db",
        snapshot_request_id="REQ-snap-1",
        guard=guard,
    )
    verified = verify.verify_snapshot(
        engine, owner_id=OWNER_ID, backup_snapshot_id=snapshot.backup_snapshot_id
    )
    assert verified.verified is True

    # `T-ST-05` starts at `maintenance`: the operator opens the window, the restore does not.
    guard.enter_maintenance()
    result = restore_snapshot(
        engine,
        owner_id=OWNER_ID,
        backup_snapshot_id=snapshot.backup_snapshot_id,
        restore_request_id="RR-01",
        confirmation_phrase=CONFIRMATION_PHRASE,
        guard=guard,
    )
    return {
        "guard": guard,
        "snapshot": snapshot,
        "restore": result,
        "hash_before": _snapshot_hash(engine),
    }


# --------------------------------------------------------------------------------------
# Fixture a — the dispatcher wakes up and sends nothing
# --------------------------------------------------------------------------------------


def test_restore_locks_the_store_and_revokes_every_lease(
    engine: Engine, restored: dict[str, Any], fixture_loader: Any
) -> None:
    """§5.2 steps 1–4, in order: locked, leases revoked, generation raised, record written."""
    fixture = fixture_loader("recovery/a-restore-old-outbox-nothing-sent")
    expected = fixture.data["expected"]
    assert expected["storage_health_after_seq1"] == "recovery_required"
    assert expected["restore_record"]["dispatcher_unlocked_at"] is None

    guard: StorageGuard = restored["guard"]
    result = restored["restore"]
    assert guard.current_health() is StorageHealth.RECOVERY_REQUIRED
    assert result.leases_revoked == 1
    assert result.new_restore_generation == 2  # the seeded intent carries 1
    assert result.integrity_check_outcome == "not_run"

    with engine.connect() as connection:
        assert (
            int(
                connection.exec_driver_sql(
                    "SELECT COUNT(*) FROM assignment_lease WHERE state = 'held'"
                ).scalar_one()
            )
            == 0
        )
        unlocked = connection.exec_driver_sql(
            "SELECT dispatcher_unlocked_at FROM restore_record WHERE id = ?",
            (result.restore_id,),
        ).scalar_one()
    assert unlocked is None


def test_dispatcher_sends_nothing_while_recovery_required(
    engine: Engine, restored: dict[str, Any]
) -> None:
    """Fixture ``a`` seq2: ``RESTORE_UNVERIFIED`` and ``messages_sent = 0``.

    Run through the sibling card's real dispatcher, not a stand-in, so this asserts what the
    shipped code does rather than what this card believes about it.
    """
    context = _delivery_context(
        engine, restored["guard"], restored["restore"].new_restore_generation
    )
    outcome = _dispatch(context)
    assert getattr(outcome, "code", None) is ErrorCode.RESTORE_UNVERIFIED
    assert context.transport.calls == []


def test_reconciliation_is_false_immediately_after_restore(
    engine: Engine, restored: dict[str, Any]
) -> None:
    """Fixture ``a``: ``reconciliation_complete(RR-01) == false``.

    Clause 1 fails because ``integrity_check_outcome`` is still ``not_run`` — which
    ``entities.yaml`` calls a valid value that MUST block the dispatcher, not a missing one.
    """
    report = reconcile.evaluate(
        engine, owner_id=OWNER_ID, restore_id=restored["restore"].restore_id
    )
    assert report.complete is False
    assert reconcile.CLAUSE_INTEGRITY in report.unmet
    assert restored["guard"].reconciliation_complete(restored["restore"].restore_id) is False


# --------------------------------------------------------------------------------------
# Fixture b — the worker that survived the backup
# --------------------------------------------------------------------------------------


def test_worker_claim_is_blocked_by_recovery_required(restored: dict[str, Any]) -> None:
    """Fixture ``b`` seq3: claim ⇒ ``RESTORE_UNVERIFIED``, independent of the stale lease."""
    guard: StorageGuard = restored["guard"]
    for operation in (
        OperationId.WORKER_CLAIM_ASSIGNMENT,
        OperationId.ANALYSIS_CLAIM_TASK,
        OperationId.DELIVERY_DISPATCH_NEXT,
    ):
        with pytest.raises(StorageRefused) as refused:
            guard.assert_writable(operation)
        assert refused.value.code is ErrorCode.RESTORE_UNVERIFIED


def test_the_surviving_workers_lease_is_no_longer_held(
    engine: Engine, restored: dict[str, Any]
) -> None:
    """Fixture ``b``: the lease the old worker still holds in memory was revoked.

    Its epoch is what the worker will present, and the row says ``revoked`` — so the claim
    cannot be honoured on the merits either, not only because the store is locked. The
    fixture pins both refusals separately for exactly that reason.
    """
    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                "SELECT state, lease_epoch FROM assignment_lease WHERE id = ?",
                ("01JLEASE900000000000000000",),
            )
            .mappings()
            .one()
        )
    assert row["state"] == "revoked"
    assert row["lease_epoch"] == 3  # unchanged; the epoch a stale worker would present


# --------------------------------------------------------------------------------------
# Fixture j — integrity ok, counts match, still locked
# --------------------------------------------------------------------------------------


def test_integrity_and_counts_alone_do_not_reconcile(
    engine: Engine, restored: dict[str, Any], fixture_loader: Any
) -> None:
    """Fixture ``j``: clauses 4 and 7 remain, and the refusal names them.

    The sharpest assertion in this file. Everything a machine can check now passes, and
    reconciliation is still false — because an un-reviewed intent and a missing human
    acknowledgement are not things a machine may sign off.
    """
    fixture = fixture_loader("recovery/j-restore-verification-incomplete-dispatch-locked")
    assert fixture.data["expected"]["seq1"]["unmet_clauses"] == [4, 7]
    assert fixture.data["expected"]["seq2"]["messages_sent"] == 0

    restore_id = restored["restore"].restore_id
    record_integrity_outcome(engine, owner_id=OWNER_ID, restore_id=restore_id, outcome="passed")
    _add_current_generation_intent(engine, restored["restore"].new_restore_generation)

    report = reconcile.evaluate(engine, owner_id=OWNER_ID, restore_id=restore_id)
    assert report.unmet == (reconcile.CLAUSE_OUTBOX_REVIEWED, reconcile.CLAUSE_OPERATOR_ACK)
    assert set(report.met) == {1, 2, 3, 5, 6}

    with pytest.raises(BackupError) as refused:
        reconcile.reconcile_after_restore(
            engine, owner_id=OWNER_ID, restore_id=restore_id, guard=restored["guard"]
        )
    assert refused.value.code is ErrorCode.RESTORE_UNVERIFIED
    assert refused.value.unmet_clauses == (4, 7)

    # seq2/seq3: still locked, still nothing sent.
    context = _delivery_context(
        engine, restored["guard"], restored["restore"].new_restore_generation
    )
    assert getattr(_dispatch(context), "code", None) is ErrorCode.RESTORE_UNVERIFIED
    assert context.transport.calls == []
    with engine.connect() as connection:
        assert (
            connection.exec_driver_sql(
                "SELECT dispatcher_unlocked_at FROM restore_record WHERE id = ?", (restore_id,)
            ).scalar_one()
            is None
        )


def test_acknowledgement_alone_is_not_enough(engine: Engine, restored: dict[str, Any]) -> None:
    """Clause 7 satisfied, clause 4 not: still locked.

    Guards against an implementation that treats the operator's signature as a master key.
    """
    restore_id = restored["restore"].restore_id
    record_integrity_outcome(engine, owner_id=OWNER_ID, restore_id=restore_id, outcome="passed")
    _add_current_generation_intent(engine, restored["restore"].new_restore_generation)
    reconcile.acknowledge(
        engine,
        owner_id=OWNER_ID,
        restore_id=restore_id,
        principal="ACT-backup-operator",
        note="đã đối chiếu count và hash với manifest",
    )
    report = reconcile.evaluate(engine, owner_id=OWNER_ID, restore_id=restore_id)
    assert report.unmet == (reconcile.CLAUSE_OUTBOX_REVIEWED,)


def test_acknowledgement_requires_a_named_principal_and_a_note(
    engine: Engine, restored: dict[str, Any]
) -> None:
    """``entities.yaml``: the note is "bằng chứng con người đã nhìn", so it is mandatory."""
    restore_id = restored["restore"].restore_id
    for principal, note in (("", "x"), ("ACT-backup-operator", "")):
        with pytest.raises(BackupError) as refused:
            reconcile.acknowledge(
                engine,
                owner_id=OWNER_ID,
                restore_id=restore_id,
                principal=principal,
                note=note,
            )
        assert refused.value.code is ErrorCode.VALIDATION_ERROR


# --------------------------------------------------------------------------------------
# Fixture m — all seven clauses, dispatch reopens, history stays put
# --------------------------------------------------------------------------------------


@pytest.fixture()
def reconciled(engine: Engine, restored: dict[str, Any]) -> dict[str, Any]:
    """Satisfy all seven clauses the way an operator would: verify, review, acknowledge."""
    restore_id = restored["restore"].restore_id
    record_integrity_outcome(engine, owner_id=OWNER_ID, restore_id=restore_id, outcome="passed")
    intent_id = _add_current_generation_intent(engine, restored["restore"].new_restore_generation)
    reconcile.review_intent(
        engine,
        owner_id=OWNER_ID,
        restore_id=restore_id,
        outbox_intent_id=intent_id,
        decision="hold",
    )
    reconcile.acknowledge(
        engine,
        owner_id=OWNER_ID,
        restore_id=restore_id,
        principal="ACT-backup-operator",
        note="đã đối chiếu count và hash với manifest BS-9",
    )
    outcome = reconcile.reconcile_after_restore(
        engine, owner_id=OWNER_ID, restore_id=restore_id, guard=restored["guard"]
    )
    return {**restored, "reconcile": outcome}


def test_reconciled_restore_reopens_dispatch(engine: Engine, reconciled: dict[str, Any]) -> None:
    """Fixture ``m`` seq2/seq3: health back to ``healthy``, unlock timestamp written."""
    outcome = reconciled["reconcile"]
    assert outcome.report.complete is True
    assert set(outcome.report.met) == {1, 2, 3, 4, 5, 6, 7}
    assert reconciled["guard"].current_health() is StorageHealth.HEALTHY
    assert outcome.dispatcher_unlocked_at is not None

    with engine.connect() as connection:
        unlocked = connection.exec_driver_sql(
            "SELECT dispatcher_unlocked_at FROM restore_record WHERE id = ?",
            (outcome.restore_id,),
        ).scalar_one()
    assert unlocked == outcome.dispatcher_unlocked_at
    # And claims work again -- the lock is released, not merely reported as released.
    reconciled["guard"].assert_writable(OperationId.WORKER_CLAIM_ASSIGNMENT)


def test_old_generation_intent_is_still_never_sent(
    engine: Engine, reconciled: dict[str, Any], fixture_loader: Any
) -> None:
    """Fixture ``m`` seq4: reopening the dispatcher is not replaying history.

    The intent recovered from the snapshot carries generation 1; the current generation is 2.
    The dispatcher is now unlocked and still sends nothing, because eligibility is a number
    comparison rather than a state the unlock could clear.
    """
    fixture = fixture_loader("recovery/m-post-restore-reconciled-dispatch-reopens")
    assert fixture.data["expected"]["seq4"]["messages_sent_for_old_generation"] == 0

    context = _delivery_context(
        engine, reconciled["guard"], reconciled["restore"].new_restore_generation
    )
    outcome = _dispatch(context)
    assert getattr(outcome, "outbound_calls", 0) == 0
    assert context.transport.calls == []

    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                "SELECT dispatch_state, restore_generation FROM outbox_intent WHERE id = ?",
                ("01JOI0LD000000000000000000",),
            )
            .mappings()
            .one()
        )
    assert row["restore_generation"] == 1  # untouched by the unlock


def test_unknown_delivery_part_is_never_resolved_by_a_restore(
    engine: Engine, reconciled: dict[str, Any]
) -> None:
    """§5.5 / clause 5: ``unknown`` stays ``unknown`` through the whole cycle.

    A restore creates no information about whether Telegram received the message, so anything
    that moved the part to ``sent`` or ``failed`` would be inventing an outcome (AMD-B03).
    """
    with engine.connect() as connection:
        state = connection.exec_driver_sql(
            "SELECT state FROM delivery_part WHERE id = ?", ("01JDP009000000000000000000",)
        ).scalar_one()
    assert state == "unknown"


def test_reconcile_is_idempotent(engine: Engine, reconciled: dict[str, Any]) -> None:
    """``ports.yaml``: the same ``restore_id`` reconciles once."""
    again = reconcile.reconcile_after_restore(
        engine,
        owner_id=OWNER_ID,
        restore_id=reconciled["restore"].restore_id,
        guard=reconciled["guard"],
    )
    assert again.replayed is True
    assert again.dispatcher_unlocked_at == reconciled["reconcile"].dispatcher_unlocked_at


# --------------------------------------------------------------------------------------
# Fixture e — the Saved snapshot is untouched by any of this
# --------------------------------------------------------------------------------------


def test_saved_snapshot_hash_is_preserved_across_the_whole_cycle(
    engine: Engine, reconciled: dict[str, Any]
) -> None:
    """``recovery/e`` / SC12: ``content_hash`` before backup == after restore == after reconcile.

    Recomputed from the stored payload, not just compared to itself: the fixture's forbidden
    effect is a snapshot *recalculated from current data*, which would still be self-consistent
    while being a different hash.
    """
    from server.app.saved.snapshot import hash_matches

    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                "SELECT payload, content_hash FROM saved_snapshot WHERE owner_id = ?",
                (OWNER_ID,),
            )
            .mappings()
            .one()
        )
    assert row["content_hash"] == reconciled["hash_before"]
    assert hash_matches(str(row["payload"]), str(row["content_hash"]))


# --------------------------------------------------------------------------------------
# SG-DENY / CR-PC08-02 — who may reach backup.*
# --------------------------------------------------------------------------------------


def test_no_http_route_exposes_backup_operations() -> None:
    """``CR-PC08-02``: an owner browser session must not be able to start a restore.

    Card §3 gives this card no router, so there is no HTTP surface at all — the strongest
    possible form of that requirement, and the reason ``CR-TC-BACKUP-01`` records the
    divergence from openapi rather than papering over it.
    """
    from server.app.main import create_app

    app = create_app()
    operation_ids = {getattr(route, "operation_id", None) for route in app.routes}
    assert not {op for op in operation_ids if isinstance(op, str) and op.startswith("backup.")}


def test_only_the_backup_cli_may_call_these_operations(engine: Engine, tmp_path: Path) -> None:
    """Default deny: any other caller module ⇒ ``FORBIDDEN_EDGE`` (R5-01 row 2)."""
    with pytest.raises(BackupError) as refused:
        create_snapshot(
            engine,
            owner_id=OWNER_ID,
            artifact_path=tmp_path / "nope.db",
            snapshot_request_id="REQ-x",
            caller_module="MOD-web-ui",
        )
    assert refused.value.code is ErrorCode.FORBIDDEN_EDGE
    assert not (tmp_path / "nope.db").exists()


def test_cli_requires_the_backup_operator_token() -> None:
    """``secrets.md`` §147 / openapi: ``backupOperatorToken`` is the only accepted scheme.

    An unconfigured expected token denies rather than admits — a deployment that forgot to
    set it must reject every operator, not accept every caller.
    """
    from tools.backup_cli import authenticate

    authenticate(presented="t0ken", expected="t0ken")
    for presented, expected in (("wrong", "t0ken"), (None, "t0ken"), ("t0ken", None), (None, None)):
        with pytest.raises(PermissionError):
            authenticate(presented=presented, expected=expected)


def _run_cli(
    monkeypatch: pytest.MonkeyPatch, database: Path, *args: str, token: str = "op-token"
) -> tuple[int, dict[str, Any]]:
    """Invoke the CLI end to end and return ``(exit_code, parsed JSON)``.

    Goes through ``main`` rather than the service functions on purpose: the defect this covers
    lived in the CLI's own error path, so a test that called the service directly would have
    stayed green while the operator got a traceback.
    """
    import io
    import json as _json
    from contextlib import redirect_stdout

    from tools.backup_cli import EXPECTED_TOKEN_ENV, TOKEN_ENV, main

    monkeypatch.setenv(TOKEN_ENV, token)
    monkeypatch.setenv(EXPECTED_TOKEN_ENV, "op-token")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["--database", str(database), *args])
    printed = buffer.getvalue().strip()
    return code, (_json.loads(printed) if printed else {})


def test_not_found_for_a_snapshot_still_says_snapshot(
    engine: Engine, database: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The half that must NOT change: a genuinely missing snapshot still reads as one.

    The fix is only meaningful if the other message kept saying what it always did; otherwise
    it is not a fix, it is a swap.
    """
    code, payload = _run_cli(
        monkeypatch, database, "verify", "--snapshot-id", "01JNOSUCHSNAPSHOT00000000"
    )
    assert code == 2
    assert payload["code"] == ErrorCode.NOT_FOUND.value
    assert payload["details_safe"]["resource_kind"] == "backup_snapshot"
    assert "snapshot" in payload["message_safe"].lower()


def test_not_found_for_a_missing_owner_names_the_bootstrap_command(
    database: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """``F-A3-P5R2-01``: a ``NOT_FOUND`` must not aim the reader at the wrong thing.

    The envelope was already correct — ``details_safe.resource_kind: "owner"`` — but the
    sentence came from a per-code table and read "Không tìm thấy snapshot được yêu cầu.", so an
    Owner on a migrated-but-un-bootstrapped database went hunting for a snapshot instead of
    creating the account. A misleading sentence is worse than a bare code: it points somewhere
    specific and wrong.

    Uses the bare ``database`` fixture — migrated, never seeded — because that IS the state the
    audit describes. (Requesting ``engine`` would seed an owner and rows that reference it.)
    """
    code, payload = _run_cli(
        monkeypatch, database, "snapshot", "--artifact", str(tmp_path / "unused.db")
    )
    assert code == 2
    assert payload["code"] == ErrorCode.NOT_FOUND.value
    assert payload["details_safe"]["resource_kind"] == "owner"
    assert "owner" in payload["message_safe"]
    assert "bootstrap-owner" in payload["message_safe"]
    # It must not send the reader after a snapshot.
    assert "snapshot" not in payload["message_safe"].lower()
    # Only the sentence changed: code, scope and retry class stay the contract's.
    assert payload["scope"] == "request"
    assert payload["retry_class"] == "none"
    assert not (tmp_path / "unused.db").exists()


def test_the_bootstrap_command_the_message_names_actually_exists() -> None:
    """The message names a command; that command has to be real.

    Telling an operator to run something that does not exist would be the same defect class as
    the one being fixed — a specific, confident, wrong instruction. ``rr-admin`` is a console
    script in ``pyproject.toml`` and ``bootstrap-owner`` is one of its subparsers, so this
    asserts both rather than trusting the string.
    """
    import tomllib

    from tools.backup_cli import NOT_FOUND_MESSAGE

    scripts = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "scripts"
    ]
    assert "rr-admin" in scripts

    from tools.rr_admin import build_parser as admin_parser

    subcommands = {
        name
        for action in admin_parser()._actions
        for name in getattr(action, "choices", None) or {}
    }
    assert "bootstrap-owner" in subcommands
    assert "rr-admin bootstrap-owner" in NOT_FOUND_MESSAGE["owner"]


def test_cli_reports_an_unknown_owner_as_an_envelope_not_a_traceback(
    engine: Engine, database: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An owner id that does not exist ⇒ exit 2 and a ``NOT_FOUND`` envelope.

    The CLI documents exit ``2`` for a contract refusal and ``0``/``3`` for the other two
    outcomes; an ``AttributeError`` escaping ``main`` is none of them. Checking the parsed
    envelope, not just the exit code, is what makes this a test of the *refusal* rather than of
    "something went wrong".
    """
    code, payload = _run_cli(
        monkeypatch,
        database,
        "--owner-id",
        "01JNOSUCHOWNER00000000000",
        "snapshot",
        "--artifact",
        str(tmp_path / "unused.db"),
    )
    assert code == 2
    assert payload["code"] == ErrorCode.NOT_FOUND.value
    assert payload["details_safe"] == {"resource_kind": "owner"}
    assert payload["correlation_id"]
    assert not (tmp_path / "unused.db").exists()


def test_cli_reports_an_empty_owner_table_as_an_envelope(
    database: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """No ``owner`` row at all ⇒ the same refusal, not a crash.

    This is the case the old code called "unreachable in practice" while raising an
    uninitialised exception for it. It is reached by a fresh deployment before
    ``bootstrap_owner``, and by a restore target before the artifact is in place — both times
    with an operator at the keyboard running exactly this tool.
    """
    empty = create_sqlite_engine(database)
    try:
        with empty.begin() as connection:
            connection.exec_driver_sql("DELETE FROM owner")
    finally:
        empty.dispose()

    code, payload = _run_cli(
        monkeypatch, database, "snapshot", "--artifact", str(tmp_path / "unused.db")
    )
    assert code == 2
    assert payload["code"] == ErrorCode.NOT_FOUND.value
    assert payload["details_safe"] == {"resource_kind": "owner"}


def test_cli_rejects_a_bad_token_before_touching_the_database(
    engine: Engine, database: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A wrong token ⇒ exit 3 and an ``UNAUTHORIZED`` payload, and no owner lookup at all.

    Ordering matters: authentication is answered before the database is opened, so an
    unauthenticated caller learns nothing about whether an owner exists.
    """
    code, payload = _run_cli(
        monkeypatch,
        database,
        "snapshot",
        "--artifact",
        str(tmp_path / "unused.db"),
        token="wrong-token",
    )
    assert code == 3
    assert payload["code"] == ErrorCode.UNAUTHORIZED.value
    assert payload["required_auth_scope"] == "backup_operator"
    assert "token" not in str(payload).lower().replace("operator token", "")


def test_cli_snapshot_and_verify_round_trip(
    engine: Engine, database: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The happy path through the CLI: exit 0 twice, and the snapshot verifies.

    Present so the refusal tests above cannot pass by the CLI being broken for everything.
    """
    artifact = tmp_path / "cli.db"
    code, payload = _run_cli(
        monkeypatch, database, "snapshot", "--artifact", str(artifact), "--request-id", "REQ-cli"
    )
    assert code == 0, payload
    assert payload["state"] == "completed"
    assert artifact.exists()

    code, verified = _run_cli(
        monkeypatch, database, "verify", "--snapshot-id", payload["backup_snapshot_id"]
    )
    assert code == 0, verified
    assert verified["state"] == "verified"
    assert verified["counts_match"] is True


def test_maintenance_open_without_a_reason_is_an_envelope_not_a_traceback(
    engine: Engine, database: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``F-A3-P5-01``: the runbook's own command must not crash.

    ``docs/owner-runbook.md`` shows ``backup_cli maintenance --open``. The guard makes
    ``reason`` mandatory (both audit columns are NOT NULL), ``--reason`` stayed optional here,
    and ``MaintenanceWindowRequired`` went straight past the CLI's error handling to the
    terminal — the operator followed the documented command and got a Python traceback.

    Refused as an envelope with exit 2, not via ``argparse(required=True)``: argparse writes a
    usage dump to stderr and leaves stdout empty, so anything parsing this tool's JSON would
    receive nothing. The check is on stdout being a *complete* envelope for that reason.
    """
    code, payload = _run_cli(monkeypatch, database, "maintenance", "--open")
    assert code == 2
    assert payload["code"] == ErrorCode.VALIDATION_ERROR.value
    assert payload["details_safe"]["field_path"] == "--reason"
    assert payload["details_safe"]["violation_kind"] == "required_field_missing"
    assert payload["correlation_id"]
    with engine.connect() as connection:
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM maintenance_window").scalar_one())
            == 0
        )


def test_maintenance_open_with_an_unknown_reason_is_rejected_by_argparse(
    database: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """An unknown reason is argparse's job: ``choices`` names the valid set back to the operator.

    Deliberately a different mechanism from the missing case. "You forgot a flag" is answered
    in the tool's own vocabulary; "that is not one of the five reasons" is answered by showing
    the five, which an envelope with a ``violation_kind`` would not do.
    """
    from tools.backup_cli import EXPECTED_TOKEN_ENV, TOKEN_ENV, main

    monkeypatch.setenv(TOKEN_ENV, "op-token")
    monkeypatch.setenv(EXPECTED_TOKEN_ENV, "op-token")
    with pytest.raises(SystemExit) as exited:
        main(["--database", str(database), "maintenance", "--open", "--reason", "nonsense"])
    assert exited.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_an_illegal_state_transition_is_an_envelope_not_a_traceback(
    engine: Engine, database: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--close`` with nothing open raises ``ForbiddenTransition`` below; the CLI renders it.

    The state machine is closed on purpose, so asking for an edge it does not have is a normal
    operator mistake, not a crash. It is ``VALIDATION_ERROR`` on ``storage_health`` for the same
    reason ``restore_snapshot`` reports a wrong health that way — ``ports.yaml`` gives
    ``backup.*`` no code for a bad precondition (``CR-TC-BACKUP-05``).
    """
    code, payload = _run_cli(monkeypatch, database, "maintenance", "--close")
    assert code == 2
    assert payload["code"] == ErrorCode.VALIDATION_ERROR.value
    assert payload["details_safe"]["field_path"] == "storage_health"
    # The internal exception text is never echoed -- only its class name, which carries no path
    # or value.
    assert payload["details_safe"]["violation_kind"] == "ForbiddenTransition"
    assert "NOT NULL" not in str(payload)


def test_an_unexpected_exception_still_leaves_a_clean_envelope(
    engine: Engine,
    database: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The catch-all: stdout stays parseable JSON even for a bug nobody anticipated.

    Requires the seeded ``engine`` so the run actually reaches ``_dispatch``: without an
    ``owner`` row it would stop earlier at the ``NOT_FOUND`` refusal, which is a different
    path and already covered.

    ``F-A3-P5-01`` was one instance of a general shape — an exception from a lower layer
    reaching the terminal. Asserted by forcing an arbitrary failure inside the dispatch, so the
    guarantee does not depend on having enumerated every exception type in advance. The class
    name goes to stderr so a developer keeps a thread to pull; the exception's *message* is
    echoed nowhere, since it can carry a path or a value the envelope does not admit.
    """
    import tools.backup_cli as cli

    monkeypatch.setenv(cli.TOKEN_ENV, "op-token")
    monkeypatch.setenv(cli.EXPECTED_TOKEN_ENV, "op-token")

    def _boom(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("/home/someone/secret/path leaked in a message")

    monkeypatch.setattr(cli, "_dispatch", _boom)
    code = cli.main(["--database", str(database), "maintenance", "--close"])
    captured = capsys.readouterr()
    assert code == 2
    payload = __import__("json").loads(captured.out)
    assert payload["code"] == ErrorCode.INTERNAL.value
    assert payload["correlation_id"]
    assert "secret/path" not in captured.out
    assert "secret/path" not in captured.err
    assert "RuntimeError" in captured.err


def test_maintenance_window_survives_into_a_separate_cli_invocation(
    engine: Engine, database: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Gap ``G-3`` / ``CR-TC-storage-07``: open the window in one process, restore in the next.

    This is the documented runbook, and until ``PKT-TC-STORAGE-FIX4`` it could not actually be
    executed. ``restore_snapshot`` refuses outside ``maintenance`` (``T-ST-05``), and
    ``_guard()`` built an in-memory guard — so the window died with the first process and the
    second was told there was no window. The operator would have followed the runbook exactly
    and been refused for doing so.

    Every step below is a **separate** ``main()`` call with its own engine and its own guard,
    which is what makes this a two-process test rather than a two-function one.
    """
    artifact = tmp_path / "twostep.db"
    code, snapshot_payload = _run_cli(
        monkeypatch, database, "snapshot", "--artifact", str(artifact), "--request-id", "REQ-2p"
    )
    assert code == 0, snapshot_payload
    code, _ = _run_cli(
        monkeypatch, database, "verify", "--snapshot-id", snapshot_payload["backup_snapshot_id"]
    )
    assert code == 0

    # -- invocation 1: open the window -------------------------------------------------
    code, opened = _run_cli(monkeypatch, database, "maintenance", "--open", "--reason", "restore")
    assert code == 0, opened
    assert opened["storage_health"] == "maintenance"
    assert opened["window_id"]

    # It is on disk, with the operator recorded -- not merely in the exited process's memory.
    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                "SELECT id, opened_by, reason, closed_at, restore_record_id"
                " FROM maintenance_window WHERE owner_id = ? AND closed_at IS NULL",
                (OWNER_ID,),
            )
            .mappings()
            .one()
        )
    assert row["opened_by"] == "ACT-backup-operator"
    assert row["reason"] == "restore"
    assert row["restore_record_id"] is None  # nothing has run inside it yet

    # -- invocation 2: a FRESH process reaches the restore path ------------------------
    code, restored = _run_cli(
        monkeypatch,
        database,
        "restore",
        "--snapshot-id",
        snapshot_payload["backup_snapshot_id"],
        "--request-id",
        "RR-2p",
        "--confirm",
        CONFIRMATION_PHRASE,
    )
    assert code == 0, restored
    assert restored["storage_health"] == "recovery_required"
    assert restored["integrity_check_outcome"] == "not_run"
    assert restored["dispatcher_unlocked_at"] is None

    # The window now points at the restore that ran inside it -- written after the INSERT,
    # because the column is a foreign key onto `restore_record`.
    with engine.connect() as connection:
        linked = connection.exec_driver_sql(
            "SELECT restore_record_id FROM maintenance_window WHERE id = ?", (row["id"],)
        ).scalar_one()
        exists = int(
            connection.exec_driver_sql(
                "SELECT COUNT(*) FROM restore_record WHERE id = ?", (linked,)
            ).scalar_one()
        )
    assert linked == restored["restore_id"]
    assert exists == 1

    # -- invocation 3: the lock is real across processes too ---------------------------
    code, status = _run_cli(monkeypatch, database, "status", "--restore-id", restored["restore_id"])
    assert code == 2, status  # not reconciled: clauses still unmet
    assert status["reconciliation_complete"] is False


def test_restore_still_refuses_without_a_window_in_a_fresh_process(
    engine: Engine, database: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The negative half: persistence must not become a way in.

    Making the window durable would be worth nothing if a process that never opened one could
    restore anyway. No ``maintenance --open``, so ``T-ST-05`` has no edge to take.
    """
    artifact = tmp_path / "nowindow.db"
    code, payload = _run_cli(
        monkeypatch, database, "snapshot", "--artifact", str(artifact), "--request-id", "REQ-nw"
    )
    assert code == 0
    _run_cli(monkeypatch, database, "verify", "--snapshot-id", payload["backup_snapshot_id"])

    code, refused = _run_cli(
        monkeypatch,
        database,
        "restore",
        "--snapshot-id",
        payload["backup_snapshot_id"],
        "--request-id",
        "RR-nw",
        "--confirm",
        CONFIRMATION_PHRASE,
    )
    assert code == 2
    assert refused["code"] == ErrorCode.VALIDATION_ERROR.value
    assert refused["details_safe"]["field_path"] == "storage_health"
    with engine.connect() as connection:
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM restore_record").scalar_one()) == 0
        )


def test_restore_requires_the_typed_confirmation(engine: Engine, tmp_path: Path) -> None:
    """``ports.yaml``: restore needs a typed confirmation, and a wrong one changes nothing."""
    guard = _guard(engine)
    snapshot = create_snapshot(
        engine,
        owner_id=OWNER_ID,
        artifact_path=tmp_path / "confirm.db",
        snapshot_request_id="REQ-confirm",
    )
    verify.verify_snapshot(
        engine, owner_id=OWNER_ID, backup_snapshot_id=snapshot.backup_snapshot_id
    )
    guard.enter_maintenance()
    with pytest.raises(BackupError) as refused:
        restore_snapshot(
            engine,
            owner_id=OWNER_ID,
            backup_snapshot_id=snapshot.backup_snapshot_id,
            restore_request_id="RR-bad",
            confirmation_phrase="restore",  # wrong case: not the phrase
            guard=guard,
        )
    assert refused.value.code is ErrorCode.VALIDATION_ERROR
    assert guard.current_health() is StorageHealth.MAINTENANCE
    with engine.connect() as connection:
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM restore_record").scalar_one()) == 0
        )


def test_restore_refuses_outside_a_maintenance_window(engine: Engine, tmp_path: Path) -> None:
    """``T-ST-05`` starts at ``maintenance``; there is no edge from ``healthy``.

    The maintenance window IS the side-effect lock the card's title names, and
    ``storage.yaml`` forbids entering it without an explicit operator action. A restore that
    opened its own window would remove the human from the one operation that most needs one,
    so this refuses instead — before the artifact is copied and before the store is touched.

    ``ports.yaml`` gives ``backup.restore_snapshot`` no code for "wrong storage health"
    (``data.purge_all`` uses ``CONFLICT`` for the same precondition), hence
    ``VALIDATION_ERROR`` and ``CR-TC-BACKUP-05``.
    """
    guard = _guard(engine)
    snapshot = create_snapshot(
        engine,
        owner_id=OWNER_ID,
        artifact_path=tmp_path / "healthy.db",
        snapshot_request_id="REQ-healthy",
    )
    verify.verify_snapshot(
        engine, owner_id=OWNER_ID, backup_snapshot_id=snapshot.backup_snapshot_id
    )
    assert guard.current_health() is StorageHealth.HEALTHY

    target = tmp_path / "restored" / "db.sqlite"
    with pytest.raises(BackupError) as refused:
        restore_snapshot(
            engine,
            owner_id=OWNER_ID,
            backup_snapshot_id=snapshot.backup_snapshot_id,
            restore_request_id="RR-healthy",
            confirmation_phrase=CONFIRMATION_PHRASE,
            guard=guard,
            target_database=target,
        )
    assert refused.value.code is ErrorCode.VALIDATION_ERROR
    assert refused.value.details_safe["field_path"] == "storage_health"
    assert guard.current_health() is StorageHealth.HEALTHY
    assert not target.exists()
    with engine.connect() as connection:
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM restore_record").scalar_one()) == 0
        )


# --------------------------------------------------------------------------------------
# Pinned contract divergences (CR-TC-BACKUP-03, -04)
# --------------------------------------------------------------------------------------


def test_outbox_dispatch_state_vocabulary_divergence_is_pinned(engine: Engine) -> None:
    """``CR-TC-BACKUP-03``: fixtures say ``pending``/``retry_wait``; the entity says otherwise.

    ``backup-restore.md`` §5.6 clause 4 and fixtures ``a``/``j``/``m`` use delivery-part
    vocabulary for ``outbox_intent.dispatch_state``. ``entities.yaml`` closes that enum over
    ``ready | claimed | done | held_for_review``, and the Coordinator ruled the entity contract
    wins — so clause 4 reads ``ready``. Pinned here so that widening the enum breaks this test
    instead of silently changing which intents clause 4 covers.
    """
    assert reconcile.INTENT_AWAITING_REVIEW == "ready"
    for forbidden in ("pending", "retry_wait", "sent"):
        with pytest.raises(IntegrityError), engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO outbox_intent (id, owner_id, intent_type, subject_ref,"
                " created_in_transaction_at, dispatch_state, restore_generation)"
                " VALUES (?, ?, 'telegram_digest', '{}', ?, ?, 1)",
                (new_ulid(), OWNER_ID, NOW, forbidden),
            )


def test_schema_migration_version_is_null_and_alembic_head_is_recorded(
    engine: Engine, tmp_path: Path
) -> None:
    """``CR-TC-BACKUP-04``: ``ENT-schema-migration`` is unimplemented, so the integer is NULL.

    The Alembic head is what actually identifies this deployment's schema, and it is what
    ``verify`` reads back out of the artifact — so §5.3 step 3 still has something real to
    compare, rather than a column nobody can populate.
    """
    result = create_snapshot(
        engine,
        owner_id=OWNER_ID,
        artifact_path=tmp_path / "rev.db",
        snapshot_request_id="REQ-rev",
        alembic_revision="0012_tc_backup_restore_drill",
    )
    with engine.connect() as connection:
        stored = connection.exec_driver_sql(
            "SELECT schema_migration_version FROM backup_snapshot WHERE id = ?",
            (result.backup_snapshot_id,),
        ).scalar_one()
        assert stored is None
        assert (
            connection.exec_driver_sql(
                "SELECT COUNT(*) FROM sqlite_master WHERE name = 'schema_migration'"
            ).scalar_one()
            == 0
        )
    observed = verify.artifact_revision(Path(result.artifact_path))
    assert observed is not None


def _set_embedding_generation(
    engine: Engine, *, expected: int | None, built: int, state: str = "active"
) -> None:
    """Replace the owner's ``embedding_generation`` with exactly one row in the given shape.

    Replaces rather than appends: the table carries a UNIQUE on the model tuple and allows one
    ``active`` row per owner, so each case has to start from a clean slate to be independent of
    the ones before it. ``expected`` may be NULL — that is the column's declared shape and the
    case this fix is about.
    """
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "DELETE FROM embedding_generation WHERE owner_id = ?", (OWNER_ID,)
        )
        connection.exec_driver_sql(
            "INSERT INTO embedding_generation (id, owner_id, model_name, model_version,"
            " dimension, normalization, state, expected_vector_count, built_vector_count,"
            " created_at, activated_at)"
            " VALUES (?, ?, 'bge-m3', '1.0', 8, 'l2', ?, ?, ?, ?, ?)",
            (new_ulid(), OWNER_ID, state, expected, built, NOW, NOW),
        )


def test_clause_six_is_unmet_when_expected_vector_count_is_null(
    engine: Engine, restored: dict[str, Any]
) -> None:
    """``CR-TC-DELIVERY-11``: a NULL expectation must produce a VERDICT, not a ``TypeError``.

    ``entities.yaml`` makes ``expected_vector_count`` nullable and defines it as the count a
    generation must reach *before it may become active*. A NULL on an **active** row therefore
    means the precondition that gated activation was never recorded, and nothing in the restored
    database can show the index is complete.

    Clause 6 is **unmet** in that case, with the reason named. Answering "met" would convert
    *undetermined* into *good* — what ``I13``/``CAP-P5`` forbid — and would reopen selection
    against an index nobody can prove is whole (``I12``). The previous code never reached either
    answer: ``int(None)`` raised, so the clause crashed instead of deciding, which is why W5C
    had to seed the column to get their own test past it.
    """
    _set_embedding_generation(engine, expected=None, built=7)
    restore_id = restored["restore"].restore_id
    record_integrity_outcome(engine, owner_id=OWNER_ID, restore_id=restore_id, outcome="passed")

    report = reconcile.evaluate(engine, owner_id=OWNER_ID, restore_id=restore_id)
    assert reconcile.CLAUSE_EMBEDDING in report.unmet
    assert "expected_vector_count = NULL" in report.detail[reconcile.CLAUSE_EMBEDDING]

    # And it stays a refusal all the way out, rather than an exception escaping the operation.
    with pytest.raises(BackupError) as refused:
        reconcile.reconcile_after_restore(
            engine, owner_id=OWNER_ID, restore_id=restore_id, guard=restored["guard"]
        )
    assert refused.value.code is ErrorCode.RESTORE_UNVERIFIED
    assert reconcile.CLAUSE_EMBEDDING in refused.value.unmet_clauses
    assert restored["guard"].current_health() is StorageHealth.RECOVERY_REQUIRED


def test_clause_six_distinguishes_no_generation_from_an_unverifiable_one(
    engine: Engine, restored: dict[str, Any]
) -> None:
    """Three inputs, three different verdicts — the distinction is the point.

    "No active generation" is met (nothing to protect); "active but unverifiable" and "active
    with counts that disagree" are both unmet, and their reasons differ so an operator can tell
    which one they are looking at.
    """
    restore_id = restored["restore"].restore_id
    record_integrity_outcome(engine, owner_id=OWNER_ID, restore_id=restore_id, outcome="passed")

    # (a) no active generation at all -> met
    assert (
        reconcile.CLAUSE_EMBEDDING
        not in reconcile.evaluate(engine, owner_id=OWNER_ID, restore_id=restore_id).unmet
    )

    # (b) a `building` generation is not `active`, so still met
    _set_embedding_generation(engine, expected=None, built=0, state="building")
    assert (
        reconcile.CLAUSE_EMBEDDING
        not in reconcile.evaluate(engine, owner_id=OWNER_ID, restore_id=restore_id).unmet
    )

    # (c) active with counts that disagree -> unmet, and the reason names the counts
    _set_embedding_generation(engine, expected=9, built=7)
    report = reconcile.evaluate(engine, owner_id=OWNER_ID, restore_id=restore_id)
    assert reconcile.CLAUSE_EMBEDDING in report.unmet
    reason = report.detail[reconcile.CLAUSE_EMBEDDING]
    assert "7" in reason and "9" in reason


def test_clause_six_is_met_when_the_active_generation_is_complete(
    engine: Engine, restored: dict[str, Any]
) -> None:
    """The positive half: counts agree ⇒ clause 6 met (``backup-restore.md`` §5.3 step 5)."""
    _set_embedding_generation(engine, expected=8, built=8)
    restore_id = restored["restore"].restore_id
    record_integrity_outcome(engine, owner_id=OWNER_ID, restore_id=restore_id, outcome="passed")
    report = reconcile.evaluate(engine, owner_id=OWNER_ID, restore_id=restore_id)
    assert reconcile.CLAUSE_EMBEDDING not in report.unmet


def test_purge_all_keeps_every_backup_table_and_artifact(
    engine: Engine, reconciled: dict[str, Any], fixture_loader: Any
) -> None:
    """``recovery/l`` — the half of the purge fixture this card actually owns.

    ``data.purge_all`` itself is a §1 non-goal and ``SG-02`` forbids implementing it here, so
    the two-phase confirmation and its four negatives stay ``NOT_RUN`` (see the handoff). What
    is **not** out of scope is the claim that fixture makes about *this* card's data:

        "``backup_snapshot`` / ``backup_manifest`` / ``restore_record`` còn nguyên hàng, và
        artifact backup trên đĩa không bị chạm."

    That matters beyond bookkeeping: it is the reason the confirmation dialog must tell the
    owner that purged data still exists in the backups (``backup-restore.md`` §8). If these
    three tables were ever moved into the purged set, "xóa hẳn" and "xóa dữ liệu nghiên cứu"
    would silently become the same operation.

    Asserted three ways, none of which needs purge to exist: the fixture's own retained list,
    ``entities.yaml``'s ratified sets, and this package's source — which contains no statement
    that could remove a backup row or artifact.
    """
    import yaml

    fixture = fixture_loader("recovery/l-purge-all-two-phase-and-negatives")
    retained = set(fixture.data["expected"]["_retained_tables"])
    purged = set(fixture.data["expected"]["_purged_tables"])
    never = set(fixture.data["expected"]["_never_purged_tables"])
    backup_tables = {"backup_snapshot", "backup_manifest", "restore_record"}

    assert backup_tables <= retained, backup_tables - retained
    assert backup_tables.isdisjoint(purged)
    assert backup_tables.isdisjoint(never)
    assert (
        "artifact backup trên đĩa không bị chạm"
        in (fixture.data["expected"]["backups_untouched_vi"])
    )
    # The dialog obligation exists because of this fact; if the sentence is ever dropped the
    # owner is told something false about what "delete everything" achieved.
    assert "backup" in fixture.data["expected"]["confirmation_dialog_must_state_vi"].lower()

    # The ratified sets in entities.yaml must say the same thing; the fixture copies them
    # ("_retained_source_vi"), and a copy that drifted from its source is the defect R4-01
    # exists for.
    entities = yaml.safe_load(
        (REPO_ROOT / "contracts" / "data" / "entities.yaml").read_text(encoding="utf-8")
    )
    txn = next(t for t in entities["transactions"] if t["id"] == "TXN-purge-all")
    declared = " ".join(str(v) for v in txn.values())
    for table in sorted(backup_tables):
        assert table in declared, f"{table} is not named in TXN-purge-all"

    # Finally: nothing in this package can delete a backup row or an artifact file.
    package = REPO_ROOT / "server" / "app" / "backup"
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(package.glob("*.py"))
    ).upper()
    for forbidden in ("DELETE FROM BACKUP_", "DROP TABLE BACKUP_", "DELETE FROM RESTORE_RECORD"):
        assert forbidden not in source
    assert "UNLINK" not in source and "SHUTIL.RMTREE" not in source

    # And the rows this run created are still there after the whole restore cycle.
    with engine.connect() as connection:
        for table in sorted(backup_tables):
            assert (
                int(connection.exec_driver_sql(f"SELECT COUNT(*) FROM {table}").scalar_one()) >= 1
            ), table


def test_a_drill_records_the_evidence_section_5_7_asks_for(
    engine: Engine, reconciled: dict[str, Any]
) -> None:
    """§5.7's evidence list is producible from the rows this card writes.

    Not a behavioural assertion but a completeness one: a drill that cannot produce these
    fields is not auditable, and the real drill (E3) is NOT_RUN, so the least this card owes
    is that the shape exists.
    """
    report = reconciled["reconcile"].report.as_evidence()
    assert report["reconciliation_complete"] is True
    with engine.connect() as connection:
        row = (
            connection.exec_driver_sql(
                "SELECT r.id, r.backup_snapshot_id, r.new_restore_generation, r.leases_revoked,"
                "       r.integrity_check_outcome, r.dispatcher_unlocked_at, r.operator_ack_at,"
                "       r.operator_ack_principal, s.artifact_sha256, m.manifest_sha256"
                "  FROM restore_record AS r"
                "  JOIN backup_snapshot AS s ON s.id = r.backup_snapshot_id"
                "  JOIN backup_manifest AS m ON m.backup_snapshot_id = s.id"
                " WHERE r.id = ?",
                (reconciled["restore"].restore_id,),
            )
            .mappings()
            .one()
        )
    assert all(value is not None for value in row.values())
    # RPO/RTO measured against a real environment is E3 and stays NOT_RUN (card §8).
    assert utc_now_ms().endswith("Z")
