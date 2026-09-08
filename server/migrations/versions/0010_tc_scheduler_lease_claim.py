"""The four tables ``MOD-scheduler``/``MOD-job-service`` own, and two indexes on a fifth.

Revision ID: 0010_tc_scheduler_lease_claim
Revises: 0009_tc_telegram_unknown_delivery
Create Date: 2026-09-08

Card: ``agent-tasks/TC-scheduler-lease-claim.md`` §4 (state effects), §6 (I01/I10/I13).
Source of truth: ``contracts/data/entities.yaml`` for every column, and
``contracts/state/run.yaml`` for the two enums that file says PC03 extends.

``assignment_lease`` is EXTENDED, never recreated
-------------------------------------------------
``0006_tc_analysis_once_per_generation`` created ``assignment_lease`` as **custodian** for a
table whose ``owner_module`` is ``MOD-job-service`` — this card's module — and its header
says in as many words that the scheduler card "must EXTEND this revision rather than issue a
second ``CREATE TABLE assignment_lease``" (``CR-TC-ANALYSIS-01``). There is no second
``CREATE TABLE`` here. All eight contract columns already exist and are correct; what this
revision adds is the one constraint the custodian could not know it needed:

``ux_assignment_lease_one_held``
    ``UNIQUE (owner_id, job_id) WHERE state = 'held'``. ``contracts/state/run.yaml``
    ``lease_model`` LM-02 says "Một job có tối đa một lease ``held``", and the existing
    ``ux_lease_job_epoch`` does **not** say that — it forbids re-issuing the *same* epoch,
    which is a different claim. Without this index, two claimants racing could each insert a
    ``held`` row at epochs 2 and 3 and both believe they hold the job; fixture
    ``collection/f-two-workers-claim-same-assignment.json`` lists "Cấp hai lease ``held`` cho
    cùng job" as a forbidden effect. Now the database refuses it, so "exactly one winner" is
    a property of the schema rather than of the order two transactions happened to run in.

Two things deliberately **not** done to that table
--------------------------------------------------
``run_id`` stays ``NOT NULL``
    ``CR-TC-ANALYSIS-02`` reports that a NOT NULL ``run_id`` is meaningless for an *analysis*
    claim, which is not scoped to a collector run. The dispatch instruction was to relax it
    "only if entities.yaml permits". It does not: ``ENT-assignment-lease`` declares
    ``run_id`` ``nullable: false``. So the column is left exactly as the contract writes it
    and the mismatch is re-filed as ``CR-TC-SCHED-01`` rather than resolved by a migration
    that would put the schema and the contract in disagreement.

``run_id`` gets no ``REFERENCES run (id)``
    It could now — ``run`` exists as of this revision — but adding a foreign key to an
    existing SQLite table requires the 12-step table rebuild, and ``analysis_attempt``
    already points *into* ``assignment_lease``. Rebuilding a parent table under a live child
    reference, to add a constraint no oracle in this card needs, is the larger risk.
    ``CR-TC-SCHED-04``.

Where the enums come from
-------------------------
``run.stop_reason`` carries **eight** values here, not the six spelled out in
``entities.yaml``. That is not an invention: the entity's own constraint text ends with
"(PC03 mở rộng)", and ``contracts/state/run.yaml`` ``enums.stop_reason`` — PC03's file — is
the extended list, adding ``source_layout_changed`` (T-RUN-24) and ``rate_limited``
(T-RUN-25). Both transitions are in the shipped state machine, so a CHECK built from the
shorter list would refuse a row the state machine is required to produce.

``schedule_occurrence.state`` is the reverse case and is decided the other way:
``run.yaml`` CU-04 says an occurrence older than the lookback is marked ``skipped_stale``,
but ``entities.yaml`` declares the enum ``due | coalesced | dispatched | skipped``. The
Coordinator's ruling is that ``entities.yaml`` wins, because it is what the schema gate
reads; the code uses ``skipped`` and the divergence is ``CR-TC-SCHED-03``.

The CHECKs that carry a rule rather than a type
------------------------------------------------
Four constraints below are the state machine written into the table, so that a row which
contradicts ``contracts/state/run.yaml`` cannot be stored even by code that bypasses the
service:

* ``outcome IS NOT NULL`` **exactly** for the three terminal statuses (``terminal_states``
  plus ``enums.outcome.note_vi``: "NOT NULL với mọi trạng thái terminal"). Written as an
  equality of two predicates, so both directions hold — a terminal run without an outcome
  and a running run with one are both refused.
* ``next_attempt_at IS NOT NULL`` exactly when ``status = 'waiting_retry'`` — the contract's
  "NOT NULL khi status = waiting_retry; NULL ở mọi trạng thái khác", which is what stops
  T-RUN-13's "retry_due" guard from reading a stale timestamp left over from an earlier wait.
* ``unblock_condition_vi`` present while ``blocked`` — the Owner-facing sentence T-RUN-23
  requires before ``run.resume`` can mean anything.
* ``x_coverage_note_vi`` non-empty when ``limit_hit`` or ``cursor_invalidated`` — the
  entity's "CẤM để trống" made enforceable, so a partially observed run cannot be displayed
  as if it had seen the whole feed (I13, AMD-B05).
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0010_tc_scheduler_lease_claim"
down_revision: str | None = "0009_tc_telegram_unknown_delivery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

#: ``contracts/state/run.yaml`` §enums. Kept as tuples so the DDL below and
#: ``server/app/jobs/service.py`` cannot drift into two different vocabularies.
_PHASES = "('collecting', 'enriching', 'analyzing', 'reporting')"
_STATUSES = (
    "('queued', 'running', 'waiting_retry', 'needs_user', 'blocked', "
    "'completed', 'failed', 'cancelled')"
)
_TERMINAL = "('completed', 'failed', 'cancelled')"
_OUTCOMES = "('complete', 'partial', 'empty', 'failed', 'cancelled')"
_STOP_REASONS = (
    "('limit_reached', 'captcha', 'session_expired', 'source_blocked', "
    "'storage_unavailable', 'worker_lost', 'source_layout_changed', 'rate_limited')"
)

_STATEMENTS: tuple[str, ...] = (
    # -- run (MOD-job-service) --------------------------------------------------------
    f"""
    CREATE TABLE run (
        id                      TEXT NOT NULL PRIMARY KEY,
        owner_id                TEXT NOT NULL REFERENCES owner (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        trigger_type            TEXT NOT NULL CHECK (trigger_type IN ('scheduled', 'manual')),
        phase                   TEXT NOT NULL CHECK (phase IN {_PHASES}),
        status                  TEXT NOT NULL CHECK (status IN {_STATUSES}),
        outcome                 TEXT NULL CHECK (outcome IS NULL OR outcome IN {_OUTCOMES}),
        stop_reason             TEXT NULL
                                     CHECK (stop_reason IS NULL OR stop_reason IN {_STOP_REASONS}),
        applied_config          TEXT NOT NULL,
        created_at              TEXT NOT NULL
                                     CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        schedule_occurrence_ids TEXT NOT NULL,
        catch_up_window_from    TEXT NULL
                                     CHECK (catch_up_window_from IS NULL
                                            OR catch_up_window_from GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        catch_up_window_to      TEXT NULL
                                     CHECK (catch_up_window_to IS NULL
                                            OR catch_up_window_to GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        current_lease_epoch     INTEGER NOT NULL CHECK (current_lease_epoch >= 0),
        attempt_count           INTEGER NOT NULL CHECK (attempt_count >= 0),
        next_attempt_at         TEXT NULL
                                     CHECK (next_attempt_at IS NULL
                                            OR next_attempt_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        last_error_code         TEXT NULL,
        unblock_condition_vi    TEXT NULL,
        alert_intent_id         TEXT NULL REFERENCES outbox_intent (id)
                                     ON DELETE RESTRICT ON UPDATE RESTRICT,
        observed_window_from    TEXT NULL
                                     CHECK (observed_window_from IS NULL
                                            OR observed_window_from GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        observed_window_to      TEXT NULL
                                     CHECK (observed_window_to IS NULL
                                            OR observed_window_to GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        posts_observed_total    INTEGER NOT NULL CHECK (posts_observed_total >= 0),
        posts_ingested_new      INTEGER NOT NULL CHECK (posts_ingested_new >= 0),
        limit_hit               INTEGER NOT NULL CHECK (limit_hit IN (0, 1)),
        limit_kind              TEXT NULL
                                     CHECK (limit_kind IS NULL
                                            OR limit_kind IN ('posts', 'duration')),
        cursor_invalidated      INTEGER NOT NULL CHECK (cursor_invalidated IN (0, 1)),
        x_coverage_note_vi      TEXT NULL,
        rate_limited_at         TEXT NULL
                                     CHECK (rate_limited_at IS NULL
                                            OR rate_limited_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

        CHECK (length(id) = 26),
        -- The state machine, in both directions. See the module docstring.
        CHECK ((status IN {_TERMINAL}) = (outcome IS NOT NULL)),
        CHECK ((status = 'waiting_retry') = (next_attempt_at IS NOT NULL)),
        CHECK (status <> 'blocked' OR unblock_condition_vi IS NOT NULL),
        CHECK (limit_hit = 0 OR limit_kind IS NOT NULL),
        CHECK ((limit_hit = 0 AND cursor_invalidated = 0)
               OR (x_coverage_note_vi IS NOT NULL AND length(x_coverage_note_vi) > 0))
    )
    """,
    # REQ-AC04: at most one alert intent per run. `entities.yaml` calls this column a
    # convenience pointer and puts the real constraint on `outbox_intent`; the index is
    # created here under the contract's own name because the key list declares it.
    """
    CREATE UNIQUE INDEX ux_run_alert_intent ON run (owner_id, id)
        WHERE alert_intent_id IS NOT NULL
    """,
    # "Is there a run that has not finished?" is asked by `run.run_now` (T-RUN-21),
    # `scheduler.evaluate_due` (CU-05) and the claim path. One index, three questions.
    """
    CREATE INDEX ix_run_owner_status ON run (owner_id, status, created_at)
    """,
    # -- assignment (MOD-job-service) -------------------------------------------------
    f"""
    CREATE TABLE assignment (
        id                    TEXT NOT NULL PRIMARY KEY,
        owner_id              TEXT NOT NULL REFERENCES owner (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        run_id                TEXT NOT NULL REFERENCES run (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        kind                  TEXT NOT NULL CHECK (kind IN ('collect', 'analyze')),
        phase                 TEXT NOT NULL CHECK (phase IN {_PHASES}),
        state                 TEXT NOT NULL
                                   CHECK (state IN ('available', 'claimed', 'done', 'abandoned')),
        required_capabilities TEXT NOT NULL,
        created_at            TEXT NOT NULL
                                   CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

        CHECK (length(id) = 26)
    )
    """,
    # `entities.yaml` gives this key a `partial_index` of its own: the uniqueness holds over
    # OPEN assignments only. Total uniqueness would forbid a run from ever being re-collected
    # after an abandoned attempt, which T-RUN-14 requires it to be.
    """
    CREATE UNIQUE INDEX ux_assignment_open ON assignment (owner_id, run_id, kind, phase)
        WHERE state IN ('available', 'claimed')
    """,
    # -- schedule_occurrence (MOD-scheduler) ------------------------------------------
    f"""
    CREATE TABLE schedule_occurrence (
        id                    TEXT NOT NULL PRIMARY KEY,
        owner_id              TEXT NOT NULL REFERENCES owner (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        due_at                TEXT NOT NULL CHECK (due_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        state                 TEXT NOT NULL
                                   CHECK (state IN ('due', 'coalesced', 'dispatched', 'skipped')),
        coalesced_into_run_id TEXT NULL REFERENCES run (id)
                                   ON DELETE RESTRICT ON UPDATE RESTRICT,
        coalesced_window_from TEXT NULL
                                   CHECK (coalesced_window_from IS NULL
                                          OR coalesced_window_from GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        coalesced_window_to   TEXT NULL
                                   CHECK (coalesced_window_to IS NULL
                                          OR coalesced_window_to GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

        CHECK (length(id) = 26),
        -- entities.yaml: "NOT NULL khi state = 'coalesced' — là bằng chứng của REQ-AC02."
        CHECK (state <> 'coalesced' OR coalesced_into_run_id IS NOT NULL)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_schedule_occurrence_due ON schedule_occurrence (owner_id, due_at)
    """,
    # -- worker_registration (MOD-job-service) ----------------------------------------
    f"""
    CREATE TABLE worker_registration (
        id                TEXT NOT NULL PRIMARY KEY,
        owner_id          TEXT NOT NULL REFERENCES owner (id)
                               ON DELETE RESTRICT ON UPDATE RESTRICT,
        worker_identity   TEXT NOT NULL CHECK (length(worker_identity) BETWEEN 1 AND 200),
        worker_kind       TEXT NOT NULL
                               CHECK (worker_kind IN ('x_collector', 'analysis_worker')),
        capabilities      TEXT NOT NULL,
        last_heartbeat_at TEXT NULL
                               CHECK (last_heartbeat_at IS NULL
                                      OR last_heartbeat_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
        -- I13: `unknown` is a third value, never rendered as `offline`.
        online_state      TEXT NOT NULL
                               CHECK (online_state IN ('online', 'offline', 'unknown')),
        last_run_at       TEXT NULL
                               CHECK (last_run_at IS NULL
                                      OR last_run_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

        CHECK (length(id) = 26)
    )
    """,
    """
    CREATE UNIQUE INDEX ux_worker_registration_identity
        ON worker_registration (owner_id, worker_identity)
    """,
    # -- assignment_lease: EXTEND (see the module docstring) ---------------------------
    """
    CREATE UNIQUE INDEX ux_assignment_lease_one_held
        ON assignment_lease (owner_id, job_id)
        WHERE state = 'held'
    """,
    # The sweep asks "which held leases have expired" every 15 s
    # (retry-policy `lease_expiry_sweep_interval`); without an index that is a table scan on
    # the hot path of every claim.
    """
    CREATE INDEX ix_assignment_lease_expiry ON assignment_lease (owner_id, state, expires_at)
    """,
)

_DOWN: tuple[str, ...] = (
    "DROP INDEX IF EXISTS ix_assignment_lease_expiry",
    "DROP INDEX IF EXISTS ux_assignment_lease_one_held",
    "DROP INDEX IF EXISTS ux_worker_registration_identity",
    "DROP TABLE IF EXISTS worker_registration",
    "DROP INDEX IF EXISTS ux_schedule_occurrence_due",
    "DROP TABLE IF EXISTS schedule_occurrence",
    "DROP INDEX IF EXISTS ux_assignment_open",
    "DROP TABLE IF EXISTS assignment",
    "DROP INDEX IF EXISTS ix_run_owner_status",
    "DROP INDEX IF EXISTS ux_run_alert_intent",
    "DROP TABLE IF EXISTS run",
)


def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    """Drops the four tables this revision created and the two indexes it added.

    ``assignment_lease`` itself is **not** dropped: this revision did not create it, and a
    downgrade that removed another revision's table would leave the graph unable to walk
    back up. Only the two indexes added above are removed.
    """
    for statement in _DOWN:
        op.execute(statement)
