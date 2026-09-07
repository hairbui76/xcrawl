"""``MOD-embedding-service`` -- generations, vectors, and the one comparison that may happen.

This module is pure: no database handle, no clock, no network. It holds the three things
invariant **I12** is made of, so that they can be asserted without a database and reused by
the report builder when ``TC-report-coverage-publish-cas`` lands.

I12, quoted from card §6
------------------------
    vector khác model/generation/dimension không được so sánh trong cùng một lần selection

The obvious implementation is a check inside the report builder. That is the implementation
this module deliberately does **not** offer, because a check the caller can forget is a
check that will be forgotten: the negative fixture
``acceptance/fixtures/reporting/l-embedding-generation-switch-blocked.json`` asserts
*"cosine comparisons between EMB and EMB2 vectors": 0*, which is a statement about what the
similarity function was ever asked to do, not about what a builder remembered to guard.

So the arithmetic is not reachable except through :func:`cosine`, and :func:`cosine` refuses
before multiplying. There is no unguarded dot product in this package to call by mistake.

The three parts
---------------
:class:`GenerationFingerprint`
    ``(generation_id, model_name, model_version, dimension, normalization)``. Two vectors are
    comparable **iff** their fingerprints are equal -- all five components, not just the id.
    ``contracts/reporting/selection.md`` §5 forbids comparing across a different
    ``embedding_generation_id``, a different ``dimension``, a different ``model_name`` *or* a
    different ``normalization``, and the fingerprint is that sentence as a value.

:class:`ComparisonLedger`
    The instrument fixture ``n-…-positive.json`` asks for in as many words: *"Một bộ đếm bọc
    quanh hàm similarity, ghi lại (generation_a, generation_b) của MỌI phép cosine. Oracle
    chính của SC52 đọc bộ đếm này."* It counts what was **performed** separately from what
    was **refused**, because a design that refuses everything and a design that compares
    everything both produce zero cross-generation comparisons if you only count one of them.

:func:`cosine`
    Guard, then arithmetic, then round to 4 decimal places -- the rounding
    ``contracts/reporting/selection.md`` §3 writes into the score formula, applied here so
    that two callers cannot round differently and disagree about a threshold.

The encoder port
----------------
``REQ-D48``/``REQ-D50`` and ``contracts/modules.yaml`` (``network_egress: []`` for this
module) say embedding runs on a **local** model with no API and no CLI. :class:`LocalEncoder`
is that port. Two implementations ship:

* :class:`SentenceTransformersEncoder` -- the adapter ADR-0011 names. It imports
  ``sentence_transformers`` lazily and is never constructed by a test, because
  ``server/pyproject.toml`` declares that dependency as an **optional extra that CI does not
  install** and states "No model is ever downloaded by this repo's test or CI paths". The
  concrete model is ``REQ-OQ09``/``REQ-A3``, still open, so this class takes the model name,
  version and dimension from its caller and chooses nothing (card §10 ``SG-01``).
* :class:`DeterministicHashEncoder` -- an offline stand-in with stable output, for the
  fixtures. It is **not** a model and must never be configured in a deployment; it exists so
  that the generation machinery can be proven without pretending a model was evaluated. The
  real-model dimension check is reported ``NOT_RUN`` in this card's evidence manifest.
"""

from __future__ import annotations

import hashlib
import importlib
import math
import struct
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode

#: ``contracts/reporting/selection.md`` §3: every score is rounded to four decimals before
#: it meets a threshold. One place, so two callers cannot disagree at the boundary.
SCORE_DECIMALS: int = 4

#: ``struct`` format for one vector component. ``<`` little-endian, ``d`` IEEE 754 binary64:
#: a fixed 8 bytes per component, so ``length(blob) // 8`` is the dimension and the
#: contract's "độ dài phải khớp `embedding_generation.dimension`" is checkable on the row.
_COMPONENT = "<d"
COMPONENT_BYTES: int = struct.calcsize(_COMPONENT)


