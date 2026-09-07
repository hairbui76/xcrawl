"""HTTP client for the nine operations the collector is allowed to call.

Card §4 lists them and card §5 says which edges exist: ``worker.*`` on ``MOD-job-service``
and ``ingest.*`` on ``MOD-ingest-service``, both with the ``collectorToken`` bearer, plus
``health.get_liveness``. Nothing else. There is no method here for ``save.create``,
``storage.get_health`` or any analysis operation, and that absence is deliberate: a client
that cannot spell a forbidden call cannot make one by accident.

The one rule that shapes this module
------------------------------------
**A transport timeout is not a rollback.** ``SRC-PLAN §5.1`` and card §6: when a mutation's
response does not arrive, the collector does not know whether the server committed. The
only permitted next step is to ask -- ``ingest.get_receipt`` -- and to decide from the
answer. :meth:`CollectorClient.submit_batch` implements that as the *only* path back to a
resend: there is no code path in this module that retries a batch without first reading a
receipt, which is why ``d-duplicate-ingest-replay``'s "gửi lại mà chưa tra get_receipt" can
be asserted absent rather than merely discouraged.

Stop reasons have two vocabularies, and they are not the same one
-----------------------------------------------------------------
The value the collector *sends* on ``worker.report_stop`` and the value the server *stores*
on ``run.stop_reason`` differ for three of the eight cases, and the difference is in the
contracts on purpose:

* wire ``challenge_required`` -> run ``captcha``
* wire ``worker_shutdown`` -> run ``worker_lost``
* wire ``local_storage_unavailable`` -> run ``storage_unavailable``

``contracts/ports.yaml`` ``worker.report_stop`` defines the request vocabulary,
``contracts/state/run.yaml`` §enums.stop_reason the stored one, and T-RUN-09 shows the
mapping explicitly ("stop_reason ∈ {challenge_required, session_expired}" going to
``captcha | session_expired``). :data:`WIRE_TO_RUN_STOP_REASON` is that table, and
``tests/contract/test_collector_stop_reasons.py`` is where it is checked against both files
rather than trusted.

Redaction
---------
The bearer token is never placed in an exception message, a ``repr`` or a details field, and
:class:`ServerError` carries only the server's ``message_safe`` and ``details_safe``
(``contracts/errors.yaml`` §error_envelope.forbidden_content_vi).
"""

from __future__ import annotations

import os
import secrets
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.states import RunStopReason

SCHEMA_VERSION_HEADER = "X-Schema-Version"
REQUEST_ID_HEADER = "X-Request-Id"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"

#: ``contracts/retry-policy.yaml §budgets.ingest_batch_backoff`` -- 2 s, 8 s, 32 s.
INGEST_BATCH_BACKOFF_S: tuple[int, ...] = (2, 8, 32)

#: ``contracts/retry-policy.yaml §budgets.claim_request_timeout``.
CLAIM_REQUEST_TIMEOUT_S = 10

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid(*, now_ms: int | None = None) -> str:
    """A 26-character Crockford base32 ULID matching ``^[0-9A-HJKMNP-TV-Z]{26}$``.

    Written here rather than imported from the server package: the collector process shares
    no code with the server (card §5, ``SL-7``).
    """
    timestamp = int(time.time() * 1000) if now_ms is None else now_ms
    value = (timestamp << 80) | secrets.randbits(80)
    out = []
    for _ in range(26):
        out.append(_CROCKFORD[value & 0x1F])
        value >>= 5
    return "".join(reversed(out))


class WireStopReason(str, Enum):
    """``stop_reason`` as sent on ``worker.report_stop`` (``contracts/ports.yaml``)."""

    CHALLENGE_REQUIRED = "challenge_required"
    LIMIT_REACHED = "limit_reached"
    SESSION_EXPIRED = "session_expired"
    SOURCE_BLOCKED = "source_blocked"
    SOURCE_LAYOUT_CHANGED = "source_layout_changed"
    RATE_LIMITED = "rate_limited"
    WORKER_SHUTDOWN = "worker_shutdown"
    LOCAL_STORAGE_UNAVAILABLE = "local_storage_unavailable"


