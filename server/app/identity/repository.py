"""Repository port for the tables ``MOD-identity-service`` owns.

Every statement the identity domain issues lives here, so the service layer reads as business
rules and the SQL that enforces ``contracts/data/entities.yaml`` is in one auditable place.
The repository never opens a transaction: it is handed a :class:`~sqlalchemy.Connection` that
already sits inside one, which is how ``TXN-identity-merge`` stays a single BEGIN…COMMIT
(entities.yaml ``transactions[TXN-identity-merge].commit_point``).

Ordering is explicit in every query that returns more than one row. Winner selection and the
merge move-set must be reproducible across runs -- an oracle that depends on SQLite's scan
order is not an oracle (identity.md §6.2).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Final

from sqlalchemy import Connection, text

#: Crockford base32, excluding I, L, O and U (ULID spec) -- matches the `ulid` pattern in
#: contracts/schemas/target.schema.json.
_CROCKFORD: Final[str] = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def utc_now_ms() -> str:
    """Server clock as RFC 3339 UTC with millisecond precision (entities.yaml ``conventions``)."""
    return format_timestamp(datetime.now(tz=UTC))


def format_timestamp(moment: datetime) -> str:
    """``2026-09-05T10:31:00.000Z`` -- the only timestamp shape this system stores."""
    moment = moment.astimezone(UTC)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def new_ulid() -> str:
    """A ULID: 48-bit millisecond timestamp + 80 random bits, Crockford base32.

    Time-ordered ids keep pagination stable without a second column (entities.yaml
    ``conventions.id_type``); the randomness comes from ``os.urandom`` so two ids minted in the
    same millisecond do not collide.
    """
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


@dataclass(frozen=True)
class WorkRow:
    """One row of ``work``, in the columns the identity domain reads."""

    id: str
    owner_id: str
    canonical_doi: str | None
    canonical_arxiv_id: str | None
    metadata_state: str
    identity_state: str
    merged_into_work_id: str | None
    first_discovered_at: str
    ingest_sequence: int
    current_work_version_id: str | None


@dataclass(frozen=True)
class AliasRow:
    """One row of ``identity_alias``."""

    id: str
    owner_id: str
    id_scheme: str
    id_value_normalized: str
    id_value_raw: str
    work_id: str
    evidence_source: str
    evidence_ref: dict[str, Any]
    confidence: str
    created_at: str
    superseded_by_merge_id: str | None


@dataclass(frozen=True)
class ConflictRow:
    """One row of ``identity_conflict``."""

    id: str
    owner_id: str
    conflict_type: str
    involved_work_ids: list[str]
    involved_identifiers: list[dict[str, Any]]
    detected_at: str
    state: str
    resolution_note: str | None
    resolved_at: str | None
    resolution_merge_id: str | None


class IdentityRepository:
    """Data access for ``work``, ``identity_alias``, ``identity_conflict``,
    ``identity_merge_audit``, ``work_version`` and the tables the merge move-set rewrites."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    # -- catalogue -----------------------------------------------------------------------

    def table_exists(self, name: str) -> bool:
        """Whether ``name`` exists in this database.

        The merge counts rows in tables owned by cards that have not run yet
        (``ingest_receipt``, ``report_item``). Asking the catalogue is how the transaction
        reports ``0`` honestly instead of crashing or pretending.
        """
        row = self._connection.execute(
            text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = :name"),
            {"name": name},
        ).first()
        return row is not None

    def count(self, table: str, where: str = "1 = 1", params: dict[str, Any] | None = None) -> int:
        """``SELECT COUNT(*)`` on a table this module may read; ``0`` if the table is absent."""
        if not self.table_exists(table):
            return 0
        result = self._connection.execute(
            text(f"SELECT COUNT(*) FROM {table} WHERE {where}"),  # noqa: S608 - internal names
            params or {},
        ).scalar_one()
        return int(result)

    # -- work ----------------------------------------------------------------------------

    def get_work(self, owner_id: str, work_id: str) -> WorkRow | None:
        row = (
            self._connection.execute(
                text(
                    "SELECT id, owner_id, canonical_doi, canonical_arxiv_id, metadata_state, "
                    "       identity_state, merged_into_work_id, first_discovered_at, "
                    "       ingest_sequence, current_work_version_id "
                    "  FROM work WHERE owner_id = :owner_id AND id = :work_id"
                ),
                {"owner_id": owner_id, "work_id": work_id},
            )
            .mappings()
            .first()
        )
        return WorkRow(**dict(row)) if row is not None else None

    def resolve_work(self, owner_id: str, work_id: str) -> WorkRow | None:
        """``resolve_work(id)``: follow ``merged_into_work_id`` to the ``active`` row.

        entities.yaml ``work.resolution_rule`` guarantees depth 1 because the merge writes a
        pointer to the already-resolved winner, but the loop is written anyway and bounded:
        a cycle is a data defect (``merge_cycle_detected``), not something to hang on.
        """
        seen: set[str] = set()
        current = self.get_work(owner_id, work_id)
        while current is not None and current.merged_into_work_id is not None:
            if current.id in seen:
                return None
            seen.add(current.id)
            current = self.get_work(owner_id, current.merged_into_work_id)
        return current

    def insert_work(self, row: dict[str, Any]) -> None:
        self._connection.execute(
            text(
                "INSERT INTO work (id, owner_id, canonical_doi, canonical_arxiv_id, title, "
                "                  paper_url, code_url, current_work_version_id, metadata_state,"
                "                  identity_state, merged_into_work_id, first_discovered_at, "
                "                  ingest_sequence, content_state, created_at) "
                "VALUES (:id, :owner_id, :canonical_doi, :canonical_arxiv_id, :title, "
                "        :paper_url, :code_url, :current_work_version_id, :metadata_state, "
                "        :identity_state, :merged_into_work_id, :first_discovered_at, "
                "        :ingest_sequence, :content_state, :created_at)"
            ),
            row,
        )

    def next_work_ingest_sequence(self, owner_id: str) -> int:
        """``work.ingest_sequence`` is monotonic per owner in its own space (entities.yaml)."""
        current = self._connection.execute(
            text("SELECT COALESCE(MAX(ingest_sequence), 0) FROM work WHERE owner_id = :owner_id"),
            {"owner_id": owner_id},
        ).scalar_one()
        return int(current) + 1

    def set_identity_state(self, owner_id: str, work_ids: list[str], state: str) -> int:
        """Set ``identity_state`` for several works; used by quarantine and its reversal."""
        changed = 0
        for work_id in sorted(work_ids):
            result = self._connection.execute(
                text(
                    "UPDATE work SET identity_state = :state "
                    " WHERE owner_id = :owner_id AND id = :work_id AND identity_state <> :state"
                ),
                {"state": state, "owner_id": owner_id, "work_id": work_id},
            )
            changed += result.rowcount
        return changed

    # -- identity_alias ------------------------------------------------------------------

    def find_alias(self, owner_id: str, scheme: str, value: str) -> AliasRow | None:
        row = (
            self._connection.execute(
                text(
                    "SELECT id, owner_id, id_scheme, id_value_normalized, id_value_raw, work_id, "
                    "       evidence_source, evidence_ref, confidence, created_at, "
                    "       superseded_by_merge_id "
                    "  FROM identity_alias "
                    " WHERE owner_id = :owner_id AND id_scheme = :scheme "
                    "   AND id_value_normalized = :value"
                ),
                {"owner_id": owner_id, "scheme": scheme, "value": value},
            )
            .mappings()
            .first()
        )
        if row is None:
            return None
        data = dict(row)
        data["evidence_ref"] = json.loads(data["evidence_ref"])
        return AliasRow(**data)

    def insert_alias(self, row: dict[str, Any]) -> None:
        payload = dict(row)
        payload["evidence_ref"] = json.dumps(payload["evidence_ref"], sort_keys=True)
        self._connection.execute(
            text(
                "INSERT INTO identity_alias (id, owner_id, id_scheme, id_value_normalized, "
                "                            id_value_raw, work_id, evidence_source, "
                "                            evidence_ref, confidence, created_at, "
                "                            superseded_by_merge_id) "
                "VALUES (:id, :owner_id, :id_scheme, :id_value_normalized, :id_value_raw, "
                "        :work_id, :evidence_source, :evidence_ref, :confidence, :created_at, "
                "        :superseded_by_merge_id)"
            ),
            payload,
        )

    def aliases_of_work(self, owner_id: str, work_id: str) -> list[AliasRow]:
        rows = (
            self._connection.execute(
                text(
                    "SELECT id, owner_id, id_scheme, id_value_normalized, id_value_raw, work_id, "
                    "       evidence_source, evidence_ref, confidence, created_at, "
                    "       superseded_by_merge_id "
                    "  FROM identity_alias WHERE owner_id = :owner_id AND work_id = :work_id "
                    " ORDER BY id_scheme, id_value_normalized"
                ),
                {"owner_id": owner_id, "work_id": work_id},
            )
            .mappings()
            .all()
        )
        out: list[AliasRow] = []
        for row in rows:
            data = dict(row)
            data["evidence_ref"] = json.loads(data["evidence_ref"])
            out.append(AliasRow(**data))
        return out

    # -- identity_conflict ---------------------------------------------------------------

    def insert_conflict(self, row: dict[str, Any]) -> None:
        payload = dict(row)
        payload["involved_work_ids"] = json.dumps(sorted(payload["involved_work_ids"]))
        payload["involved_identifiers"] = json.dumps(
            payload["involved_identifiers"], sort_keys=True
        )
        self._connection.execute(
            text(
                "INSERT INTO identity_conflict (id, owner_id, conflict_type, involved_work_ids, "
                "                               involved_identifiers, detected_at, "
                "                               detected_in_run_id, state, resolution_note, "
                "                               resolved_at, resolution_merge_id) "
                "VALUES (:id, :owner_id, :conflict_type, :involved_work_ids, "
                "        :involved_identifiers, :detected_at, :detected_in_run_id, :state, "
                "        :resolution_note, :resolved_at, :resolution_merge_id)"
            ),
            payload,
        )

    def _conflict_from_row(self, row: dict[str, Any]) -> ConflictRow:
        data = dict(row)
        data["involved_work_ids"] = json.loads(data["involved_work_ids"])
        data["involved_identifiers"] = json.loads(data["involved_identifiers"])
        return ConflictRow(**data)

    _CONFLICT_COLUMNS = (
        "id, owner_id, conflict_type, involved_work_ids, involved_identifiers, detected_at, "
        "state, resolution_note, resolved_at, resolution_merge_id"
    )

    def get_conflict(self, owner_id: str, conflict_id: str) -> ConflictRow | None:
        row = (
            self._connection.execute(
                text(
                    f"SELECT {self._CONFLICT_COLUMNS} FROM identity_conflict "
                    " WHERE owner_id = :owner_id AND id = :conflict_id"
                ),
                {"owner_id": owner_id, "conflict_id": conflict_id},
            )
            .mappings()
            .first()
        )
        return self._conflict_from_row(dict(row)) if row is not None else None

    def open_conflicts(self, owner_id: str) -> list[ConflictRow]:
        rows = (
            self._connection.execute(
                text(
                    f"SELECT {self._CONFLICT_COLUMNS} FROM identity_conflict "
                    " WHERE owner_id = :owner_id AND state = 'open' ORDER BY detected_at, id"
                ),
                {"owner_id": owner_id},
            )
            .mappings()
            .all()
        )
        return [self._conflict_from_row(dict(row)) for row in rows]

    def close_conflict(
        self,
        owner_id: str,
        conflict_id: str,
        *,
        state: str,
        resolved_at: str,
        resolution_note: str | None,
        resolution_merge_id: str | None,
    ) -> None:
        self._connection.execute(
            text(
                "UPDATE identity_conflict "
                "   SET state = :state, resolved_at = :resolved_at, "
                "       resolution_note = :resolution_note, "
                "       resolution_merge_id = :resolution_merge_id "
                " WHERE owner_id = :owner_id AND id = :conflict_id AND state = 'open'"
            ),
            {
                "state": state,
                "resolved_at": resolved_at,
                "resolution_note": resolution_note,
                "resolution_merge_id": resolution_merge_id,
                "owner_id": owner_id,
                "conflict_id": conflict_id,
            },
        )

    # -- identity_merge_audit -------------------------------------------------------------

    def insert_merge_audit(self, row: dict[str, Any]) -> None:
        payload = dict(row)
        for key in ("linking_evidence", "moved_counts", "preserved_counts"):
            payload[key] = json.dumps(payload[key], sort_keys=True)
        self._connection.execute(
            text(
                "INSERT INTO identity_merge_audit (id, owner_id, winner_work_id, loser_work_id, "
                "                                  winner_selection_rule, linking_evidence, "
                "                                  moved_counts, preserved_counts, merged_at, "
                "                                  performed_by, reversal_of_merge_id) "
                "VALUES (:id, :owner_id, :winner_work_id, :loser_work_id, "
                "        :winner_selection_rule, :linking_evidence, :moved_counts, "
                "        :preserved_counts, :merged_at, :performed_by, :reversal_of_merge_id)"
            ),
            payload,
        )

    def merge_audit_for_loser(self, owner_id: str, loser_work_id: str) -> dict[str, Any] | None:
        row = (
            self._connection.execute(
                text(
                    "SELECT id, winner_work_id, loser_work_id, winner_selection_rule, "
                    "       linking_evidence, moved_counts, preserved_counts, merged_at, "
                    "       performed_by "
                    "  FROM identity_merge_audit "
                    " WHERE owner_id = :owner_id AND loser_work_id = :loser_work_id"
                ),
                {"owner_id": owner_id, "loser_work_id": loser_work_id},
            )
            .mappings()
            .first()
        )
        if row is None:
            return None
        data = dict(row)
        for key in ("linking_evidence", "moved_counts", "preserved_counts"):
            data[key] = json.loads(data[key])
        return data

    # -- merge move-set --------------------------------------------------------------------

    def move_aliases(self, owner_id: str, loser: str, winner: str, merge_id: str) -> int:
        result = self._connection.execute(
            text(
                "UPDATE identity_alias SET work_id = :winner, superseded_by_merge_id = :merge_id "
                " WHERE owner_id = :owner_id AND work_id = :loser"
            ),
            {"winner": winner, "merge_id": merge_id, "owner_id": owner_id, "loser": loser},
        )
        return int(result.rowcount)

    def move_post_work(self, owner_id: str, loser: str, winner: str, merge_id: str) -> int:
        """Move ``(post, loser)`` edges to the winner; delete the ones the winner already has.

        Deleting a *duplicated edge row* is the single deletion this contract permits, and only
        because ``(post, winner)`` already carries the same fact (entities.yaml
        ``post_work.merge_behaviour``). No post and no work is ever deleted.
        """
        duplicates = self._connection.execute(
            text(
                "DELETE FROM post_work "
                " WHERE owner_id = :owner_id AND work_id = :loser AND post_id IN "
                "       (SELECT post_id FROM post_work WHERE owner_id = :owner_id "
                "         AND work_id = :winner)"
            ),
            {"owner_id": owner_id, "loser": loser, "winner": winner},
        ).rowcount
        moved = self._connection.execute(
            text(
                "UPDATE post_work SET work_id = :winner, moved_by_merge_id = :merge_id "
                " WHERE owner_id = :owner_id AND work_id = :loser"
            ),
            {"winner": winner, "merge_id": merge_id, "owner_id": owner_id, "loser": loser},
        ).rowcount
        return int(duplicates) + int(moved)

    def move_work_versions(self, owner_id: str, loser: str, winner: str) -> int:
        """Move versions; on a ``version_label`` collision keep the winner's and rename the
        loser's to ``<label>-from-merge-<loser_work_id>`` so no version evidence is lost."""
        taken = {
            str(row[0])
            for row in self._connection.execute(
                text(
                    "SELECT version_label FROM work_version "
                    " WHERE owner_id = :owner_id AND work_id = :winner"
                ),
                {"owner_id": owner_id, "winner": winner},
            ).all()
        }
        rows = (
            self._connection.execute(
                text(
                    "SELECT id, version_label, is_current FROM work_version "
                    " WHERE owner_id = :owner_id AND work_id = :loser ORDER BY version_label, id"
                ),
                {"owner_id": owner_id, "loser": loser},
            )
            .mappings()
            .all()
        )
        winner_has_current = (
            self._connection.execute(
                text(
                    "SELECT COUNT(*) FROM work_version "
                    " WHERE owner_id = :owner_id AND work_id = :winner AND is_current = 1"
                ),
                {"owner_id": owner_id, "winner": winner},
            ).scalar_one()
            > 0
        )
        moved = 0
        for row in rows:
            label = str(row["version_label"])
            if label in taken:
                label = f"{label}-from-merge-{loser}"
            is_current = int(row["is_current"])
            if is_current == 1 and winner_has_current:
                # `ux_work_version_current` allows exactly one current version per work; the
                # winner's own current version stays current.
                is_current = 0
            self._connection.execute(
                text(
                    "UPDATE work_version "
                    "   SET work_id = :winner, version_label = :label, is_current = :is_current "
                    " WHERE id = :id"
                ),
                {"winner": winner, "label": label, "is_current": is_current, "id": row["id"]},
            )
            if is_current == 1:
                winner_has_current = True
            taken.add(label)
            moved += 1
        return moved

    def move_row_target(self, table: str, row_id: str, winner: str, merge_id: str | None) -> None:
        """Repoint one row of ``table`` from the losing work to the winner.

        Row at a time, not one bulk UPDATE, because three of the move-set tables carry a UNIQUE
        index that a blind bulk move would violate; the collision rules live in the service.
        ``target_key`` is a STORED generated column, so it follows ``target_work_id`` by
        derivation -- the move-set entry "columns: [target_work_id, target_key]" cannot end up
        half-applied.
        """
        assignment = "target_work_id = :winner"
        params: dict[str, Any] = {"winner": winner, "row_id": row_id}
        if merge_id is not None:
            assignment += ", moved_by_merge_id = :merge_id"
            params["merge_id"] = merge_id
        self._connection.execute(
            text(
                f"UPDATE {table} SET {assignment} WHERE id = :row_id"  # noqa: S608 - literal set
            ),
            params,
        )

    def rows_for_merge_target(
        self, table: str, owner_id: str, work_id: str, columns: str
    ) -> list[dict[str, Any]]:
        if not self.table_exists(table):
            return []
        rows = (
            self._connection.execute(
                text(
                    f"SELECT {columns} FROM {table} "  # noqa: S608 - table name from a literal set
                    " WHERE owner_id = :owner_id AND target_work_id = :work_id ORDER BY id"
                ),
                {"owner_id": owner_id, "work_id": work_id},
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def demote_analysis(self, analysis_id: str, merge_id: str) -> None:
        """``status = 'superseded_by_merge'`` -- the collision outcome the move-set names.

        The row is never deleted: an analysis result is evidence of what the owner read.
        """
        self._connection.execute(
            text(
                "UPDATE analysis SET status = 'superseded_by_merge', moved_by_merge_id = :merge_id"
                " WHERE id = :id"
            ),
            {"merge_id": merge_id, "id": analysis_id},
        )

    def demote_saved_item(self, saved_item_id: str, merge_id: str) -> None:
        """``state = 'superseded_by_merge'`` -- keeps at most one ``active`` Saved (I08)."""
        self._connection.execute(
            text(
                "UPDATE saved_item SET state = 'superseded_by_merge', "
                "       moved_by_merge_id = :merge_id WHERE id = :id"
            ),
            {"merge_id": merge_id, "id": saved_item_id},
        )

    def mark_work_merged(self, owner_id: str, loser: str, winner: str) -> None:
        self._connection.execute(
            text(
                "UPDATE work SET identity_state = 'merged', merged_into_work_id = :winner "
                " WHERE owner_id = :owner_id AND id = :loser"
            ),
            {"winner": winner, "owner_id": owner_id, "loser": loser},
        )

    def update_winner_columns(self, owner_id: str, winner: str, values: dict[str, Any]) -> None:
        if not values:
            return
        assignments = ", ".join(f"{column} = :{column}" for column in sorted(values))
        params = dict(values)
        params.update({"owner_id": owner_id, "winner": winner})
        self._connection.execute(
            text(
                f"UPDATE work SET {assignments} "  # noqa: S608 - column names from a literal set
                " WHERE owner_id = :owner_id AND id = :winner"
            ),
            params,
        )

    # -- first_announced_ledger (owned by MOD-report-service; written here per
    #    contracts/reporting/time-and-tags.md §8.3, in the merge transaction) --------------

    def effective_first_announced(self, owner_id: str, work_id: str) -> dict[str, Any] | None:
        """The ledger row currently in force for a work: ``superseded_by_merge_id IS NULL``."""
        if not self.table_exists("first_announced_ledger"):
            return None
        row = (
            self._connection.execute(
                text(
                    "SELECT id, canonical_work_id, first_report_id, first_announced_at, "
                    "       merge_audit_id, superseded_by_merge_id "
                    "  FROM first_announced_ledger "
                    " WHERE owner_id = :owner_id AND canonical_work_id = :work_id "
                    "   AND superseded_by_merge_id IS NULL"
                ),
                {"owner_id": owner_id, "work_id": work_id},
            )
            .mappings()
            .first()
        )
        return dict(row) if row is not None else None

    def update_first_announced(self, ledger_id: str, values: dict[str, Any]) -> None:
        assignments = ", ".join(f"{column} = :{column}" for column in sorted(values))
        params = dict(values)
        params["id"] = ledger_id
        self._connection.execute(
            text(
                f"UPDATE first_announced_ledger SET {assignments} "  # noqa: S608 - literal set
                " WHERE id = :id"
            ),
            params,
        )

    # -- read model ------------------------------------------------------------------------

    def work_versions(self, owner_id: str, work_id: str) -> list[dict[str, Any]]:
        rows = (
            self._connection.execute(
                text(
                    "SELECT id, version_label, version_scheme, announced_at, observed_at, "
                    "       content_fingerprint, is_current FROM work_version "
                    " WHERE owner_id = :owner_id AND work_id = :work_id "
                    " ORDER BY version_label, id"
                ),
                {"owner_id": owner_id, "work_id": work_id},
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def source_posts(self, owner_id: str, work_id: str) -> list[dict[str, Any]]:
        """The "nguồn dẫn" list of REQ-AC07: every post that led to this work, once each."""
        rows = (
            self._connection.execute(
                text(
                    "SELECT p.id AS post_id, p.x_post_id, p.url, p.author_handle, p.discovered_at, "
                    "       pw.link_evidence "
                    "  FROM post_work pw JOIN post p ON p.id = pw.post_id "
                    " WHERE pw.owner_id = :owner_id AND pw.work_id = :work_id "
                    " ORDER BY p.ingest_sequence, p.id"
                ),
                {"owner_id": owner_id, "work_id": work_id},
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]

    def saved_snapshot_digest(self, owner_id: str) -> list[tuple[str, str]]:
        """``{(id, content_hash)}`` -- the set I17 compares before and after a merge."""
        if not self.table_exists("saved_snapshot"):
            return []
        rows = self._connection.execute(
            text(
                "SELECT id, content_hash FROM saved_snapshot WHERE owner_id = :owner_id "
                " ORDER BY id"
            ),
            {"owner_id": owner_id},
        ).all()
        return [(str(row[0]), str(row[1])) for row in rows]
