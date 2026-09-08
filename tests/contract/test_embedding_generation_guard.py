"""E1 — I12: a cosine between two generations is refused, and the counter proves it never ran.

Card ``agent-tasks/TC-embedding-generation-switch.md`` §8 names one oracle above all others:

    Fixture ``l-embedding-generation-switch-blocked.json``: hai generation xen kẽ ⇒ selection
    bị chặn **trước** report commit, 0 phép cosine chéo generation.

"0 cross-generation cosines" is not a property you can assert by reading code, so this file
asserts it the way the fixtures ask for it -- through the instrument
``n-embedding-generation-switch-positive.json`` specifies in ``given.instrumentation_vi``:

    Một bộ đếm bọc quanh hàm similarity, ghi lại (generation_a, generation_b) của MỌI phép
    cosine. Oracle chính của SC52 đọc bộ đếm này.

:class:`~server.app.embedding.generation.ComparisonLedger` is that counter, and every
assertion below reads it rather than reasoning about control flow.

Why the ledger has two counters
-------------------------------
``selection.md`` §5 is explicit that the negative oracle alone is not enough: *"một mình O-5a
không loại trừ được một triển khai chặn mọi thứ và không bao giờ đổi được generation."* An
implementation that refuses every comparison scores zero cross-generation cosines and is
useless. So the tests here assert **both** that ``cross_generation_performed == 0`` and that
same-generation work actually happened (``total_performed > 0``), which no
refuse-everything implementation can satisfy.

The two fixtures used, and what each is for
-------------------------------------------
``reporting/l-embedding-generation-switch-blocked.json``  the negative face (SC24): two
    generations interleaved, selection blocked, the three forbidden escapes (fall back, skip,
    mix) each refused.
``reporting/n-embedding-generation-switch-positive.json``  the positive face (SC52): the
    model change runs end to end, so "blocked" cannot be achieved by blocking everything.

Both are loaded through ``tests/conftest.py``'s ``fixture_loader``; nothing here paraphrases
a fixture into Python constants.
"""

from __future__ import annotations

import ast
import math
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.embedding.generation import (
    COMPONENT_BYTES,
    SCORE_DECIMALS,
    ComparisonLedger,
    DeterministicHashEncoder,
    EmbeddingError,
    GenerationFingerprint,
    GenerationState,
    LocalEncoder,
    Normalization,
    Vector,
    assert_comparable,
    assert_single_generation,
    cosine,
    coverage_satisfied,
    round_half_up,
)
from server.app.embedding.service import ALLOWED_CALLERS, EmbeddingService

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = REPO_ROOT / "server" / "app" / "embedding"

BLOCKED_FIXTURE = "reporting/l-embedding-generation-switch-blocked"
POSITIVE_FIXTURE = "reporting/n-embedding-generation-switch-positive"
#: In card §2 but mostly not this card's; only its I12 slice is exercised. See the section
#: comment further down for what is exercised and what is recorded ``NOT_RUN``.
DENSITY_FIXTURE = "reporting/m-density-worked-example"


# --- helpers ----------------------------------------------------------------------------------


def fingerprint_of(row: dict[str, Any]) -> GenerationFingerprint:
    """Build a fingerprint from a fixture's ``embedding_generation`` row.

    Read from the fixture, never transcribed: the dimensions (4 for G1, 8 for G2) are the
    reason the two generations are incomparable, so hard-coding them here would move the
    oracle out of the fixture and into this file.
    """
    return GenerationFingerprint(
        generation_id=row["id"],
        model_name=row["model_name"],
        model_version=row["model_version"],
        dimension=int(row["dimension"]),
        normalization=Normalization(row["normalization"]),
    )


