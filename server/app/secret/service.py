"""``MOD-secret-service``: the three ``secret.*`` operations, and the ISO-05 gate.

======================================  =========================================
``secret.store_provider_key``           :func:`store_provider_key`   (internal)
``secret.issue_task_credential``        :func:`issue_task_credential` (worker token)
``secret.revoke_task_credential``       :func:`revoke_task_credential` (internal)
======================================  =========================================

The one rule the rest of the file serves
----------------------------------------
``ADR-0010`` §1 / ``B13``: a worker receives **one** credential, for **one** provider, for
**one** task it currently holds the lease on, for ``lease_ttl_analysis`` seconds. Everything
else here is a consequence:

* the lease is not checked *here*. ``MOD-analysis-service`` owns leases, so
  :func:`issue_task_credential` asks :func:`server.app.analysis.service.verify_task_lease`
  and lets its ``STALE_LEASE`` / ``WORKER_LEASE_EXPIRED`` propagate. A second implementation
  of "does this worker hold the lease" is a second thing to get wrong;
* the check and the insert are in **one** transaction (``TXN-issue-credential``). The card's
  §6 says why: a lease that expires between a check and an insert must not produce a
  credential, and it cannot if there is no gap to expire in;
* there is no argument that widens the scope. No ``provider`` parameter, no "all", no retry
  branch that falls back to another provider's key;
* the CLI/ACP path is refused outright. ``secrets.md`` §5.1: that path receives nothing from
  the server, so a call asking for a credential for it is a contract violation, not a
  provisioning gap.

What never leaves this module
-----------------------------
A plaintext value. :func:`issue_task_credential` returns one -- that is its entire job -- and
the only other read is the idempotency comparison inside :func:`store_provider_key`. Nothing
is logged, no error message quotes a value, and every string bound for
``secret_audit.outcome_detail_safe`` goes through :func:`server.app.secret.store.redact`
first (``SEC-P6``: mask before the write, not before the display).
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine

from server.app.secret.repository import (
    SecretAuditRow,
    SecretRefRow,
    SecretRepository,
    TaskCredentialRow,
    format_timestamp,
    new_ulid,
    parse_timestamp,
)
from server.app.secret.store import (
    MasterKeyUnavailable,
    SecretMaterialMissing,
    SecretStore,
    SecretValue,
    redact,
)

MODULE_ID = "MOD-secret-service"

#: ``secrets.md`` §5: ``task_credential_ttl`` = 900 s, "bằng ``lease_ttl_analysis``". Not a
#: knob: a credential outliving the right to work is the hole the number exists to close.
TASK_CREDENTIAL_TTL_SECONDS = 900

#: ``ENT-secret-ref.purpose``.
PURPOSE_AI_PROVIDER_KEY = "ai_provider_key"
PURPOSE_COLLECTOR_TOKEN = "collector_token"
PURPOSE_TELEGRAM_BOT_TOKEN = "telegram_bot_token"
PURPOSES = frozenset({PURPOSE_AI_PROVIDER_KEY, PURPOSE_COLLECTOR_TOKEN, PURPOSE_TELEGRAM_BOT_TOKEN})

HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.STALE_LEASE: 409,
    ErrorCode.WORKER_LEASE_EXPIRED: 412,
    ErrorCode.AI_PROVIDER_UNAVAILABLE: 503,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}

#: Same registry discipline as ``server/app/analysis/service.py``: an envelope may carry only
#: the keys ``contracts/errors.yaml`` grants that code. A key not listed here cannot be set.
DETAILS_SAFE_KEYS: dict[ErrorCode, frozenset[str]] = {
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
    ErrorCode.CSRF_REJECTED: frozenset({"operation_id"}),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"caller_module", "callee_module", "forbidden_edge_ref"}),
    ErrorCode.NOT_FOUND: frozenset({"operation_id", "resource_kind"}),
    ErrorCode.IDEMPOTENCY_CONFLICT: frozenset(
        {"idempotency_key", "payload_hash_seen", "payload_hash_stored"}
    ),
    ErrorCode.STALE_LEASE: frozenset({"job_id", "lease_epoch_seen", "lease_epoch_current"}),
    ErrorCode.WORKER_LEASE_EXPIRED: frozenset(
        {"job_id", "lease_epoch_seen", "lease_epoch_current", "expired_at"}
    ),
    ErrorCode.AI_PROVIDER_UNAVAILABLE: frozenset(
        {"task_id", "provider_name", "reason_code", "attempt_number", "retry_after_ms"}
    ),
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
    ErrorCode.INTERNAL: frozenset({"correlation_id", "operation_id"}),
}


class SecretError(Exception):
    """A contract error code plus the safe envelope fields it may be reported with.

    It cannot hold a secret value: every constructor argument is a code, a category or an id,
    and ``details_safe`` is checked against the per-code allowlist above. That is a structural
    guarantee rather than a review convention -- there is no field to put a key in.
    """

    def __init__(
        self,
        code: ErrorCode,
        message_safe: str,
        *,
        details_safe: Mapping[str, Any] | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        super().__init__(f"{code.value}: {message_safe}")
        self.code = code
        self.message_safe = message_safe
        self.details_safe: dict[str, Any] | None = (
            None if details_safe is None else dict(details_safe)
        )
        self.retry_after_ms = retry_after_ms
        unknown = set(self.details_safe or {}) - DETAILS_SAFE_KEYS[code]
        if unknown:
            raise ValueError(f"{code.value} may not carry details keys {sorted(unknown)}")

    @property
    def http_status(self) -> int:
        return HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe,
            "retry_after_ms": self.retry_after_ms,
        }


class SecretDependencyUnavailable(Exception):
    """A port this operation needs is not wired. Surfaces as ``INTERNAL``, never as a 4xx.

    A deployment with no master key configured lands here rather than telling the worker it is
    unauthorised: blaming the caller for an operator gap makes a negative test pass for the
    wrong reason.
    """


# --------------------------------------------------------------------------------- ports


@dataclass(frozen=True)
class TaskCredentialScope:
    """What the lease owner says may be issued for one attempt.

    Structurally identical to ``server.app.analysis.service.TaskCredentialScope``; declared
    here so this module depends on the *shape* the port returns rather than on an import that
    would break when the analysis package is absent.
    """

    task_id: str
    attempt_id: str
    task_type: str
    provider_name: str
    model_name: str
    auth_family: str


class LeaseVerifierPort(Protocol):
    """``MOD-analysis-service``'s answer to "does this worker hold this task's lease?".

    Satisfied by :func:`server.app.analysis.service.verify_task_lease` bound to its context --
    see :class:`AnalysisLeaseVerifier`. Refusals arrive as exceptions carrying an
    ``ErrorCode``; this module re-raises them unchanged rather than re-deciding.
    """

    def verify(
        self,
        *,
        task_id: str,
        attempt_id: str,
        lease_id: str,
        lease_epoch: int,
        worker_identity: str,
    ) -> TaskCredentialScope: ...


class ProviderSecretPort(Protocol):
    """``MOD-settings-service``'s read-only view of ``provider_config`` for one task type."""

    def secret_ref_for_task(self, task_type: str) -> ProviderSecretBinding | None: ...


