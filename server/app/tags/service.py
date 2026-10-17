"""``MOD-tag-service`` — the subscription layer: tags, aliases, exclusions, config versions.

Card: ``agent-tasks/TC-tag-service.md`` (``OD-20261017-12`` item 6). Eight operations of
``contracts/ports.yaml``: six over HTTP for ``MOD-web-ui`` (``router.py``) and two internal ones
for ``MOD-report-service`` — ``tag.get_active_config_version`` and ``tag.freeze_config_version``
— which the composition root adapts onto ``server.app.report.builder.TagConfigVersionPort``.
``tag.rescan_corpus`` already lives in :mod:`server.app.tags.rescan`; this module does not
duplicate it.

The config version is written by the mutation, not by the read
---------------------------------------------------------------
``ports.yaml`` gives ``tag.create`` / ``tag.update`` / ``tag.delete`` the effect "tạo
``tag_config_version`` mới" and returns it, and reporting fixtures ``a`` and ``c`` count one new
version per mutation. So every mutation materialises the version of the tag set it leaves
behind, in the same transaction as the rows it changes. ``ux_tag_config_version_owner_hash``
makes that idempotent on *content*: a mutation that leaves the set as it was reuses the stored
row rather than minting a new sequence. The *active* version is therefore "the row whose
``content_hash`` equals the hash of the live set" — computed, never a pointer that could drift.

Two contract statements disagree with that reading and the card records both rather than
picking silently: ``ENT-tag-config-version.created_at`` says the snapshot moment is the publish
moment (``PROVISIONAL``), and ``ui/sc51-first-time-setup.json`` expects three creates to leave
**one** version (``CR-TC-TAG-01``).

What crosses a module edge, and how
-----------------------------------
* ``embedding.generate_vectors`` / ``embedding.get_active_generation`` — the module's only two
  outbound operations (``modules.yaml``). Called through :class:`EmbeddingPort`.
* The backfill activation of ``tag.create`` (D28) writes ``backfill_ledger``, which belongs to
  ``MOD-report-service``, and there is no tag → report edge. The activation is injected as
  :class:`ActivationPort` by the composition root and runs **on this module's connection**, so
  the tag row and its ledger row commit together. Nothing here imports ``server.app.report``
  (``ENF-import-rule``); the missing edge is ``CR-TC-TAG-02``.
* ``TAG_VERSION_STALE`` must reach the report publisher as a ``ReportError``; this module raises
  its own :class:`TagError` and the adapter in ``server/app/wiring.py`` translates.

Vectors are written before the rows
-----------------------------------
``generate_vectors`` opens its own transaction, and SQLite has one writer, so it cannot run
inside the tag transaction. It runs first, on pre-allocated subject ids: a refusal there leaves
nothing behind, which is what ``tag.create``'s ``EMBEDDING_GENERATION_MISMATCH`` /
``STORAGE_WRITE_FAILED`` promise. When no generation is active, or no local model is configured,
the mutation still succeeds and says ``vectors.state = "pending"`` — a report build then refuses
with ``EMBEDDING_GENERATION_MISMATCH`` (``selection.md`` §5.3), which is the honest outcome, and
nothing falls back (``CR-TC-TAG-05``).
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine, text

from server.app.embedding.generation import (
    EmbeddingError,
    GenerationFingerprint,
    LocalEncoder,
    Normalization,
    SubjectType,
    Vector,
    cosine,
    round_half_up,
)
from server.app.embedding.service import VectorRequest

OWNER_MODULE: Final[str] = "MOD-tag-service"

_CROCKFORD32: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: ``ENT-tag.text`` / ``ENT-tag-alias.text`` / ``ENT-tag-exclusion.text``: 1..200 after trim.
TEXT_MAX: Final[int] = 200

#: ``selection.md`` §4.2 — the default when neither the tag nor ``settings`` names one. The same
#: value ``SelectionSettings.default_similarity_threshold`` carries on the report side.
SETTING_DEFAULT_THRESHOLD: Final[str] = "reporting.default_similarity_threshold"
DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.8000

#: ``contracts/ui/screens.yaml`` ``SCR-topics`` empty state. Never "Không có nghiên cứu mới".
EMPTY_TAGS_MESSAGE_VI: Final[str] = "Chưa có tag nào, báo cáo sẽ trống"

STATE_ACTIVE: Final[str] = "active"
STATE_REMOVED: Final[str] = "removed"


def new_ulid() -> str:
    """A ULID. Local for the same reason as :func:`server.app.tags.rescan.new_ulid`."""
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD32[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def _format(moment: datetime) -> str:
    """RFC 3339 UTC with exactly three fractional digits (``time-and-tags.md`` §1.1)."""
    utc = moment.astimezone(UTC)
    return utc.strftime("%Y-%m-%dT%H:%M:%S.") + f"{utc.microsecond // 1000:03d}Z"


def normalize_tag_text(value: str) -> str:
    """``time-and-tags.md`` §6.2: NFC → trim → casefold → collapse whitespace.

    Re-implemented, not imported from ``server.app.report.backfill``: no tag → report edge.
    ``tests/integration/test_tag_service.py`` asserts the two agree on the fixture texts.
    """
    return " ".join(unicodedata.normalize("NFC", value).strip().casefold().split())


def canonical_json(value: Any) -> str:
    """The RFC 8785 subset every package here uses (see ``report/coverage.py``)."""
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def content_hash_of(payload: Mapping[str, Any]) -> str:
    """``ENT-tag-config-version.content_hash`` = ``"sha256:" + sha256(JCS(payload))``."""
    return "sha256:" + hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def payload_hash(value: Any) -> str:
    """The ``payload_hash_*`` of ``IDEMPOTENCY_CONFLICT``: bare hex of the canonical body."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------------------

_HTTP_STATUS: Final[dict[ErrorCode, int]] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: 409,
    ErrorCode.TAG_VERSION_STALE: 409,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}

