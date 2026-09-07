"""``MOD-saved-service`` — ``save.create``, ``save.remove``, ``save.list``.

The one sentence this module exists to make true
------------------------------------------------
*Save is an immutable snapshot of the target as it read at the moment of saving.* Dropping a
tag, the post being deleted on X, a restart, a backup/restore cycle and an identity merge all
leave ``saved_snapshot`` byte-identical (``I08``, ``I17``, ``REQ-D55``, ``REQ-AC12``). There is
consequently **no UPDATE and no DELETE against ``saved_snapshot`` anywhere in this package** —
not in a repair path, not in a migration helper, not behind a flag. ``save.remove`` moves
``saved_item.state`` to ``unsaved`` and touches nothing else, because un-saving is the *first*
of the three distinct operations of SRC-SPEC §7.3 and is not deletion of anything.

``TXN-save-target`` (``contracts/data/entities.yaml``)
-----------------------------------------------------
Commit point: one ``BEGIN…COMMIT`` writing the ``saved_snapshot`` row and the ``saved_item``
row together, opened in :func:`create_save` and nowhere else. An external observer never sees a
``saved_item`` pointing at an uncommitted snapshot, and never sees two ``active`` rows for one
``target_key``.

**UNIQUE is the arbiter, not a pre-read.** :func:`create_save` does not look for an existing
active row before inserting; it inserts and lets the partial unique index
``ux_saved_active_owner_target`` decide. ``entities.yaml`` ``ENT-saved-item.concurrency``
lists "check-then-insert without a lock" as a forbidden implementation, and a pre-read would be
exactly that: between the SELECT and the INSERT the other channel commits. The losing
transaction rolls back **whole** — its snapshot row included, so no orphan snapshot is left —
then reads the committed row and answers ``already_saved: true`` with that row's id. It never
retries the insert (fixture ``identity/d-concurrent-save-app-telegram``).

Two module boundaries, deliberately not crossed
-----------------------------------------------
*Identity.* Card §4 lists ``identity.resolve_target`` as a consumed operation, but
``contracts/modules.yaml`` gives ``MOD-saved-service`` ``outbound_operations: []`` and carries
no ``allowed_edges`` row with this module as caller; under ``default_deny`` that call would be
``FORBIDDEN_EDGE``. The registry wins over the card's prose (card §5 says so itself), so this
module resolves the target by reading the ``work`` / ``post`` row it was handed a reference to
and never calls the identity service. Raised as ``CR-TC-SAVED-01``.

*Storage.* Likewise ``storage.get_health`` has exactly two permitted callers
(``MOD-health-service``, ``MOD-job-service``). What this module uses is the in-process
:class:`~server.app.storage.guard.StorageGuard` that every mutating service uses —
``guard.assert_writable(...)`` before the transaction opens — which is a local gate, not a call
across the ``MOD-data-store`` edge.

Error codes come from ``contracts/errors.yaml`` through the generated registry; none is spelled
as a literal. The R5-01 boundary table decides which one: a principal class that may not call
the operation is ``UNAUTHORIZED``, an in-process call across an unregistered edge is
``FORBIDDEN_EDGE``, a missing CSRF proof on an admitted session is ``CSRF_REJECTED``, and a
Telegram command from a chat that is not linked is ``UNAUTHORIZED_COMMAND``.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine
from sqlalchemy.exc import IntegrityError

from server.app.auth.middleware import ALLOWED_CALLERS
from server.app.saved import snapshot as snapshot_module

OWNER_MODULE: Final[str] = "MOD-saved-service"

#: The two save channels of ``ENT-saved-item.save_channel``.
SAVE_CHANNELS: Final[frozenset[str]] = frozenset({"app", "telegram"})

#: ``ENT-saved-item.state``.
STATE_ACTIVE: Final[str] = "active"
STATE_UNSAVED: Final[str] = "unsaved"

#: The two partial unique indexes of ``saved_item``. Their names are load-bearing: they are
#: how an ``IntegrityError`` is told apart from any other constraint failure, and each one
#: means a different answer (a concurrent save vs. a repeated Telegram callback).
IX_ACTIVE: Final[str] = "ux_saved_active_owner_target"
IX_IDEMPOTENCY: Final[str] = "ux_saved_idempotency"

_CROCKFORD: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

#: The ``forbidden_edges`` rows of ``contracts/modules.yaml`` that end at this module, so a
#: refusal can cite the registry row instead of only asserting one exists.
FORBIDDEN_EDGE_REF: Final[dict[tuple[str, str], str]] = {
    ("MOD-x-collector", OWNER_MODULE): "FE-06",
    ("MOD-analysis-worker", OWNER_MODULE): "FE-14",
    ("EXT-telegram-api", OWNER_MODULE): "FE-36",
}

_HTTP_STATUS: Final[dict[ErrorCode, int]] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.UNAUTHORIZED_COMMAND: 403,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}

#: ``details_safe_keys`` of ``contracts/errors.yaml``, copied per code. The envelope rule is
#: "unknown key ⇒ the producer refuses it rather than sending it", so this is enforced in the
#: constructor: a details key that leaked a chat id or a column name would be a data leak the
#: envelope contract exists to prevent, and catching it at construction means it can never be
#: serialised even once.
DETAILS_SAFE_KEYS: Final[dict[ErrorCode, frozenset[str]]] = {
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
    ErrorCode.UNAUTHORIZED_COMMAND: frozenset({"command_kind", "rejection_reason_code"}),
    ErrorCode.CSRF_REJECTED: frozenset({"operation_id"}),
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
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
    ErrorCode.INTERNAL: frozenset({"correlation_id", "operation_id"}),
}

_MESSAGE_SAFE: Final[dict[ErrorCode, str]] = {
    ErrorCode.VALIDATION_ERROR: "Yêu cầu không hợp lệ.",
    ErrorCode.UNAUTHORIZED: "Bạn cần đăng nhập để thực hiện thao tác này.",
    ErrorCode.UNAUTHORIZED_COMMAND: "Lệnh này không được chấp nhận từ cuộc trò chuyện này.",
    ErrorCode.CSRF_REJECTED: "Yêu cầu thiếu hoặc sai CSRF token.",
    ErrorCode.FORBIDDEN_EDGE: "Lời gọi này không nằm trong các kết nối được phép.",
    ErrorCode.NOT_FOUND: "Không tìm thấy dữ liệu được yêu cầu.",
    ErrorCode.CONFLICT: "Dữ liệu đã đổi trong lúc xử lý. Hãy đọc lại rồi thử lại.",
    ErrorCode.IDEMPOTENCY_CONFLICT: "Khóa chống trùng đã được dùng cho một nội dung khác.",
    ErrorCode.STORAGE_WRITE_FAILED: "Hệ thống đang không ghi được dữ liệu. Chưa có gì được lưu.",
    ErrorCode.INTERNAL: "Có lỗi không mong đợi.",
}


class SavedError(Exception):
    """A refusal carrying one registered error code and the contract's envelope.

    Never carries transcript text, a cookie, a token or a chat id: ``details_safe`` is the
    only channel out of here and SRC-PLAN §5.1 closes it to secrets.
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
        fallback = _MESSAGE_SAFE[ErrorCode.INTERNAL]
        self.message_safe = message_safe or _MESSAGE_SAFE.get(code, fallback)
        self.details_safe = dict(details_safe or {})
        self.retry_after_ms = retry_after_ms
        unknown = set(self.details_safe) - DETAILS_SAFE_KEYS.get(code, frozenset())
        if unknown:
            # errors.yaml §error_envelope: "Khóa lạ ⇒ producer tự từ chối, không gửi ra."
            raise ValueError(f"{code.value} may not carry details keys {sorted(unknown)}")
        super().__init__(f"{code.value}: {self.message_safe}")

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """``contracts/errors.yaml`` → ``error_envelope``."""
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


