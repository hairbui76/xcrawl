"""The analysis key -- ADR-0008, ``ENT-analysis.analysis_key``.

One idea, and every property of this card follows from it: **the key of an analysis result
is a function of seven things, and a tag is not one of them.**

    owner_id · target_key · task_type · source_fingerprint ·
    prompt_version · schema_version · generation_number

``ENT-analysis.analysis_key.excluded_deliberately`` names what is left out and why:

``tag`` / ``tag_config_version``
    Removing and re-adding a tag must not call the model again (REQ-AC06, I04). The
    subscription layer and the labelling layer are separate (SRC-SPEC §8.1); if a tag were in
    the key, every tag edit would mint a new key, and the "provider call counter delta = 0"
    oracle of AC-06 would be unsatisfiable by construction rather than by mistake.
``provider`` / ``model``
    Switching provider does not invalidate a committed result; the old one stands until the
    Owner asks for reanalysis (ADR-0008 §6). Both are recorded on the row as metadata.
``report_id``
    One analysis is reused across reporting periods.

Because "a tag is not in the key" is the whole point, it is enforced rather than documented:
:func:`analysis_key_from_inputs` raises on any of the excluded names instead of quietly
ignoring it. A future edit that starts threading a tag into key construction fails loudly at
the call site rather than silently re-pricing the corpus.

Canonicalisation
----------------
``entities.yaml`` §conventions/hashes fixes the format (``sha256:`` + 64 lowercase hex) and
the canonicalisation (RFC 8785 / JCS, UTF-8, no BOM). The serialiser is defined here rather
than imported from ``server.app.ingest``: that package belongs to ``MOD-ingest-service`` and
``contracts/modules.yaml`` has no ``MOD-analysis-service -> MOD-ingest-service`` edge, so an
import in that direction would be a dependency the registry does not grant (ENF-import-rule).
The known limitation is the same one ingest records: :func:`json.dumps` with ``sort_keys``
orders by code point rather than by UTF-16 code unit, which differs only for keys above
U+FFFF -- every key in these contracts is ASCII.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

#: ``ENT-analysis.analysis_key.components``, in contract order. The tuple is the single
#: source of the field order used for hashing and for wire comparison (SV-01).
ANALYSIS_KEY_COMPONENTS: tuple[str, ...] = (
    "owner_id",
    "target_key",
    "task_type",
    "source_fingerprint",
    "prompt_version",
    "schema_version",
    "generation_number",
)

#: Names that must never reach key construction. Every one of them is a real field somewhere
#: in the schema, which is exactly why the guard exists: they are plausible, and each would
#: break a different contract promise (I04/REQ-AC06 for the tag family, ADR-0008 §6 for the
#: provider family, "reused across periods" for the report family).
EXCLUDED_FROM_ANALYSIS_KEY: frozenset[str] = frozenset(
    {
        "tag",
        "tags",
        "tag_id",
        "tag_ids",
        "tag_text",
        "tag_config_version",
        "tag_config_version_id",
        "matched_tags",
        "provider",
        "provider_name",
        "provider_config_id",
        "auth_family",
        "model",
        "model_name",
        "report_id",
        "report_build_id",
        "report_item_id",
    }
)

#: ``ENT-analysis.task_type`` -- authoritative spelling (ruling R-03 / CR-PC03-05).
TASK_TYPES: frozenset[str] = frozenset({"label", "summary", "direction_phrasing"})

_HASH_PREFIX = "sha256:"


class AnalysisKeyError(ValueError):
    """A key could not be built from the values given.

    A ``ValueError`` and not a contract error code: this is a programming fault inside the
    server (a caller tried to put a tag in the key), not something a client did. The service
    layer never turns it into a 4xx.
    """


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
    return f"{_HASH_PREFIX}{hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()}"


@dataclass(frozen=True)
class AnalysisKey:
    """The seven components, immutable.

    Frozen because a key that could be mutated after a uniqueness check is a key that can
    disagree with the row it was checked against.
    """

    owner_id: str
    target_key: str
    task_type: str
    source_fingerprint: str
    prompt_version: str
    schema_version: str
    generation_number: int

    def __post_init__(self) -> None:
        if self.task_type not in TASK_TYPES:
            raise AnalysisKeyError(f"task_type must be one of {sorted(TASK_TYPES)}")
        if self.generation_number < 1:
            raise AnalysisKeyError("generation_number is >= 1 (ENT-analysis-generation)")
        if not self.source_fingerprint.startswith(_HASH_PREFIX):
            raise AnalysisKeyError("source_fingerprint is a `sha256:` hash (entities.yaml)")

    def as_dict(self) -> dict[str, Any]:
        """The seven components as the wire object of ``analysis-result.schema.json``."""
        return {name: getattr(self, name) for name in ANALYSIS_KEY_COMPONENTS}

    def digest(self) -> str:
        """``sha256(JCS(components))`` -- a single comparable value for the whole key.

        Used as the idempotency key of ``analysis.enqueue_tasks`` (``contracts/ports.yaml``:
        "cùng analysis_key không tạo task trùng"). It is a derived convenience: the
        authoritative uniqueness arbiter is still the partial UNIQUE index
        ``ux_analysis_valid_key``, which is stated over the seven columns themselves.
        """
        return sha256_of(self.as_dict())

    def with_generation(self, generation_number: int) -> AnalysisKey:
        """The same target and task at a new generation (T-AN-12).

        Reanalysis is not a transition of the old item: it is a *different key*, which is
        why it does not collide with ``ux_analysis_valid_key`` and does not break I04.
        """
        return AnalysisKey(**{**self.as_dict(), "generation_number": generation_number})

    def same_key_ignoring_generation(self, other: AnalysisKey) -> bool:
        """Whether two keys differ only in ``generation_number``."""
        mine = self.as_dict()
        theirs = other.as_dict()
        del mine["generation_number"], theirs["generation_number"]
        return mine == theirs


def analysis_key_from_inputs(
    *,
    owner_id: str,
    target_key: str,
    task_type: str,
    source_fingerprint: str,
    prompt_version: str,
    schema_version: str,
    generation_number: int,
    extra: Mapping[str, Any] | None = None,
) -> AnalysisKey:
    """Build a key, refusing anything ``ENT-analysis`` excludes on purpose.

    ``extra`` exists to be rejected. Callers that hold a bag of "everything about this
    target" pass it here and find out immediately if it carries a tag, a provider or a
    report id; the alternative -- silently dropping them -- is how a tag ends up in a key
    two refactors later without anyone noticing.

    :raises AnalysisKeyError: if ``extra`` names any member of
        :data:`EXCLUDED_FROM_ANALYSIS_KEY`.
    """
    offending = sorted(set(extra or {}) & EXCLUDED_FROM_ANALYSIS_KEY)
    if offending:
        raise AnalysisKeyError(
            "these fields are excluded from the analysis key by ENT-analysis"
            f".analysis_key.excluded_deliberately: {offending}"
        )
    return AnalysisKey(
        owner_id=owner_id,
        target_key=target_key,
        task_type=task_type,
        source_fingerprint=source_fingerprint,
        prompt_version=prompt_version,
        schema_version=schema_version,
        generation_number=generation_number,
    )


def analysis_key_from_mapping(mapping: Mapping[str, Any]) -> AnalysisKey:
    """Parse the ``analysis_key`` object of a submitted result.

    Unknown members are rejected rather than ignored, so a worker cannot smuggle an eighth
    component past the comparison SV-01 performs.
    """
    unknown = sorted(set(mapping) - set(ANALYSIS_KEY_COMPONENTS))
    if unknown:
        raise AnalysisKeyError(
            f"analysis_key carries fields the contract does not define: {unknown}"
        )
    missing = sorted(set(ANALYSIS_KEY_COMPONENTS) - set(mapping))
    if missing:
        raise AnalysisKeyError(f"analysis_key is missing components: {missing}")
    return AnalysisKey(
        owner_id=str(mapping["owner_id"]),
        target_key=str(mapping["target_key"]),
        task_type=str(mapping["task_type"]),
        source_fingerprint=str(mapping["source_fingerprint"]),
        prompt_version=str(mapping["prompt_version"]),
        schema_version=str(mapping["schema_version"]),
        generation_number=int(mapping["generation_number"]),
    )


def compute_source_fingerprint(
    *,
    work_version_content_fingerprint: str | None = None,
    post_source_snapshot_hashes: Sequence[str] = (),
) -> str:
    """``ENT-analysis.source_fingerprint``.

    "sha256 của JCS đầu vào đã dùng: ``{work_version.content_fingerprint?,
    post.source_snapshot_hash[]}``. Đổi nội dung nguồn ⇒ đổi key."

    The post hashes are sorted before hashing: the fingerprint must describe *which sources
    were read*, not the order a particular query happened to return them in, or the same
    inputs would produce two keys and the model would run twice for one piece of work.

    The work-version member is present-or-absent rather than ``None``-valued for the same
    reason a JSON schema distinguishes the two: "no work version was available" and "a work
    version with a null fingerprint" are different inputs and must not hash alike.
    """
    material: dict[str, Any] = {"post_source_snapshot_hashes": sorted(post_source_snapshot_hashes)}
    if work_version_content_fingerprint is not None:
        material["work_version_content_fingerprint"] = work_version_content_fingerprint
    return sha256_of(material)


def target_key(kind: str, identifier: str) -> str:
    """``target_kind || ':' || id`` -- the union key of ``contracts/schemas/target.schema.json``."""
    if kind not in ("work", "post"):
        raise AnalysisKeyError("target_kind is `work` or `post`")
    return f"{kind}:{identifier}"


__all__ = [
    "ANALYSIS_KEY_COMPONENTS",
    "EXCLUDED_FROM_ANALYSIS_KEY",
    "TASK_TYPES",
    "AnalysisKey",
    "AnalysisKeyError",
    "analysis_key_from_inputs",
    "analysis_key_from_mapping",
    "canonical_json",
    "compute_source_fingerprint",
    "sha256_of",
    "target_key",
]
