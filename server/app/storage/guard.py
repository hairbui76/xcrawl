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
from typing import TYPE_CHECKING, Any

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from rr_contracts.generated.states import StorageHealth

from server.app.storage.health import (
    PROBE_INTERVAL_SECONDS,
    ForbiddenTransition,
    StorageEvent,
    StorageHealthMachine,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from sqlalchemy import Engine

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


# --------------------------------------------------------------------------------------
# Persistence -- ENT-maintenance-window (AMD-ENT-maintenance-01)
# --------------------------------------------------------------------------------------

#: ``reason`` of ``ENT-maintenance-window``. Closed enum: adding a value is an amendment.
MAINTENANCE_REASONS: frozenset[str] = frozenset(
    {"snapshot", "migration", "restore", "purge_all", "disk_cleanup"}
)


class MaintenanceWindowRequired(ValueError):
    """Raised when a persisted window is opened without the audit fields it must carry.

    ``opened_by`` and ``reason`` are ``NOT NULL`` in the contract, and the entity says why:
    *"Một cửa sổ không có principal thì không chứng minh được hành động explicit"*. So this
    refuses rather than substituting a placeholder principal -- an invented operator name in
    an audit column is worse than a failed call, because it reads as evidence afterwards.
    """


class MaintenanceWindowStore:
    """Reads and writes ``maintenance_window`` for one owner.

    **This is the only persistent part of storage health, and deliberately so.**
    ``contracts/data/entities.yaml`` ``ENT-maintenance-window`` says it in its own
    ``what_it_is_not_vi``:

    * ``write_blocked`` **must not** be persisted (``T-ST-01``,
      ``forbidden_transitions`` row 4) -- it has to come from a write that actually failed
      just now, never from a row read at startup. A stale row saying "blocked" would refuse
      writes on a healthy disk; a stale row saying "healthy" is worse.
    * ``recovery_required`` needs no table of its own: a ``restore_record`` with
      ``dispatcher_unlocked_at IS NULL`` **is** that state on disk already.

    So this store answers exactly one question -- is a maintenance window open, who opened
    it, and why -- and :meth:`load` combines it with ``restore_record`` to reconstruct the
    state a fresh process should start in.

    Every method takes its own short connection. The store is used at process start and at
    operator-driven transitions, never on a hot path, and holding a connection open across
    the life of a guard would keep a read transaction open against a database that other
    processes are writing.
    """

    def __init__(self, engine: Engine, *, owner_id: str) -> None:
        self._engine = engine
        self._owner_id = owner_id

    @property
    def owner_id(self) -> str:
        return self._owner_id

    # -- read ----------------------------------------------------------------------

    def open_window(self) -> dict[str, Any] | None:
        """The single open window (``closed_at IS NULL``), or ``None``.

        ``ux_maintenance_window_open`` makes "single" a database guarantee rather than a
        hope, so this does not have to choose between candidates.
        """
        with self._engine.connect() as connection:
            row = connection.exec_driver_sql(
                "SELECT id, opened_at, opened_by, reason, storage_health_at_open,"
                " restore_record_id"
                " FROM maintenance_window WHERE owner_id = ? AND closed_at IS NULL",
                (self._owner_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "opened_at": row[1],
            "opened_by": row[2],
            "reason": row[3],
            "storage_health_at_open": row[4],
            "restore_record_id": row[5],
        }

    def unreconciled_restore_id(self) -> str | None:
        """The restore whose dispatcher was never unlocked, if any.

        ``server/app/backup/reconcile.py`` is the only writer of ``dispatcher_unlocked_at``,
        and ``restore.py`` inserts the row with it ``NULL``. So NULL means "reconciliation is
        still owed", which is precisely ``recovery_required`` (``I15``, ``NC-10``).
        """
        with self._engine.connect() as connection:
            row = connection.exec_driver_sql(
                "SELECT id FROM restore_record"
                " WHERE owner_id = ? AND dispatcher_unlocked_at IS NULL"
                " ORDER BY restored_at DESC LIMIT 1",
                (self._owner_id,),
            ).fetchone()
        return None if row is None else str(row[0])

    def load(self) -> tuple[StorageHealth, str | None]:
        """The state a process should start in, and the restore it still owes.

        Order matters and is not arbitrary. An unreconciled restore outranks an open window:
        ``T-ST-05`` runs the restore *inside* the window, so both rows can be present at once,
        and of the two ``recovery_required`` is the state that keeps the dispatcher locked.
        Starting in ``maintenance`` instead would refuse less than the contract requires.

        ``write_blocked`` is never returned: it is not persisted, and a process that starts
        while the disk is full learns that from its first failed write, not from a row.
        """
        restore_id = self.unreconciled_restore_id()
        if restore_id is not None:
            return StorageHealth.RECOVERY_REQUIRED, restore_id
        if self.open_window() is not None:
            return StorageHealth.MAINTENANCE, None
        return StorageHealth.HEALTHY, None

    # -- write ---------------------------------------------------------------------

    def open(
        self,
        *,
        window_id: str,
        opened_at: str,
        opened_by: str,
        reason: str,
        storage_health_at_open: StorageHealth,
    ) -> str:
        """Insert the row ``T-ST-03``/``T-ST-09`` say the transition writes."""
        if reason not in MAINTENANCE_REASONS:
            raise MaintenanceWindowRequired(
                f"reason {reason!r} is not one of {sorted(MAINTENANCE_REASONS)}"
            )
        with self._engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO maintenance_window (id, owner_id, opened_at, opened_by, reason,"
                " storage_health_at_open, closed_at, closed_by, snapshot_verified_at,"
                " restore_record_id)"
                " VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL)",
                (
                    window_id,
                    self._owner_id,
                    opened_at,
                    opened_by,
                    reason,
                    storage_health_at_open.value,
                ),
            )
        return window_id

    def close(
        self, *, window_id: str, closed_at: str, closed_by: str, snapshot_verified_at: str | None
    ) -> None:
        """Record the end of the window (``T-ST-04``)."""
        with self._engine.begin() as connection:
            connection.exec_driver_sql(
                "UPDATE maintenance_window"
                " SET closed_at = ?, closed_by = ?, snapshot_verified_at = ?"
                " WHERE owner_id = ? AND id = ? AND closed_at IS NULL",
                (closed_at, closed_by, snapshot_verified_at, self._owner_id, window_id),
            )

    def link_restore_record(self, *, window_id: str, restore_record_id: str) -> None:
        """Point the open window at the restore that ran inside it.

        Separate from :meth:`open` because of write ordering, not taste:
        ``server/app/backup/restore.py`` calls ``guard.mark_recovery_required(restore_id)``
        **before** it inserts the ``restore_record`` row, and ``restore_record_id`` is a
        foreign key -- writing it at mark time would reference a row that does not exist yet.
        The backup card calls this after its INSERT commits. Until it does the column stays
        NULL, which the contract permits.
        """
        with self._engine.begin() as connection:
            connection.exec_driver_sql(
                "UPDATE maintenance_window SET restore_record_id = ?"
                " WHERE owner_id = ? AND id = ?",
                (restore_record_id, self._owner_id, window_id),
            )


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
        store: MaintenanceWindowStore | None = None,
    ) -> None:
        """
        :param reconciliation_check: the side-effect-free predicate of
            ``contracts/state/storage.yaml`` §7 ``interface_contract_vi``, owned by
            ``TC-backup-restore-drill``. Absent, :meth:`reconciliation_complete` answers
            ``False`` for every restore, so the gate stays shut.
        :param store: persistence for the maintenance window. **Optional on purpose.**
            Without it the guard behaves exactly as it always has -- everything in process
            memory -- which is what every unit-level caller wants and what the in-process
            tests of a dozen other cards rely on. With it, ``maintenance`` and
            ``recovery_required`` survive the process, which is what gap ``G-3`` needed:
            ``backup_cli maintenance --open`` in one invocation and ``restore`` in the next
            are two processes, and before this the second could not see the first's window.

            When ``machine`` is also given it wins: an explicitly constructed machine is a
            caller stating the state, and silently overwriting it from disk would make the
            parameter a lie. Use :meth:`from_engine` for the normal path.
        """
        self._machine = machine if machine is not None else StorageHealthMachine()
        self._reconciliation_check = reconciliation_check
        self._store = store
        self._window_id: str | None = None
        if store is not None and machine is None:
            state, restore_id = store.load()
            self._machine = StorageHealthMachine(initial=state, pending_restore_id=restore_id)
            window = store.open_window()
            self._window_id = None if window is None else str(window["id"])

    @classmethod
    def from_engine(
        cls,
        engine: Engine,
        *,
        owner_id: str,
        reconciliation_check: Callable[[str], bool] | None = None,
    ) -> StorageGuard:
        """A guard whose maintenance window survives this process.

        This is the constructor a CLI or a deployment wants; the bare ``StorageGuard()``
        remains the right one for a test that is asserting the state machine itself.
        """
        return cls(
            reconciliation_check=reconciliation_check,
            store=MaintenanceWindowStore(engine, owner_id=owner_id),
        )

    @property
    def window_id(self) -> str | None:
        """The open window's id, when this guard is persisted and a window is open."""
        return self._window_id

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

    def enter_maintenance(
        self,
        *,
        reason: str | None = None,
        opened_by: str | None = None,
    ) -> str:
        """Operator opens a maintenance window. ``T-ST-03`` / ``T-ST-09``.

        There is no automatic caller for this and there must not be one
        (``forbidden_transitions`` row 5).

        :param reason: one of :data:`MAINTENANCE_REASONS`. Required when this guard
            persists; the column is ``NOT NULL``.
        :param opened_by: the ``backup_operator`` principal. Required when this guard
            persists, for the same reason -- and it is not defaulted, because a fabricated
            principal in an audit column reads as evidence later.
        :raises MaintenanceWindowRequired: persisted guard, missing ``reason``/``opened_by``.
        """
        # Validated before the machine moves, so a refused call leaves memory and disk
        # agreeing. Memory and disk disagreeing is the exact failure this packet fixes.
        if self._store is not None and (reason is None or opened_by is None):
            raise MaintenanceWindowRequired(
                "a persisted guard needs reason= and opened_by= to open a window "
                "(ENT-maintenance-window: both columns are NOT NULL)"
            )
        health_at_open = self._machine.state
        transition = self._machine.open_maintenance()
        if self._store is None:
            return transition
        assert reason is not None and opened_by is not None  # noqa: S101 - narrowed above
        self._window_id = self._store.open(
            window_id=new_correlation_id(),
            opened_at=_rfc3339(self._machine.observed_at),
            opened_by=opened_by,
            reason=reason,
            storage_health_at_open=health_at_open,
        )
        return transition

    def leave_maintenance(
        self,
        *,
        snapshot_verified: bool,
        closed_by: str | None = None,
        write_path_recovered: bool = False,
    ) -> str:
        """``T-ST-04``: close the window once ``backup.verify_snapshot`` has passed.

        :param write_path_recovered: only consulted for a window opened from
            ``write_blocked`` (``T-ST-09``). That transition's ``forbidden_vi`` is *"Dùng
            đường này để lách sang `healthy`"* -- closing must not launder an unresolved disk
            failure into a healthy store. In one process the probe streak enforced that;
            across processes it could not, which is why ``storage_health_at_open`` is a
            column. The caller asserts here that the write path actually came back, and
            ``False`` refuses.

            No new transition is introduced for the refusal: ``contracts/state/storage.yaml``
            declares nine and this is not a tenth, it is ``T-ST-04`` being guarded.
        :raises ForbiddenTransition: verify has not passed, or the window came from
            ``write_blocked`` and the write path is not asserted recovered.
        :raises MaintenanceWindowRequired: persisted guard without ``closed_by``.
        """
        window = self._store.open_window() if self._store is not None else None
        if (
            window is not None
            and window["storage_health_at_open"] == (StorageHealth.WRITE_BLOCKED.value)
            and not write_path_recovered
        ):
            raise ForbiddenTransition(
                self._machine.state,
                StorageEvent.MAINTENANCE_WINDOW_CLOSED,
                "T-ST-09 forbids closing a window opened from write_blocked back into "
                "healthy while the write failure is unresolved",
            )
        if window is not None and closed_by is None:
            raise MaintenanceWindowRequired(
                "a persisted guard needs closed_by= to close a window "
                "(ck_maintenance_window_closed_by)"
            )
        transition = self._machine.close_maintenance(snapshot_verified=snapshot_verified)
        if self._store is None:
            return transition
        if window is None:
            # Nothing on disk to close: the guard was constructed around an explicit
            # machine, or another process closed the window first.
            self._window_id = None
            return transition
        assert closed_by is not None  # noqa: S101 - narrowed above
        closed_at = _rfc3339(self._machine.observed_at)
        self._store.close(
            window_id=str(window["id"]),
            closed_at=closed_at,
            closed_by=closed_by,
            # `ck_maintenance_window_verify_before_close` only binds a `snapshot` window;
            # the guard has already refused an unverified close above, so the column is a
            # record of when verify passed rather than a second gate.
            snapshot_verified_at=(
                closed_at if window["reason"] == "snapshot" and snapshot_verified else None
            ),
        )
        self._window_id = None
        return transition

    def link_restore_record(self, restore_record_id: str) -> None:
        """Attach the restore that ran inside the open window (``ENT-maintenance-window``).

        Called by ``TC-backup-restore-drill`` **after** its ``restore_record`` INSERT
        commits, because the column is a foreign key and
        ``restore.py`` calls :meth:`mark_recovery_required` before that INSERT. A no-op on a
        guard with no store or no open window.
        """
        if self._store is None or self._window_id is None:
            return
        self._store.link_restore_record(
            window_id=self._window_id, restore_record_id=restore_record_id
        )

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
