"""``MOD-health-service`` — the health channel that does not depend on the database.

``contracts/state/storage.yaml`` ``independent_health_channel`` (HC-01..HC-04) makes this
a contract obligation rather than an implementation nicety: when SQLite cannot be written
-- or cannot be read -- these endpoints are the only way the failure gets reported at all
(``contracts/errors.yaml`` ``EPR-01``).
"""

from server.app.health.router import (
    OwnerSessionRequired,
    StorageReadinessProvider,
    build_health_router,
    install_health_error_handler,
    install_storage,
    owner_session_absent,
)

__all__ = [
    "OwnerSessionRequired",
    "StorageReadinessProvider",
    "build_health_router",
    "install_health_error_handler",
    "install_storage",
    "owner_session_absent",
]