def vector_for(fingerprint: GenerationFingerprint, text: str) -> Vector:
    """A deterministic vector of the right dimension for ``fingerprint``."""
    encoder = DeterministicHashEncoder(
        model_name=fingerprint.model_name,
        model_version=fingerprint.model_version,
        dimension=fingerprint.dimension,
        normalization=fingerprint.normalization,
    )
    return Vector(fingerprint=fingerprint, values=encoder.encode([text])[0])


@pytest.fixture
def generations(fixture_loader) -> dict[str, GenerationFingerprint]:  # type: ignore[no-untyped-def]
    """G1 and G2 of the blocked fixture, keyed by id."""
    rows = fixture_loader(BLOCKED_FIXTURE).rows("embedding_generation")
    return {row["id"]: fingerprint_of(row) for row in rows}


@pytest.fixture(scope="module")
def modules_yaml() -> dict[str, Any]:
    import yaml

    document: dict[str, Any] = yaml.safe_load(
        (REPO_ROOT / "contracts" / "modules.yaml").read_text("utf-8")
    )
    return document


@pytest.fixture(scope="module")
def contract_allowed_edges(modules_yaml) -> dict[str, frozenset[str]]:  # type: ignore[no-untyped-def]
    """``allowed_edges`` into ``MOD-embedding-service``, keyed by operation id.

    Read from the registry each run so that an edge added or removed by change control makes
    :func:`test_allowed_callers_match_contracts_modules_yaml` fail instead of leaving a stale
    copy in Python agreeing with itself.
    """
    edges: dict[str, set[str]] = {}
    for edge in modules_yaml["allowed_edges"]:
        if edge["callee"] != "MOD-embedding-service":
            continue
        edges.setdefault(edge["operation"], set()).add(edge["caller"])
    return {operation: frozenset(callers) for operation, callers in edges.items()}


@pytest.fixture(scope="module")
def contract_operation_ids() -> frozenset[str]:
    import yaml

    document = yaml.safe_load((REPO_ROOT / "contracts" / "ports.yaml").read_text("utf-8"))
    return frozenset(operation["operation_id"] for operation in document["operations"])


# --- the negative face: SC24 / fixture l -------------------------------------------------------


def test_the_blocked_fixture_really_does_carry_two_incomparable_generations(
    fixture_loader,
) -> None:
    """Premise check. If the fixture ever stopped mixing generations these tests would pass
    for the wrong reason, so the mixture is asserted before it is relied on."""
    rows = fixture_loader(BLOCKED_FIXTURE).rows("embedding_generation")
    assert len(rows) == 2
    fingerprints = {fingerprint_of(row) for row in rows}
    assert len({f.generation_id for f in fingerprints}) == 2
    assert len({f.dimension for f in fingerprints}) == 2, "the fixture's dimensions converged"
    states = {row["state"] for row in rows}
    assert states == {GenerationState.ACTIVE.value, GenerationState.BUILDING.value}


def test_cosine_across_two_generations_is_refused_and_never_performed(generations) -> None:
    """O-5a: the comparison the whole card exists to prevent.

    The assertion is not only "it raised" -- an implementation could multiply first and raise
    afterwards, having already leaked the number into a score. The ledger says the arithmetic
    never ran.
    """
    g1, g2 = (generations[key] for key in sorted(generations))
    ledger = ComparisonLedger()
    a = vector_for(g1, "graph neural networks")
    b = vector_for(g2, "graph neural networks")

    with pytest.raises(EmbeddingError) as raised:
        cosine(a, b, ledger=ledger)

    assert raised.value.code is ErrorCode.EMBEDDING_GENERATION_MISMATCH
    assert ledger.total_performed == 0
    assert ledger.cross_generation_performed == 0
    assert ledger.total_refused == 1


