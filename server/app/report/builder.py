"""``report.build`` -- selection on a versioned snapshot. A data query, never an AI call.

``contracts/reporting/selection.md`` §1 is quoted in SRC-SPEC §10.1 and it is the shape of
this whole module: *"Việc **chọn** mục và **tính** hướng đang nổi là truy vấn dữ liệu, không
phải việc của AI."* There is no provider call anywhere below, and the emerging-directions block
is computed here in full; ``direction_phrasing`` (PC06) may later re-word the object, and if it
is missing the block still exists with its members and its numbers (§8.1).

What "versioned snapshot input" means, concretely
-------------------------------------------------
:func:`build_report` reads four version-carrying values once, at the top, and every later step
uses those and only those:

1. ``tag_config_version`` -- ``tag.get_active_config_version`` (§3.3 step 1). The frozen
   payload *is* the tag set; the live ``tag`` tables are not re-read afterwards, which is what
   makes "the tag set at publish decides the content" (B01) checkable.
2. ``embedding_generation`` -- ``embedding.get_active_generation``, pinned (§5.1). Every
   vector that takes part is checked against it **before** scoring (§5.3).
3. the coverage predecessor -- read through :mod:`server.app.report.coverage`.
4. ``selection_version`` -- the constant of §1, written immutably into the report.

All four travel to the publish CAS inside :class:`BuildSnapshot`, where they are re-checked
against current state. That re-check is the entire point of pinning: a build that read TCV2 and
committed under TCV3 would be a report nobody can reproduce.

The order of §4.3, which is not an optimisation
------------------------------------------------
Exclusions are applied in three passes -- all scores first, then tag-scoped exclusions, then
global ones -- because "stop at the first exclusion that matches" gives the same answer for the
global pass and the **wrong** answer for the tag-scoped one: a target excluded from ``T1``
still belongs in the report under ``T2``. Since exclusions only ever remove, the result does
not depend on the order the rows come back in, which is oracle O-4.3.

What this module does **not** do
--------------------------------
It writes nothing. Coverage advances, ledgers move and delivery intents appear only in
``publisher.py``'s single transaction (§4.4, T-RP-01 ``forbidden_vi``). The one side effect it
is *required* to have is ``analysis.enqueue_tasks`` for selected targets that lack a summary
(B17/AMD-B17, §7.3) -- that is a separate transaction in ``MOD-analysis-service`` and is
deliberately taken before the publish transaction opens, never inside it.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Connection, Engine, text

from server.app.db.engine import session_scope
from server.app.embedding.generation import (
    ComparisonLedger,
    EmbeddingError,
    GenerationFingerprint,
    Normalization,
    Vector,
    assert_comparable,
    cosine,
)
from server.app.report.backfill import (
    CandidateRange,
    ExtensionPlan,
    SettingsPort,
    TableSettings,
)
from server.app.report.backfill import (
    entitlements_to_consume as _entitlements_to_consume,
)
from server.app.report.backfill import (
    plan_extension as _plan_extension,
)
from server.app.report.coverage import (
    SELECTION_VERSION,
    CoverageRepository,
    CoverageWindow,
    IngestWatermarkPort,
    ReportError,
    WindowPlan,
    new_ulid,
    parse_timestamp_utc_ms,
    plan_next_window,
    to_timestamp_utc_ms,
    utc_now_ms,
)

MODULE_ID: Final = "MOD-report-service"

#: ``selection.md`` §3: every similarity is rounded half-up to 4 decimals before it is
#: compared with a threshold and before it is written.
SCORE_DECIMALS: Final = 4

#: The label of the emerging-directions block. ``contracts/schemas/report.schema.json`` makes
#: it a ``const``: it is a contract string, and "phát hiện mới" is forbidden (REQ-D54, B14).
EMERGING_DIRECTION_LABEL: Final = "ứng viên để đọc sâu"


def round_half_up(value: float, decimals: int = SCORE_DECIMALS) -> float:
    """§3 and §8.2 both say *half-up*, which is not what :func:`round` does.

    Python's ``round`` is round-half-to-even. The difference only shows on an exact tie, which
    binary floats rarely produce -- but "rarely" is not "never", and two machines that
    disagreed on one boundary score would disagree on the selected set, which §3 says must not
    happen. ``Decimal`` makes the rule the code follows the rule the contract states.
    """
    if not math.isfinite(value):  # pragma: no cover - defensive
        raise ValueError("cannot round a non-finite score")
    quantum = Decimal(1).scaleb(-decimals)
    return float(Decimal(repr(value)).quantize(quantum, rounding=ROUND_HALF_UP))


# ======================================================================================
# Settings and parameters -- transcribed, with their status
# ======================================================================================


@dataclass(frozen=True, slots=True)
class DensityParameters:
    """``selection.md`` §8.2. Owner-accepted **working values**, still behind gate REQ-A4.

    ``parameters_status`` is ``PROVISIONAL_BOOTSTRAP`` and stays there: ``report.schema.json``
    allows ``CALIBRATED`` but REQ-A4 has not run, and writing ``CALIBRATED`` would be a claim
    about measurement that nobody has made.
    """

    metric: str = "cosine"
    radius: float = 0.8000
    min_members: int = 3
    comparison_window_k: int = 4
    min_prior_windows: int = 2
    min_delta: float = 2.0000
    prior_floor: float = 1.0000
    rounding_decimals: int = SCORE_DECIMALS
    parameters_status: str = "PROVISIONAL_BOOTSTRAP"

    def as_read_model(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "radius": self.radius,
            "min_members": self.min_members,
            "comparison_window_k": self.comparison_window_k,
            "min_prior_windows": self.min_prior_windows,
            "min_delta": self.min_delta,
            "prior_floor": self.prior_floor,
            "rounding_decimals": self.rounding_decimals,
            "parameters_status": self.parameters_status,
        }


@dataclass(frozen=True, slots=True)
class SelectionSettings:
    """The ``settings['reporting.*']`` keys ``selection.md`` §6 and §7.2 name.

    They arrive as an injected value rather than through a ``settings`` table because no
    revision in this repository creates ``ENT-settings`` (``MOD-settings-service`` has no
    card). The defaults below are the contract's values verbatim; a deployment that grows the
    table passes them in. ``CR-TC-REPORT-01`` records the missing owner.

    ``threshold_calibration_state`` defaults to ``uncalibrated`` and every report carries it
    into ``coverage_note`` (§6): while it says ``uncalibrated`` the UI must say the threshold
    has not been calibrated, and no SRC-SPEC §1.4 quality claim may be made.
    """

    default_similarity_threshold: float = 0.8000
    threshold_calibration_state: str = "uncalibrated"
    threshold_calibration_evidence_ref: str | None = None
    max_items_per_period: int = 50
    max_emerging_directions: int = 3
    backfill_days: int = 7
    backfill_max_extension_days: int = 30
    density: DensityParameters = field(default_factory=DensityParameters)


# ======================================================================================
# The tag-service port (§3.3)
# ======================================================================================


@dataclass(frozen=True, slots=True)
class TagConfigVersion:
    """``ENT-tag-config-version``: an immutable snapshot of the whole tag set.

    ``payload`` is "toàn bộ tag/alias/exclusion active tại thời điểm chụp" (``entities.yaml``).
    The three keys this module reads are ``tags``, ``tag_aliases`` and ``tag_exclusions``; the
    shape is documented on :class:`TagSet`.
    """

    id: str
    sequence: int
    content_hash: str
    payload: Mapping[str, Any]
    created_at: str


class TagConfigVersionPort(Protocol):
    """``tag.get_active_config_version`` and ``tag.freeze_config_version``.

    A port, not a table read, for two reasons. ``contracts/modules.yaml`` grants
    ``MOD-report-service -> MOD-tag-service`` exactly these two operations and no data edge;
    and no card in the 19 creates the ``tag`` / ``tag_config_version`` tables, so a direct read
    would be a read of something that does not exist (``CR-TC-REPORT-01``).

    ``freeze_config_version`` is idempotent on ``report_build_id`` and raises
    ``ReportError(TAG_VERSION_STALE)`` when the live version is no longer
    ``expected_tag_config_version_id`` -- the second of the publish CAS's six checks. The error
    **type** is part of the port: the publisher maps that one code to
    ``abort_reason = 'tag_version_stale'`` and lets everything else through untouched.

    ``config_version`` reads one **immutable** snapshot by id. ``report.get`` needs it to
    rebuild the ``tag_config_version`` block of a published read model; ``report`` stores only
    the id, and re-reading the *active* version instead would make a published period change
    when the owner edits a tag -- exactly what I05 forbids.
    """

    def get_active_config_version(self, owner_id: str) -> TagConfigVersion: ...

    def config_version(self, *, owner_id: str, tag_config_version_id: str) -> TagConfigVersion: ...

    def freeze_config_version(
        self, *, owner_id: str, report_build_id: str, expected_tag_config_version_id: str
    ) -> TagConfigVersion: ...


@dataclass(frozen=True, slots=True)
class TagDefinition:
    """One subscription (layer 2 of §1's three layers), with its aliases."""

    id: str
    text: str
    similarity_threshold: float | None
    alias_ids: tuple[tuple[str, str], ...] = ()  # (alias_id, alias_text)


@dataclass(frozen=True, slots=True)
class TagExclusion:
    """``tag_exclusion``: ``tag_id is None`` means global scope (§4.3)."""

    id: str
    tag_id: str | None
    text: str


@dataclass(frozen=True, slots=True)
class TagSet:
    """The frozen payload, parsed.

    Expected payload shape (``entities.yaml`` leaves it to this package to pin)::

        {"tags":           [{"id", "text", "similarity_threshold"}],
         "tag_aliases":    [{"id", "tag_id", "text"}],
         "tag_exclusions": [{"id", "tag_id" | null, "text"}]}

    Only ``active`` rows are in a config version by construction, so there is no ``state``
    field to filter on here; filtering one out would mean the snapshot was not a snapshot.
    """

    tags: tuple[TagDefinition, ...]
    exclusions: tuple[TagExclusion, ...]

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> TagSet:
        aliases: dict[str, list[tuple[str, str]]] = {}
        for alias in payload.get("tag_aliases", ()):
            aliases.setdefault(str(alias["tag_id"]), []).append(
                (str(alias["id"]), str(alias["text"]))
            )
        tags = tuple(
            TagDefinition(
                id=str(tag["id"]),
                text=str(tag["text"]),
                similarity_threshold=(
                    None
                    if tag.get("similarity_threshold") is None
                    else float(tag["similarity_threshold"])
                ),
                # Byte order on the alias id is the §4.1 tie-break, so it is fixed here
                # rather than left to whatever order the payload happened to use.
                alias_ids=tuple(sorted(aliases.get(str(tag["id"]), []))),
            )
            for tag in payload.get("tags", ())
        )
        exclusions = tuple(
            TagExclusion(
                id=str(row["id"]),
                tag_id=None if row.get("tag_id") is None else str(row["tag_id"]),
                text=str(row["text"]),
            )
            for row in payload.get("tag_exclusions", ())
        )
        return cls(tags=tags, exclusions=exclusions)

    def subject_ids(self) -> list[tuple[str, str]]:
        """``(subject_type, subject_id)`` for every vector this selection needs (§5.3)."""
        subjects: list[tuple[str, str]] = []
        for tag in self.tags:
            subjects.append(("tag", tag.id))
            subjects.extend(("tag_alias", alias_id) for alias_id, _ in tag.alias_ids)
        subjects.extend(("tag_exclusion", exclusion.id) for exclusion in self.exclusions)
        return subjects


# ======================================================================================
# Candidates, labels and scores
# ======================================================================================


@dataclass(frozen=True, slots=True)
class Candidate:
    """One target in the candidate set of §2, with everything selection needs about it."""

    target_key: str
    target_kind: str
    target_id: str
    identity_state: str
    discovered_at: str
    ingest_sequence: int
    in_window: bool
    from_pending: bool
    pending_since_window_sequence: int | None
    selected_via_backfill: bool = False
    backfill_ledger_id: str | None = None

    def _replace_backfill(self, candidate_range: CandidateRange) -> Candidate:
        """Stamp this candidate as a §6.3 find, carrying the ledger row that paid for it.

        ``report_item.selection_reason.backfill_ledger_id`` is what lets a reader ask "why is
        an item older than the period in this report?", and the schema makes the id required
        whenever ``selected_via_backfill`` is true -- so the two are set together, here, and
        never apart.
        """
        return Candidate(
            target_key=self.target_key,
            target_kind=self.target_kind,
            target_id=self.target_id,
            identity_state=self.identity_state,
            discovered_at=self.discovered_at,
            ingest_sequence=self.ingest_sequence,
            in_window=False,
            from_pending=self.from_pending,
            pending_since_window_sequence=self.pending_since_window_sequence,
            selected_via_backfill=True,
            backfill_ledger_id=candidate_range.entitlement_id,
        )


@dataclass(frozen=True, slots=True)
class LabelVector:
    """One ``work_label`` row that carries a vector, paired with its generation."""

    target_key: str
    label_text: str
    vector: Vector


@dataclass(frozen=True, slots=True)
class MatchedTag:
    tag_id: str
    tag_text: str
    matched_via: str
    tag_alias_id: str | None
    score: float
    threshold_applied: float
    matched_label_text: str

    def as_read_model(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "tag_id": self.tag_id,
            "tag_text": self.tag_text,
            "matched_via": self.matched_via,
            "score": self.score,
            "threshold_applied": self.threshold_applied,
            "matched_label_text": self.matched_label_text,
        }
        if self.matched_via == "alias":
            body["tag_alias_id"] = self.tag_alias_id
        return body


@dataclass(frozen=True, slots=True)
class ExcludedBy:
    tag_exclusion_id: str
    exclusion_scope: str
    scoped_tag_id: str | None
    score: float
    threshold_applied: float

    def as_read_model(self) -> dict[str, Any]:
        return {
            "tag_exclusion_id": self.tag_exclusion_id,
            "exclusion_scope": self.exclusion_scope,
            "scoped_tag_id": self.scoped_tag_id,
            "score": self.score,
            "threshold_applied": self.threshold_applied,
        }


@dataclass(frozen=True, slots=True)
class SelectedItem:
    """A candidate that survived §4 and is inside the per-period limit."""

    candidate: Candidate
    matched_tags: tuple[MatchedTag, ...]
    excluded_by: tuple[ExcludedBy, ...]
    item_type: str
    first_announced: Mapping[str, Any] | None
    reference_reason: str | None
    analysis: Mapping[str, Any] | None
    summary_state: str

    @property
    def best_score(self) -> float:
        return max(matched.score for matched in self.matched_tags)


@dataclass(frozen=True, slots=True)
class PendingEntry:
    """A row that ``publisher.py`` will write into ``pending_item_ledger`` (§5.1)."""

    target_key: str
    reason: str


@dataclass(frozen=True, slots=True)
class EmergingDirection:
    direction_id: str
    evidence_state: str
    insufficient_reason: str | None
    member_target_keys: tuple[str, ...]
    centroid: tuple[float, ...] | None
    density: Mapping[str, Any] | None
    parameters: DensityParameters
    embedding_generation_id: str
    excluded_quarantined_target_keys: tuple[str, ...]
    phrasing_analysis_id: str | None = None

    def as_read_model(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "direction_id": self.direction_id,
            "evidence_state": self.evidence_state,
            "label": EMERGING_DIRECTION_LABEL,
            "insufficient_reason": self.insufficient_reason,
            "member_target_keys": list(self.member_target_keys),
            "parameters": self.parameters.as_read_model(),
            "embedding_generation_id": self.embedding_generation_id,
            "excluded_quarantined_target_keys": list(self.excluded_quarantined_target_keys),
            "phrasing_analysis_id": self.phrasing_analysis_id,
        }
        if self.centroid is not None:
            body["centroid"] = list(self.centroid)
        if self.density is not None:
            body["density"] = dict(self.density)
        return body


@dataclass(frozen=True, slots=True)
class BuildSnapshot:
    """Everything the publish CAS needs, and nothing it may re-derive.

    The publisher re-checks the three pinned versions against live state; it never recomputes
    the selection. If it did, "the tag set at build decided the content" would be false and
    ``TAG_VERSION_STALE`` would have nothing to detect.
    """

    owner_id: str
    report_build_id: str
    run_id: str | None
    built_at: str
    selection_version: str
    tag_config_version: TagConfigVersion
    generation: GenerationFingerprint
    window_plan: WindowPlan
    predecessor: CoverageWindow | None
    items: tuple[SelectedItem, ...]
    directions: tuple[EmergingDirection, ...]
    pending: tuple[PendingEntry, ...]
    resolved_pending_target_keys: tuple[str, ...]
    backfill_ledger_ids_applied: tuple[str, ...]
    comparison_ledger: ComparisonLedger
    coverage_note: Mapping[str, Any]

    @property
    def is_empty_period(self) -> bool:
        """T-RP-07: nothing was selected. A valid outcome, not a failure."""
        return not self.items


# ======================================================================================
# The build
# ======================================================================================


class EmbeddingPort(Protocol):
    """The two ``MOD-embedding-service`` operations this module is allowed to call."""

    def pin_generation(self, owner_id: str, *, caller_module: str) -> Any: ...

    def embedding_generation_matches(
        self, owner_id: str, expected_embedding_generation_id: str
    ) -> bool: ...


class BackfillPort(Protocol):
    """``time-and-tags.md`` §6.3/§6.4, owned by ``TC-backfill-pending-ledger``.

    Two questions, and this module asks both rather than answering either:

    ``plan_extension``
        how far back each entitled tag may reach this period. It returns **ranges**, not rows
        -- which targets fall inside a range is selection's question (§2), and answering it in
        the backfill module would put that module in the business of reading ``work`` and
        ``post``.
    ``entitlements_to_consume``
        which ledger ids conditions 2 and 3 of §6.4 allow to be spent, given how many rows the
        widening actually produced. Condition 1 -- the publish COMMIT -- is not asked here at
        all: it belongs to :mod:`server.app.report.publisher`, and consumption is written
        inside ``TXN-report-publish`` and nowhere else.

    ``CR-TC-BACKFILL-05``: before this parameter existed, ``_candidates`` never unioned the
    widened range, so no deployment could ever spend an entitlement -- the ledger was written
    and read by tests and by nothing else. The default is :class:`NoBackfill`, which keeps
    every existing caller on exactly the old behaviour instead of silently reaching seven days
    into the past.
    """

    def plan_extension(
        self,
        connection: Connection,
        *,
        owner_id: str,
        coverage_from: datetime,
        coverage_to: datetime,
        tags: Sequence[str],
    ) -> ExtensionPlan: ...

    def entitlements_to_consume(
        self, plan: ExtensionPlan, produced_by_extension: Mapping[str, int]
    ) -> tuple[str, ...]: ...


class NoBackfill:
    """The default: no widening, nothing to consume.

    An explicit no-op rather than ``backfill_port is None`` scattered through the builder, so
    the widening has exactly one code path and the "off" case is exercised by every existing
    test rather than skipped by them.
    """

    def plan_extension(
        self,
        connection: Connection,
        *,
        owner_id: str,
        coverage_from: datetime,
        coverage_to: datetime,
        tags: Sequence[str],
    ) -> ExtensionPlan:
        return ExtensionPlan(ranges=())

    def entitlements_to_consume(
        self, plan: ExtensionPlan, produced_by_extension: Mapping[str, int]
    ) -> tuple[str, ...]:
        return ()


@dataclass(frozen=True, slots=True)
class ServiceBackfill:
    """The real port: ``server.app.report.backfill``, bound to a settings reader.

    ``settings`` is left ``None`` by default and then read with :class:`TableSettings` on the
    connection the builder already holds -- a second connection to the same file would be a
    second read snapshot, and "how far back may this period reach" has to be answered on the
    same snapshot the candidates come from. An explicit ``SettingsPort`` overrides it.

    There is deliberately no code-side default for ``reporting.backfill_days`` (that card's
    ``SG-03``): N = 7 is the Owner's accepted **working value**, read from ``ENT-settings``, so
    an unconfigured deployment gets ``VALIDATION_ERROR`` instead of quietly reaching seven days
    into the past.
    """

    settings: SettingsPort | None = None

    def plan_extension(
        self,
        connection: Connection,
        *,
        owner_id: str,
        coverage_from: datetime,
        coverage_to: datetime,
        tags: Sequence[str],
    ) -> ExtensionPlan:
        settings = self.settings or TableSettings(owner_id=owner_id, connection=connection)
        return _plan_extension(
            connection,
            owner_id=owner_id,
            coverage_from=coverage_from,
            coverage_to=coverage_to,
            tags=tags,
            settings=settings,
        )

    def entitlements_to_consume(
        self, plan: ExtensionPlan, produced_by_extension: Mapping[str, int]
    ) -> tuple[str, ...]:
        return _entitlements_to_consume(plan, produced_by_extension)

    @classmethod
    def on_connection(cls, connection: Connection, owner_id: str) -> ServiceBackfill:
        """Bind :class:`TableSettings` to the connection the builder already holds."""
        return cls(settings=TableSettings(owner_id=owner_id, connection=connection))


class AnalysisEnqueuePort(Protocol):
    """``analysis.enqueue_tasks`` (B17/AMD-B17, §7.3).

    Only for targets the builder **selected**: enqueuing a summary for an unselected target is
    a ``forbidden_vi`` of ``T-RP-01`` and makes AI cost proportional to the corpus rather than
    to the report.
    """

    def enqueue_summaries(self, owner_id: str, target_keys: Sequence[str]) -> None: ...


def build_report(
    engine: Engine,
    *,
    owner_id: str,
    report_build_id: str,
    tag_port: TagConfigVersionPort,
    embedding_port: EmbeddingPort,
    settings: SelectionSettings | None = None,
    analysis_port: AnalysisEnqueuePort | None = None,
    backfill_port: BackfillPort | None = None,
    watermark_port: IngestWatermarkPort | None = None,
    run_id: str | None = None,
    clock: Callable[[], str] = utc_now_ms,
    id_factory: Callable[[], str] = new_ulid,
    run_stop_reason: str | None = None,
    source_coverage_limits_note: str | None = None,
) -> BuildSnapshot:
    """``report.build`` -- T-RP-01. Reads only; writes nothing to this module's tables.

    :param backfill_port: §6.3's widening. The default :class:`NoBackfill` widens nothing, so
        a caller that does not pass one behaves exactly as before; :class:`ServiceBackfill`
        is the real one. Whatever the widening finds is unioned into the candidate set here,
        and the entitlement is spent by ``publisher._consume_backfill`` **inside**
        ``TXN-report-publish`` -- never here, because §6.4 condition 1 is the COMMIT.

    :raises ReportError: ``EMBEDDING_GENERATION_MISMATCH`` when a candidate or subject vector
        does not belong to the pinned generation (§5.3, T-RP-04). The refusal happens while
        inputs are still being assembled -- **before** any publish transaction opens, which is
        what fixture ``l`` means by "selection bị chặn TRƯỚC report commit".
    """
    config = settings or SelectionSettings()
    backfill = backfill_port or NoBackfill()
    built_at = clock()

    pinned = embedding_port.pin_generation(owner_id, caller_module=MODULE_ID)
    generation: GenerationFingerprint = pinned.fingerprint
    tag_config = tag_port.get_active_config_version(owner_id)
    tag_set = TagSet.from_payload(tag_config.payload)
    ledger = ComparisonLedger()

    with session_scope(engine) as connection:
        coverage_repo = CoverageRepository()
        predecessor = coverage_repo.current_window(connection, owner_id)
        plan = plan_next_window(
            connection,
            owner_id=owner_id,
            predecessor=predecessor,
            snapshot_taken_at=built_at,
            watermark_port=watermark_port,
        )
        subjects = _subject_vectors(connection, owner_id, tag_set, generation, ledger)
        candidates = _candidates(connection, owner_id, plan)
        # §6.3: the widening enlarges the CANDIDATE SET only. It never moves
        # `coverage_window.window_from` -- that is fixture `j`'s third forbidden effect, and
        # mixing the two would make the window chain overlap and break I06.
        extension = backfill.plan_extension(
            connection,
            owner_id=owner_id,
            coverage_from=parse_timestamp_utc_ms(plan.window_from),
            coverage_to=parse_timestamp_utc_ms(plan.window_to),
            tags=[tag.id for tag in tag_set.tags],
        )
        entitled_by_tag = _union_backfill_candidates(
            connection, owner_id, extension, plan, candidates
        )
        labels = _label_vectors(connection, owner_id, candidates, generation, ledger)

        scored, excluded = _score_candidates(candidates, labels, tag_set, subjects, config, ledger)
        ordered = _order_candidates(scored, candidates)
        kept = ordered[: config.max_items_per_period]
        overflow = ordered[config.max_items_per_period :]

        items, pending, resolved = _classify(
            connection,
            owner_id=owner_id,
            kept=kept,
            excluded=excluded,
            candidates=candidates,
        )
        # §7.2: items past `max_items_per_period` are NOT dropped -- they become pending
        # with `budget_exceeded` and are candidates again next period (SRC-SPEC §10.4).
        pending = [
            *pending,
            *(PendingEntry(target_key=key, reason="budget_exceeded") for key, _ in overflow),
        ]
        directions = _emerging_directions(
            connection,
            owner_id=owner_id,
            items=items,
            labels=labels,
            candidates=candidates,
            generation=generation,
            predecessor=predecessor,
            config=config,
            ledger=ledger,
            id_factory=id_factory,
        )

    if analysis_port is not None:
        missing = [item.candidate.target_key for item in items if item.summary_state == "pending"]
        if missing:
            analysis_port.enqueue_summaries(owner_id, missing)

    # §6.4 conditions 2 and 3, asked of the module that owns them. Condition 3 counts rows
    # this build is about to write -- a `report_item` **or** a `pending_item_ledger` row,
    # because the contract counts both: a total model failure still spends the entitlement
    # (everything found is pending and certain to return, §5.2) while an *empty* widening does
    # not, since re-reading an empty range costs no AI.
    written_keys = {item.candidate.target_key for item in items} | {
        entry.target_key for entry in pending
    }
    produced_by_extension: dict[str, int] = {}
    for target_key, tag_id in entitled_by_tag.items():
        if target_key in written_keys:
            produced_by_extension[tag_id] = produced_by_extension.get(tag_id, 0) + 1
    backfill_ids = backfill.entitlements_to_consume(extension, produced_by_extension)
    coverage_note = {
        "observed_data_only": True,
        "empty_period": False,
        "threshold_calibration_state": config.threshold_calibration_state,
        "run_stop_reason": run_stop_reason,
        "source_coverage_limits_note": source_coverage_limits_note,
        # REQ-D28: which tags actually reached back this period. Only the ones that produced
        # something -- a widening that found nothing is not "applied" and is not spent.
        "backfill_applied_tag_ids": sorted(produced_by_extension),
    }
    return BuildSnapshot(
        owner_id=owner_id,
        report_build_id=report_build_id,
        run_id=run_id,
        built_at=built_at,
        selection_version=SELECTION_VERSION,
        tag_config_version=tag_config,
        generation=generation,
        window_plan=plan,
        predecessor=predecessor,
        items=tuple(items),
        directions=tuple(directions),
        pending=tuple(pending),
        resolved_pending_target_keys=tuple(resolved),
        backfill_ledger_ids_applied=backfill_ids,
        comparison_ledger=ledger,
        coverage_note=coverage_note,
    )


# --------------------------------------------------------------------------------------
# Step 1: the vectors, and the generation guard that runs before any arithmetic
# --------------------------------------------------------------------------------------


def _fingerprints(connection: Connection, owner_id: str) -> dict[str, GenerationFingerprint]:
    rows = (
        connection.execute(
            text(
                "SELECT id, model_name, model_version, dimension, normalization"
                "  FROM embedding_generation WHERE owner_id = :owner"
            ),
            {"owner": owner_id},
        )
        .mappings()
        .all()
    )
    return {
        str(row["id"]): GenerationFingerprint(
            generation_id=str(row["id"]),
            model_name=str(row["model_name"]),
            model_version=str(row["model_version"]),
            dimension=int(row["dimension"]),
            normalization=Normalization(str(row["normalization"])),
        )
        for row in rows
    }


def _subject_vectors(
    connection: Connection,
    owner_id: str,
    tag_set: TagSet,
    generation: GenerationFingerprint,
    ledger: ComparisonLedger,
) -> dict[tuple[str, str], Vector]:
    """Vectors for every tag, alias and exclusion in the frozen set (§5.3).

    A **missing** subject vector at the pinned generation is
    ``EMBEDDING_GENERATION_MISMATCH``. §5.3 forbids the three alternatives by name: falling
    back to the previous generation, skipping the tag, and mixing. Skipping is the dangerous
    one -- it silently narrows the report and looks like "nothing matched that tag".
    """
    fingerprints = _fingerprints(connection, owner_id)
    rows = (
        connection.execute(
            text(
                "SELECT subject_type, subject_id, embedding_generation_id, vector"
                "  FROM tag_vector WHERE owner_id = :owner"
            ),
            {"owner": owner_id},
        )
        .mappings()
        .all()
    )
    stored: dict[tuple[str, str], Vector] = {}
    for row in rows:
        generation_id = str(row["embedding_generation_id"])
        fingerprint = fingerprints.get(generation_id)
        if fingerprint is None or fingerprint != generation:
            continue
        stored[(str(row["subject_type"]), str(row["subject_id"]))] = Vector.from_blob(
            bytes(row["vector"]), fingerprint
        )

    required = tag_set.subject_ids()
    missing = [key for key in required if key not in stored]
    if missing:
        seen = _first_other_generation([dict(row) for row in rows], generation.generation_id)
        ledger.record_refused(generation, fingerprints.get(seen or "", generation))
        raise ReportError(
            ErrorCode.EMBEDDING_GENERATION_MISMATCH,
            details_safe={
                "expected_generation_id": generation.generation_id,
                "seen_generation_id": seen,
                "dimension_expected": generation.dimension,
                "dimension_seen": None,
            },
        )
    return stored


def _first_other_generation(rows: Iterable[Mapping[str, Any]], expected: str) -> str | None:
    for row in rows:
        value = str(row["embedding_generation_id"])
        if value != expected:
            return value
    return None


def _label_vectors(
    connection: Connection,
    owner_id: str,
    candidates: Mapping[str, Candidate],
    generation: GenerationFingerprint,
    ledger: ComparisonLedger,
) -> dict[str, list[LabelVector]]:
    """``labels(X)`` of §4.1: the ``work_label`` rows of the pinned generation, vector present.

    ``vector IS NULL`` means "being computed" and drops the label out of this period without
    marking the target as a permanent non-match (§5.5). A label belonging to a *different*
    generation is a different matter: it is the fixture-``l`` case, and it refuses.
    """
    if not candidates:
        return {}
    fingerprints = _fingerprints(connection, owner_id)
    rows = (
        connection.execute(
            text(
                "SELECT target_key, label_text, embedding_generation_id, vector"
                "  FROM work_label WHERE owner_id = :owner"
            ),
            {"owner": owner_id},
        )
        .mappings()
        .all()
    )
    labels: dict[str, list[LabelVector]] = {}
    for row in rows:
        target_key = str(row["target_key"])
        if target_key not in candidates:
            continue
        generation_id = str(row["embedding_generation_id"])
        fingerprint = fingerprints.get(generation_id)
        if fingerprint is None:
            continue
        # The guard runs before scoring, on the candidate set (§5.3): a stranger in the set
        # stops the build rather than being filtered out of it.
        assert_comparable(generation, fingerprint, ledger=ledger)
        if row["vector"] is None:
            continue
        labels.setdefault(target_key, []).append(
            LabelVector(
                target_key=target_key,
                label_text=str(row["label_text"]),
                vector=Vector.from_blob(bytes(row["vector"]), fingerprint),
            )
        )
    for values in labels.values():
        values.sort(key=lambda label: label.label_text)
    return labels


# --------------------------------------------------------------------------------------
# Step 2: the candidate set (§2)
# --------------------------------------------------------------------------------------


def _candidates(connection: Connection, owner_id: str, plan: WindowPlan) -> dict[str, Candidate]:
    """``[window items] ∪ [open pending items] ∪ [backfill extension]`` (§2).

    The pending union is I06 in one line: a target that could not be reported when it was
    discovered is a candidate at every later period regardless of where its ``discovered_at``
    falls, until it is reported or the owner abandons it.

    ``work`` rows that are ``merged`` are resolved to the surviving row by following
    ``merged_into_work_id``, per ``contracts/data/identity.md`` §3; ``pending`` posts are not
    targets at all (identity.md §4).
    """
    candidates: dict[str, Candidate] = {}

    work_rows = (
        connection.execute(
            text(
                "SELECT id, identity_state, merged_into_work_id, first_discovered_at,"
                "       ingest_sequence"
                "  FROM work WHERE owner_id = :owner AND ingest_sequence >= :ifrom"
                "   AND ingest_sequence < :ito"
            ),
            {"owner": owner_id, "ifrom": plan.ingest_sequence_from, "ito": plan.ingest_sequence_to},
        )
        .mappings()
        .all()
    )
    for row in work_rows:
        resolved = _resolve_work(connection, owner_id, dict(row))
        if resolved is None:
            continue
        candidates.setdefault(resolved.target_key, resolved)

    post_rows = (
        connection.execute(
            text(
                "SELECT id, identity_resolution, discovered_at, ingest_sequence"
                "  FROM post WHERE owner_id = :owner AND ingest_sequence >= :ifrom"
                "   AND ingest_sequence < :ito AND identity_resolution = 'resolved_post_only'"
            ),
            {"owner": owner_id, "ifrom": plan.ingest_sequence_from, "ito": plan.ingest_sequence_to},
        )
        .mappings()
        .all()
    )
    for row in post_rows:
        key = f"post:{row['id']}"
        candidates.setdefault(
            key,
            Candidate(
                target_key=key,
                target_kind="post",
                target_id=str(row["id"]),
                identity_state="active",
                discovered_at=str(row["discovered_at"]),
                ingest_sequence=int(row["ingest_sequence"]),
                in_window=True,
                from_pending=False,
                pending_since_window_sequence=None,
            ),
        )

    for pending in _open_pending(connection, owner_id):
        key = str(pending["target_key"])
        if key in candidates:
            candidates[key] = _mark_pending(candidates[key], pending)
            continue
        revived = _candidate_for_key(connection, owner_id, key, pending)
        if revived is not None:
            candidates[key] = revived
    return candidates


def _union_backfill_candidates(
    connection: Connection,
    owner_id: str,
    extension: ExtensionPlan,
    window: WindowPlan,
    candidates: dict[str, Candidate],
) -> dict[str, str]:
    """§6.3: union the widened part of each entitled tag's range into the candidate set.

    Mutates ``candidates`` in place and returns ``{target_key: tag_id}`` for the rows the
    widening *added*, which is what §6.4 condition 3 is counted over.

    Only ``[range.start, window_from)`` is queried. The rest of the range is the ordinary
    period, already covered by the sequence-axis query in :func:`_candidates`, and querying it
    twice would be how the same target enters the report as two rows. A target that is already
    a candidate keeps its original entry -- ``setdefault`` semantics, written out -- so an item
    inside the window is never re-labelled as a backfill find.

    Attribution is deterministic: ranges are walked in ``tag_id`` byte order, so a target that
    two entitled tags could both reach is attributed to the first of them, every run.
    """
    entitled: dict[str, str] = {}
    window_from = window.window_from
    for candidate_range in sorted(extension.extended, key=lambda item: item.tag_id):
        start = to_timestamp_utc_ms(candidate_range.start)
        if start >= window_from:  # pragma: no cover - `extended` already implies start < from
            continue
        for row in _rows_in_widened_range(connection, owner_id, start, window_from):
            key, new_candidate = row
            if key in candidates:
                continue
            candidates[key] = new_candidate._replace_backfill(candidate_range)
            entitled[key] = candidate_range.tag_id
    return entitled


def _rows_in_widened_range(
    connection: Connection, owner_id: str, start: str, end: str
) -> list[tuple[str, Candidate]]:
    """Works and post-only posts discovered in ``[start, end)``, ordered for reproducibility."""
    found: list[tuple[str, Candidate]] = []
    for row in connection.execute(
        text(
            "SELECT id, identity_state, merged_into_work_id, first_discovered_at,"
            "       ingest_sequence FROM work"
            " WHERE owner_id = :owner AND first_discovered_at >= :start"
            "   AND first_discovered_at < :end ORDER BY ingest_sequence"
        ),
        {"owner": owner_id, "start": start, "end": end},
    ).mappings():
        resolved = _resolve_work(connection, owner_id, dict(row))
        if resolved is not None:
            found.append((resolved.target_key, resolved))
    for row in connection.execute(
        text(
            "SELECT id, discovered_at, ingest_sequence FROM post"
            " WHERE owner_id = :owner AND discovered_at >= :start AND discovered_at < :end"
            "   AND identity_resolution = 'resolved_post_only' ORDER BY ingest_sequence"
        ),
        {"owner": owner_id, "start": start, "end": end},
    ).mappings():
        key = f"post:{row['id']}"
        found.append(
            (
                key,
                Candidate(
                    target_key=key,
                    target_kind="post",
                    target_id=str(row["id"]),
                    identity_state="active",
                    discovered_at=str(row["discovered_at"]),
                    ingest_sequence=int(row["ingest_sequence"]),
                    in_window=False,
                    from_pending=False,
                    pending_since_window_sequence=None,
                ),
            )
        )
    return found


def _resolve_work(
    connection: Connection, owner_id: str, row: Mapping[str, Any]
) -> Candidate | None:
    identity_state = str(row["identity_state"])
    work_id = str(row["id"])
    discovered_at = str(row["first_discovered_at"])
    ingest_sequence = int(row["ingest_sequence"])
    seen: set[str] = set()
    while identity_state == "merged":
        successor = row["merged_into_work_id"]
        if successor is None or str(successor) in seen:  # pragma: no cover - defensive
            return None
        seen.add(str(successor))
        next_row = (
            connection.execute(
                text(
                    "SELECT id, identity_state, merged_into_work_id, first_discovered_at,"
                    "       ingest_sequence FROM work WHERE owner_id = :owner AND id = :id"
                ),
                {"owner": owner_id, "id": str(successor)},
            )
            .mappings()
            .first()
        )
        if next_row is None:  # pragma: no cover - FK makes this unreachable
            return None
        row = dict(next_row)
        identity_state = str(row["identity_state"])
        work_id = str(row["id"])
    return Candidate(
        target_key=f"work:{work_id}",
        target_kind="work",
        target_id=work_id,
        # `quarantined` stays a candidate: the data is not blocked. It is excluded from the
        # density count instead (§2, identity.md §5.3) and the UI warns.
        identity_state=identity_state,
        discovered_at=discovered_at,
        ingest_sequence=ingest_sequence,
        in_window=True,
        from_pending=False,
        pending_since_window_sequence=None,
    )


def _open_pending(connection: Connection, owner_id: str) -> list[Mapping[str, Any]]:
    return [
        dict(row)
        for row in connection.execute(
            text(
                "SELECT p.id, p.target_key, p.reason, w.sequence AS window_sequence"
                "  FROM pending_item_ledger p"
                "  LEFT JOIN coverage_window w ON w.id = p.first_pending_window_id"
                " WHERE p.owner_id = :owner AND p.state = 'pending'"
            ),
            {"owner": owner_id},
        ).mappings()
    ]


def _mark_pending(candidate: Candidate, pending: Mapping[str, Any]) -> Candidate:
    sequence = pending["window_sequence"]
    return Candidate(
        target_key=candidate.target_key,
        target_kind=candidate.target_kind,
        target_id=candidate.target_id,
        identity_state=candidate.identity_state,
        discovered_at=candidate.discovered_at,
        ingest_sequence=candidate.ingest_sequence,
        in_window=candidate.in_window,
        from_pending=True,
        pending_since_window_sequence=None if sequence is None else int(sequence),
        selected_via_backfill=candidate.selected_via_backfill,
        backfill_ledger_id=candidate.backfill_ledger_id,
    )


def _candidate_for_key(
    connection: Connection, owner_id: str, target_key: str, pending: Mapping[str, Any]
) -> Candidate | None:
    kind, _, identifier = target_key.partition(":")
    sequence = pending["window_sequence"]
    if kind == "work":
        row = (
            connection.execute(
                text(
                    "SELECT id, identity_state, merged_into_work_id, first_discovered_at,"
                    "       ingest_sequence FROM work WHERE owner_id = :owner AND id = :id"
                ),
                {"owner": owner_id, "id": identifier},
            )
            .mappings()
            .first()
        )
        if row is None:
            return None
        resolved = _resolve_work(connection, owner_id, dict(row))
        return (
            None
            if resolved is None
            else _mark_pending(
                Candidate(
                    target_key=resolved.target_key,
                    target_kind=resolved.target_kind,
                    target_id=resolved.target_id,
                    identity_state=resolved.identity_state,
                    discovered_at=resolved.discovered_at,
                    ingest_sequence=resolved.ingest_sequence,
                    in_window=False,
                    from_pending=True,
                    pending_since_window_sequence=None if sequence is None else int(sequence),
                ),
                pending,
            )
        )
    row = (
        connection.execute(
            text(
                "SELECT id, discovered_at, ingest_sequence FROM post"
                " WHERE owner_id = :owner AND id = :id AND identity_resolution ="
                " 'resolved_post_only'"
            ),
            {"owner": owner_id, "id": identifier},
        )
        .mappings()
        .first()
    )
    if row is None:
        return None
    return Candidate(
        target_key=target_key,
        target_kind="post",
        target_id=identifier,
        identity_state="active",
        discovered_at=str(row["discovered_at"]),
        ingest_sequence=int(row["ingest_sequence"]),
        in_window=False,
        from_pending=True,
        pending_since_window_sequence=None if sequence is None else int(sequence),
    )


# --------------------------------------------------------------------------------------
# Step 3: scoring, exclusion precedence and ordering (§4, §7)
# --------------------------------------------------------------------------------------


def _threshold(tag: TagDefinition, settings: SelectionSettings) -> float:
    """§4.2: an alias inherits the parent tag's threshold; it never has one of its own."""
    if tag.similarity_threshold is not None:
        return round_half_up(tag.similarity_threshold)
    return round_half_up(settings.default_similarity_threshold)


def _score_candidates(
    candidates: Mapping[str, Candidate],
    labels: Mapping[str, list[LabelVector]],
    tag_set: TagSet,
    subjects: Mapping[tuple[str, str], Vector],
    settings: SelectionSettings,
    ledger: ComparisonLedger,
) -> tuple[dict[str, list[MatchedTag]], dict[str, list[ExcludedBy]]]:
    """§4.1 -> §4.3, in the three passes the contract's step list requires.

    Pass 1 scores everything and removes nothing; pass 2 removes tag-scoped pairs; pass 3
    removes whole targets. Because exclusions only ever remove, the answer does not depend on
    the order in which exclusion rows arrive -- oracle O-4.3.
    """
    survived: dict[str, list[MatchedTag]] = {}
    removed: dict[str, list[ExcludedBy]] = {}

    for target_key in sorted(candidates):
        target_labels = labels.get(target_key, [])
        if not target_labels:
            # §4.1: no labels means not selected this period. A missing label does NOT create
            # a pending row on its own -- labelling belongs to ingest, not to the builder.
            continue

        # Pass 1 -- every (X, T) pair, nothing removed.
        pairs: list[MatchedTag] = []
        for tag in tag_set.tags:
            matched = _best_pair(target_labels, tag, subjects, ledger)
            if matched is None:
                continue
            threshold = _threshold(tag, settings)
            if matched.score >= threshold:
                pairs.append(
                    MatchedTag(
                        tag_id=matched.tag_id,
                        tag_text=matched.tag_text,
                        matched_via=matched.matched_via,
                        tag_alias_id=matched.tag_alias_id,
                        score=matched.score,
                        threshold_applied=threshold,
                        matched_label_text=matched.matched_label_text,
                    )
                )
        if not pairs:
            continue

        # Pass 2 -- tag-scoped exclusions remove single pairs. Every exclusion of the scope
        # is applied, not the first matching one: "dừng ở exclusion đầu tiên khớp" gives the
        # right answer for pass 3 and the wrong one here (§4.3).
        excluded: list[ExcludedBy] = []
        scoped: dict[str, list[TagExclusion]] = {}
        for exclusion in tag_set.exclusions:
            if exclusion.tag_id is not None:
                scoped.setdefault(exclusion.tag_id, []).append(exclusion)
        kept_pairs: list[MatchedTag] = []
        for pair in pairs:
            dropped = False
            for exclusion in scoped.get(pair.tag_id, ()):
                threshold = _exclusion_threshold(exclusion, tag_set, settings)
                score = _exclusion_score(target_labels, exclusion, subjects, ledger)
                if score is not None and score >= threshold:
                    excluded.append(
                        ExcludedBy(
                            tag_exclusion_id=exclusion.id,
                            exclusion_scope="tag_scoped",
                            scoped_tag_id=exclusion.tag_id,
                            score=score,
                            threshold_applied=threshold,
                        )
                    )
                    dropped = True
            if not dropped:
                kept_pairs.append(pair)

        # Pass 3 -- a global exclusion removes the whole target, however high it scored.
        globally_removed = False
        for exclusion in tag_set.exclusions:
            if exclusion.tag_id is not None:
                continue
            threshold = _exclusion_threshold(exclusion, tag_set, settings)
            score = _exclusion_score(target_labels, exclusion, subjects, ledger)
            if score is not None and score >= threshold:
                excluded.append(
                    ExcludedBy(
                        tag_exclusion_id=exclusion.id,
                        exclusion_scope="global",
                        scoped_tag_id=None,
                        score=score,
                        threshold_applied=threshold,
                    )
                )
                globally_removed = True

        removed[target_key] = excluded
        if globally_removed or not kept_pairs:
            continue
        survived[target_key] = kept_pairs
    return survived, removed


@dataclass(frozen=True, slots=True)
class _BestPair:
    tag_id: str
    tag_text: str
    matched_via: str
    tag_alias_id: str | None
    score: float
    matched_label_text: str


def _best_pair(
    labels: Sequence[LabelVector],
    tag: TagDefinition,
    subjects: Mapping[tuple[str, str], Vector],
    ledger: ComparisonLedger,
) -> _BestPair | None:
    """``score(X, T) = max over (label, subject) of cosine`` with the §4.1 tie-break.

    On a tie after rounding, ``matched_via = 'tag'`` wins over ``'alias'``, and among aliases
    the smallest id in byte order wins. The rule has to be total or
    ``selection_reason.matched_tags`` is not reproducible.
    """
    best: _BestPair | None = None
    subject_list: list[tuple[str, str | None, str, Vector]] = []
    tag_vector = subjects.get(("tag", tag.id))
    if tag_vector is not None:
        subject_list.append(("tag", None, tag.text, tag_vector))
    for alias_id, alias_text in tag.alias_ids:
        alias_vector = subjects.get(("tag_alias", alias_id))
        if alias_vector is not None:
            subject_list.append(("alias", alias_id, alias_text, alias_vector))

    for label in labels:
        for matched_via, subject_alias_id, _text, subject in subject_list:
            try:
                score = round_half_up(cosine(label.vector, subject, ledger=ledger))
            except EmbeddingError as exc:
                if exc.code is ErrorCode.VALIDATION_ERROR:
                    # §3: a zero-norm vector has no direction; the item drops out of the
                    # comparison with reason `zero_norm_vector`. It is never scored 0.0 and
                    # never treated as a match.
                    continue
                raise
            candidate = _BestPair(
                tag_id=tag.id,
                tag_text=tag.text,
                matched_via=matched_via,
                tag_alias_id=subject_alias_id,
                score=score,
                matched_label_text=label.label_text,
            )
            if best is None or _pair_sort_key(candidate) < _pair_sort_key(best):
                best = candidate
    return best


def _pair_sort_key(pair: _BestPair) -> tuple[float, int, str]:
    """Higher score first; on a tie ``tag`` before ``alias``; then alias id in byte order."""
    return (-pair.score, 0 if pair.matched_via == "tag" else 1, pair.tag_alias_id or "")


def _exclusion_threshold(
    exclusion: TagExclusion, tag_set: TagSet, settings: SelectionSettings
) -> float:
    """§4.3: an exclusion reuses the threshold of the scope it lives in, never a third knob."""
    if exclusion.tag_id is None:
        return round_half_up(settings.default_similarity_threshold)
    for tag in tag_set.tags:
        if tag.id == exclusion.tag_id:
            return _threshold(tag, settings)
    return round_half_up(settings.default_similarity_threshold)


def _exclusion_score(
    labels: Sequence[LabelVector],
    exclusion: TagExclusion,
    subjects: Mapping[tuple[str, str], Vector],
    ledger: ComparisonLedger,
) -> float | None:
    subject = subjects.get(("tag_exclusion", exclusion.id))
    if subject is None:
        return None
    scores: list[float] = []
    for label in labels:
        try:
            scores.append(round_half_up(cosine(label.vector, subject, ledger=ledger)))
        except EmbeddingError as exc:
            if exc.code is ErrorCode.VALIDATION_ERROR:
                continue
            raise
    return max(scores) if scores else None


def _order_candidates(
    scored: Mapping[str, list[MatchedTag]], candidates: Mapping[str, Candidate]
) -> list[tuple[str, list[MatchedTag]]]:
    """§7.1 keys 2..5. Key 1 (``item_type``) is applied in :func:`_classify`.

    Keys 4 and 5 make the order **total**: no two items are indistinguishable, so two runs on
    the same data produce the same list and therefore the same ``content_hash``.
    """

    def sort_key(entry: tuple[str, list[MatchedTag]]) -> tuple[float, str, int, str]:
        target_key, matched = entry
        candidate = candidates[target_key]
        return (
            -max(tag.score for tag in matched),
            candidate.discovered_at,
            candidate.ingest_sequence,
            target_key,
        )

    return sorted(scored.items(), key=sort_key)


# --------------------------------------------------------------------------------------
# Step 4: item_type, first-announcement and summaries (§7.3, §8)
# --------------------------------------------------------------------------------------


def _classify(
    connection: Connection,
    *,
    owner_id: str,
    kept: Sequence[tuple[str, list[MatchedTag]]],
    excluded: Mapping[str, list[ExcludedBy]],
    candidates: Mapping[str, Candidate],
) -> tuple[list[SelectedItem], list[PendingEntry], list[str]]:
    """Decide ``new_discovery`` vs ``prior_reference`` and attach the summary (§8.2, §7.3).

    There is **no branch** that republishes an announced work as a new discovery: a work with
    an effective ``first_announced_ledger`` row is forced to ``prior_reference`` with its date.
    That is I07 in the read path; the UNIQUE index is the same rule in the write path, and the
    two together are why fixture ``h`` writes no second ledger row.
    """
    items: list[SelectedItem] = []
    pending: list[PendingEntry] = []
    resolved: list[str] = []
    for target_key, matched in kept:
        candidate = candidates[target_key]
        announced = _effective_first_announcement(connection, owner_id, candidate)
        analysis = _valid_summary(connection, owner_id, target_key)
        summary_state = "present" if analysis is not None else "pending"
        if analysis is None:
            pending.append(PendingEntry(target_key=target_key, reason="missing_summary"))
        elif candidate.from_pending:
            # §5.3: the pending row closes in the same publish transaction and the item is
            # labelled "phát hiện muộn". `item_type` does not change: a late discovery that
            # was never announced is still a new discovery.
            resolved.append(target_key)
        items.append(
            SelectedItem(
                candidate=candidate,
                matched_tags=tuple(matched),
                excluded_by=tuple(excluded.get(target_key, ())),
                item_type="prior_reference" if announced is not None else "new_discovery",
                first_announced=announced,
                reference_reason="already_announced" if announced is not None else None,
                analysis=analysis,
                summary_state=summary_state,
            )
        )
    # §7.1 key 1: `new_discovery` before `prior_reference`, the rest of the order preserved.
    items.sort(key=lambda item: 0 if item.item_type == "new_discovery" else 1)
    return items, pending, resolved


def _effective_first_announcement(
    connection: Connection, owner_id: str, candidate: Candidate
) -> dict[str, Any] | None:
    """§8.1. The effective row is the one with ``superseded_by_merge_id IS NULL``.

    A post-only target has no canonical identity and therefore no ledger row; for it, "already
    announced" is derived from the immutable history of published ``report_item`` rows, which
    is deterministic because those rows never change (I05) and a merge never rewrites their
    ``target_key`` (I17).
    """
    if candidate.target_kind == "post":
        row = (
            connection.execute(
                text(
                    "SELECT ri.report_id, r.published_at, w.sequence AS window_sequence,"
                    "       ri.target_key"
                    "  FROM report_item ri"
                    "  JOIN report r ON r.id = ri.report_id"
                    "  LEFT JOIN coverage_window w ON w.report_id = r.id"
                    " WHERE ri.owner_id = :owner AND ri.target_key = :key"
                    "   AND ri.item_type = 'new_discovery' AND r.status = 'published'"
                    " ORDER BY r.published_at LIMIT 1"
                ),
                {"owner": owner_id, "key": candidate.target_key},
            )
            .mappings()
            .first()
        )
        if row is None:
            return None
        return {
            "first_announced_report_id": str(row["report_id"]),
            "first_announced_at": str(row["published_at"]),
            "first_announced_window_sequence": int(row["window_sequence"] or 1),
            "target_key_at_announcement": str(row["target_key"]),
            "merge_audit_id": None,
        }

    row = (
        connection.execute(
            text(
                "SELECT f.first_report_id, f.first_announced_at, f.merge_audit_id,"
                "       w.sequence AS window_sequence"
                "  FROM first_announced_ledger f"
                "  LEFT JOIN coverage_window w ON w.report_id = f.first_report_id"
                " WHERE f.owner_id = :owner AND f.canonical_work_id = :work"
                "   AND f.superseded_by_merge_id IS NULL"
            ),
            {"owner": owner_id, "work": candidate.target_id},
        )
        .mappings()
        .first()
    )
    if row is None:
        return None
    announcement_key = connection.execute(
        text(
            "SELECT target_key FROM report_item"
            " WHERE owner_id = :owner AND report_id = :report AND item_type = 'new_discovery'"
            " ORDER BY target_key LIMIT 1"
        ),
        {"owner": owner_id, "report": str(row["first_report_id"])},
    ).scalar()
    return {
        "first_announced_report_id": str(row["first_report_id"]),
        "first_announced_at": str(row["first_announced_at"]),
        "first_announced_window_sequence": int(row["window_sequence"] or 1),
        # A derived read-model value (report.schema.json ``first_announced_ref``), not a
        # ledger column: the merge deliberately does not rewrite published `target_key`s, so
        # the bridge between the old key and the new one is computed, never stored.
        "target_key_at_announcement": (
            candidate.target_key if announcement_key is None else str(announcement_key)
        ),
        "merge_audit_id": None if row["merge_audit_id"] is None else str(row["merge_audit_id"]),
    }


def _valid_summary(connection: Connection, owner_id: str, target_key: str) -> dict[str, Any] | None:
    """The ``analysis`` row a report item points at: ``valid``, ``summary``, newest generation."""
    row = (
        connection.execute(
            text(
                "SELECT id, generation_number, payload_hash, evidence_level, analyzed_at"
                "  FROM analysis WHERE owner_id = :owner AND target_key = :key"
                "   AND task_type = 'summary' AND status = 'valid'"
                " ORDER BY generation_number DESC LIMIT 1"
            ),
            {"owner": owner_id, "key": target_key},
        )
        .mappings()
        .first()
    )
    if row is None:
        return None
    return {
        "analysis_id": str(row["id"]),
        "task_type": "summary",
        "generation_number": int(row["generation_number"]),
        "payload_hash": str(row["payload_hash"]),
        "evidence_level": str(row["evidence_level"]),
        "analyzed_at": str(row["analyzed_at"]),
        "analysis_result_schema_id": (
            "https://research-radar.local/schemas/analysis-result.schema.json"
        ),
    }


# --------------------------------------------------------------------------------------
# Step 5: vector density and the emerging-directions block (§8.3)
# --------------------------------------------------------------------------------------


def _emerging_directions(
    connection: Connection,
    *,
    owner_id: str,
    items: Sequence[SelectedItem],
    labels: Mapping[str, list[LabelVector]],
    candidates: Mapping[str, Candidate],
    generation: GenerationFingerprint,
    predecessor: CoverageWindow | None,
    config: SelectionSettings,
    ledger: ComparisonLedger,
    id_factory: Callable[[], str],
) -> list[EmergingDirection]:
    """BƯỚC 1..10 of §8.3, then §8.4's mandatory ``insufficient_evidence`` row.

    Deterministic by construction: fixed-radius neighbourhoods, a total seed order and no
    randomised initialisation. That is why §8.3 rejects k-means -- the same input has to give
    the same block, and O-8.3 checks it by reversing the row order.
    """
    parameters = config.density
    selected_keys = [item.candidate.target_key for item in items]
    quarantined = tuple(
        sorted(key for key in selected_keys if candidates[key].identity_state == "quarantined")
    )
    counted = [key for key in selected_keys if key not in set(quarantined)]

    prior_windows = _prior_windows(connection, owner_id, predecessor, generation, parameters)
    if not items:
        return []

    # BƯỚC 1-2: one vector per (target, label); neighbourhoods computed once.
    points: list[LabelVector] = [label for key in counted for label in labels.get(key, [])]
    if len(points) < parameters.min_members:
        return [
            _insufficient(
                id_factory(),
                reason=(
                    "generation_reset"
                    if _generation_reset(connection, owner_id, predecessor, generation)
                    else "below_min_sample"
                ),
                parameters=parameters,
                generation=generation,
                quarantined=quarantined,
            )
        ]

    neighbours: dict[int, set[int]] = {}
    for i, point in enumerate(points):
        near = {
            j
            for j, other in enumerate(points)
            if round_half_up(cosine(point.vector, other.vector, ledger=ledger)) >= parameters.radius
        }
        neighbours[i] = near

    # BƯỚC 3: deterministic greedy grouping.
    order = sorted(
        range(len(points)),
        key=lambda i: (-len(neighbours[i]), points[i].target_key, points[i].label_text),
    )
    assigned: set[int] = set()
    groups: list[set[int]] = []
    for seed in order:
        if seed in assigned:
            continue
        members = neighbours[seed] - assigned
        if members:
            groups.append(members)
            assigned |= members

    # BƯỚC 4-6.
    published: list[EmergingDirection] = []
    for group in groups:
        member_keys = sorted({points[i].target_key for i in group})
        if len(member_keys) < parameters.min_members:
            continue
        centroid = _centroid([points[i].vector for i in group], generation)
        density_prior, windows_used = _density_prior(
            connection, owner_id, prior_windows, centroid, parameters, ledger
        )
        if len(prior_windows) < parameters.min_prior_windows:
            continue
        density_now = len(member_keys)
        density_delta = round_half_up(density_now - density_prior)
        density_ratio = round_half_up(density_now / max(density_prior, parameters.prior_floor))
        if density_delta < parameters.min_delta:
            continue
        published.append(
            EmergingDirection(
                direction_id=id_factory(),
                evidence_state="sufficient",
                insufficient_reason=None,
                member_target_keys=tuple(member_keys),
                centroid=centroid.values,
                density={
                    "density_now": density_now,
                    "density_prior": round_half_up(density_prior),
                    "density_delta": density_delta,
                    "density_ratio": density_ratio,
                    "comparison_windows_used": windows_used,
                },
                parameters=parameters,
                embedding_generation_id=generation.generation_id,
                excluded_quarantined_target_keys=quarantined,
            )
        )

    if not published:
        return [
            _insufficient(
                id_factory(),
                reason=_insufficient_reason(
                    connection,
                    owner_id,
                    predecessor,
                    generation,
                    groups,
                    points,
                    parameters,
                    prior_windows,
                ),
                parameters=parameters,
                generation=generation,
                quarantined=quarantined,
            )
        ]

    # BƯỚC 10.
    published.sort(
        key=lambda direction: (
            -float(direction.density["density_delta"]),  # type: ignore[index]
            -len(direction.member_target_keys),
            direction.member_target_keys[0],
        )
    )
    return published[: config.max_emerging_directions]


def _insufficient(
    direction_id: str,
    *,
    reason: str,
    parameters: DensityParameters,
    generation: GenerationFingerprint,
    quarantined: tuple[str, ...],
) -> EmergingDirection:
    """§8.4: ``insufficient_evidence`` is a required outcome, not an error path.

    B14 in one row: too little data is reported as too little data, never dressed up as an
    emerging direction. Cold start always lands here, and that is correct behaviour.
    """
    return EmergingDirection(
        direction_id=direction_id,
        evidence_state="insufficient_evidence",
        insufficient_reason=reason,
        member_target_keys=(),
        centroid=None,
        density=None,
        parameters=parameters,
        embedding_generation_id=generation.generation_id,
        excluded_quarantined_target_keys=quarantined,
    )


def _insufficient_reason(
    connection: Connection,
    owner_id: str,
    predecessor: CoverageWindow | None,
    generation: GenerationFingerprint,
    groups: Sequence[set[int]],
    points: Sequence[LabelVector],
    parameters: DensityParameters,
    prior_windows: Sequence[CoverageWindow],
) -> str:
    if _generation_reset(connection, owner_id, predecessor, generation):
        return "generation_reset"
    if len(prior_windows) < parameters.min_prior_windows:
        return "cold_start_insufficient_history"
    big_enough = any(
        len({points[i].target_key for i in group}) >= parameters.min_members for group in groups
    )
    return "delta_below_threshold" if big_enough else "below_min_sample"


def _generation_reset(
    connection: Connection,
    owner_id: str,
    predecessor: CoverageWindow | None,
    generation: GenerationFingerprint,
) -> bool:
    """§8.5: a generation switch invalidates every prior period as a baseline (I12)."""
    if predecessor is None:
        return False
    previous = connection.execute(
        text(
            "SELECT embedding_generation_id FROM report r"
            "  JOIN coverage_window w ON w.report_id = r.id"
            " WHERE r.owner_id = :owner AND r.status = 'published'"
            " ORDER BY w.sequence DESC LIMIT 1"
        ),
        {"owner": owner_id},
    ).scalar()
    return previous is not None and str(previous) != generation.generation_id


def _prior_windows(
    connection: Connection,
    owner_id: str,
    predecessor: CoverageWindow | None,
    generation: GenerationFingerprint,
    parameters: DensityParameters,
) -> list[CoverageWindow]:
    """BƯỚC 7: the ``K`` preceding published periods **of the same generation** (§8.3, §8.5)."""
    if predecessor is None:
        return []
    rows = (
        connection.execute(
            text(
                "SELECT w.id, w.owner_id, w.sequence, w.window_from, w.window_to,"
                "       w.ingest_sequence_from, w.ingest_sequence_to, w.predecessor_window_id,"
                "       w.report_id, w.advanced_at"
                "  FROM coverage_window w JOIN report r ON r.id = w.report_id"
                " WHERE w.owner_id = :owner AND r.status = 'published'"
                "   AND r.embedding_generation_id = :generation AND w.sequence <= :sequence"
                " ORDER BY w.sequence DESC LIMIT :k"
            ),
            {
                "owner": owner_id,
                "generation": generation.generation_id,
                "sequence": predecessor.sequence,
                "k": parameters.comparison_window_k,
            },
        )
        .mappings()
        .all()
    )
    return [
        CoverageWindow(
            id=str(row["id"]),
            owner_id=str(row["owner_id"]),
            sequence=int(row["sequence"]),
            window_from=str(row["window_from"]),
            window_to=str(row["window_to"]),
            ingest_sequence_from=int(row["ingest_sequence_from"]),
            ingest_sequence_to=int(row["ingest_sequence_to"]),
            predecessor_window_id=(
                None if row["predecessor_window_id"] is None else str(row["predecessor_window_id"])
            ),
            report_id=None if row["report_id"] is None else str(row["report_id"]),
            advanced_at=str(row["advanced_at"]),
        )
        for row in rows
    ]


def _centroid(vectors: Sequence[Vector], generation: GenerationFingerprint) -> Vector:
    """BƯỚC 6: componentwise mean, then L2-normalised, written immutably into the row."""
    dimension = generation.dimension
    sums = [math.fsum(vector.values[i] for vector in vectors) for i in range(dimension)]
    mean = [value / len(vectors) for value in sums]
    norm = math.sqrt(math.fsum(value * value for value in mean))
    if norm == 0.0:  # pragma: no cover - a group of opposing unit vectors
        raise ReportError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={"field_path": "centroid", "violation_kind": "zero_norm"},
        )
    return Vector(
        fingerprint=generation,
        values=tuple(round_half_up(value / norm) for value in mean),
    )