class TelegramLinkResolver(Protocol):
    """Seam owned by ``TC-telegram-linking-auth`` (``MOD-telegram-adapter``).

    ``save.create`` may be reached from a chat, but only from a **linked** one. This module
    does not implement linking; it asks. A resolver that answers ``None`` means the chat is
    not linked, and the answer to that is ``UNAUTHORIZED_COMMAND`` with zero mutations —
    never a save attributed to a guessed owner.
    """

    def owner_for_chat(self, chat_id: str) -> str | None:  # pragma: no cover - protocol
        ...


# --------------------------------------------------------------------------------------
# Small value types
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class TargetRef:
    """A tagged union reference: ``work:<ulid>`` or ``post:<ulid>``."""

    kind: str
    identifier: str

    @property
    def key(self) -> str:
        return snapshot_module.target_key(self.kind, self.identifier)

    @classmethod
    def parse(cls, raw: str) -> TargetRef:
        """Parse the ``target_key`` spelling used in paths and requests.

        :raises SavedError: ``VALIDATION_ERROR`` for anything that is not exactly
            ``work:<26 Crockford chars>`` or ``post:<…>``. Nothing is repaired: a nearly
            correct key is rejected rather than coerced.
        """
        kind, separator, identifier = raw.partition(":")
        if separator != ":" or kind not in {"work", "post"} or not _is_ulid(identifier):
            raise _validation_error(OperationId.SAVE_CREATE, "target_key", "pattern_not_matched")
        return cls(kind=kind, identifier=identifier)

    @classmethod
    def from_object(cls, target: Mapping[str, Any], operation: OperationId) -> TargetRef:
        """Read the tagged union of ``target.schema.json``: exactly one id must be set."""
        kind = target.get("kind")
        work_id = target.get("work_id")
        post_id = target.get("post_id")
        if kind == "work" and _is_ulid(work_id) and post_id is None:
            return cls(kind="work", identifier=str(work_id))
        if kind == "post" and _is_ulid(post_id) and work_id is None:
            return cls(kind="post", identifier=str(post_id))
        raise _validation_error(operation, "target", "tagged_union_not_exactly_one")


@dataclass(frozen=True)
class SaveResult:
    """What ``save.create`` answers.

    ``status`` is ``created`` or ``already_saved`` — the two values ``contracts/ports.yaml``
    names for this operation's response. ``already_saved`` is a **response field**, not an
    error code (``entities.yaml`` ``error_code_note_vi``): the losing side of a concurrent
    save and the 2nd..5th press of a Telegram button both get a normal answer carrying the
    id of the row that did commit, which is what keeps "5 presses, 1 row, 5 replies" true.
    """

    saved_item_id: str
    status: str
    saved_at: str
    saved_snapshot_id: str
    content_hash: str

    @property
    def already_saved(self) -> bool:
        return self.status == "already_saved"


@dataclass(frozen=True)
class RemoveResult:
    """What ``save.remove`` answers. ``removed`` is False on an idempotent repeat."""

    saved_item_id: str
    state: str
    unsaved_at: str | None
    removed: bool
    saved_snapshot_id: str


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------


