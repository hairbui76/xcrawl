"""The collector process loop: register, claim, collect, report, repeat.

This is the piece that turns the modules of ``TC-collector-checkpoint-resume`` into a
process. Everything it does is already decided somewhere else — ``worker.*`` on
``MOD-job-service``, ``ingest.*`` on ``MOD-ingest-service``, the stop vocabulary in
``contracts/ports.yaml``, the budgets in ``contracts/retry-policy.yaml`` — so this module
contains sequencing and refusals, not policy.

One cycle
---------
``register_capabilities`` (once per process, and again whenever the declared capabilities
change) → ``claim_assignment`` → drive :class:`~collector.app.reader.SegmentRunner`, which
reads through the :class:`~collector.app.reader.XSource` port, batches, submits and either
reports a stop or closes the feed → release the lease. Then back to the top, or idle.

The three refusals that give the loop its shape
-----------------------------------------------
**It never claims work it cannot do.** ``worker-assignment.schema.json`` marks
``requires_chrome_profile`` and ``requires_x_session_ok`` as ``const: true``, so a collector
whose session is in ``challenge`` or whose profile is not ready has nothing to gain by
asking. :meth:`CollectorLoop.run_forever` stops with
:attr:`LoopExitReason.SESSION_NEEDS_OWNER` instead — the state that only a person, at the
Chrome window, can change (T-RUN-10's guard).

**It never resumes a run that is waiting for a person.** After a ``challenge_required`` or
``session_expired`` stop the run is in ``needs_user`` (T-RUN-09) and I10 forbids the worker
resuming by itself. Two independent things enforce that here: the loop stops claiming, and
the server answers ``no_work`` with ``reason: run_needs_user`` if anything asks anyway. The
second is the real guarantee; the first is politeness that also makes the first guarantee
observable in a test.

**It never treats "nothing to do" as a failure.** ``no_work`` is a 200 carrying a
``retry_after_ms`` from ``claim_idle_backoff`` (5 s, 15 s, 45 s). The loop honours the
server's number rather than its own (I13: empty is not failure).

What this module still cannot do
--------------------------------
There is no live :class:`~collector.app.reader.XSource` in this repository. Driving a real
Chrome belongs to ``TC-x-feasibility-probe`` behind gate SP1
(``contracts/ops/collector-probe.md`` §6), and the source is therefore injected. Tests pass a
recorded one; a real deployment cannot pass anything yet, and
:mod:`collector.app.main` refuses to start rather than pretending otherwise.
"""

from __future__ import annotations

import os
import stat
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from rr_contracts.generated.errors import ErrorCode

from collector.app.batcher import MAX_ITEMS_PER_BATCH
from collector.app.client import CollectorClient, ServerError, WireStopReason, new_ulid
from collector.app.reader import (
    Completion,
    SegmentOutcome,
    SegmentRunner,
    XSource,
    requires_owner_action,
)
from collector.app.session import ChromeProfile, CollectorSession, ProfileRefused, XSessionState

#: ``contracts/retry-policy.yaml §budgets.claim_idle_backoff`` -- 5 s, 15 s, then 45 s and
#: hold. The server sends its own ``retry_after_ms`` with every ``no_work``; these are the
#: fallback for a response that omitted it.
CLAIM_IDLE_BACKOFF_S: tuple[int, ...] = (5, 15, 45)

#: Environment variable names. ``RR_COLLECTOR_TOKEN_FILE`` is the one
#: ``contracts/ops/secrets.md`` §3 actually describes -- a ``0600`` file in the user's config
#: directory, never in the repo. ``RR_COLLECTOR_TOKEN`` is accepted because the packet names
#: it, and because a process manager that injects secrets as environment variables is a real
#: deployment shape; the file is preferred when both are present.
ENV_SERVER_URL = "RR_SERVER_URL"
ENV_TOKEN = "RR_COLLECTOR_TOKEN"
ENV_TOKEN_FILE = "RR_COLLECTOR_TOKEN_FILE"
ENV_CHROME_PROFILE = "RR_CHROME_PROFILE_DIR"
ENV_WORKER_ID = "RR_COLLECTOR_WORKER_ID"