# --------------------------------------------------------------------------------------
# Errors -- contracts/errors.yaml, never a string literal
# --------------------------------------------------------------------------------------

#: ``message_safe_template_vi`` of the seven codes this module may raise: the five of card §7
#: plus the two the boundary table of card §5 (ruling R5-01) assigns to a refused call. The
#: templates carry no substitutions -- the envelope forbids interpolating anything that is
#: not a ``details_safe`` key, and none of these codes has a key worth showing a person.
MESSAGE_SAFE: dict[ErrorCode, str] = {
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: (
        "Dữ liệu vector đang chuyển thế hệ nên chưa dựng được báo cáo."
    ),
    ErrorCode.VALIDATION_ERROR: "Dữ liệu gửi lên không hợp lệ.",
    ErrorCode.IDEMPOTENCY_CONFLICT: "Yêu cầu trùng khóa nhưng nội dung khác với lần đã ghi nhận.",
    ErrorCode.NOT_FOUND: "Không tìm thấy mục bạn yêu cầu.",
    ErrorCode.STORAGE_WRITE_FAILED: (
        "Hệ thống tạm thời không ghi được dữ liệu. Đã dừng nhận việc mới."
    ),
    ErrorCode.FORBIDDEN_EDGE: "Đường gọi này không được phép.",
    ErrorCode.CAPABILITY_DENIED: "Thao tác bị chặn ở mức nền tảng.",
}

#: ``details_safe_keys`` of the same five codes, verbatim from ``contracts/errors.yaml``.
#: Anything outside the set for a code is dropped before the envelope leaves the process --
#: the envelope's own rule makes an unknown key a producer-side defect, so leaking it would
#: be the worse failure. Note what is **absent** from
#: ``EMBEDDING_GENERATION_MISMATCH``: there is no key for a vector count, which is why the
#: coverage refusal reports the two generation ids and not the two counters.
DETAILS_SAFE_KEYS: dict[ErrorCode, frozenset[str]] = {
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: frozenset(
        {"expected_generation_id", "seen_generation_id", "dimension_expected", "dimension_seen"}
    ),
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.IDEMPOTENCY_CONFLICT: frozenset(
        {"idempotency_key", "payload_hash_seen", "payload_hash_stored"}
    ),
    ErrorCode.NOT_FOUND: frozenset({"operation_id", "resource_kind"}),
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"caller_module", "callee_module", "forbidden_edge_ref"}),
    ErrorCode.CAPABILITY_DENIED: frozenset(
        {"module_id", "denied_capability_kind", "forbidden_edge_ref"}
    ),
}

#: ``contracts/errors.yaml`` §VALIDATION_ERROR is the only one of the five with an HTTP
#: status in card §7 ("400"). The rest are ``internal`` operations with no HTTP path
#: (``contracts/ports.yaml``: all four ``embedding.*`` are ``transport: internal``), so this
#: map exists for the day a caller does surface one and not because a route uses it today.
_HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.IDEMPOTENCY_CONFLICT: 409,
    ErrorCode.EMBEDDING_GENERATION_MISMATCH: 409,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.CAPABILITY_DENIED: 403,
}


class EmbeddingError(Exception):
    """An error from ``MOD-embedding-service``, carrying a registered code.

    The code is an :class:`~rr_contracts.generated.errors.ErrorCode` member rather than a
    string, so a code the registry does not declare cannot be raised, and ``details_safe`` is
    filtered against that code's ``details_safe_keys`` here rather than at each call site.
    Nothing in an envelope from this module ever carries a vector: ``errors.yaml``
    ``EMBEDDING_GENERATION_MISMATCH.redaction_vi`` says "Không xuất giá trị vector", and the
    key filter is what makes that true by construction.
    """

    def __init__(
        self,
        code: ErrorCode,
        *,
        details_safe: Mapping[str, Any] | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        permitted = DETAILS_SAFE_KEYS[code]
        self.code = code
        self.details_safe: dict[str, Any] = {
            key: value for key, value in (details_safe or {}).items() if key in permitted
        }
        self.retry_after_ms = retry_after_ms
        self.message_safe = MESSAGE_SAFE[code]
        super().__init__(f"{code.value}: {self.message_safe}")

    @property
    def http_status(self) -> int:
        return _HTTP_STATUS[self.code]

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """The envelope of ``contracts/errors.yaml`` → ``error_envelope`` (card §7).

        ``scope`` and ``retry_class`` are read from the generated maps, never passed in, so a
        caller cannot hand out a retry policy the contract did not grant.
        """
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
            "retry_after_ms": self.retry_after_ms,
        }


