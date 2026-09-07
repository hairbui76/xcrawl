"""The mutation guard — the single place a service asks "may I write?".

Call contract for every mutating service (this is the interface ``TC-ingest-idempotent-ack-lost``
and the other Phase 1 cards call)
-----------------------------------------------------------------------------------------------
**Where to get the guard: ``app.state.storage_guard``.** It is set on every construction
path of ``create_app()`` by ``server.app.health.router.install_storage``, so it is always
there -- and it is always the object to use;
do not construct a second :class:`StorageGuard`. The state machine lives in process memory, so
two guards are two disagreeing views of the same disk -- one would refuse writes while the
other still reported ``healthy``, which is the divergence ``I02`` and ``I13`` exist to prevent::

    IngestContext(engine=..., owner_id=..., storage_guard=app.state.storage_guard)

Then, on every mutation::

    guard.assert_writable(OperationId.INGEST_SUBMIT_BATCH)   # raises StorageRefused
    with session_scope(engine) as connection:                # ... then, and only then,
        ...                                                  # the single BEGIN..COMMIT
    return receipt                                           # ACK *after* the commit

Three rules the caller must not reorder, because each of them is an invariant:

1. **Ask before you write.** ``assert_writable`` is called *before* the transaction opens.
   It raises :class:`StorageRefused`; it never returns a falsy value that an ``if`` could
   forget to check.
2. **ACK after commit, never before.** ``I02``. The guard refusing is the only reason a
   caller may report a mutation as not applied; a caller that ACKs and then discovers the
   write failed has already lost the data, because the collector advanced its cursor.
3. **Do not try to persist the refusal.** ``contracts/errors.yaml`` ``EPR-01``: no error
   code needs a new database row to count as reported. The error envelope returned to the
   caller plus the health channel *are* the report (SRC-PLAN §8.4). Writing an
   ``error_log`` row from this path would fail for the same reason the mutation did.

What this module owns
---------------------
* ``storage.get_health`` (``contracts/ports.yaml``, transport ``internal``), including the
  default-deny check on who may call it;
* the refusal surface derived from :data:`server.app.storage.health.REFUSALS`;
* the operator-driven transitions (``enter_maintenance``, ``mark_recovery_required``) and
  the ``reconciliation_complete`` seam that ``TC-backup-restore-drill`` will fill in.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import StorageHealth

from server.app.storage.health import (
    PROBE_INTERVAL_SECONDS,
    StorageHealthMachine,
)

# --------------------------------------------------------------------------------------
# Who may call storage.get_health -- contracts/modules.yaml allowed_edges + default_deny
# --------------------------------------------------------------------------------------

#: The only two callers with an ``allowed_edges`` row for ``storage.get_health``.
STORAGE_GET_HEALTH_CALLERS: frozenset[str] = frozenset({"MOD-health-service", "MOD-job-service"})

#: ``modules[].runtime`` of ``contracts/modules.yaml``, for the modules that appear as the
#: caller of a forbidden edge into ``MOD-data-store`` (FE-01, FE-05, FE-15, FE-18, FE-29).
#: The runtime is what decides *which* refusal code applies -- see :func:`_denial_code`.
MODULE_RUNTIME: dict[str, str] = {
    "MOD-web-ui": "RT-browser",
    "MOD-x-collector": "RT-personal-machine",
    "MOD-analysis-worker": "RT-personal-machine",
    "MOD-ai-adapter": "RT-personal-machine",
    "MOD-telegram-adapter": "RT-server",
    "MOD-health-service": "RT-server",
    "MOD-job-service": "RT-server",
    "MOD-data-store": "RT-server",
}


def _denial_code(caller_module: str) -> ErrorCode:
    """Pick the refusal code for a caller with no edge to ``storage.get_health``.

    The boundary table (card §5, ruling R5-01) draws the line by *mechanism*, not by
    module name:

    * a caller on another runtime physically has no route to the server's SQLite -- the
      platform denies it, so the code is ``CAPABILITY_DENIED``. ``contracts/state/storage.yaml``
      ``HC-03`` says this in as many words for the collector: *"NC-05: CAPABILITY_DENIED,
      không phải UNAUTHORIZED"*. It is not an authentication failure; a perfectly valid
      collector token still may not reach here.
    * a caller inside the server process is an import away, so nothing physical stops it;
      what stops it is the edge registry, and the code is ``FORBIDDEN_EDGE``.

    This reproduces the codes pinned in
    ``acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`` for all five
    forbidden edges into ``MOD-data-store`` (FE-01/05/15/18 ``CAPABILITY_DENIED``,
    FE-29 ``FORBIDDEN_EDGE``) without hard-coding a per-edge table, so a module added to
    the contract later gets the right answer rather than a default one.

    An unknown module is treated as off-runtime (``CAPABILITY_DENIED``): denying harder is
    the safe direction when the registry does not know the caller.
    """
    return (
        ErrorCode.FORBIDDEN_EDGE
        if MODULE_RUNTIME.get(caller_module) == "RT-server"
        else ErrorCode.CAPABILITY_DENIED
    )


# --------------------------------------------------------------------------------------
# Error envelope -- contracts/errors.yaml `error_envelope`
# --------------------------------------------------------------------------------------

_CROCKFORD32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_correlation_id() -> str:
    """A ULID, generated **in process memory**.

    ``error_envelope.correlation_rule_vi`` requires a ``correlation_id`` on every envelope
    *including* when storage is blocked, so this must not read a sequence from the database
    or it would be unavailable exactly when it is needed.
    """
    timestamp = int(time.time() * 1000)
    randomness = int.from_bytes(os.urandom(10), "big")
    value = (timestamp << 80) | randomness
    return "".join(_CROCKFORD32[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


#: ``message_safe_template_vi`` of the four codes this module can raise
#: (``contracts/errors.yaml`` §3). Rendered as-is: the templates carry no substitutions,
#: and the envelope forbids interpolating anything outside ``details_safe_keys``.
MESSAGE_SAFE: dict[ErrorCode, str] = {
    ErrorCode.STORAGE_WRITE_FAILED: (
        "Hệ thống tạm thời không ghi được dữ liệu. Đã dừng nhận việc mới."
    ),
    ErrorCode.RESTORE_UNVERIFIED: (
        "Vừa khôi phục dữ liệu. Việc gửi và giao việc đang tạm khóa cho tới khi đối soát xong."
    ),
    ErrorCode.CAPABILITY_DENIED: "Thao tác bị chặn ở mức nền tảng.",
    ErrorCode.FORBIDDEN_EDGE: "Đường gọi này không được phép.",
    ErrorCode.UNAUTHORIZED: "Không có quyền thực hiện thao tác này.",
}

#: ``details_safe_keys`` of the same four codes. Any key outside this set is dropped before
#: the envelope leaves the process -- the envelope's own rule is that an unknown key is a
#: producer-side ``VALIDATION_ERROR``, so silently leaking it is the worse failure.
DETAILS_SAFE_KEYS: dict[ErrorCode, frozenset[str]] = {
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
    ErrorCode.RESTORE_UNVERIFIED: frozenset(
        {"restore_id", "snapshot_id", "storage_health", "pending_outbox_count"}
    ),
    ErrorCode.CAPABILITY_DENIED: frozenset(
        {"module_id", "denied_capability_kind", "forbidden_edge_ref"}
    ),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"caller_module", "callee_module", "forbidden_edge_ref"}),
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
}


def error_envelope(
    code: ErrorCode,
    *,
    details_safe: dict[str, Any] | None = None,
    correlation_id: str | None = None,
    retry_after_ms: int | None = None,
) -> dict[str, Any]:
    """Build the seven-field envelope of ``contracts/errors.yaml`` ``error_envelope``.

    ``scope`` and ``retry_class`` are read from the generated maps rather than passed in,
    so a caller cannot hand the client a retry policy the contract did not grant.
    """
    permitted = DETAILS_SAFE_KEYS[code]
    filtered = {k: v for k, v in (details_safe or {}).items() if k in permitted}
    return {
        "code": code.value,
        "scope": SCOPE[code],
        "retry_class": RETRY_CLASS[code],
        "message_safe": MESSAGE_SAFE[code],
        "correlation_id": correlation_id or new_correlation_id(),
        "details_safe": filtered or None,
        "retry_after_ms": retry_after_ms,
    }


class StorageRefused(Exception):
    """A storage state refused an operation. Carries the envelope the caller must return.

    Deliberately an exception and not a return value: :meth:`StorageGuard.assert_writable`
    is called on the happy path of every mutation, and a boolean that a caller forgets to
    check would silently ACK an uncommitted write.
    """

    def __init__(self, envelope: dict[str, Any]) -> None:
        super().__init__(f"{envelope['code']}: {envelope['message_safe']}")
        self.envelope = envelope

    @property
    def code(self) -> ErrorCode:
        return ErrorCode(self.envelope["code"])


class StorageGuard:
    """Refusal surface over a :class:`~server.app.storage.health.StorageHealthMachine`.

    One guard per process. It holds no connection and issues no SQL, so every method here
    keeps working while the database does not.
    """

    def __init__(
        self,
        machine: StorageHealthMachine | None = None,
        *,
        reconciliation_check: Callable[[str], bool] | None = None,
    ) -> None:
        """
        :param reconciliation_check: the side-effect-free predicate of
            ``contracts/state/storage.yaml`` §7 ``interface_contract_vi``, owned by
            ``TC-backup-restore-drill``. Until that card lands the default is
            :meth:`_never_reconciled`, which answers ``False`` for every restore -- see
            :meth:`reconciliation_complete`.
        """
        self._machine = machine if machine is not None else StorageHealthMachine()
        self._reconciliation_check = reconciliation_check

    @property
    def machine(self) -> StorageHealthMachine:
        return self._machine

    # -- reads ---------------------------------------------------------------------

    def current_health(self) -> StorageHealth:
        """In-process read of ``storage.health``. No database access, by design."""
        return self._machine.state

    def get_health(self, *, caller_module: str) -> dict[str, Any]:
        """``storage.get_health`` — the ``internal`` port of ``contracts/ports.yaml``.

        :param caller_module: the ``MOD-*`` id of the caller. Required, not defaulted: the
            default-deny rule (``contracts/modules.yaml`` ``default_deny``) cannot be
            enforced against a caller that did not say who it is.
        :raises StorageRefused: ``CAPABILITY_DENIED`` or ``FORBIDDEN_EDGE`` per
            :func:`_denial_code` when the caller has no ``allowed_edges`` row.
        """
        if caller_module not in STORAGE_GET_HEALTH_CALLERS:
            code = _denial_code(caller_module)
            details: dict[str, Any] = (
                {"caller_module": caller_module, "callee_module": "MOD-data-store"}
                if code is ErrorCode.FORBIDDEN_EDGE
                else {"module_id": caller_module, "denied_capability_kind": "process"}
            )
            raise StorageRefused(error_envelope(code, details_safe=details))
        return {
            "storage_health": self._machine.state.value,
            "observed_at": _rfc3339(self._machine.observed_at),
        }

    # -- the guard itself ----------------------------------------------------------

    def assert_writable(self, operation_id: OperationId) -> None:
        """Refuse ``operation_id`` if the current state refuses it. Call before writing.

        :raises StorageRefused: with ``STORAGE_WRITE_FAILED`` while ``write_blocked`` or
            ``maintenance``, and ``RESTORE_UNVERIFIED`` while ``recovery_required``.

        ``retry_after_ms`` is only attached to the retryable code, and its value is the
        probe interval: telling a caller to come back sooner than the next probe would have
        it retry against a state that provably has not been re-evaluated.
        """
        code = self._machine.refusal_for(operation_id)
        if code is None:
            return
        state = self._machine.state
        if code is ErrorCode.STORAGE_WRITE_FAILED:
            raise StorageRefused(
                error_envelope(
                    code,
                    details_safe={
                        "storage_health": state.value,
                        "failed_operation_id": operation_id.value,
                        "observed_at": _rfc3339(self._machine.observed_at),
                    },
                    retry_after_ms=PROBE_INTERVAL_SECONDS * 1000,
                )
            )
        raise StorageRefused(
            error_envelope(
                code,
                details_safe={
                    "storage_health": state.value,
                    "restore_id": self._machine.pending_restore_id,
                },
            )
        )

    # -- state changes driven from outside ------------------------------------------

    def record_write_failure(self) -> str | None:
        """Report that a write failed. ``T-ST-01`` / ``T-ST-07``.

        The caller passes no exception detail on purpose: the state machine's answer does
        not depend on *which* I/O error occurred, and an error string from SQLite is
        exactly the kind of internal detail the envelope forbids echoing outward.
        """
        return self._machine.record_write_failure()

    def record_probe(self, *, success: bool, at: datetime | None = None) -> str | None:
        """Feed one recovery probe result into the machine. ``T-ST-02`` / ``T-ST-08``."""
        return self._machine.record_probe(success=success, at=at)

    def enter_maintenance(self) -> str:
        """Operator opens a maintenance window. ``T-ST-03`` / ``T-ST-09``.

        There is no automatic caller for this and there must not be one
        (``forbidden_transitions`` row 5).
        """
        return self._machine.open_maintenance()

    def leave_maintenance(self, *, snapshot_verified: bool) -> str:
        """``T-ST-04``: close the window once ``backup.verify_snapshot`` has passed."""
        return self._machine.close_maintenance(snapshot_verified=snapshot_verified)

    def mark_recovery_required(self, restore_id: str) -> str:
        """``T-ST-05``: a snapshot was restored, so reconciliation is owed.

        From here the dispatcher and every worker claim are locked until
        :meth:`complete_reconciliation` succeeds. There is no timeout out of this state.
        """
        return self._machine.record_restore(restore_id)

    def reconciliation_complete(self, restore_id: str) -> bool:
        """Has ``restore_id`` been reconciled? ``contracts/state/storage.yaml`` §7.

        **Interface only for now.** The clause list -- revoke every stale lease, decide each
        old outbox entry, verify ``first_announced`` / coverage / Saved against the manifest,
        and get the operator's acknowledgement -- belongs to ``contracts/ops/backup-restore.md``
        and is implemented by ``TC-backup-restore-drill``. Until that card injects a real
        ``reconciliation_check``, this answers ``False`` for every restore.

        ``False`` is the only safe default. Fixture
        ``acceptance/fixtures/recovery/j-restore-verification-incomplete-dispatch-locked.json``
        is the case that proves it: integrity was ``ok`` and every count matched the
        manifest, and reconciliation was still incomplete because two clauses (operator
        review of intent, operator acknowledgement) were not met. A default of ``True``
        would unlock dispatch on exactly that fixture and replay the outbox.
        """
        if self._reconciliation_check is None:
            return False
        return self._reconciliation_check(restore_id)

    def complete_reconciliation(self, restore_id: str) -> str:
        """``T-ST-06`` — the one gate that reopens side effects (``I15``).

        :raises StorageRefused: ``RESTORE_UNVERIFIED`` when
            :meth:`reconciliation_complete` is still ``False``.
        """
        if not self.reconciliation_complete(restore_id):
            raise StorageRefused(
                error_envelope(
                    ErrorCode.RESTORE_UNVERIFIED,
                    details_safe={
                        "restore_id": restore_id,
                        "storage_health": self._machine.state.value,
                    },
                )
            )
        return self._machine.complete_reconciliation(
            restore_id, reconciliation_complete=self.reconciliation_complete
        )


def _rfc3339(moment: datetime) -> str:
    """UTC RFC 3339 with millisecond precision (baseline §3 / AMD-B08)."""
    return moment.isoformat(timespec="milliseconds").replace("+00:00", "Z")