def utc_now_ms() -> str:
    """Server clock, RFC 3339 UTC, milliseconds (``entities.yaml`` §conventions)."""
    moment = datetime.now(tz=UTC)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def new_ulid() -> str:
    """A ULID: 48-bit millisecond timestamp + 80 random bits, Crockford base32."""
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def _is_ulid(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 26 and all(c in _CROCKFORD for c in value)


def _require_edge(operation: OperationId, caller_module: str) -> None:
    """Default deny (``contracts/modules.yaml``). Wrong caller ⇒ ``FORBIDDEN_EDGE``, not 401."""
    if caller_module not in ALLOWED_CALLERS[operation]:
        raise SavedError(
            ErrorCode.FORBIDDEN_EDGE,
            details_safe={
                "caller_module": caller_module,
                "callee_module": OWNER_MODULE,
                # `forbidden_edge_ref` stays None unless modules.yaml names an `FE-nn` for
                # this pair; inventing an id would point a reader at a row that is not there.
                "forbidden_edge_ref": FORBIDDEN_EDGE_REF.get((caller_module, OWNER_MODULE)),
            },
        )


def _validation_error(operation: OperationId, field_path: str, violation_kind: str) -> SavedError:
    return SavedError(
        ErrorCode.VALIDATION_ERROR,
        details_safe={
            "operation_id": operation.value,
            "field_path": field_path,
            "violation_kind": violation_kind,
        },
    )


def _not_found(operation: OperationId, resource_kind: str) -> SavedError:
    return SavedError(
        ErrorCode.NOT_FOUND,
        details_safe={"operation_id": operation.value, "resource_kind": resource_kind},
    )


def _assert_writable(guard: Any, operation: OperationId) -> None:
    """``guard.assert_writable`` before the transaction opens (``I02``).

    A refusal is translated into this module's error type without inventing a code: the
    guard already produced the contract envelope, and its ``code`` is carried through.
    """
    if guard is None:
        return
    try:
        guard.assert_writable(operation)
    except Exception as refused:  # StorageRefused; typed loosely to avoid a hard import cycle
        envelope = getattr(refused, "envelope", None)
        if not isinstance(envelope, dict):
            raise
        code = ErrorCode(envelope["code"])
        raise SavedError(
            code,
            message_safe=envelope.get("message_safe"),
            details_safe=envelope.get("details_safe") or {},
            retry_after_ms=envelope.get("retry_after_ms"),
        ) from refused


#: SQLite names the **columns** of a violated partial UNIQUE index, not the index. Both
#: spellings are matched: the column list is what today's library reports, and the index name
#: is what a future one (or another engine) would. Guessing from "an IntegrityError happened"
#: instead would swallow a genuinely different constraint failure -- a broken foreign key, say
#: -- and answer ``already_saved`` to a request that stored nothing.
_INDEX_SIGNATURES: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    (IX_ACTIVE, (IX_ACTIVE, "saved_item.target_key")),
    (IX_IDEMPOTENCY, (IX_IDEMPOTENCY, "saved_item.idempotency_key")),
)


def _violated_index(error: IntegrityError) -> str | None:
    """Which unique index an ``IntegrityError`` came from, if it is one of ours."""
    message = str(error.orig) if error.orig is not None else str(error)
    if "UNIQUE constraint failed" not in message:
        return None
    for index, signatures in _INDEX_SIGNATURES:
        if any(signature in message for signature in signatures):
            return index
    return None


@contextmanager
def _transaction(engine: Engine) -> Iterator[Connection]:
    """The single ``BEGIN…COMMIT`` of ``TXN-save-target``.

    An :class:`~sqlalchemy.Engine` is required rather than a caller-supplied
    :class:`~sqlalchemy.Connection`: the concurrency rule needs this transaction to be able
    to roll back *entirely* on a unique violation, and a transaction joined from a caller
    cannot do that without discarding the caller's work too.
    """
    with engine.begin() as connection:
        yield connection


# --------------------------------------------------------------------------------------
# Repository — the only place SQL for this module's tables is written
# --------------------------------------------------------------------------------------