@dataclass(frozen=True)
class ProviderSecretBinding:
    """The provider row a task type resolves to, minus anything secret."""

    provider_config_id: str
    provider_name: str
    model_name: str
    auth_family: str
    enabled: bool
    secret_ref_id: str | None


class StorageGuardPort(Protocol):
    """The write gate from ``server.app.storage.guard.StorageGuard``."""

    def assert_writable(self, operation_id: OperationId) -> None: ...

    def record_write_failure(self) -> str | None: ...


@dataclass
class SecretContext:
    """Everything an operation needs, injected rather than imported.

    ``store`` is optional on purpose: a deployment with no master key configured still runs
    (``REQ-D51`` -- no key is mandatory), and every operation that needs one refuses with
    ``INTERNAL`` rather than pretending to have stored something.
    """

    engine: Engine
    owner_id: str
    store: SecretStore | None = None
    repository: SecretRepository = field(default_factory=SecretRepository)
    leases: LeaseVerifierPort | None = None
    providers: ProviderSecretPort | None = None
    storage_guard: StorageGuardPort | None = None
    clock: Any = None
    id_factory: Any = None
    credential_ttl_seconds: int = TASK_CREDENTIAL_TTL_SECONDS

    def now(self) -> datetime:
        return datetime.now(UTC) if self.clock is None else self.clock()

    def new_id(self) -> str:
        return new_ulid() if self.id_factory is None else self.id_factory()


