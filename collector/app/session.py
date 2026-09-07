"""The collector's Chrome session: the project's own profile, never the Owner's default one.

``REQ-D09`` (answered by the Owner in ``OD-20260907-01`` item 1) says the collector drives a
real Chrome with a **profile belonging to the project**. This module holds that rule and the
capability payload derived from it. It deliberately does **not** import Playwright and does
not launch a browser: this repo never runs ``playwright install``, browsers are an
Owner-machine step, and every live assertion about X belongs to ``TC-x-feasibility-probe``
behind gate SP1 (``contracts/ops/collector-probe.md`` §0, §6).

Why the default profile is refused rather than discouraged
----------------------------------------------------------
A default profile carries the Owner's own logged-in identity and every other site's
cookies. Driving it would put the Owner's whole browsing identity behind an automated
process and make "what did the collector touch" unanswerable. So
:func:`is_default_profile_dir` is a hard guard: a default-looking ``user_data_dir`` raises
:class:`ProfileRefused` carrying ``CAPABILITY_DENIED`` -- the code the R5-01 boundary table
assigns to "actor lacks a process/filesystem/tool capability" (card §5).

``x_session_state`` and the rule that ``unknown`` is never ``ok``
-----------------------------------------------------------------
``contracts/schemas/worker-assignment.schema.json`` ``collector_capabilities`` allows
``ok | challenge | expired | unknown``, and the server only assigns work when the collector
claims ``ok`` (``assignment.capability_requirements.requires_x_session_ok``). ``unknown``
means "not observed", and this module never promotes it to ``ok``: an unobserved session
reported as healthy is how a run gets handed to a collector that is about to hit a
challenge.

``embedding_supported`` is a constant ``False``
-----------------------------------------------
``B12``/``D50``: embedding never runs on the personal machine. The schema pins the field to
``const: false`` and the server rejects a registration claiming otherwise with
``VALIDATION_ERROR``. It is written here as a literal with no way to override it, because a
configurable "do not do this" is not a guard.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePath
from typing import Any

from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode


class XSessionState(str, Enum):
    """``collector_capabilities.x_session_state`` (worker-assignment.schema.json)."""

    OK = "ok"
    CHALLENGE = "challenge"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


class ProfileRefused(Exception):
    """The configured Chrome profile is not one this collector may drive.

    Carries ``CAPABILITY_DENIED`` from the generated registry rather than a bare message,
    so the caller branches on the same code the boundary table names.
    """

    def __init__(self, message_safe: str, *, user_data_dir: PurePath) -> None:
        super().__init__(message_safe)
        self.code = ErrorCode.CAPABILITY_DENIED
        self.scope = SCOPE[ErrorCode.CAPABILITY_DENIED]
        self.retry_class = RETRY_CLASS[ErrorCode.CAPABILITY_DENIED]
        self.message_safe = message_safe
        #: The *name* of the offending directory only. The full path is a
        #: personal-machine absolute path, which the error envelope forbids
        #: (``contracts/errors.yaml`` §error_envelope.forbidden_content_vi).
        self.details_safe = {"profile_dir_name": user_data_dir.name}


#: Directory suffixes of the platform default Chrome/Chromium user-data directories.
#: Matched against the tail of the resolved path so a home directory never has to be
#: guessed, and so the check works the same on a test's ``tmp_path``.
_DEFAULT_PROFILE_SUFFIXES: tuple[tuple[str, ...], ...] = (
    # Linux
    (".config", "google-chrome"),
    (".config", "chromium"),
    (".config", "google-chrome-beta"),
    # macOS
    ("Application Support", "Google", "Chrome"),
    ("Application Support", "Chromium"),
    # Windows
    ("Google", "Chrome", "User Data"),
    ("Chromium", "User Data"),
)


def is_default_profile_dir(user_data_dir: PurePath) -> bool:
    """True when the path is (or sits inside) a platform default Chrome user-data dir."""
    parts = tuple(PurePath(os.path.normpath(str(user_data_dir))).parts)
    for suffix in _DEFAULT_PROFILE_SUFFIXES:
        window = len(suffix)
        for start in range(0, len(parts) - window + 1):
            if tuple(parts[start : start + window]) == suffix:
                return True
    return False


@dataclass(frozen=True)
class ChromeProfile:
    """A Chrome profile the collector is allowed to drive.

    :param user_data_dir: the profile root. Validated on construction.
    :param ready: whether the profile exists and is usable
        (``capabilities.chrome_profile_ready``). ``False`` means the server will not assign
        work, which is the correct outcome -- not something to paper over.
    """

    user_data_dir: Path
    ready: bool = False

    def __post_init__(self) -> None:
        if is_default_profile_dir(self.user_data_dir):
            raise ProfileRefused(
                "Hồ sơ Chrome mặc định của máy không được dùng cho collector; "
                "cần một hồ sơ riêng của dự án (REQ-D09).",
                user_data_dir=self.user_data_dir,
            )


@dataclass(frozen=True)
class CollectorSession:
    """One collector installation: its identity, its profile and its observed X session.

    This object is the single place the capability payload is built, so that
    ``embedding_supported`` cannot be set from anywhere and ``unknown`` cannot be rounded up
    to ``ok``.
    """

    worker_instance_id: str
    profile: ChromeProfile
    collector_version: str = "0.1.0"
    x_session_state: XSessionState = XSessionState.UNKNOWN

    @property
    def collector_online(self) -> bool:
        """What this process can honestly say about itself: it is running.

        Note that the *displayed* "collector online" state is computed by the server from
        heartbeats (``contracts/ops/deployment.md``), not from this claim.
        """
        return True

    def capabilities(self) -> dict[str, Any]:
        """``collector_capabilities`` exactly as the schema defines it."""
        return {
            "collector_online": self.collector_online,
            "chrome_profile_ready": self.profile.ready,
            "x_session_state": self.x_session_state.value,
            "embedding_supported": False,
            "collector_version": self.collector_version,
        }

    def registration_payload(self, registration_seq: int) -> dict[str, Any]:
        """The body of ``worker.register_capabilities``.

        Registration grants no lease -- ``g-schedule-due-claim`` asserts
        ``lease_granted: false`` explicitly, and I10 is the reason. Work only ever arrives
        through ``worker.claim_assignment``.
        """
        capabilities = self.capabilities()
        capabilities.pop("collector_version", None)
        return {
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "worker_instance_id": self.worker_instance_id,
            "worker_kind": "collector",
            "registration_seq": registration_seq,
            "collector_version": self.collector_version,
            "capabilities": capabilities,
        }

    def may_claim(self) -> bool:
        """Whether this collector meets ``capability_requirements`` for a collecting phase.

        Both conditions come from the assignment schema: ``requires_chrome_profile`` and
        ``requires_x_session_ok`` are ``const: true``. A collector that claims while it
        knows its session is in ``challenge`` would be asking the server for work it cannot
        do, and I10 forbids working around a challenge rather than reporting it.
        """
        return self.profile.ready and self.x_session_state is XSessionState.OK

    def observing(self, state: XSessionState) -> CollectorSession:
        """Return a session carrying a newly *observed* X session state."""
        return CollectorSession(
            worker_instance_id=self.worker_instance_id,
            profile=self.profile,
            collector_version=self.collector_version,
            x_session_state=state,
        )