#: ``details_safe_keys`` of ``contracts/errors.yaml`` for the codes this module emits. Enforced
#: at construction, as in ``server/app/saved/service.py``: an unknown key is refused before it
#: can be serialised even once.
DETAILS_SAFE_KEYS: Final[dict[ErrorCode, frozenset[str]]] = {
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
    ErrorCode.CSRF_REJECTED: frozenset({"operation_id"}),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"caller_module", "callee_module", "forbidden_edge_ref"}),
    ErrorCode.NOT_FOUND: frozenset({"operation_id", "resource_kind"}),
    ErrorCode.IDEMPOTENCY_CONFLICT: frozenset(
        {"idempotency_key", "payload_hash_seen", "payload_hash_stored"}
    ),
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: frozenset(
        {"expected_generation_id", "seen_generation_id", "dimension_expected", "dimension_seen"}
    ),
    ErrorCode.TAG_VERSION_STALE: frozenset(
        {
            "report_build_id",
            "expected_tag_config_version_id",
            "current_tag_config_version_id",
            "rebuild_attempt",
        }
    ),
    ErrorCode.RATE_LIMITED: frozenset(),
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
    ErrorCode.INTERNAL: frozenset({"correlation_id", "operation_id"}),
}

_MESSAGE_SAFE: Final[dict[ErrorCode, str]] = {
    ErrorCode.VALIDATION_ERROR: "Yêu cầu không hợp lệ.",
    ErrorCode.UNAUTHORIZED: "Bạn cần đăng nhập để thực hiện thao tác này.",
    ErrorCode.CSRF_REJECTED: "Yêu cầu thiếu hoặc sai CSRF token.",
    ErrorCode.FORBIDDEN_EDGE: "Lời gọi này không nằm trong các kết nối được phép.",
    ErrorCode.NOT_FOUND: "Không tìm thấy tag được yêu cầu.",
    ErrorCode.IDEMPOTENCY_CONFLICT: "Khóa chống trùng đã được dùng cho một nội dung khác.",
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: (
        "Bộ vector của tag không khớp thế hệ embedding đang dùng; chưa có gì được lưu."
    ),
    ErrorCode.TAG_VERSION_STALE: "Bộ tag đã đổi kể từ lúc dựng báo cáo.",
    ErrorCode.STORAGE_WRITE_FAILED: "Hệ thống đang không ghi được dữ liệu. Chưa có gì được lưu.",
    ErrorCode.INTERNAL: "Có lỗi không mong đợi.",
}


class TagError(Exception):
    """A refusal carrying one registered error code and the contract's envelope."""

    def __init__(
        self,
        code: ErrorCode,
        *,
        message_safe: str | None = None,
        details_safe: Mapping[str, Any] | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        details = dict(details_safe or {})
        unknown = set(details) - DETAILS_SAFE_KEYS.get(code, frozenset())
        if unknown:
            raise ValueError(f"details_safe keys not registered for {code.value}: {unknown}")
        self.code = code
        self.message_safe = message_safe or _MESSAGE_SAFE.get(
            code, _MESSAGE_SAFE[ErrorCode.INTERNAL]
        )
        self.details_safe = details
        self.retry_after_ms = retry_after_ms
        super().__init__(f"{code.value}: {self.message_safe}")

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
            "retry_after_ms": self.retry_after_ms,
        }


def _invalid(operation: OperationId, field_path: str, kind: str, **limits: Any) -> TagError:
    return TagError(
        ErrorCode.VALIDATION_ERROR,
        details_safe={
            "operation_id": operation.value,
            "field_path": field_path,
            "violation_kind": kind,
            **limits,
        },
    )


def _not_found(operation: OperationId, resource_kind: str = "tag") -> TagError:
    return TagError(
        ErrorCode.NOT_FOUND,
        details_safe={"operation_id": operation.value, "resource_kind": resource_kind},
    )


# --------------------------------------------------------------------------------------
# Ports
# --------------------------------------------------------------------------------------


class StorageGuardPort(Protocol):
    """The write gate from ``TC-storage-write-blocked-readiness``."""

    def assert_writable(self, operation_id: OperationId) -> None: ...


class EmbeddingPort(Protocol):
    """The two ``MOD-embedding-service`` operations this module may call (``modules.yaml``)."""

    def get_active_generation(self, owner_id: str, *, caller_module: str) -> dict[str, Any]: ...

    def generate_vectors(
        self,
        owner_id: str,
        *,
        caller_module: str,
        generation_id: str,
        requests: Sequence[VectorRequest],
    ) -> Sequence[Any]: ...


class ActivationPort(Protocol):
    """The D28 backfill activation of ``tag.create``, written on the caller's connection.

    The composition root binds it to ``server.app.report.backfill.open_activation`` with N read
    from ``settings`` (``time-and-tags.md`` §6.1). Returns the ledger row as a mapping.
    """

    def open_activation(
        self, connection: Connection, *, owner_id: str, tag_id: str, tag_text: str
    ) -> Mapping[str, Any]: ...

    def preflight(self, connection: Connection, *, owner_id: str) -> None:
        """Refuse now if the activation would refuse later (e.g. N not configured).

        Called before any vector is generated: a refusal after ``generate_vectors`` committed
        would leave vectors for a tag that never existed, and ``built_vector_count`` is what a
        generation's activation guard counts.
        """
        ...


@dataclass(frozen=True, slots=True)
class TagConfigVersionRecord:
    """One ``tag_config_version`` row, as this module hands it out."""

    id: str
    sequence: int
    content_hash: str
    payload: Mapping[str, Any]
    created_at: str

    def summary(self) -> dict[str, Any]:
        return {
            "tag_config_version_id": self.id,
            "sequence": self.sequence,
            "content_hash": self.content_hash,
            "created_at": self.created_at,
        }


@dataclass
class TagContext:
    """Everything the tag operations need, injected rather than imported."""

    engine: Engine
    owner_id: str
    storage_guard: StorageGuardPort | None = None
    #: ``None`` ⇒ no local embedding model configured; mutations answer ``vectors: pending``.
    embedding: EmbeddingPort | None = None
    #: The same local model, for the *draft-text* half of ``tag.preview_matches`` — a temporary
    #: vector that is never written (``ports.yaml``). ``None`` ⇒ draft preview refuses.
    encoder: LocalEncoder | None = None
    activation: ActivationPort | None = None
    clock: Callable[[], datetime] | None = None
    id_factory: Callable[[], str] | None = None
    #: Process-local ``(operation, Idempotency-Key)`` → ``(payload hash, response)``
    #: (``CR-TC-TAG-03``; the same disposition as ``CR-TC-BACKFILL-04``).
    receipts: dict[tuple[str, str], tuple[str, dict[str, Any]]] = field(default_factory=dict)
    #: Process-local ``report_build_id`` → frozen version id (``CR-TC-TAG-04``).
    frozen: dict[str, str] = field(default_factory=dict)

    def now(self) -> str:
        return _format(datetime.now(UTC) if self.clock is None else self.clock())

    def new_id(self) -> str:
        return new_ulid() if self.id_factory is None else self.id_factory()


