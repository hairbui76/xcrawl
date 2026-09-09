"""The analysis worker process loop — `MOD-analysis-worker`, one task at a time.

This is the module that closes gap **G-7b** of `…/packets/WIRING-wave-1.md`: until now the
adapter could refuse correctly and the analysis service could hand out work correctly, but
nothing joined them, so `worker/app/main.py` was a Phase-0 stub that claimed nothing.

The cycle is fixed by `contracts/ports.yaml` and runs in exactly this order::

    analysis.claim_task  ->  analysis.get_task_input  ->  secret.issue_task_credential
                         ->  ai.run_inference_task    ->  analysis.submit_result
                                                      (or  analysis.report_attempt_unknown)

with `analysis.heartbeat` interleaved so a long inference cannot outlive its lease.

Three things shape the code more than anything else:

**The server is reached over HTTP, not by import.** `contracts/modules.yaml` types every
`MOD-analysis-worker -> MOD-analysis-service` edge `transport: http`, and the worker runs on
the Owner's personal machine with no route to the server's SQLite (FE-15). So this module
imports nothing from `server.*`; it speaks to :class:`AnalysisServerPort`, and the tests bind
that port to the real FastAPI app through an in-process client. Binding it by import would
make the tests pass on an edge that does not exist in deployment.

**Nothing is reported that is not known.** Every failure below ends in one of two places: an
operation the contract provides, or a lease that is deliberately allowed to lapse. In
particular `analysis.report_attempt_unknown` is used **only** when the provider may actually
have run, because it writes `cost_uncertain = true` — filing it after a refusal that happened
*before* any provider call would record uncertainty the system does not have. See
:class:`CycleOutcome` for which outcome takes which exit, and `CR-TC-adapter-08` for the
operation the contract is missing.

**The adapters are `enabled: false`.** Both entries in `contracts/ai/providers.yaml` §2.1 are
disabled because isolation is unverified (B13/ADR-0010), so on a real machine today the loop
claims nothing at all — `analysis.claim_task` itself returns `{"task": None, "reason":
"no_enabled_provider"}` rather than handing out work whose only next step is a call the Owner
has not enabled. The loop's disabled-adapter path is still implemented and tested, because
"the provider registry says enabled and the adapter still refuses" is exactly the
disagreement that must not become a fake success.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Final, Protocol

from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.states import AnalysisTaskType

from worker.app.adapter.base import (
    AdapterError,
    AdapterResult,
    SourceRef,
    TaskCredential,
    TaskInput,
)

SCHEMA_VERSION_HEADER: Final[str] = "X-Schema-Version"
REQUEST_ID_HEADER: Final[str] = "X-Request-Id"
IDEMPOTENCY_KEY_HEADER: Final[str] = "Idempotency-Key"

#: `contracts/retry-policy.yaml`. Quoted, never redefined here (RP-05: these are runtime
#: configuration, not compile-time constants) — the loop reads the table and applies it.
CLAIM_IDLE_BACKOFF_SECONDS: Final[tuple[int, ...]] = (5, 15, 45)
PROVIDER_UNAVAILABLE_BACKOFF_SECONDS: Final[tuple[int, ...]] = (60, 300, 900)
PROVIDER_UNAVAILABLE_WAITS: Final[int] = 3
LEASE_TTL_ANALYSIS_SECONDS: Final[int] = 900
HEARTBEAT_INTERVAL_ANALYSIS_SECONDS: Final[int] = 60


class CycleOutcome(str, Enum):
    """How one pass of :meth:`AnalysisWorkerLoop.run_once` ended.

    Every member is a *named* outcome. The point of naming them is that the loop can never
    end a cycle in a way its caller has to infer from an exception type or a log line, and a
    test can assert the exact one rather than "it didn't crash".
    """

    #: The queue was empty, or no provider is enabled. Both are normal answers.
    NO_TASK = "no_task"
    #: `secret.issue_task_credential` refused, or no secret service is wired at all (G-6).
    #: Non-retrying by construction: the loop does not ask a second time for the same task.
    CREDENTIAL_REFUSED = "credential_refused"
    #: The adapter refused to dispatch — `enabled: false`, isolation unverified (B13).
    DISPATCH_REFUSED = "dispatch_refused"
    #: The provider was reachable-in-principle and did not answer. Budgeted separately from
    #: schema retries, because no inference ran (`tasks.yaml` §1 `budgets_cited`).
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    #: The model ran and its output failed the adapter's local schema/semantic check.
    OUTPUT_INVALID = "output_invalid"
    #: The model may have run and the worker cannot say whether it finished.
    ATTEMPT_UNKNOWN = "attempt_unknown"
    #: A result reached `analysis.submit_result` and the server committed it.
    SUBMITTED = "submitted"
    #: The server refused the submission. The attempt is recorded server-side; the worker
    #: does not retry it here — the budget lives at the task layer.
    SUBMIT_REJECTED = "submit_rejected"


@dataclass(frozen=True)
class CycleReport:
    """What one cycle did, in a form a supervisor and a test can both read."""

    outcome: CycleOutcome
    task_id: str | None = None
    attempt_id: str | None = None
    error_code: ErrorCode | None = None
    #: The contract's backoff for this outcome, before jitter. Recorded rather than slept, so
    #: the number a test asserts is the number `retry-policy.yaml` states.
    backoff_seconds: int = 0
    reason: str | None = None
    heartbeats: int = 0

    @property
    def claimed(self) -> bool:
        return self.task_id is not None


class CredentialRefused(Exception):
    """`secret.issue_task_credential` said no, or there is nothing to ask.

    Carries a reason code and never the request that was refused. Separate from
    :class:`~worker.app.adapter.base.AdapterError` because the refusal happens one module
    away — in `MOD-secret-service` — and the worker's job is only to stop.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class HttpResponse(Protocol):
    """The two members of a response this module uses."""

    @property
    def status_code(self) -> int: ...

    def json(self) -> Any: ...