class AnalysisLeaseVerifier:
    """Adapts ``server.app.analysis.service.verify_task_lease`` to :class:`LeaseVerifierPort`.

    The import is local to the call so that this module is importable in a deployment where
    the analysis package is not installed; the failure then is a wiring error at call time,
    not an ``ImportError`` at start-up.
    """

    def __init__(self, analysis_context: Any) -> None:
        self._context = analysis_context

    def verify(
        self,
        *,
        task_id: str,
        attempt_id: str,
        lease_id: str,
        lease_epoch: int,
        worker_identity: str,
    ) -> TaskCredentialScope:
        from server.app.analysis.service import AnalysisError, verify_task_lease

        try:
            scope = verify_task_lease(
                self._context,
                task_id=task_id,
                attempt_id=attempt_id,
                lease_id=lease_id,
                lease_epoch=lease_epoch,
                worker_identity=worker_identity,
            )
        except AnalysisError as exc:
            # Translated, not re-decided: same code, same safe details, same meaning. The
            # refusal is ``MOD-analysis-service``'s answer; this module only carries it across
            # the module boundary so the worker sees one error envelope shape.
            raise SecretError(
                exc.code,
                exc.message_safe,
                details_safe=exc.details_safe,
                retry_after_ms=exc.retry_after_ms,
            ) from exc
        return TaskCredentialScope(
            task_id=scope.task_id,
            attempt_id=scope.attempt_id,
            task_type=scope.task_type,
            provider_name=scope.provider_name,
            model_name=scope.model_name,
            auth_family=scope.auth_family,
        )


# ------------------------------------------------------------------------------- results


@dataclass(frozen=True)
class StoredKeyReference:
    """What ``secret.store_provider_key`` returns: a reference and a state. Never a value."""

    secret_ref_id: str
    purpose: str
    store_locator: str
    state: str
    created_at: str
    rotated_previous: bool


@dataclass(frozen=True)
class IssuedCredential:
    """One credential for one task. ``value`` is a :class:`SecretValue`, not a ``str``."""

    credential_id: str
    value: SecretValue
    provider_config_id: str
    provider_name: str
    model_name: str
    task_id: str
    attempt_id: str
    expires_at: str
    reused: bool


# ------------------------------------------------------------------------------- helpers


def _validation(message: str, **details: Any) -> SecretError:
    return SecretError(ErrorCode.VALIDATION_ERROR, message, details_safe=details)


def _not_found(resource_kind: str, operation: OperationId) -> SecretError:
    return SecretError(
        ErrorCode.NOT_FOUND,
        "Không tìm thấy tài nguyên yêu cầu.",
        details_safe={"operation_id": operation.value, "resource_kind": resource_kind},
    )


def _assert_writable(ctx: SecretContext, operation: OperationId) -> None:
    if ctx.storage_guard is not None:
        ctx.storage_guard.assert_writable(operation)


def _require_store(ctx: SecretContext) -> SecretStore:
    if ctx.store is None:
        raise SecretDependencyUnavailable(
            "no secret store is configured (contracts/ops/secrets.md §4.1)"
        )
    return ctx.store


def _locator(purpose: str, provider_id: str, key_version: int) -> str:
    """A deterministic locator, which is what makes the write idempotent.

    ``ports.yaml`` keys ``secret.store_provider_key`` on ``provider_id + key_version`` but
    ``ENT-secret-ref`` has no column for either, and adding one is a contract change. Encoding
    both into ``store_locator`` -- the field whose declared job is "định vị trong secret
    store" -- keeps the idempotency key inside the row the contract already defines. The
    locator is not secret: it names a slot, and the slot's contents are the envelope.
    """
    slug = re.sub(r"[^A-Za-z0-9]+", "-", provider_id).strip("-").lower()[:60] or "provider"
    return f"{purpose}--{slug}--v{key_version}"