def _assert_writable(ctx: TagContext, operation: OperationId) -> None:
    """``guard.assert_writable`` before anything is written; the guard's envelope is carried."""
    if ctx.storage_guard is None:
        return
    try:
        ctx.storage_guard.assert_writable(operation)
    except Exception as refused:  # StorageRefused; typed loosely, as in saved/service.py
        envelope = getattr(refused, "envelope", None)
        if not isinstance(envelope, dict):
            raise
        raise TagError(
            ErrorCode(envelope["code"]),
            message_safe=envelope.get("message_safe"),
            details_safe=envelope.get("details_safe") or {},
            retry_after_ms=envelope.get("retry_after_ms"),
        ) from refused


# --------------------------------------------------------------------------------------
# Input validation
# --------------------------------------------------------------------------------------


def _clean_text(value: Any, operation: OperationId, field_path: str) -> str:
    if not isinstance(value, str):
        raise _invalid(operation, field_path, "type_invalid")
    cleaned = unicodedata.normalize("NFC", value).strip()
    if not cleaned:
        raise _invalid(operation, field_path, "required_missing")
    if len(cleaned) > TEXT_MAX:
        raise _invalid(
            operation, field_path, "too_long", limit_name="max_length", limit_value=TEXT_MAX
        )
    return cleaned


