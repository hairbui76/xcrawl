"""``MOD-embedding-service`` -- the four ``embedding.*`` operations of ``contracts/ports.yaml``.

=====================================  ==========================  =================
operation id                           method                      transaction
=====================================  ==========================  =================
``embedding.generate_vectors``         :meth:`generate_vectors`    one per batch
``embedding.get_active_generation``    :meth:`get_active_generation`  none (read)
``embedding.start_generation_rebuild`` :meth:`start_generation_rebuild`  one
``embedding.activate_generation``      :meth:`activate_generation`  ``TXN-activate``
=====================================  ==========================  =================

All four are methods of :class:`EmbeddingService`.

The commit point that matters
-----------------------------
Card §6: *"``embedding.activate_generation`` là một CAS: chỉ đổi con trỏ active khi generation
mới đã đủ phủ"*. :meth:`EmbeddingService.activate_generation` is one ``BEGIN…COMMIT`` in which
the guard is re-evaluated **inside** the transaction and the retire/activate pair either both
land or neither does. Re-reading the counters inside the transaction is not belt-and-braces:
between a read and a write, another rebuild can have added vectors or another activation can
have won, and a guard evaluated on stale numbers is a guard that passes for the wrong row.

What this module refuses to do
------------------------------
``REQ-D48``/``REQ-D50`` and ``contracts/modules.yaml`` (``network_egress: []``,
``secret_access: none``) put embedding on a **local** model. There is therefore no HTTP
client, no API key, no subprocess and no provider name anywhere in this package; the only way
to produce a vector is a :class:`~server.app.embedding.generation.LocalEncoder`, and that port
has nowhere to put a credential. ``NC-25``/``FE-22`` (embedding → ``EXT-ai-provider-api``,
``CAPABILITY_DENIED``) and ``NC-26``/``FE-23`` (embedding → ``MOD-tag-service``,
``FORBIDDEN_EDGE``) are enforced structurally: this package imports neither a network library
nor ``server.app.tag``, and ``tests/contract/test_embedding_generation_guard.py`` asserts that
about the shipped source rather than trusting this paragraph.

The selection guard, before ``TC-report-coverage-publish-cas`` exists
--------------------------------------------------------------------
Card §11 makes this card depend on the report card to prove *"chặn xảy ra trước publish
commit"*. That card is not written yet, so the guard lives here, at this module's port, in two
pieces the report builder will call:

* :meth:`EmbeddingService.pin_generation` -- read the active generation at build snapshot and
  keep the fingerprint;
* :meth:`EmbeddingService.embedding_generation_matches` -- the side-effect-free predicate
  ``contracts/state/report.yaml`` ``ownership_boundary`` requires PC04 to supply to PC03's CAS,
  named exactly as ``contracts/reporting/time-and-tags.md`` §4.5 spells it.

The one thing that cannot be proven from here is the *ordering* claim -- that the refusal
happens before a publish transaction commits -- because there is no publish transaction to
order against. That test exists and is marked ``xfail(reason="pending
TC-report-coverage-publish-cas")``; it is not deleted, so it turns green by itself the day the
other card lands.
"""

from __future__ import annotations

import hashlib
import os
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError

from server.app.db.engine import session_scope
from server.app.embedding.generation import (
    ComparisonLedger,
    EmbeddingError,
    GenerationFingerprint,
    GenerationState,
    LocalEncoder,
    Normalization,
    SubjectType,
    Vector,
    assert_comparable,
    assert_single_generation,
    coverage_satisfied,
)
from server.app.embedding.repository import EmbeddingRepository, GenerationRow, is_unique_violation

#: ``contracts/modules.yaml`` ``allowed_edges``: the only modules that may call in here.
#: Default deny (``modules.yaml.default_deny``) -- an edge absent from the registry is
#: forbidden, so this is a list of who is allowed and never a list of who is blocked.
ALLOWED_CALLERS: Mapping[OperationId, frozenset[str]] = {
    OperationId.EMBEDDING_GENERATE_VECTORS: frozenset(
        {"MOD-ingest-service", "MOD-tag-service", "MOD-report-service"}
    ),
    OperationId.EMBEDDING_GET_ACTIVE_GENERATION: frozenset(
        {"MOD-tag-service", "MOD-report-service"}
    ),
    OperationId.EMBEDDING_START_GENERATION_REBUILD: frozenset({"MOD-settings-service"}),
    OperationId.EMBEDDING_ACTIVATE_GENERATION: frozenset({"MOD-embedding-service"}),
}