#: Wire vocabulary -> the value the server stores on ``run.stop_reason``.
WIRE_TO_RUN_STOP_REASON: dict[WireStopReason, RunStopReason] = {
    WireStopReason.CHALLENGE_REQUIRED: RunStopReason.CAPTCHA,
    WireStopReason.LIMIT_REACHED: RunStopReason.LIMIT_REACHED,
    WireStopReason.SESSION_EXPIRED: RunStopReason.SESSION_EXPIRED,
    WireStopReason.SOURCE_BLOCKED: RunStopReason.SOURCE_BLOCKED,
    WireStopReason.SOURCE_LAYOUT_CHANGED: RunStopReason.SOURCE_LAYOUT_CHANGED,
    WireStopReason.RATE_LIMITED: RunStopReason.RATE_LIMITED,
    WireStopReason.WORKER_SHUTDOWN: RunStopReason.WORKER_LOST,
    WireStopReason.LOCAL_STORAGE_UNAVAILABLE: RunStopReason.STORAGE_UNAVAILABLE,
}

#: Wire stop reason -> the error code the server answers with, or ``None`` when the stop is
#: not an error at all. ``limit_reached`` maps to ``None`` deliberately: ``AMD-B02`` and
#: ``T-RUN-02`` both say hitting a budget is not a failure, and giving it an error code is
#: how "dừng sớm" would start being displayed as "thất bại" (I13).
STOP_REASON_ERROR_CODE: dict[WireStopReason, ErrorCode | None] = {
    WireStopReason.CHALLENGE_REQUIRED: ErrorCode.X_CHALLENGE_REQUIRED,
    WireStopReason.LIMIT_REACHED: None,
    WireStopReason.SESSION_EXPIRED: ErrorCode.X_CHALLENGE_REQUIRED,
    WireStopReason.SOURCE_BLOCKED: ErrorCode.X_ACCESS_BLOCKED,
    WireStopReason.SOURCE_LAYOUT_CHANGED: ErrorCode.SOURCE_LAYOUT_CHANGED,
    WireStopReason.RATE_LIMITED: ErrorCode.RATE_LIMITED,
    WireStopReason.WORKER_SHUTDOWN: None,
    # ``local_storage_unavailable`` is the *collector's own* disk failing, and the registry
    # has no code for that: ``contracts/errors.yaml`` scopes ``STORAGE_WRITE_FAILED`` to the
    # server's store (its ``operations`` are ``storage.get_health``, ``health.get_readiness``,
    # the two ingest mutations, ``report.publish`` and ``delivery.record_receipt``). Reusing
    # it here would tell an operator the server's database is in trouble when it is not.
    WireStopReason.LOCAL_STORAGE_UNAVAILABLE: None,
}

#: Codes a ``worker.report_stop`` response may echo back as the *acknowledgement* of the
#: reported reason. ``a-feed-layout-changed`` answers 409 ``SOURCE_LAYOUT_CHANGED`` to a
#: successful report, so these are not client failures and must not be retried.
_STOP_ECHO_CODES = frozenset(code for code in STOP_REASON_ERROR_CODE.values() if code is not None)

#: Codes that mean "stop now, submit nothing further" (card §7).
LEASE_LOST_CODES = frozenset({ErrorCode.STALE_LEASE, ErrorCode.WORKER_LEASE_EXPIRED})


class ServerError(Exception):
    """A contract error envelope, raised as a typed exception.

    Every field comes from the envelope ``contracts/errors.yaml`` defines. ``code`` is an
    :class:`ErrorCode` member, never a string, so a caller cannot branch on a code that does
    not exist in the registry.
    """

    def __init__(
        self,
        code: ErrorCode,
        *,
        message_safe: str = "",
        scope: str | None = None,
        retry_class: str | None = None,
        correlation_id: str | None = None,
        details_safe: Mapping[str, Any] | None = None,
        retry_after_ms: int | None = None,
        http_status: int | None = None,
    ) -> None:
        super().__init__(f"{code.value}: {message_safe}")
        self.code = code
        self.message_safe = message_safe
        self.scope = scope or SCOPE.get(code)
        self.retry_class = retry_class or RETRY_CLASS.get(code)
        self.correlation_id = correlation_id
        self.details_safe = dict(details_safe or {})
        self.retry_after_ms = retry_after_ms
        self.http_status = http_status

    @property
    def is_lease_lost(self) -> bool:
        return self.code in LEASE_LOST_CODES