def _fingerprint(value: str) -> str:
    """A salted-by-purpose digest used only to compare two writes of the same version.

    Not stored, not returned, not logged: it exists for the length of one ``==`` so that a
    repeat write of the same version with a *different* key is ``IDEMPOTENCY_CONFLICT``
    instead of a silent overwrite.
    """
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- secret.store_provider_key


def store_provider_key(
    ctx: SecretContext,
    *,
    provider_id: str,
    value: str,
    key_version: int = 1,
    purpose: str = PURPOSE_AI_PROVIDER_KEY,
    actor_module: str = "MOD-settings-service",
) -> StoredKeyReference:
    """Encrypt a key into the store and return its reference (``secrets.md`` §4.1).

    The value arrives from ``MOD-settings-service`` (``transport: internal``) and leaves as a
    reference. Re-storing the **same** version with the same value is a no-op that returns the
    existing reference; with a different value it is ``IDEMPOTENCY_CONFLICT``. A *new* version
    rotates: the old ``secret_ref`` becomes ``rotated`` and is kept, per ``secrets.md`` §3's
    overlap rule and because an audit trail whose subject was deleted is not one.
    """
    if purpose not in PURPOSES:
        raise _validation(
            "Mục đích secret không hợp lệ.",
            operation_id=OperationId.SECRET_STORE_PROVIDER_KEY.value,
            field_path="purpose",
            violation_kind="enum_value_unknown",
        )
    if not value or not value.strip():
        raise _validation(
            "Giá trị secret rỗng.",
            operation_id=OperationId.SECRET_STORE_PROVIDER_KEY.value,
            field_path="value",
            violation_kind="required_field_missing",
        )
    if key_version < 1:
        raise _validation(
            "key_version phải >= 1.",
            operation_id=OperationId.SECRET_STORE_PROVIDER_KEY.value,
            field_path="key_version",
            violation_kind="value_out_of_range",
        )

    store = _require_store(ctx)
    _assert_writable(ctx, OperationId.SECRET_STORE_PROVIDER_KEY)
    locator = _locator(purpose, provider_id, key_version)
    now = format_timestamp(ctx.now())

    with ctx.engine.begin() as connection:
        existing_same_slot = _ref_by_locator(ctx, connection, locator)
        if existing_same_slot is not None:
            # Same provider, same version: the contract says no second row. Compare before
            # returning, so that a *different* key under the same version is a conflict rather
            # than a silent overwrite of the one the operator thinks is live.
            try:
                stored = store.reveal(locator=locator, purpose=purpose)
            except SecretMaterialMissing:
                stored = None
            if stored is not None and _fingerprint(stored.reveal()) != _fingerprint(value):
                raise SecretError(
                    ErrorCode.IDEMPOTENCY_CONFLICT,
                    "Cùng provider và key_version nhưng giá trị khác.",
                    details_safe={
                        "idempotency_key": f"{provider_id}+{key_version}",
                        "payload_hash_seen": _fingerprint(value)[:16],
                        "payload_hash_stored": _fingerprint(stored.reveal())[:16],
                    },
                )
            return StoredKeyReference(
                secret_ref_id=existing_same_slot.id,
                purpose=purpose,
                store_locator=locator,
                state=existing_same_slot.state,
                created_at=existing_same_slot.created_at,
                rotated_previous=False,
            )

        previous = ctx.repository.active_secret_ref(
            connection, owner_id=ctx.owner_id, purpose=purpose
        )
        rotated = False
        if previous is not None:
            ctx.repository.mark_secret_ref_rotated(
                connection, secret_ref_id=previous.id, rotated_at=now
            )
            rotated = True

        # The material is written before the pointer row: a crash between the two leaves an
        # orphan blob (harmless, unreferenced) rather than a `secret_ref` pointing at nothing.
        store.store(locator=locator, purpose=purpose, value=value)
        row = SecretRefRow(
            id=ctx.new_id(),
            owner_id=ctx.owner_id,
            purpose=purpose,
            store_locator=locator,
            created_at=now,
            rotated_at=None,
            state="active",
        )
        ctx.repository.insert_secret_ref(connection, row)
        _audit(
            ctx,
            connection,
            action="rotated" if rotated else "issued",
            secret_ref_id=row.id,
            actor_module=actor_module,
            at=now,
            detail=f"stored provider key for {provider_id} v{key_version}",
            known_secret=value,
        )

    return StoredKeyReference(
        secret_ref_id=row.id,
        purpose=purpose,
        store_locator=locator,
        state="active",
        created_at=now,
        rotated_previous=rotated,
    )


