"""Collector CLI entry point.

The collector runs as a process on the Owner's personal machine (REQ-S6.4-02) and talks to
the server over HTTP with the ``collectorToken`` bearer. This module is the entry point: it
reads configuration, refuses to start when anything is missing, and hands control to
:class:`collector.app.loop.CollectorLoop`.

What it deliberately does NOT do:

* it does not launch a browser, and this repo never runs ``playwright install`` -- browsers
  are an Owner-machine step, and CI has no live jobs (ADR-0011);
* it does not read the Chrome profile's contents or drive a page;
* it does not assert that the collector is online. ``collector_online`` in the
  ``--print-registration`` payload is a *claim by the worker*; the "online" state shown in the
  app is computed by the server from heartbeats (``contracts/ops/deployment.md``), which is
  why the value below is ``False`` and ``x_session_state`` is ``unknown`` rather than ``ok``
  (CAP-P5: ``unknown`` is never converted into ``ok``).

The one thing that is still missing, and why ``--run`` refuses
--------------------------------------------------------------
The loop is complete and tested, but a *live* :class:`~collector.app.reader.XSource` is not
in this repository. Driving a real Chrome belongs to ``TC-x-feasibility-probe`` behind gate
SP1, and ``contracts/ops/collector-probe.md`` §0 still records the probe as ``NOT_RUN`` with
§6 items 2-4 unanswered by the Owner. So ``--run`` validates the configuration, reports it
with the token redacted, and then refuses with a named reason rather than starting a loop
that would have nothing to read. Refusing is the honest outcome: a collector that started and
silently collected nothing would look like "no new research" (I13 forbids exactly that
confusion).

Tests build the loop directly and inject a recorded source, which is why the refusal here
costs no coverage.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.operations import OperationId

from collector.app.loop import ConfigError, load_config

AGENT_VERSION = "0.1.0"

#: Exit code for a refusal to start. Distinct from ``2`` (argparse usage) so an operator or a
#: process manager can tell "you typed the command wrong" from "the machine is not configured".
EXIT_CONFIG_REFUSED = 3

#: Exit code for "configured correctly, but there is nothing to drive yet" -- the SP1 gate.
EXIT_NO_SOURCE_DRIVER = 4


def capability_registration_shape() -> dict[str, Any]:
    """The payload shape for ``worker.register_capabilities`` with placeholder values.

    Every key here is a ``payload_fields[].field`` of
    ``contracts/capabilities.yaml.worker_capability_registration``; the dotted
    ``capabilities.*`` fields are nested under ``capabilities``.

    The values are deliberately the *unconfigured* ones. This command exists to show an
    operator the shape of the payload, and it must not imply an observation that has not been
    made: nothing here has looked at a Chrome profile or an X session, so the honest answers
    are ``False`` and ``unknown``. :meth:`collector.app.session.CollectorSession.capabilities`
    is what a running collector sends.
    """
    return {
        "operation": OperationId.WORKER_REGISTER_CAPABILITIES.value,
        "worker_instance_id": "<stable id of this collector installation>",
        "worker_kind": "collector",
        "registration_seq": 0,
        "agent_version": AGENT_VERSION,
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "capabilities": {
            "collector_online": False,
            "chrome_profile_ready": False,
            "x_session_state": "unknown",
        },
    }


def _describe_configuration() -> tuple[int, dict[str, Any]]:
    """Load the configuration and report it with the token redacted.

    Returns ``(exit_code, payload)``. A :class:`~collector.app.loop.ConfigError` becomes a
    payload naming the reason rather than a traceback: the operator needs to know which of
    five variables is wrong, and a stack trace answers a different question.
    """
    try:
        config = load_config()
    except ConfigError as error:
        return EXIT_CONFIG_REFUSED, {
            "status": "refused_to_start",
            "reason": error.reason,
            "message": str(error),
        }
    return 0, {"status": "configured", "config": config.redacted}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="collector.app.main",
        description="Research Radar collector (personal machine)",
    )
    parser.add_argument(
        "--print-registration",
        action="store_true",
        help="print the capability registration payload shape and exit",
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="validate the environment configuration and exit; the token is never printed",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="start the collection loop (requires a live X source driver -- see SP1)",
    )
    args = parser.parse_args(argv)

    if args.print_registration:
        print(json.dumps(capability_registration_shape(), ensure_ascii=False, indent=2))
        return 0

    if args.check_config:
        code, payload = _describe_configuration()
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return code

    if args.run:
        code, payload = _describe_configuration()
        if code != 0:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return code
        print(
            json.dumps(
                {
                    "status": "refused_to_start",
                    "reason": "no_x_source_driver",
                    "message": (
                        "Cấu hình hợp lệ, nhưng chưa có bộ điều khiển nguồn X nào để chạy. "
                        "Việc mở Chrome thuộc TC-x-feasibility-probe và còn bị chặn ở cổng "
                        "SP1 (contracts/ops/collector-probe.md §6 mục 2-4 chưa được Owner "
                        "trả lời). Vòng lặp đã có và đã được kiểm bằng nguồn ghi sẵn; nó "
                        "chưa có gì thật để đọc."
                    ),
                    "config": payload["config"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return EXIT_NO_SOURCE_DRIVER

    parser.error(
        "choose one of --print-registration, --check-config or --run; "
        "the collector does not start a loop by default"
    )
    return 2  # pragma: no cover - parser.error raises SystemExit


if __name__ == "__main__":
    raise SystemExit(main())