class OutcomeUnknown(Exception):
    """A mutation whose result the client did not learn (transport failure).

    Not an error envelope: the server never answered. ``SRC-PLAN §5.1`` -- this is
    "không biết kết quả", and the only legal response is to look the receipt up.
    """

    def __init__(self, operation: str, idempotency_key: str) -> None:
        super().__init__(f"{operation}: no response for idempotency_key={idempotency_key}")
        self.operation = operation
        self.idempotency_key = idempotency_key


@dataclass(frozen=True)
class StopAck:
    """What the server said about a reported stop.

    :param run: the run's state after the report (``status``/``phase``/``stop_reason``).
    :param alert_intent_created: whether *this* call created the run's single alert intent.
        A repeat report with the same ``stop_report_id`` answers ``False`` -- that is the
        observable form of "đúng một alert intent mỗi run" (REQ-AC04).
    :param echoed_code: the code the server echoed, when it answered with an envelope.
    """

    run: dict[str, Any]
    alert_intent_created: bool
    alert_intent_id: str | None = None
    echoed_code: ErrorCode | None = None


@dataclass(frozen=True)
class ReceiptLookup:
    """The answer to ``ingest.get_receipt``: a committed receipt, or ``not_committed``."""

    committed: bool
    receipt: dict[str, Any] | None = None
    safe_to_resubmit: bool = False

    @property
    def max_ingest_sequence(self) -> int:
        if self.receipt is None:
            return 0
        counts = self.receipt.get("counts") or {}
        return int(counts.get("max_ingest_sequence", 0))


