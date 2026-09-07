"""``MOD-analysis-service``: the task lifecycle behind one valid result per key.

Revision ID: 0006_tc_analysis_once_per_generation
Revises: 0005_tc_research_connector_metadata
Create Date: 2026-09-08

Card: ``agent-tasks/TC-analysis-once-per-generation.md``.
Source of truth: ``contracts/data/entities.yaml`` -- ``ENT-analysis-generation``,
``ENT-analysis-attempt``, ``ENT-analysis-task``, ``ENT-assignment-lease``. Every table below
carries **exactly** the fields those entities declare: no ``run_id`` on the task, no
``lease_epoch`` on the attempt, no convenience counter. ``tests/contract/
test_schema_matches_entities.py`` asserts set equality in both directions, so a helpful extra
column is a failure, not a shortcut.

``analysis`` is deliberately not created here
---------------------------------------------
``0002b_shared_move_set_tables`` already created ``analysis`` (and ``work_label``) as
custodian *on behalf of this module* because the identity merge move-set could not be proved
without them. This card takes ownership of those rows; it does not issue a second
``CREATE TABLE``, which is precisely the defect ``F-A3R1-01`` was.

Two ``REFERENCES`` clauses that ``analysis`` still lacks are reported as
``CR-TC-ANALYSIS-03`` rather than fixed here: ``analysis.analysis_generation_id`` and
``analysis.accepted_from_attempt_id`` name tables this revision creates, so the columns could
now carry foreign keys -- but adding one to an existing SQLite table means rebuilding it, and
``work_label.analysis_id`` references ``analysis``. A rebuild is the "recreate" this card was
told not to do. Both references are enforced instead inside ``TXN-analysis-accept``
(``server/app/analysis/service.py``), which reads the generation row and the attempt row in
the same transaction that writes the result.

``assignment_lease``: created here as custodian, owned by ``MOD-job-service``
-----------------------------------------------------------------------------
``contracts/state/analysis.yaml`` T-AN-02/T-AN-11 and invariant I10 are stated in terms of a
lease with a monotonic ``lease_epoch``, and ``contracts/ports.yaml`` puts ``lease_id`` and
``lease_epoch`` on the wire of ``analysis.claim_task``, ``analysis.heartbeat`` and
``analysis.submit_result``. ``ENT-assignment-lease`` is the only place the contract gives the
epoch a home, and ``ENT-analysis-task``/``ENT-analysis-attempt`` point *into* it
(``claimed_lease_id``, ``worker_lease_id``). Without the table this card's stale-worker
oracle cannot run at all.

So this revision creates it the way ``0002b`` created ``analysis``: column-for-column from
the contract, with a header that names the real owner. ``owner_module`` is
``MOD-job-service`` and ``owned_by_package`` is PC03; the card that takes it over is
``agent-tasks/TC-scheduler-lease-claim.md``, which must EXTEND this revision rather than
issue a second ``CREATE TABLE assignment_lease``. That instruction is repeated as
``CR-TC-ANALYSIS-01`` in this card's handoff.

``run_id`` carries no ``REFERENCES`` clause: ``run`` belongs to the scheduler card and does
not exist yet, and SQLite resolves foreign keys at DML time, so a clause naming a missing
table would turn every INSERT into an error. The column keeps its name, type and NOT NULL.
That NOT NULL is itself a contract gap for this card -- an analysis claim is not scoped to a
collector run, and ``ENT-analysis-task`` has no column to carry one -- reported as
``CR-TC-ANALYSIS-02``. The service does not invent a value: ``claim_task`` refuses with an
internal-dependency error when no run id is wired.

``target_key`` is a plain column here, not a generated one
----------------------------------------------------------
``analysis``, ``saved_item`` and ``work_label`` carry ``target_key`` as a STORED generated
column because the identity merge rewrites their target pointers and the key must not be able
to disagree with the pointer. ``analysis_generation`` and ``analysis_task`` are **not** in
that closed move-set, so their ``target_key`` is an ordinary NOT NULL column -- kept honest by
a CHECK that spells out the same expression. ``tests/contract/test_schema_matches_entities.py
::test_generated_columns_are_visible_to_this_check`` pins the generated set to exactly those
three tables, so making a fourth one generated would be a contract change, not a tidy-up.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0006_tc_analysis_once_per_generation"
down_revision: str | None = "0005_tc_research_connector_metadata"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: GLOB for the mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §conventions).
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

#: ``ENT-analysis.task_type`` / ``ENT-analysis-generation.task_type`` -- the authoritative
#: spelling is entities.yaml's (ruling R-03, CR-PC03-05), not ports.yaml's older one.
_TASK_TYPES = "('label', 'summary', 'direction_phrasing')"

#: ``contracts/state/analysis.yaml`` §enums.item_state. entities.yaml stores this value and
#: explicitly refuses to widen it (``ENT-analysis-task.state_authority``, CR-PC06-02): the
#: legacy names ``claimed``/``done``/``abandoned`` map onto ``running``/``valid``/``failed``
#: and are NOT members here.
_ITEM_STATES = "('pending', 'running', 'retry_wait', 'valid', 'failed', 'unknown_attempt')"

#: ``contracts/state/analysis.yaml`` §enums.attempt_outcome.
_ATTEMPT_OUTCOMES = (
    "('accepted', 'schema_invalid', 'provider_error', 'provider_unavailable', "
    "'timeout_unknown', 'cancelled_stale_lease')"
)

_EXACTLY_ONE_TARGET = (
    "CHECK ((target_kind = 'work' AND target_work_id IS NOT NULL AND target_post_id IS NULL)"
    " OR (target_kind = 'post' AND target_post_id IS NOT NULL AND target_work_id IS NULL))"
)
_TARGET_KEY_AGREES = (
    "CHECK (target_key = target_kind || ':' || COALESCE(target_work_id, target_post_id))"
)

_STATEMENTS: tuple[str, ...] = (
    # -- analysis_generation (MOD-analysis-service) ---------------------------------------
    # One "round" of analysis for one target and one task. Reanalysis opens a NEW row here
    # and keeps the old one (REQ-D26); `reason` is the closed list of legal triggers, and
    # changing a tag is deliberately not among them -- that omission IS invariant I04.
    f"""
    CREATE TABLE analysis_generation (
        id                TEXT NOT NULL PRIMARY KEY,
        owner_id          TEXT NOT NULL REFERENCES owner (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_kind       TEXT NOT NULL CHECK (target_kind IN ('work', 'post')),
        target_work_id    TEXT NULL REFERENCES work (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_post_id    TEXT NULL REFERENCES post (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_key        TEXT NOT NULL,
        task_type         TEXT NOT NULL CHECK (task_type IN {_TASK_TYPES}),
        generation_number INTEGER NOT NULL CHECK (generation_number >= 1),
        reason            TEXT NOT NULL
                               CHECK (reason IN ('initial', 'owner_reanalysis',
                                                 'new_work_version', 'prompt_version_change',
                                                 'schema_version_change')),
        requested_at      TEXT NOT NULL
                               CHECK (requested_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        requested_by      TEXT NOT NULL
                               CHECK (requested_by IN ('system_pipeline', 'owner')),
        {_EXACTLY_ONE_TARGET},
        {_TARGET_KEY_AGREES}
    )
    """,
    # The generation counter is monotonic *per key* and this index is what makes it so.
    """
    CREATE UNIQUE INDEX ux_analysis_generation_key ON analysis_generation
        (owner_id, target_key, task_type, generation_number)
    """,
    # -- assignment_lease (MOD-job-service -- custodian creation, see the header) ----------
    f"""
    CREATE TABLE assignment_lease (
        id              TEXT NOT NULL PRIMARY KEY,
        owner_id        TEXT NOT NULL REFERENCES owner (id)
                             ON DELETE RESTRICT ON UPDATE RESTRICT,
        run_id          TEXT NOT NULL,
        job_id          TEXT NOT NULL,
        worker_identity TEXT NOT NULL
                             CHECK (length(worker_identity) BETWEEN 1 AND 200),
        lease_epoch     INTEGER NOT NULL CHECK (lease_epoch >= 1),
        expires_at      TEXT NOT NULL CHECK (expires_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        state           TEXT NOT NULL
                             CHECK (state IN ('held', 'released', 'expired', 'revoked'))
    )
    """,
    # Monotonic fencing: a re-claim inserts epoch+1 for the same job, so an old epoch can
    # never be re-issued and "is this the current holder" is a lookup, not a judgement (I10).
    """
    CREATE UNIQUE INDEX ux_lease_job_epoch ON assignment_lease (owner_id, job_id, lease_epoch)
    """,
    # -- analysis_attempt (MOD-analysis-service) -------------------------------------------
    # Every try, including the failures and the ones whose outcome is unknown. There is no
    # column here that could make an attempt look like a result: that is invariant I16 in
    # table form, and `COUNT(analysis_attempt)` is the direct oracle for "how many times was
    # the model called" (retry-policy RP-02: the adapter never retries).
    f"""
    CREATE TABLE analysis_attempt (
        id                     TEXT NOT NULL PRIMARY KEY,
        owner_id               TEXT NOT NULL REFERENCES owner (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        analysis_generation_id TEXT NOT NULL REFERENCES analysis_generation (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        attempt_number         INTEGER NOT NULL CHECK (attempt_number >= 1),
        outcome                TEXT NOT NULL CHECK (outcome IN {_ATTEMPT_OUTCOMES}),
        error_code             TEXT NULL
                                    CHECK (error_code IS NULL OR outcome <> 'accepted'),
        started_at             TEXT NOT NULL
                                    CHECK (started_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        ended_at               TEXT NULL
                                    CHECK (ended_at IS NULL
                                           OR ended_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        worker_lease_id        TEXT NULL REFERENCES assignment_lease (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
        cost_uncertain         INTEGER NOT NULL CHECK (cost_uncertain IN (0, 1)),
        -- `timeout_unknown` means the model may already have run and may already have been
        -- billed. The database refuses to record that outcome as cost-certain, so no code
        -- path can claim "no cost was incurred" for something nobody knows (I14,
        -- SRC-PLAN §10 AI_ATTEMPT_UNCERTAIN).
        CHECK (outcome <> 'timeout_unknown' OR cost_uncertain = 1)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_analysis_attempt_gen_number ON analysis_attempt
        (owner_id, analysis_generation_id, attempt_number)
    """,
    # -- analysis_task (MOD-analysis-service, owned_by_package PC06) -----------------------
    # The queue. `claimed_by_worker_identity` / `claimed_lease_id` / `claimed_at` are a
    # POINTER SET, not a state: CR-PC06-02 removed `claimed` from the enum precisely so that
    # "who holds it" could not drift from "what state is it in". The three CHECKs below make
    # that equivalence a database fact rather than a coding convention.
    f"""
    CREATE TABLE analysis_task (
        id                         TEXT NOT NULL PRIMARY KEY,
        owner_id                   TEXT NOT NULL REFERENCES owner (id)
                                        ON DELETE RESTRICT ON UPDATE RESTRICT,
        analysis_generation_id     TEXT NOT NULL REFERENCES analysis_generation (id)
                                        ON DELETE RESTRICT ON UPDATE RESTRICT,
        target_key                 TEXT NOT NULL,
        task_type                  TEXT NOT NULL CHECK (task_type IN {_TASK_TYPES}),
        state                      TEXT NOT NULL CHECK (state IN {_ITEM_STATES}),
        claimed_by_worker_identity TEXT NULL,
        claimed_lease_id           TEXT NULL REFERENCES assignment_lease (id)
                                        ON DELETE RESTRICT ON UPDATE RESTRICT,
        claimed_at                 TEXT NULL
                                        CHECK (claimed_at IS NULL
                                               OR claimed_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        enqueued_at                TEXT NOT NULL
                                        CHECK (enqueued_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        attempt_budget_remaining   INTEGER NOT NULL CHECK (attempt_budget_remaining >= 0),
        CHECK ((claimed_by_worker_identity IS NOT NULL) = (state = 'running')),
        CHECK ((claimed_lease_id IS NOT NULL) = (state = 'running')),
        CHECK ((claimed_at IS NOT NULL) = (state = 'running'))
    )
    """,
    # Partial UNIQUE per `ENT-analysis-task.keys.unique` + `partial_index`: one OPEN task per
    # generation. It guarantees no duplicate queue entry; it does NOT guarantee a result --
    # results live in `analysis` and nowhere else (I16).
    """
    CREATE UNIQUE INDEX ux_analysis_task_open ON analysis_task
        (owner_id, analysis_generation_id)
        WHERE state NOT IN ('valid', 'failed')
    """,
)

_DROPS: tuple[str, ...] = (
    "DROP TABLE analysis_task",
    "DROP TABLE analysis_attempt",
    "DROP TABLE assignment_lease",
    "DROP TABLE analysis_generation",
)


def upgrade() -> None:
    """Create the four tables of the analysis task lifecycle."""
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    """Drop them in reverse dependency order."""
    for statement in _DROPS:
        op.execute(statement)