# --------------------------------------------------------------------------------------
# Enums -- the closed value sets of contracts/data/entities.yaml
# --------------------------------------------------------------------------------------


class GenerationState(str, Enum):
    """``embedding_generation.state``: ``building | active | retired``.

    ``retired`` is not ``deleted``. ``REQ-D48`` keeps the old generation and all of its
    vectors after a switch so that published reports stay readable (``REQ-S7.3-03``), and
    fixture ``n-…-positive.json`` asserts the G1 rows survive.
    """

    BUILDING = "building"
    ACTIVE = "active"
    RETIRED = "retired"


class Normalization(str, Enum):
    """``embedding_generation.normalization``: ``l2 | none``.

    ``contracts/reporting/selection.md`` §3.1: under ``l2`` the vectors are unit length and
    cosine is the dot product; under ``none`` the denominators are computed. Part of the
    fingerprint because two generations that normalise differently produce scores on
    different scales even with the same model.
    """

    L2 = "l2"
    NONE = "none"


class SubjectType(str, Enum):
    """``tag_vector.subject_type``: ``tag | tag_alias | tag_exclusion``."""

    TAG = "tag"
    TAG_ALIAS = "tag_alias"
    TAG_EXCLUSION = "tag_exclusion"


# --------------------------------------------------------------------------------------
# The fingerprint and the vector
# --------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class GenerationFingerprint:
    """Everything that has to match before two vectors may be compared.

    Frozen and hashable so that "how many distinct generations did this selection touch?" is
    a set operation rather than a code review.
    """

    generation_id: str
    model_name: str
    model_version: str
    dimension: int
    normalization: Normalization

    def mismatch_details(self, other: GenerationFingerprint) -> dict[str, Any]:
        """``details_safe`` for a refusal between ``self`` (expected) and ``other`` (seen)."""
        return {
            "expected_generation_id": self.generation_id,
            "seen_generation_id": other.generation_id,
            "dimension_expected": self.dimension,
            "dimension_seen": other.dimension,
        }


@dataclass(frozen=True, slots=True)
class Vector:
    """One embedding, inseparable from the generation that produced it.

    The pairing is the point: a bare ``list[float]`` can be handed to any arithmetic, and
    ``tag_vector``/``work_label.vector`` rows are just blobs, so the generation id would
    survive only as a convention. Here it survives as a field, and :func:`cosine` reads it.
    """

    fingerprint: GenerationFingerprint
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if len(self.values) != self.fingerprint.dimension:
            raise EmbeddingError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "field_path": "vector",
                    "violation_kind": "dimension_mismatch",
                    "limit_name": "embedding_generation.dimension",
                    "limit_value": self.fingerprint.dimension,
                },
            )

    def to_blob(self) -> bytes:
        """Little-endian float64 per component -- the ``blob`` of ``ENT-tag-vector``."""
        return struct.pack(f"<{len(self.values)}d", *self.values)

    @classmethod
    def from_blob(cls, blob: bytes, fingerprint: GenerationFingerprint) -> Vector:
        """Inverse of :meth:`to_blob`, refusing a blob whose length is not the dimension.

        This is where ``entities.yaml``'s "Độ dài phải khớp ``embedding_generation.dimension``"
        is enforced on the way out of the database. SQLite cannot express it as a CHECK --
        the length lives in another table -- so it is enforced on both edges of the row
        instead of being assumed.
        """
        if len(blob) != fingerprint.dimension * COMPONENT_BYTES:
            raise EmbeddingError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "field_path": "tag_vector.vector",
                    "violation_kind": "blob_length_mismatch",
                    "limit_name": "embedding_generation.dimension",
                    "limit_value": fingerprint.dimension,
                },
            )
        count = len(blob) // COMPONENT_BYTES
        return cls(fingerprint=fingerprint, values=struct.unpack(f"<{count}d", blob))