def test_the_refusal_envelope_is_the_one_the_contract_registers(generations) -> None:
    """Card §7 + ``contracts/errors.yaml`` ``error_envelope``: seven fields, safe details only.

    ``redaction_vi`` for this code is "Không xuất giá trị vector", so the test asserts the
    envelope's ``details_safe`` keys are a subset of the registered ones -- which is what
    makes leaking a vector impossible rather than merely unintended.
    """
    g1, g2 = (generations[key] for key in sorted(generations))
    with pytest.raises(EmbeddingError) as raised:
        assert_comparable(g1, g2)

    envelope = raised.value.envelope("01J0000000000000000000000Z")
    assert envelope["code"] == ErrorCode.EMBEDDING_GENERATION_MISMATCH.value
    assert envelope["scope"] == SCOPE[ErrorCode.EMBEDDING_GENERATION_MISMATCH]
    assert envelope["retry_class"] == RETRY_CLASS[ErrorCode.EMBEDDING_GENERATION_MISMATCH]
    assert envelope["correlation_id"] == "01J0000000000000000000000Z"
    assert set(envelope["details_safe"]) <= {
        "expected_generation_id",
        "seen_generation_id",
        "dimension_expected",
        "dimension_seen",
    }
    assert envelope["details_safe"]["expected_generation_id"] == g1.generation_id
    assert envelope["details_safe"]["seen_generation_id"] == g2.generation_id
    serialised = repr(envelope)
    assert "0." not in envelope["message_safe"], "message_safe must not carry a score"
    assert "vector" not in serialised.lower() or "expected_generation_id" in serialised


def test_a_generation_that_differs_only_in_model_or_normalization_is_still_refused() -> None:
    """``selection.md`` §5: same id is not enough; model, version, dimension and
    normalization all take part.

    Worth its own test because "same generation id" is the check a reasonable implementation
    writes first, and it is the check that would let a re-pointed generation row -- same id,
    new model -- slip a comparison through.
    """
    base = GenerationFingerprint("01JEMBGEN10000000000000000", "m", "1.0.0", 4, Normalization.L2)
    variants = [
        GenerationFingerprint(base.generation_id, "other", "1.0.0", 4, Normalization.L2),
        GenerationFingerprint(base.generation_id, "m", "2.0.0", 4, Normalization.L2),
        GenerationFingerprint(base.generation_id, "m", "1.0.0", 8, Normalization.L2),
        GenerationFingerprint(base.generation_id, "m", "1.0.0", 4, Normalization.NONE),
    ]
    for variant in variants:
        ledger = ComparisonLedger()
        with pytest.raises(EmbeddingError) as raised:
            assert_comparable(base, variant, ledger=ledger)
        assert raised.value.code is ErrorCode.EMBEDDING_GENERATION_MISMATCH
        assert ledger.total_performed == 0


def test_a_mixed_candidate_set_is_refused_before_any_scoring(generations) -> None:
    """``selection.md`` §5.3 and fixture ``l``'s ``forbidden_effects``.

    The three escapes the contract forbids by name -- fall back to the old generation for the
    tags missing in the new one, skip those tags, publish a mixed period -- are all "score
    what you can". This asserts the guard runs over the *whole* candidate set first, so there
    is no partial score to be tempted by.
    """
    g1, g2 = (generations[key] for key in sorted(generations))
    ledger = ComparisonLedger()
    candidates = [vector_for(g1, "a"), vector_for(g1, "b"), vector_for(g2, "c")]

    with pytest.raises(EmbeddingError) as raised:
        assert_single_generation(
            (candidate.fingerprint for candidate in candidates), expected=g1, ledger=ledger
        )

    assert raised.value.code is ErrorCode.EMBEDDING_GENERATION_MISMATCH
    assert ledger.total_performed == 0