def _slot_taken(
    ctx: SecretContext, connection: Any, assignment_id: str, secret_ref_id: str
) -> bool:
    """Whether ``(assignment, secret_ref)`` already holds a credential row, live or not."""
    existing = ctx.repository.credentials_for_assignment(
        connection, owner_id=ctx.owner_id, assignment_id=assignment_id
    )
    return any(row.secret_ref_id == secret_ref_id for row in existing)


def _ref_by_locator(ctx: SecretContext, connection: Any, locator: str) -> SecretRefRow | None:
    from sqlalchemy import text

    row = (
        connection.execute(
            text(
                "SELECT id, owner_id, purpose, store_locator, created_at, rotated_at, state "
                "FROM secret_ref WHERE owner_id = :owner_id AND store_locator = :locator"
            ),
            {"owner_id": ctx.owner_id, "locator": locator},
        )
        .mappings()
        .first()
    )
    return None if row is None else SecretRefRow(**dict(row))


# ------------------------------------------------------------- secret.issue_task_credential


def issue_task_credential(
    ctx: SecretContext,
    *,
    task_id: str,
    attempt_id: str,
    lease_id: str,
    lease_epoch: int,
    worker_identity: str,
    assignment_id: str,
) -> IssuedCredential:
    """Issue one short-lived credential for one task -- or refuse (ISO-05).

    Order matters and is the point:

    1. **lease first**, through ``MOD-analysis-service``. A worker that does not hold the
       current lease is refused here, before any row is written and before any key is read.
       ``providers.yaml`` §4 names this negative case by id;
    2. the provider the *task* resolves to -- not one the caller names. There is no parameter
       by which a worker asks for a different provider's key;
    3. ``cli_acp`` is refused: ``secrets.md`` §5.1 gives that path no server secret at all;
    4. replay: an unexpired credential for this (assignment, secret_ref) is returned again,
       so ``task_id + attempt_id`` yields one credential, not a new one per retry;
    5. insert + audit inside the **same** transaction the lease was verified in.
    """
    if ctx.leases is None:
        raise SecretDependencyUnavailable("no lease verifier is wired for ISO-05")
    store = _require_store(ctx)

    # 1. ISO-05. Raises STALE_LEASE / WORKER_LEASE_EXPIRED / AI_PROVIDER_UNAVAILABLE from the
    #    module that owns leases. Nothing below runs for a worker that does not hold one.
    scope = ctx.leases.verify(
        task_id=task_id,
        attempt_id=attempt_id,
        lease_id=lease_id,
        lease_epoch=lease_epoch,
        worker_identity=worker_identity,
    )

    # 3. The zero-API-key path asks for nothing and receives nothing (secrets.md §5.1).
    if scope.auth_family == "cli_acp":
        raise _validation(
            "Đường CLI/ACP không nhận credential từ server.",
            operation_id=OperationId.SECRET_ISSUE_TASK_CREDENTIAL.value,
            field_path="task.auth_family",
            violation_kind="cli_acp_receives_no_server_secret",
        )

    if ctx.providers is None:
        raise SecretDependencyUnavailable("no provider_config view is wired")
    binding = ctx.providers.secret_ref_for_task(scope.task_type)
    if binding is None or binding.secret_ref_id is None:
        raise _not_found("secret_ref", OperationId.SECRET_ISSUE_TASK_CREDENTIAL)
    if not binding.enabled:
        # Belt and braces: `verify_task_lease` already refuses a disabled provider. Repeated
        # here because "the other module checks it" is how a gate quietly stops being checked.
        raise SecretError(
            ErrorCode.AI_PROVIDER_UNAVAILABLE,
            "Provider cho task này chưa được bật.",
            details_safe={
                "task_id": scope.task_id,
                "provider_name": binding.provider_name,
                "reason_code": "isolation_unverified",
            },
        )

    _assert_writable(ctx, OperationId.SECRET_ISSUE_TASK_CREDENTIAL)
    now = ctx.now()
    now_text = format_timestamp(now)
    expires_text = format_timestamp(now + timedelta(seconds=ctx.credential_ttl_seconds))

    with ctx.engine.begin() as connection:
        secret_ref = ctx.repository.secret_ref_by_id(connection, binding.secret_ref_id)
        if secret_ref is None or secret_ref.state == "revoked":
            raise _not_found("secret_ref", OperationId.SECRET_ISSUE_TASK_CREDENTIAL)
        if not ctx.repository.assignment_exists(connection, assignment_id=assignment_id):
            raise _not_found("assignment", OperationId.SECRET_ISSUE_TASK_CREDENTIAL)

        # 4. Replay: same attempt, same live credential.
        live = ctx.repository.live_credential(
            connection,
            owner_id=ctx.owner_id,
            assignment_id=assignment_id,
            secret_ref_id=secret_ref.id,
            now=now_text,
        )
        if live is None and _slot_taken(ctx, connection, assignment_id, secret_ref.id):
            # `ux_task_credential_assignment` is UNIQUE on (owner, assignment, secret_ref) and
            # `ENT-task-credential` states the guarantee in words: "Một task nhận tối đa một
            # credential cho một secret". So a slot whose credential has been revoked (or has
            # expired) is spent -- there is no live credential to return and the contract
            # forbids minting a second one. Refusing is the only remaining answer, and it is a
            # refusal the worker can act on: obtain a new assignment.
            #
            # The contract does not say which code this is (it never contemplates a re-issue
            # after revocation), so `NOT_FOUND` is chosen from the operation's declared list as
            # the one that describes the state truthfully -- there is no credential here for
            # you -- rather than blaming the lease, which may still be perfectly current.
            # Reported as `CR-TC-SECRET-07`.
            raise _not_found("task_credential", OperationId.SECRET_ISSUE_TASK_CREDENTIAL)
        reused = live is not None
        credential_row = live or TaskCredentialRow(
            id=ctx.new_id(),
            owner_id=ctx.owner_id,
            assignment_id=assignment_id,
            secret_ref_id=secret_ref.id,
            issued_to_worker_identity=worker_identity,
            issued_at=now_text,
            expires_at=expires_text,
            revoked_at=None,
        )
        if not reused:
            ctx.repository.insert_task_credential(connection, credential_row)

        try:
            value = store.reveal(locator=secret_ref.store_locator, purpose=secret_ref.purpose)
        except (SecretMaterialMissing, MasterKeyUnavailable) as exc:
            # The pointer exists but the material does not (a restored database without its
            # secrets is the realistic case -- see the store's module docstring). Refusing as
            # NOT_FOUND keeps the transaction from committing a credential nobody can use.
            raise _not_found("secret_material", OperationId.SECRET_ISSUE_TASK_CREDENTIAL) from exc

        # 5. Audit in the same transaction as the insert: never one without the other.
        _audit(
            ctx,
            connection,
            action="issued",
            secret_ref_id=secret_ref.id,
            actor_module="MOD-analysis-worker",
            at=now_text,
            detail=(
                f"task={scope.task_id} attempt={scope.attempt_id} "
                f"provider={binding.provider_name} reused={reused}"
            ),
            known_secret=value.reveal(),
        )

    return IssuedCredential(
        credential_id=credential_row.id,
        value=value,
        provider_config_id=binding.provider_config_id,
        provider_name=binding.provider_name,
        model_name=binding.model_name,
        task_id=scope.task_id,
        attempt_id=scope.attempt_id,
        expires_at=credential_row.expires_at,
        reused=reused,
    )


