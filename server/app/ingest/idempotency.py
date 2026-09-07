"""Idempotency for ``ingest.submit_batch`` and ``ingest.commit_checkpoint``.

This module answers exactly one question and holds no state: *given an idempotency key and
the payload hash that arrived with it, is this call a new batch, a replay of a committed
one, or a conflict?* Everything else -- opening a transaction, writing rows -- belongs to
``service.py``.

The three hashes
----------------
``contracts/data/entities.yaml`` §conventions/hashes fixes the format (``sha256:`` + 64
lowercase hex) and the canonicalisation (RFC 8785 / JCS, UTF-8, no BOM) for every hash
computed over structured data. Three of them live here:

``payload_hash``
    ``sha256(JCS(payload_core))`` with ``payload_core = {schema_version, items,
    client_checkpoint_proposal}`` -- ``contracts/schemas/ingest-batch.schema.json``
    §x-contract.payload_hash_definition. ``request_id``, ``idempotency_key``, ``job_id``,
    ``lease_id`` and ``lease_epoch`` are excluded **on purpose**: a retry mints a new
    ``request_id`` and must still hash to the same value, or every ack-loss retry would
    look like ``IDEMPOTENCY_CONFLICT`` instead of a replay.

``receipt_hash``
    ``sha256(JCS({idempotency_key, payload_hash, counts, checkpoint_id,
    max_ingest_sequence}))`` -- ``ENT-ingest-receipt``. It is the client's proof that a
    replay returned *its* receipt and not some other one, so it must be identical between
    the first commit and every replay. ``counts`` is the wire ``counts`` object of
    ``contracts/schemas/ingest-receipt.schema.json``.

``source_snapshot_hash``
    ``sha256(JCS(item))`` over the ingest item exactly as received -- ``ENT-post``. It lets
    a stored row be proven to match the payload the server accepted.

Known limitation of the canonicaliser
-------------------------------------
RFC 8785 orders object members by their UTF-16 code units; :func:`json.dumps` with
``sort_keys=True`` orders by Unicode code point. The two orders differ only for keys
containing characters above U+FFFF, which no contract in this repo uses (every key is
ASCII). Numbers are emitted by Python's shortest-round-trip float repr, which agrees with
ECMAScript ``Number.prototype.toString`` for every value the ingest schemas allow
(integers, and no floats at all). The oracle for this claim is not prose: the two
``payload_hash`` values that ``acceptance/fixtures/identity/pos-ingest-batch-valid.json``
and ``.../f-ingest-replay-idempotent.json`` carry were computed independently from these
contracts, and ``tests/contract/test_ingest_idempotency.py`` recomputes them here.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from enum import Enum
from typing import Any

#: The three request fields that make up ``payload_core`` (ingest-batch.schema.json).
PAYLOAD_CORE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "items",
    "client_checkpoint_proposal",
)

#: The five fields hashed into ``receipt_hash`` (ENT-ingest-receipt).
RECEIPT_HASH_FIELDS: tuple[str, ...] = (
    "idempotency_key",
    "payload_hash",
    "counts",
    "checkpoint_id",
    "max_ingest_sequence",
)

_HASH_PREFIX = "sha256:"


class ReplayDecision(Enum):
    """What the stored receipt (if any) says about an incoming call.

    ``NEW``
        No receipt exists for this key: run the transaction.
    ``REPLAY``
        A receipt exists and its ``payload_hash`` matches: return it unchanged, write
        nothing (I02(c)).
    ``CONFLICT``
        A receipt exists with a different ``payload_hash``: ``IDEMPOTENCY_CONFLICT``, and
        the stored receipt is never overwritten (SRC-PLAN §5.1).
    """

    NEW = "new"
    REPLAY = "replay"
    CONFLICT = "conflict"


def canonical_json(value: Any) -> str:
    """Serialise ``value`` as canonical JSON (RFC 8785 subset -- see module docstring)."""
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def sha256_of(value: Any) -> str:
    """``sha256:`` + hex digest of the canonical JSON encoding of ``value``."""
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"{_HASH_PREFIX}{digest}"


def payload_core(batch: Mapping[str, Any]) -> dict[str, Any]:
    """Project a raw ingest-batch request onto the fields that ``payload_hash`` covers."""
    return {field: batch[field] for field in PAYLOAD_CORE_FIELDS if field in batch}


def compute_payload_hash(batch: Mapping[str, Any]) -> str:
    """``sha256(JCS(payload_core))`` for a raw ingest-batch request body."""
    return sha256_of(payload_core(batch))


def compute_receipt_hash(
    *,
    idempotency_key: str,
    payload_hash: str,
    counts: Mapping[str, Any],
    checkpoint_id: str,
    max_ingest_sequence: int,
) -> str:
    """``sha256(JCS({idempotency_key, payload_hash, counts, checkpoint_id, max_seq}))``.

    Deliberately a function of committed facts only. Nothing here varies between the
    commit and a later replay, which is what makes ``receipt_hash`` usable as the client's
    "this is my receipt" oracle (``ENT-ingest-receipt``, fixture ``f-ingest-replay-
    idempotent`` symbol ``H_RCf``).
    """
    return sha256_of(
        {
            "idempotency_key": idempotency_key,
            "payload_hash": payload_hash,
            "counts": dict(counts),
            "checkpoint_id": checkpoint_id,
            "max_ingest_sequence": max_ingest_sequence,
        }
    )


def compute_source_snapshot_hash(item: Mapping[str, Any]) -> str:
    """``sha256(JCS(item))`` over one ingest item as received (``ENT-post``)."""
    return sha256_of(dict(item))


def checkpoint_only_idempotency_key(assignment_id: str, checkpoint_seq: int) -> str:
    """The stored key for ``ingest.commit_checkpoint``.

    ``contracts/ports.yaml`` scopes that operation's idempotency to ``assignment_id +
    checkpoint_seq``; this is the concrete spelling of that pair. It satisfies
    ``ENT-ingest-receipt.idempotency_key``'s pattern (``[A-Za-z0-9_.:-]{16,128}``) because
    an assignment id is a 26-character ULID.
    """
    return f"{assignment_id}:{checkpoint_seq}"


def classify(stored_payload_hash: str | None, incoming_payload_hash: str) -> ReplayDecision:
    """Decide NEW / REPLAY / CONFLICT from the stored receipt's hash.

    :param stored_payload_hash: ``payload_hash`` of the committed receipt for this key, or
        ``None`` when the server has never committed that key.
    """
    if stored_payload_hash is None:
        return ReplayDecision.NEW
    if stored_payload_hash == incoming_payload_hash:
        return ReplayDecision.REPLAY
    return ReplayDecision.CONFLICT