# --------------------------------------------------------------------------------------
# The instrument
# --------------------------------------------------------------------------------------


@dataclass
class ComparisonLedger:
    """Every similarity call, split into performed and refused.

    ``performed`` is the oracle of SC52 and of fixture ``l``: the number of *(generation_a,
    generation_b)* pairs with ``a != b`` must be zero over a whole run. ``refused`` is the
    other half of the same claim -- an implementation that blocks every build also scores
    zero cross-generation comparisons, and only the two counters together tell the two apart
    (``contracts/reporting/selection.md`` §5: *"một mình O-5a không loại trừ được một triển
    khai chặn mọi thứ"*).
    """

    performed: Counter[tuple[str, str]] = field(default_factory=Counter)
    refused: Counter[tuple[str, str]] = field(default_factory=Counter)

    def record_performed(self, a: GenerationFingerprint, b: GenerationFingerprint) -> None:
        self.performed[(a.generation_id, b.generation_id)] += 1

    def record_refused(self, a: GenerationFingerprint, b: GenerationFingerprint) -> None:
        self.refused[(a.generation_id, b.generation_id)] += 1

    @property
    def total_performed(self) -> int:
        return sum(self.performed.values())

    @property
    def total_refused(self) -> int:
        return sum(self.refused.values())

    @property
    def cross_generation_performed(self) -> int:
        """**The** number fixture ``l`` and fixture ``n`` both pin to ``0``."""
        return sum(count for (a, b), count in self.performed.items() if a != b)

    @property
    def generations_touched(self) -> frozenset[str]:
        """Every generation id that took part in a performed comparison."""
        return frozenset(gen for pair in self.performed for gen in pair)


# --------------------------------------------------------------------------------------
# The guard and the one comparison
# --------------------------------------------------------------------------------------


def assert_comparable(
    expected: GenerationFingerprint,
    seen: GenerationFingerprint,
    *,
    ledger: ComparisonLedger | None = None,
) -> None:
    """Refuse unless all five components of the two fingerprints agree.

    :raises EmbeddingError: ``EMBEDDING_GENERATION_MISMATCH``.

    Called before any arithmetic, and called by the selection guard before a candidate set is
    scored at all -- ``selection.md`` §5.3 forbids the three tempting escapes explicitly:
    falling back to the old generation for the vectors that are missing in the new one,
    skipping the tag that is missing, and mixing. All three are "do something reasonable
    with a partial generation", and all three are refusals here.
    """
    if expected == seen:
        return
    if ledger is not None:
        ledger.record_refused(expected, seen)
    raise EmbeddingError(
        ErrorCode.EMBEDDING_GENERATION_MISMATCH,
        details_safe=expected.mismatch_details(seen),
    )