# ------------------------------------------------------------ secret.revoke_task_credential


def revoke_task_credential(
    ctx: SecretContext,
    *,
    assignment_id: str,
    reason: str,
    task_id: str | None = None,
    attempt_id: str | None = None,
    actor_module: str = "MOD-analysis-service",
) -> int:
    """Invalidate every live credential of an assignment. Idempotent (``ports.yaml``).

    Called at ``analysis.submit_result``, ``analysis.report_attempt_unknown``, on lease expiry,
    on run cancellation, and when the owner revokes a provider (``secrets.md`` §5). A second
    call changes nothing and still returns cleanly: "thu hồi lại không đổi trạng thái".
    """
    _assert_writable(ctx, OperationId.SECRET_REVOKE_TASK_CREDENTIAL)
    now = format_timestamp(ctx.now())
    with ctx.engine.begin() as connection:
        revoked = ctx.repository.revoke_credentials(
            connection, owner_id=ctx.owner_id, assignment_id=assignment_id, revoked_at=now
        )
        if revoked:
            _audit(
                ctx,
                connection,
                action="revoked",
                secret_ref_id=None,
                actor_module=actor_module,
                at=now,
                detail=f"assignment={assignment_id} task={task_id} attempt={attempt_id} "
                f"reason={reason} revoked={revoked}",
                known_secret=None,
            )
    return revoked