def _density_prior(
    connection: Connection,
    owner_id: str,
    prior_windows: Sequence[CoverageWindow],
    centroid: Vector,
    parameters: DensityParameters,
    ledger: ComparisonLedger,
) -> tuple[float, list[dict[str, int]]]:
    """BƯỚC 7-8. The mean is over the periods that **exist**; absent periods are not zeros.

    Padding a missing period with 0 would make a young system look like a surge, which is
    exactly the false positive B14 exists to prevent.
    """
    if not prior_windows:
        return 0.0, []
    per_window: list[dict[str, int]] = []
    counts: list[int] = []
    for window in prior_windows:
        keys = [
            str(row["target_key"])
            for row in connection.execute(
                text(
                    "SELECT target_key FROM report_item"
                    " WHERE owner_id = :owner AND report_id = :report"
                ),
                {"owner": owner_id, "report": window.report_id},
            ).mappings()
        ]
        in_radius = 0
        for target_key in keys:
            if _any_label_in_radius(connection, owner_id, target_key, centroid, parameters, ledger):
                in_radius += 1
        counts.append(in_radius)
        per_window.append(
            {"coverage_window_sequence": window.sequence, "members_in_radius": in_radius}
        )
    per_window.sort(key=lambda entry: entry["coverage_window_sequence"])
    return math.fsum(counts) / len(counts), per_window


