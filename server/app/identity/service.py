"""``MOD-identity-service`` -- resolve, alias, quarantine, merge (contracts/ports.yaml).

Each public function is named after the operation id it implements, so ``identity.merge_works``
in the contract is :func:`merge_works` here and nothing has to be looked up in a mapping table:

===============================  ==========================
``contracts/ports.yaml``         this module
===============================  ==========================
``identity.resolve_target``      :func:`resolve_target`
``identity.record_alias``        :func:`record_alias`
``identity.quarantine_conflict`` :func:`quarantine_conflict`
``identity.merge_works``         :func:`merge_works`
``identity.resolve_conflict``    :func:`resolve_conflict`
``work.get_detail``              :func:`get_detail`
===============================  ==========================

Signatures, so a caller can be written against this module without reading it. Every function
takes the executor first (an :class:`~sqlalchemy.Engine`, or a :class:`~sqlalchemy.Connection`
to join the caller's transaction) and everything else by keyword; the argument shapes come from
``contracts/schemas/target.schema.json`` and ``contracts/data/entities.yaml``::

    resolve_target(exec, *, owner_id, identifiers=(), post_id=None,
                   caller_module="MOD-ingest-service") -> TargetResolution
    record_alias(exec, *, owner_id, identifier, work_id=None,
                 caller_module="MOD-ingest-service", now=None, alias_id=None,
                 new_work_id=None) -> AliasResult
    quarantine_conflict(exec, *, owner_id, conflict_type, involved_work_ids,
                        involved_identifiers, detected_in_run_id=None,
                        caller_module="MOD-ingest-service", now=None,
                        conflict_id=None) -> ConflictRow
    merge_works(exec, *, owner_id, work_ids, linking_evidence,
                performed_by="system_automatic_on_evidence", owner_choice_work_id=None,
                caller_module="MOD-ingest-service", now=None, merge_id=None) -> MergeResult
    resolve_conflict(exec, *, owner_id, conflict_id, decision, resolution_note=None,
                     linking_evidence=None, winner_work_id=None,
                     caller_module="MOD-web-ui", now=None, merge_id=None) -> ConflictResolution
    get_detail(exec, *, owner_id, work_id, caller_module="MOD-web-ui") -> WorkDetail

An ``identifiers`` element is an :class:`Identifier` (scheme + raw string + provenance); a
``TargetResolution.target`` validates against ``target.schema.json``. ``work_ids`` is the pair
of candidates, NOT winner-then-loser: which one survives follows identity.md §6.2 and is
returned in ``MergeResult.winner_selection_rule``, so a caller cannot decide it by argument
order. ``owner_choice_work_id`` is the single, audited exception.

The one rule that shapes everything below: **evidence, never inference**. Two works are merged
only when one normalised identifier is present on both sides, or an authoritative non-AI source
states the mapping (identity.md §6.1). Everything else is quarantined, with both sources kept
(B15). There is no code path in this file that decides identity from a title, an author or a
model's output, and ``identity_merge_audit.performed_by`` has no value that could record one.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Final

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine

from server.app.identity.normalization import (
    CANONICAL_SCHEMES,
    ArxivId,
    IdScheme,
    normalize,
    normalize_arxiv,
    target_key,
)
from server.app.identity.repository import (
    AliasRow,
    ConflictRow,
    IdentityRepository,
    WorkRow,
    new_ulid,
    utc_now_ms,
)

#: ``contracts/data/entities.yaml`` → ``limits.identity_merge_max_moved_rows`` (100000 rows,
#: PROVISIONAL, CR-PC02-05). Exceeding it is a stop condition (card §10 SG-02), never a reason
#: to raise the number in code.
IDENTITY_MERGE_MAX_MOVED_ROWS: Final[int] = 100_000

#: ``contracts/modules.yaml`` → ``allowed_edges``. Default deny: a caller that is not listed
#: for an operation gets ``FORBIDDEN_EDGE``, which is a different failure from ``UNAUTHORIZED``
#: (card §5, ruling R5-01). A test asserts this table against the contract.
ALLOWED_CALLERS: Final[dict[OperationId, frozenset[str]]] = {
    OperationId.IDENTITY_RESOLVE_TARGET: frozenset(
        {"MOD-ingest-service", "MOD-report-service", "MOD-identity-service"}
    ),
    OperationId.IDENTITY_RECORD_ALIAS: frozenset({"MOD-ingest-service", "MOD-identity-service"}),
    OperationId.IDENTITY_QUARANTINE_CONFLICT: frozenset(
        {"MOD-ingest-service", "MOD-identity-service"}
    ),
    OperationId.IDENTITY_MERGE_WORKS: frozenset({"MOD-ingest-service", "MOD-identity-service"}),
    OperationId.IDENTITY_RESOLVE_CONFLICT: frozenset({"MOD-web-ui"}),
    OperationId.WORK_GET_DETAIL: frozenset({"MOD-web-ui"}),
}

OWNER_MODULE: Final[str] = "MOD-identity-service"

#: ``identity_alias.evidence_source`` (entities.yaml). There is deliberately no AI value: a
#: model's output is not evidence of identity (B15, SRC-SPEC §11.4).
EVIDENCE_SOURCES: Final[frozenset[str]] = frozenset(
    {"post_link", "arxiv_api", "openalex_api", "manual_owner"}
)
CONFIDENCE_LEVELS: Final[frozenset[str]] = frozenset(
    {"asserted_by_source", "confirmed_by_two_sources", "owner_confirmed"}
)
PERFORMED_BY: Final[frozenset[str]] = frozenset({"system_automatic_on_evidence", "owner_manual"})

#: ``work.metadata_state``, ordered from least to most informative. The merge gives the winner
#: the more informative of the two (entities.yaml merge_move_set, `work` row).
_METADATA_STATE_ORDER: Final[tuple[str, ...]] = ("none", "partial", "unavailable", "complete")

_HTTP_STATUS: Final[dict[ErrorCode, int]] = {
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.CONFLICT: 409,
    ErrorCode.IDENTITY_CONFLICT: 409,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.INTERNAL: 500,
}

_MESSAGE_SAFE: Final[dict[ErrorCode, str]] = {
    ErrorCode.VALIDATION_ERROR: "Yêu cầu không hợp lệ.",
    ErrorCode.UNAUTHORIZED: "Bạn cần đăng nhập để thực hiện thao tác này.",
    ErrorCode.CSRF_REJECTED: "Yêu cầu thiếu hoặc sai CSRF token.",
    ErrorCode.FORBIDDEN_EDGE: "Lời gọi này không nằm trong các kết nối được phép.",
    ErrorCode.NOT_FOUND: "Không tìm thấy dữ liệu được yêu cầu.",
    ErrorCode.CONFLICT: "Dữ liệu đã đổi trong lúc xử lý. Hãy đọc lại rồi thử lại.",
    ErrorCode.IDENTITY_CONFLICT: (
        "Hai định danh của cùng một công trình đang mâu thuẫn. Mục được tạm giữ để bạn xem lại."
    ),
    ErrorCode.IDEMPOTENCY_CONFLICT: "Cùng khóa idempotency nhưng nội dung khác.",
    ErrorCode.STORAGE_WRITE_FAILED: "Không ghi được dữ liệu. Chưa có gì được lưu.",
    ErrorCode.INTERNAL: "Lỗi nội bộ.",
}


class IdentityError(Exception):
    """An error from this module, carrying a code that exists in ``contracts/errors.yaml``.

    The code is an :class:`~rr_contracts.generated.errors.ErrorCode` member, never a string
    literal, so a code that the registry does not declare cannot be raised.
    ``details_safe`` is filtered by the caller against the code's ``details_safe_keys``; nothing
    here ever carries post text, a URL from an untrusted path, a token or a stack trace
    (errors.yaml ``error_envelope.forbidden_content_vi``).
    """

    def __init__(
        self,
        code: ErrorCode,
        *,
        details_safe: Mapping[str, Any] | None = None,
        message_safe: str | None = None,
    ) -> None:
        self.code = code
        self.details_safe: dict[str, Any] = dict(details_safe or {})
        self.message_safe = message_safe or _MESSAGE_SAFE.get(
            code, _MESSAGE_SAFE[ErrorCode.INTERNAL]
        )
        super().__init__(f"{code.value}: {self.message_safe}")

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS.get(self.code, 500)

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """The error envelope of ``contracts/errors.yaml`` → ``error_envelope``."""
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
        }


@dataclass(frozen=True)
class Identifier:
    """One observed identifier: the scheme, the raw string, and where it was seen."""

    scheme: IdScheme
    raw: str
    evidence_source: str = "post_link"
    evidence_ref: Mapping[str, Any] = field(default_factory=dict)
    confidence: str = "asserted_by_source"


@dataclass(frozen=True)
class TargetResolution:
    """What ``identity.resolve_target`` answers: a target object plus the aliases behind it."""

    target: dict[str, Any]
    work_id: str | None
    post_id: str | None
    canonical: dict[str, str]
    aliases: list[dict[str, str]]


@dataclass(frozen=True)
class AliasResult:
    """What ``identity.record_alias`` answers."""

    alias_id: str
    work_id: str
    id_scheme: str
    id_value_normalized: str
    created: bool
    created_work: bool


@dataclass(frozen=True)
class MergeResult:
    """What ``identity.merge_works`` answers; the counts are the oracle of I03 and I17."""

    merge_id: str
    winner_work_id: str
    loser_work_id: str
    winner_selection_rule: str
    moved_counts: dict[str, int | None]
    preserved_counts: dict[str, int]
    merged_at: str
    canonical: dict[str, str]
    already_merged: bool = False


@dataclass(frozen=True)
class ConflictResolution:
    """What ``identity.resolve_conflict`` answers."""

    conflict_id: str
    state: str
    merge: MergeResult | None


Executor = Engine | Connection


@contextmanager
def _transaction(target: Executor) -> Iterator[Connection]:
    """One BEGIN…COMMIT for the whole operation.

    Given an :class:`~sqlalchemy.Engine` this opens and commits its own transaction. Given a
    :class:`~sqlalchemy.Connection` it *joins* the caller's transaction, which is how the ingest
    path keeps ``TXN-ingest-batch`` and a merge inside one commit instead of two.
    """
    if isinstance(target, Engine):
        with target.begin() as connection:
            yield connection
    else:
        yield target


@contextmanager
def _reading(target: Executor) -> Iterator[Connection]:
    """A read-only connection, joining the caller's transaction when it is given one."""
    if isinstance(target, Engine):
        with target.connect() as connection:
            yield connection
    else:
        yield target


