"""E1/E2 — SC02/SC34: many missed slots become **one** catch-up run; DST makes neither two nor none.

Fixtures used as oracles, not paraphrased:

``reporting/f-three-offline-periods-one-catchup.json``  three missed slots → one run
``collection/j-dst-boundary-occurrences.json``          the gap hour and the repeated hour
``collection/i-run-now-while-active.json``              five "run now" presses → one run

The clock is an argument everywhere
------------------------------------
Card §8 asks for a fake clock, and it is not a testing convenience: every claim in this file
is about time. "Three periods were missed" needs a machine that was off for three days;
"a repeated local hour produces one occurrence" needs to sit on a DST boundary; "an occurrence
older than seven days is skipped" needs a week. ``scheduler.evaluate_due`` takes ``now`` as a
parameter and :class:`~server.app.jobs.service.JobContext` takes a ``clock`` callable, so all
of that is observable without waiting.

Timezone: the fixture is deliberate about what it does not fix
---------------------------------------------------------------
``collection/j``'s ``given`` says its timezone is *"Một IANA timezone CÓ DST do Owner chọn"* —
some DST zone, chosen by the Owner — and notes that the configured default
``Asia/Ho_Chi_Minh`` has no DST, so DST-01/DST-02 are correct but dormant today. This file
therefore uses ``America/New_York`` for the two DST tests (a zone with a real spring-forward
gap and a real fall-back repeat) and ``Asia/Ho_Chi_Minh`` everywhere else. That is not a
choice about the product: card §10 ``SG-02`` keeps the schedule in settings, and both values
are passed in as configuration.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from alembic import command
from alembic.config import Config
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.jobs.lease import JobError, timestamp_utc_ms
from server.app.jobs.service import (
    JobContext,
    cancel_run,
    coalesce_overdue,
    enqueue_scheduled_run,
    record_stale_occurrences,
    run_now,
)
from server.app.scheduler.evaluator import (
    CATCH_UP_LOOKBACK_MAX_SECONDS,
    ScheduleSettings,
    coalesce_window_id,
    enumerate_occurrences,
    evaluate_due,
    occurrence_id,
    resolve_local_to_utc,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "acceptance" / "fixtures"

OWNER_ID = "01JW0WNER00000000000000000"
HCM = "Asia/Ho_Chi_Minh"
#: A zone with a real DST gap and a real repeat. `collection/j` deliberately leaves the zone
#: abstract ("some IANA timezone with DST"), so the test picks one; nothing about the product
#: depends on it.
DST_ZONE = "America/New_York"

SLOTS = ("08:00", "20:00")


# --- harness ----------------------------------------------------------------------------------


def _upgrade(db_path: Path) -> None:
    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(db_path)
    try:
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    db_path = tmp_path / "radar.db"
    _upgrade(db_path)
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at, password_hash, password_updated_at, failed_login_count, "
                "locked_until) VALUES (:id, 1, 'owner', 'Asia/Ho_Chi_Minh', "
                "'2026-09-01T00:00:00.000Z', 'x', '2026-09-01T00:00:00.000Z', 0, NULL)"
            ),
            {"id": OWNER_ID},
        )
    try:
        yield engine
    finally:
        engine.dispose()


class FakeClock:
    """A clock the test moves by hand. Card §8: "Fake clock: lịch tới hạn lúc T…"."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **delta: float) -> None:
        self.now = self.now + timedelta(**delta)


def context(engine: Engine, clock: FakeClock, *, timezone: str = HCM) -> JobContext:
    counter = {"n": 0}

    def ids() -> str:
        counter["n"] += 1
        return f"01JTEST{counter['n']:019d}"[:26]

    return JobContext(
        engine=engine,
        owner_id=OWNER_ID,
        settings=ScheduleSettings(slots_local=SLOTS, timezone_iana=timezone),
        clock=clock,
        id_factory=ids,
    )


def count(engine: Engine, sql: str, **params: Any) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql), params).scalar_one())


