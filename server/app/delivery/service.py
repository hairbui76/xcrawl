"""``delivery.*`` -- the six operations of ``MOD-delivery-service``.

``contracts/ports.yaml`` operation ids map one-to-one onto the functions here:

=================================  ==========================================
``delivery.create_intent``         :func:`create_intent`
``delivery.dispatch_next``         :func:`dispatch_next`
``delivery.record_receipt``        :func:`record_receipt`
``delivery.mark_unknown``          :func:`mark_unknown`
``delivery.get_status``            :func:`get_status`
``delivery.decide_unknown``        :func:`decide_unknown`
=================================  ==========================================

The three sentences this module exists to keep true
---------------------------------------------------
1. **The attempt row is committed before the network call** (``T-DL-01``, SRC-PLAN §8.3).
   The commit happens inside :func:`dispatch_next`'s ``engine.begin()`` block, and
   ``send_payload`` is called *after* that block closes -- so a crash in between leaves a
   durable attempt with no receipt, which is the evidence that lets the system say "this may
   have been sent" instead of sending again blind.
2. **A part in ``unknown`` never leaves on its own** (AMD-B03, ``never_retry`` row 1,
   ``forbidden_transitions`` row 1). Two independent mechanisms enforce it: the part is
   skipped by the part picker, and the intent is parked in ``held_for_review``, which
   :meth:`~server.app.delivery.outbox.DeliveryRepository.claim_intent` never claims. Only
   :func:`decide_unknown` moves either of them.
3. **Delivery writes nothing to ``report`` or ``run``** (``I05``, ``I09``, B01). There is no
   SQL in this package that names either table; the published payload arrives read-only
   through :class:`ReportPayloadPort`.

Transaction boundaries
----------------------
``TXN`` points, each a single ``engine.begin()`` in this file and named at its call site:

* ``create_intent`` -- ``outbox_intent`` + ``delivery`` + ``delivery_part`` rows, committed
  *with the source content* when the caller passes its own open connection (the outbox
  pattern of SRC-PLAN §5.1; a network call inside a SQLite transaction is forbidden).
* ``dispatch_next`` -- claim + attempt row + ``sending``, committed **before** the send.
* ``record_receipt`` / ``mark_unknown`` / ``decide_unknown`` -- one transaction each, after
  the network call has returned or failed to.

Ports, and why they are ports
-----------------------------
``contracts/modules.yaml`` is default-deny. Delivery may call ``telegram.send_payload`` and
nothing else outward, so the Telegram HTTP client, the Telegram link generation and the
published report payload all arrive as protocols implemented elsewhere:

* :class:`TelegramTransport` -- ``telegram.send_payload`` (``MOD-telegram-adapter``,
  ``TC-telegram-linking-auth``).
* :class:`TelegramLinkPort` -- the current link generation, also the adapter's. Delivery does
  not read the ``telegram_link`` table: that would be an edge the registry does not grant.
* :class:`ReportPayloadPort` -- the published digest (``MOD-report-service``,
  ``TC-report-coverage-publish-cas``), read-only by construction.

None of them has a default implementation. A missing port raises
:class:`DeliveryDependencyUnavailable` (``INTERNAL``): inventing a chat id, a generation or a
payload would be worse than answering "this deployment is not wired".
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Protocol

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import (
    DeliveryIntentKind,
    DeliveryPartState,
    DeliveryState,
    DeliveryUnknownDecision,
)
from sqlalchemy import Connection, Engine

from server.app.delivery import parts as parts_module
from server.app.delivery.outbox import (
    INTENT_TYPE_OF_KIND,
    DeliveryPartRow,
    DeliveryRepository,
    DeliveryRow,
    SenderLease,
    SenderLeaseRegistry,
    parse_rfc3339,
    part_states,
    utc_now,
)
from server.app.storage.guard import StorageGuard, StorageRefused

# --------------------------------------------------------------------------------------
# Numbers -- every one of them transcribed from contracts/retry-policy.yaml §budgets.
# They are PROVISIONAL there ("not yet calibrated against real data"), and SG-02 forbids
# raising any of them to make a test pass.
# --------------------------------------------------------------------------------------

#: ``telegram_send_attempts`` -- 4, per ``delivery_part``, NOT per aggregate.
TELEGRAM_SEND_ATTEMPTS = 4
#: ``telegram_send_backoff`` -- seconds, jitter ±20%.
TELEGRAM_SEND_BACKOFF: tuple[int, ...] = (5, 30, 300, 1800)
#: ``telegram_send_backoff`` jitter half-width, as a fraction.
TELEGRAM_SEND_BACKOFF_JITTER = 0.2
#: ``telegram_send_max_window`` -- 21600 s (6 h) from ``delivery.created_at``.
TELEGRAM_SEND_MAX_WINDOW_SECONDS = 21600

#: ``contracts/ports.yaml`` ``caller_modules`` for each delivery operation. Default deny:
#: a module absent from its row is refused, and the code is picked by ruling R5-01.
ALLOWED_CALLERS: dict[OperationId, frozenset[str]] = {
    OperationId.DELIVERY_CREATE_INTENT: frozenset({"MOD-report-service", "MOD-job-service"}),
    OperationId.DELIVERY_DISPATCH_NEXT: frozenset({"MOD-delivery-service"}),
    OperationId.DELIVERY_RECORD_RECEIPT: frozenset({"MOD-delivery-service"}),
    OperationId.DELIVERY_MARK_UNKNOWN: frozenset({"MOD-delivery-service"}),
    OperationId.DELIVERY_GET_STATUS: frozenset({"MOD-web-ui"}),
    OperationId.DELIVERY_DECIDE_UNKNOWN: frozenset({"MOD-web-ui"}),
}

#: ``modules[].runtime`` for the callers that can plausibly reach these operations,
#: including the two forbidden edges that end at this module -- ``FE-24``
#: (``MOD-scheduler``, NC-09) and ``FE-34`` (``MOD-backup-cli``, NC-10). Ruling R5-01 draws
#: the line by mechanism: an in-process caller is refused ``FORBIDDEN_EDGE``, an off-runtime
#: one ``CAPABILITY_DENIED``. Both those edges are ``RT-server``, and
#: ``acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`` seq 24 and seq 34
#: (``expected_error_code_edge_class``) pin ``FORBIDDEN_EDGE`` for both.
MODULE_RUNTIME: dict[str, str] = {
    "MOD-web-ui": "RT-browser",
    "MOD-report-service": "RT-server",
    "MOD-job-service": "RT-server",
    "MOD-delivery-service": "RT-server",
    "MOD-telegram-adapter": "RT-server",
    "MOD-scheduler": "RT-server",
    "MOD-backup-cli": "RT-server",
    "MOD-x-collector": "RT-personal-machine",
    "MOD-analysis-worker": "RT-personal-machine",
    "MOD-ai-adapter": "RT-personal-machine",
}

#: ``message_safe_template_vi`` of every code this module raises
#: (``contracts/errors.yaml`` §codes). Rendered verbatim: the envelope forbids interpolating
#: anything that is not a ``details_safe`` key.
MESSAGE_SAFE: dict[ErrorCode, str] = {
    ErrorCode.TELEGRAM_SEND_UNCERTAIN: (
        "Chưa xác định được tin đã gửi tới Telegram hay chưa. Bạn quyết định có gửi lại không."
    ),
    ErrorCode.TELEGRAM_PERMANENT_FAILURE: (
        "Không gửi được tới Telegram. Báo cáo vẫn còn đầy đủ trong ứng dụng."
    ),
    ErrorCode.RESTORE_UNVERIFIED: (
        "Vừa khôi phục dữ liệu. Việc gửi và giao việc đang tạm khóa cho tới khi đối soát xong."
    ),
    ErrorCode.STORAGE_WRITE_FAILED: (
        "Hệ thống tạm thời không ghi được dữ liệu. Đã dừng nhận việc mới."
    ),
    ErrorCode.STALE_LEASE: "Yêu cầu dùng phiên làm việc đã cũ và bị từ chối.",
    ErrorCode.VALIDATION_ERROR: "Dữ liệu gửi lên không hợp lệ.",
    ErrorCode.IDEMPOTENCY_CONFLICT: "Yêu cầu trùng khóa nhưng nội dung khác với lần đã ghi nhận.",
    ErrorCode.NOT_FOUND: "Không tìm thấy mục bạn yêu cầu.",
    ErrorCode.UNAUTHORIZED: "Không có quyền thực hiện thao tác này.",
    ErrorCode.CSRF_REJECTED: "Yêu cầu không hợp lệ. Hãy tải lại trang rồi thử lại.",
    ErrorCode.FORBIDDEN_EDGE: "Đường gọi này không được phép.",
    ErrorCode.CAPABILITY_DENIED: "Thao tác bị chặn ở mức nền tảng.",
    ErrorCode.CONFLICT: "Một tiến trình khác vừa ghi trước. Hệ thống đọc lại và thử lại.",
}

#: ``details_safe_keys`` of the same codes. A key outside the set is dropped before the
#: envelope leaves the process.
DETAILS_SAFE_KEYS: dict[ErrorCode, frozenset[str]] = {
    ErrorCode.TELEGRAM_SEND_UNCERTAIN: frozenset(
        {"delivery_id", "delivery_part_id", "part_index", "attempt_seq", "uncertainty_kind"}
    ),
    ErrorCode.TELEGRAM_PERMANENT_FAILURE: frozenset(
        {"delivery_id", "delivery_part_id", "failure_kind", "attempt_count"}
    ),
    ErrorCode.RESTORE_UNVERIFIED: frozenset(
        {"restore_id", "snapshot_id", "storage_health", "pending_outbox_count"}
    ),
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
    ErrorCode.STALE_LEASE: frozenset({"job_id", "lease_epoch_seen", "lease_epoch_current"}),
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.IDEMPOTENCY_CONFLICT: frozenset(
        {"idempotency_key", "payload_hash_seen", "payload_hash_stored"}
    ),
    ErrorCode.NOT_FOUND: frozenset({"operation_id", "resource_kind"}),
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
    ErrorCode.CSRF_REJECTED: frozenset({"operation_id"}),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"caller_module", "callee_module", "forbidden_edge_ref"}),
    ErrorCode.CAPABILITY_DENIED: frozenset(
        {"module_id", "denied_capability_kind", "forbidden_edge_ref"}
    ),
    ErrorCode.CONFLICT: frozenset(
        {
            "resource_kind",
            "expected_predecessor_id",
            "current_predecessor_id",
            "attempt_number",
            "retry_after_ms",
        }
    ),
}

HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.CAPABILITY_DENIED: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.STALE_LEASE: 409,
    ErrorCode.TELEGRAM_SEND_UNCERTAIN: 409,
    ErrorCode.TELEGRAM_PERMANENT_FAILURE: 409,
    ErrorCode.RESTORE_UNVERIFIED: 503,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}


class DeliveryError(Exception):
    """A contract error code plus the safe envelope fields it must be reported with.

    Never carries digest text, a chat id, a token or a stack trace: ``contracts/errors.yaml``
    forbids all of those in an envelope, and the only durable way to keep that promise is
    for the exception itself never to hold them.
    """

    def __init__(
        self,
        code: ErrorCode,
        *,
        details_safe: Mapping[str, Any] | None = None,
        message_safe: str | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        text = message_safe or MESSAGE_SAFE[code]
        super().__init__(f"{code.value}: {text}")
        self.code = code
        self.message_safe = text
        permitted = DETAILS_SAFE_KEYS[code]
        self.details_safe: dict[str, Any] | None = (
            None
            if details_safe is None
            else {k: v for k, v in details_safe.items() if k in permitted} or None
        )
        self.retry_after_ms = retry_after_ms

    @property
    def http_status(self) -> int:
        return HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """The seven-field envelope of ``contracts/errors.yaml`` ``error_envelope``."""
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe,
            "retry_after_ms": self.retry_after_ms,
        }


class DeliveryDependencyUnavailable(Exception):
    """A port this operation needs is not wired. Surfaces as ``INTERNAL``, never as a 4xx.

    Reporting an unwired port as a client error would blame the caller for a deployment gap
    and would let broken wiring pass a negative test.
    """


# --------------------------------------------------------------------------------------
# Ports
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Sent:
    """Telegram answered with a message id. The only outcome that may become ``sent``."""

    provider_message_id: str


@dataclass(frozen=True)
class RetryableFailure:
    """``T-DL-03``: certainly not received, or a retryable error with a clear meaning.

    :param retry_after_seconds: a real ``Retry-After`` from Telegram. When present it wins
        over ``telegram_send_backoff`` (``contracts/retry-policy.yaml`` §budgets and
        ``contracts/telegram/delivery.md`` §4.2, both in as many words).
    """

    reason: str
    retry_after_seconds: float | None = None


@dataclass(frozen=True)
class PermanentFailure:
    """``T-DL-07``: recipient revoked, bot blocked -- no amount of retrying changes it."""

    failure_kind: str


@dataclass(frozen=True)
class UncertainOutcome:
    """``T-DL-04``: timeout, connection lost, or a crash after the point of possible send.

    This is *not* a rollback (SRC-PLAN §5.1). It is the absence of knowledge, and the whole
    of AMD-B03 hangs on it not being filed under :class:`RetryableFailure`.
    """

    uncertainty_kind: str


SendOutcome = Sent | RetryableFailure | PermanentFailure | UncertainOutcome


class TelegramTransport(Protocol):
    """``telegram.send_payload`` as this module consumes it.

    Plain text only: no ``parse_mode``, no ``reply_markup``, no ``callback_data``. The three
    facts those would need are ``KC``/``BLOCKED_DEPENDENCY`` in
    ``contracts/telegram/delivery.md`` §3.4, and §9 row 12 forbids supplying them from
    memory.
    """

    def send_payload(
        self,
        *,
        delivery_part_id: str,
        chat_id: str,
        link_generation: int,
        text: str,
    ) -> SendOutcome: ...  # pragma: no cover - protocol declaration


@dataclass(frozen=True)
class LinkSnapshot:
    """What ``MOD-telegram-adapter`` tells delivery about the current link."""

    chat_id: str
    generation: int
    active: bool


class TelegramLinkPort(Protocol):
    """Read-only view of ``telegram_link`` owned by ``TC-telegram-linking-auth``."""

    def current_link(self, *, owner_id: str) -> LinkSnapshot | None: ...


@dataclass(frozen=True)
class PublishedDigest:
    """The frozen, already-published content a digest is built from.

    :param blocks: plain-text, item-sized pieces in reading order. ``blocks[0]`` carries the
        period header and the "emerging directions" section, which §3.5 requires to sit whole
        inside part 0.
    :param content_hash: ``report.content_hash`` as it stands at publish. Delivery only ever
        compares it; ``I05``/B01 forbid writing it.
    """

    report_id: str
    content_hash: str
    blocks: tuple[str, ...]


class ReportPayloadPort(Protocol):
    """Read-only view of the published report (``TC-report-coverage-publish-cas``).

    ``published_digest`` must return the bytes that were frozen at publish, never a
    re-render from the current tag set: fixture
    ``reporting/c-tag-changed-after-publish-before-send`` is exactly the case where those two
    differ, and its oracle is that the payload hash of attempt 1 equals that of attempt 2.
    """

    def published_digest(self, *, owner_id: str, report_id: str) -> PublishedDigest | None: ...


@dataclass
class DeliveryContext:
    """Everything an operation needs, injected. No module-level singletons."""

    engine: Engine
    storage: StorageGuard
    transport: TelegramTransport | None = None
    link_port: TelegramLinkPort | None = None
    report_port: ReportPayloadPort | None = None
    #: ``outbox_intent.restore_generation`` currently in force. Only intents carrying this
    #: value are eligible (``I15``; fixtures ``recovery/a`` and ``recovery/m``). It is
    #: supplied by whoever wires the app -- ``TC-backup-restore-drill`` raises it on restore --
    #: and deliberately has no clever default.
    restore_generation: int = 1
    leases: SenderLeaseRegistry = field(default_factory=SenderLeaseRegistry)
    repository: DeliveryRepository = field(default_factory=DeliveryRepository)

    def now(self) -> datetime:
        return utc_now()

    def require_transport(self) -> TelegramTransport:
        if self.transport is None:
            raise DeliveryDependencyUnavailable("telegram.send_payload transport is not wired")
        return self.transport

    def require_link_port(self) -> TelegramLinkPort:
        if self.link_port is None:
            raise DeliveryDependencyUnavailable("telegram link port is not wired")
        return self.link_port

    def require_report_port(self) -> ReportPayloadPort:
        if self.report_port is None:
            raise DeliveryDependencyUnavailable("report payload port is not wired")
        return self.report_port


# --------------------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class DispatchOutcome:
    """What one :func:`dispatch_next` turn did -- and, as often, deliberately did not do.

    :param outbound_calls: how many times ``telegram.send_payload`` was invoked in this
        turn. It is 0 or 1 by construction, and the ``0`` cases are the oracles: a part in
        ``unknown``, a cancelled link generation, an exhausted budget, a locked dispatcher.
    """

    reason: str
    delivery_id: str | None = None
    delivery_part_id: str | None = None
    part_index: int | None = None
    part_state: DeliveryPartState | None = None
    delivery_state: DeliveryState | None = None
    error_code: ErrorCode | None = None
    outbound_calls: int = 0


# --------------------------------------------------------------------------------------
# Guards shared by every operation
# --------------------------------------------------------------------------------------


def _assert_caller(operation: OperationId, caller_module: str) -> None:
    """Default deny (``contracts/modules.yaml``), with the code ruling R5-01 dictates."""
    if caller_module in ALLOWED_CALLERS[operation]:
        return
    if MODULE_RUNTIME.get(caller_module) == "RT-server":
        raise DeliveryError(
            ErrorCode.FORBIDDEN_EDGE,
            details_safe={
                "caller_module": caller_module,
                "callee_module": "MOD-delivery-service",
            },
        )
    raise DeliveryError(
        ErrorCode.CAPABILITY_DENIED,
        details_safe={"module_id": caller_module, "denied_capability_kind": "process"},
    )


def _assert_storage_allows(context: DeliveryContext, operation: OperationId) -> None:
    """``T-DL-09`` and ``sender_lease.storage_guard_vi``, checked before every dispatch.

    The check goes through :meth:`StorageGuard.assert_writable` rather than through the
    ``storage.get_health`` port: ``contracts/ports.yaml`` lists only ``MOD-health-service``
    and ``MOD-job-service`` as callers of that operation, so a literal call from here would
    be a forbidden edge even though ``contracts/state/delivery.yaml`` §sender_lease tells the
    dispatcher to read it. The guard gives the identical answer for
    ``delivery.dispatch_next`` -- ``RESTORE_UNVERIFIED`` while ``recovery_required``,
    ``STORAGE_WRITE_FAILED`` while ``write_blocked`` -- without crossing an edge the registry
    does not grant. See ``CR-TC-DELIVERY-07``.
    """
    try:
        context.storage.assert_writable(operation)
    except StorageRefused as refused:
        envelope = refused.envelope
        raise DeliveryError(
            ErrorCode(envelope["code"]),
            details_safe=envelope.get("details_safe") or {},
            retry_after_ms=envelope.get("retry_after_ms"),
        ) from refused


def _require_lease(context: DeliveryContext, lease: SenderLease, now: datetime) -> None:
    """A writer holding an expired or superseded lease writes nothing (``STALE_LEASE``)."""
    if not context.leases.is_current(lease, now=now):
        raise DeliveryError(
            ErrorCode.STALE_LEASE,
            details_safe={
                "lease_epoch_seen": lease.epoch,
                "lease_epoch_current": context.leases.current_epoch(lease.delivery_id),
            },
        )


def backoff_seconds(delivery_id: str, attempt_number: int) -> float:
    """``telegram_send_backoff`` for ``attempt_number`` (1-based), jitter included.

    The jitter is ±20% as the contract says, but derived from ``sha256(delivery_id:attempt)``
    rather than from a random source: the due time has to survive a process restart, because
    ``entities.yaml`` ``ENT-delivery`` has no ``next_attempt_at`` column to persist it in
    (``CR-TC-DELIVERY-04``) and it is therefore recomputed from ``updated_at`` on every read.
    A random jitter would give a different answer each time it was recomputed.
    """
    index = min(max(attempt_number, 1), len(TELEGRAM_SEND_BACKOFF)) - 1
    base = TELEGRAM_SEND_BACKOFF[index]
    digest = hashlib.sha256(f"{delivery_id}:{attempt_number}".encode()).digest()
    unit = int.from_bytes(digest[:8], "big") / float(1 << 64)  # [0, 1)
    factor = 1.0 + TELEGRAM_SEND_BACKOFF_JITTER * (2.0 * unit - 1.0)
    return base * factor


def next_attempt_at(delivery: DeliveryRow) -> datetime:
    """When a ``retry_wait`` delivery becomes eligible again (``T-DL-05``)."""
    return parse_rfc3339(delivery.updated_at) + timedelta(
        seconds=backoff_seconds(delivery.id, delivery.attempt_count)
    )


def window_deadline(delivery: DeliveryRow) -> datetime:
    """``telegram_send_max_window`` measured from ``delivery.created_at``."""
    return parse_rfc3339(delivery.created_at) + timedelta(seconds=TELEGRAM_SEND_MAX_WINDOW_SECONDS)


# --------------------------------------------------------------------------------------
# delivery.create_intent -- T-DL-00
# --------------------------------------------------------------------------------------


def create_intent(
    context: DeliveryContext,
    *,
    owner_id: str,
    kind: DeliveryIntentKind,
    caller_module: str,
    report_id: str | None = None,
    run_id: str | None = None,
    telegram_link_generation: int | None = None,
    connection: Connection | None = None,
) -> dict[str, Any]:
    """``delivery.create_intent`` -- commit the outbox intent with the source content.

    :param connection: the *caller's* open transaction. Passing it is the outbox pattern:
        the intent lands in the same commit as the published report, so a crash between
        publish and send loses neither (SRC-PLAN §5.1, ``T-DL-00``). Omitting it opens a
        transaction here, which is correct only for a caller that has nothing else to commit.
    :param telegram_link_generation: the generation captured **at intent creation**. A later
        relink cancels this intent (``T-DL-08``); it is never re-pointed at the new chat.

    ``TXN-delivery-create-intent`` commit point: the ``engine.begin()`` below, or the
    caller's commit when ``connection`` is given.

    Idempotent on ``logical_delivery_key`` = (report_id | run_alert_id) + channel: a second
    call returns the delivery already recorded instead of creating a second one.
    """
    _assert_caller(OperationId.DELIVERY_CREATE_INTENT, caller_module)
    if kind is DeliveryIntentKind.REPORT_DIGEST and report_id is None:
        raise DeliveryError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.DELIVERY_CREATE_INTENT.value,
                "field_path": "report_id",
                "violation_kind": "required",
            },
        )
    if kind is DeliveryIntentKind.RUN_ALERT and run_id is None:
        raise DeliveryError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.DELIVERY_CREATE_INTENT.value,
                "field_path": "run_id",
                "violation_kind": "required",
            },
        )

    if connection is not None:
        return _create_intent(
            context, connection, owner_id, kind, report_id, run_id, telegram_link_generation
        )
    with context.engine.begin() as own_connection:
        return _create_intent(
            context, own_connection, owner_id, kind, report_id, run_id, telegram_link_generation
        )


def _create_intent(
    context: DeliveryContext,
    connection: Connection,
    owner_id: str,
    kind: DeliveryIntentKind,
    report_id: str | None,
    run_id: str | None,
    telegram_link_generation: int | None,
) -> dict[str, Any]:
    repository = context.repository
    now = context.now()
    subject_ref: dict[str, Any] = (
        {"report_id": report_id} if report_id is not None else {"run_id": run_id}
    )
    intent_type = INTENT_TYPE_OF_KIND[kind]

    existing_intent = repository.find_intent_for_subject(
        connection,
        owner_id=owner_id,
        intent_type=intent_type,
        subject_ref=_canonical_subject(subject_ref),
    )
    if existing_intent is not None:
        delivery = (
            None
            if report_id is None
            else repository.find_delivery_for_report(
                connection, owner_id=owner_id, report_id=report_id
            )
        )
        return {
            "intent_id": existing_intent.id,
            "delivery_id": None if delivery is None else delivery.id,
            "state": None if delivery is None else delivery.state.value,
            "created": False,
        }

    intent = repository.insert_intent(
        connection,
        owner_id=owner_id,
        kind=kind,
        subject_ref=subject_ref,
        restore_generation=context.restore_generation,
        now=now,
    )

    if kind is DeliveryIntentKind.RUN_ALERT:
        # No ``delivery`` row: ``entities.yaml`` ``ENT-delivery.report_id`` is NOT NULL with a
        # foreign key to ``report``, so an alert -- which has a run and no report -- cannot be
        # represented as one. The intent alone still carries REQ-AC04: the partial UNIQUE
        # ``ux_outbox_alert_per_run`` makes a second alert for the same run impossible.
        # ``CR-TC-DELIVERY-06``.
        return {
            "intent_id": intent.id,
            "delivery_id": None,
            "state": None,
            "created": True,
        }

    assert report_id is not None  # narrowed by the VALIDATION_ERROR above
    if telegram_link_generation is None:
        raise DeliveryError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.DELIVERY_CREATE_INTENT.value,
                "field_path": "telegram_link_generation",
                "violation_kind": "required",
            },
        )
    delivery = context.repository.insert_delivery(
        connection,
        owner_id=owner_id,
        report_id=report_id,
        channel="telegram",
        telegram_link_generation=telegram_link_generation,
        now=now,
    )
    return {
        "intent_id": intent.id,
        "delivery_id": delivery.id,
        "state": delivery.state.value,
        "created": True,
    }


def _canonical_subject(subject_ref: Mapping[str, Any]) -> str:
    """The exact string ``outbox_intent.subject_ref`` stores, so lookups match byte for byte."""
    return json.dumps(dict(subject_ref), sort_keys=True)


# --------------------------------------------------------------------------------------
# delivery.dispatch_next -- T-DL-01 .. T-DL-09
# --------------------------------------------------------------------------------------


def dispatch_next(
    context: DeliveryContext,
    *,
    owner_id: str,
    caller_module: str = "MOD-delivery-service",
    holder: str = "delivery-dispatcher",
) -> DispatchOutcome:
    """``delivery.dispatch_next`` -- claim one intent, send at most one part.

    The order of the four refusals below is the contract's, not a convenience:

    1. **Edge** (``FE-24``, ``FE-34``): the scheduler and the backup CLI are not callers of
       this operation in *any* storage state.
    2. **Storage** (``T-DL-09``, ``I15``): while ``recovery_required``, the dispatcher does
       not run at all -- ``RESTORE_UNVERIFIED``, zero outbound calls, and no timer unlocks it.
    3. **Link generation** (``T-DL-08``): a relinked or unlinked recipient cancels the
       delivery instead of receiving it, and the payload is never re-pointed at the new chat.
    4. **Part state**: ``unknown`` parts are skipped, ``sent`` parts return their receipt.

    Only after all four, and only after the attempt row has been COMMITTED, is
    ``telegram.send_payload`` called -- once.
    """
    _assert_caller(OperationId.DELIVERY_DISPATCH_NEXT, caller_module)
    _assert_storage_allows(context, OperationId.DELIVERY_DISPATCH_NEXT)

    now = context.now()
    prepared = _prepare_dispatch(context, owner_id=owner_id, holder=holder, now=now)
    if prepared.outcome is not None:
        return prepared.outcome

    # -- the transaction is closed; everything below is outside SQLite ------------------
    assert prepared.lease is not None and prepared.part is not None
    assert prepared.link is not None and prepared.text is not None
    transport = context.require_transport()
    outcome = transport.send_payload(
        delivery_part_id=prepared.part.id,
        chat_id=prepared.link.chat_id,
        link_generation=prepared.link.generation,
        text=prepared.text,
    )

    after = context.now()
    _require_lease(context, prepared.lease, after)
    if isinstance(outcome, Sent):
        record_receipt(
            context,
            owner_id=owner_id,
            delivery_part_id=prepared.part.id,
            attempt_number=prepared.attempt_number,
            provider_message_id=outcome.provider_message_id,
            caller_module="MOD-delivery-service",
        )
        state = _reload_states(context, prepared.part.id)
        return DispatchOutcome(
            reason="sent",
            delivery_id=prepared.part.delivery_id,
            delivery_part_id=prepared.part.id,
            part_index=prepared.part.part_index,
            part_state=state[0],
            delivery_state=state[1],
            outbound_calls=1,
        )
    if isinstance(outcome, UncertainOutcome):
        mark_unknown(
            context,
            owner_id=owner_id,
            delivery_part_id=prepared.part.id,
            attempt_number=prepared.attempt_number,
            uncertainty_kind=outcome.uncertainty_kind,
            caller_module="MOD-delivery-service",
        )
        state = _reload_states(context, prepared.part.id)
        return DispatchOutcome(
            reason="unknown",
            delivery_id=prepared.part.delivery_id,
            delivery_part_id=prepared.part.id,
            part_index=prepared.part.part_index,
            part_state=state[0],
            delivery_state=state[1],
            error_code=ErrorCode.TELEGRAM_SEND_UNCERTAIN,
            outbound_calls=1,
        )
    if isinstance(outcome, PermanentFailure):
        _fail_part(
            context,
            part_id=prepared.part.id,
            attempt_id=prepared.attempt_id,
            intent_id=prepared.lease.intent_id,
            error_code=ErrorCode.TELEGRAM_PERMANENT_FAILURE,
            now=after,
        )
        state = _reload_states(context, prepared.part.id)
        return DispatchOutcome(
            reason="failed",
            delivery_id=prepared.part.delivery_id,
            delivery_part_id=prepared.part.id,
            part_index=prepared.part.part_index,
            part_state=state[0],
            delivery_state=state[1],
            error_code=ErrorCode.TELEGRAM_PERMANENT_FAILURE,
            outbound_calls=1,
        )

    # RetryableFailure -- T-DL-03. Budget and window are checked before the *next* attempt
    # is prepared, not here, so the row state after a retryable error is always `retry_wait`.
    _retry_wait(
        context,
        part=prepared.part,
        attempt_id=prepared.attempt_id,
        intent_id=prepared.lease.intent_id,
        now=after,
    )
    state = _reload_states(context, prepared.part.id)
    return DispatchOutcome(
        reason="retry_wait",
        delivery_id=prepared.part.delivery_id,
        delivery_part_id=prepared.part.id,
        part_index=prepared.part.part_index,
        part_state=state[0],
        delivery_state=state[1],
        outbound_calls=1,
    )


@dataclass
class _Prepared:
    """Everything the network call needs, or the outcome that says it must not happen."""

    outcome: DispatchOutcome | None = None
    lease: SenderLease | None = None
    part: DeliveryPartRow | None = None
    link: LinkSnapshot | None = None
    text: str | None = None
    attempt_number: int = 0
    attempt_id: str = ""


def _prepare_dispatch(
    context: DeliveryContext, *, owner_id: str, holder: str, now: datetime
) -> _Prepared:
    """``TXN-delivery-dispatch`` -- one transaction, committed before any network call.

    Everything that must be durable before the send is written here: the intent claim, the
    part rows on first dispatch, the attempt row, and ``delivery_part.state = 'sending'``.
    """
    repository = context.repository
    link_port = context.require_link_port()
    report_port = context.require_report_port()

    with context.engine.begin() as connection:
        intent = repository.claim_intent(
            connection, owner_id=owner_id, restore_generation=context.restore_generation
        )
        if intent is None:
            return _Prepared(outcome=DispatchOutcome(reason="no_eligible_intent"))

        report_id = intent.subject_ref.get("report_id")
        if report_id is None:
            # A run alert has no ``delivery`` row (see ``_create_intent``); park it rather
            # than claiming it again on the next turn.
            repository.set_intent_dispatch_state(
                connection, intent_id=intent.id, dispatch_state="held_for_review"
            )
            return _Prepared(outcome=DispatchOutcome(reason="alert_intent_not_dispatchable"))

        delivery = repository.find_delivery_for_report(
            connection, owner_id=owner_id, report_id=str(report_id)
        )
        if delivery is None:
            repository.set_intent_dispatch_state(
                connection, intent_id=intent.id, dispatch_state="held_for_review"
            )
            return _Prepared(outcome=DispatchOutcome(reason="delivery_row_missing"))

        lease = context.leases.issue(
            delivery_id=delivery.id, intent_id=intent.id, holder=holder, now=now
        )

        if delivery.state is DeliveryState.CANCELLED:
            repository.set_intent_dispatch_state(
                connection, intent_id=intent.id, dispatch_state="done"
            )
            return _Prepared(
                outcome=DispatchOutcome(
                    reason="cancelled",
                    delivery_id=delivery.id,
                    delivery_state=DeliveryState.CANCELLED,
                )
            )

        # -- T-DL-08: the recipient the payload was built for must still be the current one.
        link = link_port.current_link(owner_id=owner_id)
        if link is None or not link.active or link.generation != delivery.telegram_link_generation:
            repository.set_delivery_state(
                connection, delivery_id=delivery.id, state=DeliveryState.CANCELLED, now=now
            )
            repository.set_intent_dispatch_state(
                connection, intent_id=intent.id, dispatch_state="done"
            )
            return _Prepared(
                outcome=DispatchOutcome(
                    reason="cancelled_link_generation",
                    delivery_id=delivery.id,
                    delivery_state=DeliveryState.CANCELLED,
                )
            )

        digest = report_port.published_digest(owner_id=owner_id, report_id=str(report_id))
        if digest is None:
            repository.set_intent_dispatch_state(
                connection, intent_id=intent.id, dispatch_state="held_for_review"
            )
            return _Prepared(outcome=DispatchOutcome(reason="published_report_missing"))

        rows = repository.list_parts(connection, delivery_id=delivery.id)
        if not rows:
            rows = _materialise_parts(
                context, connection, delivery=delivery, digest=digest, now=now
            )

        target = _pick_part(rows)
        if target is None:
            return _Prepared(
                outcome=_park_intent(context, connection, delivery, rows, intent.id, now)
            )

        # -- budget and window, both from contracts/retry-policy.yaml, both before the send.
        if delivery.state is DeliveryState.RETRY_WAIT and now < next_attempt_at(delivery):
            repository.set_intent_dispatch_state(
                connection, intent_id=intent.id, dispatch_state="ready"
            )
            return _Prepared(
                outcome=DispatchOutcome(
                    reason="retry_not_due",
                    delivery_id=delivery.id,
                    delivery_part_id=target.id,
                    part_index=target.part_index,
                    part_state=target.state,
                    delivery_state=delivery.state,
                )
            )
        attempt_number = repository.next_attempt_number(connection, part_id=target.id)
        if attempt_number > TELEGRAM_SEND_ATTEMPTS or now >= window_deadline(delivery):
            repository.set_part_state(
                connection,
                part_id=target.id,
                state=DeliveryPartState.FAILED,
                provider_message_id=None,
                now=now,
            )
            rows = repository.list_parts(connection, delivery_id=delivery.id)
            aggregate = parts_module.aggregate_state(part_states(rows))
            repository.set_delivery_state(
                connection, delivery_id=delivery.id, state=aggregate, now=now
            )
            repository.set_intent_dispatch_state(
                connection, intent_id=intent.id, dispatch_state="done"
            )
            return _Prepared(
                outcome=DispatchOutcome(
                    reason="budget_exhausted",
                    delivery_id=delivery.id,
                    delivery_part_id=target.id,
                    part_index=target.part_index,
                    part_state=DeliveryPartState.FAILED,
                    delivery_state=aggregate,
                    error_code=ErrorCode.TELEGRAM_PERMANENT_FAILURE,
                )
            )

        # -- T-DL-01: ATTEMPT ROW COMMITTED BEFORE THE NETWORK CALL.
        attempt = repository.insert_attempt(
            connection,
            owner_id=owner_id,
            delivery_id=delivery.id,
            part_id=target.id,
            attempt_number=attempt_number,
            now=now,
        )
        repository.set_part_state(
            connection,
            part_id=target.id,
            state=DeliveryPartState.SENDING,
            provider_message_id=None,
            now=now,
        )
        repository.set_delivery_state(
            connection, delivery_id=delivery.id, state=DeliveryState.SENDING, now=now
        )
        repository.bump_attempt_count(connection, delivery_id=delivery.id, now=now)
        text_to_send = _text_for_part(target, digest)

    return _Prepared(
        lease=lease,
        part=target,
        link=link,
        text=text_to_send,
        attempt_number=attempt_number,
        attempt_id=attempt.id,
    )


def _materialise_parts(
    context: DeliveryContext,
    connection: Connection,
    *,
    delivery: DeliveryRow,
    digest: PublishedDigest,
    now: datetime,
) -> list[DeliveryPartRow]:
    """Split the published digest and persist one ``delivery_part`` per message (``DP-01``)."""
    try:
        split = parts_module.split_plain_text(digest.blocks)
    except parts_module.PartTooLarge as too_large:
        raise DeliveryError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.DELIVERY_DISPATCH_NEXT.value,
                "field_path": f"blocks[{too_large.index}]",
                "violation_kind": "too_long",
                "limit_name": "telegram_message_length",
                "limit_value": parts_module.MAX_MESSAGE_LENGTH,
            },
        ) from too_large
    for piece in split:
        context.repository.insert_part(
            connection,
            owner_id=delivery.owner_id,
            delivery_id=delivery.id,
            part_index=piece.part_index,
            payload_hash=piece.payload_hash,
            now=now,
        )
    return context.repository.list_parts(connection, delivery_id=delivery.id)


def _text_for_part(part: DeliveryPartRow, digest: PublishedDigest) -> str:
    """Re-render the part text and refuse to send it if the hash moved.

    The re-render reads the *published* content through the port, so an unchanged report
    yields byte-identical text -- fixture ``reporting/c`` retries after a tag change and its
    oracle is that the payload hash of the two attempts is equal. If it is not equal, the
    payload is no longer the one that was published, and sending it would break ``I05``.
    """
    split = parts_module.split_plain_text(digest.blocks)
    for piece in split:
        if piece.part_index == part.part_index:
            if piece.payload_hash != part.payload_hash:
                raise DeliveryError(
                    ErrorCode.CONFLICT,
                    details_safe={"resource_kind": "delivery_part"},
                )
            return piece.text
    raise DeliveryError(
        ErrorCode.CONFLICT,
        details_safe={"resource_kind": "delivery_part"},
    )


def _pick_part(rows: Sequence[DeliveryPartRow]) -> DeliveryPartRow | None:
    """The next part that may be sent: the lowest-index ``pending`` one, or ``None``.

    ``unknown`` is not in the list, and that omission is ``DP-02``: a part in ``unknown`` is
    never picked up again *because the aggregate is not yet* ``sent``. ``sending`` is not in
    the list either -- a part left ``sending`` by a crash is exactly the "may already have
    been sent" case and belongs to ``mark_unknown``, not to a second send.
    """
    for row in rows:
        if row.state is DeliveryPartState.PENDING:
            return row
    return None


def _park_intent(
    context: DeliveryContext,
    connection: Connection,
    delivery: DeliveryRow,
    rows: Sequence[DeliveryPartRow],
    intent_id: str,
    now: datetime,
) -> DispatchOutcome:
    """No part may be sent. Record the aggregate and park the intent accordingly.

    ``held_for_review`` for an aggregate carrying an ``unknown`` part is the second lock on
    AMD-B03: ``claim_intent`` only ever claims ``ready``, so no later sweep of the outbox can
    reach that delivery until :func:`decide_unknown` puts it back.
    """
    aggregate = parts_module.aggregate_state(part_states(rows))
    context.repository.set_delivery_state(
        connection, delivery_id=delivery.id, state=aggregate, now=now
    )
    dispatch_state = "held_for_review" if aggregate is DeliveryState.UNKNOWN else "done"
    context.repository.set_intent_dispatch_state(
        connection, intent_id=intent_id, dispatch_state=dispatch_state
    )
    reason = {
        DeliveryState.UNKNOWN: "held_unknown_awaiting_operator",
        DeliveryState.SENT: "already_sent",
        DeliveryState.FAILED: "failed",
    }.get(aggregate, "nothing_dispatchable")
    return DispatchOutcome(
        reason=reason,
        delivery_id=delivery.id,
        delivery_state=aggregate,
    )


def _reload_states(
    context: DeliveryContext, part_id: str
) -> tuple[DeliveryPartState | None, DeliveryState | None]:
    with context.engine.begin() as connection:
        part = context.repository.get_part(connection, part_id=part_id)
        if part is None:
            return None, None
        delivery = context.repository.get_delivery(connection, delivery_id=part.delivery_id)
        return part.state, None if delivery is None else delivery.state


def _fail_part(
    context: DeliveryContext,
    *,
    part_id: str,
    attempt_id: str,
    intent_id: str,
    error_code: ErrorCode,
    now: datetime,
) -> None:
    """``T-DL-07`` -- part ``failed``, and not one row of ``report`` or ``run`` touched."""
    with context.engine.begin() as connection:
        context.repository.set_attempt_outcome(
            connection,
            attempt_id=attempt_id,
            outcome="permanent_error",
            error_code=error_code.value,
        )
        context.repository.set_part_state(
            connection,
            part_id=part_id,
            state=DeliveryPartState.FAILED,
            provider_message_id=None,
            now=now,
        )
        part = context.repository.get_part(connection, part_id=part_id)
        assert part is not None
        rows = context.repository.list_parts(connection, delivery_id=part.delivery_id)
        aggregate = parts_module.aggregate_state(part_states(rows))
        context.repository.set_delivery_state(
            connection, delivery_id=part.delivery_id, state=aggregate, now=now
        )
        context.repository.set_intent_dispatch_state(
            connection, intent_id=intent_id, dispatch_state="done"
        )


def _retry_wait(
    context: DeliveryContext,
    *,
    part: DeliveryPartRow,
    attempt_id: str,
    intent_id: str,
    now: datetime,
) -> None:
    """``T-DL-03`` -- back to ``pending`` behind a backoff, same logical delivery key."""
    with context.engine.begin() as connection:
        context.repository.set_attempt_outcome(
            connection, attempt_id=attempt_id, outcome="retryable_error", error_code=None
        )
        context.repository.set_part_state(
            connection,
            part_id=part.id,
            state=DeliveryPartState.PENDING,
            provider_message_id=None,
            now=now,
        )
        context.repository.set_delivery_state(
            connection, delivery_id=part.delivery_id, state=DeliveryState.RETRY_WAIT, now=now
        )
        context.repository.set_intent_dispatch_state(
            connection, intent_id=intent_id, dispatch_state="ready"
        )


# --------------------------------------------------------------------------------------
# delivery.record_receipt -- T-DL-02
# --------------------------------------------------------------------------------------


def record_receipt(
    context: DeliveryContext,
    *,
    owner_id: str,
    delivery_part_id: str,
    attempt_number: int,
    provider_message_id: str,
    caller_module: str = "MOD-delivery-service",
) -> dict[str, Any]:
    """``delivery.record_receipt`` -- persist the receipt; idempotent on the part.

    A second call returns the stored receipt and writes nothing. That is what makes
    ``T-DL-02``'s promise ("a later retry only returns the receipt") checkable: the oracle is
    an outbound call count of 0, and the count can only stay 0 if this is a read.
    """
    _assert_caller(OperationId.DELIVERY_RECORD_RECEIPT, caller_module)
    _assert_storage_allows(context, OperationId.DELIVERY_RECORD_RECEIPT)
    now = context.now()
    with context.engine.begin() as connection:
        repository = context.repository
        part = repository.get_part(connection, part_id=delivery_part_id)
        if part is None or part.owner_id != owner_id:
            raise DeliveryError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.DELIVERY_RECORD_RECEIPT.value,
                    "resource_kind": "delivery_part",
                },
            )
        existing = repository.find_receipt_for_part(connection, part_id=part.id)
        if existing is not None:
            return {
                "delivery_part_id": part.id,
                "state": DeliveryPartState.SENT.value,
                "provider_message_id": existing["provider_message_id"],
                "receipt_id": existing["id"],
                "created": False,
            }
        attempt = repository.get_attempt(connection, part_id=part.id, attempt_number=attempt_number)
        if attempt is None:
            # No attempt row means no COMMIT happened before the network call, which is the
            # one ordering SRC-PLAN §8.3 does not allow to be skipped.
            raise DeliveryError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": OperationId.DELIVERY_RECORD_RECEIPT.value,
                    "field_path": "attempt_number",
                    "violation_kind": "attempt_row_missing_before_send",
                },
            )
        receipt_id = repository.insert_receipt(
            connection,
            owner_id=owner_id,
            attempt_id=attempt.id,
            provider_message_id=provider_message_id,
            payload_hash=part.payload_hash,
            now=now,
        )
        repository.set_attempt_outcome(
            connection, attempt_id=attempt.id, outcome="sent", error_code=None
        )
        repository.set_part_state(
            connection,
            part_id=part.id,
            state=DeliveryPartState.SENT,
            provider_message_id=provider_message_id,
            now=now,
        )
        rows = repository.list_parts(connection, delivery_id=part.delivery_id)
        aggregate = parts_module.aggregate_state(part_states(rows))
        repository.set_delivery_state(
            connection, delivery_id=part.delivery_id, state=aggregate, now=now
        )
        _settle_intent(context, connection, delivery_id=part.delivery_id, owner_id=owner_id)
        return {
            "delivery_part_id": part.id,
            "state": DeliveryPartState.SENT.value,
            "provider_message_id": provider_message_id,
            "receipt_id": receipt_id,
            "delivery_state": aggregate.value,
            "created": True,
        }


# --------------------------------------------------------------------------------------
# delivery.mark_unknown -- T-DL-04
# --------------------------------------------------------------------------------------


def mark_unknown(
    context: DeliveryContext,
    *,
    owner_id: str,
    delivery_part_id: str,
    attempt_number: int,
    uncertainty_kind: str,
    caller_module: str = "MOD-delivery-service",
) -> dict[str, Any]:
    """``delivery.mark_unknown`` -- the part may or may not have arrived, and we stop here.

    Writes ``provider_message_id = NULL`` (fixture ``telegram/b`` forbids inventing one),
    leaves ``report`` and ``run`` untouched (``I09``), and parks the intent in
    ``held_for_review`` so that no outbox sweep can pick the delivery up again. Idempotent on
    ``delivery_part_id + attempt_seq``.
    """
    _assert_caller(OperationId.DELIVERY_MARK_UNKNOWN, caller_module)
    now = context.now()
    with context.engine.begin() as connection:
        repository = context.repository
        part = repository.get_part(connection, part_id=delivery_part_id)
        if part is None or part.owner_id != owner_id:
            raise DeliveryError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.DELIVERY_MARK_UNKNOWN.value,
                    "resource_kind": "delivery_part",
                },
            )
        attempt = repository.get_attempt(connection, part_id=part.id, attempt_number=attempt_number)
        if attempt is None:
            raise DeliveryError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": OperationId.DELIVERY_MARK_UNKNOWN.value,
                    "field_path": "attempt_number",
                    "violation_kind": "attempt_row_missing_before_send",
                },
            )
        if part.state is not DeliveryPartState.UNKNOWN:
            repository.set_attempt_outcome(
                connection,
                attempt_id=attempt.id,
                outcome="unknown",
                error_code=ErrorCode.TELEGRAM_SEND_UNCERTAIN.value,
            )
            repository.set_part_state(
                connection,
                part_id=part.id,
                state=DeliveryPartState.UNKNOWN,
                provider_message_id=None,
                now=now,
            )
        rows = repository.list_parts(connection, delivery_id=part.delivery_id)
        aggregate = parts_module.aggregate_state(part_states(rows))
        repository.set_delivery_state(
            connection, delivery_id=part.delivery_id, state=aggregate, now=now
        )
        _settle_intent(context, connection, delivery_id=part.delivery_id, owner_id=owner_id)
        return {
            "delivery_part_id": part.id,
            "state": DeliveryPartState.UNKNOWN.value,
            "provider_message_id": None,
            "delivery_state": aggregate.value,
            "uncertainty_kind": uncertainty_kind,
        }


def _settle_intent(
    context: DeliveryContext, connection: Connection, *, delivery_id: str, owner_id: str
) -> str:
    """Decide what the claimed intent should be after one part reached a resting state.

    Three answers, and the middle one is AMD-B03's second lock:

    * a part is still ``pending`` -> ``ready``. A part nobody has attempted yet is still
      sendable; ``DP-02`` forbids resending the *unknown* part, not the untouched ones.
    * otherwise a part is ``unknown`` -> ``held_for_review``, which
      :meth:`~server.app.delivery.outbox.DeliveryRepository.claim_intent` never claims. Only
      :func:`decide_unknown` puts it back.
    * otherwise -> ``done``.
    """
    from sqlalchemy import text as sql_text

    delivery = context.repository.get_delivery(connection, delivery_id=delivery_id)
    if delivery is None:
        return "done"
    rows = context.repository.list_parts(connection, delivery_id=delivery_id)
    if any(row.state is DeliveryPartState.PENDING for row in rows):
        dispatch_state = "ready"
    elif any(row.state is DeliveryPartState.UNKNOWN for row in rows):
        dispatch_state = "held_for_review"
    else:
        dispatch_state = "done"
    connection.execute(
        sql_text(
            "UPDATE outbox_intent SET dispatch_state = :s "
            "WHERE owner_id = :o AND intent_type = 'telegram_digest' "
            "AND subject_ref = :ref AND dispatch_state <> 'done'"
        ),
        {
            "s": dispatch_state,
            "o": owner_id,
            "ref": _canonical_subject({"report_id": delivery.report_id}),
        },
    )
    return dispatch_state


# --------------------------------------------------------------------------------------
# delivery.get_status -- I13
# --------------------------------------------------------------------------------------


def get_status(
    context: DeliveryContext,
    *,
    owner_id: str,
    delivery_id: str,
    caller_module: str = "MOD-web-ui",
) -> dict[str, Any]:
    """``delivery.get_status`` -- aggregate plus every part, with ``unknown`` on its own.

    The four situations ``I13`` requires to stay distinguishable come back as four different
    ``state`` values -- ``sent``, ``unknown``, ``failed``, ``cancelled`` -- and never as a
    single "not sent". ``attempt_count`` and timestamps ride along so the UI can explain what
    it is showing.
    """
    _assert_caller(OperationId.DELIVERY_GET_STATUS, caller_module)
    with context.engine.begin() as connection:
        delivery = context.repository.get_delivery(connection, delivery_id=delivery_id)
        if delivery is None or delivery.owner_id != owner_id:
            raise DeliveryError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.DELIVERY_GET_STATUS.value,
                    "resource_kind": "delivery",
                },
            )
        rows = context.repository.list_parts(connection, delivery_id=delivery.id)
        derived = parts_module.aggregate_state(
            part_states(rows),
            cancelled=delivery.state is DeliveryState.CANCELLED,
            retry_wait=delivery.state is DeliveryState.RETRY_WAIT,
        )
        return {
            "delivery_id": delivery.id,
            "report_id": delivery.report_id,
            "channel": delivery.channel,
            "state": derived.value,
            "status_label": parts_module.STATUS_LABELS[derived],
            "attempt_count": delivery.attempt_count,
            "telegram_link_generation": delivery.telegram_link_generation,
            "created_at": delivery.created_at,
            "updated_at": delivery.updated_at,
            "parts": [
                {
                    "delivery_part_id": row.id,
                    "part_index": row.part_index,
                    "state": row.state.value,
                    "payload_hash": row.payload_hash,
                    "provider_message_id": row.provider_message_id,
                    "updated_at": row.updated_at,
                }
                for row in rows
            ],
        }


# --------------------------------------------------------------------------------------
# delivery.decide_unknown -- T-DL-06
# --------------------------------------------------------------------------------------

#: Decision -> the part state it produces. ``abandon`` is the odd one:
#: ``contracts/telegram/delivery.md`` §5.2 and ``T-DL-06`` both say the part becomes
#: ``cancelled``, but ``delivery_part_state`` has no such member (``CR-TC-DELIVERY-02``). The
#: part therefore lands in ``failed`` -- "this part was not delivered" -- and the *delivery*
#: carries ``cancelled``, which is a real member of ``delivery_state`` and the value fixture
#: ``telegram/d`` reads.
_DECISION_PART_STATE: dict[DeliveryUnknownDecision, DeliveryPartState] = {
    DeliveryUnknownDecision.RESEND_ACCEPTING_DUPLICATE_RISK: DeliveryPartState.PENDING,
    DeliveryUnknownDecision.MARK_NOT_DELIVERED: DeliveryPartState.FAILED,
    DeliveryUnknownDecision.ABANDON: DeliveryPartState.FAILED,
}


def decide_unknown(
    context: DeliveryContext,
    *,
    owner_id: str,
    delivery_part_id: str,
    decision: DeliveryUnknownDecision,
    decision_request_id: str,
    duplicate_risk_accepted: bool = False,
    caller_module: str = "MOD-web-ui",
) -> dict[str, Any]:
    """``delivery.decide_unknown`` -- the **only** exit from ``unknown``.

    The system never chooses, and no timeout chooses for it (``T-DL-06``, §5.2). A resend
    requires ``duplicate_risk_accepted``: ``contracts/telegram/delivery.md`` §5.1 is explicit
    that a duplicate message after this decision is an accepted outcome and not a defect, and
    that is only true if the acceptance was actually expressed.

    Replay: ``contracts/ports.yaml`` keys idempotency on
    ``delivery_part_id + decision_request_id``, but ``entities.yaml`` declares no entity to
    store a decision in (``CR-TC-DELIVERY-03``). Idempotency is therefore derived from the
    state machine: a part that has already left ``unknown`` answers with its current state
    when the replayed decision matches the state it produced, and ``IDEMPOTENCY_CONFLICT``
    when it does not. What is lost with the missing entity is the durable *evidence* that the
    operator accepted the risk, which the handoff records rather than papering over.
    """
    _assert_caller(OperationId.DELIVERY_DECIDE_UNKNOWN, caller_module)
    _assert_storage_allows(context, OperationId.DELIVERY_DECIDE_UNKNOWN)
    if (
        decision is DeliveryUnknownDecision.RESEND_ACCEPTING_DUPLICATE_RISK
        and not duplicate_risk_accepted
    ):
        raise DeliveryError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.DELIVERY_DECIDE_UNKNOWN.value,
                "field_path": "duplicate_risk_accepted",
                "violation_kind": "confirmation_required",
            },
        )

    now = context.now()
    with context.engine.begin() as connection:
        repository = context.repository
        part = repository.get_part(connection, part_id=delivery_part_id)
        if part is None or part.owner_id != owner_id:
            raise DeliveryError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.DELIVERY_DECIDE_UNKNOWN.value,
                    "resource_kind": "delivery_part",
                },
            )
        target_state = _DECISION_PART_STATE[decision]
        if part.state is not DeliveryPartState.UNKNOWN:
            if part.state is target_state:
                delivery = repository.get_delivery(connection, delivery_id=part.delivery_id)
                return {
                    "delivery_part_id": part.id,
                    "state": part.state.value,
                    "delivery_state": None if delivery is None else delivery.state.value,
                    "decision": decision.value,
                    "applied": False,
                }
            raise DeliveryError(
                ErrorCode.IDEMPOTENCY_CONFLICT,
                details_safe={"idempotency_key": f"{delivery_part_id}:{decision_request_id}"},
            )

        repository.set_part_state(
            connection,
            part_id=part.id,
            state=target_state,
            provider_message_id=None,
            now=now,
        )
        rows = repository.list_parts(connection, delivery_id=part.delivery_id)
        cancelled = decision is DeliveryUnknownDecision.ABANDON and not any(
            row.state is DeliveryPartState.SENT for row in rows
        )
        aggregate = parts_module.aggregate_state(part_states(rows), cancelled=cancelled)
        repository.set_delivery_state(
            connection, delivery_id=part.delivery_id, state=aggregate, now=now
        )
        _release_or_close_intent(
            context,
            connection,
            delivery_id=part.delivery_id,
            owner_id=owner_id,
            reopen=decision is DeliveryUnknownDecision.RESEND_ACCEPTING_DUPLICATE_RISK,
        )
        return {
            "delivery_part_id": part.id,
            "state": target_state.value,
            "delivery_state": aggregate.value,
            "decision": decision.value,
            "applied": True,
        }


def _release_or_close_intent(
    context: DeliveryContext,
    connection: Connection,
    *,
    delivery_id: str,
    owner_id: str,
    reopen: bool,
) -> None:
    """Put a held intent back to ``ready`` on resend, or close it on the other two answers.

    This is the *only* place ``held_for_review -> ready`` happens, and it is reachable only
    from :func:`decide_unknown`. That is AMD-B03 expressed as control flow rather than as a
    comment.
    """
    from sqlalchemy import text as sql_text

    delivery = context.repository.get_delivery(connection, delivery_id=delivery_id)
    if delivery is None:
        return
    connection.execute(
        sql_text(
            "UPDATE outbox_intent SET dispatch_state = :s WHERE owner_id = :o "
            "AND intent_type = 'telegram_digest' AND subject_ref = :ref"
        ),
        {
            "s": "ready" if reopen else "done",
            "o": owner_id,
            "ref": _canonical_subject({"report_id": delivery.report_id}),
        },
    )


__all__ = [
    "DeliveryContext",
    "DeliveryDependencyUnavailable",
    "DeliveryError",
    "DispatchOutcome",
    "LinkSnapshot",
    "PermanentFailure",
    "PublishedDigest",
    "ReportPayloadPort",
    "RetryableFailure",
    "Sent",
    "TelegramLinkPort",
    "TelegramTransport",
    "UncertainOutcome",
    "create_intent",
    "decide_unknown",
    "dispatch_next",
    "get_status",
    "mark_unknown",
    "record_receipt",
]
