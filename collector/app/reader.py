"""Reading the X feed: the source port, the parser, and the segment loop that knows when to stop.

The narrow port
---------------
:class:`XSource` is the only surface through which this package touches X. It has one
method. Everything above it -- batching, checkpointing, stop reporting -- is driven by
:class:`SegmentRunner` and is exercised in tests against a recorded or synthetic source,
with no browser, no network and no X session. Driving a real Chrome behind this port belongs
to ``TC-x-feasibility-probe`` under gate SP1 (``contracts/ops/collector-probe.md`` §0, §6),
and nothing in this module may be read as evidence about X's real behaviour.

The three rules the loop exists to enforce
------------------------------------------
**I02 -- a checkpoint never runs ahead of durable data.** Items sit in a buffer until a
receipt comes back. When a stop signal arrives, the buffer is *discarded*, not flushed:
``c-challenge-mid-batch`` has 7 posts downloaded and 0 rows written, and §CP-03 says
downloaded-but-not-ingested is not a checkpoint. The one exception is
``source_layout_changed``, where T-RUN-24 explicitly keeps the parseable part ("phần đã bóc
đủ trường VẪN COMMIT bình thường") -- there the request succeeded and the parsed items are
sound; it is the *unparseable* ones that must not be guessed at.

**I10 -- a challenge is never worked around and never auto-resumed.** :meth:`SegmentRunner.
run_segment` reports and returns. There is no claim loop in this module, no retry after
``X_CHALLENGE_REQUIRED``, and no code that interacts with a verification page. Resume is an
Owner action in the app (``run.resume``, T-RUN-10), and the next lease arrives through a
fresh claim.

**I13 -- empty, limited and failed are three different outcomes.** :class:`Completion`
keeps them apart in the return value, so a caller cannot collapse "read the whole feed and
found nothing" into "stopped at a budget" or into "failed".

Resuming
--------
:func:`resume_position` reads the cursor from the **server's** checkpoint in the assignment,
never from anything this process remembered. ``worker-assignment.schema.json``
§x-contract.checkpoint_rule: "Collector KHÔNG được coi con trỏ nội bộ của mình là nguồn sự
thật; khi claim lại, giá trị ở đây thắng." An invalidated cursor means re-reading from the
start is permitted -- ``AMD-B05``/§CP-05 -- because the commitment is "no duplicate
*ingest*", enforced by the server on ``x_post_id``, not "never read twice".
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from rr_contracts.generated.errors import ErrorCode

from collector.app.batcher import (
    MAX_ITEMS_PER_BATCH,
    Batcher,
    CheckpointProposal,
    ingest_item,
)
from collector.app.client import (
    CollectorClient,
    ServerError,
    StopAck,
    WireStopReason,
    new_ulid,
)
from collector.app.limits import LimitKind, SegmentBudget
from collector.app.session import XSessionState


class SourceSignal(str, Enum):
    """What the source said about this page, beyond its contents.

    These are *observations*, not decisions. The mapping from an observation to a stop
    reason lives in :data:`SIGNAL_STOP_REASON`, and the mapping from a stop reason to an
    error code lives in :mod:`collector.app.client` -- one table each, so a wrong pairing is
    a failing assertion rather than a scattered ``if``.
    """

    OK = "ok"
    END_OF_FEED = "end_of_feed"
    CHALLENGE = "challenge"
    SESSION_EXPIRED = "session_expired"
    BLOCKED = "blocked"
    RATE_LIMITED = "rate_limited"


#: Observation -> the ``stop_reason`` the collector reports. ``OK`` and ``END_OF_FEED`` have
#: no entry: neither is a stop reason. Reaching the end of a feed is reported by releasing
#: the assignment with ``completed_phase``, which is why the wire vocabulary has no
#: "finished" value.
SIGNAL_STOP_REASON: dict[SourceSignal, WireStopReason] = {
    SourceSignal.CHALLENGE: WireStopReason.CHALLENGE_REQUIRED,
    SourceSignal.SESSION_EXPIRED: WireStopReason.SESSION_EXPIRED,
    SourceSignal.BLOCKED: WireStopReason.SOURCE_BLOCKED,
    SourceSignal.RATE_LIMITED: WireStopReason.RATE_LIMITED,
}

#: Observation -> the X session state to report on the next heartbeat/registration.
SIGNAL_SESSION_STATE: dict[SourceSignal, XSessionState] = {
    SourceSignal.CHALLENGE: XSessionState.CHALLENGE,
    SourceSignal.SESSION_EXPIRED: XSessionState.EXPIRED,
    SourceSignal.BLOCKED: XSessionState.UNKNOWN,
    SourceSignal.RATE_LIMITED: XSessionState.OK,
}

#: The fields a post must yield before it may be ingested. Wider than the wire schema's
#: ``required`` list by one entry -- ``published_at`` -- and deliberately so:
#: ``a-feed-layout-changed`` names ``author.handle`` and ``published_at`` together as the
#: missing fields that constitute a layout change, so the parser treats a post without a
#: publication time as unreadable rather than ingesting it with the field omitted.
REQUIRED_ITEM_FIELDS: tuple[str, ...] = (
    "x_post_id",
    "author.handle",
    "url",
    "text",
    "published_at",
)

#: How many items on a page may fail to parse before the feed is declared changed.
#:
#: Zero, and that is not a placeholder. The contract leaves the collector no third option
#: for an item whose required fields are missing: T-RUN-24 forbids guessing a value
#: ("Đoán giá trị cho trường không bóc được") and forbids ingesting it hollow ("Ingest item
#: với trường rỗng hoặc bịa"), and I13 forbids showing the result as "no new research". With
#: neither guessing nor silent dropping available, one unreadable item is already a reason
#: to stop and have a person look. A tolerance above zero would be a tuning decision with a
#: measurement behind it; there is no measurement yet (the probe is NOT_RUN), so inventing
#: a threshold here would be exactly the guess the card forbids.
LAYOUT_CHANGE_PARSE_FAILURE_TOLERANCE = 0


@dataclass(frozen=True)
class FeedPage:
    """One page as observed from the source.

    :param raw_posts: raw post records, unparsed. Counted against the budget whether or not
        they parse -- reading them spent the budget.
    :param next_cursor: the cursor for the following page, or ``None`` at the end.
    :param cursor_state: ``valid`` or ``invalidated`` (§CP-05).
    :param signal: what else the source said.
    """

    raw_posts: tuple[Mapping[str, Any], ...] = ()
    next_cursor: str | None = None
    cursor_state: str = "valid"
    signal: SourceSignal = SourceSignal.OK


class XSource(Protocol):
    """The collector's entire view of X.

    One method, on purpose. A wide port would let collection logic leak into the browser
    driver, where it could not be tested without a live session -- and there is no live
    session available to this card at all.
    """

    def fetch_page(self, *, cursor: str | None, query: str) -> FeedPage:
        """Return the next page of results for ``query`` starting at ``cursor``."""
        ...


@dataclass(frozen=True)
class ParsedPage:
    """The result of parsing one page."""

    items: tuple[dict[str, Any], ...]
    missing_required_fields: tuple[str, ...]
    posts_seen: int

    @property
    def posts_parsed_ok(self) -> int:
        return len(self.items)

    @property
    def failed_count(self) -> int:
        return self.posts_seen - self.posts_parsed_ok


def _get_path(raw: Mapping[str, Any], path: str) -> Any:
    current: Any = raw
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def parse_post(
    raw: Mapping[str, Any], *, collected_at: str
) -> tuple[dict[str, Any] | None, list[str]]:
    """Turn one raw post into an ingest item, or report which required fields were missing.

    Never invents a value. A missing field is returned as a *name*, which is what
    T-RUN-24 requires the stop report to carry so a developer knows what to fix.
    """
    missing = [path for path in REQUIRED_ITEM_FIELDS if _get_path(raw, path) in (None, "")]
    if missing:
        return None, missing
    # ``author`` is projected onto the three keys the schema allows rather than forwarded
    # wholesale: ``ingest-batch.schema.json`` §author sets ``additionalProperties: false``,
    # so passing a field the page happened to carry would fail the whole batch on a
    # ``schema_invalid`` pointer that names one item and rejects two hundred.
    source_author = raw["author"]
    author = {
        key: source_author[key]
        for key in ("handle", "display_name", "x_user_id")
        if isinstance(source_author, Mapping) and source_author.get(key) not in (None, "")
    }
    item = ingest_item(
        x_post_id=str(raw["x_post_id"]),
        author=author,
        url=str(raw["url"]),
        text=str(raw["text"]),
        collected_at=str(raw.get("collected_at") or collected_at),
        published_at=str(raw["published_at"]),
        lang=raw.get("lang"),
        media_refs=raw.get("media_refs") or (),
        referenced_links=raw.get("referenced_links") or (),
        thread_context=raw.get("thread_context"),
        source_provenance=raw.get("source_provenance"),
        source_deleted_observed_at=raw.get("source_deleted_observed_at"),
    )
    return item, []


def parse_page(page: FeedPage, *, collected_at: str) -> ParsedPage:
    """Parse a page, collecting the names of every required field that failed to read."""
    items: list[dict[str, Any]] = []
    missing: list[str] = []
    for raw in page.raw_posts:
        item, item_missing = parse_post(raw, collected_at=collected_at)
        if item is None:
            for name in item_missing:
                if name not in missing:
                    missing.append(name)
        else:
            items.append(item)
    return ParsedPage(
        items=tuple(items),
        missing_required_fields=tuple(missing),
        posts_seen=len(page.raw_posts),
    )


def resume_position(assignment: Mapping[str, Any]) -> tuple[str | None, str]:
    """The cursor to resume from, taken from the **server's** checkpoint.

    Returns ``(cursor_token, cursor_state)``. An ``invalidated`` cursor yields ``None``:
    re-reading from the start of the feed is permitted, and the no-duplicate guarantee is
    kept by the server deduplicating on ``x_post_id`` at ingest (``AMD-B05``, §CP-05, and
    the oracle in ``b-cursor-invalidated-reread-dedup``: the measurement is row count, not
    request count).
    """
    checkpoint = assignment.get("checkpoint") or {}
    state = str(checkpoint.get("cursor_state", "valid"))
    if state == "invalidated":
        return None, state
    token = checkpoint.get("cursor_token")
    return (str(token) if token is not None else None), state


class Completion(str, Enum):
    """How a segment ended. Three outcomes that must never be collapsed (I13)."""

    #: The feed ran out. Nothing stopped the run; it simply finished.
    FEED_EXHAUSTED = "feed_exhausted"
    #: A stop condition was reported through ``worker.report_stop``.
    STOPPED = "stopped"
    #: The lease became stale or expired. Nothing further was submitted, and no stop was
    #: reported: a report carrying a dead lease would be rejected too, and the server's
    #: sweep already owns this transition (T-RUN-14).
    LEASE_LOST = "lease_lost"
    #: The server could not write. Nothing was ACKed and the cursor did not advance
    #: (T-RUN-19).
    STORAGE_UNAVAILABLE = "storage_unavailable"


@dataclass
class SegmentOutcome:
    """Everything measurable about one collection segment."""

    completion: Completion
    stop_reason: WireStopReason | None = None
    error_code: ErrorCode | None = None
    limit_kind: LimitKind | None = None
    acked_through_ingest_sequence: int = 0
    checkpoint_sequence: int = 0
    posts_observed_total: int = 0
    posts_ingested_new: int = 0
    posts_deduplicated: int = 0
    posts_discarded_unsubmitted: int = 0
    pages_fetched: int = 0
    batches_submitted: int = 0
    missing_required_fields: tuple[str, ...] = ()
    x_coverage_note_vi: str = ""
    stop_ack: StopAck | None = None
    x_session_state: XSessionState = XSessionState.OK

    @property
    def is_empty(self) -> bool:
        """No posts observed at all. Distinct from limited and from failed (I13)."""
        return self.posts_observed_total == 0


def requires_owner_action(outcome: SegmentOutcome) -> bool:
    """Whether the run now waits for a person, so the collector must not claim again.

    ``challenge_required`` and ``session_expired`` put the run in ``needs_user`` (T-RUN-09),
    and I10 forbids the worker resuming by itself: only ``run.resume`` in the app moves it,
    and only after the Owner has dealt with the challenge in the Chrome window
    (T-RUN-10 guard). ``source_blocked`` and ``source_layout_changed`` land in ``blocked``
    and also need a person -- an unblocking condition or a fixed parser.
    """
    return outcome.stop_reason in {
        WireStopReason.CHALLENGE_REQUIRED,
        WireStopReason.SESSION_EXPIRED,
        WireStopReason.SOURCE_BLOCKED,
        WireStopReason.SOURCE_LAYOUT_CHANGED,
    }


@dataclass
class SegmentRunner:
    """Runs one collection segment for one assignment, then stops.

    One segment, one object, and no loop back to ``claim``: the runner cannot re-acquire
    work, which is the structural form of I10. A supervisor that wants another segment
    claims again itself -- and after a ``needs_user`` stop, :func:`requires_owner_action`
    tells it not to.

    :param clock: returns the current UTC timestamp as an RFC 3339 millisecond string. The
        collector stamps ``collected_at``; ``discovered_at`` is the *server's* to assign
        (``contracts/ports.yaml`` ``ingest.submit_batch``), and this class never sends one.
    :param monotonic: budget clock, separate from ``clock`` so wall-clock adjustment cannot
        shorten or extend a segment.
    """

    client: CollectorClient
    source: XSource
    assignment: Mapping[str, Any]
    clock: Callable[[], str]
    monotonic: Callable[[], float]
    query: str = ""
    #: How many parsed items accumulate before a batch is submitted. The ceiling is the
    #: schema's ``items.maxItems``; a deployment picks something smaller so that a segment
    #: interrupted mid-way has already made most of its work durable. The size is what
    #: decides how much sits in RAM when a challenge arrives -- and that buffer is exactly
    #: what §CP-03 says is not a checkpoint.
    batch_size: int = MAX_ITEMS_PER_BATCH
    _stop_report_id: str = field(default="", init=False)

    def __post_init__(self) -> None:
        if not self.query:
            tags = (self.assignment.get("search_config") or {}).get("tags") or []
            self.query = " OR ".join(str(tag) for tag in tags)

    @property
    def stop_report_id(self) -> str:
        """One id per segment, minted once and reused on every repeat report.

        The idempotency scope of ``worker.report_stop`` is ``assignment_id +
        stop_report_id``. Reusing the id is what makes a second report answer
        ``alert_intent_created: false`` instead of creating the second alert REQ-AC04
        forbids -- so this is a stable property, never a fresh ULID per call.
        """
        if not self._stop_report_id:
            self._stop_report_id = new_ulid()
        return self._stop_report_id

    def run_segment(self) -> SegmentOutcome:  # noqa: C901 - one loop, one exit table
        """Collect until a stop condition, then report it. Never resumes by itself."""
        assignment_id = str(self.assignment["assignment_id"])
        lease = self.assignment.get("lease") or {}
        lease_id = str(lease["lease_id"])
        lease_epoch = int(lease["lease_epoch"])
        heartbeat_interval_s = int(lease.get("heartbeat_interval_s", 30))
        checkpoint = self.assignment.get("checkpoint") or {}

        budget = SegmentBudget.from_stop_conditions(
            self.assignment.get("stop_conditions") or {}, monotonic=self.monotonic
        )
        budget.start()

        batcher = Batcher(
            assignment_id=assignment_id,
            job_id=str(self.assignment.get("job_id") or self.assignment["run_id"]),
            lease_id=lease_id,
            lease_epoch=lease_epoch,
            run_id=str(self.assignment["run_id"]),
            max_items=self.batch_size,
        )

        outcome = SegmentOutcome(
            completion=Completion.FEED_EXHAUSTED,
            acked_through_ingest_sequence=int(checkpoint.get("acked_through_ingest_sequence", 0)),
            checkpoint_sequence=int(checkpoint.get("checkpoint_sequence", 0)),
        )
        cursor, cursor_state = resume_position(self.assignment)
        last_heartbeat = self.monotonic()

        while True:
            elapsed_since_beat = self.monotonic() - last_heartbeat
            if elapsed_since_beat >= heartbeat_interval_s:
                try:
                    response = self.client.heartbeat(
                        assignment_id=assignment_id,
                        lease_id=lease_id,
                        lease_epoch=lease_epoch,
                        posts_seen_in_run=budget.posts_observed,
                        posts_submitted_in_run=outcome.posts_ingested_new,
                        elapsed_s=budget.elapsed_s,
                        x_session_state=outcome.x_session_state.value,
                    )
                except ServerError as error:
                    if error.is_lease_lost:
                        outcome.completion = Completion.LEASE_LOST
                        outcome.error_code = error.code
                        outcome.posts_discarded_unsubmitted += batcher.discard_pending()
                        return outcome
                    raise
                last_heartbeat = self.monotonic()
                beat = response.get("heartbeat_response") or response
                if beat.get("directive", "continue") != "continue":
                    outcome.completion = Completion.LEASE_LOST
                    outcome.posts_discarded_unsubmitted += batcher.discard_pending()
                    return outcome

            page = self.source.fetch_page(cursor=cursor, query=self.query)
            outcome.pages_fetched += 1

            if page.signal in SIGNAL_STOP_REASON:
                # I02/§CP-03: whatever is buffered was downloaded, never ingested, and is
                # therefore not a checkpoint. It is dropped, not flushed.
                outcome.posts_discarded_unsubmitted += batcher.discard_pending()
                outcome.x_session_state = SIGNAL_SESSION_STATE[page.signal]
                return self._report(
                    outcome,
                    reason=SIGNAL_STOP_REASON[page.signal],
                    assignment_id=assignment_id,
                    lease_id=lease_id,
                    lease_epoch=lease_epoch,
                    budget=budget,
                )

            parsed = parse_page(page, collected_at=self.clock())
            budget.record_observed(parsed.posts_seen)
            outcome.posts_observed_total = budget.posts_observed
            for item in parsed.items:
                batcher.add(item)

            layout_changed = parsed.failed_count > LAYOUT_CHANGE_PARSE_FAILURE_TOLERANCE
            limit = budget.reached()
            at_end = page.signal is SourceSignal.END_OF_FEED or page.next_cursor is None

            if batcher.pending_count and (
                batcher.is_full or layout_changed or limit is not None or at_end
            ):
                try:
                    self._submit(batcher, outcome, page, cursor_state, assignment_id)
                except ServerError as error:
                    if error.is_lease_lost:
                        outcome.completion = Completion.LEASE_LOST
                        outcome.error_code = error.code
                        return outcome
                    if error.code is ErrorCode.STORAGE_WRITE_FAILED:
                        # T-RUN-19: nothing was ACKed, so the cursor does not move and the
                        # buffer is kept rather than dropped. No stop is reported: the
                        # server observed its own storage failure.
                        outcome.completion = Completion.STORAGE_UNAVAILABLE
                        outcome.error_code = error.code
                        return outcome
                    raise

            if layout_changed:
                outcome.missing_required_fields = parsed.missing_required_fields
                return self._report(
                    outcome,
                    reason=WireStopReason.SOURCE_LAYOUT_CHANGED,
                    assignment_id=assignment_id,
                    lease_id=lease_id,
                    lease_epoch=lease_epoch,
                    budget=budget,
                    extra={
                        "missing_required_fields": list(parsed.missing_required_fields),
                        "posts_seen": parsed.posts_seen,
                        "posts_parsed_ok": parsed.posts_parsed_ok,
                    },
                )

            if limit is not None:
                outcome.limit_kind = limit
                outcome.x_coverage_note_vi = budget.coverage_note_vi(limit)
                return self._report(
                    outcome,
                    reason=WireStopReason.LIMIT_REACHED,
                    assignment_id=assignment_id,
                    lease_id=lease_id,
                    lease_epoch=lease_epoch,
                    budget=budget,
                    extra={
                        "limit_kind": limit.value,
                        "posts_observed_total": budget.posts_observed,
                        "x_coverage_note_vi": outcome.x_coverage_note_vi,
                    },
                )

            if at_end:
                self._close_feed(
                    outcome,
                    assignment_id=assignment_id,
                    lease_id=lease_id,
                    lease_epoch=lease_epoch,
                    cursor=page.next_cursor,
                    cursor_state=page.cursor_state,
                )
                return outcome

            cursor = page.next_cursor
            cursor_state = page.cursor_state

    # ------------------------------------------------------------- internals

    def _submit(
        self,
        batcher: Batcher,
        outcome: SegmentOutcome,
        page: FeedPage,
        cursor_state: str,
        assignment_id: str,
    ) -> None:
        """Submit the buffer and adopt the server's checkpoint acknowledgement.

        The values written back onto ``outcome`` come from ``receipt.checkpoint_ack`` --
        the server's numbers, not the collector's. That is the operational form of
        "checkpoint đã ACK" (§CP-02): the collector's own count of what it sent is never
        the source of truth for what is durable.
        """
        proposal = CheckpointProposal(
            phase="collecting",
            cursor_token=page.next_cursor,
            cursor_state=cursor_state,
            items_collected_in_run=outcome.posts_observed_total,
        )
        batch = batcher.build(request_id=new_ulid(), proposal=proposal)
        if batch is None:
            return
        receipt = self.client.submit_batch(batch, assignment_id=assignment_id)
        outcome.batches_submitted += 1
        counts = receipt.get("counts") or {}
        outcome.posts_ingested_new += int(counts.get("inserted", 0))
        outcome.posts_deduplicated += int(counts.get("deduplicated", 0))
        ack = receipt.get("checkpoint_ack") or {}
        outcome.acked_through_ingest_sequence = int(
            ack.get("acked_through_ingest_sequence", outcome.acked_through_ingest_sequence)
        )
        outcome.checkpoint_sequence = int(
            ack.get("checkpoint_sequence", outcome.checkpoint_sequence)
        )

    def _close_feed(
        self,
        outcome: SegmentOutcome,
        *,
        assignment_id: str,
        lease_id: str,
        lease_epoch: int,
        cursor: str | None,
        cursor_state: str,
    ) -> None:
        """End of feed: advance the cursor only, then hand the assignment back.

        The proposed sequence is exactly ``outcome.acked_through_ingest_sequence`` -- the
        number the last receipt gave. §CP-07's guard rejects a proposal beyond the committed
        mark, and passing anything else here would be I02's own counterexample.
        """
        outcome.completion = Completion.FEED_EXHAUSTED
        answer = self.client.commit_checkpoint(
            assignment_id=assignment_id,
            checkpoint_seq=outcome.checkpoint_sequence + 1,
            lease_id=lease_id,
            lease_epoch=lease_epoch,
            cursor_token=cursor,
            cursor_state=cursor_state,
            proposed_acked_through_ingest_sequence=outcome.acked_through_ingest_sequence,
            reason="end_of_feed",
        )
        receipt = answer.get("receipt") or {}
        ack = receipt.get("checkpoint_ack") or {}
        if ack:
            outcome.checkpoint_sequence = int(
                ack.get("checkpoint_sequence", outcome.checkpoint_sequence)
            )
            outcome.acked_through_ingest_sequence = int(
                ack.get("acked_through_ingest_sequence", outcome.acked_through_ingest_sequence)
            )
        self.client.release_assignment(
            assignment_id=assignment_id,
            lease_id=lease_id,
            lease_epoch=lease_epoch,
            release_reason="completed_phase",
        )

    def _report(
        self,
        outcome: SegmentOutcome,
        *,
        reason: WireStopReason,
        assignment_id: str,
        lease_id: str,
        lease_epoch: int,
        budget: SegmentBudget,
        extra: Mapping[str, Any] | None = None,
    ) -> SegmentOutcome:
        """Report the stop and return. No retry, no re-claim, no further source reads."""
        from collector.app.client import STOP_REASON_ERROR_CODE

        outcome.completion = Completion.STOPPED
        outcome.stop_reason = reason
        outcome.error_code = STOP_REASON_ERROR_CODE[reason]
        payload: dict[str, Any] = dict(extra or {})
        if outcome.posts_discarded_unsubmitted:
            payload.setdefault("posts_downloaded_not_ingested", outcome.posts_discarded_unsubmitted)
        if reason is WireStopReason.RATE_LIMITED and not outcome.x_coverage_note_vi:
            # T-RUN-25 forbids an empty coverage note here and requires it to name the
            # moment: "x_coverage_note_vi ... bắt buộc nhắc mốc run.rate_limited_at".
            rate_limited_at = self.clock()
            outcome.x_coverage_note_vi = (
                f"Nguồn X báo giới hạn nhịp lúc {rate_limited_at}; đợt thu thập dừng tại đó "
                "và phần feed sau mốc đó KHÔNG được quét trong đợt này."
            )
            payload.setdefault("rate_limited_at", rate_limited_at)
            payload.setdefault("x_coverage_note_vi", outcome.x_coverage_note_vi)
        outcome.stop_ack = self.client.report_stop(
            assignment_id=assignment_id,
            stop_report_id=self.stop_report_id,
            lease_id=lease_id,
            lease_epoch=lease_epoch,
            stop_reason=reason,
            last_acked_ingest_sequence=outcome.acked_through_ingest_sequence,
            extra=payload,
        )
        outcome.posts_observed_total = budget.posts_observed
        return outcome


class RecordedSource:
    """An :class:`XSource` that replays a fixed list of pages and counts its own reads.

    Lives beside the port rather than in a test file because both test modules need it and
    because the read counter is the oracle for "no new collection requests after the stop"
    (``c-challenge-mid-batch`` and ``a-feed-layout-changed`` both measure exactly that).
    It never touches a browser, a network or an X session.
    """

    def __init__(self, pages: Sequence[FeedPage]) -> None:
        self._pages = list(pages)
        self.reads: list[str | None] = []

    @property
    def read_count(self) -> int:
        return len(self.reads)

    def fetch_page(self, *, cursor: str | None, query: str) -> FeedPage:
        self.reads.append(cursor)
        if not self._pages:
            return FeedPage(signal=SourceSignal.END_OF_FEED)
        return self._pages.pop(0)