def test_a_null_vector_is_absent_from_the_set_and_is_not_scored_zero(fixture_loader) -> None:
    """Fixture ``l``: ``work:Q3`` has ``_vector_present: false``.

    ``forbidden_effects`` includes "Coi vector NULL là điểm tương đồng 0 (phải loại khỏi tập,
    không phải cho điểm)". The distinction is not cosmetic: a zero score is a measurement that
    says "dissimilar", and the fixture's row oracle requires Q3 to remain a candidate in a
    later period rather than be recorded as a permanent non-match.

    There is no vector to hand to :func:`cosine` for such a row, which is the point -- the
    repository's ``labels()`` query filters ``vector IS NOT NULL``, so the row never reaches
    the scorer at all. Here that is asserted at the level this file can reach: a degenerate
    zero vector, the closest thing to "nothing" the arithmetic can be handed, is refused
    rather than scored.
    """
    rows = fixture_loader(BLOCKED_FIXTURE).rows("work_label")
    absent = [row for row in rows if row.get("_vector_present") is False]
    assert absent, "the fixture no longer carries a NULL-vector label"

    fingerprint = GenerationFingerprint(
        "01JEMBGEN10000000000000000", "m", "1.0.0", 4, Normalization.L2
    )
    zero = Vector(fingerprint=fingerprint, values=(0.0, 0.0, 0.0, 0.0))
    other = vector_for(fingerprint, "graph neural networks")
    ledger = ComparisonLedger()

    with pytest.raises(EmbeddingError) as raised:
        cosine(zero, other, ledger=ledger)
    assert raised.value.code is ErrorCode.VALIDATION_ERROR


# --- the positive face: SC52 / fixture n -------------------------------------------------------


def test_same_generation_comparisons_are_performed_and_counted(generations) -> None:
    """The half that stops "refuse everything" from passing (``selection.md`` §5, O-5b)."""
    g1 = generations["01JEMBGEN10000000000000000"]
    ledger = ComparisonLedger()

    identical = cosine(vector_for(g1, "x"), vector_for(g1, "x"), ledger=ledger)
    different = cosine(vector_for(g1, "x"), vector_for(g1, "y"), ledger=ledger)

    assert identical == pytest.approx(1.0)
    assert -1.0 <= different <= 1.0
    assert ledger.total_performed == 2
    assert ledger.cross_generation_performed == 0
    assert ledger.generations_touched == {g1.generation_id}


def test_scores_are_rounded_to_the_four_decimals_selection_md_specifies(generations) -> None:
    """``selection.md`` §3: ``[round 4dp]``, in one place so two callers cannot disagree."""
    g1 = generations["01JEMBGEN10000000000000000"]
    score = cosine(vector_for(g1, "alpha"), vector_for(g1, "beta"))
    assert score == round_half_up(score)
    assert Decimal(str(score)).as_tuple().exponent >= -SCORE_DECIMALS


def test_rounding_is_half_up_and_not_pythons_half_to_even() -> None:
    """``CR-TC-REPORT-04``. ``selection.md`` §3: *"làm tròn **half-up** về 4 chữ số thập phân"*,
    and its parameter table repeats it (``rounding: half-up``).

    Python's ``round`` rounds half to **even**, so the two disagree on exactly the inputs that
    sit on a tie — which is the worst place to disagree, because a tie is a score sitting on
    the threshold the comparison is about. ``0.15625`` is a genuine tie: it is exactly
    representable in binary (5/32), so ``Decimal(0.15625)`` really is ``0.15625`` and the
    fourth decimal really is a coin flip between the two rules.

    Both directions are asserted, and the divergence from the built-in is asserted too — a
    test that only checked the expected value would still pass if someone put ``round`` back
    and the platform happened to agree.
    """
    assert round_half_up(0.15625) == 0.1563
    assert round(0.15625, SCORE_DECIMALS) == 0.1562, "the premise moved: no longer a tie"
    assert round_half_up(0.15625) != round(0.15625, SCORE_DECIMALS)

    assert round_half_up(0.03125) == 0.0313
    assert round(0.03125, SCORE_DECIMALS) == 0.0312

    # Half **away from zero**, so a negative tie goes to the larger magnitude. Cosine is
    # legitimately negative, so this half is not hypothetical.
    assert round_half_up(-0.15625) == -0.1563
    assert round_half_up(-0.03125) == -0.0313

    # Values that are not ties are unaffected, in both rules.
    for value in (0.1234, 0.98765431, -0.5, 0.0, 1.0):
        assert round_half_up(value) == pytest.approx(round(value, SCORE_DECIMALS))


