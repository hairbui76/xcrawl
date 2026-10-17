"""``G-7`` loopback drill — the collector and worker loops against a real server **process**.

What it proves, and why it exists
---------------------------------
``docs/owner-runbook.md`` §11.2 ``G-7``: registration, heartbeat and claim had only ever been
exercised in-process (``TestClient`` behind ``httpx.MockTransport``). This drill starts
``uvicorn server.app.main:app`` as a separate OS process on ``127.0.0.1``, bootstraps an owner
through ``rr-admin`` exactly as the runbook does, and then drives the production
:class:`~collector.app.loop.CollectorLoop` and :class:`~worker.app.loop.AnalysisServerPort`
over a real TCP socket with real ``httpx`` transports:

1. owner login → ``POST /v1/runs/run-now`` (cookie + ``X-CSRF-Token``, as the web UI does);
2. collector: ``register`` → ``claim`` → collect → ``ingest.submit_batch`` →
   ``ingest.commit_checkpoint`` → ``release``;
3. ``GET /v1/workers/status`` and ``GET /v1/runs`` as the owner;
4. worker: ``POST /v1/analysis/tasks/claim`` with the analysis-worker bearer.

What it does **not** prove
--------------------------
The X source is :class:`~collector.app.reader.RecordedSource` over synthetic posts — no
browser, no X session (``SP1`` is the Owner's). No AI adapter runs: both are ``enabled: false``
(``G-8``), so the worker only claims. Both shipped ``--run`` entry points still refuse before
touching the server, for exactly those two reasons; this drill builds the loops directly and
says so. It touches **only** ``127.0.0.1`` and a temporary directory.

Usage::

    uv run python tools/loopback_drill.py            # prints one JSON report, exit 0 on success
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION  # noqa: E402

from collector.app.client import (  # noqa: E402
    REQUEST_ID_HEADER,
    SCHEMA_VERSION_HEADER,
    CollectorClient,
    new_ulid,
)
from collector.app.loop import CollectorConfig, CollectorLoop  # noqa: E402
from collector.app.reader import FeedPage, RecordedSource, SourceSignal  # noqa: E402
from collector.app.session import ChromeProfile, XSessionState  # noqa: E402
from server.app.auth.service import hash_bearer_token  # noqa: E402
from worker.app.loop import AnalysisServerPort  # noqa: E402

#: Throwaway credentials for a throwaway database. Never reused, never written to the repo.
COLLECTOR_TOKEN = "loopback-drill-collector-token"
WORKER_TOKEN = "loopback-drill-worker-token"
OWNER_PASSWORD = "loopback-drill-owner-password"
COLLECTOR_ID = "01JDR1LLC0LLECT0R000000000"
WORKER_ID = "01JDR1LLW0RKER00000000000A"
BATCH_SIZE = 5


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _environment(data_dir: Path) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("RR_")}
    env.update(
        {
            "RR_DATA_DIR": str(data_dir),
            "RR_COLLECTOR_TOKEN": COLLECTOR_TOKEN,
            "RR_ANALYSIS_WORKER_TOKEN_SHA256": hash_bearer_token(WORKER_TOKEN),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    return env


def _admin(env: dict[str, str], *args: str, stdin: str | None = None) -> str:
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "rr_admin.py"), *args],
        env=env,
        input=stdin,
        capture_output=True,
        text=True,
        check=True,
        cwd=str(data_dir_of(env)),
    )
    return result.stdout.strip()


def data_dir_of(env: dict[str, str]) -> Path:
    return Path(env["RR_DATA_DIR"])


def _wait_ready(base_url: str, server: subprocess.Popen[bytes], timeout_s: float = 30.0) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise RuntimeError(f"uvicorn exited early with code {server.returncode}")
        try:
            if httpx.get(f"{base_url}/healthz", timeout=1.0).status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.2)
    raise RuntimeError("uvicorn did not become ready")


def _raw_post(index: int, now: str) -> dict[str, Any]:
    post_id = f"19900000000000000{index:02d}"
    return {
        "x_post_id": post_id,
        "author": {"handle": "loopback", "x_user_id": "1234567890"},
        "url": f"https://x.com/loopback/status/{post_id}",
        "text": f"bài thử loopback số {index}",
        "published_at": now,
        "collected_at": now,
        "media_refs": [],
        "referenced_links": [],
    }


def _owner(base_url: str) -> httpx.Client:
    """An owner browser session: login, then echo the CSRF cookie on every mutation."""
    owner = httpx.Client(
        base_url=base_url,
        timeout=10.0,
        headers={SCHEMA_VERSION_HEADER: CONTRACT_SCHEMA_VERSION},
        event_hooks={"request": [_stamp_request_id]},
    )
    # `display_name` is the login name, case-sensitive; `rr-admin bootstrap-owner` defaults
    # it to "Owner" (docs/owner-runbook.md §3).
    response = owner.post("/v1/auth/login", json={"username": "Owner", "password": OWNER_PASSWORD})
    response.raise_for_status()
    # Both cookies are `Secure`, so httpx's jar will not replay them over http://127.0.0.1.
    # A browser treats loopback as a secure context and does; send them the way it would.
    session, csrf = response.cookies["rr_session"], response.cookies["rr_csrf"]
    owner.cookies.clear()
    owner.headers["Cookie"] = f"rr_session={session}; rr_csrf={csrf}"
    owner.headers["X-CSRF-Token"] = csrf
    return owner


def _stamp_request_id(request: httpx.Request) -> None:
    request.headers[REQUEST_ID_HEADER] = new_ulid()


def drill(work: Path) -> dict[str, Any]:
    data_dir = work / "data"
    data_dir.mkdir()
    env = _environment(data_dir)
    report: dict[str, Any] = {"server": "uvicorn server.app.main:app (separate OS process)"}

    report["migrate"] = _admin(env, "migrate").splitlines()[-1]
    # A non-TTY stdin is the documented non-interactive path (`rr_admin._read_password`).
    report["owner_id"] = _admin(env, "bootstrap-owner", stdin=OWNER_PASSWORD).splitlines()[-1]

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    log = (work / "uvicorn.log").open("wb")
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "server.app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        env=env,
        cwd=str(REPO_ROOT),
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_ready(base_url, server)
        report["server_pid"] = server.pid

        owner = _owner(base_url)
        try:
            run = owner.post("/v1/runs/run-now", json={"request_id": "01JDR1LLRUNN0W000000000000"})
            report["run_now"] = {"status": run.status_code, "body": run.json()}

            now = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            profile = work / "rr-chrome-profile"
            profile.mkdir()
            source = RecordedSource(
                [
                    FeedPage(
                        raw_posts=tuple(_raw_post(i, now) for i in range(1, BATCH_SIZE + 1)),
                        next_cursor=None,
                        signal=SourceSignal.END_OF_FEED,
                    )
                ]
            )
            with CollectorClient(base_url=base_url, token=COLLECTOR_TOKEN) as client:
                loop = CollectorLoop(
                    config=CollectorConfig(
                        server_url=base_url,
                        token=COLLECTOR_TOKEN,
                        profile=ChromeProfile(user_data_dir=profile, ready=True),
                        worker_instance_id=COLLECTOR_ID,
                    ),
                    client=client,
                    source=source,
                    batch_size=BATCH_SIZE,
                )
                loop.session = loop.session.observing(XSessionState.OK)
                report["collector_register"] = loop.register()
                cycle = loop.run_cycle()
                outcome = cycle.outcome
                report["collector_cycle"] = {
                    "kind": cycle.kind.value,
                    "completion": outcome.completion.value if outcome else None,
                    "stop_reason": outcome.stop_reason if outcome else None,
                    "acked_through_ingest_sequence": (
                        outcome.acked_through_ingest_sequence if outcome else None
                    ),
                    "source_reads": source.read_count,
                }

            status = owner.get("/v1/workers/status")
            report["workers_status"] = {"status": status.status_code, "body": status.json()}
            runs = owner.get("/v1/runs")
            report["runs"] = {"status": runs.status_code, "body": runs.json()}
        finally:
            owner.close()

        with httpx.Client(base_url=base_url, timeout=10.0) as transport:
            port_ = AnalysisServerPort(transport, token=WORKER_TOKEN)
            try:
                claimed = port_.claim_task(
                    worker_instance_id=WORKER_ID,
                    task_types=["label", "summary"],
                    claim_request_id=new_ulid(),
                )
                report["worker_claim"] = {"ok": True, "body": claimed}
            except Exception as refusal:  # the refusal IS the observation; record its shape
                report["worker_claim"] = {
                    "ok": False,
                    "error": type(refusal).__name__,
                    "detail": str(refusal),
                }
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
        log.close()
    report["server_exit"] = server.returncode
    return report


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rr-loopback-") as tmp:
        report = drill(Path(tmp))
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    cycle = report.get("collector_cycle", {})
    ok = (
        report.get("run_now", {}).get("status") in (200, 201, 202)
        and cycle.get("acked_through_ingest_sequence") == BATCH_SIZE
        and report.get("workers_status", {}).get("status") == 200
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
