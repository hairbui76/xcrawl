"""``MOD-scheduler`` — ``scheduler.evaluate_due``: which schedule slots are due, and when.

Pure and read-only. ``contracts/ports.yaml`` types ``scheduler.evaluate_due`` as
``mutation: false`` with the note *"Không ghi; chỉ tính toán"*, so there is no database
handle and no clock in this module: ``now`` is an argument. That is what makes the DST rules
and the seven-day catch-up window testable at all — a fake clock is not a testing
convenience here, it is the only way to observe a schedule that spans days.

The three questions this module answers
---------------------------------------
1. **What instant does a nominal local time resolve to?** ``contracts/state/run.yaml``
   ``schedule_model.dst_rules`` gives two formulas, and this module implements them as
   formulas rather than as special cases — see :func:`resolve_local_to_utc`.
2. **What is an occurrence's identity?** ``occurrence_identity.rule_vi``: derived from
   ``(owner_id, slot_key, nominal_local_date, nominal_local_time)`` — from the **nominal
   local time**, never from the resolved UTC instant. That single sentence is what stops a
   repeated hour from producing two occurrences, and :func:`occurrence_id` is where it lives.
3. **Which of them are due, and which are too old?** ``earliest_run_semantics`` (a slot time
   is the earliest a run *may* start, not a deadline) plus ``catch_up`` CU-01 and CU-04.

Numbers come from settings, never from here
--------------------------------------------
Card §10 ``SG-02``: 08:00/20:00 and ``Asia/Ho_Chi_Minh`` are values the Owner accepted
(``OD-20260907-01``), and ``REQ-OQ05`` still has to re-measure after M0 — so they are read
from configuration, not written into code. :class:`ScheduleSettings` has **no defaults for
the slots or the timezone**: a deployment that configured neither gets a ``TypeError`` at
construction rather than a scheduler quietly running on this file's opinion. The two window
sizes do carry the ``contracts/retry-policy.yaml`` values as defaults, because those are
server mechanics rather than Owner-facing schedule choices, and each names its contract key.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

#: ``contracts/retry-policy.yaml`` §budgets.schedule_catch_up_lookback_max — 7 days.
#: An occurrence older than this is ``skipped``, never coalesced (CU-04).
CATCH_UP_LOOKBACK_MAX_SECONDS: int = 604800

#: ``contracts/retry-policy.yaml`` §budgets.schedule_coalescing_window — **0** seconds of
#: lookahead, deliberately: coalescing a slot that has not arrived yet would run it before
#: its "earliest allowed" instant, which is the one thing ``REQ-D13`` forbids.
COALESCING_LOOKAHEAD_SECONDS: int = 0

#: Crockford base32, the alphabet ULIDs use. Occurrence ids are *derived*, not random, so
#: they are built from this alphabet rather than from ``os.urandom``.
_CROCKFORD32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: ``entities.yaml`` types every id as ``string_ulid`` and the migration enforces
#: ``length(id) = 26``.
_ULID_LENGTH = 26


def _timestamp_utc_ms(moment: datetime) -> str:
    """RFC 3339, UTC, exactly three fractional digits — the ``timestamp_utc_ms`` shape."""
    aware = moment.astimezone(UTC)
    return f"{aware.strftime('%Y-%m-%dT%H:%M:%S')}.{aware.microsecond // 1000:03d}Z"


# --------------------------------------------------------------------------------------
# DST: the two rules of contracts/state/run.yaml, as formulas
# --------------------------------------------------------------------------------------


def _local_naive(instant: datetime, tz: ZoneInfo) -> datetime:
    return instant.astimezone(tz).replace(tzinfo=None)


def _first_instant_at_or_after(
    nominal: datetime, tz: ZoneInfo, low: datetime, high: datetime
) -> datetime:
    """``min{ t ∈ [low, high] : local(t) >= nominal }``, by bisection on the instant axis.

    Used only for the spring-forward gap. A closed-form answer would have to know where the
    transition is and by how much the offset moved, which is exactly the knowledge the tz
    database holds and this module should not duplicate; bisection asks the tz database the
    only question that matters — "what is the local time at this instant?" — and converges in
    about fifty steps at millisecond resolution.

    ``local(t)`` is non-decreasing in ``t`` for every real timezone (a jump forward skips
    local times; a jump back is handled by :func:`resolve_local_to_utc` before it gets here),
    so the predicate is monotone and the bisection has a single answer. That is the same
    ``determinism_vi`` the contract claims for DST-01: "Một nghiệm duy nhất."
    """
    lo, hi = low, high
    while (hi - lo) > timedelta(milliseconds=1):
        mid = lo + (hi - lo) / 2
        if _local_naive(mid, tz) >= nominal:
            hi = mid
        else:
            lo = mid
    return hi


def resolve_local_to_utc(nominal_local: datetime, tz: ZoneInfo) -> datetime:
    """Resolve a **nominal local** wall-clock time to the single UTC instant it means.

    Three cases, and the contract names all three
    (``contracts/state/run.yaml`` ``schedule_model.dst_rules``):

    ordinary
        The local time exists exactly once. Both folds agree; return either.

    DST-02, repeated hour (fall back)
        The local time happens twice. ``fold=0`` is the earlier instant and ``fold=1`` the
        later one. The rule takes the **first** occurrence — ``min{ t : local(t) == nominal }``
        — because it is the only choice that is both deterministic and does not add a run.

    DST-01, missing hour (spring forward)
        The local time never happens: converting with the pre-transition offset lands
        *after* the transition, so ``fold=0`` yields a **later** instant than ``fold=1``.
        The occurrence is not dropped — dropping it would open a coverage hole for that day —
        it runs at ``min{ t : local(t) >= nominal }``, which is the transition instant itself.

    ``nominal_local`` must be naive; passing an aware datetime is a programming error, and
    silently ignoring its tzinfo would resolve a slot against the wrong clock.
    """
    if nominal_local.tzinfo is not None:
        raise ValueError("nominal_local must be a naive wall-clock time, not an aware one")
    earlier = nominal_local.replace(tzinfo=tz, fold=0).astimezone(UTC)
    later = nominal_local.replace(tzinfo=tz, fold=1).astimezone(UTC)
    if earlier <= later:
        # Ordinary (equal) or repeated (earlier < later): DST-02 takes the first.
        return earlier
    # Gap: `earlier` overshoots the transition and `later` falls before it, so the answer is
    # bracketed by [later, earlier] and is the first instant whose local time reaches nominal.
    return _first_instant_at_or_after(nominal_local, tz, later, earlier)


# --------------------------------------------------------------------------------------
# Occurrence identity
# --------------------------------------------------------------------------------------


def occurrence_id(
    *, owner_id: str, slot_key: str, nominal_local_date: date, nominal_local_time: time
) -> str:
    """A deterministic 26-character id for one schedule slot on one local day.

    ``occurrence_identity.rule_vi`` derives it from ``(owner_id, slot_key,
    nominal_local_date, nominal_local_time)`` — **not** from the resolved UTC instant. Both
    halves of that sentence do work:

    *Deterministic* makes ``job.enqueue_scheduled_run``'s idempotency key
    (``schedule_occurrence_id``) meaningful across process restarts: the same slot on the
    same local day is the same row, so an evaluator that runs twice cannot enqueue twice.

    *From the nominal local time* is what survives DST. A repeated hour resolves to two UTC
    instants; if the id were derived from the instant, that hour would produce two ids and
    therefore two runs, which fixture ``collection/j-dst-boundary-occurrences.json`` lists as
    a forbidden effect in exactly those words.

    A SHA-256 of the tuple, rendered in Crockford base32 and truncated to 26 characters. Not
    a real ULID — it carries no timestamp prefix — but it satisfies the column's shape
    (``length(id) = 26``, ``string_ulid``) and it is a *function*, which a ULID is not.
    """
    material = "\x1f".join(
        (owner_id, slot_key, nominal_local_date.isoformat(), nominal_local_time.isoformat())
    ).encode("utf-8")
    digest = int.from_bytes(hashlib.sha256(material).digest(), "big")
    characters = []
    for _ in range(_ULID_LENGTH):
        characters.append(_CROCKFORD32[digest & 0x1F])
        digest >>= 5
    return "".join(reversed(characters))


# --------------------------------------------------------------------------------------
# Settings and results
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ScheduleSettings:
    """The schedule as configured, not as this file imagines it (card §10 ``SG-02``).

    ``slots_local`` and ``timezone_iana`` have **no defaults**. ``08:00``/``20:00`` and
    ``Asia/Ho_Chi_Minh`` are Owner-accepted working values (``OD-20260907-01`` items 20 and
    4) that ``REQ-OQ05`` still has to re-measure after M0, and a default here would be this
    module quietly deciding a number the Owner owns. The caller reads them from settings.
    """

    slots_local: tuple[str, ...]
    timezone_iana: str
    catch_up_lookback_seconds: int = CATCH_UP_LOOKBACK_MAX_SECONDS
    coalescing_lookahead_seconds: int = COALESCING_LOOKAHEAD_SECONDS

    def __post_init__(self) -> None:
        if not self.slots_local:
            raise ValueError("slots_local is empty: a schedule with no slots is not a schedule")
        for slot in self.slots_local:
            parse_slot(slot)
        ZoneInfo(self.timezone_iana)

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_iana)


def parse_slot(slot: str) -> time:
    """``"08:00"`` -> :class:`datetime.time`. Raises on anything else.

    Strict on purpose: ``retry-policy.yaml`` types ``schedule_slots_default`` as
    ``local_time_hh_mm``, and a slot string the parser guessed at would move a run by hours.
    """
    hour_text, _, minute_text = slot.partition(":")
    if not (hour_text.isdigit() and minute_text.isdigit() and len(slot) == 5):
        raise ValueError(f"slot {slot!r} is not HH:MM local time")
    return time(hour=int(hour_text), minute=int(minute_text))


@dataclass(frozen=True, slots=True)
class Occurrence:
    """One schedule slot on one local day, resolved to an instant."""

    occurrence_id: str
    slot_key: str
    nominal_local_date: date
    nominal_local_time: time
    resolved_utc: datetime

    @property
    def due_at(self) -> str:
        """The ``schedule_occurrence.due_at`` column value (``timestamp_utc_ms``)."""
        return _timestamp_utc_ms(self.resolved_utc)


@dataclass(frozen=True, slots=True)
class DueEvaluation:
    """The read-only answer of ``scheduler.evaluate_due``.

    ``due`` and ``stale`` are separate lists rather than one list with a flag because CU-01
    and CU-04 do different things with them: ``due`` occurrences are coalesced into exactly
    one run, ``stale`` ones are recorded as ``skipped`` and shown by
    ``health.get_readiness``. Collapsing them would make it possible to coalesce a
    three-week-old slot, which ``REQ-D16`` forbids.
    """

    due: tuple[Occurrence, ...] = field(default_factory=tuple)
    stale: tuple[Occurrence, ...] = field(default_factory=tuple)

    @property
    def window(self) -> tuple[datetime, datetime] | None:
        """``(catch_up_window_from, catch_up_window_to)`` over the due occurrences."""
        if not self.due:
            return None
        instants = [occurrence.resolved_utc for occurrence in self.due]
        return min(instants), max(instants)


# --------------------------------------------------------------------------------------
# scheduler.evaluate_due
# --------------------------------------------------------------------------------------


def enumerate_occurrences(
    *, owner_id: str, settings: ScheduleSettings, since: datetime, until: datetime
) -> list[Occurrence]:
    """Every occurrence of every slot whose resolved instant falls in ``[since, until]``.

    Enumeration walks **local days**, not UTC days, because a slot is defined in local time;
    walking UTC would drop or duplicate a slot on the days either side of an offset change.
    One extra day is scanned at each end so that a slot near midnight local is not missed by
    the day boundary itself.
    """
    tz = settings.tz
    first_day = _local_naive(since, tz).date() - timedelta(days=1)
    last_day = _local_naive(until, tz).date() + timedelta(days=1)
    found: list[Occurrence] = []
    for slot in settings.slots_local:
        slot_time = parse_slot(slot)
        day = first_day
        while day <= last_day:
            resolved = resolve_local_to_utc(datetime.combine(day, slot_time), tz)
            if since <= resolved <= until:
                found.append(
                    Occurrence(
                        occurrence_id=occurrence_id(
                            owner_id=owner_id,
                            slot_key=slot,
                            nominal_local_date=day,
                            nominal_local_time=slot_time,
                        ),
                        slot_key=slot,
                        nominal_local_date=day,
                        nominal_local_time=slot_time,
                        resolved_utc=resolved,
                    )
                )
            day += timedelta(days=1)
    found.sort(key=lambda occurrence: (occurrence.resolved_utc, occurrence.occurrence_id))
    return found


def evaluate_due(
    *,
    owner_id: str,
    now: datetime,
    settings: ScheduleSettings,
    known_occurrence_ids: Iterable[str] = (),
) -> DueEvaluation:
    """``scheduler.evaluate_due`` — read-only (``contracts/ports.yaml``).

    :param now: the current instant. An argument, not ``datetime.now()``: this operation is
        pure, and a fake clock is the only way to observe a week of missed slots in a test.
    :param known_occurrence_ids: occurrences that already have a row, in any state. They are
        excluded because "due" means *due and not yet turned into an occurrence row*; an
        occurrence that already produced a run must not produce a second one (``REQ-AC02``).

    Splits the result per CU-01 and CU-04:

    ``due``
        Resolved instant in ``[now - catch_up_lookback, now + coalescing_lookahead]``. With
        the contract's lookahead of **0** the upper bound is ``now`` exactly, so nothing runs
        before its slot (``REQ-D13``, ``earliest_run_semantics``).

    ``stale``
        Older than the lookback. Recorded as ``skipped``, **not** coalesced: ``REQ-D16``
        forbids sending old digests, and CU-04 notes these leave no coverage hole because
        coverage is decided by the ``coverage_window`` ledger and not by the schedule (B04).
    """
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware; a naive instant has no meaning here")
    now_utc = now.astimezone(UTC)
    lookback_start = now_utc - timedelta(seconds=settings.catch_up_lookback_seconds)
    horizon = now_utc + timedelta(seconds=settings.coalescing_lookahead_seconds)
    known = set(known_occurrence_ids)

    # The stale window is scanned back one further lookback so that CU-04 can *report*
    # skipped slots instead of silently forgetting them. Two lookbacks is a bounded scan, and
    # an occurrence older than that has long since stopped being actionable.
    scan_start = lookback_start - timedelta(seconds=settings.catch_up_lookback_seconds)
    candidates = enumerate_occurrences(
        owner_id=owner_id, settings=settings, since=scan_start, until=horizon
    )
    due: list[Occurrence] = []
    stale: list[Occurrence] = []
    for occurrence in candidates:
        if occurrence.occurrence_id in known:
            continue
        if occurrence.resolved_utc < lookback_start:
            stale.append(occurrence)
        else:
            due.append(occurrence)
    return DueEvaluation(due=tuple(due), stale=tuple(stale))


def coalesce_window_id(occurrences: Sequence[Occurrence]) -> str:
    """The ``coalesce_window_id`` idempotency key of ``job.coalesce_overdue``.

    Derived from the **set** of occurrence ids being coalesced, so that two evaluators seeing
    the same overdue set compute the same key and the second one is a replay rather than a
    second catch-up run (``schedule_max_runs_per_catch_up = 1``). Sorted before hashing: the
    key must not depend on the order a query happened to return rows in.
    """
    material = "\x1f".join(sorted(o.occurrence_id for o in occurrences)).encode("utf-8")
    digest = int.from_bytes(hashlib.sha256(material).digest(), "big")
    characters = []
    for _ in range(_ULID_LENGTH):
        characters.append(_CROCKFORD32[digest & 0x1F])
        digest >>= 5
    return "".join(reversed(characters))


__all__ = [
    "CATCH_UP_LOOKBACK_MAX_SECONDS",
    "COALESCING_LOOKAHEAD_SECONDS",
    "DueEvaluation",
    "Occurrence",
    "ScheduleSettings",
    "coalesce_window_id",
    "enumerate_occurrences",
    "evaluate_due",
    "occurrence_id",
    "parse_slot",
    "resolve_local_to_utc",
]