def load(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURE_ROOT / f"{name}.json").read_text(encoding="utf-8"))
    return data


# --- SC02: three offline periods, one catch-up run --------------------------------------------


def test_three_missed_periods_produce_exactly_one_run(engine) -> None:
    """Fixture ``reporting/f``: *"Ba mốc quá hạn GỘP thành MỘT run (REQ-D15). Không chạy dồn
    ba đợt."*

    The oracle is a count, not a log line: one run row, and its
    ``schedule_occurrence_ids`` carries all three. ``schedule_max_runs_per_catch_up = 1``.
    """
    fixture = load("reporting/f-three-offline-periods-one-catchup")
    assert fixture["expected"]["counts"]["run created by event 2"] == 1

    clock = FakeClock(datetime(2026, 9, 7, 3, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    evaluation = evaluate_due(owner_id=OWNER_ID, now=clock.now, settings=ctx.settings)
    overdue = evaluation.due[-3:]
    assert len(overdue) == 3

    result = coalesce_overdue(ctx, occurrences=overdue)

    assert result["created"] is True
    assert count(engine, "SELECT COUNT(*) FROM run WHERE owner_id = :o", o=OWNER_ID) == 1
    with engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    "SELECT schedule_occurrence_ids, catch_up_window_from, catch_up_window_to, "
                    "trigger_type, status FROM run WHERE id = :id"
                ),
                {"id": result["run_id"]},
            )
            .mappings()
            .one()
        )
    assert len(json.loads(row["schedule_occurrence_ids"])) == 3
    assert row["trigger_type"] == "scheduled"
    assert row["status"] == "queued"
    assert row["catch_up_window_from"] == min(o.due_at for o in overdue)
    assert row["catch_up_window_to"] == max(o.due_at for o in overdue)


def test_the_six_occurrence_case_the_contract_states_as_its_oracle(engine) -> None:
    """``catch_up.oracle_vi``: machine off Monday to Thursday, slots 08:00 and 20:00, six
    overdue occurrences ⇒ ``COUNT(run) = 1`` and ``len(schedule_occurrence_ids) = 6``.

    Stated in the contract with those exact numbers, so it is run with those exact numbers.
    """
    clock = FakeClock(datetime(2026, 9, 10, 9, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    overdue = enumerate_occurrences(
        owner_id=OWNER_ID,
        settings=ctx.settings,
        since=clock.now - timedelta(days=3),
        until=clock.now,
    )[-6:]
    assert len(overdue) == 6
    assert len({o.occurrence_id for o in overdue}) == 6, "six slots, six distinct identities"
    assert [o.resolved_utc for o in overdue] == sorted(o.resolved_utc for o in overdue)

    result = coalesce_overdue(ctx, occurrences=overdue)

    assert count(engine, "SELECT COUNT(*) FROM run WHERE owner_id = :o", o=OWNER_ID) == 1
    with engine.connect() as connection:
        ids = json.loads(
            connection.execute(
                text("SELECT schedule_occurrence_ids FROM run WHERE id = :id"),
                {"id": result["run_id"]},
            ).scalar_one()
        )
    assert len(ids) == 6
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM schedule_occurrence WHERE owner_id = :o AND state = 'coalesced'",
            o=OWNER_ID,
        )
        == 6
    )