def cosine(a: Vector, b: Vector, *, ledger: ComparisonLedger | None = None) -> float:
    """Cosine similarity between two vectors of the **same** generation, rounded to 4 dp.

    :raises EmbeddingError: ``EMBEDDING_GENERATION_MISMATCH`` if the two fingerprints differ,
        raised **before** any multiplication, so a refused pair contributes nothing to
        :attr:`ComparisonLedger.performed`.

    ``selection.md`` §3.1: with ``normalization = 'l2'`` the vectors are unit length and the
    cosine is the dot product. That shortcut is *not* taken here -- the denominators are
    computed either way -- because "the vectors are unit length" is a property of a model
    that has not been chosen yet (``REQ-OQ09``), and a shortcut that is wrong when the
    premise is wrong fails silently, by returning a plausible number.
    """
    assert_comparable(a.fingerprint, b.fingerprint, ledger=ledger)
    if ledger is not None:
        ledger.record_performed(a.fingerprint, b.fingerprint)
    dot = math.fsum(x * y for x, y in zip(a.values, b.values, strict=True))
    norm_a = math.sqrt(math.fsum(x * x for x in a.values))
    norm_b = math.sqrt(math.fsum(y * y for y in b.values))
    if norm_a == 0.0 or norm_b == 0.0:
        # A zero vector has no direction, so it has no cosine. Returning 0.0 would read as
        # "measured, and dissimilar"; the fixtures forbid exactly that confusion for the
        # NULL case ("Coi vector NULL là điểm tương đồng 0" is a forbidden effect), and the
        # same reasoning applies to a degenerate vector.
        raise EmbeddingError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "field_path": "vector",
                "violation_kind": "zero_norm",
            },
        )
    return round(dot / (norm_a * norm_b), SCORE_DECIMALS)


def assert_single_generation(
    fingerprints: Iterable[GenerationFingerprint],
    *,
    expected: GenerationFingerprint,
    ledger: ComparisonLedger | None = None,
) -> None:
    """The whole-selection guard of ``selection.md`` §5: one generation, or nothing.

    Every candidate vector in one selection is checked against the pinned generation
    **before** scoring starts, which is what makes the negative fixture's *"selection bị chặn
    TRƯỚC report commit"* true: the refusal happens while the builder is still assembling its
    inputs, long before a publish transaction opens.

    :raises EmbeddingError: ``EMBEDDING_GENERATION_MISMATCH`` at the first stranger.
    """
    for fingerprint in fingerprints:
        assert_comparable(expected, fingerprint, ledger=ledger)


def coverage_satisfied(*, built: int, expected: int | None) -> bool:
    """``entities.yaml``: "Guard chuyển active: built >= expected".

    ``expected is None`` answers **False**, not True. ``contracts/ports.yaml``
    ``embedding.activate_generation`` takes "generation_id + bằng chứng đã đủ vector"; a
    generation that never recorded how many vectors it needs has not produced that evidence,
    and treating an absent target as a satisfied one would make the guard vacuous for exactly
    the rows most likely to be half-built.
    """
    return expected is not None and built >= expected


# --------------------------------------------------------------------------------------
# The local encoder port (REQ-D48 / REQ-D50: local model, no API, no CLI)
# --------------------------------------------------------------------------------------


@runtime_checkable
class LocalEncoder(Protocol):
    """A local embedding model. No network, no API key, no subprocess.

    ``contracts/modules.yaml`` gives ``MOD-embedding-service`` ``network_egress: []`` and
    ``secret_access: none``; ``NC-25``/``FE-22`` make a call from here to
    ``EXT-ai-provider-api`` a ``CAPABILITY_DENIED``. That is the whole reason ``AC-16`` ("the
    no-API-key flow still completes") stands, so this port has no place to put a base URL or
    a credential -- not as a convenience, as the enforcement.
    """

    @property
    def model_name(self) -> str: ...

    @property
    def model_version(self) -> str: ...

    @property
    def dimension(self) -> int: ...

    @property
    def normalization(self) -> Normalization: ...

    def encode(self, texts: Sequence[str]) -> list[tuple[float, ...]]:
        """One vector per input text, in input order."""