def _clean_texts(value: Any, operation: OperationId, field_path: str) -> list[str]:
    """A list of alias or exclusion texts, de-duplicated on the normalized form, order kept."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise _invalid(operation, field_path, "type_invalid")
    seen: set[str] = set()
    out: list[str] = []
    for index, item in enumerate(value):
        cleaned = _clean_text(item, operation, f"{field_path}[{index}]")
        key = normalize_tag_text(cleaned)
        if key not in seen:
            seen.add(key)
            out.append(cleaned)
    return out


def _clean_threshold(value: Any, operation: OperationId) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise _invalid(operation, "similarity_threshold", "type_invalid")
    if not 0 <= float(value) <= 1:
        raise _invalid(
            operation, "similarity_threshold", "out_of_range", limit_name="0..1", limit_value=1
        )
    return round_half_up(float(value))


def _reject_unknown(body: Mapping[str, Any], allowed: set[str], operation: OperationId) -> None:
    for key in body:
        if key not in allowed:
            raise _invalid(operation, key, "unknown_field")


# --------------------------------------------------------------------------------------
# Reads
# --------------------------------------------------------------------------------------


def _active_tags(connection: Connection, owner_id: str) -> list[dict[str, Any]]:
    rows = connection.execute(
        text(
            'SELECT id, "text", similarity_threshold, created_at, updated_at FROM tag '
            "WHERE owner_id = :o AND state = 'active' ORDER BY id"
        ),
        {"o": owner_id},
    ).mappings()
    return [dict(row) for row in rows]


def _active_children(connection: Connection, table: str, owner_id: str) -> list[dict[str, Any]]:
    """Active aliases or exclusions whose tag (if any) is itself active."""
    rows = connection.execute(
        text(
            f'SELECT c.id, c.tag_id, c."text" FROM {table} c '
            "LEFT JOIN tag t ON t.id = c.tag_id "
            "WHERE c.owner_id = :o AND c.state = 'active' "
            "AND (c.tag_id IS NULL OR t.state = 'active') ORDER BY c.id"
        ),
        {"o": owner_id},
    ).mappings()
    return [dict(row) for row in rows]


def live_payload(connection: Connection, owner_id: str) -> dict[str, Any]:
    """The payload shape ``server.app.report.builder.TagSet.from_payload`` parses.

    Active rows only, ordered by id, ``state`` omitted — a config version is a snapshot of what
    is active, so there is nothing to filter on afterwards.
    """
    return {
        "tags": [
            {
                "id": row["id"],
                "text": row["text"],
                "similarity_threshold": row["similarity_threshold"],
            }
            for row in _active_tags(connection, owner_id)
        ],
        "tag_aliases": [
            {"id": row["id"], "tag_id": row["tag_id"], "text": row["text"]}
            for row in _active_children(connection, "tag_alias", owner_id)
        ],
        "tag_exclusions": [
            {"id": row["id"], "tag_id": row["tag_id"], "text": row["text"]}
            for row in _active_children(connection, "tag_exclusion", owner_id)
        ],
    }


def _version_row(row: Any) -> TagConfigVersionRecord:
    return TagConfigVersionRecord(
        id=str(row["id"]),
        sequence=int(row["sequence"]),
        content_hash=str(row["content_hash"]),
        payload=json.loads(str(row["payload"])),
        created_at=str(row["created_at"]),
    )


_VERSION_COLUMNS = "id, sequence, payload, content_hash, created_at"


def _version_by_hash(
    connection: Connection, owner_id: str, digest: str
) -> TagConfigVersionRecord | None:
    row = (
        connection.execute(
            text(
                f"SELECT {_VERSION_COLUMNS} FROM tag_config_version "
                "WHERE owner_id = :o AND content_hash = :h"
            ),
            {"o": owner_id, "h": digest},
        )
        .mappings()
        .first()
    )
    return None if row is None else _version_row(row)


def _materialize_version(ctx: TagContext, connection: Connection) -> TagConfigVersionRecord:
    """The version of the live set: the stored row with that content, or a new sequence."""
    payload = live_payload(connection, ctx.owner_id)
    digest = content_hash_of(payload)
    existing = _version_by_hash(connection, ctx.owner_id, digest)
    if existing is not None:
        return existing
    sequence = int(
        connection.execute(
            text(
                "SELECT COALESCE(MAX(sequence), 0) + 1 FROM tag_config_version WHERE owner_id = :o"
            ),
            {"o": ctx.owner_id},
        ).scalar_one()
    )
    record = TagConfigVersionRecord(
        id=ctx.new_id(),
        sequence=sequence,
        content_hash=digest,
        payload=payload,
        created_at=ctx.now(),
    )
    connection.execute(
        text(
            "INSERT INTO tag_config_version (id, owner_id, sequence, payload, content_hash, "
            "created_at) VALUES (:id, :o, :seq, :payload, :hash, :at)"
        ),
        {
            "id": record.id,
            "o": ctx.owner_id,
            "seq": record.sequence,
            "payload": canonical_json(payload),
            "hash": record.content_hash,
            "at": record.created_at,
        },
    )
    return record


def get_active_config_version(ctx: TagContext) -> TagConfigVersionRecord:
    """``tag.get_active_config_version`` — internal, read-only, ``NOT_FOUND`` when none exists.

    "Active" is computed: the stored version whose content equals the live set. Absent only
    before the first tag mutation, which is the one case the contract's ``NOT_FOUND`` names.
    """
    with ctx.engine.connect() as connection:
        digest = content_hash_of(live_payload(connection, ctx.owner_id))
        record = _version_by_hash(connection, ctx.owner_id, digest)
    if record is None:
        raise _not_found(OperationId.TAG_GET_ACTIVE_CONFIG_VERSION, "tag_config_version")
    return record


def config_version(ctx: TagContext, *, tag_config_version_id: str) -> TagConfigVersionRecord:
    """The immutable snapshot a published report points at (``GET /v1/reports/{id}``)."""
    with ctx.engine.connect() as connection:
        row = (
            connection.execute(
                text(
                    f"SELECT {_VERSION_COLUMNS} FROM tag_config_version "
                    "WHERE owner_id = :o AND id = :id"
                ),
                {"o": ctx.owner_id, "id": tag_config_version_id},
            )
            .mappings()
            .first()
        )
    if row is None:
        raise _not_found(OperationId.TAG_GET_ACTIVE_CONFIG_VERSION, "tag_config_version")
    return _version_row(row)


def freeze_config_version(
    ctx: TagContext, *, report_build_id: str, expected_tag_config_version_id: str
) -> TagConfigVersionRecord:
    """``tag.freeze_config_version`` — §3.3 steps 2-4 of ``time-and-tags.md``.

    The version a build read must still be the live one; otherwise ``TAG_VERSION_STALE`` and
    the publisher aborts. A repeat within one build returns the version it froze the first time
    (``ports.yaml`` idempotency on ``report_build_id``), even if tags moved since — the publish
    that froze it already holds it. The registry is process-local (``CR-TC-TAG-04``): no column
    stores ``report_build_id``, and the ``report`` row that does belongs to the report service.

    ``rebuild_attempt`` is ``None``: the attempt count is the publisher's, not this module's.
    """
    previous = ctx.frozen.get(report_build_id)
    if previous is not None:
        return config_version(ctx, tag_config_version_id=previous)
    try:
        current = get_active_config_version(ctx)
    except TagError:
        current = None
    if current is None or current.id != expected_tag_config_version_id:
        raise TagError(
            ErrorCode.TAG_VERSION_STALE,
            details_safe={
                "report_build_id": report_build_id,
                "expected_tag_config_version_id": expected_tag_config_version_id,
                "current_tag_config_version_id": None if current is None else current.id,
                "rebuild_attempt": None,
            },
        )
    ctx.frozen[report_build_id] = current.id
    return current


def _tag_view(connection: Connection, owner_id: str, tag_id: str) -> dict[str, Any]:
    tag = (
        connection.execute(
            text(
                'SELECT id, "text", similarity_threshold, state, created_at, updated_at, '
                "removed_at FROM tag WHERE owner_id = :o AND id = :id"
            ),
            {"o": owner_id, "id": tag_id},
        )
        .mappings()
        .first()
    )
    assert tag is not None  # noqa: S101 - callers resolved the id in this transaction
    aliases = connection.execute(
        text(
            'SELECT id, "text" FROM tag_alias WHERE owner_id = :o AND tag_id = :t '
            "AND state = 'active' ORDER BY id"
        ),
        {"o": owner_id, "t": tag_id},
    ).mappings()
    exclusions = connection.execute(
        text(
            'SELECT id, "text" FROM tag_exclusion WHERE owner_id = :o AND tag_id = :t '
            "AND state = 'active' ORDER BY id"
        ),
        {"o": owner_id, "t": tag_id},
    ).mappings()
    return {
        "tag_id": tag["id"],
        "text": tag["text"],
        "similarity_threshold": tag["similarity_threshold"],
        "state": tag["state"],
        "created_at": tag["created_at"],
        "updated_at": tag["updated_at"],
        "removed_at": tag["removed_at"],
        "aliases": [{"alias_id": row["id"], "text": row["text"]} for row in aliases],
        "exclusions": [{"exclusion_id": row["id"], "text": row["text"]} for row in exclusions],
    }


def list_tags(ctx: TagContext) -> dict[str, Any]:
    """``tag.list`` — active tags with their aliases and exclusions, global exclusions, and the
    active config version (``null`` before the first mutation)."""
    with ctx.engine.connect() as connection:
        tags = [
            _tag_view(connection, ctx.owner_id, row["id"])
            for row in _active_tags(connection, ctx.owner_id)
        ]
        globals_ = connection.execute(
            text(
                'SELECT id, "text" FROM tag_exclusion WHERE owner_id = :o AND tag_id IS NULL '
                "AND state = 'active' ORDER BY id"
            ),
            {"o": ctx.owner_id},
        ).mappings()
        global_exclusions = [{"exclusion_id": row["id"], "text": row["text"]} for row in globals_]
        digest = content_hash_of(live_payload(connection, ctx.owner_id))
        version = _version_by_hash(connection, ctx.owner_id, digest)
    return {
        "tags": tags,
        "global_exclusions": global_exclusions,
        "tag_config_version": None if version is None else version.summary(),
        "empty_state_vi": EMPTY_TAGS_MESSAGE_VI if not tags else None,
    }


# --------------------------------------------------------------------------------------
# Idempotency (process-local, CR-TC-TAG-03)
# --------------------------------------------------------------------------------------


def _replay(
    ctx: TagContext, operation: OperationId, key: str, body: Mapping[str, Any]
) -> dict[str, Any] | None:
    stored = ctx.receipts.get((operation.value, key))
    if stored is None:
        return None
    seen = payload_hash(body)
    if stored[0] != seen:
        raise TagError(
            ErrorCode.IDEMPOTENCY_CONFLICT,
            details_safe={
                "idempotency_key": key,
                "payload_hash_seen": seen,
                "payload_hash_stored": stored[0],
            },
        )
    return stored[1]


def _remember(
    ctx: TagContext,
    operation: OperationId,
    key: str,
    body: Mapping[str, Any],
    response: dict[str, Any],
) -> dict[str, Any]:
    ctx.receipts[(operation.value, key)] = (payload_hash(body), response)
    return response


# --------------------------------------------------------------------------------------
# Vectors
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Subject:
    subject_type: SubjectType
    subject_id: str
    text: str


def _active_generation(ctx: TagContext) -> dict[str, Any] | None:
    if ctx.embedding is None:
        return None
    try:
        return ctx.embedding.get_active_generation(ctx.owner_id, caller_module=OWNER_MODULE)
    except EmbeddingError as error:
        if error.code is ErrorCode.NOT_FOUND:
            return None
        raise


def _generation_id(generation: Mapping[str, Any]) -> str:
    """``embedding.get_active_generation`` answers ``generation_id`` (``EmbeddingRepository``)."""
    return str(generation["generation_id"])


def _embed(ctx: TagContext, subjects: Sequence[_Subject]) -> dict[str, Any]:
    """Vectors for new subjects in the active generation, before any row is written.

    ``pending`` is a statement, not a fallback: the rows are stored, the report builder will
    refuse until vectors exist (``selection.md`` §5.3), and nothing pretends otherwise.
    """
    if ctx.embedding is None:
        return {"state": "pending", "reason": "no_local_embedding_model"}
    generation = _active_generation(ctx)
    if generation is None:
        return {"state": "pending", "reason": "no_active_embedding_generation"}
    generation_id = _generation_id(generation)
    if subjects:
        try:
            ctx.embedding.generate_vectors(
                ctx.owner_id,
                caller_module=OWNER_MODULE,
                generation_id=generation_id,
                requests=[
                    VectorRequest(
                        subject_type=item.subject_type,
                        subject_id=item.subject_id,
                        text=item.text,
                    )
                    for item in subjects
                ],
            )
        except EmbeddingError as error:
            if error.code in (
                ErrorCode.EMBEDDING_GENERATION_MISMATCH,
                ErrorCode.STORAGE_WRITE_FAILED,
            ):
                raise TagError(error.code, details_safe=error.details_safe) from error
            raise
    return {"state": "generated", "embedding_generation_id": generation_id}


def active_subjects(ctx: TagContext) -> list[_Subject]:
    """Every subject a report selection needs a vector for: active tags, aliases, exclusions."""
    with ctx.engine.connect() as connection:
        payload = live_payload(connection, ctx.owner_id)
    return (
        [_Subject(SubjectType.TAG, str(t["id"]), str(t["text"])) for t in payload["tags"]]
        + [_Subject(_ALIAS_TYPE, str(a["id"]), str(a["text"])) for a in payload["tag_aliases"]]
        + [
            _Subject(_EXCLUSION_TYPE, str(e["id"]), str(e["text"]))
            for e in payload["tag_exclusions"]
        ]
    )


def embed_into_generation(ctx: TagContext, *, generation_id: str) -> int:
    """``embedding.generate_vectors`` for every active subject, into a *named* generation.

    Fixture ``reporting/n`` event 3: during a rebuild, ``MOD-tag-service`` writes the new
    generation's vectors for tags, aliases and exclusions. The generation is an argument —
    typically one still ``building`` — never "whichever is active". Idempotent: a subject
    that already has a vector in that generation is returned unchanged by the embedding
    service. Returns the number of subjects sent.
    """
    if ctx.embedding is None:
        raise TagError(
            ErrorCode.EMBEDDING_GENERATION_MISMATCH,
            message_safe="Chưa cấu hình model embedding cục bộ.",
            details_safe={
                "expected_generation_id": generation_id,
                "seen_generation_id": None,
                "dimension_expected": None,
                "dimension_seen": None,
            },
        )
    subjects = active_subjects(ctx)
    if subjects:
        ctx.embedding.generate_vectors(
            ctx.owner_id,
            caller_module=OWNER_MODULE,
            generation_id=generation_id,
            requests=[
                VectorRequest(subject_type=s.subject_type, subject_id=s.subject_id, text=s.text)
                for s in subjects
            ],
        )
    return len(subjects)


# --------------------------------------------------------------------------------------
# Mutations
# --------------------------------------------------------------------------------------


def _tag_row(connection: Connection, owner_id: str, tag_id: str) -> dict[str, Any] | None:
    row = (
        connection.execute(
            text('SELECT id, "text", state FROM tag WHERE owner_id = :o AND id = :id'),
            {"o": owner_id, "id": tag_id},
        )
        .mappings()
        .first()
    )
    return None if row is None else dict(row)


def _assert_text_free(connection: Connection, owner_id: str, value: str) -> None:
    """No two active tags with the same casefold + NFC text (``ENT-tag.text``)."""
    wanted = normalize_tag_text(value)
    for row in _active_tags(connection, owner_id):
        if normalize_tag_text(str(row["text"])) == wanted:
            raise _invalid(OperationId.TAG_CREATE, "text", "duplicate_active_tag")


def _children(
    connection: Connection, table: str, owner_id: str, tag_id: str
) -> dict[str, dict[str, Any]]:
    rows = connection.execute(
        text(f'SELECT id, "text", state FROM {table} WHERE owner_id = :o AND tag_id = :t'),
        {"o": owner_id, "t": tag_id},
    ).mappings()
    return {normalize_tag_text(str(row["text"])): dict(row) for row in rows}


def _plan_children(
    ctx: TagContext,
    connection: Connection | None,
    table: str,
    tag_id: str,
    wanted: Sequence[str],
) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    """``(new rows (id, text), ids to reactivate, ids to remove)`` to make ``wanted`` active.

    ``ux_tag_alias_owner_tag_text`` covers removed rows too, so re-adding a text the tag once
    had re-activates that row — same id, same text, and its vector is still valid.
    """
    existing = {} if connection is None else _children(connection, table, ctx.owner_id, tag_id)
    wanted_keys = {normalize_tag_text(item): item for item in wanted}
    new_rows: list[tuple[str, str]] = []
    reactivate: list[str] = []
    for key, value in wanted_keys.items():
        row = existing.get(key)
        if row is None:
            new_rows.append((ctx.new_id(), value))
        elif row["state"] != STATE_ACTIVE:
            reactivate.append(str(row["id"]))
    remove = [
        str(row["id"])
        for key, row in existing.items()
        if key not in wanted_keys and row["state"] == STATE_ACTIVE
    ]
    return new_rows, reactivate, remove


def _write_children(
    connection: Connection,
    ctx: TagContext,
    table: str,
    tag_id: str,
    plan: tuple[list[tuple[str, str]], list[str], list[str]],
    now: str,
) -> None:
    new_rows, reactivate, remove = plan
    for child_id, value in new_rows:
        connection.execute(
            text(
                f'INSERT INTO {table} (id, owner_id, tag_id, "text", state, created_at) '
                "VALUES (:id, :o, :t, :text, 'active', :at)"
            ),
            {"id": child_id, "o": ctx.owner_id, "t": tag_id, "text": value, "at": now},
        )
    for child_id in reactivate:
        connection.execute(
            text(f"UPDATE {table} SET state = 'active' WHERE owner_id = :o AND id = :id"),
            {"o": ctx.owner_id, "id": child_id},
        )
    for child_id in remove:
        connection.execute(
            text(f"UPDATE {table} SET state = 'removed' WHERE owner_id = :o AND id = :id"),
            {"o": ctx.owner_id, "id": child_id},
        )


_ALIAS_TYPE = SubjectType.TAG_ALIAS
_EXCLUSION_TYPE = SubjectType.TAG_EXCLUSION


def create_tag(ctx: TagContext, *, idempotency_key: str, body: Mapping[str, Any]) -> dict[str, Any]:
    """``tag.create`` — the tag, its vectors, a new config version and one backfill activation.

    Commit point: the single ``engine.begin()`` block. The tag row, its aliases and exclusions,
    the config version and the ``backfill_ledger`` activation commit together, so "a tag that
    exists without its activation" cannot be observed (``backfill.open_activation`` docstring).
    """
    operation = OperationId.TAG_CREATE
    _reject_unknown(body, {"text", "aliases", "exclusions", "similarity_threshold"}, operation)
    replayed = _replay(ctx, operation, idempotency_key, body)
    if replayed is not None:
        return replayed
    value = _clean_text(body.get("text"), operation, "text")
    aliases = _clean_texts(body.get("aliases"), operation, "aliases")
    exclusions = _clean_texts(body.get("exclusions"), operation, "exclusions")
    threshold = _clean_threshold(body.get("similarity_threshold"), operation)
    if ctx.activation is None:
        # Not a soft skip: D28 makes the activation part of tag.create, and a tag created
        # without one would have a backfill history nobody could reconstruct.
        raise TagError(ErrorCode.INTERNAL, details_safe={"operation_id": operation.value})
    _assert_writable(ctx, operation)
    with ctx.engine.connect() as connection:
        _assert_text_free(connection, ctx.owner_id, value)
        ctx.activation.preflight(connection, owner_id=ctx.owner_id)

    tag_id = ctx.new_id()
    alias_plan = _plan_children(ctx, None, "tag_alias", tag_id, aliases)
    exclusion_plan = _plan_children(ctx, None, "tag_exclusion", tag_id, exclusions)
    vectors = _embed(
        ctx,
        [_Subject(SubjectType.TAG, tag_id, value)]
        + [_Subject(_ALIAS_TYPE, i, t) for i, t in alias_plan[0]]
        + [_Subject(_EXCLUSION_TYPE, i, t) for i, t in exclusion_plan[0]],
    )

    now = ctx.now()
    with ctx.engine.begin() as connection:
        _assert_text_free(connection, ctx.owner_id, value)
        connection.execute(
            text(
                'INSERT INTO tag (id, owner_id, "text", similarity_threshold, state, '
                "created_at, updated_at, removed_at) "
                "VALUES (:id, :o, :text, :threshold, 'active', :at, :at, NULL)"
            ),
            {"id": tag_id, "o": ctx.owner_id, "text": value, "threshold": threshold, "at": now},
        )
        _write_children(connection, ctx, "tag_alias", tag_id, alias_plan, now)
        _write_children(connection, ctx, "tag_exclusion", tag_id, exclusion_plan, now)
        activation = ctx.activation.open_activation(
            connection, owner_id=ctx.owner_id, tag_id=tag_id, tag_text=value
        )
        version = _materialize_version(ctx, connection)
        response = {
            "tag": _tag_view(connection, ctx.owner_id, tag_id),
            "tag_config_version": version.summary(),
            "backfill": dict(activation),
            "vectors": vectors,
        }
    return _remember(ctx, operation, idempotency_key, body, response)


def update_tag(
    ctx: TagContext, *, tag_id: str, idempotency_key: str, body: Mapping[str, Any]
) -> dict[str, Any]:
    """``tag.update`` — threshold, aliases and exclusions; a new config version.

    ``text`` is **not** editable (``CR-TC-TAG-06``): the backfill subscription identity is the
    normalized text (§6.2), and vectors are keyed by ``(subject, generation)`` with no text in
    the key, so editing it in place would silently re-key a subscription and keep a vector of the
    old words. Changing a tag's text is delete + create, which is what both ledgers expect.
    Published reports are untouched (I05): they point at an immutable version row.
    """
    operation = OperationId.TAG_UPDATE
    _reject_unknown(body, {"aliases", "exclusions", "similarity_threshold"}, operation)
    replayed = _replay(ctx, operation, idempotency_key, body)
    if replayed is not None:
        return replayed
    if not body:
        raise _invalid(operation, "body", "required_missing")
    aliases = _clean_texts(body.get("aliases"), operation, "aliases") if "aliases" in body else None
    exclusions = (
        _clean_texts(body.get("exclusions"), operation, "exclusions")
        if "exclusions" in body
        else None
    )
    threshold = (
        _clean_threshold(body.get("similarity_threshold"), operation)
        if "similarity_threshold" in body
        else None
    )
    _assert_writable(ctx, operation)
    with ctx.engine.connect() as connection:
        row = _tag_row(connection, ctx.owner_id, tag_id)
        if row is None or row["state"] != STATE_ACTIVE:
            raise _not_found(operation)
        alias_plan = (
            _plan_children(ctx, connection, "tag_alias", tag_id, aliases)
            if aliases is not None
            else ([], [], [])
        )
        exclusion_plan = (
            _plan_children(ctx, connection, "tag_exclusion", tag_id, exclusions)
            if exclusions is not None
            else ([], [], [])
        )
    vectors = _embed(
        ctx,
        [_Subject(_ALIAS_TYPE, i, t) for i, t in alias_plan[0]]
        + [_Subject(_EXCLUSION_TYPE, i, t) for i, t in exclusion_plan[0]],
    )
    now = ctx.now()
    with ctx.engine.begin() as connection:
        row = _tag_row(connection, ctx.owner_id, tag_id)
        if row is None or row["state"] != STATE_ACTIVE:
            raise _not_found(operation)
        if "similarity_threshold" in body:
            connection.execute(
                text(
                    "UPDATE tag SET similarity_threshold = :th, updated_at = :at "
                    "WHERE owner_id = :o AND id = :id"
                ),
                {"th": threshold, "at": now, "o": ctx.owner_id, "id": tag_id},
            )
        else:
            connection.execute(
                text("UPDATE tag SET updated_at = :at WHERE owner_id = :o AND id = :id"),
                {"at": now, "o": ctx.owner_id, "id": tag_id},
            )
        _write_children(connection, ctx, "tag_alias", tag_id, alias_plan, now)
        _write_children(connection, ctx, "tag_exclusion", tag_id, exclusion_plan, now)
        version = _materialize_version(ctx, connection)
        response = {
            "tag": _tag_view(connection, ctx.owner_id, tag_id),
            "tag_config_version": version.summary(),
            "vectors": vectors,
        }
    return _remember(ctx, operation, idempotency_key, body, response)


def delete_tag(
    ctx: TagContext, *, tag_id: str, idempotency_key: str, body: Mapping[str, Any]
) -> dict[str, Any]:
    """``tag.delete`` — ``state = removed``; nothing else is deleted (I01, I08, ``§8.5``).

    Deleting an already-removed tag is an idempotent result, not an error (``ports.yaml``).
    Posts, works, analyses, Saved rows, vectors and both ledgers are untouched: removing a tag
    only changes which rows the next config version contains.
    """
    operation = OperationId.TAG_DELETE
    _reject_unknown(body, {"request_id"}, operation)
    replayed = _replay(ctx, operation, idempotency_key, body)
    if replayed is not None:
        return replayed
    _assert_writable(ctx, operation)
    now = ctx.now()
    with ctx.engine.begin() as connection:
        row = _tag_row(connection, ctx.owner_id, tag_id)
        if row is None:
            raise _not_found(operation)
        already = row["state"] == STATE_REMOVED
        if not already:
            connection.execute(
                text(
                    "UPDATE tag SET state = 'removed', removed_at = :at, updated_at = :at "
                    "WHERE owner_id = :o AND id = :id"
                ),
                {"at": now, "o": ctx.owner_id, "id": tag_id},
            )
        version = _materialize_version(ctx, connection)
        response = {
            "tag": _tag_view(connection, ctx.owner_id, tag_id),
            "tag_config_version": version.summary(),
            "already_removed": already,
        }
    return _remember(ctx, operation, idempotency_key, body, response)


# --------------------------------------------------------------------------------------
# tag.preview_matches
# --------------------------------------------------------------------------------------


def _default_threshold(connection: Connection, owner_id: str) -> float:
    """``settings['reporting.default_similarity_threshold']``, else the §4.2 default.

    Reading the table is not calling ``settings.*`` (the same reasoning as
    ``report/backfill.py``'s ``TableSettings``); the shape is ``ENT-settings``.
    """
    row = connection.execute(
        text('SELECT value_json FROM settings WHERE owner_id = :o AND "key" = :k'),
        {"o": owner_id, "k": SETTING_DEFAULT_THRESHOLD},
    ).first()
    if row is None:
        return DEFAULT_SIMILARITY_THRESHOLD
    try:
        return float(json.loads(str(row[0])))
    except (TypeError, ValueError):
        return DEFAULT_SIMILARITY_THRESHOLD


def _fingerprint(generation: Mapping[str, Any]) -> GenerationFingerprint:
    return GenerationFingerprint(
        generation_id=_generation_id(generation),
        model_name=str(generation["model_name"]),
        model_version=str(generation["model_version"]),
        dimension=int(generation["dimension"]),
        normalization=Normalization(str(generation["normalization"])),
    )


def _stored_vector(
    connection: Connection,
    owner_id: str,
    subject_type: SubjectType,
    subject_id: str,
    fingerprint: GenerationFingerprint,
) -> Vector | None:
    row = connection.execute(
        text(
            "SELECT vector FROM tag_vector WHERE owner_id = :o AND subject_type = :st "
            "AND subject_id = :sid AND embedding_generation_id = :g"
        ),
        {
            "o": owner_id,
            "st": subject_type.value,
            "sid": subject_id,
            "g": fingerprint.generation_id,
        },
    ).first()
    return None if row is None else Vector.from_blob(bytes(row[0]), fingerprint)


def preview_matches(ctx: TagContext, body: Mapping[str, Any]) -> dict[str, Any]:
    """``tag.preview_matches`` — which labels a tag (or a draft text) would match, and how well.

    Read-only: a draft text gets a temporary vector from the local model and nothing is written
    (``ports.yaml``). Scores follow ``selection.md`` §3-§4: cosine rounded half-up to four
    decimals, the max over the tag and its active aliases, the tag's own threshold or the
    default. Exclusions are reported, not applied silently: a label that a tag-scoped or global
    exclusion would remove is listed under ``excluded_labels``.

    With no tag at all and nothing to preview, the answer is the empty state of ``SCR-topics``
    — never "Không có nghiên cứu mới" (fixture ``ui/sc51``).
    """
    operation = OperationId.TAG_PREVIEW_MATCHES
    _reject_unknown(body, {"tag_id", "text", "similarity_threshold"}, operation)
    tag_id = body.get("tag_id")
    draft = body.get("text")
    if tag_id is not None and draft is not None:
        raise _invalid(operation, "tag_id", "mutually_exclusive")
    trial = _clean_threshold(body.get("similarity_threshold"), operation)

    with ctx.engine.connect() as connection:
        if tag_id is None and draft is None:
            if not _active_tags(connection, ctx.owner_id):
                return {
                    "matched_labels": [],
                    "excluded_labels": [],
                    "threshold_used": None,
                    "embedding_generation_id": None,
                    "empty_state_vi": EMPTY_TAGS_MESSAGE_VI,
                }
            raise _invalid(operation, "tag_id", "required_missing")

        generation = _active_generation(ctx)
        if generation is None:
            raise TagError(
                ErrorCode.EMBEDDING_GENERATION_MISMATCH,
                message_safe="Chưa có thế hệ embedding nào đang dùng, nên chưa xem trước được.",
                details_safe={
                    "expected_generation_id": None,
                    "seen_generation_id": None,
                    "dimension_expected": None,
                    "dimension_seen": None,
                },
            )
        fingerprint = _fingerprint(generation)

        subjects: list[Vector] = []
        exclusion_vectors: list[Vector] = []
        threshold: float
        if tag_id is not None:
            if not isinstance(tag_id, str):
                raise _invalid(operation, "tag_id", "type_invalid")
            row = _tag_row(connection, ctx.owner_id, tag_id)
            if row is None or row["state"] != STATE_ACTIVE:
                raise _not_found(operation)
            view = _tag_view(connection, ctx.owner_id, tag_id)
            keys = [(SubjectType.TAG, tag_id)] + [
                (SubjectType.TAG_ALIAS, str(a["alias_id"])) for a in view["aliases"]
            ]
            for subject_type, subject_id in keys:
                vector = _stored_vector(
                    connection, ctx.owner_id, subject_type, subject_id, fingerprint
                )
                if vector is None:
                    raise TagError(
                        ErrorCode.EMBEDDING_GENERATION_MISMATCH,
                        details_safe={
                            "expected_generation_id": fingerprint.generation_id,
                            "seen_generation_id": None,
                            "dimension_expected": fingerprint.dimension,
                            "dimension_seen": None,
                        },
                    )
                subjects.append(vector)
            scoped = [(str(e["exclusion_id"])) for e in view["exclusions"]]
            globals_ = connection.execute(
                text(
                    "SELECT id FROM tag_exclusion WHERE owner_id = :o AND tag_id IS NULL "
                    "AND state = 'active' ORDER BY id"
                ),
                {"o": ctx.owner_id},
            ).scalars()
            for exclusion_id in scoped + [str(value) for value in globals_]:
                vector = _stored_vector(
                    connection, ctx.owner_id, SubjectType.TAG_EXCLUSION, exclusion_id, fingerprint
                )
                if vector is not None:
                    exclusion_vectors.append(vector)
            own = view["similarity_threshold"]
            threshold = (
                trial
                if trial is not None
                else (
                    round_half_up(float(own))
                    if own is not None
                    else round_half_up(_default_threshold(connection, ctx.owner_id))
                )
            )
        else:
            cleaned = _clean_text(draft, operation, "text")
            if ctx.encoder is None:
                raise TagError(
                    ErrorCode.EMBEDDING_GENERATION_MISMATCH,
                    message_safe=(
                        "Chưa cấu hình model embedding cục bộ, nên chưa xem trước được chữ nháp."
                    ),
                    details_safe={
                        "expected_generation_id": fingerprint.generation_id,
                        "seen_generation_id": None,
                        "dimension_expected": fingerprint.dimension,
                        "dimension_seen": None,
                    },
                )
            encoder_fingerprint = GenerationFingerprint(
                generation_id=fingerprint.generation_id,
                model_name=ctx.encoder.model_name,
                model_version=ctx.encoder.model_version,
                dimension=ctx.encoder.dimension,
                normalization=ctx.encoder.normalization,
            )
            if encoder_fingerprint != fingerprint:
                raise TagError(
                    ErrorCode.EMBEDDING_GENERATION_MISMATCH,
                    details_safe={
                        "expected_generation_id": fingerprint.generation_id,
                        "seen_generation_id": None,
                        "dimension_expected": fingerprint.dimension,
                        "dimension_seen": ctx.encoder.dimension,
                    },
                )
            subjects.append(
                Vector(fingerprint=fingerprint, values=ctx.encoder.encode([cleaned])[0])
            )
            threshold = (
                trial
                if trial is not None
                else round_half_up(_default_threshold(connection, ctx.owner_id))
            )

        labels = connection.execute(
            text(
                "SELECT target_key, label_text, vector FROM work_label WHERE owner_id = :o "
                "AND embedding_generation_id = :g AND vector IS NOT NULL "
                "ORDER BY target_key, label_text"
            ),
            {"o": ctx.owner_id, "g": fingerprint.generation_id},
        ).mappings()
        matched: list[dict[str, Any]] = []
        excluded: list[dict[str, Any]] = []
        for label in labels:
            label_vector = Vector.from_blob(bytes(label["vector"]), fingerprint)
            score = round_half_up(max(cosine(subject, label_vector) for subject in subjects))
            if score < threshold:
                continue
            item = {
                "target_key": label["target_key"],
                "label_text": label["label_text"],
                "score": score,
            }
            if any(
                round_half_up(cosine(exclusion, label_vector)) >= threshold
                for exclusion in exclusion_vectors
            ):
                excluded.append(item)
            else:
                matched.append(item)
    matched.sort(key=lambda item: (-item["score"], item["target_key"], item["label_text"]))
    excluded.sort(key=lambda item: (-item["score"], item["target_key"], item["label_text"]))
    return {
        "matched_labels": matched,
        "excluded_labels": excluded,
        "threshold_used": threshold,
        "embedding_generation_id": fingerprint.generation_id,
        "empty_state_vi": None,
    }


__all__ = [
    "DEFAULT_SIMILARITY_THRESHOLD",
    "EMPTY_TAGS_MESSAGE_VI",
    "OWNER_MODULE",
    "ActivationPort",
    "EmbeddingPort",
    "TagConfigVersionRecord",
    "TagContext",
    "TagError",
    "config_version",
    "content_hash_of",
    "create_tag",
    "delete_tag",
    "embed_into_generation",
    "active_subjects",
    "freeze_config_version",
    "get_active_config_version",
    "list_tags",
    "live_payload",
    "new_ulid",
    "normalize_tag_text",
    "preview_matches",
    "update_tag",
]