def _require_edge(operation: OperationId, caller_module: str) -> None:
    """Default deny (contracts/modules.yaml). Wrong caller ⇒ ``FORBIDDEN_EDGE``, not 401."""
    if caller_module not in ALLOWED_CALLERS[operation]:
        raise IdentityError(
            ErrorCode.FORBIDDEN_EDGE,
            details_safe={
                "caller_module": caller_module,
                "callee_module": OWNER_MODULE,
                "forbidden_edge_ref": None,
            },
        )


def _validation_error(
    operation: OperationId, field_path: str, violation_kind: str
) -> IdentityError:
    return IdentityError(
        ErrorCode.VALIDATION_ERROR,
        details_safe={
            "operation_id": operation.value,
            "field_path": field_path,
            "violation_kind": violation_kind,
        },
    )


def _normalized_pairs(
    operation: OperationId, identifiers: Sequence[Identifier]
) -> list[tuple[Identifier, str, str | None]]:
    """Normalise each identifier and DROP the rejects (identity.md §3 step 1).

    A rejected identifier is not an error: the item simply carries one identifier fewer and may
    end up on the post-only branch. Nothing is repaired to make it parse.
    """
    pairs: list[tuple[Identifier, str, str | None]] = []
    for identifier in identifiers:
        if identifier.evidence_source not in EVIDENCE_SOURCES:
            raise _validation_error(operation, "evidence_source", "enum_not_allowed")
        if identifier.confidence not in CONFIDENCE_LEVELS:
            raise _validation_error(operation, "confidence", "enum_not_allowed")
        version: str | None = None
        if identifier.scheme is IdScheme.ARXIV:
            parsed = normalize_arxiv(identifier.raw)
            if not isinstance(parsed, ArxivId):
                continue
            value, version = parsed.base, parsed.version
        else:
            normalized = normalize(identifier.scheme, identifier.raw)
            if not isinstance(normalized, str):
                continue
            value = normalized
        pairs.append((identifier, value, version))
    return pairs


def _work_target(work: WorkRow) -> dict[str, Any]:
    """A ``work`` branch object of ``contracts/schemas/target.schema.json``."""
    canonical: dict[str, str] = {}
    if work.canonical_doi is not None:
        canonical["doi"] = work.canonical_doi
    if work.canonical_arxiv_id is not None:
        canonical["arxiv_base"] = work.canonical_arxiv_id
    target: dict[str, Any] = {
        "kind": "work",
        "work_id": work.id,
        "target_key": target_key("work", work.id),
        "identity_state": work.identity_state,
    }
    if canonical:
        target["canonical"] = canonical
    return target


