"""``assignment_lease``: the epoch, the TTL, and the refusal of everything older.

This module is the whole of invariant **I10** — *"worker stale/cancelled không commit kết quả
mới"* — and of ``contracts/state/run.yaml`` ``lease_model`` LM-01…LM-08. It is kept separate
from :mod:`server.app.jobs.service` for one reason: card §12 tells the reviewer to ask *"có
đường nào để worker epoch cũ ghi được dữ liệu không"*, and that question is answerable only if
there is a single place where the epoch is checked. There is, and it is
:func:`assert_current_lease`.

The eight rules, and where each one lives
------------------------------------------
=====  =============================================  ====================================
rule   what it says                                   where
=====  =============================================  ====================================
LM-01  registration grants no lease                   ``service.register_capabilities``
LM-02  at most one ``held`` lease per job             ``ux_assignment_lease_one_held`` (0010)
LM-03  epoch ``+1`` per grant, never reused           :func:`next_epoch`
LM-04  epoch checked before any write, same txn       :func:`assert_current_lease`
LM-05  expiry is ``expires_at + heartbeat_grace``     :func:`is_expired`
LM-06  revocation always bumps the epoch              :func:`revoke`
LM-07  resume always issues a *new* lease             ``service.resume_run`` + :func:`revoke`
LM-08  after a restore every lease is stale           :func:`assert_current_lease`
=====  =============================================  ====================================

Why two error codes and not one
-------------------------------
``contracts/errors.yaml`` registers both ``STALE_LEASE`` and ``WORKER_LEASE_EXPIRED``, and
they answer different questions:

``STALE_LEASE``
    *Somebody else holds this job now.* The caller's epoch is behind the current one. Card §7:
    "lời gọi bị từ chối, dữ liệu authoritative không đổi". Fixture
    ``collection/f-two-workers-claim-same-assignment.json`` pins this for worker A's heartbeat
    **and** for its ``ingest.submit_batch``.

``WORKER_LEASE_EXPIRED``
    *Your lease ran out and nobody has taken over yet.* The epoch still matches but the clock
    passed ``expires_at + heartbeat_grace``. Card §7: the assignment is revoked and the run
    returns to ``queued`` — unless ``worker.report_stop`` already committed ``needs_user`` or
    ``blocked``, in which case T-RUN-15 keeps the stored state.

Collapsing them would make the run-state consequence unrecoverable from the error alone,
which is precisely the difference between T-RUN-14 and a lost job.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode

# --------------------------------------------------------------------------------------
# Numbers -- contracts/retry-policy.yaml §budgets. Named, not inlined.
# --------------------------------------------------------------------------------------

#: ``lease_ttl_collector`` = 120 s (PROVISIONAL). The contract states the constraint that
#: makes it a valid choice rather than a round number: ``>= 4 x heartbeat_interval`` and
#: ``> online_threshold`` (90 s, ``contracts/ops/deployment.md``).
LEASE_TTL_COLLECTOR_SECONDS: int = 120

#: ``lease_ttl_analysis`` = 900 s. Present because ``assignment_lease`` is shared with
#: ``MOD-analysis-service``; this card does not issue analysis leases.
LEASE_TTL_ANALYSIS_SECONDS: int = 900

#: ``heartbeat_interval_collector`` = 30 s — defined by ``contracts/ops/deployment.md`` §6 and
#: only *referenced* by retry-policy, which is why the constraint below is asserted rather
#: than assumed.
HEARTBEAT_INTERVAL_COLLECTOR_SECONDS: int = 30

#: ``heartbeat_grace`` = 30 s. A missed beat caused by a GC pause or a two-second network
#: blip must not cost a lease, because revocation costs a re-claim and can duplicate work.
HEARTBEAT_GRACE_SECONDS: int = 30

#: ``lease_expiry_sweep_interval`` = 15 s: how often the server looks for expired leases.
LEASE_EXPIRY_SWEEP_INTERVAL_SECONDS: int = 15

#: ``claim_idle_backoff`` = 5/15/45 s. The ``retry_after_ms`` of a ``no_work`` answer; the
#: fixture pins the ceiling (45 000 ms) for a worker that already holds an assignment.
CLAIM_IDLE_BACKOFF_SECONDS: tuple[int, int, int] = (5, 15, 45)

#: ``lease_epoch_rule`` = 1 increment per grant *and* per deliberate revocation.
LEASE_EPOCH_INCREMENT: int = 1

# The relationship retry-policy states as a constraint rather than a coincidence. Asserted at
# import so that changing one number without the other fails loudly instead of silently
# producing a TTL shorter than the heartbeat that is supposed to renew it.
assert LEASE_TTL_COLLECTOR_SECONDS >= 4 * HEARTBEAT_INTERVAL_COLLECTOR_SECONDS  # noqa: S101


class LeaseState(str, Enum):
    """``assignment_lease.state``: ``held | released | expired | revoked``."""

    HELD = "held"
    RELEASED = "released"
    EXPIRED = "expired"
    REVOKED = "revoked"


#: The three states a lease can be moved to. ``held`` is not among them: a lease becomes
#: ``held`` only by being inserted, so a released or expired row can never be revived —
#: LM-03's "không bao giờ dùng lại" as a data rule.
TERMINAL_LEASE_STATES: frozenset[LeaseState] = frozenset(
    {LeaseState.RELEASED, LeaseState.EXPIRED, LeaseState.REVOKED}
)


# --------------------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------------------

#: ``message_safe_template_vi`` verbatim from ``contracts/errors.yaml``. Copied from the
#: contract rather than paraphrased: the envelope forbids interpolating anything outside
#: ``details_safe_keys``, so these strings are the whole of what a person is shown.
#: ``UNAUTHORIZED_COMMAND``'s template is the contract's own literal text -- that code is
#: never emitted to an unknown chat at all (silence policy, ``telegram`` cards), and the
#: string exists so a log line has something honest to carry.
MESSAGE_SAFE: dict[ErrorCode, str] = {
    ErrorCode.STALE_LEASE: "Yêu cầu dùng phiên làm việc đã cũ và bị từ chối.",
    ErrorCode.WORKER_LEASE_EXPIRED: "Phiên làm việc của worker đã hết hạn. Việc sẽ được giao lại.",
    ErrorCode.VALIDATION_ERROR: "Dữ liệu gửi lên không hợp lệ.",
    ErrorCode.NOT_FOUND: "Không tìm thấy mục bạn yêu cầu.",
    ErrorCode.IDEMPOTENCY_CONFLICT: "Yêu cầu trùng khóa nhưng nội dung khác với lần đã ghi nhận.",
    ErrorCode.CONFLICT: "Một tiến trình khác vừa ghi trước. Hệ thống đọc lại và thử lại.",
    ErrorCode.UNAUTHORIZED: "Không có quyền thực hiện thao tác này.",
    ErrorCode.UNAUTHORIZED_COMMAND: "(không phát ra ngoài — chính sách im lặng)",
    ErrorCode.CSRF_REJECTED: "Yêu cầu không hợp lệ. Hãy tải lại trang rồi thử lại.",
    ErrorCode.FORBIDDEN_EDGE: "Đường gọi này không được phép.",
    ErrorCode.CAPABILITY_DENIED: "Thao tác bị chặn ở mức nền tảng.",
    ErrorCode.STORAGE_WRITE_FAILED: (
        "Hệ thống tạm thời không ghi được dữ liệu. Đã dừng nhận việc mới."
    ),
    ErrorCode.RESTORE_UNVERIFIED: (
        "Vừa khôi phục dữ liệu. Việc gửi và giao việc đang tạm khóa cho tới khi đối soát " "xong."
    ),
    ErrorCode.X_CHALLENGE_REQUIRED: (
        "Đợt chạy đang chờ bạn xác minh trên X. Xử lý trong cửa sổ Chrome rồi bấm “tiếp tục”."
    ),
    ErrorCode.X_ACCESS_BLOCKED: (
        "Đợt chạy dừng vì X đang chặn truy cập. Không có thay đổi nào được thực hiện để lách."
    ),
    ErrorCode.RATE_LIMITED: "Nguồn đang giới hạn nhịp truy cập. Hệ thống chờ rồi thử lại.",
    ErrorCode.SOURCE_LAYOUT_CHANGED: (
        "Đợt chạy dừng vì bố cục nguồn đã thay đổi và không đọc được dữ liệu. Cần cập nhật bộ "
        "đọc."
    ),
    ErrorCode.INTERNAL: "Có lỗi hệ thống. Trạng thái của thao tác chưa xác định.",
}

#: ``details_safe_keys`` verbatim from ``contracts/errors.yaml``. Keys outside a code's set
#: are dropped before the envelope leaves the process; the envelope's own rule makes an
#: unknown key a producer-side defect, so leaking one is the worse failure. Note the two
#: lease codes name ``lease_epoch_seen``/``lease_epoch_current`` -- not the shorter names a
#: reader might expect -- and ``WORKER_LEASE_EXPIRED`` carries ``expired_at``, not a run
#: status: the contract does not let this module put run state in an envelope.
DETAILS_SAFE_KEYS: dict[ErrorCode, frozenset[str]] = {
    ErrorCode.STALE_LEASE: frozenset({"job_id", "lease_epoch_current", "lease_epoch_seen"}),
    ErrorCode.WORKER_LEASE_EXPIRED: frozenset(
        {"expired_at", "job_id", "lease_epoch_current", "lease_epoch_seen"}
    ),
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"field_path", "limit_name", "limit_value", "operation_id", "violation_kind"}
    ),
    ErrorCode.NOT_FOUND: frozenset({"operation_id", "resource_kind"}),
    ErrorCode.IDEMPOTENCY_CONFLICT: frozenset(
        {"idempotency_key", "payload_hash_seen", "payload_hash_stored"}
    ),
    ErrorCode.CONFLICT: frozenset(
        {
            "attempt_number",
            "current_predecessor_id",
            "expected_predecessor_id",
            "resource_kind",
            "retry_after_ms",
        }
    ),
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
    ErrorCode.UNAUTHORIZED_COMMAND: frozenset({"command_kind", "rejection_reason_code"}),
    ErrorCode.CSRF_REJECTED: frozenset({"operation_id"}),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"callee_module", "caller_module", "forbidden_edge_ref"}),
    ErrorCode.CAPABILITY_DENIED: frozenset(
        {"denied_capability_kind", "forbidden_edge_ref", "module_id"}
    ),
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"failed_operation_id", "observed_at", "retry_after_ms", "storage_health"}
    ),
    ErrorCode.RESTORE_UNVERIFIED: frozenset(
        {"pending_outbox_count", "restore_id", "snapshot_id", "storage_health"}
    ),
    ErrorCode.X_CHALLENGE_REQUIRED: frozenset(
        {"acked_through_ingest_sequence", "detected_at", "phase", "run_id", "stop_reason"}
    ),
    ErrorCode.X_ACCESS_BLOCKED: frozenset(
        {"blocked_since", "phase", "run_id", "stop_reason", "unblock_condition_vi"}
    ),
    ErrorCode.RATE_LIMITED: frozenset(
        {"attempt_number", "rate_limited_at", "retry_after_ms", "source_kind", "window_seconds"}
    ),
    ErrorCode.SOURCE_LAYOUT_CHANGED: frozenset(
        {
            "missing_required_fields",
            "phase",
            "posts_parsed_ok",
            "posts_seen",
            "run_id",
            "stop_reason",
        }
    ),
    ErrorCode.INTERNAL: frozenset({"correlation_id", "operation_id"}),
}

_HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.UNAUTHORIZED_COMMAND: 401,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.CAPABILITY_DENIED: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.STALE_LEASE: 409,
    ErrorCode.WORKER_LEASE_EXPIRED: 409,
    ErrorCode.RESTORE_UNVERIFIED: 409,
    ErrorCode.X_CHALLENGE_REQUIRED: 409,
    ErrorCode.X_ACCESS_BLOCKED: 409,
    ErrorCode.SOURCE_LAYOUT_CHANGED: 409,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}


class JobError(Exception):
    """An error from ``MOD-job-service`` / ``MOD-scheduler``, carrying a registered code."""

    def __init__(
        self,
        code: ErrorCode,
        *,
        details_safe: dict[str, Any] | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        permitted = DETAILS_SAFE_KEYS[code]
        self.code = code
        self.details_safe = {k: v for k, v in (details_safe or {}).items() if k in permitted}
        self.retry_after_ms = retry_after_ms
        self.message_safe = MESSAGE_SAFE[code]
        super().__init__(f"{code.value}: {self.message_safe}")

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS[self.code]

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """The seven-field envelope of ``contracts/errors.yaml`` → ``error_envelope``.

        ``scope`` and ``retry_class`` are read from the generated maps rather than passed in,
        so no handler can hand a caller a retry policy the contract did not grant. Nothing
        here ever carries a transcript, a cookie or a token (SRC-PLAN §5.1) — the
        ``details_safe`` filter above is what makes that structural.
        """
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
            "retry_after_ms": self.retry_after_ms,
        }


# --------------------------------------------------------------------------------------
# The lease itself
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Lease:
    """One ``assignment_lease`` row, as the contract declares it."""

    id: str
    owner_id: str
    run_id: str
    job_id: str
    worker_identity: str
    lease_epoch: int
    expires_at: datetime
    state: LeaseState

    def wire(self, *, ttl_seconds: int = LEASE_TTL_COLLECTOR_SECONDS) -> dict[str, Any]:
        """The ``lease`` object of ``contracts/schemas/worker-assignment.schema.json``.

        Five required properties and nothing else — the schema is
        ``additionalProperties: false``, so an extra field here is a validation failure
        rather than a harmless extra.
        """
        return {
            "lease_id": self.id,
            "lease_epoch": self.lease_epoch,
            "ttl_s": ttl_seconds,
            "heartbeat_interval_s": HEARTBEAT_INTERVAL_COLLECTOR_SECONDS,
            "expires_at": timestamp_utc_ms(self.expires_at),
        }


def timestamp_utc_ms(moment: datetime) -> str:
    """RFC 3339, UTC, exactly three fractional digits (``timestamp_utc_ms``, AMD-B08)."""
    aware = moment.astimezone(UTC)
    return f"{aware.strftime('%Y-%m-%dT%H:%M:%S')}.{aware.microsecond // 1000:03d}Z"


def parse_timestamp_utc_ms(text: str) -> datetime:
    """Inverse of :func:`timestamp_utc_ms`."""
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)


def next_epoch(current: int) -> int:
    """LM-03: exactly ``+1``, every grant and every deliberate revocation.

    A function rather than an inline ``+ 1`` so that "the epoch moved by one" is one fact in
    one place. LM-03's other half — never reused — is enforced by
    ``ux_lease_job_epoch (owner_id, job_id, lease_epoch)``: re-issuing a used epoch is a
    UNIQUE violation, not a judgement call.
    """
    if current < 0:
        raise ValueError("lease_epoch never goes below zero")
    return current + LEASE_EPOCH_INCREMENT


def expiry_from(now: datetime, *, ttl_seconds: int = LEASE_TTL_COLLECTOR_SECONDS) -> datetime:
    """LM-05, the renewing half: ``expires_at = now + lease_ttl``."""
    return now.astimezone(UTC) + timedelta(seconds=ttl_seconds)


def is_expired(
    lease: Lease, now: datetime, *, grace_seconds: int = HEARTBEAT_GRACE_SECONDS
) -> bool:
    """LM-05: expired when ``now > expires_at + heartbeat_grace``.

    The grace period is part of the definition, not a courtesy applied at some call sites and
    not others: a lease read as expired 30 s early is a lease revoked while its holder is
    still working, and the duplicate claim that follows is exactly what I10 is about.
    """
    return now.astimezone(UTC) > lease.expires_at + timedelta(seconds=grace_seconds)


def assert_current_lease(
    lease: Lease | None,
    *,
    presented_epoch: int,
    job_id: str,
    now: datetime,
    restore_pending: bool = False,
    operation_id: str = "worker.heartbeat",
) -> Lease:
    """**The** gate. LM-04: call this before any write, inside the same transaction.

    The order of the four refusals is load-bearing, and each answers a different question:

    1. **no lease at all** → ``NOT_FOUND``. There is nothing to be stale *relative to*.
    2. **a restore is pending** → ``STALE_LEASE`` (LM-08). Every lease in a restored snapshot
       is stale regardless of ``expires_at``, because the clock jumped and the worker that
       held it may no longer exist. Only ``backup.reconcile_after_restore`` clears this.
       Checked **before** the epoch, so a worker whose epoch happens to match is still
       refused — fixture ``recovery/b-post-restore-stale-lease-rejected.json``.
    3. **epoch behind, or the lease is no longer held** → ``STALE_LEASE``. Somebody else has
       the job.
    4. **epoch matches but the clock passed** → ``WORKER_LEASE_EXPIRED``.

    :raises JobError: with the code above. It raises rather than returning a flag because a
        boolean a caller forgets to check would let a stale worker's write through, and that
        single omission is the whole of the I10 counterexample in
        ``contracts/state/run.yaml`` ``lease_model.stale_writer_rejection``.
    """
    if lease is None:
        raise JobError(
            ErrorCode.NOT_FOUND,
            details_safe={"operation_id": operation_id, "resource_kind": "assignment_lease"},
        )
    if restore_pending:
        raise JobError(
            ErrorCode.STALE_LEASE,
            details_safe={
                "job_id": job_id,
                "lease_epoch_seen": presented_epoch,
                "lease_epoch_current": lease.lease_epoch,
            },
        )
    if presented_epoch != lease.lease_epoch or lease.state is not LeaseState.HELD:
        raise JobError(
            ErrorCode.STALE_LEASE,
            details_safe={
                "job_id": job_id,
                "lease_epoch_seen": presented_epoch,
                "lease_epoch_current": lease.lease_epoch,
            },
        )
    if is_expired(lease, now):
        raise JobError(
            ErrorCode.WORKER_LEASE_EXPIRED,
            # `run_status` is deliberately NOT reported here: `WORKER_LEASE_EXPIRED`'s
            # `details_safe_keys` do not include it, so it would be filtered out anyway, and
            # accepting the argument would imply a promise the envelope cannot keep.
            details_safe={
                "job_id": job_id,
                "lease_epoch_seen": presented_epoch,
                "lease_epoch_current": lease.lease_epoch,
                "expired_at": timestamp_utc_ms(lease.expires_at),
            },
        )
    return lease


def revoke(lease: Lease, *, to: LeaseState) -> tuple[LeaseState, int]:
    """LM-06: every deliberate revocation moves the state **and** bumps the epoch.

    Returns the pair so a caller cannot do one without the other. Bumping on revocation — not
    only on grant — is what makes a revoked lease unusable even if its holder never learns:
    the next presented epoch is behind, so :func:`assert_current_lease` refuses it. Without
    the bump, ``run.cancel`` would leave a worker holding a lease whose epoch still matches.
    """
    if to not in TERMINAL_LEASE_STATES:
        raise ValueError(f"{to} is not a revocation state; a lease is never revived")
    return to, next_epoch(lease.lease_epoch)


__all__ = [
    "CLAIM_IDLE_BACKOFF_SECONDS",
    "DETAILS_SAFE_KEYS",
    "HEARTBEAT_GRACE_SECONDS",
    "HEARTBEAT_INTERVAL_COLLECTOR_SECONDS",
    "LEASE_EPOCH_INCREMENT",
    "LEASE_EXPIRY_SWEEP_INTERVAL_SECONDS",
    "LEASE_TTL_ANALYSIS_SECONDS",
    "LEASE_TTL_COLLECTOR_SECONDS",
    "MESSAGE_SAFE",
    "TERMINAL_LEASE_STATES",
    "JobError",
    "Lease",
    "LeaseState",
    "assert_current_lease",
    "expiry_from",
    "is_expired",
    "next_epoch",
    "parse_timestamp_utc_ms",
    "revoke",
    "timestamp_utc_ms",
]
