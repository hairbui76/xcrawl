"""Steps 2 and 3 of ``contracts/ai/tasks.yaml`` §4 — schema, then the seven SV checks.

The sentence this module exists to make true is ``tasks.yaml`` §1 ``adapter_contract_vi``:
**"JSON đúng schema" is not the whole contract.** A payload that satisfies
``analysis-result.schema.json`` may still cite a source the model was never given, claim an
evidence level higher than the sources support, or quietly re-pick the members of an
emerging direction. JSON Schema cannot express any of those, because each of them is a
comparison against the *task input*, which the schema never sees.

So there are two functions and they are deliberately separate:

* :func:`schema_violations` — validated against the schema **file**, not against the
  generated Pydantic model. The model is downstream of the contract and, for this schema,
  strictly weaker: ``datamodel-codegen`` renders ``result`` as ``dict[str, Any]`` because
  it cannot express the ``allOf``/``if``/``then`` discrimination on ``task_type``. Checking
  against the model would silently stop checking ``result`` at all.
* :func:`semantic_violations` — SV-01…SV-07, each returning the exact
  ``validation_failure_kind`` that ``tasks.yaml`` §4 assigns to it. The kind is what the
  fixtures assert on, so it is a contract value, not a log message.

``contracts/ai/tasks.yaml`` §4 places semantic validation at ``MOD-analysis-service`` and
schema validation at both the adapter (early, to save a round trip) and the service
(authoritative). These are pure functions over a payload and a task input: running them in
the adapter costs a failed call less, and running them again on the server is what makes
the server the decider (SRC-PLAN §6.1 — the worker only *proposes* a result).
"""

from __future__ import annotations

import functools
import json
import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Final

from jsonschema import Draft202012Validator
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.states import AnalysisAttemptOutcome, AnalysisTaskType

from worker.app.adapter.base import REPO_ROOT, AdapterError, TaskInput

ANALYSIS_RESULT_SCHEMA: Final[Path] = (
    REPO_ROOT / "contracts" / "schemas" / "analysis-result.schema.json"
)

#: ``analysis-result.schema.json`` ``$defs.evidence_level``: "Thứ tự tăng dần:
#: post_only < abstract < full_text". A dict rather than an ``Enum`` ordering because the
#: comparison is only ever "is this one at most that one".
EVIDENCE_LEVEL_RANK: Final[Mapping[str, int]] = {
    "post_only": 0,
    "abstract": 1,
    "full_text": 2,
}

#: ``contracts/ai/tasks.yaml`` SV-06, ``PROVISIONAL``, matched case-insensitively on NFC.
#: The list is coarse **on purpose** (``rationale_vi``): it is the last fence, not the main
#: one. The main fence is that the model is given nothing with which to judge novelty.
FORBIDDEN_NOVELTY_PHRASES: Final[tuple[str, ...]] = (
    "phát hiện mới",
    "đột phá",
    "lần đầu tiên chứng minh",
    "hướng nghiên cứu mới",
    "breakthrough",
    "first to show",
    "novel discovery",
)

#: Decimal literals in the phrasing text, for SV-05's "numbers must match the input".
_NUMBER_RE: Final[re.Pattern[str]] = re.compile(r"\d+(?:[.,]\d+)?")

_STATEMENT_KINDS_NEEDING_CITATION: Final[frozenset[str]] = frozenset(
    {"author_claim", "source_verified"}
)


class ValidationFailureKind(str, Enum):
    """``validation_failure_kind`` values, verbatim from ``contracts/ai/tasks.yaml`` §4."""

    ANALYSIS_KEY_MISMATCH = "analysis_key_mismatch"
    CITATION_UNKNOWN_SOURCE = "citation_unknown_source"
    UNSUPPORTED_CLAIM_KIND = "unsupported_claim_kind"
    EVIDENCE_LEVEL_OVERCLAIM = "evidence_level_overclaim"
    DIRECTION_MEMBERS_ALTERED = "direction_members_altered"
    FORBIDDEN_NOVELTY_PHRASING = "forbidden_novelty_phrasing"
    VERSION_MISMATCH = "version_mismatch"


@dataclass(frozen=True)
class SchemaViolation:
    """One JSON Schema error, reduced to the two things a fixture predicts."""

    json_pointer: str
    validator: str

    def __str__(self) -> str:  # pragma: no cover - diagnostics only
        return f"{self.json_pointer} ({self.validator})"


@dataclass(frozen=True)
class SemanticViolation:
    """One failed SV check."""

    check_id: str
    kind: ValidationFailureKind
    json_pointer: str


