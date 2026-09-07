"""The §5 per-run record: shape, validation, ULID, JSONL append, and redaction.

``contracts/ops/collector-probe.md`` §5 fixes the format: one JSONL file, one line per run,
written to a directory on the Owner's personal machine. No database (M0 has none, §1 P6),
nothing sent to the server.

Three rules from §5 are enforced here rather than left to discipline:

* ``unobservable_scope_vi`` must be non-empty. It is the only place in the whole probe that
  records the part of the feed that was **not** observed (AMD-B05), and GO-7 exists because
  a probe that omits it gets read as "we swept everything".
* ``limit_kind`` is NOT NULL exactly when ``stop_reason = limit_reached``, and NULL
  otherwise -- both directions, so a stray ``posts`` on a challenge run is a validation
  error, not a curiosity.
* ``rate_limited_at`` is NOT NULL when ``stop_reason = rate_limited``.

And the redaction rule: post text, cookies, tokens, screenshots carrying session data and
absolute paths containing the user name never reach the file (§5 last paragraph,
SRC-SPEC §11.2). :func:`redact` is applied to every log line and to the free-text fields of
the record before writing.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

#: §5 ``stop_reason`` enum. The first six match ``contracts/state/run.yaml`` §1;
#: ``operator_stop`` is the probe's own value (ST-8) because real operation has no manual
#: stop button for the collector.
STOP_REASONS: tuple[str, ...] = (
    "limit_reached",
    "captcha",
    "session_expired",
    "source_blocked",
    "rate_limited",
    "source_layout_changed",
    "operator_stop",
)

#: §5 ``limit_kind`` enum.
LIMIT_KINDS: tuple[str, ...] = ("posts", "duration")

#: Every §5 field, in the contract's row order. The JSONL writer emits exactly these keys,
#: so a reviewer can diff a record against the contract table line by line.
RECORD_FIELDS: tuple[str, ...] = (
    "probe_run_id",
    "started_at",
    "ended_at",
    "duration_s",
    "search_terms",
    "posts_seen",
    "posts_parsed_ok",
    "posts_new_vs_previous_runs",
    "posts_with_paper_link",
    "posts_image_only",
    "author_threads_opened",
    "challenge_count",
    "session_expired_count",
    "blocked_count",
    "rate_limited_count",
    "rate_limited_at",
    "parser_degraded_count",
    "stop_reason",
    "limit_kind",
    "cursor_invalidated",
    "unobservable_scope_vi",
    "notes_vi",
)

#: Provenance fields the probe adds beyond §5. They are metadata about the tooling, not
#: measurements, and they are listed separately so nobody mistakes them for contract fields.
PROVENANCE_FIELDS: tuple[str, ...] = ("protocol_version", "probe_tool_version", "clock_note_vi")

PROBE_TOOL_VERSION = "0.1.0"

#: §5: the timestamps are the *personal machine's* clock, not the server's (AMD-B08).
CLOCK_NOTE_VI = (
    "Mốc thời gian lấy từ đồng hồ máy cá nhân của Owner (UTC), KHÔNG phải đồng hồ server "
    "(AMD-B08)."
)


class RecordValidationError(ValueError):
    """A record does not satisfy ``collector-probe.md`` §5."""


# --- ULID ---------------------------------------------------------------------------
_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid(*, now_ms: int | None = None, randomness: bytes | None = None) -> str:
    """A 26-character Crockford base32 ULID.

    Written here rather than pulled in as a dependency: the probe runs on the Owner's
    machine from the workspace environment, and adding a package to the lockfile for 20
    lines of encoding would be a toolchain change this card may not make (``SG-STACK``).
    """
    timestamp = now_ms if now_ms is not None else int(time.time() * 1000)
    rand = randomness if randomness is not None else secrets.token_bytes(10)
    if len(rand) != 10:
        raise ValueError("ULID randomness must be exactly 10 bytes")
    value = (timestamp << 80) | int.from_bytes(rand, "big")
    out = []
    for shift in range(125, -1, -5):
        out.append(_CROCKFORD[(value >> shift) & 0x1F])
    return "".join(out)


def format_utc_ms(moment: datetime) -> str:
    """Format an aware datetime as RFC 3339 UTC with milliseconds."""
    aware = moment.astimezone(UTC)
    return aware.strftime("%Y-%m-%dT%H:%M:%S.") + f"{aware.microsecond // 1000:03d}Z"


def utc_now_ms() -> str:
    """RFC 3339 UTC with millisecond precision, as §5 requires."""
    return format_utc_ms(datetime.now(UTC))


TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")
ULID_RE = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")


# --- redaction ----------------------------------------------------------------------
#: Ordered (pattern, replacement) pairs. Applied to every log line and to every free-text
#: field of a record. Redaction here is deliberately blunt: over-redacting a note costs a
#: reviewer nothing, while one leaked ``auth_token`` is a real credential in a file the
#: Owner will send back.
REDACTIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]+"), "Bearer <redacted>"),
    (
        re.compile(r"(?i)\b(auth_token|ct0|guest_id|twid|kdt|_twitter_sess)=[^;\s\"']+"),
        r"\1=<redacted>",
    ),
    (re.compile(r"(?i)\b(set-)?cookie\s*:\s*[^\r\n]+"), "cookie: <redacted>"),
    (
        re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\s*[=:]\s*[^\s,;\"']+"),
        r"\1=<redacted>",
    ),
    (re.compile(r"/home/[^/\s\"']+"), "<HOME>"),
    (re.compile(r"/Users/[^/\s\"']+"), "<HOME>"),
    (re.compile(r"(?i)[A-Z]:\\\\Users\\\\[^\\\\\s\"']+"), "<HOME>"),
    # Account identity: §5 forbids "danh tính tài khoản" in the file. A handle is the
    # identity, so it never survives -- not the Owner's, not an observed author's.
    (re.compile(r"(?<![\w/])@[A-Za-z0-9_]{1,15}\b"), "@<handle>"),
)


def redact(text: str) -> str:
    """Remove credentials, cookies, home paths and account handles from free text."""
    out = text
    for pattern, replacement in REDACTIONS:
        out = pattern.sub(replacement, out)
    return out


# --- the record ---------------------------------------------------------------------
@dataclass
class ProbeRunRecord:
    """One line of the §5 JSONL. Every field of the contract table, none invented."""

    probe_run_id: str
    started_at: str
    ended_at: str
    duration_s: int
    search_terms: list[str]
    posts_seen: int
    posts_parsed_ok: int
    posts_new_vs_previous_runs: int
    posts_with_paper_link: int
    posts_image_only: int
    author_threads_opened: int
    challenge_count: int
    session_expired_count: int
    blocked_count: int
    rate_limited_count: int
    rate_limited_at: str | None
    parser_degraded_count: int
    stop_reason: str
    limit_kind: str | None
    cursor_invalidated: bool
    unobservable_scope_vi: str
    notes_vi: str = ""
    protocol_version: str = ""
    probe_tool_version: str = PROBE_TOOL_VERSION
    clock_note_vi: str = CLOCK_NOTE_VI

    def to_json_dict(self) -> dict[str, Any]:
        """Contract fields in contract order, then provenance. Free text redacted."""
        raw = asdict(self)
        out: dict[str, Any] = {}
        for key in RECORD_FIELDS:
            value = raw[key]
            out[key] = redact(value) if isinstance(value, str) and value else value
        for key in PROVENANCE_FIELDS:
            out[key] = raw[key]
        return out


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RecordValidationError(message)


def validate_record(data: dict[str, Any]) -> None:
    """Validate a record mapping against §5. Raises :class:`RecordValidationError`."""
    missing = [f for f in RECORD_FIELDS if f not in data]
    _require(not missing, f"Thiếu trường §5 bắt buộc: {missing}")

    _require(
        isinstance(data["probe_run_id"], str) and bool(ULID_RE.match(data["probe_run_id"])),
        "probe_run_id phải là ULID 26 ký tự Crockford base32.",
    )
    for key in ("started_at", "ended_at"):
        _require(
            isinstance(data[key], str) and bool(TIMESTAMP_RE.match(data[key])),
            f"{key} phải là UTC RFC 3339 với mili giây, ví dụ 2026-09-08T08:00:00.000Z.",
        )
    _require(data["started_at"] <= data["ended_at"], "started_at phải <= ended_at.")

    for key in (
        "duration_s",
        "posts_seen",
        "posts_parsed_ok",
        "posts_new_vs_previous_runs",
        "posts_with_paper_link",
        "posts_image_only",
        "author_threads_opened",
        "challenge_count",
        "session_expired_count",
        "blocked_count",
        "rate_limited_count",
        "parser_degraded_count",
    ):
        value = data[key]
        _require(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0,
            f"{key} phải là số nguyên >= 0; nhận {value!r}.",
        )

    _require(
        isinstance(data["search_terms"], list)
        and bool(data["search_terms"])
        and all(isinstance(t, str) and t.strip() for t in data["search_terms"]),
        "search_terms phải là mảng chuỗi không rỗng (§5: từ khóa đã dùng).",
    )
    _require(
        data["posts_parsed_ok"] <= data["posts_seen"],
        "posts_parsed_ok không thể lớn hơn posts_seen.",
    )
    _require(
        data["posts_new_vs_previous_runs"] <= data["posts_seen"],
        "posts_new_vs_previous_runs không thể lớn hơn posts_seen.",
    )

    _require(
        data["stop_reason"] in STOP_REASONS,
        f"stop_reason phải thuộc {list(STOP_REASONS)}; nhận {data['stop_reason']!r}.",
    )

    limit_kind = data["limit_kind"]
    if data["stop_reason"] == "limit_reached":
        _require(
            limit_kind in LIMIT_KINDS,
            "limit_kind BẮT BUỘC NOT NULL và thuộc "
            f"{list(LIMIT_KINDS)} khi stop_reason = limit_reached (§5, REQ-A7).",
        )
    else:
        _require(
            limit_kind is None,
            "limit_kind phải NULL khi stop_reason khác limit_reached; "
            f"nhận {limit_kind!r} cùng stop_reason={data['stop_reason']!r}.",
        )

    rate_limited_at = data["rate_limited_at"]
    if data["stop_reason"] == "rate_limited":
        _require(
            isinstance(rate_limited_at, str) and bool(TIMESTAMP_RE.match(rate_limited_at)),
            "rate_limited_at BẮT BUỘC NOT NULL (UTC RFC 3339 ms) khi "
            "stop_reason = rate_limited (§5 ST-4).",
        )
    else:
        _require(
            rate_limited_at is None or bool(TIMESTAMP_RE.match(str(rate_limited_at))),
            "rate_limited_at phải là NULL hoặc UTC RFC 3339 ms.",
        )
    if rate_limited_at is not None:
        _require(
            data["rate_limited_count"] >= 1,
            "rate_limited_at có giá trị thì rate_limited_count phải >= 1.",
        )

    _require(
        isinstance(data["cursor_invalidated"], bool),
        "cursor_invalidated phải là boolean (B05).",
    )
    _require(
        isinstance(data["unobservable_scope_vi"], str)
        and bool(data["unobservable_scope_vi"].strip()),
        "unobservable_scope_vi BẮT BUỘC KHÔNG RỖNG (§5, AMD-B05, GO-7): phải mô tả phần "
        "feed KHÔNG quan sát được. Một probe không ghi phần mình không thấy sẽ bị đọc "
        "thành 'đã quét đủ'.",
    )
    _require(isinstance(data.get("notes_vi", ""), str), "notes_vi phải là chuỗi.")

    blob = json.dumps(data, ensure_ascii=False)
    _require(
        blob == redact(blob),
        "Bản ghi còn chứa chuỗi nhạy cảm (cookie/token/@handle/đường dẫn home) sau khi "
        "so với bộ luật che ở record.REDACTIONS (§5, SRC-SPEC §11.2).",
    )


# --- JSONL I/O ----------------------------------------------------------------------
def append_record(jsonl_path: str | Path, record: ProbeRunRecord) -> dict[str, Any]:
    """Validate then append one record as one JSONL line. Returns what was written.

    ``fsync`` after each line: a probe run is expensive and unrepeatable (each one spends
    Owner budget against a real X account), so a record must survive the crash of the very
    next step.
    """
    payload = record.to_json_dict()
    validate_record(payload)
    path = Path(jsonl_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(payload, ensure_ascii=False, sort_keys=False)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    return payload


def read_records(jsonl_path: str | Path, *, validate: bool = True) -> list[dict[str, Any]]:
    """Read every record from a JSONL file, skipping blank lines.

    ``validate=True`` (the default) refuses to hand a malformed record to the go/no-go
    computation: §7 is applied over records, and a record that does not satisfy §5 is not
    a measurement.
    """
    path = Path(jsonl_path)
    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file JSONL: {path}")
    records: list[dict[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RecordValidationError(f"{path}:{lineno} không phải JSON hợp lệ: {exc}") from exc
        if not isinstance(data, dict):
            raise RecordValidationError(f"{path}:{lineno} không phải một object JSON.")
        if validate:
            try:
                validate_record(data)
            except RecordValidationError as exc:
                raise RecordValidationError(f"{path}:{lineno} — {exc}") from exc
        records.append(data)
    return records


@dataclass
class RunCounters:
    """Mutable tally a run builds up, converted into a record at the end."""

    posts_seen: int = 0
    posts_parsed_ok: int = 0
    posts_new_vs_previous_runs: int = 0
    posts_with_paper_link: int = 0
    posts_image_only: int = 0
    author_threads_opened: int = 0
    challenge_count: int = 0
    session_expired_count: int = 0
    blocked_count: int = 0
    rate_limited_count: int = 0
    rate_limited_at: str | None = None
    parser_degraded_count: int = 0
    cursor_invalidated: bool = False
    terms_completed: list[str] = field(default_factory=list)

    def bump(self, counter_field: str | None, *, at: str | None = None) -> None:
        """Increment the §4 counter a detection names; record the first rate-limit stamp."""
        if counter_field is None:
            return
        setattr(self, counter_field, getattr(self, counter_field) + 1)
        if counter_field == "rate_limited_count" and self.rate_limited_at is None:
            self.rate_limited_at = at or utc_now_ms()


def hash_post_id(x_post_id: str) -> str:
    """Ledger key for ``posts_new_vs_previous_runs``.

    §5 needs the count of post ids not seen in earlier runs, which needs a cross-run
    memory. Storing raw ids would put source identifiers in the evidence directory for no
    measurement benefit, so the ledger keeps ``sha256`` digests: enough to answer "seen
    before?", useless for reconstructing who posted what.
    """
    import hashlib

    return hashlib.sha256(x_post_id.encode("utf-8")).hexdigest()


def load_seen_ledger(path: str | Path) -> set[str]:
    ledger = Path(path)
    if not ledger.is_file():
        return set()
    lines = ledger.read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip()}


def append_seen_ledger(path: str | Path, digests: set[str]) -> None:
    if not digests:
        return
    ledger = Path(path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as handle:
        for digest in sorted(digests):
            handle.write(digest + "\n")
        handle.flush()
        os.fsync(handle.fileno())
