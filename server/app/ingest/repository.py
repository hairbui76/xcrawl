"""Repository port for ``MOD-ingest-service``.

Scope of the port
-----------------
Exactly three tables: ``post``, ``ingest_receipt``, ``checkpoint``. Those are the tables
``contracts/data/entities.yaml`` marks ``owner_module: MOD-ingest-service``. Nothing here
reads or writes ``run``, ``owner``, ``assignment_lease``, ``work``, ``identity_alias`` or
any other module's table -- that restriction is the point of the port
(``contracts/modules.yaml`` default deny, ``DC-SRV-01``), not an accident of what this card
happened to need.

Every method takes an already-open :class:`~sqlalchemy.Connection`. The repository never
opens or commits a transaction: the transaction boundary is a contract fact
(``TXN-ingest-batch``, ``TXN-checkpoint-only``) and it lives in ``service.py`` where the
commit point is named. A repository that could commit on its own would make "one
transaction" unverifiable from reading the service.

SQLAlchemy 2 **Core** with explicit SQL, per ADR-0011: the DDL in
``server/migrations/versions/0002_tc_ingest_idempotent_ack_lost.py`` uses deferred foreign
keys and multi-column CHECKs that an ORM mapping would obscure.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, text

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid() -> str:
    """A 26-character Crockford base32 ULID (``entities.yaml`` §conventions/id_type).

    Timestamp-ordered so row ids sort by creation time; the random tail is
    :func:`os.urandom`, not the ``random`` module, so two processes minting ids in the same
    millisecond do not collide.
    """
    timestamp = int(time.time() * 1000)
    randomness = int.from_bytes(os.urandom(10), "big")
    value = (timestamp << 80) | randomness
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


@dataclass(frozen=True)
class PostRow:
    """The columns of ``post`` this card reads back (``ENT-post``)."""

    id: str
    x_post_id: str
    discovered_at: str
    ingest_sequence: int
    identity_resolution: str
    source_deleted_observed_at: str | None


@dataclass(frozen=True)
class CheckpointRow:
    """``ENT-checkpoint`` -- a durable cursor mark, append-only."""

    id: str
    owner_id: str
    run_id: str
    phase: str
    sequence: int
    cursor_token: str | None
    cursor_state: str
    acked_through_ingest_sequence: int
    items_ingested_total: int
    created_at: str
    created_by_receipt_id: str | None


@dataclass(frozen=True)
class ReceiptRow:
    """``ENT-ingest-receipt`` -- immutable proof that one batch committed."""

    id: str
    owner_id: str
    receipt_kind: str
    idempotency_key: str
    request_id: str
    payload_hash: str
    schema_version: str
    run_id: str
    job_id: str
    lease_id: str
    lease_epoch: int
    items_received: int
    posts_inserted: int
    posts_duplicate: int
    items_rejected: int
    works_linked: int
    checkpoint_id: str
    max_ingest_sequence: int
    committed_at: str
    receipt_hash: str


class IngestRepository:
    """Table-scoped data access for the ingest domain."""

    # ---------------------------------------------------------------- receipts

    def find_receipt(
        self, connection: Connection, *, owner_id: str, idempotency_key: str
    ) -> ReceiptRow | None:
        """Look up the committed receipt for ``(owner_id, idempotency_key)``.

        This is the read behind ``ingest.get_receipt`` and behind the replay branch of
        ``ingest.submit_batch``. It opens no write transaction: a replay must not touch the
        database (``TXN-ingest-batch.idempotency.same_key_same_payload``).
        """
        row = connection.execute(
            text(
                "SELECT * FROM ingest_receipt "
                "WHERE owner_id = :owner_id AND idempotency_key = :idempotency_key"
            ),
            {"owner_id": owner_id, "idempotency_key": idempotency_key},
        ).first()
        return None if row is None else self._receipt_row(dict(row._mapping))

    def insert_receipt(self, connection: Connection, row: ReceiptRow) -> None:
        """Insert one ``ingest_receipt``. Rows are immutable; there is no update path."""
        connection.execute(
            text(
                "INSERT INTO ingest_receipt ("
                "id, owner_id, receipt_kind, idempotency_key, request_id, payload_hash, "
                "schema_version, run_id, job_id, lease_id, lease_epoch, items_received, "
                "posts_inserted, posts_duplicate, items_rejected, works_linked, "
                "checkpoint_id, max_ingest_sequence, committed_at, receipt_hash"
                ") VALUES ("
                ":id, :owner_id, :receipt_kind, :idempotency_key, :request_id, :payload_hash, "
                ":schema_version, :run_id, :job_id, :lease_id, :lease_epoch, :items_received, "
                ":posts_inserted, :posts_duplicate, :items_rejected, :works_linked, "
                ":checkpoint_id, :max_ingest_sequence, :committed_at, :receipt_hash)"
            ),
            row.__dict__,
        )

    def max_committed_ingest_sequence(
        self, connection: Connection, *, owner_id: str, run_id: str
    ) -> int:
        """``MAX(ingest_receipt.max_ingest_sequence)`` for one run, or 0.

        This is the right-hand side of the I02 oracle: no checkpoint may point past it.
        """
        value = connection.execute(
            text(
                "SELECT COALESCE(MAX(max_ingest_sequence), 0) FROM ingest_receipt "
                "WHERE owner_id = :owner_id AND run_id = :run_id"
            ),
            {"owner_id": owner_id, "run_id": run_id},
        ).scalar_one()
        return int(value)

    # ------------------------------------------------------------- checkpoints

    def latest_checkpoint(
        self, connection: Connection, *, owner_id: str, run_id: str
    ) -> CheckpointRow | None:
        """The highest-``sequence`` checkpoint of a run (the current cursor mark)."""
        row = connection.execute(
            text(
                "SELECT * FROM checkpoint WHERE owner_id = :owner_id AND run_id = :run_id "
                'ORDER BY "sequence" DESC LIMIT 1'
            ),
            {"owner_id": owner_id, "run_id": run_id},
        ).first()
        return None if row is None else self._checkpoint_row(dict(row._mapping))

    def checkpoint_by_id(self, connection: Connection, checkpoint_id: str) -> CheckpointRow | None:
        """One checkpoint by primary key -- the row a receipt's ``checkpoint_id`` names."""
        row = connection.execute(
            text("SELECT * FROM checkpoint WHERE id = :id"), {"id": checkpoint_id}
        ).first()
        return None if row is None else self._checkpoint_row(dict(row._mapping))

    def insert_checkpoint(self, connection: Connection, row: CheckpointRow) -> None:
        """Append one ``checkpoint`` row.

        Append-only by contract (``ENT-checkpoint``, ``TXN-checkpoint-only``
        §append_only_note): advancing the cursor writes a new row, never an UPDATE of an
        existing one, so the cursor's history survives for diagnosis and the "no row was
        modified" oracle stays measurable.
        """
        payload = dict(row.__dict__)
        payload["sequence_"] = payload.pop("sequence")
        connection.execute(
            text(
                "INSERT INTO checkpoint ("
                'id, owner_id, run_id, phase, "sequence", cursor_token, cursor_state, '
                "acked_through_ingest_sequence, items_ingested_total, created_at, "
                "created_by_receipt_id"
                ") VALUES ("
                ":id, :owner_id, :run_id, :phase, :sequence_, :cursor_token, :cursor_state, "
                ":acked_through_ingest_sequence, :items_ingested_total, :created_at, "
                ":created_by_receipt_id)"
            ),
            payload,
        )

    # ------------------------------------------------------------------- posts

    def posts_by_x_post_id(
        self, connection: Connection, *, owner_id: str, x_post_ids: Sequence[str]
    ) -> dict[str, PostRow]:
        """Existing rows for the given ``x_post_id`` values, keyed by ``x_post_id``.

        ``x_post_id`` is the ingest dedup key (AMD-B05). Absence here is what makes an item
        ``inserted``; presence makes it ``deduplicated``, and the commitment is "no
        duplicate ingest", never "never read twice".
        """
        if not x_post_ids:
            return {}
        params: dict[str, Any] = {"owner_id": owner_id}
        placeholders = []
        for index, x_post_id in enumerate(x_post_ids):
            key = f"x{index}"
            params[key] = x_post_id
            placeholders.append(f":{key}")
        rows = connection.execute(
            text(
                "SELECT id, x_post_id, discovered_at, ingest_sequence, identity_resolution, "
                "source_deleted_observed_at FROM post "
                f"WHERE owner_id = :owner_id AND x_post_id IN ({', '.join(placeholders)})"
            ),
            params,
        ).all()
        return {str(row._mapping["x_post_id"]): self._post_row(dict(row._mapping)) for row in rows}

    def insert_post(self, connection: Connection, values: Mapping[str, Any]) -> None:
        """Insert one ``post`` row. ``media_refs``/``referenced_links`` arrive as JSON text."""
        connection.execute(
            text(
                "INSERT INTO post ("
                "id, owner_id, x_post_id, author_handle, author_display_name, "
                "author_x_user_id, url, text, lang, published_at, discovered_at, "
                "ingest_sequence, collected_at_client, discovered_by_run_id, "
                "ingest_receipt_id, thread_root_x_post_id, is_author_thread_member, "
                "media_refs, referenced_links, identity_resolution, source_snapshot_hash, "
                "content_state, source_deleted_observed_at"
                ") VALUES ("
                ":id, :owner_id, :x_post_id, :author_handle, :author_display_name, "
                ":author_x_user_id, :url, :text, :lang, :published_at, :discovered_at, "
                ":ingest_sequence, :collected_at_client, :discovered_by_run_id, "
                ":ingest_receipt_id, :thread_root_x_post_id, :is_author_thread_member, "
                ":media_refs, :referenced_links, :identity_resolution, :source_snapshot_hash, "
                ":content_state, :source_deleted_observed_at)"
            ),
            dict(values),
        )

    def observe_source_deleted(
        self,
        connection: Connection,
        *,
        owner_id: str,
        x_post_id: str,
        observed_at: str,
    ) -> None:
        """Monotonic NULL -> value write on an existing post.

        ``ENT-post.immutability.monotonic_fields``: ``source_deleted_observed_at`` is the
        **only** column of an already-existing post that a duplicate batch may write, and
        only while it is still NULL. The ``IS NULL`` predicate in the WHERE clause is what
        makes "once set, never overwritten" a property of the SQL rather than of a code
        path that could be reordered later.
        """
        connection.execute(
            text(
                "UPDATE post SET source_deleted_observed_at = :observed_at "
                "WHERE owner_id = :owner_id AND x_post_id = :x_post_id "
                "AND source_deleted_observed_at IS NULL"
            ),
            {"owner_id": owner_id, "x_post_id": x_post_id, "observed_at": observed_at},
        )

    def max_ingest_sequence(self, connection: Connection, *, owner_id: str) -> int:
        """``MAX(post.ingest_sequence)`` for the owner, or 0 when no post exists.

        Owner-scoped, not run-scoped: ``ux_post_owner_ingest_sequence`` is the uniqueness
        the sequence has to respect, and two runs of the same owner share the counter.
        """
        value = connection.execute(
            text("SELECT COALESCE(MAX(ingest_sequence), 0) FROM post WHERE owner_id = :owner_id"),
            {"owner_id": owner_id},
        ).scalar_one()
        return int(value)

    def max_discovered_at(self, connection: Connection, *, owner_id: str) -> str | None:
        """``MAX(post.discovered_at)`` for the owner, for the clock clamp (CR-PC04-03)."""
        value = connection.execute(
            text("SELECT MAX(discovered_at) FROM post WHERE owner_id = :owner_id"),
            {"owner_id": owner_id},
        ).scalar()
        return None if value is None else str(value)

    # ------------------------------------------------------------------ counts

    def count_rows(self, connection: Connection, table: str) -> int:
        """Row count of one of this port's three tables. Refuses any other table name."""
        if table not in {"post", "ingest_receipt", "checkpoint"}:
            raise ValueError(
                f"{table!r} is not a table of MOD-ingest-service; the repository port is "
                "scoped to post, ingest_receipt and checkpoint (contracts/modules.yaml)"
            )
        return int(connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one())

    # ------------------------------------------------------------ row adapters

    @staticmethod
    def _post_row(mapping: Mapping[str, Any]) -> PostRow:
        return PostRow(
            id=str(mapping["id"]),
            x_post_id=str(mapping["x_post_id"]),
            discovered_at=str(mapping["discovered_at"]),
            ingest_sequence=int(mapping["ingest_sequence"]),
            identity_resolution=str(mapping["identity_resolution"]),
            source_deleted_observed_at=(
                None
                if mapping["source_deleted_observed_at"] is None
                else str(mapping["source_deleted_observed_at"])
            ),
        )

    @staticmethod
    def _checkpoint_row(mapping: Mapping[str, Any]) -> CheckpointRow:
        return CheckpointRow(
            id=str(mapping["id"]),
            owner_id=str(mapping["owner_id"]),
            run_id=str(mapping["run_id"]),
            phase=str(mapping["phase"]),
            sequence=int(mapping["sequence"]),
            cursor_token=(
                None if mapping["cursor_token"] is None else str(mapping["cursor_token"])
            ),
            cursor_state=str(mapping["cursor_state"]),
            acked_through_ingest_sequence=int(mapping["acked_through_ingest_sequence"]),
            items_ingested_total=int(mapping["items_ingested_total"]),
            created_at=str(mapping["created_at"]),
            created_by_receipt_id=(
                None
                if mapping["created_by_receipt_id"] is None
                else str(mapping["created_by_receipt_id"])
            ),
        )

    @staticmethod
    def _receipt_row(mapping: Mapping[str, Any]) -> ReceiptRow:
        return ReceiptRow(
            id=str(mapping["id"]),
            owner_id=str(mapping["owner_id"]),
            receipt_kind=str(mapping["receipt_kind"]),
            idempotency_key=str(mapping["idempotency_key"]),
            request_id=str(mapping["request_id"]),
            payload_hash=str(mapping["payload_hash"]),
            schema_version=str(mapping["schema_version"]),
            run_id=str(mapping["run_id"]),
            job_id=str(mapping["job_id"]),
            lease_id=str(mapping["lease_id"]),
            lease_epoch=int(mapping["lease_epoch"]),
            items_received=int(mapping["items_received"]),
            posts_inserted=int(mapping["posts_inserted"]),
            posts_duplicate=int(mapping["posts_duplicate"]),
            items_rejected=int(mapping["items_rejected"]),
            works_linked=int(mapping["works_linked"]),
            checkpoint_id=str(mapping["checkpoint_id"]),
            max_ingest_sequence=int(mapping["max_ingest_sequence"]),
            committed_at=str(mapping["committed_at"]),
            receipt_hash=str(mapping["receipt_hash"]),
        )


def json_text(value: Iterable[Any]) -> str:
    """Serialise a JSON column value (``post.media_refs``, ``post.referenced_links``)."""
    return json.dumps(list(value), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