def expire_credentials(ctx: SecretContext, *, assignment_id: str) -> int:
    """Convenience for the lease sweeper: revoke with the fixed reason ``lease_expired``."""
    return revoke_task_credential(
        ctx, assignment_id=assignment_id, reason="lease_expired", actor_module=MODULE_ID
    )


# --------------------------------------------------------------------------------- audit


def record_denial(
    ctx: SecretContext,
    *,
    actor_module: str,
    detail: str,
    secret_ref_id: str | None = None,
) -> None:
    """``secret_audit.action = 'denied'`` -- ``secrets.md`` §8 logs every refusal too.

    Written in its own transaction because the refusal path has no other transaction to join,
    and a refusal that is not recorded is indistinguishable from one that never happened.
    """
    now = format_timestamp(ctx.now())
    with ctx.engine.begin() as connection:
        _audit(
            ctx,
            connection,
            action="denied",
            secret_ref_id=secret_ref_id,
            actor_module=actor_module,
            at=now,
            detail=detail,
            known_secret=None,
        )


def _audit(
    ctx: SecretContext,
    connection: Any,
    *,
    action: str,
    secret_ref_id: str | None,
    actor_module: str,
    at: str,
    detail: str,
    known_secret: str | None,
) -> None:
    """Mask, then write. Never the other way round (``SEC-P6``, ``secrets.md`` §4.3)."""
    safe = redact(detail, *(known_secret,) if known_secret else ())
    ctx.repository.insert_audit(
        connection,
        SecretAuditRow(
            id=ctx.new_id(),
            owner_id=ctx.owner_id,
            action=action,
            secret_ref_id=secret_ref_id,
            actor_module=actor_module,
            at=at,
            outcome_detail_safe=safe[:500],
        ),
    )


def credential_is_live(row: TaskCredentialRow, *, now: datetime) -> bool:
    """Whether a stored credential may still be used. Used by tests and by the sweeper."""
    return row.revoked_at is None and parse_timestamp(row.expires_at) > now


__all__ = [
    "MODULE_ID",
    "PURPOSES",
    "PURPOSE_AI_PROVIDER_KEY",
    "PURPOSE_COLLECTOR_TOKEN",
    "PURPOSE_TELEGRAM_BOT_TOKEN",
    "TASK_CREDENTIAL_TTL_SECONDS",
    "AnalysisLeaseVerifier",
    "IssuedCredential",
    "LeaseVerifierPort",
    "ProviderSecretBinding",
    "ProviderSecretPort",
    "SecretContext",
    "SecretDependencyUnavailable",
    "SecretError",
    "StorageGuardPort",
    "StoredKeyReference",
    "TaskCredentialScope",
    "credential_is_live",
    "expire_credentials",
    "issue_task_credential",
    "record_denial",
    "revoke_task_credential",
    "store_provider_key",
]