def _any_label_in_radius(
    connection: Connection,
    owner_id: str,
    target_key: str,
    centroid: Vector,
    parameters: DensityParameters,
    ledger: ComparisonLedger,
) -> bool:
    rows = (
        connection.execute(
            text(
                "SELECT vector FROM work_label"
                " WHERE owner_id = :owner AND target_key = :key"
                "   AND embedding_generation_id = :generation AND vector IS NOT NULL"
            ),
            {
                "owner": owner_id,
                "key": target_key,
                "generation": centroid.fingerprint.generation_id,
            },
        )
        .mappings()
        .all()
    )
    for row in rows:
        vector = Vector.from_blob(bytes(row["vector"]), centroid.fingerprint)
        try:
            score = round_half_up(cosine(vector, centroid, ledger=ledger))
        except EmbeddingError:
            continue
        if score >= parameters.radius:
            return True
    return False


class ServiceAnalysisEnqueue:
    """Adapter onto the real ``analysis.enqueue_tasks``, kept out of the publish transaction.

    ``MOD-report-service -> MOD-analysis-service`` is an allowed edge for exactly this
    operation and nothing else; ``FE-28`` forbids this module from touching a committed
    analysis, so the adapter only ever enqueues.

    ``prompt_version`` and ``schema_version`` have **no defaults**. They belong to
    ``contracts/ai/tasks.yaml`` (PC06), which is outside this card's read set (§9), and a
    guessed value would silently change the analysis key -- the one component whose stability
    makes REQ-AC06's "tag edit ⇒ provider call delta 0" true. The wiring supplies them or
    there is no adapter.

    ``source_fingerprint`` *is* computed here, from committed rows only
    (``server.app.analysis.key.compute_source_fingerprint``): a work target hashes its current
    ``work_version.content_fingerprint`` together with the ``source_snapshot_hash`` of every
    post linked to it; a post target hashes its own. Those are the inputs the analysis card
    documents, and they are all readable at the moment of selection.
    """

    def __init__(
        self,
        context: Any,
        engine: Engine,
        *,
        prompt_version: str,
        schema_version: str,
    ) -> None:
        self._context = context
        self._engine = engine
        self._prompt_version = prompt_version
        self._schema_version = schema_version

    def enqueue_summaries(self, owner_id: str, target_keys: Sequence[str]) -> None:
        from server.app.analysis.key import compute_source_fingerprint
        from server.app.analysis.service import TargetRequest, enqueue_tasks

        requests: list[Any] = []
        with session_scope(self._engine) as connection:
            for target_key in target_keys:
                kind, _, identifier = target_key.partition(":")
                fingerprint = _source_fingerprint(
                    connection, owner_id, kind, identifier, compute_source_fingerprint
                )
                requests.append(
                    TargetRequest(
                        target_kind=kind,
                        target_id=identifier,
                        task_type="summary",
                        source_fingerprint=fingerprint,
                        prompt_version=self._prompt_version,
                        schema_version=self._schema_version,
                    )
                )
        if requests:
            enqueue_tasks(self._context, requests, caller_module=MODULE_ID)