@dataclass(frozen=True, slots=True)
class DeterministicHashEncoder:
    """An offline stand-in: SHA-256 of the text, expanded to ``dimension`` components.

    **This is not a model.** It exists because ``REQ-OQ09`` (which embedding model) is still
    open behind ``REQ-A3``, and card §10 ``SG-01``/``SG-STACK`` forbid choosing one here. What
    the fixtures actually need from an encoder is that it be a *function* -- same text and
    same generation produce the same vector, different generations produce different ones --
    and that is what this provides, deterministically and without a download.

    It carries no semantics whatsoever: two texts about the same subject are as far apart as
    two unrelated ones. Any similarity threshold measured with it would be meaningless, which
    is why this card's evidence records the real-model checks as ``NOT_RUN`` rather than
    reporting a number this class produced.
    """

    model_name: str
    model_version: str
    dimension: int
    normalization: Normalization = Normalization.L2

    def encode(self, texts: Sequence[str]) -> list[tuple[float, ...]]:
        return [self._one(text) for text in texts]

    def _one(self, text: str) -> tuple[float, ...]:
        seed = f"{self.model_name}\x1f{self.model_version}\x1f{text}".encode()
        raw: list[float] = []
        counter = 0
        while len(raw) < self.dimension:
            digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
            for offset in range(0, len(digest), 2):
                if len(raw) == self.dimension:
                    break
                # Two bytes -> a value in [-1, 1); enough spread for a deterministic fixture.
                raw.append(int.from_bytes(digest[offset : offset + 2], "big") / 32768.0 - 1.0)
            counter += 1
        if self.normalization is Normalization.NONE:
            return tuple(raw)
        norm = math.sqrt(math.fsum(value * value for value in raw)) or 1.0
        return tuple(value / norm for value in raw)


@dataclass(frozen=True, slots=True)
class SentenceTransformersEncoder:
    """The ADR-0011 adapter: ``sentence-transformers``, loaded from a **local** artifact.

    ``server/pyproject.toml`` declares ``sentence-transformers`` under the ``embedding``
    extra and states, as a rule and not as an observation, that CI does not install it and
    that no model is downloaded by any test path. ``contracts/modules.yaml`` says the same
    thing about the deployment: "Model được nạp từ artifact cục bộ trên server, không tải về
    lúc chạy."

    So this class takes ``model_path`` -- a path on disk -- rather than a model *name* that a
    library would resolve by fetching it. ``model_name``, ``model_version`` and ``dimension``
    are supplied by the caller because they are contract data (they end up in
    ``embedding_generation`` and in every report), and because choosing them is ``REQ-OQ09``,
    which is not this card's to answer.

    Nothing in this repository constructs one. It is here so that the port has a real
    implementation on the day a model is chosen, and so that the shape of that day's change
    is "configure a path", not "rewrite the service".
    """

    model_path: str
    model_name: str
    model_version: str
    dimension: int
    normalization: Normalization = Normalization.L2

    def encode(self, texts: Sequence[str]) -> list[tuple[float, ...]]:
        model = self._load()
        vectors = model.encode(
            list(texts),
            normalize_embeddings=self.normalization is Normalization.L2,
            convert_to_numpy=False,
        )
        return [tuple(float(component) for component in vector) for vector in vectors]

    def _load(self) -> Any:
        """Import the optional dependency at call time, or refuse.

        ``importlib`` rather than a plain ``import`` statement, and the reason is not style:
        ``server/pyproject.toml`` puts ``sentence-transformers`` behind an extra that
        ``uv sync`` does **not** install, so the module genuinely is not on the path of the
        environment that type-checks and tests this repository. A static ``import`` would
        make ``mypy --strict`` fail on a dependency the toolchain deliberately excludes, and
        the usual fix -- a blanket ``ignore_missing_imports`` in ``pyproject.toml`` -- would
        silence that class of error for every module, not just this one.
        """
        try:
            module = importlib.import_module("sentence_transformers")
        except ImportError as exc:  # pragma: no cover - the extra is not installed in CI
            raise EmbeddingError(
                ErrorCode.VALIDATION_ERROR,
                details_safe={
                    "field_path": "encoder",
                    "violation_kind": "optional_dependency_absent",
                    "limit_name": "server[embedding]",
                },
            ) from exc
        # `local_files_only` is the enforcement of FE-22 at the library boundary: a missing
        # artifact must fail loudly, never turn into a download.
        return module.SentenceTransformer(self.model_path, local_files_only=True)