class ConfigError(RuntimeError):
    """Configuration is missing or unsafe, with the reason named.

    :param reason: a stable machine-readable token (``missing_server_url``,
        ``token_file_permissions_too_open``, …) so a test can assert *which* refusal
        happened rather than matching prose, and so an operator sees the same token in the
        message and in the documentation.
    """

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class CollectorConfig:
    """Everything the process needs to start, and nothing it can guess.

    There are no defaults for the server URL, the token or the profile directory. A default
    for any of them would let the collector start pointed somewhere nobody chose — at the
    wrong server, with no credential, or driving the Owner's own Chrome profile, which
    REQ-D09 forbids outright.
    """

    server_url: str
    token: str
    profile: ChromeProfile
    worker_instance_id: str

    @property
    def redacted(self) -> dict[str, Any]:
        """A description safe to log or print: the token is never included."""
        return {
            "server_url": self.server_url,
            "chrome_profile_dir_name": self.profile.user_data_dir.name,
            "chrome_profile_ready": self.profile.ready,
            "worker_instance_id": self.worker_instance_id,
            "token": "<redacted>",
        }


def _read_token_file(path: Path) -> str:
    """Read the token from a ``0600`` file, refusing anything more permissive.

    ``contracts/ops/secrets.md`` §3: "Worker **từ chối khởi động** nếu quyền rộng hơn `0600`
    — một cảnh báo im lặng là vô dụng." So this raises; it does not warn and continue.
    """
    if not path.is_file():
        raise ConfigError(
            "token_file_missing",
            f"{ENV_TOKEN_FILE} points at {path.name}, which is not a readable file",
        )
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise ConfigError(
            "token_file_permissions_too_open",
            f"{path.name} has mode {mode:04o}; contracts/ops/secrets.md §3 requires 0600 "
            "(owner read/write only). Fix with: chmod 600 <file>",
        )
    token = path.read_text(encoding="utf-8").strip()
    if not token:
        raise ConfigError("token_file_empty", f"{path.name} is empty")
    return token


def load_config(env: Mapping[str, str] | None = None) -> CollectorConfig:
    """Build the configuration from the environment, or raise :class:`ConfigError`.

    Every failure names its reason. "Refuses to start" is only useful if the operator is
    told which of five things is wrong, and a collector that starts with half a
    configuration is worse than one that does not start at all: it registers, claims work,
    and fails in the middle of a run.
    """
    source = os.environ if env is None else env

    server_url = (source.get(ENV_SERVER_URL) or "").strip()
    if not server_url:
        raise ConfigError(
            "missing_server_url",
            f"{ENV_SERVER_URL} is not set; the collector has no default server address",
        )
    if not server_url.startswith(("http://", "https://")):
        raise ConfigError(
            "server_url_not_absolute",
            f"{ENV_SERVER_URL} must be an absolute http(s) URL",
        )

    token_file = (source.get(ENV_TOKEN_FILE) or "").strip()
    token = (source.get(ENV_TOKEN) or "").strip()
    if token_file:
        token = _read_token_file(Path(token_file))
    elif not token:
        raise ConfigError(
            "missing_collector_token",
            f"neither {ENV_TOKEN_FILE} nor {ENV_TOKEN} is set. The contract's shape is a "
            "0600 file in the user's config directory (contracts/ops/secrets.md §3), never "
            "a value committed to the repository",
        )

    profile_dir = (source.get(ENV_CHROME_PROFILE) or "").strip()
    if not profile_dir:
        raise ConfigError(
            "missing_chrome_profile_dir",
            f"{ENV_CHROME_PROFILE} is not set; REQ-D09 requires the project's own Chrome "
            "profile and there is no safe default (the machine default is forbidden)",
        )
    path = Path(profile_dir)
    try:
        profile = ChromeProfile(user_data_dir=path, ready=path.is_dir())
    except ProfileRefused as refused:
        raise ConfigError("chrome_profile_is_the_machine_default", str(refused)) from refused

    worker_id = (source.get(ENV_WORKER_ID) or "").strip() or new_ulid()
    return CollectorConfig(
        server_url=server_url,
        token=token,
        profile=profile,
        worker_instance_id=worker_id,
    )


class CycleKind(str, Enum):
    """What one pass of the loop turned out to be."""

    #: The server had nothing to give. Not an error (I13).
    NO_WORK = "no_work"
    #: An assignment was claimed and a segment ran.
    SEGMENT = "segment"


@dataclass(frozen=True)
class CycleResult:
    """One pass of the loop, as data a test can assert on."""

    kind: CycleKind
    no_work_reason: str | None = None
    retry_after_ms: int | None = None
    assignment_id: str | None = None
    outcome: SegmentOutcome | None = None
    released: bool = False


