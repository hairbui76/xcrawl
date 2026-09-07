"""Building an ingest batch: item shape, ``payload_hash``, and the idempotency key.

Three things have to be exactly right here, and each has a contract that says why.

``payload_hash``
    ``contracts/schemas/ingest-batch.schema.json`` §x-contract.payload_hash_definition:
    ``"sha256:" + hex(sha256(JCS(payload_core)))`` over
    ``payload_core = {schema_version, items, client_checkpoint_proposal}``. ``request_id``,
    ``idempotency_key``, ``job_id``, ``lease_id`` and ``lease_epoch`` are excluded **on
    purpose**: a retry mints a new ``request_id`` and must still hash the same, or every
    ack-loss retry would come back ``IDEMPOTENCY_CONFLICT`` instead of a replay.

``idempotency_key``
    Derived, not random: :func:`batch_idempotency_key` is a pure function of
    ``(assignment_id, lease_epoch, batch_seq)``. A retry recomputes the same key without
    having to remember one, which is what makes the ack-loss path in
    ``acceptance/fixtures/collection/d-duplicate-ingest-replay.json`` work at all -- and the
    epoch keeps a resumed segment from colliding with the one it resumed.

``client_checkpoint_proposal``
    Sent *with* the items, committed in the same transaction as them
    (``contracts/state/run.yaml`` §CP-01). This is the only path by which a checkpoint
    becomes durable together with its data; the standalone
    ``ingest.commit_checkpoint`` is a cursor-only step (§CP-07) and lives in
    :mod:`collector.app.client`.

Why the hash is recomputed here instead of imported from the server
-------------------------------------------------------------------
``server.app.ingest.idempotency`` has the same function, but importing it would create an
in-process edge from ``MOD-x-collector`` into the server package -- exactly the class of
call ``contracts/modules.yaml`` default-deny forbids, and ``SL-7`` of
``contracts/ops/collector-probe.md`` states the collector process carries no server-side
machinery at all. The two implementations are held together by an oracle rather than by an
import: ``tests/contract/test_collector_stop_reasons.py`` recomputes the ``payload_hash``
values pinned in the ingest fixtures and asserts equality, so a divergence fails a test
instead of silently producing 409s in production.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION

#: ``ingest-batch.schema.json`` ``items.maxItems``. A batch larger than this is a contract
#: violation, so the batcher flushes at the boundary rather than letting the server reject.
MAX_ITEMS_PER_BATCH = 200

#: The three fields ``payload_hash`` covers, in the contract's own order.
PAYLOAD_CORE_FIELDS: tuple[str, ...] = ("schema_version", "items", "client_checkpoint_proposal")

_HASH_PREFIX = "sha256:"


def canonical_json(value: Any) -> str:
    """Canonical JSON (RFC 8785 / JCS subset): sorted keys, no spaces, no NaN.

    The one documented divergence from RFC 8785 is member ordering for keys containing
    characters above U+FFFF (JCS orders by UTF-16 code unit, Python by code point). No key
    in any contract in this repository is non-ASCII, so the two orders coincide here.
    """
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def sha256_of(value: Any) -> str:
    """``sha256:`` + lowercase hex digest of the canonical JSON encoding of ``value``."""
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"{_HASH_PREFIX}{digest}"


def payload_core(batch: Mapping[str, Any]) -> dict[str, Any]:
    """Project a batch body onto the fields ``payload_hash`` covers."""
    return {
        field_name: batch[field_name] for field_name in PAYLOAD_CORE_FIELDS if field_name in batch
    }


def compute_payload_hash(batch: Mapping[str, Any]) -> str:
    """``sha256(JCS(payload_core))`` for an ingest-batch body."""
    return sha256_of(payload_core(batch))


def batch_idempotency_key(assignment_id: str, lease_epoch: int, batch_seq: int) -> str:
    """A deterministic key for one batch of one lease.

    Must satisfy ``^[A-Za-z0-9_.:-]{16,128}$``. An assignment id is a 26-character ULID, so
    ``<ulid>:e<4 digits>:b<6 digits>`` is 40 characters of permitted alphabet.

    **Determinism** is the first reason for a derived key: after a transport timeout the
    collector has to ask about *this* key (``ingest.get_receipt``) and may have to resend
    under it, and a random key it never wrote down is a key it cannot ask about. Within one
    segment the epoch and the sequence do not move, so a retry recomputes the identical key
    and the server recognises a replay.

    **The lease epoch is in the key** because a segment is not the only one an assignment
    can have. Keying on ``assignment_id + batch_seq`` alone makes the first batch of a
    resumed segment collide with the first batch of the interrupted one -- same key, different
    contents -- which the server correctly answers with ``IDEMPOTENCY_CONFLICT``, blocking a
    resume that ought to work. ``contracts/retry-policy.yaml §lease_epoch_rule`` guarantees the
    epoch increments on every grant and is never reused, so including it separates the
    segments without making the key unpredictable.
    """
    if batch_seq < 0:
        raise ValueError("batch_seq must be non-negative")
    if lease_epoch < 1:
        raise ValueError("lease_epoch is `minimum: 1` in worker-assignment.schema.json")
    key = f"{assignment_id}:e{lease_epoch:04d}:b{batch_seq:06d}"
    if not 16 <= len(key) <= 128:
        raise ValueError(f"idempotency key length {len(key)} is outside the contract's 16..128")
    return key


def checkpoint_idempotency_key(assignment_id: str, checkpoint_seq: int) -> str:
    """``assignment_id + checkpoint_seq`` -- the idempotency scope ``contracts/ports.yaml``
    gives ``ingest.commit_checkpoint``. Same spelling the server stores."""
    return f"{assignment_id}:{checkpoint_seq}"


@dataclass(frozen=True)
class CheckpointProposal:
    """``client_checkpoint_proposal`` -- where the collector believes the feed cursor is.

    A *proposal*: the server decides what becomes durable, and the value that comes back in
    the receipt's ``checkpoint_ack`` is the one that counts. The collector never treats its
    own cursor as truth (``worker-assignment.schema.json`` §x-contract.checkpoint_rule).
    """

    phase: str
    cursor_token: str | None
    cursor_state: str
    items_collected_in_run: int
    stop_hint: str = "none"

    def to_wire(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "cursor_token": self.cursor_token,
            "cursor_state": self.cursor_state,
            "items_collected_in_run": self.items_collected_in_run,
            "stop_hint": self.stop_hint,
        }


@dataclass
class Batcher:
    """Accumulates parsed posts and turns them into schema-valid ingest batches.

    :param assignment_id: scopes the idempotency keys.
    :param job_id: ``ingest-batch.job_id``.
    :param lease_id: current lease.
    :param lease_epoch: current epoch. Sent on every batch so the server can reject a
        stale writer *before* any write (``f-two-workers-claim-same-assignment``).
    :param max_items: flush boundary, defaults to the schema's ``maxItems``.
    """

    assignment_id: str
    job_id: str
    lease_id: str
    lease_epoch: int
    run_id: str | None = None
    max_items: int = MAX_ITEMS_PER_BATCH
    _pending: list[dict[str, Any]] = field(default_factory=list, init=False)
    _batch_seq: int = field(default=0, init=False)

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    @property
    def is_full(self) -> bool:
        return len(self._pending) >= self.max_items

    def add(self, item: Mapping[str, Any]) -> None:
        """Buffer one parsed item. Buffered is *not* durable -- see I02."""
        self._pending.append(dict(item))

    def discard_pending(self) -> int:
        """Drop the buffer and report how many items were dropped.

        Called when a stop signal makes further interaction with the source impossible.
        Dropping is the correct behaviour, not a loss: items that were downloaded but never
        ingested are, by ``SRC-PLAN §8.1`` and §CP-03, not a durable checkpoint and must not
        be treated as one. ``c-challenge-mid-batch`` is exactly this case -- 7 posts in RAM,
        0 rows.
        """
        dropped = len(self._pending)
        self._pending.clear()
        return dropped

    def build(
        self,
        *,
        request_id: str,
        proposal: CheckpointProposal,
    ) -> dict[str, Any] | None:
        """Build a batch body from the buffer and clear it. ``None`` when the buffer is empty.

        ``None`` rather than an empty batch: ``ingest-batch.schema.json`` sets
        ``items.minItems = 1`` and says so in prose -- "batch rỗng là lỗi hợp đồng"; the end
        of a segment is reported with a stop operation, never with an empty batch.
        """
        if not self._pending:
            return None
        items = self._pending
        self._pending = []
        self._batch_seq += 1
        batch: dict[str, Any] = {
            "request_id": request_id,
            "schema_version": CONTRACT_SCHEMA_VERSION,
            "idempotency_key": batch_idempotency_key(
                self.assignment_id, self.lease_epoch, self._batch_seq
            ),
            "payload_hash": "",
            "job_id": self.job_id,
            "lease_id": self.lease_id,
            "lease_epoch": self.lease_epoch,
            "items": items,
            "client_checkpoint_proposal": proposal.to_wire(),
        }
        if self.run_id is not None:
            batch["run_id"] = self.run_id
        batch["payload_hash"] = compute_payload_hash(batch)
        return batch


def ingest_item(
    *,
    x_post_id: str,
    author: Mapping[str, Any],
    url: str,
    text: str,
    collected_at: str,
    published_at: str | None = None,
    lang: str | None = None,
    media_refs: Sequence[Mapping[str, Any]] = (),
    referenced_links: Sequence[Mapping[str, Any]] = (),
    thread_context: Mapping[str, Any] | None = None,
    source_provenance: Mapping[str, Any] | None = None,
    source_deleted_observed_at: str | None = None,
) -> dict[str, Any]:
    """One ``ingest-batch.schema.json`` item, with optionals omitted rather than nulled.

    Optional keys are left out when absent instead of being sent as ``null``: the schema
    sets ``additionalProperties: false`` and the collector has no reason to assert "this
    field is null" when what it means is "not observed". ``source_deleted_observed_at`` is
    the exception the contract calls out -- it is an *observation* the collector reports and
    the server interprets (``contracts/ports.yaml`` ``ingest.submit_batch``), so it is
    included whenever it was observed.
    """
    item: dict[str, Any] = {
        "x_post_id": x_post_id,
        "author": dict(author),
        "url": url,
        "text": text,
        "collected_at": collected_at,
        "media_refs": [dict(ref) for ref in media_refs],
        "referenced_links": [dict(link) for link in referenced_links],
    }
    if published_at is not None:
        item["published_at"] = published_at
    if lang is not None:
        item["lang"] = lang
    if thread_context is not None:
        item["thread_context"] = dict(thread_context)
    if source_provenance is not None:
        item["source_provenance"] = dict(source_provenance)
    if source_deleted_observed_at is not None:
        item["source_deleted_observed_at"] = source_deleted_observed_at
    return item