def test_cosine_rounds_its_own_result_with_the_half_up_rule(generations) -> None:
    """The link between the rule and the function that applies it.

    The raw quotient is recomputed here the way :func:`cosine` computes it and passed through
    :func:`round_half_up`; the two must agree. That is what stops the rule from being correct
    in isolation while ``cosine`` quietly keeps calling the built-in.
    """
    g1 = generations["01JEMBGEN10000000000000000"]
    a = vector_for(g1, "graph neural networks")
    b = vector_for(g1, "molecular property prediction")

    dot = math.fsum(x * y for x, y in zip(a.values, b.values, strict=True))
    norm_a = math.sqrt(math.fsum(x * x for x in a.values))
    norm_b = math.sqrt(math.fsum(y * y for y in b.values))

    assert cosine(a, b) == round_half_up(dot / (norm_a * norm_b))


def test_the_activation_guard_is_built_greater_or_equal_expected(fixture_loader) -> None:
    """``entities.yaml``: "Guard chuyển active: built >= expected", read off fixture ``n``.

    Event 7 of that fixture attempts activation at ``built=2, expected=4`` and pins the
    refusal; event 9 activates at ``built=4``. Both numbers come from the fixture.
    """
    expected_rows = fixture_loader(POSITIVE_FIXTURE).data["expected"]
    building = next(
        row
        for row in expected_rows["after_event_6"]["rows"]["embedding_generation"]
        if row["state"] == GenerationState.BUILDING.value
    )
    assert not coverage_satisfied(
        built=int(building["built_vector_count"]),
        expected=int(building["expected_vector_count"]),
    )

    activated = next(
        row
        for row in expected_rows["after_event_9"]["rows"]["embedding_generation"]
        if row["state"] == GenerationState.ACTIVE.value
    )
    assert coverage_satisfied(
        built=int(activated["built_vector_count"]),
        expected=int(activated["expected_vector_count"]),
    )


def test_an_unknown_expected_count_is_not_a_satisfied_one() -> None:
    """``expected_vector_count`` is nullable, and NULL is not evidence of coverage.

    ``ports.yaml`` wants "bằng chứng đã đủ vector" before an activation; a row that never
    recorded a target has produced none, and answering True would make the guard vacuous for
    exactly the generations most likely to be half-built.
    """
    assert coverage_satisfied(built=10, expected=None) is False
    assert coverage_satisfied(built=0, expected=0) is True


# --- fixture m: the I12 slice of the density worked example ------------------------------------
#
# ``m-density-worked-example.json`` is in card §2 and is mostly **not** this card's: the density
# algorithm belongs to ``TC-report-coverage-publish-cas`` and card §1 lists it as a non-goal.
# But the fixture carries ``invariant_refs: ["I12"]`` and one forbidden effect that is squarely
# this module's -- *"So sánh với kỳ trước thuộc embedding generation khác (I12)"* -- so the part
# of it that this card owns is exercised here rather than left unread. What is **not** exercised
# is recorded ``NOT_RUN`` with its reason in the evidence manifest and the handoff addendum;
# see :func:`test_the_density_parameters_are_left_untouched_by_this_card` for the boundary.