def _post_target(post: Mapping[str, Any]) -> dict[str, Any]:
    """A ``post`` branch object -- the "chỉ có post" target of REQ-D33."""
    return {
        "kind": "post",
        "post_id": str(post["id"]),
        "target_key": target_key("post", str(post["id"])),
        "x_post_id": str(post["x_post_id"]),
        "identity_resolution": str(post["identity_resolution"]),
    }


# ---------------------------------------------------------------------------------------------
# identity.resolve_target
# ---------------------------------------------------------------------------------------------


def resolve_target(
    target: Executor,
    *,
    owner_id: str,
    identifiers: Sequence[Identifier] = (),
    post_id: str | None = None,
    caller_module: str = "MOD-ingest-service",
) -> TargetResolution:
    """``identity.resolve_target`` -- read-only lookup (identity.md §3).

    Three outcomes, and the third is the point of the whole design:

    * exactly one work behind the identifiers -> that work;
    * no work, but a post that resolved post-only -> the ``post`` branch of the union;
    * **two or more works** -> ``IDENTITY_CONFLICT``. This function never picks "the first work
      found"; joining them needs evidence and a transaction, not a query plan.

    ``mutation: false`` in ports.yaml is honoured literally: nothing here writes, not even a
    quarantine row -- the caller decides, through :func:`quarantine_conflict`.
    """
    _require_edge(OperationId.IDENTITY_RESOLVE_TARGET, caller_module)
    with _reading(target) as connection:
        repository = IdentityRepository(connection)
        pairs = _normalized_pairs(OperationId.IDENTITY_RESOLVE_TARGET, identifiers)
        aliases: list[AliasRow] = []
        works: dict[str, WorkRow] = {}
        for _identifier, value, _version in pairs:
            alias = repository.find_alias(owner_id, _identifier.scheme.value, value)
            if alias is None:
                continue
            aliases.append(alias)
            resolved = repository.resolve_work(owner_id, alias.work_id)
            if resolved is not None:
                works[resolved.id] = resolved

        if len(works) > 1:
            raise IdentityError(
                ErrorCode.IDENTITY_CONFLICT,
                details_safe={
                    "conflict_type": "alias_points_to_two_works",
                    "target_key_a": target_key("work", sorted(works)[0]),
                    "target_key_b": target_key("work", sorted(works)[1]),
                },
            )

        if len(works) == 1:
            work = next(iter(works.values()))
            canonical = {
                key: value
                for key, value in (
                    ("doi", work.canonical_doi),
                    ("arxiv", work.canonical_arxiv_id),
                )
                if value is not None
            }
            return TargetResolution(
                target=_work_target(work),
                work_id=work.id,
                post_id=None,
                canonical=canonical,
                aliases=[
                    {"id_scheme": alias.id_scheme, "id_value_normalized": alias.id_value_normalized}
                    for alias in repository.aliases_of_work(owner_id, work.id)
                ],
            )

        if post_id is None:
            raise IdentityError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.IDENTITY_RESOLVE_TARGET.value,
                    "resource_kind": "work",
                },
            )

        row = (
            connection.exec_driver_sql(
                "SELECT id, x_post_id, identity_resolution FROM post "
                " WHERE owner_id = ? AND id = ?",
                (owner_id, post_id),
            )
            .mappings()
            .first()
        )
        if row is None:
            raise IdentityError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.IDENTITY_RESOLVE_TARGET.value,
                    "resource_kind": "post",
                },
            )
        return TargetResolution(
            target=_post_target(dict(row)),
            work_id=None,
            post_id=str(row["id"]),
            canonical={},
            aliases=[],
        )


# ---------------------------------------------------------------------------------------------
# identity.record_alias
# ---------------------------------------------------------------------------------------------


def record_alias(
    target: Executor,
    *,
    owner_id: str,
    identifier: Identifier,
    work_id: str | None = None,
    caller_module: str = "MOD-ingest-service",
    now: str | None = None,
    alias_id: str | None = None,
    new_work_id: str | None = None,
) -> AliasResult:
    """``identity.record_alias`` -- record one identifier against one work (identity.md §3, §7).

    Idempotent by the alias pair itself (ports.yaml key ``alias_pair_hash``): recording the same
    ``(scheme, normalised value)`` twice returns the existing row. Recording it against a
    *different* work is ``IDENTITY_CONFLICT``, never a silent repoint -- that is the case B15
    exists for.

    ``work_id=None`` is identity.md §3 step 3 case ``|W| = 0``: no work is known for this
    identifier yet, so one is created and the identifier becomes its first alias. Only a
    canonical scheme (``doi``, ``arxiv``) may create a work; an OpenAlex id or a landing URL is
    a bridge, not a definition (identity.md §2.3).
    """
    _require_edge(OperationId.IDENTITY_RECORD_ALIAS, caller_module)
    moment = now or utc_now_ms()
    with _transaction(target) as connection:
        repository = IdentityRepository(connection)
        pairs = _normalized_pairs(OperationId.IDENTITY_RECORD_ALIAS, [identifier])
        if not pairs:
            raise _validation_error(
                OperationId.IDENTITY_RECORD_ALIAS, "id_value_raw", "not_an_identifier"
            )
        _, value, _version = pairs[0]

        existing = repository.find_alias(owner_id, identifier.scheme.value, value)
        if existing is not None:
            resolved = repository.resolve_work(owner_id, existing.work_id)
            resolved_id = resolved.id if resolved is not None else existing.work_id
            if work_id is not None:
                requested = repository.resolve_work(owner_id, work_id)
                requested_id = requested.id if requested is not None else work_id
                if requested_id != resolved_id:
                    raise IdentityError(
                        ErrorCode.IDENTITY_CONFLICT,
                        details_safe={
                            "conflict_type": "alias_points_to_two_works",
                            "target_key_a": target_key("work", resolved_id),
                            "target_key_b": target_key("work", requested_id),
                        },
                    )
            return AliasResult(
                alias_id=existing.id,
                work_id=resolved_id,
                id_scheme=existing.id_scheme,
                id_value_normalized=existing.id_value_normalized,
                created=False,
                created_work=False,
            )

        created_work = False
        if work_id is None:
            if identifier.scheme not in CANONICAL_SCHEMES:
                raise _validation_error(
                    OperationId.IDENTITY_RECORD_ALIAS,
                    "id_scheme",
                    "alias_scheme_cannot_create_work",
                )
            work_id = new_work_id or new_ulid()
            repository.insert_work(
                {
                    "id": work_id,
                    "owner_id": owner_id,
                    "canonical_doi": value if identifier.scheme is IdScheme.DOI else None,
                    "canonical_arxiv_id": value if identifier.scheme is IdScheme.ARXIV else None,
                    "title": None,
                    "paper_url": None,
                    "code_url": None,
                    "current_work_version_id": None,
                    "metadata_state": "none",
                    "identity_state": "active",
                    "merged_into_work_id": None,
                    "first_discovered_at": moment,
                    "ingest_sequence": repository.next_work_ingest_sequence(owner_id),
                    "content_state": "present",
                    "created_at": moment,
                }
            )
            created_work = True
        else:
            resolved = repository.resolve_work(owner_id, work_id)
            if resolved is None:
                raise IdentityError(
                    ErrorCode.NOT_FOUND,
                    details_safe={
                        "operation_id": OperationId.IDENTITY_RECORD_ALIAS.value,
                        "resource_kind": "work",
                    },
                )
            # An alias must never point at a `merged` row (I03d), so it follows the pointer.
            work_id = resolved.id

        row_id = alias_id or new_ulid()
        repository.insert_alias(
            {
                "id": row_id,
                "owner_id": owner_id,
                "id_scheme": identifier.scheme.value,
                "id_value_normalized": value,
                "id_value_raw": identifier.raw,
                "work_id": work_id,
                "evidence_source": identifier.evidence_source,
                "evidence_ref": dict(identifier.evidence_ref),
                "confidence": identifier.confidence,
                "created_at": moment,
                "superseded_by_merge_id": None,
            }
        )
        return AliasResult(
            alias_id=row_id,
            work_id=work_id,
            id_scheme=identifier.scheme.value,
            id_value_normalized=value,
            created=True,
            created_work=created_work,
        )


