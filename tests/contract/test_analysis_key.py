"""E1 — the analysis key does not move when a tag moves (REQ-AC06, I04, ADR-0008).

The fixtures under ``acceptance/fixtures/`` are the only oracle (SRC-PLAN §15) and
``contracts/data/entities.yaml`` is the only definition of the key. Nothing here writes a
second list of components: the seven names and the deliberate exclusions are **read out of
the contract** and compared with the code, so a future edit that adds an eighth component
fails here rather than quietly re-pricing the corpus.

What this file is really asserting
----------------------------------
AC-06 says: remove a tag, add it back, and the model is not called again. That promise is
not a piece of control flow anyone can inspect -- it is a property of the *key*. If the key
were a function of the tag set, no amount of careful branching downstream could keep the
promise; because it is not, the promise holds even for code paths nobody has written yet.
So the test for AC-06 at this level is: **take a tag edit, and show that not one of the
seven components changes.**

Scenario anchors: SC06 (tag removed then re-added), SC28 (same key resubmitted).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from server.app.analysis.key import (
    ANALYSIS_KEY_COMPONENTS,
    EXCLUDED_FROM_ANALYSIS_KEY,
    AnalysisKey,
    AnalysisKeyError,
    analysis_key_from_inputs,
    analysis_key_from_mapping,
    compute_source_fingerprint,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01JW0WNER00000000000000000"


@pytest.fixture(scope="module")
def entity_analysis() -> dict[str, Any]:
    document = yaml.safe_load(
        (REPO_ROOT / "contracts" / "data" / "entities.yaml").read_text("utf-8")
    )
    for entity in document["entities"]:
        if entity["name"] == "analysis":
            return dict(entity)
    raise AssertionError("entities.yaml declares no `analysis` entity")


def _key(**overrides: Any) -> AnalysisKey:
    values: dict[str, Any] = {
        "owner_id": OWNER_ID,
        "target_key": "work:01JWRKA1000000000000000000",
        "task_type": "summary",
        "source_fingerprint": (
            "sha256:858c06cf9c505c9f135e64d506f2e40dcb5bc6992bfd8d97f31e6b7caa8b0d38"
        ),
        "prompt_version": "1.0.0",
        "schema_version": "0.1.0",
        "generation_number": 1,
    }
    values.update(overrides)
    return analysis_key_from_inputs(**values)


# ------------------------------------------------------------------ the key is the contract's


def test_the_seven_components_are_exactly_the_contract_s(entity_analysis) -> None:
    """``ENT-analysis.analysis_key.components``, order included.

    Order matters as well as membership: the components are hashed as a canonical JSON
    object, and the tuple is what the wire comparison in SV-01 walks.
    """
    assert list(ANALYSIS_KEY_COMPONENTS) == list(entity_analysis["analysis_key"]["components"])


def test_every_field_the_contract_excludes_is_refused_by_construction(entity_analysis) -> None:
    """``excluded_deliberately`` is prose; this turns it into a guard.

    The contract names three families -- tag, provider/model, report -- and each is excluded
    for a different reason. The test reads the prose, extracts the field names it mentions,
    and requires each to be in the refusal set: a family that fell out of the code would
    otherwise be invisible until it changed someone's bill.
    """
    prose = " ".join(entity_analysis["analysis_key"]["excluded_deliberately"])
    families = {
        "tag": {"tag", "tag_config_version"},
        "provider": {"provider", "model"},
        "report": {"report_id"},
    }
    for family, names in families.items():
        assert any(name in prose for name in names), f"{family} is no longer excluded in prose"
        assert names <= EXCLUDED_FROM_ANALYSIS_KEY, f"{family} is not refused in code"


def test_key_construction_refuses_a_tag_rather_than_ignoring_it() -> None:
    """Silently dropping the field is the failure mode this guards against.

    Ignoring an excluded name would keep today's behaviour correct and make tomorrow's
    regression silent: whoever threads a tag through would see it accepted and assume it
    counted. The refusal names the field, so the mistake is corrected at the call site.
    """
    with pytest.raises(AnalysisKeyError) as raised:
        _key(extra={"tag_config_version": "01JTCV30000000000000000000"})
    assert "tag_config_version" in str(raised.value)

    for excluded in sorted(EXCLUDED_FROM_ANALYSIS_KEY):
        with pytest.raises(AnalysisKeyError):
            _key(extra={excluded: "whatever"})


def test_an_unknown_component_in_a_submitted_key_is_rejected() -> None:
    """SV-01 compares seven names. An eighth cannot be smuggled past the comparison."""
    payload = _key().as_dict()
    payload["tag_config_version"] = "01JTCV30000000000000000000"
    with pytest.raises(AnalysisKeyError):
        analysis_key_from_mapping(payload)
    del payload["tag_config_version"], payload["prompt_version"]
    with pytest.raises(AnalysisKeyError):
        analysis_key_from_mapping(payload)


# ------------------------------------------------------------------------------ AC-06 proper


def test_a_tag_edit_moves_no_component_of_the_key(fixture_loader) -> None:
    """AC-06 / fixture ``reporting/b``: tag removed, re-added, key unchanged.

    The fixture's ``given`` holds four ``analysis`` rows written while tag ``T`` existed, and
    its first event re-creates ``T`` with a **new** ``tag.id`` and a new
    ``tag_config_version`` (sequence 3). Both of those are inputs to the reporting layer and
    to nothing else. The keys are rebuilt from the fixture's own rows on both sides of that
    event and compared by digest.
    """
    fixture = fixture_loader("reporting/b-tag-removed-then-readded-reuse-analysis")
    rows = fixture.rows("analysis")
    assert rows, "the fixture no longer carries the analysis rows this test reads"

    readded = fixture.events[0]
    assert readded["operation"] == "tag.create"
    new_tag_config_version = readded["produces"]["tag_config_version"]["id"]

    for row in rows:
        before = _key(
            target_key=row["target_key"],
            task_type=row["task_type"],
            generation_number=row["generation_number"],
        )
        # The only thing that changed in the world between these two lines is the tag
        # configuration, and it is not an argument the key function will even accept.
        with pytest.raises(AnalysisKeyError):
            _key(
                target_key=row["target_key"],
                task_type=row["task_type"],
                generation_number=row["generation_number"],
                extra={"tag_config_version_id": new_tag_config_version},
            )
        after = _key(
            target_key=row["target_key"],
            task_type=row["task_type"],
            generation_number=row["generation_number"],
        )
        assert before == after
        assert before.digest() == after.digest()


def test_the_fixture_s_own_counters_state_the_same_thing(fixture_loader) -> None:
    """``counters_before`` in fixture ``b`` is the arithmetic form of the same claim.

    The fixture records the provider call counter, the generation count and the attempt count
    before the tag is re-added, and ``ENT-analysis-generation.ac06_oracle`` requires all three
    deltas to be zero. This asserts the fixture still carries that oracle, so the integration
    test that measures the deltas is measuring the number the contract named.
    """
    fixture = fixture_loader("reporting/b-tag-removed-then-readded-reuse-analysis")
    counters = fixture.given["counters_before"]
    assert counters["provider_call_counter[task_type='summary']"] == 5
    assert counters["analysis_generation"] == 5
    assert counters["analysis_attempt"] == 5


# ------------------------------------------------------------- what DOES move the key


def test_reanalysis_moves_only_the_generation(fixture_loader) -> None:
    """T-AN-12: a new generation is a different key, not a mutation of the old one.

    This is why reanalysis neither collides with ``ux_analysis_valid_key`` nor breaks I04:
    the old row keeps its key and stays valid, and the new work is filed under a key that has
    never had a result.
    """
    first = _key()
    second = first.with_generation(2)
    assert first.digest() != second.digest()
    assert first.same_key_ignoring_generation(second)
    assert second.generation_number == 2


def test_changed_source_content_changes_the_key() -> None:
    """``ENT-analysis.source_fingerprint``: "đổi nội dung nguồn ⇒ đổi key".

    And the converse property, which matters just as much: the fingerprint is stable under
    the *order* the sources come back in. Two queries returning the same posts in different
    orders must not produce two keys, or the model would run twice for one piece of work.
    """
    a = "sha256:" + "a" * 64
    b = "sha256:" + "b" * 64
    assert compute_source_fingerprint(post_source_snapshot_hashes=[a, b]) == (
        compute_source_fingerprint(post_source_snapshot_hashes=[b, a])
    )
    assert compute_source_fingerprint(post_source_snapshot_hashes=[a]) != (
        compute_source_fingerprint(post_source_snapshot_hashes=[a, b])
    )
    # "no work version was available" and "a work version was" are different inputs, so they
    # must not hash alike -- the same distinction a JSON schema draws between absent and null.
    assert compute_source_fingerprint(post_source_snapshot_hashes=[a]) != (
        compute_source_fingerprint(
            post_source_snapshot_hashes=[a], work_version_content_fingerprint=b
        )
    )


def test_the_key_a_worker_submits_round_trips(fixture_loader) -> None:
    """Fixture ``ai/j`` carries a real ``analysis_key``; parsing it must be lossless.

    SV-01 compares the submitted key with the assignment component by component, so a parser
    that dropped or coerced a component would make the comparison meaningless.
    """
    fixture = fixture_loader("ai/j-same-key-resubmitted-one-result")
    submitted = fixture.expected["analysis_result"]["analysis_key"]
    key = analysis_key_from_mapping(submitted)
    assert key.as_dict() == submitted
    assert json.loads(json.dumps(key.as_dict())) == submitted


def test_a_key_cannot_be_built_out_of_contract() -> None:
    """The three shape rules ``entities.yaml`` states, enforced at construction."""
    with pytest.raises(AnalysisKeyError):
        _key(task_type="open_labeling")  # the pre-CR-PC03-05 spelling is not a value
    with pytest.raises(AnalysisKeyError):
        _key(generation_number=0)
    with pytest.raises(AnalysisKeyError):
        _key(source_fingerprint="not-a-hash")