class HttpTransport(Protocol):
    """`httpx.Client` in deployment, an in-process test client in tests.

    Both satisfy this shape, which is why the tests can drive the **real** FastAPI app and
    the real routers without a second code path existing for them.
    """

    def get(self, url: str, *, headers: Mapping[str, str]) -> HttpResponse: ...

    def post(self, url: str, *, json: Any, headers: Mapping[str, str]) -> HttpResponse: ...


class CredentialPort(Protocol):
    """`secret.issue_task_credential` (`contracts/ports.yaml`, `transport: http`).

    `MOD-analysis-worker` is that operation's only caller, which is why the port lives here
    and not in the adapter package: `contracts/modules.yaml` gives `MOD-ai-adapter`
    `outbound_operations: []`, so the worker fetches and the adapter receives.
    """

    def issue_task_credential(
        self, *, task_id: str, attempt_id: str, lease_id: str, lease_epoch: int
    ) -> TaskCredential: ...


class AdapterPort(Protocol):
    """`ai.run_inference_task` (`transport: internal`, same process)."""

    def run_inference_task(
        self, task: TaskInput, *, credential: TaskCredential | None = None
    ) -> AdapterResult: ...


class AbsentSecretService:
    """The state of the world today: `MOD-secret-service` has no code (gap **G-6**).

    This is not a stub that pretends. It refuses every request with a named reason, so the
    loop exercises its real `CREDENTIAL_REFUSED` path instead of a path that only exists in
    tests. When the service lands, it replaces this object and nothing else changes.
    """

    reason: Final[str] = "secret_service_absent"

    def issue_task_credential(
        self, *, task_id: str, attempt_id: str, lease_id: str, lease_epoch: int
    ) -> TaskCredential:
        raise CredentialRefused(self.reason)


class ServerRefusal(Exception):
    """A non-2xx answer from the server, reduced to its contract envelope fields.

    A plain exception rather than a frozen dataclass: Python assigns ``__traceback__`` onto
    the instance as it propagates, which a frozen dataclass refuses — turning every server
    refusal into a `FrozenInstanceError` that hides the refusal it was carrying.
    """

    def __init__(self, *, status_code: int, code: ErrorCode | None, message_safe: str) -> None:
        super().__init__(f"{status_code} {code.value if code else '?'}")
        self.status_code = status_code
        self.code = code
        self.message_safe = message_safe


