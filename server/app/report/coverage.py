"""Coverage windows: half-open ``[from, to)``, contiguous, and the CAS the publisher runs on.

``contracts/reporting/time-and-tags.md`` §4 is the whole of this module. The three sentences
it exists to keep true:

1. **Every window is half-open and every window touches its predecessor.** ``window_from[n] =
   window_to[n-1]`` *and* ``ingest_sequence_from[n] = ingest_sequence_to[n-1]`` (§4.2, §4.9
   O-4.1). Both, not either: two items in the same millisecond are only separable on the
   sequence axis, so the timestamp pair alone cannot decide membership (§4.3).
2. **Coverage advances only at the publish commit** (§4.4). An aborted build --
   ``TAG_VERSION_STALE``, ``EMBEDDING_GENERATION_MISMATCH``, a crash -- writes no window at
   all, so the same data is reconsidered by the next build.
3. **An empty period still writes a window** (§4.7, AMD-B04). Skipping it is what puts a hole
   in the chain, and a hole is how "we never looked" becomes indistinguishable from "we looked
   and found nothing".

Why this module also carries the package's shared primitives
------------------------------------------------------------
Card §3 gives this card four files: ``builder.py``, ``publisher.py``, ``coverage.py`` and
``router.py``. A fifth ``errors.py``/``ids.py`` would be outside the write set, so the error
type, the ULID/timestamp helpers and the JCS canonicaliser live here, in the module the other
three already depend on. They are deliberately at the top of the file and separated by a
banner; nothing about them is coverage-specific.

What is a **port** here and why
-------------------------------
:class:`IngestWatermarkPort` exists because §4.3's watermark is defined over *allocated*
sequence numbers ("a sequence allocated but not yet committed blocks the watermark there"),
and no entity in ``contracts/data/entities.yaml`` records an allocation that has not
committed. :class:`CommittedRowsWatermark` therefore answers the question it *can* answer --
the highest committed sequence -- and a deployment that grows a real allocator injects a port
that also knows the outstanding ones. The gap is reported as ``CR-TC-REPORT-03`` rather than
papered over by pretending the committed maximum is the same thing.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from sqlalchemy import Connection, text

# ======================================================================================
# Shared primitives (see the module docstring for why they live in this file)
# ======================================================================================

_CROCKFORD32: Final = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: ``contracts/reporting/selection.md`` §1: the version of the selection algorithm, written
#: immutably into ``report.selection_version``. Changing any rule of §3-§8 bumps this.
SELECTION_VERSION: Final = "0.1.0"

#: ``contracts/schemas/report.schema.json`` ``schema_version``: a const, never "latest".
REPORT_SCHEMA_VERSION: Final = "0.1.0"


def new_ulid() -> str:
    """A ULID: 48-bit millisecond timestamp, 80 bits of randomness, Crockford base32."""
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD32[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def utc_now_ms() -> str:
    """``timestamp_utc_ms``: RFC 3339, UTC, exactly three fractional digits (§1.1)."""
    return to_timestamp_utc_ms(datetime.now(UTC))


def to_timestamp_utc_ms(moment: datetime) -> str:
    """Render a datetime in the one persisted timestamp shape the contract allows."""
    utc = moment.astimezone(UTC)
    return f"{utc.strftime('%Y-%m-%dT%H:%M:%S')}.{utc.microsecond // 1000:03d}Z"


def parse_timestamp_utc_ms(value: str) -> datetime:
    """Inverse of :func:`to_timestamp_utc_ms`. Rejects anything that is not the exact shape.

    §1.1 is explicit that a microsecond timestamp, a non-``Z`` offset or a missing millisecond
    field is refused **at the boundary** rather than rounded silently: a value that was
    rounded on the way in cannot be compared against a window edge afterwards.
    """
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
        raise ValueError(f"not a timestamp_utc_ms: {value!r}") from exc
    if not value.endswith("Z") or len(value) != 24:
        raise ValueError(f"not a timestamp_utc_ms: {value!r}")
    return parsed


def plus_one_millisecond(value: str) -> str:
    return to_timestamp_utc_ms(parse_timestamp_utc_ms(value) + timedelta(milliseconds=1))


def minus_one_millisecond(value: str) -> str:
    return to_timestamp_utc_ms(parse_timestamp_utc_ms(value) - timedelta(milliseconds=1))


def canonical_json(value: Any) -> str:
    """RFC 8785 (JCS) subset: sorted keys, no insignificant whitespace, UTF-8, no NaN.

    The subset is the same one ``contracts/schemas/saved-snapshot.schema.json`` pins and the
    same one ``server/app/saved/snapshot.py`` implements: this module re-implements it rather
    than importing that one because ``MOD-report-service -> MOD-saved-service`` is not an edge
    in ``contracts/modules.yaml`` and ``ENF-import-rule`` is enforced by imports.

    Known limitation, stated rather than hidden: Python's ``repr`` for floats is shortest
    round-trip, which agrees with JCS for every value this codebase produces (scores are
    rounded to 4 decimals before serialisation) but is not a full ES6 ``Number::toString``.
    """
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def content_hash_of(content: Mapping[str, Any]) -> str:
    """``"sha256:" + sha256(JCS(content))`` -- the value stored in ``report.content_hash``.

    This is the oracle of I05: it is computed once, inside the publish transaction, and every
    later read recomputes it from the stored read model and must get the same string. Delivery
    never writes to ``report``, so a changed hash means someone mutated a published period.
    """
    digest = hashlib.sha256(canonical_json(content).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


_HTTP_STATUS: Final[dict[ErrorCode, int]] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.TAG_VERSION_STALE: 409,
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: 409,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}

#: ``details_safe_keys`` of ``contracts/errors.yaml``, copied per code. The envelope rule is
#: "unknown key => the producer refuses it rather than sending it", so it is enforced in the
#: constructor: a key that leaked a table name or a tag text could then never be serialised,
#: not even once.
DETAILS_SAFE_KEYS: Final[dict[ErrorCode, frozenset[str]]] = {
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"caller_module", "callee_module", "forbidden_edge_ref"}),
    ErrorCode.NOT_FOUND: frozenset({"operation_id", "resource_kind"}),
    ErrorCode.CONFLICT: frozenset(
        {
            "resource_kind",
            "expected_predecessor_id",
            "current_predecessor_id",
            "attempt_number",
            "retry_after_ms",
        }
    ),
    ErrorCode.IDEMPOTENCY_CONFLICT: frozenset(
        {"idempotency_key", "payload_hash_seen", "payload_hash_stored"}
    ),
    ErrorCode.TAG_VERSION_STALE: frozenset(
        {
            "report_build_id",
            "expected_tag_config_version_id",
            "current_tag_config_version_id",
            "rebuild_attempt",
        }
    ),
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: frozenset(
        {"expected_generation_id", "seen_generation_id", "dimension_expected", "dimension_seen"}
    ),
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
    ErrorCode.INTERNAL: frozenset({"correlation_id", "operation_id"}),
}

_MESSAGE_SAFE: Final[dict[ErrorCode, str]] = {
    ErrorCode.VALIDATION_ERROR: "Yêu cầu không hợp lệ.",
    ErrorCode.UNAUTHORIZED: "Bạn cần đăng nhập để xem báo cáo.",
    ErrorCode.FORBIDDEN_EDGE: "Lời gọi này không nằm trong các kết nối được phép.",
    ErrorCode.NOT_FOUND: "Không tìm thấy kỳ báo cáo được yêu cầu.",
    ErrorCode.CONFLICT: "Một tiến trình khác vừa ghi trước. Hệ thống đọc lại và thử lại.",
    ErrorCode.IDEMPOTENCY_CONFLICT: "Khóa chống trùng đã được dùng cho một nội dung khác.",
    ErrorCode.TAG_VERSION_STALE: "Bộ tag đã đổi trong lúc dựng kỳ báo cáo. Sẽ dựng lại.",
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: (
        "Thế hệ vector đã đổi trong lúc dựng kỳ báo cáo; không trộn hai thế hệ."
    ),
    ErrorCode.STORAGE_WRITE_FAILED: "Hệ thống đang không ghi được dữ liệu. Chưa có gì được lưu.",
    ErrorCode.INTERNAL: "Có lỗi không mong đợi.",
}


class ReportError(Exception):
    """A refusal carrying one registered error code and the ``contracts/errors.yaml`` envelope.

    Nothing here may carry a tag text, a post body, a table name or a SQL string: the envelope
    contract's ``forbidden_content_vi`` closes ``details_safe`` to all of them, and the
    constructor enforces the key allowlist so a mistake fails at construction rather than on
    the wire.
    """

    def __init__(
        self,
        code: ErrorCode,
        *,
        message_safe: str | None = None,
        details_safe: Mapping[str, Any] | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        self.code = code
        self.message_safe = message_safe or _MESSAGE_SAFE.get(
            code, _MESSAGE_SAFE[ErrorCode.INTERNAL]
        )
        self.details_safe = dict(details_safe or {})
        self.retry_after_ms = retry_after_ms
        unknown = set(self.details_safe) - DETAILS_SAFE_KEYS.get(code, frozenset())
        if unknown:
            raise ValueError(f"{code.value} may not carry details keys {sorted(unknown)}")
        super().__init__(f"{code.value}: {self.message_safe}")

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        body: dict[str, Any] = {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
        }
        if self.retry_after_ms is not None:
            body["retry_after_ms"] = self.retry_after_ms
        return body


# ======================================================================================
# Coverage proper
# ======================================================================================


@dataclass(frozen=True, slots=True)
class CoverageWindow:
    """One row of ``coverage_window`` (``ENT-coverage-window``)."""

    id: str
    owner_id: str
    sequence: int
    window_from: str
    window_to: str
    ingest_sequence_from: int
    ingest_sequence_to: int
    predecessor_window_id: str | None
    report_id: str | None
    advanced_at: str

    @property
    def spans_no_items(self) -> bool:
        """``ingest_sequence_from == ingest_sequence_to`` -- the half-open span is empty."""
        return self.ingest_sequence_from == self.ingest_sequence_to


@dataclass(frozen=True, slots=True)
class WindowPlan:
    """The window a build intends to write, computed at the build snapshot (§4.3).

    It is a *plan*, not a row: nothing is written until the publish transaction commits, which
    is the whole content of §4.4. The publisher turns it into a row (or discards it, when the
    build aborts) and nothing else may.
    """

    sequence: int
    window_from: str
    window_to: str
    ingest_sequence_from: int
    ingest_sequence_to: int
    predecessor_window_id: str | None
    snapshot_taken_at: str

    @property
    def spans_no_items(self) -> bool:
        return self.ingest_sequence_from == self.ingest_sequence_to


class IngestWatermarkPort(Protocol):
    """§4.3 rule 1: the largest ``W`` such that every sequence in ``[1, W]`` has **committed**.

    See the module docstring: the "allocated but not committed" half of the rule has no entity
    behind it, so the default implementation cannot observe it and says so.
    """

    def contiguous_watermark(self, connection: Connection, owner_id: str) -> int: ...

    def discovered_at_of(
        self, connection: Connection, owner_id: str, ingest_sequence: int
    ) -> str | None: ...

    def earliest_discovered_at(self, connection: Connection, owner_id: str) -> str | None: ...


class CommittedRowsWatermark:
    """The watermark visible from committed rows alone.

    ``post.ingest_sequence`` and ``work.ingest_sequence`` are one shared monotone series per
    owner (``entities.yaml``; §1.3), so both tables are unioned. The answer is the maximum
    committed value, and :attr:`outstanding_floor` lets a caller that *does* know about an
    in-flight allocation clamp it -- which is the only honest way to express §4.3 rule 1 on a
    schema with no allocation table (``CR-TC-REPORT-03``).
    """

    def __init__(self, *, outstanding_floor: int | None = None) -> None:
        #: The lowest sequence known to be allocated but not committed, or ``None``.
        self.outstanding_floor = outstanding_floor

    _MAX_SQL = text(
        "SELECT MAX(seq) FROM ("
        "  SELECT ingest_sequence AS seq FROM post WHERE owner_id = :owner"
        "  UNION ALL"
        "  SELECT ingest_sequence AS seq FROM work WHERE owner_id = :owner"
        ")"
    )
    _AT_SQL = text(
        "SELECT ts FROM ("
        "  SELECT ingest_sequence AS seq, discovered_at AS ts FROM post WHERE owner_id = :owner"
        "  UNION ALL"
        "  SELECT ingest_sequence AS seq, first_discovered_at AS ts FROM work"
        "   WHERE owner_id = :owner"
        ") WHERE seq = :seq ORDER BY ts LIMIT 1"
    )
    _MIN_TS_SQL = text(
        "SELECT MIN(ts) FROM ("
        "  SELECT discovered_at AS ts FROM post WHERE owner_id = :owner"
        "  UNION ALL"
        "  SELECT first_discovered_at AS ts FROM work WHERE owner_id = :owner"
        ")"
    )

    def contiguous_watermark(self, connection: Connection, owner_id: str) -> int:
        highest = connection.execute(self._MAX_SQL, {"owner": owner_id}).scalar()
        watermark = int(highest or 0)
        if self.outstanding_floor is not None:
            watermark = min(watermark, self.outstanding_floor - 1)
        return max(watermark, 0)

    def discovered_at_of(
        self, connection: Connection, owner_id: str, ingest_sequence: int
    ) -> str | None:
        row = connection.execute(self._AT_SQL, {"owner": owner_id, "seq": ingest_sequence}).scalar()
        return None if row is None else str(row)

    def earliest_discovered_at(self, connection: Connection, owner_id: str) -> str | None:
        row = connection.execute(self._MIN_TS_SQL, {"owner": owner_id}).scalar()
        return None if row is None else str(row)


class CoverageRepository:
    """Every read and write of ``coverage_window``, in one place.

    The insert is the CAS. It carries no "check then write" pre-read on purpose: the arbiter
    is ``ux_coverage_window_predecessor``, and a pre-read would move the decision out of the
    database and into a race (§4.6).
    """

    def current_window(self, connection: Connection, owner_id: str) -> CoverageWindow | None:
        """The pointer: the window with the highest ``sequence`` for this owner."""
        row = (
            connection.execute(
                text(
                    "SELECT id, owner_id, sequence, window_from, window_to, ingest_sequence_from,"
                    "       ingest_sequence_to, predecessor_window_id, report_id, advanced_at"
                    "  FROM coverage_window WHERE owner_id = :owner"
                    " ORDER BY sequence DESC LIMIT 1"
                ),
                {"owner": owner_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else _window(dict(row))

    def window(self, connection: Connection, window_id: str) -> CoverageWindow | None:
        row = (
            connection.execute(
                text(
                    "SELECT id, owner_id, sequence, window_from, window_to, ingest_sequence_from,"
                    "       ingest_sequence_to, predecessor_window_id, report_id, advanced_at"
                    "  FROM coverage_window WHERE id = :id"
                ),
                {"id": window_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else _window(dict(row))

    def windows_in_order(self, connection: Connection, owner_id: str) -> list[CoverageWindow]:
        rows = (
            connection.execute(
                text(
                    "SELECT id, owner_id, sequence, window_from, window_to, ingest_sequence_from,"
                    "       ingest_sequence_to, predecessor_window_id, report_id, advanced_at"
                    "  FROM coverage_window WHERE owner_id = :owner ORDER BY sequence"
                ),
                {"owner": owner_id},
            )
            .mappings()
            .all()
        )
        return [_window(dict(row)) for row in rows]

    def window_for_report(
        self, connection: Connection, owner_id: str, report_id: str
    ) -> CoverageWindow | None:
        row = (
            connection.execute(
                text(
                    "SELECT id, owner_id, sequence, window_from, window_to, ingest_sequence_from,"
                    "       ingest_sequence_to, predecessor_window_id, report_id, advanced_at"
                    "  FROM coverage_window WHERE owner_id = :owner AND report_id = :report"
                ),
                {"owner": owner_id, "report": report_id},
            )
            .mappings()
            .first()
        )
        return None if row is None else _window(dict(row))

    def count(self, connection: Connection, owner_id: str) -> int:
        return int(
            connection.execute(
                text("SELECT COUNT(*) FROM coverage_window WHERE owner_id = :owner"),
                {"owner": owner_id},
            ).scalar()
            or 0
        )

    def insert_window(
        self,
        connection: Connection,
        *,
        window_id: str,
        owner_id: str,
        plan: WindowPlan,
        report_id: str | None,
        advanced_at: str,
    ) -> CoverageWindow:
        """Write the window. **This statement is the CAS**; a UNIQUE violation means loss.

        The caller does not catch the ``IntegrityError`` here -- the publisher does, because
        losing the CAS is a state transition (``T-RP-05``) and not merely a failed insert.
        """
        connection.execute(
            text(
                "INSERT INTO coverage_window (id, owner_id, sequence, window_from, window_to,"
                "  ingest_sequence_from, ingest_sequence_to, predecessor_window_id, report_id,"
                "  advanced_at) VALUES (:id, :owner, :sequence, :wfrom, :wto, :ifrom, :ito,"
                "  :pred, :report, :advanced)"
            ),
            {
                "id": window_id,
                "owner": owner_id,
                "sequence": plan.sequence,
                "wfrom": plan.window_from,
                "wto": plan.window_to,
                "ifrom": plan.ingest_sequence_from,
                "ito": plan.ingest_sequence_to,
                "pred": plan.predecessor_window_id,
                "report": report_id,
                "advanced": advanced_at,
            },
        )
        return CoverageWindow(
            id=window_id,
            owner_id=owner_id,
            sequence=plan.sequence,
            window_from=plan.window_from,
            window_to=plan.window_to,
            ingest_sequence_from=plan.ingest_sequence_from,
            ingest_sequence_to=plan.ingest_sequence_to,
            predecessor_window_id=plan.predecessor_window_id,
            report_id=report_id,
            advanced_at=advanced_at,
        )


def _window(row: Mapping[str, Any]) -> CoverageWindow:
    return CoverageWindow(
        id=str(row["id"]),
        owner_id=str(row["owner_id"]),
        sequence=int(row["sequence"]),
        window_from=str(row["window_from"]),
        window_to=str(row["window_to"]),
        ingest_sequence_from=int(row["ingest_sequence_from"]),
        ingest_sequence_to=int(row["ingest_sequence_to"]),
        predecessor_window_id=(
            None if row["predecessor_window_id"] is None else str(row["predecessor_window_id"])
        ),
        report_id=None if row["report_id"] is None else str(row["report_id"]),
        advanced_at=str(row["advanced_at"]),
    )


def coverage_predecessor_matches(
    connection: Connection,
    *,
    owner_id: str,
    expected_predecessor_id: str | None,
    repository: CoverageRepository | None = None,
) -> bool:
    """Predicate 1 of the publish CAS (``contracts/state/report.yaml`` ``ownership_boundary``).

    True when the pointer is still the window the build read. Pure: it reads committed state,
    writes nothing and calls no network -- the three properties ``interface_contract_vi``
    requires of the predicates PC03 asks this package for.

    It returns ``False`` rather than raising for the same reason the embedding predicate does:
    the CAS runs six checks in a fixed order and maps each failure to its own code, and a
    predicate that raised would take that mapping away from the transaction that owns it.
    """
    repo = repository or CoverageRepository()
    current = repo.current_window(connection, owner_id)
    current_id = None if current is None else current.id
    return current_id == expected_predecessor_id


def plan_next_window(
    connection: Connection,
    *,
    owner_id: str,
    predecessor: CoverageWindow | None,
    snapshot_taken_at: str,
    watermark_port: IngestWatermarkPort | None = None,
) -> WindowPlan:
    """Compute ``[from, to)`` for the period about to be built (§4.3, §4.8).

    The sequence axis decides membership; the timestamp pair is the readable label of that
    decision (§4.3 rule 4). Concretely:

    * ``ingest_sequence_from`` = the predecessor's ``ingest_sequence_to``, or ``0`` for the
      first window (§4.8);
    * ``ingest_sequence_to`` = ``W + 1``, exclusive, where ``W`` is the watermark;
    * ``window_to`` = ``discovered_at`` of the row carrying ``W``, or ``snapshot_taken_at``
      when the span is empty;
    * ``window_from`` = the predecessor's ``window_to``, or (first window) the earliest
      ``discovered_at`` in the store, or ``snapshot_taken_at - 1ms`` on an empty store.

    ``CR-TC-REPORT-02``: §4.3 rule 3 and the CHECK ``window_to > window_from`` can disagree.
    When every item in a non-empty period shares the millisecond that the previous period
    ended on, ``discovered_at(W) == window_from`` and the row would be rejected. The contract
    does not resolve it, so the resolution here is the smallest one that keeps both §4.2
    (contiguity) and the CHECK true: the label is pushed forward by exactly one millisecond.
    Membership is unaffected because membership is decided on the sequence axis.
    """
    port = watermark_port or CommittedRowsWatermark()
    watermark = port.contiguous_watermark(connection, owner_id)

    if predecessor is None:
        sequence = 1
        ingest_from = 0
        earliest = port.earliest_discovered_at(connection, owner_id)
        window_from = earliest if earliest is not None else minus_one_millisecond(snapshot_taken_at)
        predecessor_id: str | None = None
    else:
        sequence = predecessor.sequence + 1
        ingest_from = predecessor.ingest_sequence_to
        window_from = predecessor.window_to
        predecessor_id = predecessor.id

    # ``ingest_sequence_to := W + 1`` (§4.3 rule 2), with one boundary case the rule leaves
    # implicit: ``ingest_sequence`` starts at 1 (``entities.yaml``: ``CHECK >= 1``), so a
    # watermark of 0 means *nothing has ever committed* rather than "sequence 0 is covered".
    # Writing ``W + 1 = 1`` there would claim a span containing a sequence that cannot exist,
    # and the first real item would then land outside its own period.
    ingest_to = ingest_from if watermark == 0 else max(watermark + 1, ingest_from)
    if ingest_to == ingest_from:
        window_to = snapshot_taken_at
    else:
        at_watermark = port.discovered_at_of(connection, owner_id, watermark)
        window_to = at_watermark if at_watermark is not None else snapshot_taken_at

    if parse_timestamp_utc_ms(window_to) <= parse_timestamp_utc_ms(window_from):
        window_to = plus_one_millisecond(window_from)

    return WindowPlan(
        sequence=sequence,
        window_from=window_from,
        window_to=window_to,
        ingest_sequence_from=ingest_from,
        ingest_sequence_to=ingest_to,
        predecessor_window_id=predecessor_id,
        snapshot_taken_at=snapshot_taken_at,
    )


def contiguity_violations(windows: list[CoverageWindow]) -> list[str]:
    """The O-4.1 oracle as a value: an empty list means the chain is intact.

    Both axes are checked, and so is "exactly one bootstrap window". A list of strings rather
    than a boolean because a test that fails should say *which* pair broke, not merely that
    something did.
    """
    problems: list[str] = []
    ordered = sorted(windows, key=lambda w: w.sequence)
    bootstraps = [w for w in ordered if w.predecessor_window_id is None]
    if len(bootstraps) != 1 and ordered:
        problems.append(f"expected exactly one bootstrap window, found {len(bootstraps)}")
    for previous, current in zip(ordered, ordered[1:], strict=False):
        if current.predecessor_window_id != previous.id:
            problems.append(
                f"sequence {current.sequence} chains to {current.predecessor_window_id!r}, "
                f"not to the window at sequence {previous.sequence}"
            )
        if current.window_from != previous.window_to:
            problems.append(
                f"time gap/overlap between sequence {previous.sequence} and "
                f"{current.sequence}: {previous.window_to} != {current.window_from}"
            )
        if current.ingest_sequence_from != previous.ingest_sequence_to:
            problems.append(
                f"sequence-axis gap/overlap between {previous.sequence} and "
                f"{current.sequence}: {previous.ingest_sequence_to} != "
                f"{current.ingest_sequence_from}"
            )
    for window in ordered:
        if parse_timestamp_utc_ms(window.window_to) <= parse_timestamp_utc_ms(window.window_from):
            problems.append(f"sequence {window.sequence} is not half-open: {window}")
    return problems


__all__ = [
    "REPORT_SCHEMA_VERSION",
    "SELECTION_VERSION",
    "CommittedRowsWatermark",
    "CoverageRepository",
    "CoverageWindow",
    "IngestWatermarkPort",
    "ReportError",
    "WindowPlan",
    "canonical_json",
    "content_hash_of",
    "contiguity_violations",
    "coverage_predecessor_matches",
    "minus_one_millisecond",
    "new_ulid",
    "parse_timestamp_utc_ms",
    "plan_next_window",
    "plus_one_millisecond",
    "to_timestamp_utc_ms",
    "utc_now_ms",
]
