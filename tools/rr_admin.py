#!/usr/bin/env python3
"""``rr_admin`` -- the three operator commands the Owner needs before anything else works.

    uv run rr-admin migrate          # from ANY working directory
    uv run rr-admin bootstrap-owner
    uv run rr-admin status

(`uv run python tools/rr_admin.py …` still works from the repo root; the console script is
the supported path because it does not care where you are standing.)

Why these three
---------------
``docs/owner-runbook.md`` found the stack un-startable for three separate reasons, and this
file closes two of them:

``G-1``
    Nothing set ``owner.password_hash``. ``AuthService.bootstrap_owner()`` is documented as a
    "CLI/console call" and there was no CLI, so the only exercised path was the runbook's
    ``python -c`` one-liner **with the password on the command line** -- readable by every
    other process on the machine. ``bootstrap-owner`` below prompts on a TTY, never echoes,
    never accepts the password as an argument, and never prints it.

``G-4``
    ``alembic upgrade head`` worked only from inside ``server/``, because
    ``script_location = migrations`` in ``server/alembic.ini`` resolves against the cwd.
    ``migrate`` builds the config with absolute paths, so it runs from anywhere.

``status`` exists because "is it broken or is it just not configured yet?" was, before this,
answerable only by reading source. It distinguishes *no database file*, *not migrated*, *not
bootstrapped* and *ready*, and it lists exactly which contexts a server process would wire.

Secrets
-------
No command takes a secret as an argument, prints one, or writes one to a file. ``status``
reports the presence of each configured credential as a boolean and never its value
(``contracts/ops/secrets.md`` §2.4).
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from server.app.settings import Settings, load_settings  # noqa: E402
from server.app.wiring import build_runtime, resolve_owner_id, wire  # noqa: E402

#: `contracts/ops/secrets.md` §2.2 / the login route's own validation. Checked here as well
#: so the operator learns at the prompt, not after typing a password twice.
MIN_PASSWORD_LENGTH = 8


def database_line(settings: Settings) -> str:
    """The one place either command turns the configured database into text.

    Both `migrate` and `status` used to format `settings.database_path` themselves. One
    formatting site means the two can never disagree about which file they are talking
    about — and the Coordinator's process check found them agreeing on something wrong,
    which is only diagnosable if they agree at all.

    What is printed is the **resolved absolute path the engine will open**, not the raw
    environment value: the operator's next action is usually `ls` or `sqlite3` on it, and a
    URL is not something either accepts.
    """
    return str(settings.database_path.resolve())


# ----------------------------------------------------------------------------------------
# migrate
# ----------------------------------------------------------------------------------------


def cmd_migrate(settings: Settings, args: argparse.Namespace) -> int:
    """``alembic upgrade head`` against the configured database, from any directory."""
    from server.app.wiring import upgrade_database

    print(f"migrating {database_line(settings)} -> {args.revision}")
    upgrade_database(settings.database_path, args.revision)
    print("done")
    return 0


# ----------------------------------------------------------------------------------------
# bootstrap-owner
# ----------------------------------------------------------------------------------------


def _read_password(stream_password: str | None) -> str:
    """Get the password without ever putting it in ``argv``.

    Two accepted sources, in order: a non-TTY stdin (so an operator can pipe from a
    ``0600`` file or a password manager), then an interactive double prompt. There is
    deliberately no ``--password`` flag: process arguments are world-readable on a shared
    machine, which is exactly the hazard the runbook warned about in prose and could not fix.
    """
    if stream_password is not None:
        return stream_password
    first = getpass.getpass("Owner password: ")
    second = getpass.getpass("Repeat password: ")
    if first != second:
        raise SystemExit("passwords do not match; nothing was written")
    return first


def cmd_bootstrap_owner(settings: Settings, args: argparse.Namespace) -> int:
    """Create -- or re-credential -- the single owner row.

    Calling it twice is not an error: ``owner.singleton_guard`` forbids a second row, so the
    second call sets a new password and **revokes every open session**
    (``contracts/ops/secrets.md`` §2.3). That is the documented password-reset path, and it
    is the only one: ``REQ-D05`` forbids a signup page and automated recovery.
    """
    runtime = build_runtime(settings)

    piped = None
    if not sys.stdin.isatty():
        piped = sys.stdin.read().strip("\n")
        if not piped:
            piped = None
    password = _read_password(piped)

    if len(password) < MIN_PASSWORD_LENGTH:
        raise SystemExit(
            f"password must be at least {MIN_PASSWORD_LENGTH} characters "
            "(contracts/ops/secrets.md §2.2); nothing was written"
        )

    owner_id = runtime.auth_service.bootstrap_owner(
        display_name=args.display_name,
        password=password,
        timezone_iana=settings.timezone_iana,
    )
    # The id, and nothing else. Not the password, not the hash, not the parameters.
    print(owner_id)
    return 0


# ----------------------------------------------------------------------------------------
# status
# ----------------------------------------------------------------------------------------


def _database_state(settings: Settings) -> tuple[str, str]:
    """Distinguish the four states an operator actually cares about."""
    if not settings.database_path.exists():
        return ("absent", "no database file; run `uv run rr-admin migrate`")
    from sqlalchemy import text

    from server.app.db import create_sqlite_engine

    engine = create_sqlite_engine(settings.database_path)
    try:
        with engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version LIMIT 1")
            ).fetchone()
    except Exception:
        return ("unmigrated", "no alembic_version table; run `uv run rr-admin migrate`")
    if revision is None:
        return ("unmigrated", "alembic_version is empty; run `uv run rr-admin migrate`")
    if resolve_owner_id(engine) is None:
        return (
            f"migrated ({revision[0]})",
            "no owner row; run `uv run rr-admin bootstrap-owner`",
        )
    return (f"migrated ({revision[0]})", "ready")


def cmd_status(settings: Settings, args: argparse.Namespace) -> int:
    """Report configuration, database state, and what a server process would wire."""
    state, hint = _database_state(settings)
    payload: dict[str, Any] = {
        "database": database_line(settings),
        "database_state": state,
        "next_step": hint,
        "settings": settings.redacted(),
    }

    if state.startswith("migrated"):
        # Build a real application and ask it what it wired. Anything less would be this
        # command's own opinion of the wiring rather than the wiring itself.
        from server.app.main import create_app

        app = create_app()
        runtime = wire(app, settings)
        payload["wiring"] = runtime.report()

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"database    : {database_line(settings)}")
    print(f"state       : {state}")
    print(f"next step   : {hint}")
    print(f"timezone    : {settings.timezone_iana}")
    print(f"slots       : {', '.join(settings.schedule_slots)}")
    wiring = payload.get("wiring")
    if isinstance(wiring, dict):
        print(f"wired       : {', '.join(wiring['wired'])}")
        for name, reason in wiring["unwired"].items():
            print(f"  not wired : {name} — {reason}")
    return 0


# ----------------------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rr_admin",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    migrate = sub.add_parser("migrate", help="alembic upgrade (default: head), from any cwd")
    migrate.add_argument("--revision", default="head")
    migrate.set_defaults(func=cmd_migrate)

    bootstrap = sub.add_parser(
        "bootstrap-owner",
        help="create or re-credential the single owner account (prompts; never echoes)",
    )
    bootstrap.add_argument("--display-name", default="Owner")
    bootstrap.set_defaults(func=cmd_bootstrap_owner)

    status = sub.add_parser("status", help="configuration, database state and wiring report")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=cmd_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings()
    result: int = args.func(settings, args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
