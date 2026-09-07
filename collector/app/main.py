"""Collector CLI entry point — Phase 0 stub.

What it does: prints the *shape* of the capability-registration payload that
``worker.register_capabilities`` expects, taken field by field from
``contracts/capabilities.yaml`` ``worker_capability_registration``.

What it deliberately does NOT do:

* it does not launch a browser, and this repo never runs ``playwright install`` -- browsers
  are an Owner-machine step, and CI has no live jobs (ADR-0011);
* it does not call the server, read a token, or touch the Chrome profile;
* it does not assert that the collector is online. ``collector_online`` in the payload is a
  *claim by the worker*; the "online" state shown in the app is computed by the server from
  heartbeats (``contracts/ops/deployment.md``), which is why the value below is ``False``
  and ``x_session_state`` is ``unknown`` rather than ``ok`` (CAP-P5: ``unknown`` is never
  converted into ``ok``).

The real registration call belongs to ``agent-tasks/TC-collector-checkpoint-resume.md``.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.operations import OperationId

AGENT_VERSION = "0.1.0"


def capability_registration_shape() -> dict[str, Any]:
    """The payload shape for ``worker.register_capabilities`` with placeholder values.

    Every key here is a ``payload_fields[].field`` of
    ``contracts/capabilities.yaml.worker_capability_registration``; the dotted
    ``capabilities.*`` fields are nested under ``capabilities``.
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Research Radar collector (Phase 0 stub)")
    parser.add_argument(
        "--print-registration",
        action="store_true",
        help="print the capability registration payload shape and exit",
    )
    args = parser.parse_args(argv)
    if not args.print_registration:
        parser.error("Phase 0 collector has no runnable behaviour; use --print-registration")
    print(json.dumps(capability_registration_shape(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
