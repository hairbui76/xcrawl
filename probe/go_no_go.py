"""Entry point for the §7 go/no-go computation.

    uv run python probe/go_no_go.py evidence/runs/SP1-x-feasibility/runs.jsonl

The logic lives in :mod:`probe.x_feasibility.go_no_go`, next to the record shape it reads.
This file exists because the task packet names ``probe/go_no_go.py`` as the command the
Owner types, and a runbook step should be one path, not a package path.
"""

from __future__ import annotations

# ruff: noqa: E402 -- the sys.path bootstrap below must run before the package imports.
import sys
from pathlib import Path as _Path

if __name__ == "__main__" and __package__ in {None, ""}:
    # The card gives this command as a FILE PATH (`python probe/go_no_go.py`).
    # Python then puts *this file's directory* on sys.path -- not the repo root -- so
    # `import probe.…` would fail on the first import line. Putting the repo root first makes
    # the documented command work. It is a no-op for `python -m probe.go_no_go`
    # and for every import, which never enter this branch.
    sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

from probe.x_feasibility.go_no_go import main

if __name__ == "__main__":
    raise SystemExit(main())
