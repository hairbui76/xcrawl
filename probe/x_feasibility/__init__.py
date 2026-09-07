"""SP1 / M0 X feasibility probe (card ``agent-tasks/TC-x-feasibility-probe.md``).

This package is **tooling and a runbook**, not evidence. Nothing in here has been run
against X. The live runs need the Owner's machine, the Owner's Chrome profile and the four
written confirmations of ``contracts/ops/collector-probe.md`` §6 -- of which only item 1
(D09) is answered (``OD-20260907-01``). Until items 2-4 exist in writing, the state is
``OWNER_DECISION_REQUIRED`` and :mod:`probe.x_feasibility.run_probe` refuses to launch a
browser (SG-02 of the card, enforced in :mod:`probe.x_feasibility.config`).

Module map
----------

``config``    load + validate the run configuration; hold the Owner gate; refuse the OS
              default Chrome profile (REQ-D09).
``signals``   pure state-signal detector for the §4 stop conditions. No I/O, no browser --
              it takes a snapshot of what a page looked like and returns one decision.
``record``    the §5 per-run record: shape, validation, ULID, JSONL append, redaction.
``go_no_go``  §7 go/no-go computed over a JSONL file, verbatim thresholds.
``run_probe`` the CLI that drives Chrome through Playwright and writes one record per run.

Boundaries that are constraints, not settings (``collector-probe.md`` §2). No code here
may ever evade a CAPTCHA, fake a fingerprint or user agent, rotate an account or a proxy,
or automate a verification click. ``tests/contract/test_x_probe_boundaries.py`` asserts the
absence of those mechanisms in this package's own source; a violation fails the card
regardless of the numbers a run produced.
"""

__all__ = ["PROTOCOL_VERSION"]

#: Version of ``contracts/ops/collector-probe.md`` this tooling implements. Written into
#: every record and every evidence manifest, so a record can never be read against a
#: protocol it was not produced under.
PROTOCOL_VERSION = "CT-ops-collector-probe@0.4.0"