@dataclass
class CollectorClient:
    """The collector's only door to the server.

    :param base_url: server root.
    :param token: the ``collectorToken``. Read from a restricted-permission file on the
        personal machine in a real deployment (SRC-SPEC §11.2); never logged.
    :param transport: an ``httpx`` transport, so tests can drive the real client against a
        fixture replay or the real ASGI app without a socket.
    :param sleep: injected so retry backoff is measurable without waiting.
    """

    base_url: str
    token: str
    transport: httpx.BaseTransport | None = None
    timeout_s: float = float(CLAIM_REQUEST_TIMEOUT_S)
    sleep: Any = time.sleep
    _client: httpx.Client = field(init=False)

    def __post_init__(self) -> None:
        self._client = httpx.Client(
            base_url=self.base_url,
            transport=self.transport,
            timeout=self.timeout_s,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> CollectorClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # ---------------------------------------------------------------- plumbing

    def _headers(self, *, idempotency_key: str | None = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION,
            REQUEST_ID_HEADER: new_ulid(),
            "Content-Type": "application/json",
        }
        if idempotency_key is not None:
            headers[IDEMPOTENCY_KEY_HEADER] = idempotency_key
        return headers

    @staticmethod
    def _envelope(body: Any) -> dict[str, Any] | None:
        """Find the error envelope in a response body, in either of its two shapes.

        Fixtures use both: ``d``/``f`` answer with a bare envelope, ``a`` nests it under
        ``error`` alongside a ``run`` object. Accepting both is not laxity -- the contract
        pins the envelope's *fields*, and a client that only understood one nesting would
        read a real error as an unparsable response.
        """
        if not isinstance(body, dict):
            return None
        if isinstance(body.get("error"), dict):
            envelope = body["error"]
            return envelope if "code" in envelope else None
        return body if "code" in body and "message_safe" in body else None

    def _raise_for_envelope(self, response: httpx.Response) -> dict[str, Any]:
        """Return the parsed body, or raise :class:`ServerError` if it carries an envelope."""
        try:
            body = response.json()
        except ValueError:
            raise ServerError(
                ErrorCode.INTERNAL,
                message_safe="Phản hồi của máy chủ không phải JSON.",
                http_status=response.status_code,
            ) from None
        envelope = self._envelope(body)
        if envelope is None:
            if response.status_code >= 400:
                raise ServerError(
                    ErrorCode.INTERNAL,
                    message_safe="Máy chủ trả lỗi không đúng hình dạng envelope hợp đồng.",
                    http_status=response.status_code,
                )
            return body if isinstance(body, dict) else {}
        code = ErrorCode(envelope["code"])
        raise ServerError(
            code,
            message_safe=str(envelope.get("message_safe", "")),
            scope=envelope.get("scope"),
            retry_class=envelope.get("retry_class"),
            correlation_id=envelope.get("correlation_id"),
            details_safe=envelope.get("details_safe") or {},
            retry_after_ms=envelope.get("retry_after_ms"),
            http_status=response.status_code,
        )

    def _post(
        self, path: str, body: Mapping[str, Any], *, idempotency_key: str | None = None
    ) -> dict[str, Any]:
        response = self._client.post(
            path, json=dict(body), headers=self._headers(idempotency_key=idempotency_key)
        )
        return self._raise_for_envelope(response)

    def _get(self, path: str, *, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        response = self._client.get(path, params=dict(params or {}), headers=self._headers())
        return self._raise_for_envelope(response)

    # ------------------------------------------------------------- worker.*

    def register_capabilities(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        """``worker.register_capabilities``. Grants no lease -- see ``g-schedule-due-claim``."""
        body = dict(payload)
        body.setdefault("request_id", new_ulid())
        key = f"{body['worker_instance_id']}:reg:{int(body['registration_seq']):06d}"
        return self._post("/v1/workers/registrations", body, idempotency_key=key)

    def claim_assignment(
        self,
        *,
        claim_request_id: str,
        worker_instance_id: str,
        capabilities: Mapping[str, Any],
        max_assignments: int = 1,
    ) -> dict[str, Any]:
        """``worker.claim_assignment``.

        Returns the whole ``worker-assignment`` union body, so the caller sees whether it
        got ``assignment`` or ``no_work``. ``no_work`` is not an error
        (``worker-assignment.schema.json``: "Response khi không có việc. KHÔNG phải lỗi") and
        must not be raised as one -- I13 again: nothing to do is not failure.

        On a transport timeout the claim is retried with the **same**
        ``claim_request_id``. ``contracts/ports.yaml`` guarantees "cùng claim_request_id trả
        cùng assignment; không cấp hai lease", so re-asking is safe and minting a fresh id
        would be the one way to end up with two leases.
        """
        body = {
            "claim_request": {
                "request_id": new_ulid(),
                "schema_version": CONTRACT_SCHEMA_VERSION,
                "claim_request_id": claim_request_id,
                "worker_instance_id": worker_instance_id,
                "worker_kind": "collector",
                "capabilities": dict(capabilities),
                "max_assignments": max_assignments,
            }
        }
        try:
            return self._post(
                "/v1/workers/assignments/claim", body, idempotency_key=claim_request_id
            )
        except (httpx.TimeoutException, httpx.TransportError):
            body["claim_request"]["request_id"] = new_ulid()
            return self._post(
                "/v1/workers/assignments/claim", body, idempotency_key=claim_request_id
            )

    def heartbeat(
        self,
        *,
        assignment_id: str,
        lease_id: str,
        lease_epoch: int,
        posts_seen_in_run: int,
        posts_submitted_in_run: int,
        elapsed_s: int,
        x_session_state: str,
    ) -> dict[str, Any]:
        """``worker.heartbeat``. Carries the lease epoch on every beat.

        A stale epoch answers ``STALE_LEASE`` and changes nothing
        (``f-two-workers-claim-same-assignment`` event 2); the caller must stop rather than
        keep collecting, which is why this raises instead of returning a status.
        """
        body = {
            "heartbeat_request": {
                "request_id": new_ulid(),
                "schema_version": CONTRACT_SCHEMA_VERSION,
                "assignment_id": assignment_id,
                "lease_id": lease_id,
                "lease_epoch": lease_epoch,
                "observed_progress": {
                    "posts_seen_in_run": posts_seen_in_run,
                    "posts_submitted_in_run": posts_submitted_in_run,
                    "elapsed_s": elapsed_s,
                },
                "x_session_state": x_session_state,
            }
        }
        return self._post(f"/v1/workers/assignments/{assignment_id}/heartbeat", body)

    def report_stop(
        self,
        *,
        assignment_id: str,
        stop_report_id: str,
        lease_id: str,
        lease_epoch: int,
        stop_reason: WireStopReason,
        last_acked_ingest_sequence: int,
        extra: Mapping[str, Any] | None = None,
    ) -> StopAck:
        """``worker.report_stop`` -- report and halt. Never a prelude to a retry.

        ``stop_report_id`` is supplied by the caller and **reused** on a repeat report: the
        idempotency scope is ``assignment_id + stop_report_id`` and reusing it is what makes
        "báo lại không tạo alert thứ hai" true. Minting a fresh id on the second call would
        produce the second alert the contract forbids.

        A response carrying one of the stop codes (``X_CHALLENGE_REQUIRED``,
        ``SOURCE_LAYOUT_CHANGED``, ``X_ACCESS_BLOCKED``, ``RATE_LIMITED``,
        ``STORAGE_WRITE_FAILED``) is the server *echoing the reported reason*, not rejecting
        the call -- ``a-feed-layout-changed`` answers 409 to a report that was accepted and
        did move the run to ``blocked``. Those are returned; everything else (a stale lease,
        a validation failure) is raised.
        """
        body: dict[str, Any] = {
            "request_id": new_ulid(),
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "assignment_id": assignment_id,
            "stop_report_id": stop_report_id,
            "lease_id": lease_id,
            "lease_epoch": lease_epoch,
            "stop_reason": stop_reason.value,
            "last_acked_ingest_sequence": last_acked_ingest_sequence,
        }
        body.update(dict(extra or {}))
        try:
            answer = self._post(
                f"/v1/workers/assignments/{assignment_id}/stop",
                body,
                idempotency_key=stop_report_id,
            )
        except ServerError as error:
            if error.code not in _STOP_ECHO_CODES:
                raise
            run = error.details_safe.get("run")
            return StopAck(
                run=dict(run) if isinstance(run, dict) else {},
                alert_intent_created=bool(error.details_safe.get("alert_intent_created", False)),
                alert_intent_id=None,
                echoed_code=error.code,
            )
        return StopAck(
            run=dict(answer.get("run") or {}),
            alert_intent_created=bool(answer.get("alert_intent_created", False)),
            alert_intent_id=answer.get("alert_intent_id"),
        )

    def release_assignment(
        self,
        *,
        assignment_id: str,
        lease_id: str,
        lease_epoch: int,
        release_reason: str,
    ) -> dict[str, Any]:
        """``worker.release_assignment``. Idempotent on ``assignment_id``.

        ``release_reason`` is one of ``completed_phase | worker_shutdown |
        local_storage_unavailable`` (``release_request`` in the assignment schema). Work
        that finished the feed normally ends here, not with a ``report_stop``: the wire stop
        vocabulary has no "finished" value because finishing is not a stop reason.
        """
        body = {
            "request_id": new_ulid(),
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "assignment_id": assignment_id,
            "lease_id": lease_id,
            "lease_epoch": lease_epoch,
            "release_reason": release_reason,
        }
        return self._post(
            f"/v1/workers/assignments/{assignment_id}/release",
            body,
            idempotency_key=assignment_id,
        )

    # ------------------------------------------------------------- ingest.*

    def get_receipt(self, *, idempotency_key: str, assignment_id: str) -> ReceiptLookup:
        """``ingest.get_receipt`` -- the mandatory lookup before any retry of a mutation."""
        answer = self._get(
            f"/v1/ingest/receipts/{idempotency_key}",
            params={"assignment_id": assignment_id},
        )
        receipt = answer.get("receipt")
        if isinstance(receipt, dict):
            return ReceiptLookup(committed=True, receipt=receipt)
        not_committed = answer.get("not_committed")
        if isinstance(not_committed, dict):
            return ReceiptLookup(
                committed=False,
                safe_to_resubmit=bool(not_committed.get("safe_to_resubmit", True)),
            )
        if answer.get("status") == "not_committed":
            return ReceiptLookup(
                committed=False, safe_to_resubmit=bool(answer.get("safe_to_resubmit", True))
            )
        raise ServerError(
            ErrorCode.INTERNAL,
            message_safe="Phản hồi get_receipt không khớp hình dạng hợp đồng.",
        )

    def submit_batch(self, batch: Mapping[str, Any], *, assignment_id: str) -> dict[str, Any]:
        """``ingest.submit_batch``. Returns the receipt.

        The ack-loss path, in the order ``SRC-PLAN §5.1`` fixes:

        1. POST. If a receipt comes back -- committed or ``duplicate_replay`` -- done.
        2. If the *transport* failed, the outcome is unknown. Ask ``ingest.get_receipt``.
        3. A committed receipt means the batch is already durable: return it and **do not
           resend**. This is the ``d-duplicate-ingest-replay`` timeline.
        4. ``not_committed`` is the only answer that authorises resending, and the resend
           reuses the same ``idempotency_key`` and the same ``payload_hash``.

        There is no fifth branch. A batch is never resent on a hunch.
        """
        key = str(batch["idempotency_key"])
        for attempt, backoff in enumerate((0, *INGEST_BATCH_BACKOFF_S)):
            if backoff:
                self.sleep(backoff)
            try:
                answer = self._post("/v1/ingest/batches", batch, idempotency_key=key)
            except (httpx.TimeoutException, httpx.TransportError):
                lookup = self.get_receipt(idempotency_key=key, assignment_id=assignment_id)
                if lookup.committed and lookup.receipt is not None:
                    return lookup.receipt
                if not lookup.safe_to_resubmit:
                    raise OutcomeUnknown("ingest.submit_batch", key) from None
                if attempt == len(INGEST_BATCH_BACKOFF_S):
                    raise OutcomeUnknown("ingest.submit_batch", key) from None
                continue
            receipt = answer.get("receipt")
            if not isinstance(receipt, dict):
                raise ServerError(
                    ErrorCode.INTERNAL,
                    message_safe="Phản hồi submit_batch thiếu receipt.",
                )
            return receipt
        raise OutcomeUnknown("ingest.submit_batch", key)

    def commit_checkpoint(
        self,
        *,
        assignment_id: str,
        checkpoint_seq: int,
        lease_id: str,
        lease_epoch: int,
        cursor_token: str | None,
        cursor_state: str,
        proposed_acked_through_ingest_sequence: int,
        reason: str,
    ) -> dict[str, Any]:
        """``ingest.commit_checkpoint`` -- the cursor-only path (§CP-07).

        Three situations only: ``empty_page``, ``end_of_feed``, ``segment_close``. It never
        carries items; items go through :meth:`submit_batch`.

        ``proposed_acked_through_ingest_sequence`` must not exceed what the server has
        already committed (§CP-07 guard, I02). The caller passes the value it read from the
        last receipt's ``checkpoint_ack``; proposing anything ahead of that is the exact
        counterexample I02 names, so this method refuses a negative value outright and the
        runner never sources the number from its own cursor.
        """
        if reason not in {"empty_page", "end_of_feed", "segment_close"}:
            raise ValueError(
                "ingest.commit_checkpoint reason must be empty_page|end_of_feed|segment_close"
            )
        if proposed_acked_through_ingest_sequence < 0:
            raise ValueError("proposed_acked_through_ingest_sequence must be >= 0")
        body = {
            "checkpoint_only_request": {
                "request_id": new_ulid(),
                "schema_version": CONTRACT_SCHEMA_VERSION,
                "assignment_id": assignment_id,
                "checkpoint_seq": checkpoint_seq,
                "lease_id": lease_id,
                "lease_epoch": lease_epoch,
                "cursor_token": cursor_token,
                "cursor_state": cursor_state,
                "proposed_acked_through_ingest_sequence": (proposed_acked_through_ingest_sequence),
                "reason": reason,
            }
        }
        key = f"{assignment_id}:{checkpoint_seq}"
        return self._post("/v1/ingest/checkpoints", body, idempotency_key=key)

    # ------------------------------------------------------------- health.*

    def get_liveness(self) -> dict[str, Any]:
        """``health.get_liveness`` -- ``public_minimal``, answers even when the DB cannot write."""
        response = self._client.get("/healthz")
        body = response.json()
        return body if isinstance(body, dict) else {}


def token_from_environment(variable: str = "RR_COLLECTOR_TOKEN") -> str:
    """Read the collector token from the environment.

    A helper rather than a default inside :class:`CollectorClient`: a client that silently
    picks up a token from ambient state is one whose authentication is hard to reason about.
    Raises rather than returning an empty string -- an empty bearer is ``UNAUTHORIZED`` at
    the server, several layers away from the missing configuration that caused it.
    """
    token = os.environ.get(variable)
    if not token:
        raise RuntimeError(
            f"{variable} is not set; the collector token lives in a restricted-permission "
            "file on the personal machine (SRC-SPEC §11.2)"
        )
    return token
