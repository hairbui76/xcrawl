"""Per-segment collection budget: stop at 200 posts or 30 minutes, whichever comes first.

The two numbers are ``contracts/retry-policy.yaml`` ``per_run_post_limit`` (200 posts) and
``per_run_duration_limit`` (1800 s). Both are ``ACCEPTED (OD-20260907-01)`` as *working
values* with a measurement still pending after M0 (``REQ-OQ05``), which is why they are
module constants with a decision reference rather than literals buried in the loop: when
the Owner replaces them with measured values, exactly one line changes.

The evaluation rule is fixed by
``contracts/schemas/worker-assignment.schema.json`` ``stop_conditions.evaluation =
"first_of_either"``: whichever threshold is crossed first ends the segment, and ``run``
records *which* one in ``limit_kind``. Recording the kind is not decoration --
``contracts/state/run.yaml`` T-RUN-02 requires ``limit_kind`` alongside ``limit_hit``, and a
segment that stopped on time reads differently to an operator than one that stopped on
volume.

What a limit is not (I13, ``AMD-B02``)
--------------------------------------
Hitting a limit is neither a failure nor a complete sweep of X. ``T-RUN-02`` forbids
``status = failed`` for this case outright, and forbids leaving ``x_coverage_note_vi``
empty when ``limit_hit`` is true. :meth:`SegmentBudget.coverage_note_vi` exists so the
non-empty note is produced by the same object that knows why the segment stopped, rather
than assembled by a caller that might leave it blank.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

#: ``contracts/retry-policy.yaml §budgets.per_run_post_limit`` -- ACCEPTED (OD-20260907-01
#: item 20) as a working value; the measured value arrives after M0 (REQ-OQ05).
PER_RUN_POST_LIMIT = 200

#: ``contracts/retry-policy.yaml §budgets.per_run_duration_limit`` -- 30 minutes, same
#: status and same pending measurement as the post limit.
PER_RUN_DURATION_LIMIT_S = 1800


class LimitKind(str, Enum):
    """Which threshold ended the segment (``run.limit_kind``, ``contracts/state/run.yaml``)."""

    POSTS = "posts"
    DURATION = "duration"


@dataclass
class SegmentBudget:
    """The stop conditions of one collection segment, and the observations against them.

    :param max_posts: ``stop_conditions.max_posts`` from the assignment.
    :param max_duration_s: ``stop_conditions.max_duration_s`` from the assignment.
    :param monotonic: injected clock. A monotonic source, not wall time: the budget must
        not move when the machine's clock is adjusted mid-segment, and a test needs to
        advance time without sleeping.

    ``posts_observed`` counts posts the collector *saw on the source*, not posts it
    ingested. The budget is a ceiling on how much of X this run reads, so a post that was
    read and then deduplicated at ingest still spent budget.
    """

    max_posts: int = PER_RUN_POST_LIMIT
    max_duration_s: int = PER_RUN_DURATION_LIMIT_S
    monotonic: Callable[[], float] = time.monotonic
    posts_observed: int = 0
    _started_at: float = field(default=0.0, init=False)
    _started: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.max_posts < 1 or self.max_duration_s < 1:
            raise ValueError(
                "stop_conditions.max_posts and max_duration_s are both `minimum: 1` in "
                "contracts/schemas/worker-assignment.schema.json"
            )

    @classmethod
    def from_stop_conditions(
        cls,
        stop_conditions: object,
        *,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> SegmentBudget:
        """Build a budget from an assignment's ``stop_conditions`` (model or mapping).

        The assignment is authoritative: the server sends the limits with every assignment
        precisely so the collector does not carry its own idea of them
        (``contracts/ops/collector-probe.md`` §8 preamble). The module constants are only
        the fallback for a payload that omitted them.
        """
        if isinstance(stop_conditions, dict):
            max_posts = int(stop_conditions.get("max_posts", PER_RUN_POST_LIMIT))
            max_duration_s = int(stop_conditions.get("max_duration_s", PER_RUN_DURATION_LIMIT_S))
        else:
            max_posts = int(getattr(stop_conditions, "max_posts", PER_RUN_POST_LIMIT))
            max_duration_s = int(
                getattr(stop_conditions, "max_duration_s", PER_RUN_DURATION_LIMIT_S)
            )
        return cls(max_posts=max_posts, max_duration_s=max_duration_s, monotonic=monotonic)

    def start(self) -> None:
        """Mark the beginning of the segment. Idempotent; a second call does not restart."""
        if not self._started:
            self._started_at = self.monotonic()
            self._started = True

    @property
    def elapsed_s(self) -> int:
        if not self._started:
            return 0
        return int(self.monotonic() - self._started_at)

    def record_observed(self, count: int) -> None:
        """Add posts seen on the source to the budget."""
        if count < 0:
            raise ValueError("observed post count cannot be negative")
        self.posts_observed += count

    @property
    def remaining_posts(self) -> int:
        return max(0, self.max_posts - self.posts_observed)

    def reached(self) -> LimitKind | None:
        """The threshold that has been crossed, or ``None``.

        ``first_of_either``: posts are checked first only because a tie has to resolve
        somehow. A tie is reported as ``posts`` and the note records both numbers, so the
        choice is visible rather than hidden.
        """
        if self.posts_observed >= self.max_posts:
            return LimitKind.POSTS
        if self.elapsed_s >= self.max_duration_s:
            return LimitKind.DURATION
        return None

    def coverage_note_vi(self, kind: LimitKind) -> str:
        """The non-empty Vietnamese coverage note ``T-RUN-02`` requires when a limit is hit.

        It states the ceiling that was reached and says plainly that the rest of the feed
        was not read in this segment -- ``AMD-B05``: "completed" never means all of X was
        swept.
        """
        if kind is LimitKind.POSTS:
            return (
                f"Dừng ở {self.posts_observed} bài theo ngân sách "
                f"({self.max_posts} bài); phần feed sau mốc đó KHÔNG được quét trong đợt này."
            )
        return (
            f"Dừng sau {self.elapsed_s} giây theo ngân sách "
            f"({self.max_duration_s} giây); phần feed sau mốc đó KHÔNG được quét trong đợt này."
        )