def _embedding_generation_blocks(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Every full ``embedding_generation`` descriptor anywhere in a fixture.

    A walk rather than a list of paths: a hard-coded path list would quietly stop covering a
    block if the fixture grew one. "Full" means it names the model as well as the id -- three
    of these exist in fixture ``m`` (``given``, ``expected.report`` and the below-min-sample
    variant's report); the cold-start direction carries only the id, which
    :func:`_embedding_generation_ids` picks up instead.
    """
    found: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "model_name" in node and "dimension" in node and "normalization" in node:
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return found


def _embedding_generation_ids(data: dict[str, Any]) -> list[str]:
    """Every ``embedding_generation_id`` value anywhere, including bare references.

    Separate from the block walk because the two catch different things and both matter: a
    report can *name* a generation without restating the model, and a stray id is exactly how
    a second generation would enter a density baseline unnoticed.
    """
    found: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "embedding_generation_id" and isinstance(value, str):
                    found.append(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return found


def test_the_density_example_never_spans_two_generations(fixture_loader) -> None:
    """Fixture ``m``'s ``forbidden_effects``: no comparison with a prior period of another
    generation (I12).

    The worked example is a whole report period with prior windows, variants and a cold start,
    and **every** generation reference in it is the same one. Collapsing all of them through
    :class:`GenerationFingerprint` turns that into a single assertion: if the set has more than
    one member, some part of the example spans two generations and the density baseline would
    be crossing I12.
    """
    data = fixture_loader(DENSITY_FIXTURE).data
    blocks = _embedding_generation_blocks(data)
    references = _embedding_generation_ids(data)
    assert len(blocks) >= 3, f"the fixture no longer carries its generation blocks: {len(blocks)}"
    assert len(references) >= 6, f"the fixture no longer names its generation: {len(references)}"
    assert len(set(references)) == 1, set(references)

    fingerprints = {
        GenerationFingerprint(
            generation_id=block["embedding_generation_id"],
            model_name=block["model_name"],
            model_version=block["model_version"],
            dimension=int(block["dimension"]),
            normalization=Normalization(block["normalization"]),
        )
        for block in blocks
    }
    assert len(fingerprints) == 1, fingerprints
    assert {f.generation_id for f in fingerprints} == set(references)

    # And the guard agrees: the whole example passes the single-generation check with zero
    # comparisons refused, which is the positive half -- a guard that refused this would be
    # blocking a period that is perfectly legal.
    (pinned,) = fingerprints
    ledger = ComparisonLedger()
    assert_single_generation(fingerprints, expected=pinned, ledger=ledger)
    assert ledger.total_refused == 0
    assert ledger.cross_generation_performed == 0


def test_the_cold_start_period_after_a_switch_has_no_prior_baseline(fixture_loader) -> None:
    """Fixture ``m``'s ``variant_cold_start``: the first period after
    ``embedding.activate_generation``.

    ``insufficient_reason = 'generation_reset'`` is the report-side name for the consequence
    this card's switch creates: periods built under the previous generation are not a baseline
    for periods built under the new one. Asserted from the fixture, and the direction block's
    own ``embedding_generation_id`` is checked to be the current generation rather than the
    retired one -- the I12 face of it. Computing the density itself is not this card's.
    """
    variant = fixture_loader(DENSITY_FIXTURE).data["expected"]["variant_cold_start"]
    direction = variant["expected_direction"]

    assert direction["evidence_state"] == "insufficient_evidence"
    assert direction["insufficient_reason"] == "generation_reset"
    assert direction["member_target_keys"] == []
    given = fixture_loader(DENSITY_FIXTURE).data["given"]["embedding_generation"]
    assert direction["embedding_generation_id"] == given["embedding_generation_id"]


def test_the_density_parameters_are_left_untouched_by_this_card(fixture_loader) -> None:
    """The boundary, asserted rather than described (card §1 non-goal, §10 ``SG-01``).

    Two of the fixture's parameters *are* this card's, because they describe the comparison
    function rather than the density rule: ``metric`` and ``rounding_decimals``. Those are
    checked against the shipped code. The other six -- ``radius``, ``min_members``,
    ``comparison_window_k``, ``min_prior_windows``, ``min_delta``, ``prior_floor`` -- are
    ``PROVISIONAL_BOOTSTRAP`` behind ``REQ-A4``/``REQ-OQ08`` and belong to
    ``TC-report-coverage-publish-cas``; this asserts only that they are still marked
    provisional, so that nothing here reads as a calibrated number.
    """
    parameters = fixture_loader(DENSITY_FIXTURE).data["parameters"]

    assert parameters["metric"] == "cosine"
    assert parameters["rounding_decimals"] == SCORE_DECIMALS
    assert parameters["parameters_status"] == "PROVISIONAL_BOOTSTRAP"
    assert set(parameters) >= {
        "radius",
        "min_members",
        "comparison_window_k",
        "min_prior_windows",
        "min_delta",
        "prior_floor",
    }


# --- the vector blob: entities.yaml "độ dài phải khớp dimension" -------------------------------


def test_a_vector_whose_length_is_not_the_dimension_cannot_be_constructed() -> None:
    with pytest.raises(EmbeddingError) as raised:
        Vector(
            fingerprint=GenerationFingerprint(
                "01JEMBGEN10000000000000000", "m", "1.0.0", 4, Normalization.L2
            ),
            values=(1.0, 2.0, 3.0),
        )
    assert raised.value.code is ErrorCode.VALIDATION_ERROR


def test_blob_round_trip_preserves_the_vector_and_refuses_a_wrong_length() -> None:
    """SQLite cannot CHECK a length against another table's column, so both edges enforce it."""
    fingerprint = GenerationFingerprint(
        "01JEMBGEN10000000000000000", "m", "1.0.0", 4, Normalization.L2
    )
    vector = vector_for(fingerprint, "round trip")
    blob = vector.to_blob()

    assert len(blob) == fingerprint.dimension * COMPONENT_BYTES
    assert Vector.from_blob(blob, fingerprint) == vector

    wider = GenerationFingerprint("01JEMBGEN20000000000000000", "m", "1.0.0", 8, Normalization.L2)
    with pytest.raises(EmbeddingError) as raised:
        Vector.from_blob(blob, wider)
    assert raised.value.code is ErrorCode.VALIDATION_ERROR


# --- default deny at this module's port (card §5, SG-DENY) -------------------------------------


def test_allowed_callers_match_contracts_modules_yaml(contract_allowed_edges) -> None:
    """The allow list is the registry's, not a hand-kept copy.

    ``contracts/modules.yaml`` ``allowed_edges`` is read and compared entry by entry, so an
    edge added or removed by change control shows up here as a failure rather than as a
    divergence nobody notices.
    """
    for operation_id, callers in ALLOWED_CALLERS.items():
        assert callers == contract_allowed_edges[operation_id.value], operation_id


@pytest.mark.parametrize(
    "operation_id",
    sorted(ALLOWED_CALLERS, key=lambda op: op.value),
)
def test_an_unregistered_caller_is_refused_with_forbidden_edge(operation_id) -> None:
    """Ruling R5-01 row 2: an in-process call over an unregistered edge is ``FORBIDDEN_EDGE``.

    Not ``UNAUTHORIZED`` -- that answers "wrong principal class at the HTTP boundary", and all
    four ``embedding.*`` operations are ``transport: internal`` with no HTTP path. Card §10
    ``SG-DENY``: the wrong code is a FAIL even when the behaviour is right.
    """
    with pytest.raises(EmbeddingError) as raised:
        EmbeddingService.assert_caller_allowed(operation_id, "MOD-x-collector")
    assert raised.value.code is ErrorCode.FORBIDDEN_EDGE
    assert raised.value.details_safe["callee_module"] == "MOD-embedding-service"


def test_the_analysis_worker_is_not_an_allowed_caller_of_any_embedding_operation() -> None:
    """``contracts/ports.yaml`` (worker health): "Worker **không bao giờ** khai ``embedding``"
    (D50/B12). The worker holds no edge into this module at all."""
    for callers in ALLOWED_CALLERS.values():
        assert "MOD-analysis-worker" not in callers
        assert "MOD-ai-adapter" not in callers


# --- FE-22 and FE-23, asserted about the shipped source ----------------------------------------

#: Modules and libraries this package may not reach. ``FE-22`` (embedding →
#: ``EXT-ai-provider-api``, ``CAPABILITY_DENIED``) is enforced by an empty ``network_egress``
#: and by ``ENF-import-rule``; ``FE-23`` (embedding → ``MOD-tag-service``,
#: ``FORBIDDEN_EDGE``) by ``ENF-import-rule`` alone. An import rule is testable here, and
#: ``tests/integration/test_denied_edges.py`` records ``FE-22`` as
#: ``NOT_TESTABLE_AT_THIS_LAYER`` for the *sandbox* half, which this does not claim to close.
FORBIDDEN_IMPORTS = frozenset(
    {
        "httpx",
        "requests",
        "urllib",
        "urllib3",
        "socket",
        "http",
        "aiohttp",
        "subprocess",
        "anthropic",
        "openai",
        "server.app.tag",
    }
)


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None and node.level == 0:
            names.add(node.module)
    return names


@pytest.mark.parametrize("source", sorted(PACKAGE_ROOT.glob("*.py")), ids=lambda p: p.name)
def test_the_embedding_package_imports_no_network_and_no_tag_module(source: Path) -> None:
    """FE-22 and FE-23 as a property of the bytes that shipped, not of a paragraph.

    ``sentence_transformers`` is deliberately absent from the forbidden set: it is the local
    model ADR-0011 names, imported lazily and constructed with ``local_files_only=True``. A
    library that loads a file is not an egress; a client that opens a socket is, and every
    name in :data:`FORBIDDEN_IMPORTS` is one of the latter.
    """
    imported = _imported_modules(source)
    for name in imported:
        root = name.split(".")[0]
        assert root not in FORBIDDEN_IMPORTS, f"{source.name} imports {name}"
        assert name not in FORBIDDEN_IMPORTS, f"{source.name} imports {name}"


def test_the_encoder_port_has_nowhere_to_put_a_credential() -> None:
    """``secret_access: none``: the local encoder protocol exposes no endpoint and no key."""
    attributes = set(dir(LocalEncoder))
    for forbidden in ("api_key", "base_url", "endpoint", "token", "secret_ref"):
        assert forbidden not in attributes


def test_the_deterministic_encoder_is_a_function_of_text_and_model() -> None:
    """The stand-in has to be *deterministic* for the fixtures to be oracles at all.

    It is not a model and this asserts nothing about embedding quality -- ``REQ-OQ09`` is
    still open and this card records the real-model checks as ``NOT_RUN``.
    """
    encoder = DeterministicHashEncoder("m", "1.0.0", 6, Normalization.L2)
    assert encoder.encode(["graph neural networks"]) == encoder.encode(["graph neural networks"])
    assert encoder.encode(["a"]) != encoder.encode(["b"])

    other_version = DeterministicHashEncoder("m", "2.0.0", 6, Normalization.L2)
    assert other_version.encode(["a"]) != encoder.encode(["a"])

    (values,) = encoder.encode(["unit length under l2"])
    assert sum(value * value for value in values) == pytest.approx(1.0)


# --- the operation ids are the contract's ------------------------------------------------------


def test_the_four_operations_this_card_produces_are_the_contract_s(contract_operation_ids) -> None:
    """Card §4: the four ids come from ``contracts/ports.yaml`` and are not near-misses."""
    produced = {
        OperationId.EMBEDDING_GENERATE_VECTORS,
        OperationId.EMBEDDING_GET_ACTIVE_GENERATION,
        OperationId.EMBEDDING_START_GENERATION_REBUILD,
        OperationId.EMBEDDING_ACTIVATE_GENERATION,
    }
    assert {op.value for op in produced} <= contract_operation_ids
    assert set(ALLOWED_CALLERS) == produced