# ---------------------------------------------------------------------------------------------
# identity.quarantine_conflict
# ---------------------------------------------------------------------------------------------


def conflict_fingerprint(
    conflict_type: str,
    involved_work_ids: Sequence[str],
    involved_identifiers: Sequence[Mapping[str, Any]],
) -> str:
    """The idempotency key of ``identity.quarantine_conflict``.

    ports.yaml names it ``conflict_fingerprint``.

    ``identity_conflict`` has no column for it (entities.yaml), so it is *computed* from the
    stored content instead of stored: same type, same works, same identifiers ⇒ same conflict.
    """
    payload = json.dumps(
        {
            "conflict_type": conflict_type,
            "involved_work_ids": sorted(involved_work_ids),
            "involved_identifiers": sorted(
                json.dumps(identifier, sort_keys=True) for identifier in involved_identifiers
            ),
        },
        sort_keys=True,
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def quarantine_conflict(
    target: Executor,
    *,
    owner_id: str,
    conflict_type: str,
    involved_work_ids: Sequence[str],
    involved_identifiers: Sequence[Mapping[str, Any]],
    detected_in_run_id: str | None = None,
    caller_module: str = "MOD-ingest-service",
    now: str | None = None,
    conflict_id: str | None = None,
) -> ConflictRow:
    """``identity.quarantine_conflict`` -- hold the item, keep every source (identity.md §5).

    Quarantine blocks *identity inference*, not data: the works stay readable, Saved stays,
    existing analysis stays valid. What stops is any automatic joining of the two, and the only
    way out is an owner decision through :func:`resolve_conflict`. There is no timeout that
    turns a conflict into a merge.
    """
    _require_edge(OperationId.IDENTITY_QUARANTINE_CONFLICT, caller_module)
    if conflict_type not in {
        "cross_scheme_disagreement",
        "alias_points_to_two_works",
        "canonical_value_mismatch",
        "merge_cycle_detected",
    }:
        raise _validation_error(
            OperationId.IDENTITY_QUARANTINE_CONFLICT, "conflict_type", "enum_not_allowed"
        )
    if not involved_work_ids:
        raise _validation_error(
            OperationId.IDENTITY_QUARANTINE_CONFLICT, "involved_work_ids", "empty"
        )
    moment = now or utc_now_ms()
    fingerprint = conflict_fingerprint(conflict_type, involved_work_ids, involved_identifiers)
    with _transaction(target) as connection:
        repository = IdentityRepository(connection)
        for candidate in repository.open_conflicts(owner_id):
            if (
                conflict_fingerprint(
                    candidate.conflict_type,
                    candidate.involved_work_ids,
                    candidate.involved_identifiers,
                )
                == fingerprint
            ):
                return candidate
        row_id = conflict_id or new_ulid()
        repository.insert_conflict(
            {
                "id": row_id,
                "owner_id": owner_id,
                "conflict_type": conflict_type,
                "involved_work_ids": list(involved_work_ids),
                "involved_identifiers": [dict(item) for item in involved_identifiers],
                "detected_at": moment,
                "detected_in_run_id": detected_in_run_id,
                "state": "open",
                "resolution_note": None,
                "resolved_at": None,
                "resolution_merge_id": None,
            }
        )
        repository.set_identity_state(owner_id, list(involved_work_ids), "quarantined")
        conflict = repository.get_conflict(owner_id, row_id)
        assert conflict is not None  # noqa: S101 - just inserted inside this transaction
        return conflict


# ---------------------------------------------------------------------------------------------
# identity.merge_works — TXN-identity-merge
# ---------------------------------------------------------------------------------------------


def _select_winner(
    first: WorkRow, second: WorkRow, owner_choice_work_id: str | None
) -> tuple[WorkRow, WorkRow, str]:
    """Winner selection, total and deterministic (identity.md §6.2).

    Order: the owner's choice, then the only side with a DOI (a DOI outlives an arXiv id), then
    the earliest discovery, tie-broken by ``ingest_sequence`` and finally by id byte order. A
    rule that depended on query order would make fixture (a) unreproducible.
    """
    if owner_choice_work_id is not None:
        if owner_choice_work_id == first.id:
            return first, second, "owner_choice"
        if owner_choice_work_id == second.id:
            return second, first, "owner_choice"
        raise _validation_error(
            OperationId.IDENTITY_MERGE_WORKS, "owner_choice_work_id", "not_a_candidate"
        )
    has_doi = [work for work in (first, second) if work.canonical_doi is not None]
    if len(has_doi) == 1:
        winner = has_doi[0]
        loser = second if winner is first else first
        return winner, loser, "only_candidate_with_canonical_doi"
    ordered = sorted(
        (first, second), key=lambda w: (w.first_discovered_at, w.ingest_sequence, w.id)
    )
    return ordered[0], ordered[1], "earliest_first_discovered_at"


def _canonical_mismatch(first: WorkRow, second: WorkRow) -> bool:
    """Both sides carry a canonical value and the values differ ⇒ never merge (B15)."""
    doi_clash = (
        first.canonical_doi is not None
        and second.canonical_doi is not None
        and first.canonical_doi != second.canonical_doi
    )
    arxiv_clash = (
        first.canonical_arxiv_id is not None
        and second.canonical_arxiv_id is not None
        and first.canonical_arxiv_id != second.canonical_arxiv_id
    )
    return doi_clash or arxiv_clash


def _validate_linking_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    """``identity_merge_audit.linking_evidence`` is NOT NULL and never comes from a model."""
    required = {"id_scheme", "id_value_normalized", "evidence_source"}
    missing = required - set(evidence)
    if missing:
        raise _validation_error(
            OperationId.IDENTITY_MERGE_WORKS, "linking_evidence", "missing_required_field"
        )
    if str(evidence["evidence_source"]) not in EVIDENCE_SOURCES:
        raise _validation_error(
            OperationId.IDENTITY_MERGE_WORKS, "linking_evidence.evidence_source", "enum_not_allowed"
        )
    return dict(evidence)


def _merge_analysis(
    repository: IdentityRepository, owner_id: str, loser: str, winner: str, merge_id: str
) -> int:
    """Move ``analysis`` rows; on an ``ux_analysis_valid_key`` collision the EARLIER
    ``analyzed_at`` stays ``valid`` and the other becomes ``superseded_by_merge``."""
    columns = (
        "id, target_key, task_type, source_fingerprint, prompt_version, schema_version, "
        "generation_number, status, analyzed_at"
    )
    loser_rows = repository.rows_for_merge_target("analysis", owner_id, loser, columns)
    winner_rows = repository.rows_for_merge_target("analysis", owner_id, winner, columns)
    if not loser_rows:
        return 0

    def key(row: Mapping[str, Any]) -> tuple[Any, ...]:
        return (
            row["task_type"],
            row["source_fingerprint"],
            row["prompt_version"],
            row["schema_version"],
            row["generation_number"],
        )

    winner_valid = {key(row): row for row in winner_rows if row["status"] == "valid"}
    moved = 0
    for row in loser_rows:
        clash = winner_valid.get(key(row))
        if clash is not None and row["status"] == "valid":
            if str(row["analyzed_at"]) < str(clash["analyzed_at"]):
                repository.demote_analysis(str(clash["id"]), merge_id)
            else:
                repository.demote_analysis(str(row["id"]), merge_id)
        repository.move_row_target("analysis", str(row["id"]), winner, merge_id)
        moved += 1
    return moved


def _merge_saved_items(
    repository: IdentityRepository, owner_id: str, loser: str, winner: str, merge_id: str
) -> int:
    """Move ``saved_item`` pointers; on a collision the EARLIER ``saved_at`` stays ``active``.

    The losing row becomes ``superseded_by_merge``; it is not deleted, because a Saved row is a
    record of what the owner did (I08).
    """
    columns = "id, state, saved_at"
    loser_rows = repository.rows_for_merge_target("saved_item", owner_id, loser, columns)
    winner_rows = repository.rows_for_merge_target("saved_item", owner_id, winner, columns)
    if not loser_rows:
        return 0
    active_winner = next((row for row in winner_rows if row["state"] == "active"), None)
    moved = 0
    for row in loser_rows:
        if active_winner is not None and row["state"] == "active":
            if str(row["saved_at"]) < str(active_winner["saved_at"]):
                repository.demote_saved_item(str(active_winner["id"]), merge_id)
                active_winner = row
            else:
                repository.demote_saved_item(str(row["id"]), merge_id)
        repository.move_row_target("saved_item", str(row["id"]), winner, merge_id)
        moved += 1
    return moved


def _merge_work_labels(
    repository: IdentityRepository, owner_id: str, loser: str, winner: str
) -> int:
    """Move ``work_label`` rows that do not collide on ``ux_work_label_owner_target_label_gen``.

    A colliding label is the same text, on the same target, in the same embedding generation --
    the winner already carries it, so the losing row is left in place rather than deleted or
    forced through the index. entities.yaml does not name a collision rule for this table; the
    handoff records the reading as a change request.
    """
    columns = "id, label_text, embedding_generation_id"
    loser_rows = repository.rows_for_merge_target("work_label", owner_id, loser, columns)
    winner_rows = repository.rows_for_merge_target("work_label", owner_id, winner, columns)
    taken = {(row["label_text"], row["embedding_generation_id"]) for row in winner_rows}
    moved = 0
    for row in loser_rows:
        if (row["label_text"], row["embedding_generation_id"]) in taken:
            continue
        repository.move_row_target("work_label", str(row["id"]), winner, None)
        taken.add((row["label_text"], row["embedding_generation_id"]))
        moved += 1
    return moved


def _apply_first_announced(
    repository: IdentityRepository, owner_id: str, loser: str, winner: str, merge_id: str
) -> int:
    """The first-announcement hook, inside the merge transaction.

    ``contracts/reporting/time-and-tags.md`` §8.3 closes ``CR-PC02-06``: **the winner inherits
    the earliest first-announcement among the merged works**, every other row is kept as
    evidence, and a later report may only show the work as a dated reference -- never as a new
    discovery. Returns the count written to ``moved_counts.first_announced``.
    """
    if not repository.table_exists("first_announced_ledger"):
        return 0
    winner_row = repository.effective_first_announced(owner_id, winner)
    loser_row = repository.effective_first_announced(owner_id, loser)
    if loser_row is None:
        # Neither side has a row, or only the winner does: nothing to inherit.
        return 0
    if winner_row is None:
        repository.update_first_announced(
            str(loser_row["id"]),
            {"canonical_work_id": winner, "merge_audit_id": merge_id},
        )
        return 1
    earlier = min(
        (winner_row, loser_row),
        key=lambda row: (str(row["first_announced_at"]), str(row["first_report_id"])),
    )
    repository.update_first_announced(
        str(winner_row["id"]),
        {
            "first_report_id": earlier["first_report_id"],
            "first_announced_at": earlier["first_announced_at"],
            "merge_audit_id": merge_id,
        },
    )
    repository.update_first_announced(str(loser_row["id"]), {"superseded_by_merge_id": merge_id})
    return 2


def merge_works(
    target: Executor,
    *,
    owner_id: str,
    work_ids: tuple[str, str],
    linking_evidence: Mapping[str, Any],
    performed_by: str = "system_automatic_on_evidence",
    owner_choice_work_id: str | None = None,
    caller_module: str = "MOD-ingest-service",
    now: str | None = None,
    merge_id: str | None = None,
) -> MergeResult:
    """``identity.merge_works`` -- ``TXN-identity-merge``.

    **Commit point:** the single COMMIT at the end of the ``with _transaction(...)`` block below.
    The ``identity_merge_audit`` row is written inside it, so a merge without an audit row is not
    a state this database can be in (entities.yaml ``commit_point``).

    Which two works are merged is the caller's input; **which one wins is not** -- that follows
    the deterministic rule of identity.md §6.2, so two runs on the same data give the same
    result. ``owner_choice_work_id`` is the one exception, and it is recorded as such in
    ``winner_selection_rule``.

    Failures, in the order they are checked:

    * malformed or AI-sourced evidence -> ``VALIDATION_ERROR``, nothing written;
    * a work that does not exist -> ``NOT_FOUND``;
    * the same loser already merged: same evidence -> the committed result is returned again
      (idempotent), different evidence -> ``CONFLICT`` and no second merge;
    * conflicting canonical values -> an ``identity_conflict`` row is written, both works are
      quarantined and ``IDENTITY_CONFLICT`` is raised. No guess, no source discarded (B15);
    * more rows to move than ``identity_merge_max_moved_rows`` -> ``CONFLICT``, nothing written
      (card §10 SG-02: raise a change request, do not raise the threshold);
    * a work whose state changed between the read and the write -> ``CONFLICT``: the losing side
      of the CAS re-reads instead of overwriting.
    """
    _require_edge(OperationId.IDENTITY_MERGE_WORKS, caller_module)
    if performed_by not in PERFORMED_BY:
        raise _validation_error(
            OperationId.IDENTITY_MERGE_WORKS, "performed_by", "enum_not_allowed"
        )
    evidence = _validate_linking_evidence(linking_evidence)
    first_id, second_id = work_ids
    if first_id == second_id:
        raise _validation_error(OperationId.IDENTITY_MERGE_WORKS, "work_ids", "same_work")

    moment = now or utc_now_ms()

    # Phase 1 -- read and decide. Nothing is written here; the decision is re-checked under the
    # write transaction below, so a concurrent merge cannot slip between the two.
    with _reading(target) as connection:
        repository = IdentityRepository(connection)
        first = repository.get_work(owner_id, first_id)
        second = repository.get_work(owner_id, second_id)
        if first is None or second is None:
            raise IdentityError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.IDENTITY_MERGE_WORKS.value,
                    "resource_kind": "work",
                },
            )
        replay = _replay_result(repository, owner_id, first, second, evidence)
        if replay is not None:
            return replay
        mismatch = _canonical_mismatch(first, second)
        winner, loser, rule = (
            (first, second, "") if mismatch else _select_winner(first, second, owner_choice_work_id)
        )

    if mismatch:
        conflict = quarantine_conflict(
            target,
            owner_id=owner_id,
            conflict_type="canonical_value_mismatch",
            involved_work_ids=[first.id, second.id],
            involved_identifiers=_conflict_identifiers(first, second, evidence),
            caller_module=OWNER_MODULE,
            now=moment,
        )
        raise IdentityError(
            ErrorCode.IDENTITY_CONFLICT,
            details_safe={
                "conflict_id": conflict.id,
                "conflict_type": conflict.conflict_type,
                "target_key_a": target_key("work", first.id),
                "target_key_b": target_key("work", second.id),
            },
        )

    audit_id = merge_id or new_ulid()
    with _transaction(target) as connection:
        repository = IdentityRepository(connection)
        # CAS: both works must still be exactly what phase 1 read.
        for before in (winner, loser):
            after = repository.get_work(owner_id, before.id)
            if after != before or after.identity_state != "active":
                raise IdentityError(
                    ErrorCode.CONFLICT,
                    details_safe={
                        "resource_kind": "work",
                        "expected_predecessor_id": before.id,
                        "current_predecessor_id": before.id,
                    },
                )

        estimate = sum(
            repository.count(
                table,
                "owner_id = :owner_id AND " + column + " = :work_id",
                {"owner_id": owner_id, "work_id": loser.id},
            )
            for table, column in (
                ("identity_alias", "work_id"),
                ("post_work", "work_id"),
                ("work_version", "work_id"),
                ("work_label", "target_work_id"),
                ("analysis", "target_work_id"),
                ("saved_item", "target_work_id"),
            )
        )
        if estimate > IDENTITY_MERGE_MAX_MOVED_ROWS:
            raise IdentityError(
                ErrorCode.CONFLICT,
                details_safe={
                    "resource_kind": "identity_merge",
                    "attempt_number": 1,
                },
                message_safe=(
                    "Số hàng phải chuyển vượt ngưỡng an toàn của một lần hợp nhất. "
                    "Không có gì được ghi."
                ),
            )

        snapshots_before = repository.saved_snapshot_digest(owner_id)

        moved_counts: dict[str, int | None] = {
            "identity_alias": repository.move_aliases(owner_id, loser.id, winner.id, audit_id),
            "post_work": repository.move_post_work(owner_id, loser.id, winner.id, audit_id),
            "work_version": repository.move_work_versions(owner_id, loser.id, winner.id),
            "work_label": _merge_work_labels(repository, owner_id, loser.id, winner.id),
            "analysis": _merge_analysis(repository, owner_id, loser.id, winner.id, audit_id),
            "saved_item": _merge_saved_items(repository, owner_id, loser.id, winner.id, audit_id),
            # Published report items are never rewritten (I05, I17): the count is structurally 0.
            "report_item_pointer": 0,
            "first_announced": _apply_first_announced(
                repository, owner_id, loser.id, winner.id, audit_id
            ),
        }

        # The identifier that PROVED the two works are one becomes an alias of the winner, if
        # it is not already an alias. Fixture (a) requires it: the evidence that justified the
        # merge has to be queryable afterwards, not only readable inside the audit row. It is
        # NOT counted in `moved_counts.identity_alias`, which counts rows moved off the loser.
        _record_linking_alias(repository, owner_id, winner.id, evidence, moment)

        winner_updates: dict[str, Any] = {}
        if winner.canonical_doi is None and loser.canonical_doi is not None:
            winner_updates["canonical_doi"] = loser.canonical_doi
        if winner.canonical_arxiv_id is None and loser.canonical_arxiv_id is not None:
            winner_updates["canonical_arxiv_id"] = loser.canonical_arxiv_id
        earliest = min(winner.first_discovered_at, loser.first_discovered_at)
        if earliest != winner.first_discovered_at:
            winner_updates["first_discovered_at"] = earliest
        richer = max((winner.metadata_state, loser.metadata_state), key=_METADATA_STATE_ORDER.index)
        if richer != winner.metadata_state:
            winner_updates["metadata_state"] = richer
        if winner.current_work_version_id is None and loser.current_work_version_id is not None:
            winner_updates["current_work_version_id"] = loser.current_work_version_id

        # The loser is marked `merged` BEFORE the winner takes its canonical values: the partial
        # UNIQUE index excludes `merged` rows, so this order is what lets both rows keep the same
        # canonical value -- the loser as evidence, the winner as the live identity.
        repository.mark_work_merged(owner_id, loser.id, winner.id)
        repository.update_winner_columns(owner_id, winner.id, winner_updates)

        preserved_counts = {
            "saved_snapshot": len(snapshots_before),
            "ingest_receipt": repository.count(
                "ingest_receipt", "owner_id = :owner_id", {"owner_id": owner_id}
            ),
            "published_report_item": _published_report_items(repository, owner_id),
        }

        repository.insert_merge_audit(
            {
                "id": audit_id,
                "owner_id": owner_id,
                "winner_work_id": winner.id,
                "loser_work_id": loser.id,
                "winner_selection_rule": rule,
                "linking_evidence": evidence,
                "moved_counts": moved_counts,
                "preserved_counts": preserved_counts,
                "merged_at": moment,
                "performed_by": performed_by,
                "reversal_of_merge_id": None,
            }
        )

        snapshots_after = repository.saved_snapshot_digest(owner_id)
        if snapshots_after != snapshots_before:
            # I17 is checked inside the transaction so a violation rolls back rather than being
            # reported after the fact.
            raise IdentityError(
                ErrorCode.INTERNAL,
                message_safe="Merge đã chạm vào snapshot lịch sử; giao dịch bị hủy.",
            )

        merged_work = repository.get_work(owner_id, winner.id)
        assert merged_work is not None  # noqa: S101 - read back inside the same transaction
        canonical = {
            key: value
            for key, value in (
                ("doi", merged_work.canonical_doi),
                ("arxiv", merged_work.canonical_arxiv_id),
            )
            if value is not None
        }
        return MergeResult(
            merge_id=audit_id,
            winner_work_id=winner.id,
            loser_work_id=loser.id,
            winner_selection_rule=rule,
            moved_counts=moved_counts,
            preserved_counts=preserved_counts,
            merged_at=moment,
            canonical=canonical,
        )


