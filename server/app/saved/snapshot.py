"""Canonical JSON and ``content_hash`` for ``saved_snapshot`` — the oracle of I08 and I17.

Everything in this module is a pure function of its arguments. It opens no connection and
reads no clock, because ``content_hash`` has to be reproducible from the stored bytes alone:
``sha256(JCS(payload)) == content_hash`` must hold *at every moment after commit*
(``contracts/data/entities.yaml`` ``ENT-saved-snapshot.immutability``), and a hash that
depended on anything outside ``payload`` could not be rechecked after a restart or a restore.

The canonicalisation rule
-------------------------
``contracts/schemas/saved-snapshot.schema.json`` §x-contract.canonical_json_rule pins it:

* algorithm ``sha256``;
* serialisation RFC 8785 (JSON Canonicalization Scheme), UTF-8, no BOM;
* input is **the ``content`` object itself** — not the wrapper, not ``saved_item``, and
  never ``content_hash`` itself;
* format ``"sha256:" + 64 lowercase hex``.

Known limitation of this canonicaliser (identical to the one recorded in
``server/app/ingest/idempotency.py``): RFC 8785 orders object members by UTF-16 code units
while :func:`json.dumps` with ``sort_keys=True`` orders by Unicode code point. The two
differ only for keys containing characters above U+FFFF, and every key in
``saved-snapshot.schema.json`` is ASCII (``additionalProperties: false`` everywhere means no
caller can introduce another one). Numbers use Python's shortest-round-trip repr, which
agrees with ECMAScript for the one numeric field the schema allows
(``matched_tags[].similarity``, a 0..1 double) and for the one integer
(``analysis_ref.generation_number``).

That claim is not left as prose. Two fixtures carry a **literal** hex ``content_hash``
computed outside this repository —
``acceptance/fixtures/telegram/j-concurrent-save-app-telegram.json``
(``sha256:8e3ca77f…``) and ``.../k-save-then-source-deleted.json`` (``sha256:17f5b053…``) —
and ``tests/contract/test_saved_snapshot_schema.py`` recomputes both with
:func:`compute_content_hash`. If this module's canonicalisation ever drifted from the
contract's, those two equalities would break.

A deliberate non-feature: nothing here can *rewrite* a snapshot. There is no ``update``,
no ``rehash_from_current_rows``, no repair path. Recomputing a stored snapshot from today's
rows is precisely the forbidden effect of
``acceptance/fixtures/recovery/e-saved-snapshot-hash-preserved.json``.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any, Final

#: ``snapshot_content.content_version``. Bumping this changes what is canonicalised and so
#: makes every older ``content_hash`` unreproducible; ``entities.yaml`` §schema_versioning
#: therefore requires a migration alongside the bump. The value matches the two positive
#: fixtures, which is what keeps their literal hashes reachable.
CONTENT_VERSION: Final[str] = "0.1.0"

#: Wire ``schema_version`` of the saved-snapshot envelope (the two positive fixtures).
SCHEMA_VERSION: Final[str] = "0.1.0"

_HASH_PREFIX: Final[str] = "sha256:"

#: ``analysis-result.schema.json`` ``comparator.kind`` -> ``summary_block.comparator``.
#: ``ref`` means an actual comparison source was cited; ``unknown`` means there was none and
#: B16 forbids inventing one. There is no third value on either side, so an unrecognised
#: input maps to ``unknown`` rather than to a guess.
_COMPARATOR_KIND: Final[dict[str, str]] = {"ref": "known", "unknown": "unknown"}


def canonical_json(value: Any) -> str:
    """Serialise ``value`` as canonical JSON (RFC 8785 subset — see the module docstring)."""
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


def compute_content_hash(content: Mapping[str, Any]) -> str:
    """``"sha256:" + sha256(JCS(content))`` — the value stored in ``content_hash``.

    :param content: the ``snapshot_content`` object, exactly as it will be persisted in
        ``saved_snapshot.payload``. Passing the envelope, or a dict that still carries
        ``content_hash``, would hash the wrong bytes; the schema's ``input`` clause names
        this object and nothing else.
    """
    digest = hashlib.sha256(canonical_json(content).encode("utf-8")).hexdigest()
    return f"{_HASH_PREFIX}{digest}"


def hash_matches(payload_json: str, content_hash: str) -> bool:
    """Recheck a **stored** snapshot: does ``sha256(JCS(payload))`` still equal its hash?

    Takes the raw ``saved_snapshot.payload`` text rather than a parsed object so that the
    check starts from the bytes on disk. This is the assertion the restart, restore and
    source-deletion tests run; it is a read, and it never writes a corrected value back.
    """
    return compute_content_hash(json.loads(payload_json)) == content_hash


def target_key(kind: str, identifier: str) -> str:
    """``work:<ulid>`` / ``post:<ulid>`` — the union key of ``ADR-0009``.

    Spelled the same way the ``target_key`` generated column spells it in
    ``server/migrations/versions/0002b_shared_move_set_tables.py``, so that a key computed in
    Python and one computed by SQLite cannot disagree.
    """
    return f"{kind}:{identifier}"


def target_object(kind: str, identifier: str) -> dict[str, Any]:
    """The tagged union of ``target.schema.json``: exactly one id, plus its key.

    Setting both ids is the defect negative fixture ``neg-saved-snapshot-target-both-ids``
    pins, so this builder can only ever set one.
    """
    if kind == "work":
        return {"kind": "work", "work_id": identifier, "target_key": target_key(kind, identifier)}
    if kind == "post":
        return {"kind": "post", "post_id": identifier, "target_key": target_key(kind, identifier)}
    raise ValueError(f"target kind must be 'work' or 'post', not {kind!r}")


def summary_block(analysis_payload: Mapping[str, Any]) -> dict[str, Any] | None:
    """Project an ``analysis-result`` ``summary`` payload onto ``summary_block``.

    ``None`` when the payload is not a summary result or is missing one of the three fields
    ``REQ-D20`` requires. Returning ``None`` rather than a partly-filled block is the point:
    ``neg-saved-snapshot-summary-missing-limitation`` exists because a snapshot whose
    ``limitation_vi`` was silently defaulted would look self-contained and not be
    (``REQ-AC10``, B16 — show the missing label, never invent the line).

    ==========================================  ==============================
    ``analysis-result.schema.json``             ``saved-snapshot.schema.json``
    ==========================================  ==============================
    ``result.content``                          ``summary.content_vi``
    ``result.difference_from_existing.text``    ``summary.novelty_vi``
    ``result.limitation_line``                  ``summary.limitation_vi``
    ``…difference_from_existing.comparator``    ``summary.comparator``
    ``result.statements[].kind``                ``summary.claim_kinds``
    ==========================================  ==============================
    """
    result = analysis_payload.get("result")
    if not isinstance(result, Mapping):
        return None
    difference = result.get("difference_from_existing")
    difference = difference if isinstance(difference, Mapping) else {}
    content_vi = result.get("content")
    novelty_vi = difference.get("text")
    limitation_vi = result.get("limitation_line")
    if not (
        isinstance(content_vi, str)
        and content_vi
        and isinstance(novelty_vi, str)
        and novelty_vi
        and isinstance(limitation_vi, str)
        and limitation_vi
    ):
        return None

    block: dict[str, Any] = {
        "content_vi": content_vi,
        "novelty_vi": novelty_vi,
        "limitation_vi": limitation_vi,
    }
    comparator = difference.get("comparator")
    if isinstance(comparator, Mapping):
        block["comparator"] = _COMPARATOR_KIND.get(str(comparator.get("kind")), "unknown")
    statements = result.get("statements")
    if isinstance(statements, Sequence) and not isinstance(statements, str | bytes):
        kinds = [
            str(statement["kind"])
            for statement in statements
            if isinstance(statement, Mapping) and "kind" in statement
        ]
        # De-duplicated but order-preserving: `claim_kinds` is a set of labels, and a stable
        # order keeps the canonical JSON — and therefore the hash — stable too.
        seen: dict[str, None] = dict.fromkeys(kinds)
        if seen:
            block["claim_kinds"] = list(seen)
    return block


def display_title(*, work_title: str | None, post_text: str | None) -> str | None:
    """The one line the Saved screen shows for this item, captured at save time.

    ``display_title`` is ``required`` with ``minLength: 1`` and no other contract defines
    how it is filled, so the rule is stated here rather than left to each call site:

    1. a work target with a title -> that title;
    2. otherwise the first non-empty line of the post text, truncated to the schema's 1000
       characters — a post-only target has no title, and what the screen shows is the post;
    3. otherwise ``None``, and the caller refuses the save.

    Step 3 is why this returns an optional. Substituting a placeholder such as "(no title)"
    would put a string into an immutable snapshot that no source ever produced.
    """
    if work_title and work_title.strip():
        return work_title.strip()[:1000]
    if post_text:
        for line in post_text.splitlines():
            if line.strip():
                return line.strip()[:1000]
    return None


def source_post(row: Mapping[str, Any]) -> dict[str, Any]:
    """One ``source_posts[]`` entry from a ``post`` row.

    ``text`` is copied verbatim. It is DATA (I11): it is escaped at render time and never
    executed, and it is emphatically not sanitised here — rewriting it would change the
    hash and destroy the evidence the snapshot exists to keep.
    """
    entry: dict[str, Any] = {
        "x_post_id": str(row["x_post_id"]),
        "author_handle": str(row["author_handle"]),
        "url": str(row["url"]),
        "text": str(row["text"]),
    }
    for optional in ("published_at", "discovered_at"):
        value = row.get(optional)
        if value is not None:
            entry[optional] = str(value)
    return entry


def work_metadata(row: Mapping[str, Any], *, version_label: str | None = None) -> dict[str, Any]:
    """The ``work_metadata`` block — absent keys stay absent (REQ-D33).

    A post-only target legitimately has no work metadata at all, and an empty string is not
    the same fact as "no DOI": only keys with a real value are emitted.
    """
    metadata: dict[str, Any] = {}
    for column, key in (
        ("canonical_doi", "canonical_doi"),
        ("canonical_arxiv_id", "canonical_arxiv_id"),
        ("paper_url", "paper_url"),
        ("code_url", "code_url"),
    ):
        value = row.get(column)
        if value:
            metadata[key] = str(value)
    if version_label:
        metadata["work_version_label"] = str(version_label)
    return metadata


def build_content(
    *,
    target_kind: str,
    target_id: str,
    title: str | None,
    summary: Mapping[str, Any],
    evidence_level: str,
    matched_tags: Sequence[Mapping[str, Any]] = (),
    topic_labels: Sequence[str] = (),
    work_row: Mapping[str, Any] | None = None,
    work_version_label: str | None = None,
    source_posts: Sequence[Mapping[str, Any]] = (),
    analysis_ref: Mapping[str, Any] | None = None,
    first_announced: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble one ``snapshot_content`` object.

    The result must be **self-contained** (REQ-AC12/REQ-AC10): readable without querying any
    table and without opening any external source. That is why the caller passes rows in and
    this function copies values out — a snapshot holding an id to be dereferenced later
    would stop being readable exactly when the source disappears, which is the case it
    exists for.

    ``matched_tags`` is a snapshot of the tags matched at save time. Dropping a tag
    afterwards must not change this array (REQ-S8.2-07), which follows from the array being
    copied here and the row never being updated.
    """
    content: dict[str, Any] = {
        "content_version": CONTENT_VERSION,
        "target": target_object(target_kind, target_id),
        "display_title": title,
        "summary": dict(summary),
        "evidence_level": evidence_level,
        "matched_tags": [dict(tag) for tag in matched_tags],
        "source_posts": [dict(post) for post in source_posts],
    }
    if topic_labels:
        content["topic_labels"] = [str(label) for label in topic_labels]
    if work_row is not None:
        metadata = work_metadata(work_row, version_label=work_version_label)
        if metadata:
            content["work_metadata"] = metadata
    if analysis_ref:
        content["analysis_ref"] = dict(analysis_ref)
    if first_announced:
        content["first_announced"] = dict(first_announced)
    return content


__all__ = [
    "CONTENT_VERSION",
    "SCHEMA_VERSION",
    "build_content",
    "canonical_json",
    "compute_content_hash",
    "display_title",
    "hash_matches",
    "source_post",
    "summary_block",
    "target_key",
    "target_object",
    "work_metadata",
]