class LoopExitReason(str, Enum):
    """Why :meth:`CollectorLoop.run_forever` returned. Every one of these is deliberate."""

    #: The caller's cycle budget ran out (``--max-cycles``, or one pass in a test).
    CYCLE_BUDGET = "cycle_budget"
    #: The X session needs a person: a challenge, an expiry, or a profile that is not ready.
    #: The loop stops claiming; only the Owner, in the Chrome window, can change this.
    SESSION_NEEDS_OWNER = "session_needs_owner"
    #: The run is blocked and needs a person (source blocked, or the feed layout changed).
    RUN_NEEDS_OWNER = "run_needs_owner"
    #: The server refused the credential. Retrying with the same token cannot help.
    UNAUTHORIZED = "unauthorized"


@dataclass(frozen=True)
class LoopExit:
    """The result of :meth:`CollectorLoop.run_forever`."""

    reason: LoopExitReason
    cycles: tuple[CycleResult, ...] = ()
    detail: str = ""


@dataclass
class CollectorLoop:
    """The collector process, minus the process.

    :param client: the HTTP client. Constructed by the caller so a test can hand it a
        transport that reaches the real application in-process.
    :param source: the X source port. There is no live implementation in this repository.
    :param source_factory: called once per claimed assignment when the source must be built
        per segment; when absent, ``source`` is reused.
    :param clock: UTC ``datetime`` supplier, used for ``collected_at`` on items.
    :param monotonic: budget and heartbeat clock, separate from ``clock`` so a wall-clock
        adjustment cannot lengthen or shorten a segment.
    :param sleep: injected so idle backoff is measurable without waiting.
    """

    config: CollectorConfig
    client: CollectorClient
    source: XSource
    clock: Callable[[], datetime] = lambda: datetime.now(UTC)
    monotonic: Callable[[], float] = field(default_factory=lambda: __import__("time").monotonic)
    sleep: Callable[[float], None] = field(default_factory=lambda: __import__("time").sleep)
    batch_size: int = MAX_ITEMS_PER_BATCH
    session: CollectorSession = field(init=False)
    _registration_seq: int = field(default=0, init=False)
    _idle_streak: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.session = CollectorSession(
            worker_instance_id=self.config.worker_instance_id,
            profile=self.config.profile,
            x_session_state=XSessionState.UNKNOWN,
        )

    # ------------------------------------------------------------------ helpers

    def _timestamp(self) -> str:
        """RFC 3339 UTC with the millisecond precision ``AMD-B08`` requires."""
        moment = self.clock().astimezone(UTC)
        return f"{moment.strftime('%Y-%m-%dT%H:%M:%S')}.{moment.microsecond // 1000:03d}Z"

    def register(self) -> dict[str, Any]:
        """Send ``worker.register_capabilities``. Grants no lease, and is not work (LM-01).

        Called at startup and again after the observed session state changes, because that
        is what the server uses to decide whether this collector is eligible for an
        assignment at all.
        """
        self._registration_seq += 1
        return self.client.register_capabilities(
            self.session.registration_payload(self._registration_seq)
        )

    def observe_session(self, state: XSessionState) -> None:
        """Record an observed X session state and tell the server about it.

        ``unknown`` is never promoted to ``ok`` here or anywhere else (CAP-P5); this only
        ever records what was actually seen.
        """
        if state is self.session.x_session_state:
            return
        self.session = self.session.observing(state)
        self.register()

    # ------------------------------------------------------------------ one cycle

    def run_cycle(self) -> CycleResult:
        """Claim once and, if work came back, run one segment to its stop.

        The claim key is minted per cycle and reused if the claim has to be repeated:
        ``contracts/ports.yaml`` guarantees "cùng claim_request_id trả cùng assignment; không
        cấp hai lease", so a repeated ask is safe and a fresh key is the one way to end up
        holding two leases.
        """
        answer = self.client.claim_assignment(
            claim_request_id=f"claim-{new_ulid()}",
            worker_instance_id=self.config.worker_instance_id,
            capabilities=self.session.capabilities(),
        )
        no_work = answer.get("no_work")
        if isinstance(no_work, dict):
            self._idle_streak += 1
            retry_after = no_work.get("retry_after_ms")
            return CycleResult(
                kind=CycleKind.NO_WORK,
                no_work_reason=str(no_work.get("reason", "")),
                retry_after_ms=int(retry_after) if retry_after is not None else None,
            )

        assignment = answer.get("assignment")
        if not isinstance(assignment, dict):
            raise ServerError(
                ErrorCode.INTERNAL,
                message_safe="Phản hồi claim_assignment không phải assignment hay no_work.",
            )

        self._idle_streak = 0
        runner = SegmentRunner(
            client=self.client,
            source=self.source,
            assignment=assignment,
            clock=self._timestamp,
            monotonic=self.monotonic,
            batch_size=self.batch_size,
        )
        outcome = runner.run_segment()

        if outcome.x_session_state is not self.session.x_session_state:
            # Observed on the source, so it is a real observation, not an assumption.
            self.session = self.session.observing(outcome.x_session_state)

        released = self._release(assignment, outcome)
        return CycleResult(
            kind=CycleKind.SEGMENT,
            assignment_id=str(assignment["assignment_id"]),
            outcome=outcome,
            released=released,
        )

    def _release(self, assignment: Mapping[str, Any], outcome: SegmentOutcome) -> bool:
        """Hand the lease back, except when it is already gone.

        Skipped for :attr:`Completion.LEASE_LOST`: the epoch has moved on, so a release
        carrying the old one is refused with ``STALE_LEASE`` and the server's sweep
        (T-RUN-14) already owns that transition. Skipped for
        :attr:`Completion.FEED_EXHAUSTED` because the runner released it itself when it
        closed the feed.
        """
        if outcome.completion in (Completion.LEASE_LOST, Completion.FEED_EXHAUSTED):
            return False
        lease = assignment.get("lease") or {}
        reason = (
            "local_storage_unavailable"
            if outcome.completion is Completion.STORAGE_UNAVAILABLE
            else "completed_phase"
        )
        try:
            self.client.release_assignment(
                assignment_id=str(assignment["assignment_id"]),
                lease_id=str(lease["lease_id"]),
                lease_epoch=int(lease["lease_epoch"]),
                release_reason=reason,
            )
        except ServerError as error:
            if error.is_lease_lost:
                return False
            raise
        return True

    # ------------------------------------------------------------------ the loop

    def run_forever(self, *, max_cycles: int | None = None) -> LoopExit:
        """Cycle until the budget runs out or something needs a person.

        The two "needs a person" exits are not failures and are not retried. A challenge
        cannot be cleared by trying again — I10 — and a blocked run needs either an
        unblocking condition or a fixed parser (T-RUN-16, T-RUN-24). Continuing to poll in
        either case would be a busy loop that changes nothing, and after a challenge it
        would also mean claiming with a session this collector knows is not ``ok``.
        """
        cycles: list[CycleResult] = []
        while max_cycles is None or len(cycles) < max_cycles:
            if not self.session.profile.ready or self.session.x_session_state in (
                XSessionState.CHALLENGE,
                XSessionState.EXPIRED,
            ):
                return LoopExit(
                    reason=LoopExitReason.SESSION_NEEDS_OWNER,
                    cycles=tuple(cycles),
                    detail=(
                        "phiên X ở trạng thái "
                        f"{self.session.x_session_state.value}; chỉ Owner xử lý được trong "
                        "cửa sổ Chrome, rồi resume trong app (T-RUN-10)"
                    ),
                )
            try:
                result = self.run_cycle()
            except ServerError as error:
                if error.code is ErrorCode.UNAUTHORIZED:
                    return LoopExit(
                        reason=LoopExitReason.UNAUTHORIZED,
                        cycles=tuple(cycles),
                        detail=error.message_safe,
                    )
                raise
            cycles.append(result)

            if result.kind is CycleKind.NO_WORK:
                self._idle_sleep(result.retry_after_ms)
                continue

            outcome = result.outcome
            if outcome is not None and requires_owner_action(outcome):
                if outcome.stop_reason in (
                    WireStopReason.CHALLENGE_REQUIRED,
                    WireStopReason.SESSION_EXPIRED,
                ):
                    return LoopExit(
                        reason=LoopExitReason.SESSION_NEEDS_OWNER,
                        cycles=tuple(cycles),
                        detail=f"stop_reason={outcome.stop_reason.value}",
                    )
                return LoopExit(
                    reason=LoopExitReason.RUN_NEEDS_OWNER,
                    cycles=tuple(cycles),
                    detail=(
                        f"stop_reason={outcome.stop_reason.value if outcome.stop_reason else ''}"
                    ),
                )
        return LoopExit(reason=LoopExitReason.CYCLE_BUDGET, cycles=tuple(cycles))

    def _idle_sleep(self, retry_after_ms: int | None) -> None:
        """Wait as long as the server asked, or fall back to ``claim_idle_backoff``."""
        if retry_after_ms is not None:
            self.sleep(retry_after_ms / 1000)
            return
        index = min(self._idle_streak - 1, len(CLAIM_IDLE_BACKOFF_S) - 1)
        self.sleep(CLAIM_IDLE_BACKOFF_S[max(index, 0)])