def _record_linking_alias(
    repository: IdentityRepository,
    owner_id: str,
    winner_work_id: str,
    evidence: Mapping[str, Any],
    moment: str,
) -> None:
    """Store the linking identifier as an alias of the winner (identity.md §7).

    ``confidence`` defaults to ``confirmed_by_two_sources``: an identifier that an authoritative
    source states for BOTH canonical ids is, by construction, attested on two sides. It is one
    of three discrete levels -- never a probability, because this system does not guess.
    """
    scheme_value = str(evidence["id_scheme"])
    try:
        scheme = IdScheme(scheme_value)
    except ValueError:
        return
    value = str(evidence["id_value_normalized"])
    if repository.find_alias(owner_id, scheme.value, value) is not None:
        return
    repository.insert_alias(
        {
            "id": str(evidence.get("alias_id") or new_ulid()),
            "owner_id": owner_id,
            "id_scheme": scheme.value,
            "id_value_normalized": value,
            "id_value_raw": str(evidence.get("id_value_raw") or value),
            "work_id": winner_work_id,
            "evidence_source": str(evidence["evidence_source"]),
            "evidence_ref": dict(evidence.get("evidence_ref") or {"retrieved_at": moment}),
            "confidence": str(evidence.get("confidence") or "confirmed_by_two_sources"),
            "created_at": moment,
            "superseded_by_merge_id": None,
        }
    )


