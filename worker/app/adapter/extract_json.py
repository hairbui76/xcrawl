"""Step 1 of ``contracts/ai/tasks.yaml`` §4: lift one JSON document out of a transcript.

``contracts/ai/providers.yaml`` §3 ``hard_rules_vi`` gives this module four rules and each
is a refusal rather than a capability:

* the algorithm is **deterministic** — the same transcript yields the same answer;
* **more than one candidate ⇒ reject**, and specifically not "take the last block". This
  is the rule the whole module exists for: source content can plant a decoy JSON before
  or after the real one, so *any* tie-break turns a data channel into a control channel;
* **broken JSON is never repaired**. Adding a brace to make a document parse is inventing
  data, not recovering it;
* **the transcript never reaches a log or an error envelope**
  (``contracts/errors.yaml`` ``AI_OUTPUT_INVALID.redaction_vi``).

The last one shapes the interface: :class:`ExtractionFailure` carries a *kind*, never a
snippet, and the offsets it records are integers. A caller that wants to know why a
transcript failed gets a category and a position, which is enough to route the retry and
not enough to leak content.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.states import AnalysisAttemptOutcome

from worker.app.adapter.base import AdapterError, JsonExtractionMethod

#: A fenced block opened with ```json (case-insensitive) and closed with ```.
_FENCE_RE: Final[re.Pattern[str]] = re.compile(
    r"^[ \t]*```[ \t]*json[ \t]*\r?\n(?P<body>.*?)\r?\n[ \t]*```[ \t]*$",
    re.DOTALL | re.IGNORECASE | re.MULTILINE,
)

#: A nonce is generated per run and must not be derivable from source content
#: (``contracts/ai/tasks.yaml`` §1 ``block_shape_vi``). 16 hex characters is the shortest
#: shape this module will accept; a shorter one is guessable from a transcript.
_NONCE_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9]{16,}$")


class ExtractionFailureKind(str, Enum):
    """Why extraction refused. Categories only — never a fragment of the transcript."""

    #: More than one JSON candidate was present. ``providers.yaml`` §3 names this exactly.
    MULTIPLE_JSON_CANDIDATES = "multiple_json_candidates"
    #: No candidate at all: no fence, no envelope, or nothing that parses.
    NO_JSON_CANDIDATE = "no_json_candidate"
    #: A candidate was found and did not parse. It is *not* repaired.
    MALFORMED_JSON = "malformed_json"
    #: The envelope delimiters were absent or unbalanced.
    ENVELOPE_NOT_FOUND = "envelope_not_found"
    #: The document parsed but is not a JSON object; an analysis result always is one.
    NOT_A_JSON_OBJECT = "not_a_json_object"


@dataclass(frozen=True)
class ExtractionFailure:
    """The refusal, in a form that can be counted and asserted on."""

    kind: ExtractionFailureKind
    method: JsonExtractionMethod
    #: How many candidates the scan found. The number is safe to record; the text is not.
    candidate_count: int = 0

    def as_error(self, *, task_id: str, task_type: str, attempt_number: int) -> AdapterError:
        """``AI_OUTPUT_INVALID`` with ``attempt_outcome = schema_invalid``.

        ``contracts/ai/providers.yaml`` §3 ``on_fail`` fixes both values; the mapping is not
        this module's to choose.
        """
        return AdapterError(
            ErrorCode.AI_OUTPUT_INVALID,
            "Kết quả phân tích không đúng định dạng nên không được ghi nhận.",
            details_safe={
                "task_id": task_id,
                "task_type": task_type,
                "attempt_number": attempt_number,
                "validation_failure_kind": self.kind.value,
            },
            attempt_outcome=AnalysisAttemptOutcome.SCHEMA_INVALID,
        )


class ExtractionError(Exception):
    """Raised by :func:`extract_json`. Holds the :class:`ExtractionFailure`, no content."""

    def __init__(self, failure: ExtractionFailure) -> None:
        super().__init__(f"{failure.kind.value} ({failure.method.value})")
        self.failure = failure


def _fail(
    kind: ExtractionFailureKind, method: JsonExtractionMethod, count: int = 0
) -> ExtractionError:
    return ExtractionError(ExtractionFailure(kind=kind, method=method, candidate_count=count))


def _parse_object(text: str, method: JsonExtractionMethod) -> dict[str, Any]:
    """Parse one candidate, strictly.

    ``json.loads`` already refuses trailing commas and unquoted keys; nothing here relaxes
    it and nothing here retries with a "fixed" string.
    """
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise _fail(ExtractionFailureKind.MALFORMED_JSON, method) from exc
    if not isinstance(document, dict):
        raise _fail(ExtractionFailureKind.NOT_A_JSON_OBJECT, method)
    return document


def _native_json(transcript: str) -> dict[str, Any]:
    """The API-key path: the response body *is* the document (``providers.yaml`` §3).

    "Exactly one document" is enforced by requiring that the decoder consume the whole
    string apart from whitespace. Two concatenated documents are two candidates, and the
    rule for two candidates is the same here as anywhere else: refuse.
    """
    method = JsonExtractionMethod.NATIVE_JSON
    stripped = transcript.strip()
    if not stripped:
        raise _fail(ExtractionFailureKind.NO_JSON_CANDIDATE, method)
    decoder = json.JSONDecoder()
    try:
        document, end = decoder.raw_decode(stripped)
    except json.JSONDecodeError as exc:
        raise _fail(ExtractionFailureKind.MALFORMED_JSON, method) from exc
    if stripped[end:].strip():
        raise _fail(ExtractionFailureKind.MULTIPLE_JSON_CANDIDATES, method, 2)
    if not isinstance(document, dict):
        raise _fail(ExtractionFailureKind.NOT_A_JSON_OBJECT, method)
    return document


def _fenced_block(transcript: str) -> dict[str, Any]:
    """Take the content of the ```json fence — when there is exactly one.

    Two fences is the attack fixture (g)'s negative variant describes: one planted by
    source content, one produced by the model. Neither "first" nor "last" is a safe answer,
    because the attacker chooses the position.
    """
    method = JsonExtractionMethod.FENCED_BLOCK
    bodies = [match.group("body") for match in _FENCE_RE.finditer(transcript)]
    if not bodies:
        raise _fail(ExtractionFailureKind.NO_JSON_CANDIDATE, method)
    if len(bodies) > 1:
        raise _fail(ExtractionFailureKind.MULTIPLE_JSON_CANDIDATES, method, len(bodies))
    return _parse_object(bodies[0], method)


def _delimited_envelope(transcript: str, nonce: str) -> dict[str, Any]:
    """Take what lies between one pair of per-run nonce delimiters.

    Why this is the strongest of the three: the nonce is generated after the source content
    is fixed and never appears in it (``contracts/ai/tasks.yaml`` §1), so content cannot
    forge an envelope. That property is asserted, not assumed — see
    :func:`assert_nonce_absent_from_sources`.

    Exactly two occurrences are required. Three means a candidate was planted; one means
    the envelope was never closed. Both refuse.
    """
    method = JsonExtractionMethod.DELIMITED_ENVELOPE
    if not _NONCE_RE.match(nonce):
        raise ValueError(
            "a delimited envelope needs a per-run random nonce of at least 16 alphanumeric "
            "characters (contracts/ai/tasks.yaml §1 untrusted_content_framing)"
        )
    marker = f"<<<{nonce}>>>"
    positions = [m.start() for m in re.finditer(re.escape(marker), transcript)]
    if len(positions) < 2:
        raise _fail(ExtractionFailureKind.ENVELOPE_NOT_FOUND, method, len(positions))
    if len(positions) > 2:
        raise _fail(ExtractionFailureKind.MULTIPLE_JSON_CANDIDATES, method, len(positions) - 1)
    body = transcript[positions[0] + len(marker) : positions[1]]
    if not body.strip():
        raise _fail(ExtractionFailureKind.NO_JSON_CANDIDATE, method)
    return _parse_object(body, method)


def extract_json(
    transcript: str,
    method: JsonExtractionMethod,
    *,
    nonce: str | None = None,
) -> dict[str, Any]:
    """Lift exactly one JSON object out of ``transcript``.

    Deterministic by construction: no randomness, no clock, no "best effort" ordering. The
    same transcript and the same nonce always produce the same answer, which is what
    fixture (g)'s first row asserts.

    :raises ExtractionError: with an :class:`ExtractionFailure` whose ``kind`` is the
        reason. The transcript is not attached to it, and callers must not attach it later.
    """
    if method is JsonExtractionMethod.NATIVE_JSON:
        return _native_json(transcript)
    if method is JsonExtractionMethod.FENCED_BLOCK:
        return _fenced_block(transcript)
    if nonce is None:
        raise ValueError("delimited_envelope requires the nonce generated for this run")
    return _delimited_envelope(transcript, nonce)


def envelope_marker(nonce: str) -> str:
    """The delimiter pair the prompt asks the model to wrap its JSON in."""
    return f"<<<{nonce}>>>"


def assert_nonce_absent_from_sources(nonce: str, source_texts: list[str]) -> None:
    """The property that makes :func:`_delimited_envelope` sound.

    If the nonce occurs in source content, the content can close the real envelope early
    and open a fake one, and the extractor would have no way to tell. The correct response
    is to draw a new nonce, not to proceed — so this raises rather than warning.
    """
    marker = envelope_marker(nonce)
    for text in source_texts:
        if nonce in text or marker in text:
            raise ValueError(
                "the run nonce occurs in source content; draw a new one before building the "
                "prompt (contracts/ai/tasks.yaml §1 block_shape_vi)"
            )