def _source_fingerprint(
    connection: Connection,
    owner_id: str,
    kind: str,
    identifier: str,
    compute: Callable[..., str],
) -> str:
    if kind == "post":
        row = connection.execute(
            text("SELECT source_snapshot_hash FROM post WHERE owner_id = :o AND id = :i"),
            {"o": owner_id, "i": identifier},
        ).scalar()
        return compute(post_source_snapshot_hashes=[] if row is None else [str(row)])
    version = connection.execute(
        text(
            "SELECT v.content_fingerprint FROM work w"
            "  LEFT JOIN work_version v ON v.id = w.current_work_version_id"
            " WHERE w.owner_id = :o AND w.id = :i"
        ),
        {"o": owner_id, "i": identifier},
    ).scalar()
    hashes = [
        str(row[0])
        for row in connection.execute(
            text(
                "SELECT p.source_snapshot_hash FROM post p"
                "  JOIN post_work pw ON pw.post_id = p.id"
                " WHERE pw.owner_id = :o AND pw.work_id = :i"
            ),
            {"o": owner_id, "i": identifier},
        )
    ]
    return compute(
        work_version_content_fingerprint=None if version is None else str(version),
        post_source_snapshot_hashes=hashes,
    )


__all__ = [
    "EMERGING_DIRECTION_LABEL",
    "MODULE_ID",
    "AnalysisEnqueuePort",
    "BackfillPort",
    "BuildSnapshot",
    "Candidate",
    "DensityParameters",
    "EmbeddingPort",
    "EmergingDirection",
    "ExcludedBy",
    "MatchedTag",
    "NoBackfill",
    "PendingEntry",
    "SelectedItem",
    "SelectionSettings",
    "ServiceAnalysisEnqueue",
    "ServiceBackfill",
    "TagConfigVersion",
    "TagConfigVersionPort",
    "TagDefinition",
    "TagExclusion",
    "TagSet",
    "build_report",
    "round_half_up",
]
