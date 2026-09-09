"""Runtime configuration, read from the environment exactly once.

Why this file exists
--------------------
Before it, ``RR_DATABASE_URL`` was read by Alembic and **by nothing else** -- the application
never learned where its database was, so the server the Owner started was not connected to
the database the Owner had just migrated (``docs/owner-runbook.md`` gap ``G-2``). This module
is the single place that turns environment into typed values, so there is one answer to
"where does the data live" instead of one per caller.

Rules it follows
----------------
* **No secret is defaulted.** A missing Telegram webhook secret stays ``None``, and the
  adapter then denies every update (``contracts/ops/secrets.md`` §2.4, and the deny-by-default
  behaviour already built into ``TelegramContext``). Inventing a value would turn "not
  configured" into "configured with something guessable".
* **No secret is read from a command line or written to a log.** Bearer tokens are supplied
  as **hashes** (``RR_*_TOKEN_SHA256``), which is the path ``TokenRegistry.from_hashes``
  exists for: the server never has to hold a token to recognise one.
* **Numbers the Owner owns are not invented here.** The schedule slots and the timezone have
  defaults, but they are the Owner-accepted working values of ``OD-20260907-01`` (items 20
  and 4) and they are labelled as such below -- ``REQ-OQ05`` still has to re-measure the
  slots after M0. Everything else that has no safe default has no default.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

#: Owner-accepted working value (OD-20260907-01 item 4; AMD-B08/ADR-0007). Still the Owner's
#: to change: it is stored per deployment, not compiled in.
DEFAULT_TIMEZONE = "Asia/Ho_Chi_Minh"

#: Owner-accepted working values (OD-20260907-01 item 20). REQ-OQ05 re-measures after M0.
DEFAULT_SCHEDULE_SLOTS: tuple[str, ...] = ("08:00", "20:00")

#: Where a default deployment keeps its database and its generated artefacts. Relative to
#: the repository root so a fresh clone works with no configuration at all; `.gitignore`
#: already excludes it.
DEFAULT_DATA_DIR = "var"

DEFAULT_DATABASE_FILENAME = "research-radar.db"

#: The provider catalogue is a *contract* file, not deployment state: it lists which
#: providers exist and under what terms, and the AI worker reads it. The path is settable so
#: a deployment can point at a checked-out contracts tree elsewhere.
DEFAULT_PROVIDER_CONFIG = "contracts/ai/providers.yaml"

REPO_ROOT = Path(__file__).resolve().parents[2]

_SQLITE_PREFIX = "sqlite+pysqlite:///"


def _env(name: str) -> str | None:
    """Read an environment variable, treating blank as absent.

    An empty string is how a shell passes "I meant to unset this"; treating it as a
    configured value produces a database path of ``""`` and a very confusing error much
    later.
    """
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


@dataclass(frozen=True, slots=True)
class Settings:
    """Everything the composition root needs to build the application."""

    #: Filesystem path of the SQLite database (never a URL: SQLAlchemy and Alembic disagree
    #: on prefixes, and one representation avoids a class of "which form is this?" bugs).
    database_path: Path
    data_dir: Path
    timezone_iana: str
    schedule_slots: tuple[str, ...]
    provider_config_path: Path
    telegram_webhook_secret: str | None
    collector_token_sha256: str | None
    analysis_worker_token_sha256: str | None
    backup_operator_token_sha256: str | None
    #: The collector's bearer token **in clear**. Needed because `ingest.submit_batch` and
    #: `ingest.commit_checkpoint` compare the presented token against
    #: `app.state.collector_token` with `hmac.compare_digest`
    #: (`server/app/ingest/router.py`), so the digest above cannot authenticate those two
    #: routes. `CR-TC-COLLECTOR-10`.
    #:
    #: Last in the field list and defaulted, deliberately: this field was added after other
    #: packets were already constructing `Settings` (`tests/integration/test_collector_loop.py`),
    #: and a required field would have broken every one of them for a value that is optional
    #: by nature. Absent stays absent -- the router reads "not configured" as UNAUTHORIZED.
    collector_token: str | None = None
    #: Directory the file-backed secret material store writes to (0700, one 0600 file per
    #: locator). Defaults under the data dir; `RR_SECRET_MATERIAL_DIR` overrides.
    #: The master key itself is deliberately NOT a field here: `server/app/secret/store.py`
    #: owns `RR_SECRET_MASTER_KEY` and its decoding rules, and copying a 32-byte key into a
    #: second dataclass would mean a second object that can leak it.
    secret_material_dir: Path | None = None

    @property
    def database_url(self) -> str:
        """The SQLAlchemy URL form, for callers that need one."""
        return f"{_SQLITE_PREFIX}{self.database_path}"

    @property
    def is_memory_database(self) -> bool:
        """``True`` for the in-memory database, which has no file and no parent directory."""
        return self.database_path == MEMORY_PATH

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_iana)

    def redacted(self) -> dict[str, object]:
        """A summary safe to print or log.

        Secrets are reported as booleans -- their presence is operationally useful and their
        value never is. ``contracts/errors.yaml`` forbids leaking configuration through error
        envelopes; the same discipline applies to a status command.
        """
        return {
            "database_path": str(self.database_path),
            "data_dir": str(self.data_dir),
            "timezone_iana": self.timezone_iana,
            "schedule_slots": list(self.schedule_slots),
            "provider_config_path": str(self.provider_config_path),
            "telegram_webhook_secret_configured": self.telegram_webhook_secret is not None,
            "collector_token_configured": self.collector_token is not None
            or self.collector_token_sha256 is not None,
            "secret_material_dir": str(self.secret_material_dir),
            # Presence only. The key's value never reaches a status line or a log.
            "secret_master_key_configured": bool(os.environ.get("RR_SECRET_MASTER_KEY")),
            "analysis_worker_token_configured": self.analysis_worker_token_sha256 is not None,
            "backup_operator_token_configured": self.backup_operator_token_sha256 is not None,
        }


#: Every SQLAlchemy SQLite URL scheme, longest first so `sqlite+pysqlite` is matched before
#: the bare `sqlite`. SQLAlchemy writes the *path* after three slashes, so what follows a
#: prefix is already `rel/path`, `/abs/path` (the familiar four-slash form) or `:memory:`.
_SQLITE_SCHEMES: tuple[str, ...] = ("sqlite+pysqlite://", "sqlite+aiosqlite://", "sqlite://")

#: SQLite's in-memory database. Not a filesystem path and must never be joined to one.
MEMORY_PATH = Path(":memory:")


def _resolve_database_path(data_dir: Path) -> Path:
    """Turn ``RR_DATABASE_URL`` into the file the engine will actually open.

    Accepts a bare path (what ``server/migrations/env.py`` has always taken) **and** every
    SQLAlchemy SQLite URL form. The previous version stripped only ``sqlite+pysqlite:///``,
    so the most ordinary spelling of all -- ``sqlite:////tmp/x/rr.db``, which is SQLAlchemy's
    own absolute form and is all over its documentation -- fell through to the relative
    branch and was joined onto the working directory. The engine then opened a file
    *literally named* ``sqlite:...`` next to wherever the operator happened to be standing,
    and the database they named was never touched (``CR-P0-10``).

    Where a **relative** path lands, and why it is not the cwd
    ---------------------------------------------------------
    ``contracts/ops/deployment.md`` describes the data store as "file trên volume" -- a file
    on a mounted volume (rows ``RT-server``, ``MOD-data-store``). A relative location is
    therefore a location *within the data volume*, and ``RR_DATA_DIR`` is this repo's name
    for that volume root. Resolving against the cwd instead would mean the same configuration
    opens a different database depending on which directory the shell was in when the process
    started -- which is exactly the class of bug this function just had.

    The one exception is an **explicit** ``./`` or ``../``, which is an operator saying "here,
    where I am standing" in so many words. That also keeps the example
    ``RR_DATABASE_URL=./var/research-radar.db`` printed by ``server/migrations/env.py``
    meaning what it has always meant.
    """
    raw = _env("RR_DATABASE_URL")
    if raw is None:
        return data_dir / DEFAULT_DATABASE_FILENAME

    for scheme in _SQLITE_SCHEMES:
        if raw.startswith(scheme):
            raw = raw[len(scheme) :]
            # `sqlite:///x` -> `/x` after the scheme; the leading slash is the URL's
            # authority separator, not part of the path. `sqlite:////x` -> `//x` -> `/x`.
            raw = raw[1:] if raw.startswith("/") else raw
            break

    if not raw or raw == ":memory:":
        # `sqlite://` and `sqlite:///:memory:` both mean the in-memory database.
        return MEMORY_PATH

    path = Path(raw)
    if path.is_absolute():
        return path
    if raw.startswith(("./", "../")):
        return (Path.cwd() / path).resolve()
    return (data_dir / path).resolve()


def _resolve_dir(name: str, default: str) -> Path:
    raw = _env(name)
    path = Path(raw) if raw is not None else REPO_ROOT / default
    return path if path.is_absolute() else (Path.cwd() / path).resolve()


def _resolve_slots() -> tuple[str, ...]:
    raw = _env("RR_SCHEDULE_SLOTS")
    if raw is None:
        return DEFAULT_SCHEDULE_SLOTS
    slots = tuple(part.strip() for part in raw.split(",") if part.strip())
    if not slots:
        raise ValueError("RR_SCHEDULE_SLOTS is set but lists no slots")
    return slots


def load_settings() -> Settings:
    """Build :class:`Settings` from the current environment.

    Validation that fails here fails at startup, which is the only place a configuration
    error is cheap: an unparsable timezone or slot discovered during a scheduled run would
    surface as a missed run hours later.
    """
    data_dir = _resolve_dir("RR_DATA_DIR", DEFAULT_DATA_DIR)
    timezone_iana = _env("RR_TIMEZONE") or DEFAULT_TIMEZONE
    ZoneInfo(timezone_iana)  # raises now rather than at the first scheduled occurrence

    provider_raw = _env("RR_PROVIDER_CONFIG")
    provider_path = (
        Path(provider_raw) if provider_raw is not None else REPO_ROOT / DEFAULT_PROVIDER_CONFIG
    )

    return Settings(
        database_path=_resolve_database_path(data_dir),
        data_dir=data_dir,
        timezone_iana=timezone_iana,
        schedule_slots=_resolve_slots(),
        provider_config_path=provider_path,
        telegram_webhook_secret=_env("RR_TELEGRAM_WEBHOOK_SECRET"),
        collector_token=_env("RR_COLLECTOR_TOKEN"),
        secret_material_dir=(
            Path(_material_raw)
            if (_material_raw := _env("RR_SECRET_MATERIAL_DIR")) is not None
            else data_dir / "secret-material"
        ),
        collector_token_sha256=_env("RR_COLLECTOR_TOKEN_SHA256"),
        analysis_worker_token_sha256=_env("RR_ANALYSIS_WORKER_TOKEN_SHA256"),
        backup_operator_token_sha256=_env("RR_BACKUP_OPERATOR_TOKEN_SHA256"),
    )


__all__ = [
    "DEFAULT_DATA_DIR",
    "DEFAULT_PROVIDER_CONFIG",
    "DEFAULT_SCHEDULE_SLOTS",
    "DEFAULT_TIMEZONE",
    "REPO_ROOT",
    "Settings",
    "load_settings",
]
