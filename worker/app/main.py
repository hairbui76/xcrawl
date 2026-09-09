"""Analysis worker entry point.

`contracts/ops/deployment.md` §1–§2: this process runs on the Owner's personal machine, in
no container, listening on **no port** — every connection it makes is outbound. It claims
analysis tasks from the server over HTTP, runs them through an adapter in its own process,
and submits results. The cycle itself lives in :mod:`worker.app.loop`.

Three modes, and each refuses rather than improvises:

* ``--print-capabilities`` — what this worker would advertise. Unchanged from the Phase-0
  stub, byte for byte, because `docs/owner-runbook.md` §4.3 pins its exact output as a
  command the Owner has already run.
* ``--print-adapters`` — the AI adapter registry as `contracts/ai/providers.yaml` §2.1
  states it, with each entry's probe outcome and the REQ-AC16 verdict. New: the Owner had no
  way to see *why* no provider is usable without reading the contract.
* ``--run`` — the real loop. It **refuses to start** unless the configuration is complete,
  and every refusal names its reason: `contracts/ops/secrets.md` §3 requires the worker to
  refuse when the token file's permissions are wider than ``0600``, on the grounds that a
  silent warning is useless.

The worker holds no API key. Provider credentials are issued **per task** by
`MOD-secret-service` (B13, ADR-0010 §1) and live only in process memory for the length of
one attempt; the only secret this file reads is the worker's own bearer token, and it is
never printed, logged or placed in an error message.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.states import AnalysisTaskType

from worker.app.adapter.api_provider import (
    ApiProviderAdapter,
    ProviderRequest,
    ProviderResponse,
)
from worker.app.adapter.base import TaskCredential, ac16_status, load_registered_adapters

AGENT_VERSION = "0.1.0"

#: Environment variables `docs/owner-runbook.md` §4.3 will document. Names, not values.
SERVER_URL_ENV: Final[str] = "RR_SERVER_URL"
TOKEN_FILE_ENV: Final[str] = "RR_WORKER_TOKEN_FILE"
WORKER_ID_ENV: Final[str] = "RR_WORKER_INSTANCE_ID"

#: `contracts/ops/secrets.md` §3: "Quyền file `0600`, chủ sở hữu là user chạy worker …
#: Worker **từ chối khởi động** nếu quyền rộng hơn `0600`."
MAX_TOKEN_FILE_MODE: Final[int] = 0o600


class ConfigRefusal(str, Enum):
    """Why the worker will not start. One name per cause, and no catch-all.

    A single "bad configuration" message would make three quite different operator actions
    look the same: set a variable, create a file, fix its permissions.
    """

    SERVER_URL_MISSING = "server_url_not_configured"
    TOKEN_FILE_MISSING = "worker_token_file_missing"
    TOKEN_FILE_NOT_A_FILE = "worker_token_file_not_a_file"
    TOKEN_FILE_PERMISSIONS = "worker_token_file_permissions_too_wide"
    TOKEN_EMPTY = "worker_token_empty"


class ConfigError(Exception):
    """A refusal to start, carrying its reason and never the token."""

    def __init__(self, reason: ConfigRefusal, detail: str) -> None:
        super().__init__(f"{reason.value}: {detail}")
        self.reason = reason
        self.detail = detail


@dataclass(frozen=True)
class WorkerConfig:
    """Everything the loop needs, read from the environment and one ``0600`` file."""

    server_url: str
    worker_instance_id: str
    token_file: Path
    _token: str

    def token(self) -> str:
        """The one accessor. Not a field read, so a grep finds every use."""
        return self._token

    def __repr__(self) -> str:
        return (
            f"WorkerConfig(server_url={self.server_url!r}, "
            f"worker_instance_id={self.worker_instance_id!r}, "
            f"token_file={str(self.token_file)!r}, token=<redacted>)"
        )

    __str__ = __repr__


def advertised_task_types() -> list[str]:
    """The three AI task types of ``contracts/state/analysis.yaml`` ``task_type``.

    Embedding is not among them: it runs locally on the server (REQ-D48/REQ-D50), not on
    the worker.
    """
    return [member.value for member in AnalysisTaskType]


def load_config(environ: dict[str, str] | None = None) -> WorkerConfig:
    """Read the configuration, refusing with a named reason at the first thing missing.

    The permission check is a **refusal**, not a warning (`secrets.md` §3). It reads the
    file's mode rather than trying to open it as the wrong user, because the contract's
    requirement is about the mode.
    """
    env = environ if environ is not None else dict(os.environ)

    server_url = (env.get(SERVER_URL_ENV) or "").strip()
    if not server_url:
        raise ConfigError(
            ConfigRefusal.SERVER_URL_MISSING,
            f"set {SERVER_URL_ENV} to the base URL of the Research Radar server",
        )

    raw_path = (env.get(TOKEN_FILE_ENV) or "").strip()
    if not raw_path:
        raise ConfigError(
            ConfigRefusal.TOKEN_FILE_MISSING,
            f"set {TOKEN_FILE_ENV} to a 0600 file holding the analysis_worker_token "
            f"(contracts/ops/secrets.md §3: never in the repo)",
        )
    token_file = Path(raw_path).expanduser()
    if not token_file.exists():
        raise ConfigError(ConfigRefusal.TOKEN_FILE_MISSING, f"{token_file} does not exist")
    if not token_file.is_file():
        raise ConfigError(ConfigRefusal.TOKEN_FILE_NOT_A_FILE, f"{token_file} is not a file")

    mode = stat.S_IMODE(token_file.stat().st_mode)
    if mode & ~MAX_TOKEN_FILE_MODE:
        raise ConfigError(
            ConfigRefusal.TOKEN_FILE_PERMISSIONS,
            f"{token_file} is {mode:04o}; contracts/ops/secrets.md §3 requires 0600 or "
            f"narrower, and a silent warning would be useless",
        )

    token = token_file.read_text(encoding="utf-8").strip()
    if not token:
        raise ConfigError(ConfigRefusal.TOKEN_EMPTY, f"{token_file} is empty")

    return WorkerConfig(
        server_url=server_url,
        worker_instance_id=(env.get(WORKER_ID_ENV) or "analysis-worker-1").strip(),
        token_file=token_file,
        _token=token,
    )


class RefusingTransport:
    """A provider transport that raises if anything ever tries to send through it.

    Used where an adapter object must exist but no call may be made — probing, and the
    not-yet-reachable branch of :func:`_run`. A transport that quietly returned an empty
    answer would let a missing configuration read as a working one.
    """

    def send(self, request: ProviderRequest, *, credential: TaskCredential) -> ProviderResponse:
        raise RuntimeError(
            "no provider transport is configured; this adapter was built to be asked about, "
            "not to be called"
        )


def adapter_report() -> dict[str, object]:
    """The registry of `contracts/ai/providers.yaml` §2.1, probed and summarised.

    Reports each entry's probe outcome rather than a boolean: `contracts/ports.yaml` gives
    ``ai.probe_provider_capability`` three values and forbids converting ``unknown`` into
    ``usable``. And REQ-AC16 is reported ``BLOCKED``, never ``FAIL`` — the zero-API-key path
    has not been tried and found wanting, it has not been permitted to run (ADR-0010).

    The probe runs through a real :class:`ApiProviderAdapter` rather than re-deriving the
    verdict here, so this command and the loop cannot come to different conclusions about
    the same entry. Probing opens nothing, which is why a refusing transport is enough.
    """
    entries = load_registered_adapters()
    rows = []
    for entry in entries:
        adapter = ApiProviderAdapter(entry, transport=RefusingTransport(), endpoint="")
        probe = adapter.probe_provider_capability()
        rows.append(
            {
                "adapter_id": entry.adapter_id,
                "auth_family": entry.auth_family.value,
                "task_support": sorted(t.value for t in entry.task_support),
                "enabled": entry.enabled,
                "probe_outcome": probe.outcome.value,
                "reason_code": probe.reason_code.value if probe.reason_code else None,
                "disabled_reason_present": bool(entry.disabled_reason),
            }
        )
    return {"registered_adapters": rows, "ac16": ac16_status(entries)}


def _print_capabilities() -> int:
    print(
        json.dumps(
            {
                "worker_kind": "analysis",
                "agent_version": AGENT_VERSION,
                "schema_version": CONTRACT_SCHEMA_VERSION,
                "tasks_supported": advertised_task_types(),
                # Still empty, and for the same reason as in Phase 0: `ai_providers` lists
                # providers this worker may actually use, and both registered adapters are
                # `enabled: false` while isolation is unverified. `--print-adapters` shows
                # the registry behind that emptiness.
                "ai_providers": [],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _print_adapters() -> int:
    print(json.dumps(adapter_report(), ensure_ascii=False, indent=2))
    return 0


def _run(config: WorkerConfig) -> int:
    """Build the loop against the real server and run it.

    Deliberately **not** covered by a unit test that starts a process: what a test can prove
    is the cycle, and `tests/integration/test_worker_loop.py` proves it against the real
    FastAPI app in-process. What this function adds over that is `httpx` and a socket, and a
    test that asserted those would be asserting the transport library.
    """
    import httpx

    from worker.app.loop import AbsentSecretService, AnalysisServerPort, AnalysisWorkerLoop

    entries = load_registered_adapters()
    usable = [entry for entry in entries if entry.dispatchable]
    if not usable:
        # Not an error: the contract's answer. Both adapters are `enabled: false` because
        # isolation is unverified (B13), so there is no work this process could finish.
        # Saying so and exiting beats spinning against a queue that will refuse anyway.
        print(
            json.dumps(
                {
                    "started": False,
                    "reason": "no_dispatchable_adapter",
                    "detail": (
                        "every entry in contracts/ai/providers.yaml §2.1 is enabled: false "
                        "(isolation unverified, E3 NOT_RUN). See docs/owner-runbook.md §8.3."
                    ),
                    "ac16": ac16_status(entries),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 3

    with httpx.Client(base_url=config.server_url, timeout=30.0) as client:  # pragma: no cover
        loop = AnalysisWorkerLoop(
            server=AnalysisServerPort(client, token=config.token()),
            # `RefusingTransport` on purpose: an entry that is dispatchable but has no wired
            # provider transport must fail loudly. Inventing an endpoint here is exactly the
            # class of guess ISO-03 exists to prevent.
            adapter=ApiProviderAdapter(usable[0], transport=RefusingTransport(), endpoint=""),
            worker_instance_id=config.worker_instance_id,
            credentials=AbsentSecretService(),
        )
        for report in loop.run_forever():
            print(json.dumps({"outcome": report.outcome.value, "task_id": report.task_id}))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Research Radar analysis worker")
    parser.add_argument(
        "--print-capabilities",
        action="store_true",
        help="print the task types this worker would advertise and exit",
    )
    parser.add_argument(
        "--print-adapters",
        action="store_true",
        help="print the AI adapter registry, each entry's probe outcome and the AC-16 verdict",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="claim and process analysis tasks (refuses to start without configuration)",
    )
    args = parser.parse_args(argv)

    if args.print_capabilities:
        return _print_capabilities()
    if args.print_adapters:
        return _print_adapters()
    if args.run:
        try:
            config = load_config()
        except ConfigError as refusal:
            print(
                json.dumps(
                    {
                        "started": False,
                        "reason": refusal.reason.value,
                        "detail": refusal.detail,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                file=sys.stderr,
            )
            return 2
        return _run(config)

    parser.error("choose one of --print-capabilities, --print-adapters or --run")
    return 2  # pragma: no cover - argparse.error exits


if __name__ == "__main__":
    raise SystemExit(main())