@functools.lru_cache(maxsize=1)
def analysis_result_validator() -> Draft202012Validator:
    """The contract file itself, with the format checker on (``protocol.md`` §10)."""
    schema = json.loads(ANALYSIS_RESULT_SCHEMA.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)


def _pointer(path: Iterable[Any]) -> str:
    parts = [str(part).replace("~", "~0").replace("/", "~1") for part in path]
    return "/" + "/".join(parts) if parts else ""


def schema_violations(payload: Mapping[str, Any]) -> list[SchemaViolation]:
    """Every schema error, sorted by pointer so the list is deterministic."""
    validator = analysis_result_validator()
    found = [
        SchemaViolation(json_pointer=_pointer(error.absolute_path), validator=error.validator)
        for error in validator.iter_errors(dict(payload))
    ]
    return sorted(found, key=lambda violation: (violation.json_pointer, violation.validator))


# ---------------------------------------------------------------------------- SV checks
def _collect_source_refs(payload: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Every ``source_id`` the payload points at, with the pointer that holds it.

    Covers all three carriers ``tasks.yaml`` SV-02 names: ``citation_refs``,
    ``evidence_refs`` and the ``comparator`` of a ``summary``. Missing one of them would
    leave a hole exactly where a fabricated citation would sit.
    """
    refs: list[tuple[str, str]] = []
    result = payload.get("result")
    if not isinstance(result, dict):
        return refs

    for index, label in enumerate(result.get("labels", []) or []):
        if isinstance(label, dict):
            for j, ref in enumerate(label.get("evidence_refs", []) or []):
                refs.append((str(ref), f"/result/labels/{index}/evidence_refs/{j}"))

    for index, statement in enumerate(result.get("statements", []) or []):
        if isinstance(statement, dict):
            for j, ref in enumerate(statement.get("citation_refs", []) or []):
                refs.append((str(ref), f"/result/statements/{index}/citation_refs/{j}"))

    difference = result.get("difference_from_existing")
    if isinstance(difference, dict):
        comparator = difference.get("comparator")
        if isinstance(comparator, dict) and comparator.get("kind") == "ref":
            refs.append(
                (
                    str(comparator.get("source_ref")),
                    "/result/difference_from_existing/comparator/source_ref",
                )
            )
    return refs


def _sv01_analysis_key(payload: Mapping[str, Any], task: TaskInput) -> list[SemanticViolation]:
    """The model may not change the target, the task type or the generation."""
    declared = payload.get("analysis_key")
    if not isinstance(declared, dict):
        return [
            SemanticViolation("SV-01", ValidationFailureKind.ANALYSIS_KEY_MISMATCH, "/analysis_key")
        ]
    failures = [
        SemanticViolation(
            "SV-01", ValidationFailureKind.ANALYSIS_KEY_MISMATCH, f"/analysis_key/{component}"
        )
        for component, expected in task.analysis_key.items()
        if declared.get(component) != expected
    ]
    if payload.get("task_type") != task.task_type.value:
        failures.append(
            SemanticViolation("SV-01", ValidationFailureKind.ANALYSIS_KEY_MISMATCH, "/task_type")
        )
    return failures


def _sv02_citations(payload: Mapping[str, Any], task: TaskInput) -> list[SemanticViolation]:
    """Every citation target must be one of the sources this run was *given*.

    An id that exists in the store but was not supplied still fails, and fixture (c) lists
    "look it up and accept it because it exists" among its forbidden effects: the model
    could not have read it, so the citation is fabricated whatever the row says.
    """
    granted = set(task.input_source_ids)
    return [
        SemanticViolation("SV-02", ValidationFailureKind.CITATION_UNKNOWN_SOURCE, pointer)
        for ref, pointer in _collect_source_refs(payload)
        if ref not in granted
    ]


def _sv03_claim_kind(payload: Mapping[str, Any], _task: TaskInput) -> list[SemanticViolation]:
    """``author_claim``/``source_verified`` need a citation; ``source_verified`` needs a source.

    The second half is the part schema cannot reach: whether ``source_verified`` is
    permitted depends on ``evidence_level``, and "kiểm được từ nguồn" is impossible when the
    only source is a post (REQ-AC11, ``grounding.md`` §2).
    """
    result = payload.get("result")
    if not isinstance(result, dict):
        return []
    level_rank = EVIDENCE_LEVEL_RANK.get(str(payload.get("evidence_level")), -1)
    failures: list[SemanticViolation] = []
    for index, statement in enumerate(result.get("statements", []) or []):
        if not isinstance(statement, dict):
            continue
        kind = str(statement.get("kind"))
        citations = statement.get("citation_refs") or []
        if kind in _STATEMENT_KINDS_NEEDING_CITATION and not citations:
            failures.append(
                SemanticViolation(
                    "SV-03",
                    ValidationFailureKind.UNSUPPORTED_CLAIM_KIND,
                    f"/result/statements/{index}/citation_refs",
                )
            )
        if kind == "source_verified" and level_rank < EVIDENCE_LEVEL_RANK["abstract"]:
            failures.append(
                SemanticViolation(
                    "SV-03",
                    ValidationFailureKind.UNSUPPORTED_CLAIM_KIND,
                    f"/result/statements/{index}/kind",
                )
            )
    return failures


def _sv04_evidence_ceiling(payload: Mapping[str, Any], task: TaskInput) -> list[SemanticViolation]:
    """``evidence_level`` may not exceed the ceiling the *server* computed (§3).

    The ceiling comes from the sources actually placed in the input; neither the model nor
    the worker gets to declare it.
    """
    declared = EVIDENCE_LEVEL_RANK.get(str(payload.get("evidence_level")), -1)
    ceiling = EVIDENCE_LEVEL_RANK.get(task.max_evidence_level, -1)
    if declared < 0 or ceiling < 0 or declared > ceiling:
        return [
            SemanticViolation(
                "SV-04", ValidationFailureKind.EVIDENCE_LEVEL_OVERCLAIM, "/evidence_level"
            )
        ]
    return []


def _numbers_in(text: str) -> set[str]:
    return {match.group(0).replace(",", ".") for match in _NUMBER_RE.finditer(text)}


def _density_numbers(task: TaskInput) -> set[str]:
    """Every number the phrasing is allowed to contain.

    The density figures were computed at ``contracts/reporting/selection.md`` §8 before the
    task existed, and the member count is the one further number a sentence can honestly
    carry ("four works in this period"). Anything else in the text is a number the model
    produced, which is exactly what SV-05 forbids.
    """
    allowed = {str(len(task.member_target_keys))}
    for value in task.density.values():
        if isinstance(value, bool) or value is None:
            continue
        if isinstance(value, int | float):
            allowed.add(f"{value:g}")
            allowed.add(str(value))
        else:
            allowed.add(str(value))
    return allowed


def _sv05_direction_members(payload: Mapping[str, Any], task: TaskInput) -> list[SemanticViolation]:
    """The AI phrases a result; it does not recompute one (CR-PC04-05)."""
    if task.task_type is not AnalysisTaskType.DIRECTION_PHRASING:
        return []
    result = payload.get("result")
    if not isinstance(result, dict):
        return []
    failures: list[SemanticViolation] = []
    members = [str(ref) for ref in result.get("member_refs", []) or []]
    if sorted(members) != sorted(task.member_target_keys) or len(members) != len(
        task.member_target_keys
    ):
        failures.append(
            SemanticViolation(
                "SV-05", ValidationFailureKind.DIRECTION_MEMBERS_ALTERED, "/result/member_refs"
            )
        )
    allowed = _density_numbers(task)
    if _numbers_in(str(result.get("text", ""))) - allowed:
        failures.append(
            SemanticViolation(
                "SV-05", ValidationFailureKind.DIRECTION_MEMBERS_ALTERED, "/result/text"
            )
        )
    return failures


def _sv06_novelty(payload: Mapping[str, Any], task: TaskInput) -> list[SemanticViolation]:
    """No claim of scientific novelty in the phrasing block (REQ-D54, SRC-SPEC §2.3)."""
    if task.task_type is not AnalysisTaskType.DIRECTION_PHRASING:
        return []
    result = payload.get("result")
    if not isinstance(result, dict):
        return []
    text = unicodedata.normalize("NFC", str(result.get("text", ""))).casefold()
    if any(
        unicodedata.normalize("NFC", phrase).casefold() in text
        for phrase in FORBIDDEN_NOVELTY_PHRASES
    ):
        return [
            SemanticViolation(
                "SV-06", ValidationFailureKind.FORBIDDEN_NOVELTY_PHRASING, "/result/text"
            )
        ]
    return []


def _sv07_versions(payload: Mapping[str, Any], task: TaskInput) -> list[SemanticViolation]:
    """Envelope, key and assignment must agree on both versions."""
    failures: list[SemanticViolation] = []
    key = payload.get("analysis_key")
    key_schema_version = key.get("schema_version") if isinstance(key, dict) else None
    if payload.get("schema_version") != key_schema_version:
        failures.append(
            SemanticViolation("SV-07", ValidationFailureKind.VERSION_MISMATCH, "/schema_version")
        )
    if payload.get("schema_version") != task.schema_version:
        failures.append(
            SemanticViolation("SV-07", ValidationFailureKind.VERSION_MISMATCH, "/schema_version")
        )
    key_prompt_version = key.get("prompt_version") if isinstance(key, dict) else None
    if key_prompt_version != task.prompt_version:
        failures.append(
            SemanticViolation(
                "SV-07", ValidationFailureKind.VERSION_MISMATCH, "/analysis_key/prompt_version"
            )
        )
    return failures


_SEMANTIC_CHECKS: Final[tuple[str, ...]] = (
    "SV-01",
    "SV-02",
    "SV-03",
    "SV-04",
    "SV-05",
    "SV-06",
    "SV-07",
)


def semantic_violations(payload: Mapping[str, Any], task: TaskInput) -> list[SemanticViolation]:
    """SV-01…SV-07, in contract order, all of them run.

    All seven run even after the first failure: a payload that cites an unknown source *and*
    overclaims its evidence level has two contract problems, and reporting one hides the
    other from whoever reads the attempt row.
    """
    checks = (
        _sv01_analysis_key,
        _sv02_citations,
        _sv03_claim_kind,
        _sv04_evidence_ceiling,
        _sv05_direction_members,
        _sv06_novelty,
        _sv07_versions,
    )
    failures: list[SemanticViolation] = []
    for check in checks:
        failures.extend(check(payload, task))
    return failures


def validate_result(payload: Mapping[str, Any], task: TaskInput) -> None:
    """Schema first, then semantics; raise ``AI_OUTPUT_INVALID`` on either.

    The order matters for a reason that is not efficiency: a payload that fails the schema
    has no reliable shape, so running semantic checks over it would report failures against
    fields that may not mean what their names say.

    :raises AdapterError: ``AI_OUTPUT_INVALID`` with ``attempt_outcome = schema_invalid``
        and a ``validation_failure_kind`` in ``details_safe``. Never with the payload: the
        model's JSON is as forbidden in an envelope as the transcript is
        (``errors.yaml`` ``redaction_vi``).
    """
    if schema_violations(payload):
        raise _invalid(task, SCHEMA_FAILURE_KIND)
    semantic = semantic_violations(payload, task)
    if semantic:
        raise _invalid(task, semantic[0].kind.value)


#: The ``validation_failure_kind`` reported when step 2 refuses.
#:
#: ``contracts/errors.yaml`` lists ``validation_failure_kind`` as a permitted details key but
#: defines no closed set of values; ``tasks.yaml`` §4 supplies seven, all of them names of
#: *semantic* checks, and ``providers.yaml`` §3 adds ``multiple_json_candidates`` for
#: extraction. There is no contract name for "the schema itself refused", so the adapter
#: reports the layer that did refuse rather than borrowing a semantic name for it. Fixture
#: (d) variant 1 labels a schema failure ``unsupported_claim_kind`` — the semantic name of
#: the same defect — which is the mismatch recorded as ``CR-TC-adapter-02``. The fixture's
#: binding assertion for that variant is its ``json_pointer``, and that is what the contract
#: test checks.
SCHEMA_FAILURE_KIND: Final[str] = "schema_invalid"


def _invalid(task: TaskInput, kind: str) -> AdapterError:
    return AdapterError(
        ErrorCode.AI_OUTPUT_INVALID,
        "Kết quả phân tích không đúng định dạng nên không được ghi nhận.",
        details_safe={
            "task_id": task.task_id,
            "task_type": task.task_type.value,
            "attempt_number": task.attempt_number,
            "validation_failure_kind": kind,
        },
        attempt_outcome=AnalysisAttemptOutcome.SCHEMA_INVALID,
    )


def declared_semantic_check_ids() -> tuple[str, ...]:
    """The seven ids this module implements, for a test that compares them to the contract."""
    return _SEMANTIC_CHECKS


def contract_semantic_check_ids(tasks_yaml: Mapping[str, Any]) -> tuple[str, ...]:
    """The ids ``contracts/ai/tasks.yaml`` §4 declares, read from the contract."""
    checks: Sequence[Mapping[str, Any]] = tasks_yaml["validation_pipeline"]["semantic_checks"]
    return tuple(str(check["id"]) for check in checks)