def test_coalescing_the_same_overdue_set_twice_is_a_replay(engine) -> None:
    """Idempotency key ``coalesce_window_id`` — derived from the sorted occurrence set.

    The second call returns the first run and creates nothing, which is what stops a scheduler
    that restarts mid-pass from running the catch-up twice.
    """
    clock = FakeClock(datetime(2026, 9, 7, 3, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    overdue = evaluate_due(owner_id=OWNER_ID, now=clock.now, settings=ctx.settings).due[-3:]

    first = coalesce_overdue(ctx, occurrences=overdue)
    second = coalesce_overdue(ctx, occurrences=list(reversed(overdue)))

    assert (
        first["coalesce_window_id"] == second["coalesce_window_id"] == coalesce_window_id(overdue)
    )
    assert first["run_id"] == second["run_id"]
    assert second["created"] is False
    assert count(engine, "SELECT COUNT(*) FROM run WHERE owner_id = :o", o=OWNER_ID) == 1


def test_an_occurrence_older_than_the_lookback_is_skipped_not_coalesced(engine) -> None:
    """CU-04: past ``schedule_catch_up_lookback_max`` (7 days) a slot is ``skipped``.

    ``REQ-D16`` forbids sending old digests, so a three-week-old slot must not join a catch-up
    window. The state written is ``skipped``: ``run.yaml`` calls it ``skipped_stale`` but
    ``entities.yaml`` closes the enum without that value, and the Coordinator ruled
    ``entities.yaml`` wins (``CR-TC-SCHED-03``).
    """
    clock = FakeClock(datetime(2026, 9, 20, 3, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    evaluation = evaluate_due(owner_id=OWNER_ID, now=clock.now, settings=ctx.settings)

    assert evaluation.stale, "no occurrence fell outside the lookback"
    for occurrence in evaluation.stale:
        age = (clock.now - occurrence.resolved_utc).total_seconds()
        assert age > CATCH_UP_LOOKBACK_MAX_SECONDS
    for occurrence in evaluation.due:
        age = (clock.now - occurrence.resolved_utc).total_seconds()
        assert age <= CATCH_UP_LOOKBACK_MAX_SECONDS

    recorded = record_stale_occurrences(ctx, occurrences=evaluation.stale)

    assert recorded == len(evaluation.stale)
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM schedule_occurrence WHERE owner_id = :o AND state = 'skipped'",
            o=OWNER_ID,
        )
        == recorded
    )
    assert count(engine, "SELECT COUNT(*) FROM run WHERE owner_id = :o", o=OWNER_ID) == 0


def test_nothing_is_due_before_its_slot(engine) -> None:
    """``earliest_run_semantics`` + ``schedule_coalescing_window = 0`` lookahead.

    A slot time is the earliest a run **may** start (``REQ-D13``), so no occurrence resolves
    into ``due`` while its instant is still in the future. A positive lookahead would run a
    slot early, which is the one thing that rule forbids.
    """
    clock = FakeClock(datetime(2026, 9, 7, 0, 5, tzinfo=UTC))  # 07:05 local, before 08:00
    ctx = context(engine, clock)
    evaluation = evaluate_due(owner_id=OWNER_ID, now=clock.now, settings=ctx.settings)
    for occurrence in evaluation.due:
        assert occurrence.resolved_utc <= clock.now


def test_a_new_slot_while_a_run_is_active_does_not_create_a_second_run(engine) -> None:
    """CU-05: the occurrence waits for the next catch-up window instead of starting a run.

    It stays ``due`` rather than ``skipped`` — it has not expired, it is queued behind the run
    that is already going.
    """
    clock = FakeClock(datetime(2026, 9, 7, 3, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    first = evaluate_due(owner_id=OWNER_ID, now=clock.now, settings=ctx.settings).due[-1:]
    enqueue_scheduled_run(ctx, occurrences=first)
    assert count(engine, "SELECT COUNT(*) FROM run WHERE owner_id = :o", o=OWNER_ID) == 1

    clock.advance(hours=13)  # the next slot arrives
    later = evaluate_due(
        owner_id=OWNER_ID,
        now=clock.now,
        settings=ctx.settings,
        known_occurrence_ids=[o.occurrence_id for o in first],
    ).due[-1:]
    result = enqueue_scheduled_run(ctx, occurrences=later)

    assert result["created"] is False
    assert result["reason"] == "run_already_active"
    assert count(engine, "SELECT COUNT(*) FROM run WHERE owner_id = :o", o=OWNER_ID) == 1
    with engine.connect() as connection:
        state = connection.execute(
            text("SELECT state FROM schedule_occurrence WHERE id = :id"),
            {"id": later[0].occurrence_id},
        ).scalar_one()
    assert state == "due"


# --- SC34: DST ---------------------------------------------------------------------------------


def test_a_missing_local_hour_still_produces_exactly_one_occurrence() -> None:
    """DST-01, spring forward. Fixture ``collection/j``: *"KHÔNG bỏ occurrence."*

    2026-03-08 in ``America/New_York``: 02:00 jumps to 03:00, so 02:30 never happens. The
    contract's formula is ``min{ t : local(t) >= nominal }``, which is the transition instant
    — 07:00 UTC — and the assertion checks that instant rather than only that something was
    produced. Dropping the slot would open a coverage hole for that day.
    """
    tz = ZoneInfo(DST_ZONE)
    resolved = resolve_local_to_utc(datetime(2026, 3, 8, 2, 30), tz)

    assert resolved == datetime(2026, 3, 8, 7, 0, tzinfo=UTC)
    local = resolved.astimezone(tz)
    assert (local.hour, local.minute) == (3, 0), "the resolved instant is the end of the gap"
    assert local.replace(tzinfo=None) >= datetime(2026, 3, 8, 2, 30)


def test_a_repeated_local_hour_produces_one_occurrence_at_the_first_instant() -> None:
    """DST-02, fall back. *"lấy lần xuất hiện ĐẦU (instant UTC nhỏ hơn)."*

    2026-11-01 in ``America/New_York``: 01:30 happens twice, at 05:30 UTC (EDT) and 06:30 UTC
    (EST). The rule takes the earlier. Both candidate instants are asserted so the test shows
    there really were two to choose between.
    """
    tz = ZoneInfo(DST_ZONE)
    nominal = datetime(2026, 11, 1, 1, 30)
    first = nominal.replace(tzinfo=tz, fold=0).astimezone(UTC)
    second = nominal.replace(tzinfo=tz, fold=1).astimezone(UTC)
    assert first != second, "the fixture's premise moved: this hour no longer repeats"

    resolved = resolve_local_to_utc(nominal, tz)

    assert resolved == min(first, second) == datetime(2026, 11, 1, 5, 30, tzinfo=UTC)


def test_the_occurrence_id_is_a_function_of_the_nominal_local_time_not_the_instant() -> None:
    """The forbidden effect fixture ``collection/j`` names in as many words.

    *"Suy ``schedule_occurrence_id`` từ instant UTC đã giải thay vì từ giờ địa phương danh
    nghĩa — làm vậy thì giờ lặp sinh hai id."* The repeated hour has two UTC instants and one
    nominal local time; this asserts that the id follows the second, which is what makes
    ``COUNT(run) = 1`` structural rather than lucky.
    """
    identical = occurrence_id(
        owner_id=OWNER_ID,
        slot_key="01:30",
        nominal_local_date=datetime(2026, 11, 1).date(),
        nominal_local_time=datetime(2026, 11, 1, 1, 30).time(),
    )
    again = occurrence_id(
        owner_id=OWNER_ID,
        slot_key="01:30",
        nominal_local_date=datetime(2026, 11, 1).date(),
        nominal_local_time=datetime(2026, 11, 1, 1, 30).time(),
    )
    other_day = occurrence_id(
        owner_id=OWNER_ID,
        slot_key="01:30",
        nominal_local_date=datetime(2026, 11, 2).date(),
        nominal_local_time=datetime(2026, 11, 1, 1, 30).time(),
    )
    assert identical == again
    assert identical != other_day
    assert len(identical) == 26


def test_each_dst_boundary_slot_enqueues_exactly_one_run(engine) -> None:
    """Fixture ``collection/j`` counts: two nominal slots, two occurrences, two runs, none
    skipped, ``runs_per_nominal_slot: 1``.

    Both boundary days are walked through the real ``job.enqueue_scheduled_run``, with the run
    cancelled between them so CU-05 does not (correctly) suppress the second — the fixture is
    about DST, not about concurrency.
    """
    fixture = load("collection/j-dst-boundary-occurrences")
    expected = fixture["expected"]["counts"]
    assert expected["runs_per_nominal_slot"] == 1
    assert expected["occurrences_skipped"] == 0

    clock = FakeClock(datetime(2026, 3, 8, 12, 0, tzinfo=UTC))
    ctx = context(engine, clock, timezone=DST_ZONE)
    tz = ZoneInfo(DST_ZONE)

    runs: list[str] = []
    for day, slot in ((datetime(2026, 3, 8), "02:30"), (datetime(2026, 11, 1), "01:30")):
        nominal_time = datetime.strptime(slot, "%H:%M").time()
        resolved = resolve_local_to_utc(datetime.combine(day.date(), nominal_time), tz)
        clock.now = resolved + timedelta(hours=1)
        occurrence = type(
            evaluate_due(owner_id=OWNER_ID, now=clock.now, settings=ctx.settings).due[0]
        )(
            occurrence_id=occurrence_id(
                owner_id=OWNER_ID,
                slot_key=slot,
                nominal_local_date=day.date(),
                nominal_local_time=nominal_time,
            ),
            slot_key=slot,
            nominal_local_date=day.date(),
            nominal_local_time=nominal_time,
            resolved_utc=resolved,
        )
        result = enqueue_scheduled_run(ctx, occurrences=[occurrence])
        assert result["created"] is True, slot
        runs.append(result["run_id"])
        cancel_run(ctx, run_id=result["run_id"])

    assert len(set(runs)) == expected["run_total"] == 2
    assert (
        count(engine, "SELECT COUNT(*) FROM schedule_occurrence WHERE owner_id = :o", o=OWNER_ID)
        == expected["schedule_occurrence_total"]
        == 2
    )
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM schedule_occurrence WHERE owner_id = :o AND state = 'skipped'",
            o=OWNER_ID,
        )
        == 0
    )


# --- SC33: run.run_now while a run is active ---------------------------------------------------


def test_five_run_now_presses_produce_no_new_run(engine) -> None:
    """Fixture ``collection/i``: five presses, two channels, ``run_created_by_these_events: 0``.

    ``run_now_active_run_policy = coalesce``: each call returns the existing ``run_id`` with a
    reason, and none of them is an error — ``ports.yaml`` promised "bấm lặp trả run đang có",
    so answering 409 to the second press would break the contract as surely as creating a
    second run would.
    """
    fixture = load("collection/i-run-now-while-active")
    expected = fixture["expected"]["counts"]
    assert expected["run_created_by_these_events"] == 0
    assert expected["run_total"] == 1

    clock = FakeClock(datetime(2026, 9, 7, 3, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    first = run_now(ctx, request_id="01JREQ0000000000000000000A")
    assert first["created"] is True

    answers = [run_now(ctx, request_id=f"01JREQ000000000000000000{i}") for i in range(1, 6)]

    assert {answer["run_id"] for answer in answers} == {first["run_id"]}
    assert all(answer["created"] is False for answer in answers)
    assert count(engine, "SELECT COUNT(*) FROM run WHERE owner_id = :o", o=OWNER_ID) == 1
    assert (
        count(engine, "SELECT COUNT(*) FROM assignment_lease WHERE owner_id = :o", o=OWNER_ID) == 0
    )


def test_run_now_on_a_needs_user_run_changes_nothing(engine) -> None:
    """Card §8: *"``run.run_now`` trên run ``needs_user`` ⇒ transition log **rỗng**."*

    T-RUN-11 and B10/AMD-B10. The whole run row is compared before and after, so "changed
    nothing" is measured rather than inferred from the absence of an exception. Fixture
    ``collection/i``'s forbidden effects list "Resume một run đang ``needs_user``" explicitly.
    """
    clock = FakeClock(datetime(2026, 9, 7, 3, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    created = run_now(ctx, request_id="01JREQ0000000000000000000A")
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE run SET status = 'needs_user', stop_reason = 'captcha' WHERE id = :id"),
            {"id": created["run_id"]},
        )
    before = _run_snapshot(engine, created["run_id"])

    answer = run_now(ctx, request_id="01JREQ0000000000000000000B")

    assert answer["run_id"] == created["run_id"]
    assert answer["created"] is False
    assert answer["status"] == "needs_user"
    assert _run_snapshot(engine, created["run_id"]) == before


def _run_snapshot(engine: Engine, run_id: str) -> tuple[Any, ...]:
    with engine.connect() as connection:
        return tuple(
            connection.execute(
                text(
                    "SELECT status, phase, outcome, stop_reason, current_lease_epoch, "
                    "attempt_count, next_attempt_at FROM run WHERE id = :id"
                ),
                {"id": run_id},
            ).one()
        )


def test_run_now_without_a_request_id_is_a_validation_error(engine) -> None:
    """``ports.yaml`` makes ``request_id`` the idempotency key; without it there is none."""
    clock = FakeClock(datetime(2026, 9, 7, 3, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    with pytest.raises(JobError) as raised:
        run_now(ctx, request_id="")
    assert raised.value.code is ErrorCode.VALIDATION_ERROR


# --- settings, not literals (card §10 SG-02) ---------------------------------------------------


def test_the_schedule_has_no_default_slots_or_timezone() -> None:
    """A schedule this module invented would be a number the Owner owns, decided here.

    ``REQ-OQ05`` still re-measures 08:00/20:00 after M0, so :class:`ScheduleSettings` refuses
    to be constructed without them rather than falling back to a value that looks official.
    """
    with pytest.raises(TypeError):
        ScheduleSettings()  # type: ignore[call-arg]
    with pytest.raises(ValueError, match="slots_local is empty"):
        ScheduleSettings(slots_local=(), timezone_iana=HCM)
    with pytest.raises(ValueError, match="not HH:MM"):
        ScheduleSettings(slots_local=("8:00",), timezone_iana=HCM)


def test_the_applied_config_snapshot_records_the_schedule_the_run_used(engine) -> None:
    """``run.applied_config`` is immutable after the run leaves ``queued``.

    A run re-read later must show the limits it actually ran under, not the ones Settings
    holds today, so the snapshot is taken at creation.
    """
    clock = FakeClock(datetime(2026, 9, 7, 3, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    created = run_now(ctx, request_id="01JREQ0000000000000000000A")
    with engine.connect() as connection:
        config = json.loads(
            connection.execute(
                text("SELECT applied_config FROM run WHERE id = :id"), {"id": created["run_id"]}
            ).scalar_one()
        )
    assert config["schedule_slots_local"] == list(SLOTS)
    assert config["schedule_timezone"] == HCM
    assert config["per_run_post_limit"] == 200
    assert config["per_run_duration_limit_s"] == 1800


def test_the_due_at_written_is_the_resolved_utc_instant(engine) -> None:
    """AMD-B08: every stored timestamp is UTC with millisecond precision.

    The slot is local; the column is UTC. Asserted by re-resolving the nominal time and
    comparing strings, so a row stored in local time would fail here rather than shift a run
    by seven hours.
    """
    clock = FakeClock(datetime(2026, 9, 7, 3, 0, tzinfo=UTC))
    ctx = context(engine, clock)
    due = evaluate_due(owner_id=OWNER_ID, now=clock.now, settings=ctx.settings).due[-1:]
    enqueue_scheduled_run(ctx, occurrences=due)
    with engine.connect() as connection:
        stored = connection.execute(
            text("SELECT due_at FROM schedule_occurrence WHERE id = :id"),
            {"id": due[0].occurrence_id},
        ).scalar_one()
    expected = resolve_local_to_utc(
        datetime.combine(due[0].nominal_local_date, due[0].nominal_local_time),
        ZoneInfo(HCM),
    )
    assert stored == timestamp_utc_ms(expected) == due[0].due_at