class SavedRepository:
    """Row access for ``saved_item``, ``saved_snapshot`` and the rows a snapshot copies.

    There is no ``update_snapshot`` and no ``delete_snapshot`` method. That is not an
    oversight: ``ENT-saved-snapshot.immutability`` says the row count only ever grows, and a
    method that could break it would eventually be called.
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    # -- reads -------------------------------------------------------------------------

    def work_row(self, owner_id: str, work_id: str) -> dict[str, Any] | None:
        row = (
            self._connection.exec_driver_sql(
                "SELECT id, canonical_doi, canonical_arxiv_id, title, paper_url, code_url,"
                "       identity_state, merged_into_work_id, content_state"
                "  FROM work WHERE owner_id = ? AND id = ?",
                (owner_id, work_id),
            )
            .mappings()
            .first()
        )
        return dict(row) if row is not None else None

    def post_row(self, owner_id: str, post_id: str) -> dict[str, Any] | None:
        row = (
            self._connection.exec_driver_sql(
                "SELECT id, x_post_id, author_handle, url, text, published_at, discovered_at,"
                "       content_state, source_deleted_observed_at"
                "  FROM post WHERE owner_id = ? AND id = ?",
                (owner_id, post_id),
            )
            .mappings()
            .first()
        )
        return dict(row) if row is not None else None

    def posts_of_work(
        self, owner_id: str, work_id: str, *, limit: int = 200
    ) -> list[dict[str, Any]]:
        """The posts that led to a work, oldest first, capped at the schema's 200.

        Ordered by ``discovered_at`` then ``id`` so the array — and therefore the hash — is
        the same whatever order SQLite happens to return rows in.
        """
        rows = self._connection.exec_driver_sql(
            "SELECT p.id, p.x_post_id, p.author_handle, p.url, p.text, p.published_at,"
            "       p.discovered_at"
            "  FROM post AS p JOIN post_work AS pw ON pw.post_id = p.id"
            " WHERE pw.owner_id = ? AND pw.work_id = ?"
            " ORDER BY p.discovered_at, p.id LIMIT ?",
            (owner_id, work_id, limit),
        ).mappings()
        return [dict(row) for row in rows]

    def work_version_label(self, owner_id: str, work_id: str) -> str | None:
        row = (
            self._connection.exec_driver_sql(
                "SELECT wv.version_label FROM work AS w"
                "  JOIN work_version AS wv ON wv.id = w.current_work_version_id"
                " WHERE w.owner_id = ? AND w.id = ?",
                (owner_id, work_id),
            )
            .mappings()
            .first()
        )
        return str(row["version_label"]) if row is not None else None

    def analysis_row(self, owner_id: str, analysis_id: str) -> dict[str, Any] | None:
        row = (
            self._connection.exec_driver_sql(
                "SELECT id, target_key, task_type, status, payload, payload_hash,"
                "       evidence_level, analyzed_at, generation_number, provider_name, model_name"
                "  FROM analysis WHERE owner_id = ? AND id = ?",
                (owner_id, analysis_id),
            )
            .mappings()
            .first()
        )
        return dict(row) if row is not None else None

    def latest_valid_summary(self, owner_id: str, target_key_value: str) -> dict[str, Any] | None:
        """The newest ``valid`` summary analysis **as at the start of this transaction**.

        Used only when the caller did not name the revision it was reading
        (``source_report_item_id`` absent), which is the Work-detail branch of
        ``TXN-save-target.snapshot_source_rule``. Inside one transaction this cannot pick up
        a newer row that appeared while the user was reading, which is the forbidden effect
        of that rule.
        """
        row = (
            self._connection.exec_driver_sql(
                "SELECT id, target_key, task_type, status, payload, payload_hash,"
                "       evidence_level, analyzed_at, generation_number, provider_name, model_name"
                "  FROM analysis"
                " WHERE owner_id = ? AND target_key = ? AND status = 'valid'"
                "   AND task_type = 'summary'"
                " ORDER BY analyzed_at DESC, id DESC LIMIT 1",
                (owner_id, target_key_value),
            )
            .mappings()
            .first()
        )
        return dict(row) if row is not None else None

    def topic_labels(self, owner_id: str, target_key_value: str, *, limit: int = 50) -> list[str]:
        """Open topic labels attached to the target (REQ-D22), captured at save time."""
        rows = self._connection.exec_driver_sql(
            "SELECT DISTINCT label_text FROM work_label"
            " WHERE owner_id = ? AND target_key = ? ORDER BY label_text LIMIT ?",
            (owner_id, target_key_value, limit),
        ).mappings()
        return [str(row["label_text"]) for row in rows]

    def active_item(self, owner_id: str, target_key_value: str) -> dict[str, Any] | None:
        return self._item_where(
            "owner_id = ? AND target_key = ? AND state = 'active'", (owner_id, target_key_value)
        )

    def any_item(self, owner_id: str, target_key_value: str) -> dict[str, Any] | None:
        """The most recent row for this target whatever its state — the idempotent repeat."""
        return self._item_where(
            "owner_id = ? AND target_key = ? ORDER BY saved_at DESC, id DESC",
            (owner_id, target_key_value),
        )

    def item_by_idempotency_key(self, owner_id: str, key: str) -> dict[str, Any] | None:
        return self._item_where("owner_id = ? AND idempotency_key = ?", (owner_id, key))

    def _item_where(self, predicate: str, parameters: tuple[Any, ...]) -> dict[str, Any] | None:
        row = (
            self._connection.exec_driver_sql(
                "SELECT id, owner_id, target_kind, target_work_id, target_post_id, target_key,"
                "       state, saved_at, unsaved_at, save_channel, saved_snapshot_id,"
                "       source_report_item_id, idempotency_key, moved_by_merge_id"
                f"  FROM saved_item WHERE {predicate}",
                parameters,
            )
            .mappings()
            .first()
        )
        return dict(row) if row is not None else None

    def snapshot(self, owner_id: str, snapshot_id: str) -> dict[str, Any] | None:
        row = (
            self._connection.exec_driver_sql(
                "SELECT id, owner_id, target_kind, target_key_at_save, analysis_id_at_save,"
                "       payload, content_hash, created_at"
                "  FROM saved_snapshot WHERE owner_id = ? AND id = ?",
                (owner_id, snapshot_id),
            )
            .mappings()
            .first()
        )
        return dict(row) if row is not None else None

    def list_items(
        self, owner_id: str, *, limit: int, offset: int, query: str | None
    ) -> list[tuple[dict[str, Any], dict[str, Any]]]:
        """Active Saved rows joined to their snapshots, newest first.

        ``query`` filters on the snapshot payload text. The search runs over the *snapshot*,
        not over today's ``work``/``post`` rows, so an item whose source was deleted on X is
        still findable — which is the whole promise of the Saved screen.
        """
        predicate = "si.owner_id = ? AND si.state = 'active'"
        parameters: list[Any] = [owner_id]
        if query:
            predicate += " AND ss.payload LIKE ? ESCAPE '\\'"
            parameters.append(f"%{_escape_like(query)}%")
        parameters.extend((limit, offset))
        rows = self._connection.exec_driver_sql(
            "SELECT si.id AS item_id, si.owner_id, si.target_kind, si.target_work_id,"
            "       si.target_post_id, si.target_key, si.state, si.saved_at, si.unsaved_at,"
            "       si.save_channel, si.saved_snapshot_id, si.source_report_item_id,"
            "       si.idempotency_key, si.moved_by_merge_id,"
            "       ss.id AS snapshot_id, ss.target_kind AS snapshot_target_kind,"
            "       ss.target_key_at_save, ss.analysis_id_at_save, ss.payload,"
            "       ss.content_hash, ss.created_at"
            "  FROM saved_item AS si"
            "  JOIN saved_snapshot AS ss ON ss.id = si.saved_snapshot_id"
            f" WHERE {predicate}"
            " ORDER BY si.saved_at DESC, si.id DESC LIMIT ? OFFSET ?",
            tuple(parameters),
        ).mappings()
        pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for row in rows:
            item = {
                "id": row["item_id"],
                "owner_id": row["owner_id"],
                "target_kind": row["target_kind"],
                "target_work_id": row["target_work_id"],
                "target_post_id": row["target_post_id"],
                "target_key": row["target_key"],
                "state": row["state"],
                "saved_at": row["saved_at"],
                "unsaved_at": row["unsaved_at"],
                "save_channel": row["save_channel"],
                "saved_snapshot_id": row["saved_snapshot_id"],
                "source_report_item_id": row["source_report_item_id"],
                "idempotency_key": row["idempotency_key"],
                "moved_by_merge_id": row["moved_by_merge_id"],
            }
            snapshot_row = {
                "id": row["snapshot_id"],
                "owner_id": row["owner_id"],
                "target_kind": row["snapshot_target_kind"],
                "target_key_at_save": row["target_key_at_save"],
                "analysis_id_at_save": row["analysis_id_at_save"],
                "payload": row["payload"],
                "content_hash": row["content_hash"],
                "created_at": row["created_at"],
            }
            pairs.append((item, snapshot_row))
        return pairs

    def count_active(self, owner_id: str, target_key_value: str) -> int:
        """``COUNT(saved_item active WHERE target=T)`` — the oracle of I08, read directly."""
        return int(
            self._connection.exec_driver_sql(
                "SELECT COUNT(*) FROM saved_item"
                " WHERE owner_id = ? AND target_key = ? AND state = 'active'",
                (owner_id, target_key_value),
            ).scalar_one()
        )

    # -- writes ------------------------------------------------------------------------

    def insert_snapshot(
        self,
        *,
        snapshot_id: str,
        owner_id: str,
        target_kind: str,
        target_key_at_save: str,
        analysis_id_at_save: str | None,
        payload_json: str,
        content_hash: str,
        created_at: str,
    ) -> None:
        """INSERT only. There is no counterpart that updates or deletes this row."""
        self._connection.exec_driver_sql(
            "INSERT INTO saved_snapshot"
            " (id, owner_id, target_kind, target_key_at_save, analysis_id_at_save,"
            "  payload, content_hash, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                snapshot_id,
                owner_id,
                target_kind,
                target_key_at_save,
                analysis_id_at_save,
                payload_json,
                content_hash,
                created_at,
            ),
        )

    def insert_item(
        self,
        *,
        item_id: str,
        owner_id: str,
        target: TargetRef,
        saved_at: str,
        save_channel: str,
        saved_snapshot_id: str,
        source_report_item_id: str | None,
        idempotency_key: str | None,
    ) -> None:
        """INSERT a new ``active`` row. ``target_key`` is generated by the table, not here."""
        self._connection.exec_driver_sql(
            "INSERT INTO saved_item"
            " (id, owner_id, target_kind, target_work_id, target_post_id, state, saved_at,"
            "  unsaved_at, save_channel, saved_snapshot_id, source_report_item_id,"
            "  idempotency_key, moved_by_merge_id)"
            " VALUES (?, ?, ?, ?, ?, 'active', ?, NULL, ?, ?, ?, ?, NULL)",
            (
                item_id,
                owner_id,
                target.kind,
                target.identifier if target.kind == "work" else None,
                target.identifier if target.kind == "post" else None,
                saved_at,
                save_channel,
                saved_snapshot_id,
                source_report_item_id,
                idempotency_key,
            ),
        )

    def mark_unsaved(self, *, item_id: str, owner_id: str, unsaved_at: str) -> int:
        """``state -> 'unsaved'`` and nothing else. The snapshot pointer is left in place."""
        result = self._connection.exec_driver_sql(
            "UPDATE saved_item SET state = 'unsaved', unsaved_at = ?"
            " WHERE id = ? AND owner_id = ? AND state = 'active'",
            (unsaved_at, item_id, owner_id),
        )
        return int(result.rowcount)


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# --------------------------------------------------------------------------------------
# save.create
# --------------------------------------------------------------------------------------


def create_save(
    engine: Engine,
    *,
    owner_id: str,
    target: TargetRef,
    save_channel: str,
    analysis_id: str | None = None,
    source_report_item_id: str | None = None,
    idempotency_key: str | None = None,
    matched_tags: Sequence[Mapping[str, Any]] = (),
    caller_module: str = "MOD-web-ui",
    guard: Any = None,
    now: str | None = None,
) -> SaveResult:
    """``save.create`` — ``TXN-save-target``, one transaction, snapshot + pointer together.

    :param analysis_id: the analysis revision the caller **was reading**
        (``report_item.analysis_id`` of the report open on screen). When it is ``None`` the
        Work-detail branch applies and the newest ``valid`` summary as at the start of this
        transaction is used. A newer analysis that appeared between the read and the click is
        never substituted — that substitution is the forbidden effect of
        ``TXN-save-target.snapshot_source_rule``.
    :param matched_tags: the tags that matched at save time. Copied into the snapshot, so
        removing a tag afterwards leaves this array untouched (REQ-S8.2-07).
    :returns: ``status='created'`` for the transaction that committed, ``already_saved`` for
        one that lost the unique race or repeated a Telegram callback.
    """
    _require_edge(OperationId.SAVE_CREATE, caller_module)
    if save_channel not in SAVE_CHANNELS:
        raise _validation_error(OperationId.SAVE_CREATE, "save_channel", "enum_not_allowed")
    if idempotency_key is not None and not _valid_idempotency_key(idempotency_key):
        raise _validation_error(OperationId.SAVE_CREATE, "idempotency_key", "pattern_not_matched")
    if source_report_item_id is not None and not _is_ulid(source_report_item_id):
        raise _validation_error(
            OperationId.SAVE_CREATE, "source_report_item_id", "pattern_not_matched"
        )
    if analysis_id is not None and not _is_ulid(analysis_id):
        raise _validation_error(OperationId.SAVE_CREATE, "analysis_id", "pattern_not_matched")

    _assert_writable(guard, OperationId.SAVE_CREATE)

    saved_at = now or utc_now_ms()
    try:
        with _transaction(engine) as connection:
            repository = SavedRepository(connection)
            content, analysis_id_at_save = _build_snapshot_content(
                repository,
                owner_id=owner_id,
                target=target,
                analysis_id=analysis_id,
                matched_tags=matched_tags,
            )
            payload_json = snapshot_module.canonical_json(content)
            content_hash = snapshot_module.compute_content_hash(content)
            snapshot_id = new_ulid()
            item_id = new_ulid()
            repository.insert_snapshot(
                snapshot_id=snapshot_id,
                owner_id=owner_id,
                target_kind=target.kind,
                target_key_at_save=target.key,
                analysis_id_at_save=analysis_id_at_save,
                payload_json=payload_json,
                content_hash=content_hash,
                created_at=saved_at,
            )
            repository.insert_item(
                item_id=item_id,
                owner_id=owner_id,
                target=target,
                saved_at=saved_at,
                save_channel=save_channel,
                saved_snapshot_id=snapshot_id,
                source_report_item_id=source_report_item_id,
                idempotency_key=idempotency_key,
            )
    except IntegrityError as collision:
        index = _violated_index(collision)
        if index is None:
            raise
        # The whole transaction has rolled back, snapshot row included: no orphan snapshot
        # is left behind (fixture `identity/d`, forbidden_effects[1]). Read the row that did
        # commit and answer with it. No insert is retried.
        return _already_saved(
            engine,
            owner_id=owner_id,
            target=target,
            idempotency_key=idempotency_key if index == IX_IDEMPOTENCY else None,
        )

    return SaveResult(
        saved_item_id=item_id,
        status="created",
        saved_at=saved_at,
        saved_snapshot_id=snapshot_id,
        content_hash=content_hash,
    )


def _valid_idempotency_key(value: str) -> bool:
    """``^[A-Za-z0-9_.:-]{8,128}$`` — ``saved-snapshot.schema.json`` ``saved_item``."""
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.:-")
    return 8 <= len(value) <= 128 and set(value) <= allowed


def _already_saved(
    engine: Engine, *, owner_id: str, target: TargetRef, idempotency_key: str | None
) -> SaveResult:
    """Read the committed row after losing the unique race, and answer with it.

    ``CONFLICT`` is the code ``contracts/errors.yaml`` registers for this collision class, and
    the resolution ``entities.yaml`` mandates for it is *read and return*, not *raise*: the
    caller is told ``already_saved`` with the id of the row that exists. It becomes a real
    ``CONFLICT`` only if the row cannot be found at all, which would mean the constraint that
    just fired has no row behind it.
    """
    with engine.connect() as connection:
        repository = SavedRepository(connection)
        row = None
        if idempotency_key is not None:
            row = repository.item_by_idempotency_key(owner_id, idempotency_key)
        if row is None:
            row = repository.active_item(owner_id, target.key)
        if row is None:
            raise SavedError(
                ErrorCode.CONFLICT,
                details_safe={"resource_kind": "saved_item"},
            )
        snapshot_row = repository.snapshot(owner_id, str(row["saved_snapshot_id"]))
    return SaveResult(
        saved_item_id=str(row["id"]),
        status="already_saved",
        saved_at=str(row["saved_at"]),
        saved_snapshot_id=str(row["saved_snapshot_id"]),
        content_hash=str(snapshot_row["content_hash"]) if snapshot_row else "",
    )


def _build_snapshot_content(
    repository: SavedRepository,
    *,
    owner_id: str,
    target: TargetRef,
    analysis_id: str | None,
    matched_tags: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], str | None]:
    """Assemble the ``snapshot_content`` for this target, or refuse.

    Refusals are ``VALIDATION_ERROR`` / ``NOT_FOUND`` **before** any row is written, and the
    transaction that wraps this call therefore commits nothing. The one refusal worth naming:
    a target with no ``valid`` summary analysis cannot produce a schema-valid ``summary``
    block, and B16 forbids inventing the three lines. Rather than write an immutable snapshot
    containing text no source produced, the save is refused — see ``CR-TC-SAVED-04``, which
    asks the Owner for the "missing" label wording that would let this case save instead.
    """
    work_row: dict[str, Any] | None = None
    post_rows: list[dict[str, Any]] = []
    title: str | None = None
    version_label: str | None = None

    if target.kind == "work":
        work_row = repository.work_row(owner_id, target.identifier)
        if work_row is None:
            raise _not_found(OperationId.SAVE_CREATE, "work")
        post_rows = repository.posts_of_work(owner_id, target.identifier)
        version_label = repository.work_version_label(owner_id, target.identifier)
        title = snapshot_module.display_title(
            work_title=work_row.get("title"),
            post_text=str(post_rows[0]["text"]) if post_rows else None,
        )
    else:
        post_row = repository.post_row(owner_id, target.identifier)
        if post_row is None:
            raise _not_found(OperationId.SAVE_CREATE, "post")
        post_rows = [post_row]
        title = snapshot_module.display_title(
            work_title=None, post_text=str(post_row.get("text") or "")
        )
    if title is None:
        raise _validation_error(
            OperationId.SAVE_CREATE, "snapshot.content.display_title", "missing_required"
        )

    analysis = _analysis_at_save(
        repository, owner_id=owner_id, target=target, analysis_id=analysis_id
    )
    if analysis is None:
        raise _validation_error(
            OperationId.SAVE_CREATE, "snapshot.content.summary", "missing_required"
        )
    payload = json.loads(str(analysis["payload"]))
    summary = snapshot_module.summary_block(payload)
    if summary is None:
        raise _validation_error(
            OperationId.SAVE_CREATE, "snapshot.content.summary", "missing_required"
        )

    analysis_ref: dict[str, Any] = {
        "analysis_id": str(analysis["id"]),
        "analyzed_at": str(analysis["analyzed_at"]),
    }
    for column, key in (
        ("generation_number", "generation_number"),
        ("payload_hash", "payload_hash"),
        ("provider_name", "provider_name"),
        ("model_name", "model_name"),
    ):
        value = analysis.get(column)
        if value is not None:
            analysis_ref[key] = value

    content = snapshot_module.build_content(
        target_kind=target.kind,
        target_id=target.identifier,
        title=title,
        summary=summary,
        evidence_level=str(analysis["evidence_level"]),
        matched_tags=matched_tags,
        topic_labels=repository.topic_labels(owner_id, target.key),
        work_row=work_row,
        work_version_label=version_label,
        source_posts=[snapshot_module.source_post(row) for row in post_rows],
        analysis_ref=analysis_ref,
    )
    return content, str(analysis["id"])


def _analysis_at_save(
    repository: SavedRepository,
    *,
    owner_id: str,
    target: TargetRef,
    analysis_id: str | None,
) -> dict[str, Any] | None:
    """The revision to snapshot: the one named by the caller, else the newest valid one."""
    if analysis_id is None:
        return repository.latest_valid_summary(owner_id, target.key)
    analysis = repository.analysis_row(owner_id, analysis_id)
    if analysis is None:
        raise _not_found(OperationId.SAVE_CREATE, "analysis")
    if str(analysis["target_key"]) != target.key:
        raise _validation_error(OperationId.SAVE_CREATE, "analysis_id", "does_not_belong_to_target")
    if str(analysis["status"]) != "valid":
        raise _validation_error(OperationId.SAVE_CREATE, "analysis_id", "not_valid_revision")
    return analysis


# --------------------------------------------------------------------------------------
# save.remove
# --------------------------------------------------------------------------------------


def remove_save(
    engine: Engine,
    *,
    owner_id: str,
    target: TargetRef,
    caller_module: str = "MOD-web-ui",
    guard: Any = None,
    now: str | None = None,
) -> RemoveResult:
    """``save.remove`` — un-save. The snapshot is not touched, ever.

    This is the first of the three operations of SRC-SPEC §7.3 and the smallest: one UPDATE
    of ``state`` and ``unsaved_at`` on the active row. It does not delete the ``post``/``work``
    (that is ``data.delete_target``, a different module) and it does not delete the snapshot
    (nothing does). Repeating it on an already-unsaved target is idempotent and writes
    nothing.
    """
    _require_edge(OperationId.SAVE_REMOVE, caller_module)
    _assert_writable(guard, OperationId.SAVE_REMOVE)
    unsaved_at = now or utc_now_ms()
    with _transaction(engine) as connection:
        repository = SavedRepository(connection)
        active = repository.active_item(owner_id, target.key)
        if active is None:
            previous = repository.any_item(owner_id, target.key)
            if previous is None:
                raise _not_found(OperationId.SAVE_REMOVE, "saved_item")
            return RemoveResult(
                saved_item_id=str(previous["id"]),
                state=str(previous["state"]),
                unsaved_at=previous["unsaved_at"],
                removed=False,
                saved_snapshot_id=str(previous["saved_snapshot_id"]),
            )
        repository.mark_unsaved(item_id=str(active["id"]), owner_id=owner_id, unsaved_at=unsaved_at)
        return RemoveResult(
            saved_item_id=str(active["id"]),
            state=STATE_UNSAVED,
            unsaved_at=unsaved_at,
            removed=True,
            saved_snapshot_id=str(active["saved_snapshot_id"]),
        )


# --------------------------------------------------------------------------------------
# save.list
# --------------------------------------------------------------------------------------


def list_saved(
    engine: Engine,
    *,
    owner_id: str,
    limit: int = 50,
    offset: int = 0,
    query: str | None = None,
    caller_module: str = "MOD-web-ui",
) -> list[dict[str, Any]]:
    """``save.list`` — the Saved screen. Read-only; ``mutation: false`` taken literally.

    Each element is one ``saved-snapshot.schema.json`` object (``schema_version``,
    ``saved_item``, ``snapshot``), assembled from the stored rows. The snapshot content comes
    out of ``saved_snapshot.payload`` verbatim, which is why an item whose source post was
    deleted on X still reads.
    """
    _require_edge(OperationId.SAVE_LIST, caller_module)
    if limit < 1 or limit > 200:
        raise _validation_error(OperationId.SAVE_LIST, "limit", "out_of_range")
    if offset < 0:
        raise _validation_error(OperationId.SAVE_LIST, "offset", "out_of_range")
    with engine.connect() as connection:
        pairs = SavedRepository(connection).list_items(
            owner_id, limit=limit, offset=offset, query=query
        )
    return [to_wire(item, snapshot_row) for item, snapshot_row in pairs]


def to_wire(item: Mapping[str, Any], snapshot_row: Mapping[str, Any]) -> dict[str, Any]:
    """One stored ``(saved_item, saved_snapshot)`` pair as the wire object of the schema.

    Column names are kept as field names on purpose (``saved-snapshot.schema.json``
    §x-contract.entities_alignment): an implicit mapping layer between table and wire is
    where two spellings of one fact start to drift apart. The two exceptions are declared
    there too — the wire carries ``target`` as a tagged union next to ``target_key``, and the
    stored ``payload`` appears as ``content``.
    """
    identifier = item["target_work_id"] or item["target_post_id"]
    wire_item: dict[str, Any] = {
        "id": item["id"],
        "owner_id": item["owner_id"],
        "target": snapshot_module.target_object(str(item["target_kind"]), str(identifier)),
        "target_key": item["target_key"],
        "state": item["state"],
        "saved_at": item["saved_at"],
        "unsaved_at": item["unsaved_at"],
        "save_channel": item["save_channel"],
        "saved_snapshot_id": item["saved_snapshot_id"],
        "source_report_item_id": item["source_report_item_id"],
        "idempotency_key": item["idempotency_key"],
        "moved_by_merge_id": item["moved_by_merge_id"],
    }
    wire_snapshot: dict[str, Any] = {
        "id": snapshot_row["id"],
        "owner_id": snapshot_row["owner_id"],
        "target_kind": snapshot_row["target_kind"],
        "target_key_at_save": snapshot_row["target_key_at_save"],
        "analysis_id_at_save": snapshot_row["analysis_id_at_save"],
        "created_at": snapshot_row["created_at"],
        "content": json.loads(str(snapshot_row["payload"])),
        "content_hash": snapshot_row["content_hash"],
    }
    return {
        "schema_version": snapshot_module.SCHEMA_VERSION,
        "saved_item": wire_item,
        "snapshot": wire_snapshot,
    }


def read_saved(
    engine: Engine, *, owner_id: str, target: TargetRef, caller_module: str = "MOD-web-ui"
) -> dict[str, Any] | None:
    """The wire object for one target's most recent Saved row, or ``None``.

    Used by the tests as the "can the owner still read it?" oracle after the source is gone.
    """
    _require_edge(OperationId.SAVE_LIST, caller_module)
    with engine.connect() as connection:
        repository = SavedRepository(connection)
        item = repository.any_item(owner_id, target.key)
        if item is None:
            return None
        snapshot_row = repository.snapshot(owner_id, str(item["saved_snapshot_id"]))
        if snapshot_row is None:
            return None
    return to_wire(item, snapshot_row)


# --------------------------------------------------------------------------------------
# The seam TC-telegram-linking-auth calls
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class TelegramSaveResult:
    """Shape of ``server.app.telegram.commands.SaveResult``, restated to avoid an import.

    ``MOD-telegram-adapter`` -> ``MOD-saved-service`` is a registered edge, but it is an
    **HTTP** edge (``allowed_edges``, transport ``http``). Importing that module's dataclass
    here would put a Python dependency where the registry puts a network hop, and the two
    packages would stop being separately deployable. Duck typing keeps the shape and drops
    the coupling; ``tests/integration/test_concurrent_save.py`` asserts the two agree.
    """

    saved_item_id: str
    already_saved: bool


class TelegramSaveAdapter:
    """``CMD-save`` (plain text) -> ``save.create`` with ``save_channel = 'telegram'``.

    Wired into ``CommandPorts.save_create`` by the deployment. It exists so the chat command
    goes through the *same* :func:`create_save` as the browser — one transaction, one unique
    index, one snapshot rule — instead of a second save path that would drift from it.

    ``report_item_id`` is the parameter name of the adapter's port. Until the reporting card
    exists there is no ``report_item`` table to resolve, so the argument is read as a target
    reference (``work:<ulid>`` / ``post:<ulid>``), which is what ``save.create`` keys on
    anyway (``x-idempotency.key_scope: owner_id + target_ref``). Raised as
    ``CR-TC-SAVED-07``; when ``report_item`` lands, this is the one place that changes.
    """

    def __init__(self, engine: Engine, *, guard: Any = None) -> None:
        self._engine = engine
        self._guard = guard

    def create_save(
        self, *, owner_id: str, report_item_id: str, idempotency_key: str
    ) -> TelegramSaveResult:
        result = create_save(
            self._engine,
            owner_id=owner_id,
            target=TargetRef.parse(report_item_id),
            save_channel="telegram",
            idempotency_key=idempotency_key,
            caller_module="MOD-telegram-adapter",
            guard=self._guard,
        )
        return TelegramSaveResult(
            saved_item_id=result.saved_item_id, already_saved=result.already_saved
        )


__all__ = [
    "IX_ACTIVE",
    "IX_IDEMPOTENCY",
    "OWNER_MODULE",
    "SAVE_CHANNELS",
    "RemoveResult",
    "SaveResult",
    "SavedError",
    "SavedRepository",
    "TargetRef",
    "TelegramLinkResolver",
    "TelegramSaveAdapter",
    "TelegramSaveResult",
    "create_save",
    "list_saved",
    "new_ulid",
    "read_saved",
    "remove_save",
    "to_wire",
    "utc_now_ms",
]