def _published_report_items(repository: IdentityRepository, owner_id: str) -> int:
    """Rows of ``report_item`` belonging to a published report -- 0 while the reporting card's
    tables do not exist. The number is reported, never assumed."""
    if not (repository.table_exists("report_item") and repository.table_exists("report")):
        return 0
    return repository.count(
        "report_item",
        "owner_id = :owner_id AND report_id IN (SELECT id FROM report WHERE status = 'published')",
        {"owner_id": owner_id},
    )


def _conflict_identifiers(
    first: WorkRow, second: WorkRow, evidence: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Every identifier involved in a conflict, so no source is lost (B15, identity.md §5.1)."""
    identifiers: list[dict[str, Any]] = []
    for work in (first, second):
        if work.canonical_doi is not None:
            identifiers.append({"id_scheme": "doi", "id_value_normalized": work.canonical_doi})
        if work.canonical_arxiv_id is not None:
            identifiers.append(
                {"id_scheme": "arxiv", "id_value_normalized": work.canonical_arxiv_id}
            )
    identifiers.append(
        {
            "id_scheme": str(evidence["id_scheme"]),
            "id_value_normalized": str(evidence["id_value_normalized"]),
            "evidence_source": str(evidence["evidence_source"]),
        }
    )
    return identifiers


def _replay_result(
    repository: IdentityRepository,
    owner_id: str,
    first: WorkRow,
    second: WorkRow,
    evidence: Mapping[str, Any],
) -> MergeResult | None:
    """Idempotency (ports.yaml key ``loser_work_id + winner_work_id + alias_evidence_hash``).

    Calling again with the same pair and the same evidence returns the committed merge; the same
    pair with *different* evidence is ``CONFLICT`` and merges nothing a second time.
    """
    for candidate in (first, second):
        audit = repository.merge_audit_for_loser(owner_id, candidate.id)
        if audit is None:
            continue
        other = second if candidate is first else first
        if str(audit["winner_work_id"]) != other.id:
            continue
        if audit["linking_evidence"] != dict(evidence):
            raise IdentityError(
                ErrorCode.CONFLICT,
                details_safe={
                    "resource_kind": "identity_merge_audit",
                    "expected_predecessor_id": str(audit["id"]),
                    "current_predecessor_id": str(audit["id"]),
                },
            )
        winner_row = repository.get_work(owner_id, str(audit["winner_work_id"]))
        canonical = (
            {
                key: value
                for key, value in (
                    ("doi", winner_row.canonical_doi),
                    ("arxiv", winner_row.canonical_arxiv_id),
                )
                if value is not None
            }
            if winner_row is not None
            else {}
        )
        return MergeResult(
            merge_id=str(audit["id"]),
            winner_work_id=str(audit["winner_work_id"]),
            loser_work_id=str(audit["loser_work_id"]),
            winner_selection_rule=str(audit["winner_selection_rule"]),
            moved_counts=dict(audit["moved_counts"]),
            preserved_counts=dict(audit["preserved_counts"]),
            merged_at=str(audit["merged_at"]),
            canonical=canonical,
            already_merged=True,
        )
    return None


# ---------------------------------------------------------------------------------------------
# identity.resolve_conflict
# ---------------------------------------------------------------------------------------------


def resolve_conflict(
    target: Executor,
    *,
    owner_id: str,
    conflict_id: str,
    decision: str,
    resolution_note: str | None = None,
    linking_evidence: Mapping[str, Any] | None = None,
    winner_work_id: str | None = None,
    caller_module: str = "MOD-web-ui",
    now: str | None = None,
    merge_id: str | None = None,
) -> ConflictResolution:
    """``identity.resolve_conflict`` -- the owner decides; the system never does.

    ``decision='merge'`` runs :func:`merge_works` with ``performed_by='owner_manual'``; that call
    is the ONLY merge path out of a conflict, so a merge decided by a human still leaves the same
    audit row as an automatic one. ``decision='keep_separate'`` closes the conflict as
    ``resolved_distinct`` and returns both works to ``active`` with their canonical ids intact.

    Idempotency: ``identity_conflict`` has no column for the request id ports.yaml names, so a
    conflict that is already resolved is *not* resolved twice -- repeating the same decision
    returns the stored outcome, a different decision is ``IDEMPOTENCY_CONFLICT``. The handoff
    records the missing column as a change request.
    """
    _require_edge(OperationId.IDENTITY_RESOLVE_CONFLICT, caller_module)
    if decision not in {"merge", "keep_separate"}:
        raise _validation_error(
            OperationId.IDENTITY_RESOLVE_CONFLICT, "decision", "enum_not_allowed"
        )
    moment = now or utc_now_ms()

    with _reading(target) as connection:
        conflict = IdentityRepository(connection).get_conflict(owner_id, conflict_id)
    if conflict is None:
        raise IdentityError(
            ErrorCode.NOT_FOUND,
            details_safe={
                "operation_id": OperationId.IDENTITY_RESOLVE_CONFLICT.value,
                "resource_kind": "identity_conflict",
            },
        )
    if conflict.state != "open":
        expected = "resolved_merged" if decision == "merge" else "resolved_distinct"
        if conflict.state != expected:
            raise IdentityError(
                ErrorCode.IDEMPOTENCY_CONFLICT,
                details_safe={"idempotency_key": conflict_id},
            )
        return ConflictResolution(conflict_id=conflict.id, state=conflict.state, merge=None)

    if decision == "keep_separate":
        with _transaction(target) as connection:
            repository = IdentityRepository(connection)
            repository.set_identity_state(owner_id, conflict.involved_work_ids, "active")
            repository.close_conflict(
                owner_id,
                conflict_id,
                state="resolved_distinct",
                resolved_at=moment,
                resolution_note=resolution_note,
                resolution_merge_id=None,
            )
        return ConflictResolution(conflict_id=conflict.id, state="resolved_distinct", merge=None)

    if len(conflict.involved_work_ids) != 2:
        raise _validation_error(
            OperationId.IDENTITY_RESOLVE_CONFLICT, "involved_work_ids", "merge_needs_two_works"
        )
    if linking_evidence is None:
        raise _validation_error(
            OperationId.IDENTITY_RESOLVE_CONFLICT, "linking_evidence", "missing_required_field"
        )

    first_id, second_id = conflict.involved_work_ids[0], conflict.involved_work_ids[1]
    with _transaction(target) as connection:
        repository = IdentityRepository(connection)
        # A quarantined work is not `active`, and merge_works refuses anything else; the owner's
        # decision is what lifts the quarantine, inside the same transaction as the merge.
        repository.set_identity_state(owner_id, [first_id, second_id], "active")
        result = merge_works(
            connection,
            owner_id=owner_id,
            work_ids=(first_id, second_id),
            linking_evidence=linking_evidence,
            performed_by="owner_manual",
            owner_choice_work_id=winner_work_id,
            caller_module=OWNER_MODULE,
            now=moment,
            merge_id=merge_id,
        )
        repository.close_conflict(
            owner_id,
            conflict_id,
            state="resolved_merged",
            resolved_at=moment,
            resolution_note=resolution_note,
            resolution_merge_id=result.merge_id,
        )
    return ConflictResolution(conflict_id=conflict.id, state="resolved_merged", merge=result)


# ---------------------------------------------------------------------------------------------
# work.get_detail
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class WorkDetail:
    """The read model behind ``work.get_detail``.

    ``target`` alone is what the HTTP route returns, because ``contracts/http/openapi.yaml``
    pins the 200 response of this operation to ``target.schema.json``, whose branches are
    ``additionalProperties: false``. The remaining fields are the "nguồn dẫn", version and alias
    lists ports.yaml describes; the handoff raises a change request about the gap between the
    two contracts rather than inventing a wire shape here.
    """

    target: dict[str, Any]
    source_posts: list[dict[str, Any]]
    work_versions: list[dict[str, Any]]
    aliases: list[dict[str, Any]]
    first_announced: dict[str, Any] | None


def get_detail(
    target: Executor,
    *,
    owner_id: str,
    work_id: str,
    caller_module: str = "MOD-web-ui",
) -> WorkDetail:
    """``work.get_detail`` -- read-only. A ``merged`` id resolves to the surviving work.

    That resolution is the visible half of I03d: a link to a work that was later merged keeps
    working and shows the identity that survived, instead of a dead page.
    """
    _require_edge(OperationId.WORK_GET_DETAIL, caller_module)
    with _reading(target) as connection:
        repository = IdentityRepository(connection)
        work = repository.resolve_work(owner_id, work_id)
        if work is None:
            raise IdentityError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.WORK_GET_DETAIL.value,
                    "resource_kind": "work",
                },
            )
        return WorkDetail(
            target=_work_target(work),
            source_posts=repository.source_posts(owner_id, work.id),
            work_versions=repository.work_versions(owner_id, work.id),
            aliases=[
                {
                    "id_scheme": alias.id_scheme,
                    "id_value_normalized": alias.id_value_normalized,
                    "id_value_raw": alias.id_value_raw,
                    "evidence_source": alias.evidence_source,
                    "confidence": alias.confidence,
                }
                for alias in repository.aliases_of_work(owner_id, work.id)
            ],
            first_announced=repository.effective_first_announced(owner_id, work.id),
        )
