"""Analysis worker entry point — Phase 0 stub.

It prints the task types the worker would advertise and exits. It does not claim a task,
does not read a credential, and does not start any provider: ``secret.issue_task_credential``
issues a short-lived, per-task credential (ADR-0010) and no adapter may be enabled before
its terms check and isolation probe have been recorded
(``contracts/ops/cli-acp-probe.md``). Those are the write set of
``agent-tasks/TC-analysis-adapter-validation.md``.
"""

from __future__ import annotations

import argparse
import json

from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.states import AnalysisTaskType

AGENT_VERSION = "0.1.0"


def advertised_task_types() -> list[str]:
    """The three AI task types of ``contracts/state/analysis.yaml`` ``task_type``.

    Embedding is not among them: it runs locally on the server (REQ-D48/REQ-D50), not on
    the worker.
    """
    return [member.value for member in AnalysisTaskType]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Research Radar analysis worker (Phase 0 stub)")
    parser.add_argument(
        "--print-capabilities",
        action="store_true",
        help="print the task types this worker would advertise and exit",
    )
    args = parser.parse_args(argv)
    if not args.print_capabilities:
        parser.error("Phase 0 worker has no runnable behaviour; use --print-capabilities")
    print(
        json.dumps(
            {
                "worker_kind": "analysis",
                "agent_version": AGENT_VERSION,
                "schema_version": CONTRACT_SCHEMA_VERSION,
                "tasks_supported": advertised_task_types(),
                "ai_providers": [],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