class AnalysisServerPort:
    """The five `analysis.*` operations a worker may call, over HTTP.

    Every request carries the three wire headers `contracts/http/openapi.yaml` requires, and
    every mutation carries an `Idempotency-Key`: a replay after a lost response must not
    produce a second claim or a second result (SRC-PLAN §5.1). The bearer is the
    `analysis_worker_token`; it is read from the config once and never logged.
    """

    def __init__(
        self,
        transport: HttpTransport,
        *,
        token: str,
        base_url: str = "",
        request_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._transport = transport
        self._token = token
        self._base = base_url.rstrip("/")
        self._request_id = request_id_factory or (lambda: uuid.uuid4().hex)

    # -- wire ---------------------------------------------------------------------------
    def _headers(self, *, idempotency_key: str | None = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self._token}",
            SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION,
            REQUEST_ID_HEADER: self._request_id(),
        }
        if idempotency_key is not None:
            headers[IDEMPOTENCY_KEY_HEADER] = idempotency_key
        return headers

    def _read(self, response: HttpResponse) -> dict[str, Any]:
        if 200 <= response.status_code < 300:
            body = response.json()
            return dict(body) if isinstance(body, dict) else {}
        envelope = response.json() if callable(getattr(response, "json", None)) else {}
        code = None
        if isinstance(envelope, dict) and isinstance(envelope.get("code"), str):
            try:
                code = ErrorCode(envelope["code"])
            except ValueError:  # a code outside the registry is itself the problem
                code = None
        message = ""
        if isinstance(envelope, dict):
            message = str(envelope.get("message_safe") or "")
        raise ServerRefusal(status_code=response.status_code, code=code, message_safe=message)

    # -- operations ---------------------------------------------------------------------
    def claim_task(
        self,
        *,
        worker_instance_id: str,
        task_types: Sequence[str],
        claim_request_id: str,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "worker_instance_id": worker_instance_id,
            "task_types": list(task_types),
        }
        if run_id is not None:
            body["run_id"] = run_id
        return self._read(
            self._transport.post(
                f"{self._base}/v1/analysis/tasks/claim",
                json=body,
                headers=self._headers(idempotency_key=claim_request_id),
            )
        )

    def get_task_input(self, *, task_id: str, lease_id: str, lease_epoch: int) -> dict[str, Any]:
        url = (
            f"{self._base}/v1/analysis/tasks/{task_id}/input"
            f"?lease_id={lease_id}&lease_epoch={lease_epoch}"
        )
        return self._read(self._transport.get(url, headers=self._headers()))

    def heartbeat(self, *, task_id: str, lease_id: str, lease_epoch: int) -> dict[str, Any]:
        return self._read(
            self._transport.post(
                f"{self._base}/v1/analysis/tasks/{task_id}/heartbeat",
                json={"lease_id": lease_id, "lease_epoch": lease_epoch},
                headers=self._headers(),
            )
        )

    def submit_result(
        self,
        *,
        task_id: str,
        lease_id: str,
        lease_epoch: int,
        result: Mapping[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        return self._read(
            self._transport.post(
                f"{self._base}/v1/analysis/tasks/{task_id}/result",
                json={
                    "lease_id": lease_id,
                    "lease_epoch": lease_epoch,
                    "analysis_result": dict(result),
                },
                headers=self._headers(idempotency_key=idempotency_key),
            )
        )

    def report_attempt_unknown(
        self,
        *,
        task_id: str,
        attempt_id: str,
        lease_id: str,
        lease_epoch: int,
        reason: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        return self._read(
            self._transport.post(
                f"{self._base}/v1/analysis/tasks/{task_id}/attempt-unknown",
                json={
                    "lease_id": lease_id,
                    "lease_epoch": lease_epoch,
                    "attempt_id": attempt_id,
                    "reason": reason,
                },
                headers=self._headers(idempotency_key=idempotency_key),
            )
        )


@dataclass
class _Lease:
    """The claim pointers one cycle carries. Nothing here outlives the cycle."""

    task_id: str
    task_type: AnalysisTaskType
    attempt_id: str
    attempt_number: int
    lease_id: str
    lease_epoch: int
    claimed_at: datetime
    last_beat_at: datetime
    heartbeats: int = 0


@dataclass
class AnalysisWorkerLoop:
    """One worker instance. Single task at a time; `max_concurrency` is 1 for CLI (§1).

    `clock` and `sleeper` are injected so the tests can drive a long inference past the
    heartbeat interval without waiting for it, and so the backoff a test asserts is the
    contract's number rather than an elapsed wall clock.
    """

    server: AnalysisServerPort
    adapter: AdapterPort
    worker_instance_id: str
    credentials: CredentialPort = field(default_factory=AbsentSecretService)
    task_types: Sequence[str] = tuple(t.value for t in AnalysisTaskType)
    run_id: str | None = None
    clock: Callable[[], datetime] = lambda: datetime.now(UTC)
    #: Called with a whole-second delay instead of `time.sleep`, so a supervisor can decide
    #: how to wait and a test can assert without waiting at all.
    sleeper: Callable[[int], None] = lambda _seconds: None
    id_factory: Callable[[], str] = lambda: uuid.uuid4().hex
    #: **Vestigial. Leave it ``None``.** It was the seam ``CR-TC-adapter-10`` needed while
    #: ``analysis.get_task_input`` returned no ``analysis_key`` and four of the key's seven
    #: components were underivable by a worker — so building one here would have been
    #: inventing the value SV-01 exists to check. ``PKT-TC-ANALYSIS-FIX4`` closed that: the
    #: response now carries the full seven-component key, computed by the server from the
    #: sources it is about to hand out, and :meth:`_task_input` uses it. The parameter is kept
    #: only because ``tests/integration/test_analysis_once_per_key.py`` passes it explicitly,
    #: and that file belongs to another card; it can go the moment that call drops the keyword.
    analysis_key_resolver: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None
    #: Consecutive empty claims, for the idle backoff ladder.
    _idle_streak: int = field(default=0, init=False)
    #: Consecutive provider-unavailable answers, for its own ladder and its own budget.
    _unavailable_streak: int = field(default=0, init=False)

    # -- one cycle ----------------------------------------------------------------------
    def run_once(self) -> CycleReport:
        """Claim at most one task and take it to a named end.

        Reads top to bottom as the contract's sequence. Every `return` is an outcome that
        the contract has a place for; there is no branch that ends by assuming success.
        """
        claimed = self.server.claim_task(
            worker_instance_id=self.worker_instance_id,
            task_types=self.task_types,
            claim_request_id=self.id_factory(),
            run_id=self.run_id,
        )
        task = claimed.get("task")
        if not isinstance(task, dict):
            self._idle_streak += 1
            return CycleReport(
                outcome=CycleOutcome.NO_TASK,
                backoff_seconds=_ladder(CLAIM_IDLE_BACKOFF_SECONDS, self._idle_streak - 1),
                reason=str(claimed.get("reason") or "queue_empty"),
            )
        self._idle_streak = 0
        lease = _Lease(
            task_id=str(task["task_id"]),
            task_type=AnalysisTaskType(task["task_type"]),
            attempt_id=str(task["attempt_id"]),
            attempt_number=int(task.get("attempt_number", 1)),
            lease_id=str(task["lease_id"]),
            lease_epoch=int(task["lease_epoch"]),
            claimed_at=self.clock(),
            last_beat_at=self.clock(),
        )

        payload = self.server.get_task_input(
            task_id=lease.task_id, lease_id=lease.lease_id, lease_epoch=lease.lease_epoch
        )
        task_input = self._task_input(lease, payload)

        try:
            credential = self.credentials.issue_task_credential(
                task_id=lease.task_id,
                attempt_id=lease.attempt_id,
                lease_id=lease.lease_id,
                lease_epoch=lease.lease_epoch,
            )
        except CredentialRefused as refusal:
            # A named, NON-RETRYING outcome. The loop does not ask again for this task and
            # does not file an unknown attempt: no provider call happened, so there is no
            # uncertainty about cost to record, and `report_attempt_unknown` would write
            # `cost_uncertain = true` — a claim the system cannot support. The lease is
            # left to lapse and the server's own sweep returns the task; there is no
            # worker-side "give it back" operation (`CR-TC-adapter-08`).
            return CycleReport(
                outcome=CycleOutcome.CREDENTIAL_REFUSED,
                task_id=lease.task_id,
                attempt_id=lease.attempt_id,
                reason=refusal.reason,
                backoff_seconds=_ladder(PROVIDER_UNAVAILABLE_BACKOFF_SECONDS, 0),
                heartbeats=lease.heartbeats,
            )

        return self._dispatch(lease, task_input, credential)

    def _dispatch(
        self, lease: _Lease, task_input: TaskInput, credential: TaskCredential
    ) -> CycleReport:
        """Run the adapter, heartbeat around it, and route every failure to its own exit."""
        self._beat_if_due(lease)
        try:
            result = self.adapter.run_inference_task(task_input, credential=credential)
        except AdapterError as error:
            return self._after_adapter_error(lease, error)
        finally:
            self._beat_if_due(lease)

        if self._lease_overrun(lease):
            # The inference outlived the lease. The provider ran and the result cannot be
            # submitted under a dead lease, so what is true is exactly `unknown`.
            return self._file_unknown(lease, reason="inference_outlived_lease")

        try:
            self.server.submit_result(
                task_id=lease.task_id,
                lease_id=lease.lease_id,
                lease_epoch=lease.lease_epoch,
                result=result.payload,
                idempotency_key=lease.attempt_id,
            )
        except ServerRefusal as refusal:
            return CycleReport(
                outcome=CycleOutcome.SUBMIT_REJECTED,
                task_id=lease.task_id,
                attempt_id=lease.attempt_id,
                error_code=refusal.code,
                reason="server_refused_submission",
                heartbeats=lease.heartbeats,
            )
        self._unavailable_streak = 0
        return CycleReport(
            outcome=CycleOutcome.SUBMITTED,
            task_id=lease.task_id,
            attempt_id=lease.attempt_id,
            heartbeats=lease.heartbeats,
        )

    def _after_adapter_error(self, lease: _Lease, error: AdapterError) -> CycleReport:
        """Map an adapter refusal onto the outcome the contract has a place for.

        The split is by **whether the provider ran**, not by how bad the error looks:

        * `CAPABILITY_DENIED` — refused before any transport was touched, so nothing ran;
        * `AI_PROVIDER_UNAVAILABLE` — the call could not start; its own budget
          (`provider_unavailable_waits` = 3) precisely because no inference happened;
        * `AI_OUTPUT_INVALID` — the model **did** run, and a cost may exist;
        * `AI_ATTEMPT_UNCERTAIN` — the only case where the honest record is "unknown".
        """
        if error.code is ErrorCode.AI_ATTEMPT_UNCERTAIN:
            return self._file_unknown(lease, reason="worker_lost_after_provider_call")
        if error.code is ErrorCode.AI_PROVIDER_UNAVAILABLE:
            self._unavailable_streak += 1
            return CycleReport(
                outcome=CycleOutcome.PROVIDER_UNAVAILABLE,
                task_id=lease.task_id,
                attempt_id=lease.attempt_id,
                error_code=error.code,
                reason=str(error.details_safe.get("reason_code") or ""),
                backoff_seconds=_ladder(
                    PROVIDER_UNAVAILABLE_BACKOFF_SECONDS, self._unavailable_streak - 1
                ),
                heartbeats=lease.heartbeats,
            )
        if error.code is ErrorCode.AI_OUTPUT_INVALID:
            # The provider ran. The server is the authority on a rejected result and records
            # it through a failing `analysis.submit_result` — but the adapter's early local
            # check (`tasks.yaml` §4 step 2, "adapter kiểm sớm để tiết kiệm một vòng mạng")
            # means the worker holds no document to submit. `CR-TC-adapter-09`.
            return CycleReport(
                outcome=CycleOutcome.OUTPUT_INVALID,
                task_id=lease.task_id,
                attempt_id=lease.attempt_id,
                error_code=error.code,
                reason=str(error.details_safe.get("validation_failure_kind") or ""),
                heartbeats=lease.heartbeats,
            )
        # CAPABILITY_DENIED and VALIDATION_ERROR: refused before the transport. Nothing ran,
        # so nothing is uncertain; back off on the provider ladder and do not retry the task.
        self._unavailable_streak += 1
        return CycleReport(
            outcome=CycleOutcome.DISPATCH_REFUSED,
            task_id=lease.task_id,
            attempt_id=lease.attempt_id,
            error_code=error.code,
            reason=str(error.details_safe.get("denied_capability_kind") or ""),
            backoff_seconds=_ladder(
                PROVIDER_UNAVAILABLE_BACKOFF_SECONDS, self._unavailable_streak - 1
            ),
            heartbeats=lease.heartbeats,
        )

    def _file_unknown(self, lease: _Lease, *, reason: str) -> CycleReport:
        """`analysis.report_attempt_unknown` — used only when the provider may have run."""
        self.server.report_attempt_unknown(
            task_id=lease.task_id,
            attempt_id=lease.attempt_id,
            lease_id=lease.lease_id,
            lease_epoch=lease.lease_epoch,
            reason=reason,
            idempotency_key=lease.attempt_id,
        )
        return CycleReport(
            outcome=CycleOutcome.ATTEMPT_UNKNOWN,
            task_id=lease.task_id,
            attempt_id=lease.attempt_id,
            error_code=ErrorCode.AI_ATTEMPT_UNCERTAIN,
            reason=reason,
            heartbeats=lease.heartbeats,
        )

    # -- lease upkeep -------------------------------------------------------------------
    def _beat_if_due(self, lease: _Lease) -> None:
        """Heartbeat when the interval has elapsed, and never after the lease has died.

        `heartbeat_interval_analysis` is 60 s inside a `lease_ttl_analysis` of 900 s — fifteen
        beats per TTL. Beating a lease the server has already reclaimed is refused there
        (`STALE_LEASE`); this avoids sending it, but does not rely on avoiding it.
        """
        now = self.clock()
        if self._lease_overrun(lease, now=now):
            return
        if (now - lease.last_beat_at).total_seconds() < HEARTBEAT_INTERVAL_ANALYSIS_SECONDS:
            return
        self.server.heartbeat(
            task_id=lease.task_id, lease_id=lease.lease_id, lease_epoch=lease.lease_epoch
        )
        lease.last_beat_at = now
        lease.heartbeats += 1

    def _lease_overrun(self, lease: _Lease, *, now: datetime | None = None) -> bool:
        moment = now if now is not None else self.clock()
        return moment - lease.claimed_at >= timedelta(seconds=LEASE_TTL_ANALYSIS_SECONDS)

    # -- translation --------------------------------------------------------------------
    def _task_input(self, lease: _Lease, payload: Mapping[str, Any]) -> TaskInput:
        """`analysis.get_task_input`'s response, as the adapter's input type.

        `max_evidence_level` is copied from the server's answer and never recomputed here:
        `contracts/ai/tasks.yaml` §3 makes the **server** the one that derives it from the
        sources actually present, so a worker that computed its own could raise the ceiling
        the model is checked against (SV-04).
        """
        sources = [
            SourceRef(
                source_id=str(row["source_id"]),
                kind=str(row["kind"]),
                text=str(row["text"]),
                source_hash=str(row["source_hash"]),
                retrieved_at=str(row["retrieved_at"]),
            )
            for row in payload.get("sources", [])
        ]
        # The server's key, as of `PKT-TC-ANALYSIS-FIX4`. It is authoritative: the server
        # derives `source_fingerprint` from the sources it is about to serve, which is what
        # `ENT-analysis.source_fingerprint` is defined to be, and SV-01 compares the model's
        # answer against exactly this. An override is only honoured when one is passed.
        key = payload.get("analysis_key") or {}
        if self.analysis_key_resolver is not None:
            key = self.analysis_key_resolver(payload)
        return TaskInput(
            task_id=lease.task_id,
            task_type=lease.task_type,
            analysis_key=dict(key),
            target_key=str((payload.get("target_ref") or {}).get("target_key", "")),
            sources=sources,
            max_evidence_level=str(payload.get("max_evidence_level", "post_only")),
            # Taken from the resolved key when there is one. The fallbacks are the values
            # `contracts/ai/tasks.yaml` §2 states for all three tasks and the `const` of
            # `analysis-result.schema.json`; they are the contract's numbers, not a guess,
            # and SV-07 compares against them either way.
            prompt_version=str(key.get("prompt_version", payload.get("prompt_version", "1.0.0"))),
            schema_version=str(key.get("schema_version", payload.get("schema_version", "0.1.0"))),
            attempt_id=lease.attempt_id,
            attempt_number=lease.attempt_number,
        )

    # -- supervision --------------------------------------------------------------------
    def run_forever(self, *, max_cycles: int | None = None) -> list[CycleReport]:
        """Cycle until `max_cycles`, sleeping the contract's backoff between passes.

        `max_cycles` exists so the process has a bounded mode a test and an operator can
        both use; `None` runs until the caller stops it. The sleep is delegated to
        :attr:`sleeper` so no wall-clock wait is compiled into the loop.
        """
        reports: list[CycleReport] = []
        cycles = 0
        while max_cycles is None or cycles < max_cycles:
            report = self.run_once()
            reports.append(report)
            cycles += 1
            if report.backoff_seconds:
                self.sleeper(report.backoff_seconds)
        return reports

    @property
    def provider_unavailable_budget_left(self) -> int:
        """`provider_unavailable_waits` = 3, counted down. Never mixed with schema retries."""
        return max(0, PROVIDER_UNAVAILABLE_WAITS - self._unavailable_streak)


def _ladder(values: Sequence[int], index: int) -> int:
    """Read a backoff ladder, holding at its last rung.

    `retry-policy.yaml` states each ladder as three numbers with a ceiling; holding at the
    top is the ceiling, not an omission.
    """
    if not values:
        return 0
    return values[min(index, len(values) - 1)]
