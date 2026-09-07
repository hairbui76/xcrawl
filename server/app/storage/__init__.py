"""Storage health and the mutation guard (``MOD-data-store``).

Two modules, deliberately split by who depends on them:

``health``
    the ``storage.health`` state machine of ``contracts/state/storage.yaml``
    (``T-ST-01``..``T-ST-09``). Pure, in-memory, no I/O.
``guard``
    the refusal surface every mutating service calls *before* it ACKs anything, plus
    the ``storage.get_health`` port.

Nothing here writes to the database. That is the point: ``contracts/state/storage.yaml``
``T-ST-01`` says the ``write_blocked`` fact lives in **process memory**, because writing
"cannot write" into a database that cannot be written is a contradiction (SRC-PLAN §8.4).
"""

from server.app.storage.guard import (
    StorageGuard,
    StorageRefused,
    error_envelope,
)
from server.app.storage.health import (
    PROBE_CONSECUTIVE_SUCCESS,
    PROBE_INTERVAL_SECONDS,
    TRANSITIONS,
    ForbiddenTransition,
    StorageEvent,
    StorageHealthMachine,
)

__all__ = [
    "PROBE_CONSECUTIVE_SUCCESS",
    "PROBE_INTERVAL_SECONDS",
    "TRANSITIONS",
    "ForbiddenTransition",
    "StorageEvent",
    "StorageGuard",
    "StorageHealthMachine",
    "StorageRefused",
    "error_envelope",
]
