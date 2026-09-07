"""The vector repository port: ``embedding_generation`` and ``tag_vector``, and nothing else.

``contracts/modules.yaml`` gives ``MOD-embedding-service`` ``data_owner_of: [tag_vector,
embedding_generation]``. Those two tables are the whole surface of this file. It reads
``work_label.vector`` -- a table ``MOD-analysis-service`` owns -- for exactly one purpose,
counting coverage, and never writes it; card §5 grants no edge that would allow otherwise.

Transactions
------------
Every method takes a live :class:`~sqlalchemy.Connection` rather than opening one. The
service layer owns the boundaries, because card §6 names a commit point
(``embedding.activate_generation`` is "một CAS") and a repository that opened its own
transaction per statement would make that sentence unimplementable: retire-then-activate
would be two commits with a visible instant between them, and the fixture asserts there is
no such instant.

Failure mapping
---------------
A write that SQLite refuses for an operational reason -- disk full, I/O error, database
locked -- becomes ``STORAGE_WRITE_FAILED`` (card §7: "không ghi vector, không đổi active").
A write that SQLite refuses because it would break a constraint is **not** remapped: those
are the invariants doing their job, and the service layer reads the specific violation and
answers with the code the contract assigns to that situation (``IDEMPOTENCY_CONFLICT`` for a
duplicate rebuild, ``EMBEDDING_GENERATION_MISMATCH`` for a second active row). Collapsing
both into one code would hide which of the two happened.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Any

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, text
from sqlalchemy.exc import IntegrityError, OperationalError

from server.app.embedding.generation import (
    EmbeddingError,
    GenerationFingerprint,
    GenerationState,
    Normalization,
    SubjectType,
    Vector,
)

#: The eleven columns of ``ENT-embedding-generation``, in contract order.
_GENERATION_COLUMNS = (
    "id, owner_id, model_name, model_version, dimension, normalization, state, "
    "expected_vector_count, built_vector_count, created_at, activated_at"
)


class GenerationRow:
    """One ``embedding_generation`` row, as the contract declares it.

    A small class rather than a ``dict`` so that a typo in a column name is an attribute
    error at the point of the typo, and so that :meth:`fingerprint` -- the value I12 is
    stated in -- is derived in one place instead of rebuilt by every caller.
    """

    __slots__ = (
        "activated_at",
        "built_vector_count",
        "created_at",
        "dimension",
        "expected_vector_count",
        "id",
        "model_name",
        "model_version",
        "normalization",
        "owner_id",
        "state",
    )

    def __init__(self, row: Sequence[Any]) -> None:
        (
            self.id,
            self.owner_id,
            self.model_name,
            self.model_version,
            dimension,
            normalization,
            state,
            self.expected_vector_count,
            self.built_vector_count,
            self.created_at,
            self.activated_at,
        ) = row
        self.dimension: int = int(dimension)
        self.normalization = Normalization(normalization)
        self.state = GenerationState(state)

    @property
    def fingerprint(self) -> GenerationFingerprint:
        return GenerationFingerprint(
            generation_id=str(self.id),
            model_name=str(self.model_name),
            model_version=str(self.model_version),
            dimension=self.dimension,
            normalization=self.normalization,
        )

    def as_dict(self) -> dict[str, Any]:
        """The response shape of ``embedding.get_active_generation`` (``ports.yaml``)."""
        return {
            "generation_id": self.id,
            "owner_id": self.owner_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "dimension": self.dimension,
            "normalization": self.normalization.value,
            "state": self.state.value,
            "expected_vector_count": self.expected_vector_count,
            "built_vector_count": self.built_vector_count,
            "created_at": self.created_at,
            "activated_at": self.activated_at,
        }


@contextmanager
def _storage_errors(operation_id: OperationId, observed_at: str) -> Iterator[None]:
    """Map an operational SQLite failure to ``STORAGE_WRITE_FAILED``.

    ``IntegrityError`` is deliberately **not** caught: a constraint violation is a contract
    invariant refusing a row, and the caller has a specific code for it.
    """
    try:
        yield
    except OperationalError as exc:
        raise EmbeddingError(
            ErrorCode.STORAGE_WRITE_FAILED,
            details_safe={
                "storage_health": "write_blocked",
                "failed_operation_id": operation_id.value,
                "observed_at": observed_at,
            },
        ) from exc


class EmbeddingRepository:
    """SQL for the two tables ``MOD-embedding-service`` owns."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    # -- reads -------------------------------------------------------------------------

    def active_generation(self, owner_id: str) -> GenerationRow | None:
        """The one row with ``state = 'active'``, or ``None``.

        ``ux_embedding_generation_active`` guarantees there is at most one, so this returns a
        row and not a list: a caller that had to choose between two active generations would
        already have lost I12.
        """
        row = self._connection.execute(
            text(
                f"SELECT {_GENERATION_COLUMNS} FROM embedding_generation "
                "WHERE owner_id = :owner_id AND state = 'active'"
            ),
            {"owner_id": owner_id},
        ).fetchone()
        return None if row is None else GenerationRow(row)

    def generation(self, owner_id: str, generation_id: str) -> GenerationRow | None:
        row = self._connection.execute(
            text(
                f"SELECT {_GENERATION_COLUMNS} FROM embedding_generation "
                "WHERE owner_id = :owner_id AND id = :id"
            ),
            {"owner_id": owner_id, "id": generation_id},
        ).fetchone()
        return None if row is None else GenerationRow(row)

    def generation_by_model(
        self,
        owner_id: str,
        *,
        model_name: str,
        model_version: str,
        dimension: int,
        normalization: Normalization,
    ) -> GenerationRow | None:
        """The row ``ux_embedding_generation_model`` would collide with.

        This is the read half of ``embedding.start_generation_rebuild``'s idempotency rule;
        the index is the half that survives two callers racing.
        """
        row = self._connection.execute(
            text(
                f"SELECT {_GENERATION_COLUMNS} FROM embedding_generation "
                "WHERE owner_id = :owner_id AND model_name = :model_name "
                "AND model_version = :model_version AND dimension = :dimension "
                "AND normalization = :normalization"
            ),
            {
                "owner_id": owner_id,
                "model_name": model_name,
                "model_version": model_version,
                "dimension": dimension,
                "normalization": normalization.value,
            },
        ).fetchone()
        return None if row is None else GenerationRow(row)

    def generations(self, owner_id: str) -> list[GenerationRow]:
        rows = self._connection.execute(
            text(
                f"SELECT {_GENERATION_COLUMNS} FROM embedding_generation "
                "WHERE owner_id = :owner_id ORDER BY created_at, id"
            ),
            {"owner_id": owner_id},
        ).fetchall()
        return [GenerationRow(row) for row in rows]

    def tag_vector(
        self,
        owner_id: str,
        *,
        subject_type: SubjectType,
        subject_id: str,
        generation: GenerationRow,
    ) -> Vector | None:
        """One stored vector, decoded against its generation's dimension.

        Decoding through :meth:`~server.app.embedding.generation.Vector.from_blob` is what
        turns "the blob length must match the dimension" from a comment in ``entities.yaml``
        into a refusal: a row whose length drifted cannot be read back as a usable vector.
        """
        row = self._connection.execute(
            text(
                "SELECT vector FROM tag_vector WHERE owner_id = :owner_id "
                "AND subject_type = :subject_type AND subject_id = :subject_id "
                "AND embedding_generation_id = :generation_id"
            ),
            {
                "owner_id": owner_id,
                "subject_type": subject_type.value,
                "subject_id": subject_id,
                "generation_id": generation.id,
            },
        ).fetchone()
        return None if row is None else Vector.from_blob(bytes(row[0]), generation.fingerprint)

    def count_vectors(self, owner_id: str, generation_id: str) -> int:
        """Vectors that exist for a generation: ``tag_vector`` rows plus non-NULL labels.

        ``work_label.vector`` is nullable precisely so that a label can exist before its
        vector has been computed ("NULL khi generation đang build"), so a NULL label counts
        towards *expected* and not towards *built*. Counting it as built would let a
        generation activate while half its labels are unscoreable -- which is the failure the
        activation guard exists to prevent.
        """
        tags = self._connection.execute(
            text(
                "SELECT COUNT(*) FROM tag_vector WHERE owner_id = :owner_id "
                "AND embedding_generation_id = :generation_id"
            ),
            {"owner_id": owner_id, "generation_id": generation_id},
        ).scalar_one()
        labels = self._connection.execute(
            text(
                "SELECT COUNT(*) FROM work_label WHERE owner_id = :owner_id "
                "AND embedding_generation_id = :generation_id AND vector IS NOT NULL"
            ),
            {"owner_id": owner_id, "generation_id": generation_id},
        ).scalar_one()
        return int(tags) + int(labels)

    def label_vectors(
        self, owner_id: str, target_key: str, generation: GenerationRow
    ) -> list[Vector]:
        """``labels(X)`` of ``selection.md`` §3.2, for one target and one generation.

        ``vector IS NOT NULL`` is in the WHERE clause rather than handled afterwards: the
        contract's rule is that a label still being computed is **excluded from the set**,
        not scored as zero, and a filter that never produces the row cannot accidentally
        score it (fixture ``l``: "Coi vector NULL là điểm tương đồng 0" is a forbidden
        effect).
        """
        rows = self._connection.execute(
            text(
                "SELECT vector FROM work_label WHERE owner_id = :owner_id "
                "AND target_key = :target_key AND embedding_generation_id = :generation_id "
                "AND vector IS NOT NULL ORDER BY id"
            ),
            {
                "owner_id": owner_id,
                "target_key": target_key,
                "generation_id": generation.id,
            },
        ).fetchall()
        return [Vector.from_blob(bytes(row[0]), generation.fingerprint) for row in rows]

    # -- writes ------------------------------------------------------------------------

    def insert_generation(
        self,
        *,
        generation_id: str,
        owner_id: str,
        model_name: str,
        model_version: str,
        dimension: int,
        normalization: Normalization,
        state: GenerationState,
        expected_vector_count: int | None,
        created_at: str,
        activated_at: str | None,
    ) -> None:
        """Insert one generation. Raises :class:`~sqlalchemy.exc.IntegrityError` on collision.

        The collision is meaningful, so it is left to propagate: the service turns a
        ``ux_embedding_generation_model`` violation into ``IDEMPOTENCY_CONFLICT`` and a
        ``ux_embedding_generation_active`` violation into ``EMBEDDING_GENERATION_MISMATCH``.
        """
        with _storage_errors(OperationId.EMBEDDING_START_GENERATION_REBUILD, created_at):
            self._connection.execute(
                text(
                    "INSERT INTO embedding_generation (id, owner_id, model_name, model_version, "
                    "dimension, normalization, state, expected_vector_count, built_vector_count, "
                    "created_at, activated_at) VALUES (:id, :owner_id, :model_name, "
                    ":model_version, :dimension, :normalization, :state, :expected, 0, "
                    ":created_at, :activated_at)"
                ),
                {
                    "id": generation_id,
                    "owner_id": owner_id,
                    "model_name": model_name,
                    "model_version": model_version,
                    "dimension": dimension,
                    "normalization": normalization.value,
                    "state": state.value,
                    "expected": expected_vector_count,
                    "created_at": created_at,
                    "activated_at": activated_at,
                },
            )

    def upsert_tag_vector(
        self,
        *,
        vector_id: str,
        owner_id: str,
        subject_type: SubjectType,
        subject_id: str,
        generation: GenerationRow,
        vector: Vector,
        observed_at: str,
    ) -> bool:
        """Store one vector idempotently. Returns ``True`` if a new row was created.

        ``ports.yaml`` gives ``embedding.generate_vectors`` the idempotency key
        ``text_hash + model_name + model_version + generation`` with the rule "Cùng khóa trả
        vector đã lưu; không sinh bản thứ hai". The durable expression of that key is
        ``ux_tag_vector_subject_generation``: the subject identifies the text, and the
        generation carries the model name and version. ``ON CONFLICT DO NOTHING`` is what
        makes a re-run of a half-finished rebuild cheap and, more importantly, what keeps
        ``built_vector_count`` honest -- the counter is incremented only when this returns
        ``True``.
        """
        if vector.fingerprint != generation.fingerprint:
            raise EmbeddingError(
                ErrorCode.EMBEDDING_GENERATION_MISMATCH,
                details_safe=generation.fingerprint.mismatch_details(vector.fingerprint),
            )
        with _storage_errors(OperationId.EMBEDDING_GENERATE_VECTORS, observed_at):
            result = self._connection.execute(
                text(
                    "INSERT INTO tag_vector (id, owner_id, subject_type, subject_id, "
                    "embedding_generation_id, vector) VALUES (:id, :owner_id, :subject_type, "
                    ":subject_id, :generation_id, :vector) "
                    "ON CONFLICT (owner_id, subject_type, subject_id, embedding_generation_id) "
                    "DO NOTHING"
                ),
                {
                    "id": vector_id,
                    "owner_id": owner_id,
                    "subject_type": subject_type.value,
                    "subject_id": subject_id,
                    "generation_id": generation.id,
                    "vector": vector.to_blob(),
                },
            )
        return bool(result.rowcount)

    def set_built_vector_count(self, owner_id: str, generation_id: str, count: int) -> None:
        """Write the coverage counter back from a real ``COUNT(*)``.

        Recomputed rather than incremented: an increment drifts the first time a rebuild is
        interrupted between the vector insert and the counter update, and the guard that
        decides whether a generation may go live must not be reading a number that drifted.
        """
        self._connection.execute(
            text(
                "UPDATE embedding_generation SET built_vector_count = :count "
                "WHERE owner_id = :owner_id AND id = :id"
            ),
            {"count": count, "owner_id": owner_id, "id": generation_id},
        )

    def swap_active(
        self,
        *,
        owner_id: str,
        from_generation_id: str | None,
        to_generation_id: str,
        activated_at: str,
    ) -> None:
        """Retire the current active generation and activate ``to_generation_id``.

        Two statements, **one** transaction -- the caller's. Ordered retire-then-activate
        because ``ux_embedding_generation_active`` is a real index: the reverse order would
        have two active rows momentarily and SQLite would refuse the second statement, which
        is the constraint doing exactly what it is for.

        The old rows are updated, never deleted: ``REQ-D48`` keeps the previous generation and
        every vector under it, so an already-published report stays readable (I05, and fixture
        ``n``'s "G1 được GIỮ LẠI, không xóa").
        """
        with _storage_errors(OperationId.EMBEDDING_ACTIVATE_GENERATION, activated_at):
            if from_generation_id is not None:
                self._connection.execute(
                    text(
                        "UPDATE embedding_generation SET state = 'retired' "
                        "WHERE owner_id = :owner_id AND id = :id AND state = 'active'"
                    ),
                    {"owner_id": owner_id, "id": from_generation_id},
                )
            result = self._connection.execute(
                text(
                    "UPDATE embedding_generation SET state = 'active', activated_at = :at "
                    "WHERE owner_id = :owner_id AND id = :id AND state = 'building'"
                ),
                {"at": activated_at, "owner_id": owner_id, "id": to_generation_id},
            )
        if result.rowcount != 1:
            # The row moved between the read and the write: another activation won, or the
            # generation was retired. Losing this race is `CONFLICT` territory for the
            # caller, so surface it as a mismatch rather than committing a half-swap.
            raise EmbeddingError(
                ErrorCode.EMBEDDING_GENERATION_MISMATCH,
                details_safe={
                    "expected_generation_id": to_generation_id,
                    "seen_generation_id": from_generation_id,
                },
            )


def is_unique_violation(exc: IntegrityError, *, distinguishing_column: str) -> bool:
    """Whether ``exc`` is a UNIQUE violation whose column list mentions ``distinguishing_column``.

    SQLite names the *columns* in the message, never the index::

        UNIQUE constraint failed: embedding_generation.owner_id
        UNIQUE constraint failed: embedding_generation.owner_id, embedding_generation.model_name, …

    which is why the two indexes on this table are told apart by a column only one of them
    covers (``model_name``) rather than by the index name a caller would expect to see.
    Matching on the index name would compile, run, and silently never match.
    """
    message = str(exc.orig)
    return "UNIQUE constraint failed" in message and distinguishing_column in message
