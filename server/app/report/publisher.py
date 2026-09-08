"""``report.publish`` -- ``TXN-report-publish``: six checks, one commit, one winner.

**Commit point: the COMMIT of the single ``engine.begin()`` block in :func:`_publish_period`
(and, for an empty period, in :func:`_publish_empty_period`).**
Everything ``contracts/reporting/time-and-tags.md`` §4.5 lists lands in that one transaction --
``report``, ``report_item``, ``emerging_direction``, ``coverage_window``,
``first_announced_ledger``, ``pending_item_ledger``, the backfill consumption, the frozen
``tag_config_version_id`` and the delivery **intent**. Nothing in the list is committed on its
own, and no network call happens inside it (SRC-PLAN §5.1: an external effect leaves through a
committed intent, never through a socket held open across a SQLite transaction).

The CAS, and why the arbiter is an index
-----------------------------------------
``ux_coverage_window_predecessor`` decides which of two concurrent publishers wins. It is a
UNIQUE index rather than a read-then-write check because a read-then-write check is a race: two
builders that both read predecessor ``P`` both pass it. The loser gets an ``IntegrityError``,
rolls back **everything**, is marked ``aborted`` with ``abort_reason = 'cas_conflict'``
(``T-RP-05``) and is handed ``CONFLICT`` -- not ``IDEMPOTENCY_CONFLICT``, which is the
different situation of one key with two payloads. It must then re-read the pointer and rebuild
under a **new** ``report_build_id``; retrying the same item set against a new predecessor is a
``forbidden_effect`` of fixture ``g``.

The six checks, in the contract's order
----------------------------------------
``contracts/state/report.yaml`` ``publish_cas.checks_in_order``:

======  =============================  ================================
order   check                          failure
======  =============================  ================================
1       coverage predecessor           ``CONFLICT``
2       tag config version             ``TAG_VERSION_STALE``
3       embedding generation           ``EMBEDDING_GENERATION_MISMATCH``
4       analysis generation            ``VALIDATION_ERROR``
5       pending items decide quality   ``VALIDATION_ERROR``
6       storage health                 ``STORAGE_WRITE_FAILED``
======  =============================  ================================

The order is not cosmetic. Checks 1-5 are reads, so running them before check 6 means the
storage guard is the last thing consulted before the first write -- the guard's own contract is
"ask before you write", and a check that ran after a write would be decoration.

Immutability after publish (I05)
---------------------------------
``content_hash = sha256(JCS(read model))`` is computed inside the publish transaction, from
ids minted up front and from the pending rows that transaction is opening, and it is stored in
the same commit. Every later read rebuilds the read model from the stored rows and must get the
same string. Delivery never writes to ``report``; a changed hash therefore means a published
period was mutated, which is the failure I05 names.

Why the item's read-model extras live in ``report_item.selection_reason``
--------------------------------------------------------------------------
``entities.yaml`` gives this package the shape of that JSON column, and the read model has to
be **immutable** even though some of the rows it is derived from are not: an identity merge
rewrites ``first_announced_ledger`` (§8.3) and can mark an ``analysis`` row
``superseded_by_merge``. Re-deriving those at read time would let a published period change
under a reader, so the resolved values are frozen into the column at publish. The report-level
``coverage_note`` is frozen the same way, under the reserved key ``report_context``:
``ENT-report`` has no column for it while ``report.schema.json`` makes it required and
immutable, and adding a column would put the schema and ``entities.yaml`` in disagreement.
``CR-TC-REPORT-05`` asks for the proper column.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import ReportAbortReason, ReportQuality, ReportStatus
from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import IntegrityError, OperationalError

from server.app.db.engine import session_scope
from server.app.report.builder import (
    EMERGING_DIRECTION_LABEL,
    MODULE_ID,
    BuildSnapshot,
    EmbeddingPort,
    SelectedItem,
    TagConfigVersion,
    TagConfigVersionPort,
)
from server.app.report.coverage import (
    REPORT_SCHEMA_VERSION,
    CoverageRepository,
    CoverageWindow,
    ReportError,
    content_hash_of,
    new_ulid,
    utc_now_ms,
)

#: ``contracts/modules.yaml``: ``report.publish`` has exactly one caller -- this module.
PUBLISH_CALLERS: Final[frozenset[str]] = frozenset({MODULE_ID})

#: ``contracts/modules.yaml``: ``report.build`` is called by the job service.
BUILD_CALLERS: Final[frozenset[str]] = frozenset({"MOD-job-service"})

#: The reserved key of ``report_item.selection_reason`` that freezes the report-level note.
REPORT_CONTEXT_KEY: Final = "report_context"

#: ``report.schema.json`` ``report_item.summary_state``: the value that means the summary is
#: **final** for this item -- a ``analysis[status='valid', task_type='summary']`` row exists and
#: the item points at it. The other member, ``pending``, covers all four
#: ``pending_item_ledger.reason`` values, so "not present" is the whole of "not yet settled".
#: :func:`_write_first_announcements` is the one place that reads it, and the reason it does is
#: written out there.
SUMMARY_FINAL: Final = "present"


class StorageGuardPort(Protocol):
    """The write gate ``TC-storage-write-blocked-readiness`` provides.

    Optional for the same reason ``server/app/embedding/service.py`` makes it optional: card §4
    lists ``storage.get_health`` under *Consumes*, but ``contracts/modules.yaml`` has **no**
    ``MOD-report-service -> MOD-data-store`` edge (only health and job services have one). The
    contract is the naming authority, not the card, so this module never calls the operation
    itself -- it accepts a guard the caller already holds. Reported as ``CR-TC-REPORT-06``,
    mirroring ``CR-TC-embedding-02``.
    """

    def assert_writable(self, operation_id: OperationId) -> None: ...


class DeliveryIntentPort(Protocol):
    """``delivery.create_intent``, called **with this module's open connection**.

    Passing the connection is the outbox pattern of SRC-PLAN §5.1: the intent commits with the
    report, so a crash between publishing and sending loses neither. An empty period does not
    call this at all (REQ-D57).
    """

    def create_report_intent(
        self, *, connection: Connection, owner_id: str, report_id: str
    ) -> Mapping[str, Any]: ...


class RunOutcomePort(Protocol):
    """``run.status`` / ``run.outcome`` (§4.5 item 10) -- ``MOD-job-service``'s rows.

    ``ENT-run`` has no table in this repository (the scheduler card owns it and lands in the
    same wave), so this is a seam rather than a write. When it is absent the publish still
    commits everything this module owns, and the handoff records the run row as ``NOT_RUN``
    rather than pretending it was written.
    """

    def record_period_outcome(
        self, *, connection: Connection, owner_id: str, run_id: str | None, outcome: str
    ) -> None: ...


@dataclass
class PublishContext:
    """Everything ``report.publish`` needs, injected. No module-level singletons."""

    engine: Engine
    tag_port: TagConfigVersionPort
    embedding_port: EmbeddingPort
    storage_guard: StorageGuardPort | None = None
    delivery: DeliveryIntentPort | None = None
    run_outcome: RunOutcomePort | None = None
    coverage: CoverageRepository = field(default_factory=CoverageRepository)
    clock: Callable[[], str] = utc_now_ms
    id_factory: Callable[[], str] = new_ulid


@dataclass(frozen=True, slots=True)
class PublishResult:
    """What ``report.publish`` answers with (``ports.yaml`` ``response_summary_vi``)."""

    report_id: str
    status: str
    abort_reason: str | None
    coverage_window_id: str | None
    coverage_from: str | None
    coverage_to: str | None
    quality: str | None
    content_hash: str | None
    delivery_intent_id: str | None
    read_model: Mapping[str, Any] | None
    replayed: bool = False

    @property
    def published(self) -> bool:
        return self.status == ReportStatus.PUBLISHED.value


class _CasLost(Exception):
    """Internal signal: the UNIQUE index refused the window. Never leaves this module."""


#: The exceptions SQLite raises when it cannot write -- a full volume, a read-only file, a
#: lock it never got. ``sqlite3.OperationalError`` appears bare when the fault is injected
#: before SQLAlchemy wraps it (``server/app/db/faults.py``), and wrapped otherwise.
WRITE_FAILURES: Final = (OperationalError, sqlite3.OperationalError)


def _storage_write_failed(context: PublishContext, operation: OperationId) -> ReportError:
    """``STORAGE_WRITE_FAILED``: nothing committed, so nothing advanced.

    The build stays at ``building`` rather than being marked ``aborted``: writing the abort
    would be another write, on a database that just refused one. ``T-RP-06`` sweeps a build
    that stayed ``building`` past ``report_build_stale_after``, which is the path that exists
    for exactly this.
    """
    return ReportError(
        ErrorCode.STORAGE_WRITE_FAILED,
        details_safe={
            "failed_operation_id": operation.value,
            "observed_at": context.clock(),
        },
    )


# ======================================================================================
# T-RP-01 -- open the build
# ======================================================================================


def record_build(
    context: PublishContext,
    snapshot: BuildSnapshot,
    *,
    caller_module: str = "MOD-job-service",
) -> str:
    """``T-RP-01``: persist the ``building`` row that anchors ``report_build_id``.

    **Commit point: the COMMIT of the ``engine.begin()`` block below.**

    This row is the receipt the idempotency rule needs. ``publish_cas.idempotency_rule_vi``
    case (4) is "no row at all ⇒ ``NOT_FOUND``: publish does not create a build", so the row
    has to exist before publish, and ``ux_report_owner_build_id`` is what makes a replay after
    a lost ACK find it instead of advancing coverage a second time (F-A1R2-01).

    ``quality`` starts at ``partial`` because the column is NOT NULL and the answer is not yet
    known: ``complete`` is a claim that every selected item has a summary, and at ``building``
    nobody has checked. Writing the optimistic value and correcting it later is how B17 gets
    violated by accident.
    """
    _require_caller(OperationId.REPORT_BUILD, caller_module, BUILD_CALLERS)
    _assert_writable(context, OperationId.REPORT_BUILD)
    # `created_at` IS the build snapshot instant, not "whenever this row happened to be
    # written": `built_at` is part of the published read model and therefore part of
    # `content_hash`, so the two have to be the same value or a rebuilt read model would not
    # hash to the stored digest.
    now = snapshot.built_at
    with session_scope(context.engine) as connection:
        existing = _report_by_build_id(connection, snapshot.owner_id, snapshot.report_build_id)
        if existing is not None:
            # ports.yaml: "Cùng build_id không tạo hai bản dựng."
            return str(existing["id"])
        report_id = context.id_factory()
        connection.execute(
            text(
                "INSERT INTO report (id, owner_id, coverage_from, coverage_to,"
                " tag_config_version_id, embedding_generation_id, report_build_id, status,"
                " abort_reason, quality, published_at, content_hash, selection_version,"
                " created_at, updated_at)"
                " VALUES (:id, :owner, :cfrom, :cto, :tcv, :gen, :build, 'building', NULL,"
                " 'partial', NULL, NULL, :selection, :now, :now)"
            ),
            {
                "id": report_id,
                "owner": snapshot.owner_id,
                "cfrom": snapshot.window_plan.window_from,
                "cto": snapshot.window_plan.window_to,
                "tcv": snapshot.tag_config_version.id,
                "gen": snapshot.generation.generation_id,
                "build": snapshot.report_build_id,
                "selection": snapshot.selection_version,
                "now": now,
            },
        )
    return report_id


# ======================================================================================
# report.publish
# ======================================================================================


def publish_report(
    context: PublishContext,
    snapshot: BuildSnapshot,
    *,
    caller_module: str = MODULE_ID,
    empty_period_allowed: bool = True,
    attempt_number: int = 1,
) -> PublishResult:
    """``report.publish`` -- the CAS transaction of ``T-RP-02`` / ``T-RP-05`` / ``T-RP-07``.

    :param empty_period_allowed: ``T-RP-07``'s guard has two halves -- nothing was selected
        **and** nothing was missing (``limit_hit`` false, ``cursor_invalidated`` false, no
        unhandled ``SOURCE_METADATA_UNAVAILABLE``). This module can see the first half and not
        the second, because those flags live on ``ENT-run``, which has no table here. The job
        service passes ``False`` when the run fell short, and an empty selection is then a
        ``builder_failure`` rather than a valid empty period -- which is the distinction
        §4.4 insists on: "a failed collection run does not become a successful empty period".
    :param attempt_number: reported in the ``CONFLICT`` envelope so a caller can see its
        position in ``cas_conflict_retries`` (3, ``contracts/retry-policy.yaml``).

    :raises ReportError: ``CONFLICT``, ``TAG_VERSION_STALE``,
        ``EMBEDDING_GENERATION_MISMATCH``, ``VALIDATION_ERROR``, ``IDEMPOTENCY_CONFLICT``,
        ``NOT_FOUND`` or ``STORAGE_WRITE_FAILED``.
    """
    _require_caller(OperationId.REPORT_PUBLISH, caller_module, PUBLISH_CALLERS)

    replay = _replay(context, snapshot)
    if replay is not None:
        return replay

    frozen = _check_tag_and_generation(context, snapshot)
    _check_analysis_generation(context, snapshot)
    _check_quality_rule(snapshot)
    _assert_writable(context, OperationId.REPORT_PUBLISH)

    if snapshot.is_empty_period:
        if not empty_period_allowed:
            _abort(context, snapshot, ReportAbortReason.BUILDER_FAILURE)
            raise ReportError(
                ErrorCode.VALIDATION_ERROR,
                message_safe="Đợt thu thập chưa hoàn tất nên kỳ rỗng không hợp lệ.",
                details_safe={
                    "operation_id": OperationId.REPORT_PUBLISH.value,
                    "field_path": "empty_period_allowed",
                    "violation_kind": "run_incomplete",
                },
            )
        return _publish_empty_period(context, snapshot, attempt_number=attempt_number)

    return _publish_period(context, snapshot, frozen, attempt_number=attempt_number)


# --------------------------------------------------------------------------------------
# The six checks
# --------------------------------------------------------------------------------------


def _check_tag_and_generation(context: PublishContext, snapshot: BuildSnapshot) -> TagConfigVersion:
    """Checks 2 and 3. Check 1 runs inside the transaction, where the CAS can enforce it.

    ``tag.freeze_config_version`` is idempotent on ``report_build_id`` and is the operation
    that *is* the freeze point (B01/AMD-B01): the version becomes immutable here, in the
    publish path, not when a digest is later sent.
    """
    try:
        frozen = context.tag_port.freeze_config_version(
            owner_id=snapshot.owner_id,
            report_build_id=snapshot.report_build_id,
            expected_tag_config_version_id=snapshot.tag_config_version.id,
        )
    except ReportError as error:
        if error.code is ErrorCode.TAG_VERSION_STALE:
            _abort(context, snapshot, ReportAbortReason.TAG_VERSION_STALE)
        raise
    if not context.embedding_port.embedding_generation_matches(
        snapshot.owner_id, snapshot.generation.generation_id
    ):
        _abort(context, snapshot, ReportAbortReason.EMBEDDING_GENERATION_MISMATCH)
        raise ReportError(
            ErrorCode.EMBEDDING_GENERATION_MISMATCH,
            details_safe={
                "expected_generation_id": snapshot.generation.generation_id,
                "seen_generation_id": None,
                "dimension_expected": snapshot.generation.dimension,
                "dimension_seen": None,
            },
        )
    return frozen


def _check_analysis_generation(context: PublishContext, snapshot: BuildSnapshot) -> None:
    """Check 4 (owned by PC06): every item points at a ``valid`` analysis of the pinned row.

    An analysis that turned ``superseded_by_merge`` between build and publish is exactly the
    case this catches: the item would otherwise be published pointing at a row that is no
    longer the one being read.
    """
    with session_scope(context.engine) as connection:
        for item in snapshot.items:
            if item.analysis is None:
                continue
            row = (
                connection.execute(
                    text("SELECT status, generation_number FROM analysis WHERE id = :id"),
                    {"id": item.analysis["analysis_id"]},
                )
                .mappings()
                .first()
            )
            if (
                row is None
                or str(row["status"]) != "valid"
                or int(row["generation_number"]) != int(item.analysis["generation_number"])
            ):
                raise ReportError(
                    ErrorCode.VALIDATION_ERROR,
                    message_safe="Bản phân tích của một mục đã đổi sau khi dựng kỳ báo cáo.",
                    details_safe={
                        "operation_id": OperationId.REPORT_PUBLISH.value,
                        "field_path": "items[].analysis.analysis_id",
                        "violation_kind": "analysis_generation_stale",
                    },
                )


def _check_quality_rule(snapshot: BuildSnapshot) -> None:
    """Check 5: ``quality = complete`` **iff** this period has no pending row (B17, O-5.3).

    Computed rather than accepted from the caller, so "complete with pending items" is not
    representable: it is the forbidden transition of ``contracts/state/report.yaml``.
    """
    if _quality_of(snapshot) == ReportQuality.COMPLETE.value and snapshot.pending:
        raise ReportError(  # pragma: no cover - unreachable by construction, kept as a guard
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.REPORT_PUBLISH.value,
                "field_path": "quality",
                "violation_kind": "complete_with_pending_items",
            },
        )


def _quality_of(snapshot: BuildSnapshot) -> str:
    return ReportQuality.COMPLETE.value if not snapshot.pending else ReportQuality.PARTIAL.value


# --------------------------------------------------------------------------------------
# Idempotent replay (publish_cas.idempotency_rule_vi)
# --------------------------------------------------------------------------------------


def _replay(context: PublishContext, snapshot: BuildSnapshot) -> PublishResult | None:
    """The four cases of ``idempotency_rule_vi``, in order.

    Case (1) is the one that matters after a lost ACK: the *same* report comes back, coverage
    does not advance, no second delivery intent appears and ``content_hash`` is unchanged. That
    is why an empty period still leaves a ``report`` row -- without it there would be no
    receipt to find, and the replay would try to advance coverage a second time (§4.7.1).
    """
    with session_scope(context.engine) as connection:
        row = _report_by_build_id(connection, snapshot.owner_id, snapshot.report_build_id)
        if row is None:
            raise ReportError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.REPORT_PUBLISH.value,
                    "resource_kind": "report",
                },
            )
        status = str(row["status"])
        if status == ReportStatus.PUBLISHED.value:
            window = context.coverage.window_for_report(
                connection, snapshot.owner_id, str(row["id"])
            )
            return PublishResult(
                report_id=str(row["id"]),
                status=status,
                abort_reason=None,
                coverage_window_id=None if window is None else window.id,
                coverage_from=str(row["coverage_from"]),
                coverage_to=str(row["coverage_to"]),
                quality=str(row["quality"]),
                content_hash=str(row["content_hash"]),
                delivery_intent_id=None,
                read_model=read_model(
                    connection, context, owner_id=snapshot.owner_id, report_id=str(row["id"])
                ),
                replayed=True,
            )
        if status == ReportStatus.ABORTED.value:
            if str(row["abort_reason"]) == ReportAbortReason.EMPTY_PERIOD.value:
                # The empty-period receipt, and the whole reason §4.7.1 chose option (b).
                # Fixture d's negative oracle: replaying the same build_id creates no second
                # coverage window and does NOT answer CONFLICT -- it hands back the old result.
                empty = _empty_window_for_build(connection, snapshot)
                return PublishResult(
                    report_id=str(row["id"]),
                    status=status,
                    abort_reason=ReportAbortReason.EMPTY_PERIOD.value,
                    coverage_window_id=None if empty is None else empty.id,
                    coverage_from=str(row["coverage_from"]),
                    coverage_to=str(row["coverage_to"]),
                    quality=None,
                    content_hash=None,
                    delivery_intent_id=None,
                    read_model=None,
                    replayed=True,
                )
            raise ReportError(
                ErrorCode.CONFLICT,
                message_safe="Bản dựng này đã bị bỏ; hãy dựng lại với build id mới.",
                details_safe={"resource_kind": "report"},
            )
    return None


def _empty_window_for_build(
    connection: Connection, snapshot: BuildSnapshot
) -> CoverageWindow | None:
    """The ``report_id IS NULL`` window an empty period left, found by its boundaries."""
    repository = CoverageRepository()
    for window in repository.windows_in_order(connection, snapshot.owner_id):
        if window.report_id is None and window.window_from == snapshot.window_plan.window_from:
            return window
    return None


# --------------------------------------------------------------------------------------
# The empty period (T-RP-07)
# --------------------------------------------------------------------------------------


def _publish_empty_period(
    context: PublishContext, snapshot: BuildSnapshot, *, attempt_number: int
) -> PublishResult:
    """One transaction: ``coverage_window(report_id = NULL)`` + ``report(aborted)``.

    Coverage **advances**. No display report, no ``outbox_intent``, no digest (REQ-D57,
    AMD-B04). Skipping the window is the failure mode this branch exists to prevent: the next
    period would have no ``coverage_from`` and the chain would have a hole (I06).
    """
    now = context.clock()
    window_id = context.id_factory()
    report_id = _report_id_of(context, snapshot)
    try:
        with session_scope(context.engine) as connection:
            _assert_predecessor(context, connection, snapshot)
            _insert_window(context, connection, snapshot, window_id, report_id=None, now=now)
            connection.execute(
                text(
                    "UPDATE report SET status = 'aborted', abort_reason = 'empty_period',"
                    " updated_at = :now WHERE id = :id"
                ),
                {"now": now, "id": report_id},
            )
            if context.run_outcome is not None:
                context.run_outcome.record_period_outcome(
                    connection=connection,
                    owner_id=snapshot.owner_id,
                    run_id=snapshot.run_id,
                    outcome="empty",
                )
    except _CasLost as lost:
        raise _cas_conflict(context, snapshot, attempt_number) from lost
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(context, OperationId.REPORT_PUBLISH) from exc
    return PublishResult(
        report_id=report_id,
        status=ReportStatus.ABORTED.value,
        abort_reason=ReportAbortReason.EMPTY_PERIOD.value,
        coverage_window_id=window_id,
        coverage_from=snapshot.window_plan.window_from,
        coverage_to=snapshot.window_plan.window_to,
        quality=None,
        content_hash=None,
        delivery_intent_id=None,
        read_model=None,
    )


# --------------------------------------------------------------------------------------
# The published period (T-RP-02)
# --------------------------------------------------------------------------------------


def _publish_period(
    context: PublishContext,
    snapshot: BuildSnapshot,
    frozen: TagConfigVersion,
    *,
    attempt_number: int,
) -> PublishResult:
    """Everything of §4.5, inside one ``engine.begin()``. **That COMMIT is the commit point.**

    The read model is assembled *inside* the transaction because two of its fields are only
    known once rows are being written: the ``pending_item_ledger`` ids, and which pending
    entries actually open a new row (a target already pending keeps its original row and its
    original window, ``ux_pending_owner_target_open``). Assembling outside would put values in
    ``content_hash`` that the stored rows do not carry, and the I05 oracle -- rebuild, rehash,
    compare -- would fail for a reason that has nothing to do with immutability.
    """
    now = context.clock()
    report_id = _report_id_of(context, snapshot)
    window_id = context.id_factory()
    item_ids = [context.id_factory() for _ in snapshot.items]
    direction_ids = [direction.direction_id for direction in snapshot.directions]
    quality = _quality_of(snapshot)

    intent_id: str | None = None
    body: dict[str, Any]
    try:
        with session_scope(context.engine) as connection:
            _assert_predecessor(context, connection, snapshot)
            _insert_window(context, connection, snapshot, window_id, report_id=report_id, now=now)
            pending_view = _write_pending(context, connection, snapshot, window_id)

            body = _assemble_read_model(
                snapshot,
                frozen=frozen,
                report_id=report_id,
                window_id=window_id,
                item_ids=item_ids,
                direction_ids=direction_ids,
                published_at=now,
                quality=quality,
                pending=pending_view,
            )
            digest = content_hash_of(body)
            body = {**body, "content_hash": digest}

            connection.execute(
                text(
                    "UPDATE report SET status = 'published', abort_reason = NULL,"
                    " quality = :quality, published_at = :now, content_hash = :hash,"
                    " selection_version = :selection, tag_config_version_id = :tcv,"
                    " coverage_from = :cfrom, coverage_to = :cto, updated_at = :now"
                    " WHERE id = :id"
                ),
                {
                    "quality": quality,
                    "now": now,
                    "hash": digest,
                    "selection": snapshot.selection_version,
                    "tcv": frozen.id,
                    "cfrom": snapshot.window_plan.window_from,
                    "cto": snapshot.window_plan.window_to,
                    "id": report_id,
                },
            )
            _insert_items(connection, snapshot, report_id, item_ids, body)
            _insert_directions(connection, snapshot, report_id, direction_ids)
            _write_first_announcements(connection, snapshot, report_id, now)
            _consume_backfill(connection, snapshot, report_id, now)
            if context.delivery is not None:
                intent = context.delivery.create_report_intent(
                    connection=connection, owner_id=snapshot.owner_id, report_id=report_id
                )
                intent_id = None if intent is None else str(intent.get("intent_id"))
            if context.run_outcome is not None:
                context.run_outcome.record_period_outcome(
                    connection=connection,
                    owner_id=snapshot.owner_id,
                    run_id=snapshot.run_id,
                    outcome="delivered" if intent_id else "reported",
                )
    except _CasLost as lost:
        raise _cas_conflict(context, snapshot, attempt_number) from lost
    except WRITE_FAILURES as exc:
        raise _storage_write_failed(context, OperationId.REPORT_PUBLISH) from exc

    return PublishResult(
        report_id=report_id,
        status=ReportStatus.PUBLISHED.value,
        abort_reason=None,
        coverage_window_id=window_id,
        coverage_from=snapshot.window_plan.window_from,
        coverage_to=snapshot.window_plan.window_to,
        quality=quality,
        content_hash=digest,
        delivery_intent_id=intent_id,
        read_model=body,
    )


def _assert_predecessor(
    context: PublishContext,
    connection: Connection,
    snapshot: BuildSnapshot,
) -> None:
    """Check 1, read inside the transaction. The **index** is still the arbiter.

    This read catches the common case early and gives the caller a useful envelope
    (``expected_predecessor_id`` / ``current_predecessor_id``); it does not replace the
    UNIQUE index, because between this read and the insert another transaction may still
    commit. Both are needed: the read for the message, the index for the truth.
    """
    expected = None if snapshot.predecessor is None else snapshot.predecessor.id
    current = context.coverage.current_window(connection, snapshot.owner_id)
    current_id = None if current is None else current.id
    if current_id != expected:
        raise _CasLost(f"{expected!r} -> {current_id!r}")


def _insert_window(
    context: PublishContext,
    connection: Connection,
    snapshot: BuildSnapshot,
    window_id: str,
    *,
    report_id: str | None,
    now: str,
) -> None:
    try:
        context.coverage.insert_window(
            connection,
            window_id=window_id,
            owner_id=snapshot.owner_id,
            plan=snapshot.window_plan,
            report_id=report_id,
            advanced_at=now,
        )
    except IntegrityError as exc:
        # ux_coverage_window_predecessor (or ux_coverage_window_bootstrap) refused. This is
        # the CAS and this is the loss; everything in the transaction rolls back.
        raise _CasLost(str(exc)) from exc


def _cas_conflict(
    context: PublishContext, snapshot: BuildSnapshot, attempt_number: int
) -> ReportError:
    """``T-RP-05``: mark the losing build ``aborted`` and hand back ``CONFLICT``.

    The abort is a **separate** transaction on purpose: the losing one has already rolled
    back, and writing into it would be writing into a transaction the database discarded. The
    loser leaves exactly one ``report`` row at ``aborted`` and zero ``report_item`` rows,
    which is fixture ``g``'s row oracle.
    """
    _abort(context, snapshot, ReportAbortReason.CAS_CONFLICT)
    with session_scope(context.engine) as connection:
        current = context.coverage.current_window(connection, snapshot.owner_id)
    return ReportError(
        ErrorCode.CONFLICT,
        details_safe={
            "resource_kind": "coverage_window",
            "expected_predecessor_id": (
                None if snapshot.predecessor is None else snapshot.predecessor.id
            ),
            "current_predecessor_id": None if current is None else current.id,
            "attempt_number": attempt_number,
        },
    )


def _abort(context: PublishContext, snapshot: BuildSnapshot, reason: ReportAbortReason) -> None:
    """Mark the build ``aborted`` with an explicit reason (``ck_report_abort_reason``).

    ``abort_reason`` is what keeps ``aborted`` from meaning six different things at once --
    most importantly it keeps a *valid empty period* apart from a *broken build*, which is the
    I13 distinction the UI depends on.
    """
    now = context.clock()
    with session_scope(context.engine) as connection:
        connection.execute(
            text(
                "UPDATE report SET status = 'aborted', abort_reason = :reason,"
                " updated_at = :now WHERE owner_id = :owner AND report_build_id = :build"
                "   AND status = 'building'"
            ),
            {
                "reason": reason.value,
                "now": now,
                "owner": snapshot.owner_id,
                "build": snapshot.report_build_id,
            },
        )


# --------------------------------------------------------------------------------------
# The rows of §4.5
# --------------------------------------------------------------------------------------


def _insert_items(
    connection: Connection,
    snapshot: BuildSnapshot,
    report_id: str,
    item_ids: Sequence[str],
    body: Mapping[str, Any],
) -> None:
    for item, item_id, view in zip(snapshot.items, item_ids, body["items"], strict=True):
        candidate = item.candidate
        connection.execute(
            text(
                "INSERT INTO report_item (id, owner_id, report_id, target_kind,"
                " target_work_id, target_post_id, target_key, item_type,"
                " first_announced_report_id, analysis_id, selection_reason)"
                " VALUES (:id, :owner, :report, :kind, :work, :post, :key, :type, :first,"
                " :analysis, :reason)"
            ),
            {
                "id": item_id,
                "owner": snapshot.owner_id,
                "report": report_id,
                "kind": candidate.target_kind,
                "work": candidate.target_id if candidate.target_kind == "work" else None,
                "post": candidate.target_id if candidate.target_kind == "post" else None,
                # Written once, never regenerated: a published item's key is frozen (I05/I17)
                # and the CHECK in the migration is what makes "written once" also "written
                # right".
                "key": candidate.target_key,
                "type": item.item_type,
                "first": (
                    None
                    if item.first_announced is None
                    else item.first_announced["first_announced_report_id"]
                ),
                "analysis": None if item.analysis is None else item.analysis["analysis_id"],
                # The frozen read-model extras. See the module docstring: re-deriving them
                # later would let a merge change a published period (I05).
                "reason": json.dumps(
                    {
                        **{
                            key: value
                            for key, value in view.items()
                            if key not in ("report_item_id", "target", "target_key")
                        },
                        REPORT_CONTEXT_KEY: body["coverage_note"],
                    },
                    sort_keys=True,
                    ensure_ascii=False,
                ),
            },
        )


def _insert_directions(
    connection: Connection,
    snapshot: BuildSnapshot,
    report_id: str,
    direction_ids: Sequence[str],
) -> None:
    for direction, direction_id in zip(snapshot.directions, direction_ids, strict=True):
        view = direction.as_read_model()
        connection.execute(
            text(
                "INSERT INTO emerging_direction (id, owner_id, report_id,"
                " member_target_keys, density_metric, evidence_state, embedding_generation_id)"
                " VALUES (:id, :owner, :report, :members, :metric, :state, :generation)"
            ),
            {
                "id": direction_id,
                "owner": snapshot.owner_id,
                "report": report_id,
                "members": json.dumps(list(direction.member_target_keys)),
                "metric": json.dumps(
                    {
                        key: value
                        for key, value in view.items()
                        if key
                        not in ("direction_id", "evidence_state", "member_target_keys", "label")
                    },
                    sort_keys=True,
                    ensure_ascii=False,
                ),
                "state": direction.evidence_state,
                "generation": direction.embedding_generation_id,
            },
        )


def _write_first_announcements(
    connection: Connection, snapshot: BuildSnapshot, report_id: str, now: str
) -> None:
    """§4.5 item 5 / §8.2: one row per ``new_discovery`` **work** whose summary is final.

    Post-only targets get no row: the ledger is keyed on ``canonical_work_id`` and a post-only
    target has no canonical identity (§8.1). "Already announced" for them is derived from the
    immutable published history instead.

    Why ``summary_state == 'present'`` is a condition (``CR-TC-BACKFILL-09``, ``F-A3-P4-01``)
    ---------------------------------------------------------------------------------------
    The controlling clause is ``contracts/reporting/time-and-tags.md`` **§5.3**, third bullet:

        *"``item_type`` **không** đổi vì việc này: một mục phát hiện muộn chưa từng được công bố
        vẫn là ``new_discovery`` (§8). 'Phát hiện muộn' là nhãn hiển thị, không phải loại mục."*

    Read it against §8.2 rule 2, which is **total**: a candidate that already has an effective
    ledger row *must* become ``prior_reference``, and "không có nhánh nào cho phép công bố lại
    như phát hiện mới". Those two are only simultaneously satisfiable if an item that is still
    waiting for its summary is **not** announced. Announcing it would guarantee that the very
    late discovery §5.3 promises will be ``new_discovery`` comes back as ``prior_reference`` —
    the row oracle of fixture ``e-late-analysis-pending-then-late-discovery`` ("item_type vẫn =
    'new_discovery'"), and therefore REQ-D29 / REQ-AC09 / I07.

    So the announcement waits for the summary. The item is **not** hidden meanwhile — §7.3 and
    AMD-B17 put it in ``report_item`` with ``summary_state = 'pending'`` and make the period
    ``quality = 'partial'`` — but appearing in a partial period is not the same event as being
    *announced*, and the open ``pending_item_ledger`` row is the durable record of that
    difference. The consequence is deliberate and worth stating plainly: a work can be listed
    as ``new_discovery`` in two consecutive periods, once without a summary and once with one.
    §5.3 blesses exactly that, and the second appearance carries ``late_discovery = true`` so a
    reader sees why.

    ``budget_exceeded`` items never reach here at all: they are not in ``snapshot.items``.
    """
    for item in snapshot.items:
        if item.item_type != "new_discovery" or item.candidate.target_kind != "work":
            continue
        if item.summary_state != SUMMARY_FINAL:
            continue
        connection.execute(
            text(
                "INSERT INTO first_announced_ledger (id, owner_id, canonical_work_id,"
                " first_report_id, first_announced_at, merge_audit_id, superseded_by_merge_id)"
                " VALUES (:id, :owner, :work, :report, :at, NULL, NULL)"
            ),
            {
                "id": new_ulid(),
                "owner": snapshot.owner_id,
                "work": item.candidate.target_id,
                "report": report_id,
                "at": now,
            },
        )


def _write_pending(
    context: PublishContext,
    connection: Connection,
    snapshot: BuildSnapshot,
    window_id: str,
) -> list[dict[str, Any]]:
    """§4.5 item 6: open the new pending rows, close the ones this period resolved.

    Returns the ``pending_items`` block of the read model -- the rows whose
    ``first_pending_window_id`` is **this** period's window, which is exactly what
    ``report.get`` will later join back. A target that was already pending keeps its original
    row and its original window (``ux_pending_owner_target_open``), so it belongs to that
    period's list and not to this one; ``pending_since_window_sequence`` on the item is what
    renders "phát hiện muộn, thuộc kỳ #12".

    Nothing is ever deleted. O-5.1 counts the ledger across a publish and the arithmetic has
    to balance: rows leave ``pending`` only by becoming ``resolved_reported_late`` or
    ``abandoned_by_owner``, and both of those stay in the table.
    """
    for target_key in snapshot.resolved_pending_target_keys:
        connection.execute(
            text(
                "UPDATE pending_item_ledger SET state = 'resolved_reported_late'"
                " WHERE owner_id = :owner AND target_key = :key AND state = 'pending'"
            ),
            {"owner": snapshot.owner_id, "key": target_key},
        )
    view: list[dict[str, Any]] = []
    for entry in snapshot.pending:
        already_open = connection.execute(
            text(
                "SELECT 1 FROM pending_item_ledger WHERE owner_id = :owner"
                " AND target_key = :key AND state = 'pending'"
            ),
            {"owner": snapshot.owner_id, "key": entry.target_key},
        ).first()
        if already_open is not None:
            continue
        ledger_id = context.id_factory()
        connection.execute(
            text(
                "INSERT INTO pending_item_ledger (id, owner_id, target_key, reason,"
                " first_pending_window_id, state)"
                " VALUES (:id, :owner, :key, :reason, :window, 'pending')"
            ),
            {
                "id": ledger_id,
                "owner": snapshot.owner_id,
                "key": entry.target_key,
                "reason": entry.reason,
                "window": window_id,
            },
        )
        view.append(
            {
                "pending_item_ledger_id": ledger_id,
                "target_key": entry.target_key,
                "reason": entry.reason,
                "first_pending_window_sequence": snapshot.window_plan.sequence,
                "state": "pending",
            }
        )
    view.sort(key=lambda row: str(row["pending_item_ledger_id"]))
    return view


def _consume_backfill(
    connection: Connection, snapshot: BuildSnapshot, report_id: str, now: str
) -> None:
    """§6.4: consumption happens **only** here, and only for entitlements actually applied.

    All three conditions of §6.4 are already decided by the time this runs: the transaction is
    committing (1), the builder widened the candidate range for these ledger ids (2), and the
    widening produced at least one row that is being written in this same commit (3). A
    builder crash never reaches this line, which is AMD-B04's "do not consume backfill because
    the builder crashed".
    """
    for ledger_id in snapshot.backfill_ledger_ids_applied:
        connection.execute(
            text(
                "UPDATE backfill_ledger SET entitlement = 'consumed',"
                " consumed_in_report_id = :report, consumed_at = :now"
                " WHERE owner_id = :owner AND id = :id AND consumed_in_report_id IS NULL"
            ),
            {"report": report_id, "now": now, "owner": snapshot.owner_id, "id": ledger_id},
        )


# ======================================================================================
# The read model (contracts/schemas/report.schema.json)
# ======================================================================================


def _target_object(
    kind: str, identifier: str, target_key: str, identity_state: str
) -> dict[str, Any]:
    """The tagged union of ``contracts/schemas/target.schema.json``, exactly.

    Both branches are ``additionalProperties: false`` and they do **not** carry the same
    fields: ``identity_state`` belongs to ``work_target`` only, and a post says
    ``identity_resolution`` instead. Copying the work shape onto a post would be rejected by
    the schema -- correctly, because a post has no canonical identity to be quarantined
    (identity.md §4).
    """
    if kind == "work":
        return {
            "kind": "work",
            "work_id": identifier,
            "target_key": target_key,
            "identity_state": identity_state,
        }
    return {
        "kind": "post",
        "post_id": identifier,
        "target_key": target_key,
        "identity_resolution": "resolved_post_only",
    }


def _item_read_model(item: SelectedItem, item_id: str) -> dict[str, Any]:
    candidate = item.candidate
    body: dict[str, Any] = {
        "report_item_id": item_id,
        "target": _target_object(
            candidate.target_kind,
            candidate.target_id,
            candidate.target_key,
            candidate.identity_state,
        ),
        "target_key": candidate.target_key,
        "item_type": item.item_type,
        "matched_tags": [matched.as_read_model() for matched in item.matched_tags],
        "late_discovery": candidate.from_pending,
        "selected_via_backfill": candidate.selected_via_backfill,
        "identity_state": candidate.identity_state,
        "summary_state": item.summary_state,
        "discovered_at": candidate.discovered_at,
        "ingest_sequence": candidate.ingest_sequence,
        "pending_since_window_sequence": candidate.pending_since_window_sequence,
    }
    if item.excluded_by:
        body["excluded_by"] = [excluded.as_read_model() for excluded in item.excluded_by]
    if item.analysis is not None:
        body["analysis"] = dict(item.analysis)
    if item.first_announced is not None:
        body["first_announced"] = dict(item.first_announced)
        body["reference_reason"] = item.reference_reason
    if candidate.selected_via_backfill:
        body["backfill_ledger_id"] = candidate.backfill_ledger_id
    return body


def _assemble_read_model(
    snapshot: BuildSnapshot,
    *,
    frozen: TagConfigVersion,
    report_id: str,
    window_id: str,
    item_ids: Sequence[str],
    direction_ids: Sequence[str],
    published_at: str,
    quality: str,
    pending: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    plan = snapshot.window_plan
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_id": report_id,
        "report_build_id": snapshot.report_build_id,
        "owner_id": snapshot.owner_id,
        "status": ReportStatus.PUBLISHED.value,
        "quality": quality,
        "coverage": {
            "coverage_window_id": window_id,
            "sequence": plan.sequence,
            "coverage_from": plan.window_from,
            "coverage_to": plan.window_to,
            "ingest_sequence_from": plan.ingest_sequence_from,
            "ingest_sequence_to": plan.ingest_sequence_to,
            "predecessor_window_id": plan.predecessor_window_id,
        },
        "tag_config_version": {
            "tag_config_version_id": frozen.id,
            "sequence": frozen.sequence,
            "content_hash": frozen.content_hash,
            # report.schema.json: "Bằng published_at: freeze xảy ra TRONG transaction publish".
            "frozen_at": published_at,
        },
        "selection_version": snapshot.selection_version,
        "embedding_generation": {
            "embedding_generation_id": snapshot.generation.generation_id,
            "model_name": snapshot.generation.model_name,
            "model_version": snapshot.generation.model_version,
            "dimension": snapshot.generation.dimension,
            "normalization": snapshot.generation.normalization.value,
        },
        "items": [
            _item_read_model(item, item_id)
            for item, item_id in zip(snapshot.items, item_ids, strict=True)
        ],
        "emerging_directions": [
            {**direction.as_read_model(), "direction_id": direction_id}
            for direction, direction_id in zip(snapshot.directions, direction_ids, strict=True)
        ],
        "pending_items": list(pending),
        "coverage_note": dict(snapshot.coverage_note),
        "built_at": snapshot.built_at,
        "published_at": published_at,
        "content_hash": "",
        "evidence_refs": [],
    }


def read_model(
    connection: Connection,
    context: PublishContext,
    *,
    owner_id: str,
    report_id: str,
) -> dict[str, Any] | None:
    """Rebuild the published read model from stored rows -- the ``report.get`` payload.

    Every field comes from a row written inside the publish transaction, so the rebuilt object
    hashes to the stored ``content_hash``. That equality **is** the I05 oracle, and
    :func:`verify_content_hash` is the assertion form of it.
    """
    row = (
        connection.execute(
            text(
                "SELECT id, owner_id, report_build_id, status, quality, coverage_from,"
                "       coverage_to, tag_config_version_id, embedding_generation_id,"
                "       selection_version, published_at, content_hash, created_at"
                "  FROM report WHERE owner_id = :owner AND id = :id"
            ),
            {"owner": owner_id, "id": report_id},
        )
        .mappings()
        .first()
    )
    if row is None or str(row["status"]) != ReportStatus.PUBLISHED.value:
        return None
    window = context.coverage.window_for_report(connection, owner_id, report_id)
    generation_row = (
        connection.execute(
            text(
                "SELECT id, model_name, model_version, dimension, normalization"
                "  FROM embedding_generation WHERE id = :id"
            ),
            {"id": str(row["embedding_generation_id"])},
        )
        .mappings()
        .first()
    )
    if generation_row is None:  # pragma: no cover - the FK on report makes this unreachable
        raise ReportError(
            ErrorCode.INTERNAL,
            details_safe={"operation_id": OperationId.REPORT_GET.value},
        )
    generation = dict(generation_row)
    frozen = context.tag_port.config_version(
        owner_id=owner_id, tag_config_version_id=str(row["tag_config_version_id"])
    )

    item_rows = (
        connection.execute(
            text(
                "SELECT id, target_kind, target_work_id, target_post_id, target_key, item_type,"
                "       selection_reason FROM report_item"
                " WHERE owner_id = :owner AND report_id = :report ORDER BY id"
            ),
            {"owner": owner_id, "report": report_id},
        )
        .mappings()
        .all()
    )
    items: list[dict[str, Any]] = []
    coverage_note: dict[str, Any] = {}
    for item_row in item_rows:
        extras = json.loads(str(item_row["selection_reason"]))
        coverage_note = dict(extras.get(REPORT_CONTEXT_KEY, coverage_note))
        extras.pop(REPORT_CONTEXT_KEY, None)
        kind = str(item_row["target_kind"])
        identifier = str(
            item_row["target_work_id"] if kind == "work" else item_row["target_post_id"]
        )
        items.append(
            {
                "report_item_id": str(item_row["id"]),
                "target": _target_object(
                    kind,
                    identifier,
                    str(item_row["target_key"]),
                    str(extras.get("identity_state", "active")),
                ),
                "target_key": str(item_row["target_key"]),
                **extras,
            }
        )
    # §7.1 again, on the stored values. Sorting by ``report_item_id`` would NOT work: two
    # ULIDs minted in the same millisecond differ only in their random tail, so the publish
    # order is not recoverable from the ids. A stored rank column would recover it but is not
    # in ``ENT-report-item`` and would show up as an extra property under the schema's
    # ``additionalProperties: false``. Re-sorting on the same five keys the builder used is
    # both faithful and total, so the rebuilt list is byte-identical to the published one.
    items.sort(key=_read_model_sort_key)

    direction_rows = (
        connection.execute(
            text(
                "SELECT id, member_target_keys, density_metric, evidence_state"
                "  FROM emerging_direction WHERE owner_id = :owner AND report_id = :report"
                " ORDER BY id"
            ),
            {"owner": owner_id, "report": report_id},
        )
        .mappings()
        .all()
    )
    directions = [
        {
            "direction_id": str(direction["id"]),
            "evidence_state": str(direction["evidence_state"]),
            "label": EMERGING_DIRECTION_LABEL,
            "member_target_keys": json.loads(str(direction["member_target_keys"])),
            **json.loads(str(direction["density_metric"])),
        }
        for direction in direction_rows
    ]

    pending_rows = (
        connection.execute(
            text(
                "SELECT p.id, p.target_key, p.reason, p.state, w.sequence"
                "  FROM pending_item_ledger p"
                "  JOIN coverage_window w ON w.id = p.first_pending_window_id"
                " WHERE p.owner_id = :owner AND w.report_id = :report ORDER BY p.id"
            ),
            {"owner": owner_id, "report": report_id},
        )
        .mappings()
        .all()
    )

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_id": str(row["id"]),
        "report_build_id": str(row["report_build_id"]),
        "owner_id": str(row["owner_id"]),
        "status": ReportStatus.PUBLISHED.value,
        "quality": str(row["quality"]),
        "coverage": {
            "coverage_window_id": "" if window is None else window.id,
            "sequence": 0 if window is None else window.sequence,
            "coverage_from": str(row["coverage_from"]),
            "coverage_to": str(row["coverage_to"]),
            "ingest_sequence_from": 0 if window is None else window.ingest_sequence_from,
            "ingest_sequence_to": 0 if window is None else window.ingest_sequence_to,
            "predecessor_window_id": None if window is None else window.predecessor_window_id,
        },
        "tag_config_version": {
            "tag_config_version_id": frozen.id,
            "sequence": frozen.sequence,
            "content_hash": frozen.content_hash,
            "frozen_at": str(row["published_at"]),
        },
        "selection_version": str(row["selection_version"]),
        "embedding_generation": {
            "embedding_generation_id": str(generation["id"]),
            "model_name": str(generation["model_name"]),
            "model_version": str(generation["model_version"]),
            "dimension": int(generation["dimension"]),
            "normalization": str(generation["normalization"]),
        },
        "items": items,
        "emerging_directions": directions,
        "pending_items": [
            {
                "pending_item_ledger_id": str(pending["id"]),
                "target_key": str(pending["target_key"]),
                "reason": str(pending["reason"]),
                "first_pending_window_sequence": int(pending["sequence"]),
                "state": str(pending["state"]),
            }
            for pending in pending_rows
        ],
        "coverage_note": coverage_note,
        "built_at": str(row["created_at"]),
        "published_at": str(row["published_at"]),
        "content_hash": str(row["content_hash"]),
        "evidence_refs": [],
    }


def _read_model_sort_key(entry: Mapping[str, Any]) -> tuple[int, float, str, int, str]:
    """``contracts/reporting/selection.md`` §7.1, evaluated on a read-model item.

    Keys 4 and 5 (``ingest_sequence``, then ``target_key`` in byte order) make it total, which
    is what lets two processes -- the publisher and a later reader -- agree on the list.
    """
    return (
        0 if str(entry["item_type"]) == "new_discovery" else 1,
        -max(float(tag["score"]) for tag in entry["matched_tags"]),
        str(entry.get("discovered_at", "")),
        int(entry.get("ingest_sequence", 0)),
        str(entry["target_key"]),
    )


def verify_content_hash(body: Mapping[str, Any]) -> bool:
    """Recompute ``sha256(JCS(read model))`` and compare it with the stored value.

    The stored ``content_hash`` is excluded from its own input -- a hash cannot cover itself --
    by hashing the object with that field blanked, exactly as :func:`_publish_period` computed
    it.
    """
    stored = str(body.get("content_hash", ""))
    recomputed = content_hash_of({**dict(body), "content_hash": ""})
    return stored == recomputed


class PublishedDigestPort:
    """``ReportPayloadPort`` for ``MOD-delivery-service``: the frozen payload, never a re-render.

    Fixture ``c`` is the case that makes this matter: the tag set changes after publish and
    before the send, and the payload of attempt 2 must equal the payload of attempt 1. Since
    the blocks below are rendered from the stored read model -- which the tag change cannot
    touch -- they are equal by construction rather than by discipline.
    """

    def __init__(self, engine: Engine, context: PublishContext) -> None:
        self._engine = engine
        self._context = context

    def published_digest(self, *, owner_id: str, report_id: str) -> Any:
        from server.app.delivery.service import PublishedDigest

        with session_scope(self._engine) as connection:
            body = read_model(connection, self._context, owner_id=owner_id, report_id=report_id)
        if body is None:
            return None
        return PublishedDigest(
            report_id=report_id,
            content_hash=str(body["content_hash"]),
            blocks=_digest_blocks(body),
        )


def _digest_blocks(body: Mapping[str, Any]) -> tuple[str, ...]:
    """Plain-text, item-sized pieces in reading order (``PublishedDigest.blocks``).

    Block 0 carries the period header and the emerging-directions section whole, which is what
    ``contracts/telegram/delivery.md`` §3.5 requires of part 0. No ``parse_mode`` markup: the
    Phase 5 scope is plain text only, and an escape table for the alternative is still
    unresolved (``CR-PC07-04``).
    """
    coverage = body["coverage"]
    header = [
        f"Kỳ {coverage['coverage_from']} → {coverage['coverage_to']}",
        f"Chất lượng: {body['quality']}",
    ]
    for direction in body["emerging_directions"]:
        if direction["evidence_state"] == "sufficient":
            members = ", ".join(direction["member_target_keys"])
            header.append(f"{EMERGING_DIRECTION_LABEL}: {members}")
        else:
            header.append(
                f"{EMERGING_DIRECTION_LABEL}: chưa đủ bằng chứng "
                f"({direction.get('insufficient_reason')})"
            )
    blocks = ["\n".join(header)]
    for item in body["items"]:
        label = "mới" if item["item_type"] == "new_discovery" else "đã báo cáo trước"
        blocks.append(f"[{label}] {item['target_key']}")
    return tuple(blocks)


# --------------------------------------------------------------------------------------
# Plumbing
# --------------------------------------------------------------------------------------


def _require_caller(operation: OperationId, caller_module: str, allowed: frozenset[str]) -> None:
    """Default deny at this module's port (card §5, ruling R5-01 row 2).

    ``FORBIDDEN_EDGE`` and not ``UNAUTHORIZED``: these two operations are ``transport:
    internal``, so a caller that is not on the list is an in-process call across an edge the
    registry does not have. ``FE-13`` (the analysis worker publishing) is the named instance.
    """
    if caller_module not in allowed:
        raise ReportError(
            ErrorCode.FORBIDDEN_EDGE,
            details_safe={
                "caller_module": caller_module,
                "callee_module": MODULE_ID,
                "forbidden_edge_ref": "FE-13" if operation is OperationId.REPORT_PUBLISH else None,
            },
        )


def _assert_writable(context: PublishContext, operation: OperationId) -> None:
    if context.storage_guard is not None:
        context.storage_guard.assert_writable(operation)


def _report_by_build_id(
    connection: Connection, owner_id: str, report_build_id: str
) -> Mapping[str, Any] | None:
    row = (
        connection.execute(
            text(
                "SELECT id, status, abort_reason, quality, coverage_from, coverage_to,"
                "       content_hash FROM report"
                " WHERE owner_id = :owner AND report_build_id = :build"
            ),
            {"owner": owner_id, "build": report_build_id},
        )
        .mappings()
        .first()
    )
    return None if row is None else dict(row)


def _report_id_of(context: PublishContext, snapshot: BuildSnapshot) -> str:
    with session_scope(context.engine) as connection:
        row = _report_by_build_id(connection, snapshot.owner_id, snapshot.report_build_id)
    if row is None:  # pragma: no cover - _replay already raised NOT_FOUND
        raise ReportError(
            ErrorCode.NOT_FOUND,
            details_safe={
                "operation_id": OperationId.REPORT_PUBLISH.value,
                "resource_kind": "report",
            },
        )
    return str(row["id"])


__all__ = [
    "REPORT_CONTEXT_KEY",
    "DeliveryIntentPort",
    "PublishContext",
    "PublishResult",
    "PublishedDigestPort",
    "RunOutcomePort",
    "StorageGuardPort",
    "publish_report",
    "read_model",
    "record_build",
    "verify_content_hash",
]