#: ``MOD-embedding-service`` runs *inside* the server process (``runs_on: server``) and all
#: four of its operations are ``transport: internal``, so a caller that is not on the list
#: above is an in-process call across an edge the registry does not have. Ruling R5-01 row 2
#: assigns that ``FORBIDDEN_EDGE`` -- not ``UNAUTHORIZED``, which answers the HTTP question,
#: and not ``CAPABILITY_DENIED``, which answers the process/network/filesystem one.
EDGE_DENIAL_CODE = ErrorCode.FORBIDDEN_EDGE

_CROCKFORD32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid() -> str:
    """A ULID: 48-bit millisecond timestamp, 80 bits of randomness, Crockford base32."""
    value = (int(time.time() * 1000) << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD32[(value >> shift) & 0x1F] for shift in range(125, -1, -5))


def utc_now_ms() -> str:
    """``timestamp_utc_ms``: RFC 3339, UTC, exactly three fractional digits."""
    now = datetime.now(UTC)
    return f"{now.strftime('%Y-%m-%dT%H:%M:%S')}.{now.microsecond // 1000:03d}Z"


def text_hash(text: str) -> str:
    """The ``text_hash`` component of ``embedding.generate_vectors``'s idempotency key."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class StorageGuardPort(Protocol):
    """The write gate ``TC-storage-write-blocked-readiness`` provides.

    Its call contract, quoted from :mod:`server.app.storage.guard`: ask ``assert_writable``
    *before* the write, and let ``StorageRefused`` propagate. It is optional here because
    ``contracts/ports.yaml`` gives ``storage.get_health`` the caller list
    ``[MOD-health-service, MOD-job-service]`` and ``contracts/modules.yaml`` has **no**
    ``MOD-embedding-service → MOD-data-store`` edge, while card §4 lists ``storage.get_health``
    under *Consumes*. Those two cannot both be right, and the card is not the naming authority
    for edges; the contract is. So this module never calls the port itself -- it accepts a
    guard the caller already holds, exactly as :mod:`server.app.ingest.service` does, and the
    contradiction is reported as ``CR-TC-embedding-02`` rather than resolved by taking an edge
    the registry does not grant.
    """

    def assert_writable(self, operation_id: OperationId) -> None: ...


@dataclass(frozen=True, slots=True)
class VectorRequest:
    """One item of ``embedding.generate_vectors``: which subject, and the text to embed."""

    subject_type: SubjectType
    subject_id: str
    text: str


@dataclass(frozen=True, slots=True)
class GeneratedVector:
    """One result: the vector, and whether this call is what created the row.

    ``created=False`` means the idempotency key hit an existing row and the stored vector was
    returned unchanged -- ``ports.yaml``'s "Cùng khóa trả vector đã lưu; không sinh bản thứ
    hai". A caller counting work done reads this field; a caller counting coverage reads
    ``built_vector_count``, which only moves when a row is actually new.
    """

    subject_type: SubjectType
    subject_id: str
    idempotency_key: str
    vector: Vector
    created: bool


@dataclass(frozen=True, slots=True)
class PinnedGeneration:
    """The generation a build snapshot pinned, carried to the publish CAS.

    ``contracts/reporting/selection.md`` §5.1: G is read once, at build snapshot, and written
    into ``report.embedding_generation_id``. Everything that follows in that build is checked
    against this value, and the publish CAS re-checks it against the *current* active
    generation, which is how the switch that happens mid-build is caught.
    """

    fingerprint: GenerationFingerprint
    pinned_at: str

    @property
    def generation_id(self) -> str:
        return self.fingerprint.generation_id


class EmbeddingService:
    """The four operations, over one engine and one local encoder."""

    def __init__(
        self,
        engine: Engine,
        *,
        encoder: LocalEncoder,
        storage_guard: StorageGuardPort | None = None,
        clock: Callable[[], str] = utc_now_ms,
        id_factory: Callable[[], str] = new_ulid,
    ) -> None:
        self._engine = engine
        self._encoder = encoder
        self._storage_guard = storage_guard
        self._clock = clock
        self._new_id = id_factory

    # -- boundary ----------------------------------------------------------------------

    @staticmethod
    def assert_caller_allowed(operation_id: OperationId, caller_module: str) -> None:
        """Default deny at this module's port (card §5, ruling R5-01 row 2).

        ``caller_module`` is a required argument at every entry point rather than a
        defaulted one: a default would mean the deny rule is enforced against callers that
        remembered to identify themselves, which is not a rule.
        """
        if caller_module not in ALLOWED_CALLERS[operation_id]:
            raise EmbeddingError(
                EDGE_DENIAL_CODE,
                details_safe={
                    "caller_module": caller_module,
                    "callee_module": "MOD-embedding-service",
                    # None, and it stays None: none of the 36 `forbidden_edges` has
                    # `MOD-embedding-service` as its *callee*. A refused call in here is the
                    # default-deny rule firing on an unregistered edge, not a named one, and
                    # inventing an `FE-` id for it would put a reference in an envelope that
                    # `contracts/modules.yaml` cannot be looked up against.
                    "forbidden_edge_ref": None,
                },
            )

    def _assert_writable(self, operation_id: OperationId) -> None:
        if self._storage_guard is not None:
            self._storage_guard.assert_writable(operation_id)

    # -- embedding.get_active_generation ------------------------------------------------

    def get_active_generation(self, owner_id: str, *, caller_module: str) -> dict[str, Any]:
        """``embedding.get_active_generation`` -- read-only, no transaction.

        :raises EmbeddingError: ``NOT_FOUND`` when no generation is active. The contract lists
            ``NOT_FOUND`` as this operation's only error code, and "no active generation"
            genuinely is one: returning ``None`` would let a builder proceed with an unpinned
            selection, which is the state I12 forbids most directly.
        """
        self.assert_caller_allowed(OperationId.EMBEDDING_GET_ACTIVE_GENERATION, caller_module)
        with session_scope(self._engine) as connection:
            row = EmbeddingRepository(connection).active_generation(owner_id)
        if row is None:
            raise EmbeddingError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.EMBEDDING_GET_ACTIVE_GENERATION.value,
                    "resource_kind": "embedding_generation",
                },
            )
        return row.as_dict()

    def pin_generation(self, owner_id: str, *, caller_module: str) -> PinnedGeneration:
        """The build-snapshot read of ``selection.md`` §5.1, as a value the builder keeps."""
        self.assert_caller_allowed(OperationId.EMBEDDING_GET_ACTIVE_GENERATION, caller_module)
        with session_scope(self._engine) as connection:
            row = EmbeddingRepository(connection).active_generation(owner_id)
        if row is None:
            raise EmbeddingError(
                ErrorCode.NOT_FOUND,
                details_safe={
                    "operation_id": OperationId.EMBEDDING_GET_ACTIVE_GENERATION.value,
                    "resource_kind": "embedding_generation",
                },
            )
        return PinnedGeneration(fingerprint=row.fingerprint, pinned_at=self._clock())

    # -- embedding.start_generation_rebuild ---------------------------------------------

    def start_generation_rebuild(
        self,
        owner_id: str,
        *,
        caller_module: str,
        target_model_name: str,
        target_model_version: str,
        dimension: int,
        normalization: Normalization = Normalization.L2,
        expected_vector_count: int | None = None,
    ) -> dict[str, Any]:
        """``embedding.start_generation_rebuild`` -- create the ``building`` generation.

        Idempotency key: ``target_model_name + target_model_version`` (``ports.yaml``), rule
        "Cùng model mục tiêu không dựng hai generation song song". Two things implement it:

        1. a read, so the ordinary repeat returns the existing row cheaply;
        2. ``ux_embedding_generation_model``, so two *concurrent* commands cannot both insert.
           The loser catches the ``IntegrityError`` and re-reads -- card §6's "Hai lệnh rebuild
           đồng thời ⇒ một thắng", implemented as one winner rather than as a lock the second
           caller might not take.

        A repeat that asks for the same model with a **different** ``expected_vector_count``
        is ``IDEMPOTENCY_CONFLICT``: same key, different payload. Silently keeping the first
        target would make the activation guard answer a question nobody asked.

        The new generation is **not** made active here. ``selection.md`` §5.5: the old
        generation stays active for the whole rebuild, and only
        :meth:`activate_generation` moves the pointer.
        """
        self.assert_caller_allowed(OperationId.EMBEDDING_START_GENERATION_REBUILD, caller_module)
        self._assert_writable(OperationId.EMBEDDING_START_GENERATION_REBUILD)
        if dimension <= 0:
            raise EmbeddingError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": OperationId.EMBEDDING_START_GENERATION_REBUILD.value,
                    "field_path": "dimension",
                    "violation_kind": "out_of_range",
                    "limit_name": "dimension > 0",
                    "limit_value": 0,
                },
            )
        if target_model_version == "latest":
            raise EmbeddingError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "operation_id": OperationId.EMBEDDING_START_GENERATION_REBUILD.value,
                    "field_path": "model_version",
                    "violation_kind": "unpinned_version",
                },
            )
        idempotency_key = f"{target_model_name}\x1f{target_model_version}"
        with session_scope(self._engine) as connection:
            repository = EmbeddingRepository(connection)
            existing = repository.generation_by_model(
                owner_id,
                model_name=target_model_name,
                model_version=target_model_version,
                dimension=dimension,
                normalization=normalization,
            )
            if existing is not None:
                return self._replay_rebuild(existing, idempotency_key, expected_vector_count)
            created_at = self._clock()
            try:
                repository.insert_generation(
                    generation_id=self._new_id(),
                    owner_id=owner_id,
                    model_name=target_model_name,
                    model_version=target_model_version,
                    dimension=dimension,
                    normalization=normalization,
                    state=GenerationState.BUILDING,
                    expected_vector_count=expected_vector_count,
                    created_at=created_at,
                    activated_at=None,
                )
            except IntegrityError as exc:
                if not is_unique_violation(exc, distinguishing_column="model_name"):
                    raise
                connection.rollback()
                winner = EmbeddingRepository(connection).generation_by_model(
                    owner_id,
                    model_name=target_model_name,
                    model_version=target_model_version,
                    dimension=dimension,
                    normalization=normalization,
                )
                if winner is None:  # pragma: no cover - the index said it exists
                    raise
                return self._replay_rebuild(winner, idempotency_key, expected_vector_count)
            row = repository.generation_by_model(
                owner_id,
                model_name=target_model_name,
                model_version=target_model_version,
                dimension=dimension,
                normalization=normalization,
            )
            assert row is not None  # noqa: S101 - just inserted inside this transaction
            return row.as_dict()

    @staticmethod
    def _replay_rebuild(
        existing: GenerationRow, idempotency_key: str, expected_vector_count: int | None
    ) -> dict[str, Any]:
        """Return the existing generation, or refuse a same-key-different-payload repeat."""
        if (
            expected_vector_count is not None
            and existing.expected_vector_count is not None
            and expected_vector_count != existing.expected_vector_count
        ):
            raise EmbeddingError(
                ErrorCode.IDEMPOTENCY_CONFLICT,
                details_safe={
                    "idempotency_key": idempotency_key,
                    "payload_hash_seen": text_hash(str(expected_vector_count)),
                    "payload_hash_stored": text_hash(str(existing.expected_vector_count)),
                },
            )
        return existing.as_dict()

    # -- embedding.generate_vectors -----------------------------------------------------

    def generate_vectors(
        self,
        owner_id: str,
        *,
        caller_module: str,
        generation_id: str,
        requests: Sequence[VectorRequest],
    ) -> list[GeneratedVector]:
        """``embedding.generate_vectors`` -- embed texts into one named generation.

        The generation is an **argument**, never "whichever is active": a rebuild's whole
        purpose is to write vectors into the generation that is *not* active, and defaulting
        to the active one would quietly write the new model's output under the old
        generation's id -- the mixing I12 forbids, arrived at by convenience.

        The encoder's own ``(model_name, model_version, dimension, normalization)`` is checked
        against the target generation's before anything is embedded. A configured encoder that
        does not match the generation being built is ``EMBEDDING_GENERATION_MISMATCH``, not a
        silent re-labelling of its output.

        :raises EmbeddingError: ``NOT_FOUND`` for an unknown generation;
            ``EMBEDDING_GENERATION_MISMATCH`` when the encoder does not match it, or when the
            generation is ``retired``; ``STORAGE_WRITE_FAILED`` when the write fails.
        """
        self.assert_caller_allowed(OperationId.EMBEDDING_GENERATE_VECTORS, caller_module)
        self._assert_writable(OperationId.EMBEDDING_GENERATE_VECTORS)
        observed_at = self._clock()
        with session_scope(self._engine) as connection:
            repository = EmbeddingRepository(connection)
            generation = repository.generation(owner_id, generation_id)
            if generation is None:
                raise EmbeddingError(
                    ErrorCode.NOT_FOUND,
                    details_safe={
                        "operation_id": OperationId.EMBEDDING_GENERATE_VECTORS.value,
                        "resource_kind": "embedding_generation",
                    },
                )
            if generation.state is GenerationState.RETIRED:
                # Writing into a retired generation would grow a set that nothing may use
                # and that REQ-D48 keeps only as history.
                raise EmbeddingError(
                    ErrorCode.EMBEDDING_GENERATION_MISMATCH,
                    details_safe=generation.fingerprint.mismatch_details(generation.fingerprint),
                )
            self._assert_encoder_matches(generation)
            results = self._embed_into(repository, owner_id, generation, requests, observed_at)
            repository.set_built_vector_count(
                owner_id, generation.id, repository.count_vectors(owner_id, generation.id)
            )
        return results

    def _assert_encoder_matches(self, generation: GenerationRow) -> None:
        encoder_fingerprint = GenerationFingerprint(
            generation_id=generation.id,
            model_name=self._encoder.model_name,
            model_version=self._encoder.model_version,
            dimension=self._encoder.dimension,
            normalization=self._encoder.normalization,
        )
        assert_comparable(generation.fingerprint, encoder_fingerprint)

    def _embed_into(
        self,
        repository: EmbeddingRepository,
        owner_id: str,
        generation: GenerationRow,
        requests: Sequence[VectorRequest],
        observed_at: str,
    ) -> list[GeneratedVector]:
        pending: list[VectorRequest] = []
        stored: dict[tuple[SubjectType, str], Vector] = {}
        for request in requests:
            existing = repository.tag_vector(
                owner_id,
                subject_type=request.subject_type,
                subject_id=request.subject_id,
                generation=generation,
            )
            if existing is None:
                pending.append(request)
            else:
                stored[(request.subject_type, request.subject_id)] = existing

        encoded = (
            dict(
                zip(
                    pending,
                    (
                        Vector(fingerprint=generation.fingerprint, values=values)
                        for values in self._encoder.encode([item.text for item in pending])
                    ),
                    strict=True,
                )
            )
            if pending
            else {}
        )

        results: list[GeneratedVector] = []
        for request in requests:
            key = (request.subject_type, request.subject_id)
            if key in stored:
                results.append(
                    GeneratedVector(
                        subject_type=request.subject_type,
                        subject_id=request.subject_id,
                        idempotency_key=self._idempotency_key(request, generation),
                        vector=stored[key],
                        created=False,
                    )
                )
                continue
            vector = encoded[request]
            created = repository.upsert_tag_vector(
                vector_id=self._new_id(),
                owner_id=owner_id,
                subject_type=request.subject_type,
                subject_id=request.subject_id,
                generation=generation,
                vector=vector,
                observed_at=observed_at,
            )
            stored[key] = vector
            results.append(
                GeneratedVector(
                    subject_type=request.subject_type,
                    subject_id=request.subject_id,
                    idempotency_key=self._idempotency_key(request, generation),
                    vector=vector,
                    created=created,
                )
            )
        return results

    @staticmethod
    def _idempotency_key(request: VectorRequest, generation: GenerationRow) -> str:
        """``text_hash + model_name + model_version + generation`` (``ports.yaml``)."""
        return "\x1f".join(
            (
                text_hash(request.text),
                str(generation.model_name),
                str(generation.model_version),
                str(generation.id),
            )
        )

    # -- embedding.activate_generation --------------------------------------------------

    def activate_generation(
        self, owner_id: str, *, caller_module: str, generation_id: str
    ) -> dict[str, Any]:
        """``embedding.activate_generation`` -- ``TXN-activate``, one transaction, one CAS.

        Commit point: the single ``BEGIN…COMMIT`` opened here. Inside it, in order:

        1. read the target generation and the current active one;
        2. if the target is already active, return it unchanged -- ``ports.yaml``'s
           idempotency rule "Kích hoạt lại generation đã active không đổi trạng thái";
        3. recount the vectors and re-evaluate ``built >= expected`` on the recounted number,
           refusing with ``EMBEDDING_GENERATION_MISMATCH`` if it does not hold (fixture ``n``
           event 7: "THỬ chuyển active khi built (2) < expected (4) → BỊ TỪ CHỐI");
        4. retire the old, activate the new, guarded by
           ``ux_embedding_generation_active`` so that no observer ever sees zero or two.

        A refusal at step 3 commits nothing: the fixture's oracle for that event is "Từ chối
        KHÔNG đổi state của G1 hay G2; không có transaction nào commit", and raising before any
        UPDATE is issued is what makes that true rather than relying on a rollback.
        """
        self.assert_caller_allowed(OperationId.EMBEDDING_ACTIVATE_GENERATION, caller_module)
        self._assert_writable(OperationId.EMBEDDING_ACTIVATE_GENERATION)
        activated_at = self._clock()
        with session_scope(self._engine) as connection:
            repository = EmbeddingRepository(connection)
            target = repository.generation(owner_id, generation_id)
            if target is None:
                raise EmbeddingError(
                    ErrorCode.NOT_FOUND,
                    details_safe={
                        "operation_id": OperationId.EMBEDDING_ACTIVATE_GENERATION.value,
                        "resource_kind": "embedding_generation",
                    },
                )
            if target.state is GenerationState.ACTIVE:
                return target.as_dict()
            if target.state is GenerationState.RETIRED:
                raise EmbeddingError(
                    ErrorCode.VALIDATION_ERROR,
                    details_safe={
                        "operation_id": OperationId.EMBEDDING_ACTIVATE_GENERATION.value,
                        "field_path": "state",
                        "violation_kind": "retired_generation",
                    },
                )
            current = repository.active_generation(owner_id)
            built = repository.count_vectors(owner_id, target.id)
            repository.set_built_vector_count(owner_id, target.id, built)
            if not coverage_satisfied(built=built, expected=target.expected_vector_count):
                raise EmbeddingError(
                    ErrorCode.EMBEDDING_GENERATION_MISMATCH,
                    details_safe={
                        "expected_generation_id": current.id if current else None,
                        "seen_generation_id": target.id,
                        "dimension_expected": current.dimension if current else None,
                        "dimension_seen": target.dimension,
                    },
                )
            repository.swap_active(
                owner_id=owner_id,
                from_generation_id=current.id if current is not None else None,
                to_generation_id=target.id,
                activated_at=activated_at,
            )
            activated = repository.generation(owner_id, target.id)
            assert activated is not None  # noqa: S101 - updated inside this transaction
            return activated.as_dict()

    # -- the predicate PC03's publish CAS calls ------------------------------------------

    def embedding_generation_matches(
        self, owner_id: str, expected_embedding_generation_id: str
    ) -> bool:
        """``contracts/reporting/time-and-tags.md`` §4.5, check 3 of the publish CAS.

        True when the currently active generation is the one the build pinned **and** its
        dimension is unchanged. Pure: it reads committed state, writes nothing and calls no
        network, as ``contracts/state/report.yaml`` ``ownership_boundary`` requires of all
        three predicates it asks PC04 for.

        Returning ``False`` (rather than raising) is deliberate -- the CAS runs six checks in
        a fixed order and maps each failure to its own code; a predicate that raised would
        take that mapping away from the transaction that owns it.
        """
        with session_scope(self._engine) as connection:
            active = EmbeddingRepository(connection).active_generation(owner_id)
        return active is not None and active.id == expected_embedding_generation_id

    # -- the selection guard -------------------------------------------------------------

    @staticmethod
    def assert_selection_uses_one_generation(
        pinned: PinnedGeneration,
        candidates: Iterable[Vector],
        *,
        ledger: ComparisonLedger | None = None,
    ) -> None:
        """``selection.md`` §5.2-5.3: every candidate vector belongs to the pinned generation.

        Runs **before** scoring, so a mixed candidate set is refused while the builder is
        still assembling inputs -- which is what fixture ``l`` means by "selection bị chặn
        TRƯỚC report commit", and why the ledger it instruments records zero performed
        comparisons for that run rather than a few before the guard noticed.
        """
        assert_single_generation(
            (candidate.fingerprint for candidate in candidates),
            expected=pinned.fingerprint,
            ledger=ledger,
        )
