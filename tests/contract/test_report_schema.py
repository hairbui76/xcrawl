"""E1 -- ``contracts/schemas/report.schema.json`` is the wire oracle of a published period.

Three questions, and they are not the same question:

1. **Do the fixtures validate?** ``acceptance/fixtures/reporting/*`` carry ``expected.report``
   objects that PC04 wrote by hand. If one of them stopped validating, either the schema or the
   fixture drifted, and this file would say so before any code was blamed.
2. **Does what this card *produces* validate?** A real ``report.build`` -> ``report.publish``
   runs against a database created by the real migrations, and the returned read model is
   validated against the same schema. Passing (1) without (2) would mean the schema is
   satisfiable but this implementation does not satisfy it.
3. **Does the read model survive a round trip?** ``report.get`` rebuilds the object from
   stored rows; the rebuilt object must validate *and* hash to the stored ``content_hash``.
   That equality is the I05 oracle, and it is what makes "delivery does not change published
   content" a measurement rather than a promise.

``target.schema.json`` in the resolver store
---------------------------------------------
``report_item.target`` is an external ``$ref`` to the tagged union. It is registered by ``$id``
rather than inlined so that the two files stay separately owned -- and so that a ``post``
target carrying a ``work``'s ``identity_state`` is caught, which the two branches'
``additionalProperties: false`` makes possible.

Not covered here
----------------
Whether the *content* is useful is E4 and out of scope (card §8, "Tính hữu ích của nội dung là
E4"). Whether the similarity threshold separates signal from noise is REQ-A2 and remains
``uncalibrated``; every report this file produces carries
``coverage_note.threshold_calibration_state = 'uncalibrated'`` and the assertion below pins
that, because a report that silently claimed calibration would be the more dangerous defect.
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import yaml
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from sqlalchemy import Engine, text

from server.app.auth.service import AuthService
from server.app.db import create_sqlite_engine
from server.app.embedding.generation import (
    DeterministicHashEncoder,
    GenerationFingerprint,
    Normalization,
    Vector,
)
from server.app.embedding.service import EmbeddingService
from server.app.main import create_app
from server.app.report.builder import (
    EMERGING_DIRECTION_LABEL,
    DensityParameters,
    SelectionSettings,
    TagConfigVersion,
    build_report,
    round_half_up,
)
from server.app.report.coverage import SELECTION_VERSION, canonical_json, content_hash_of
from server.app.report.publisher import (
    PublishContext,
    publish_report,
    read_model,
    record_build,
    verify_content_hash,
)
from server.app.report.router import UNWIRED_MESSAGE_SAFE

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = REPO_ROOT / "contracts" / "schemas"
FIXTURES = REPO_ROOT / "acceptance" / "fixtures" / "reporting"

OWNER_ID = "01JW0WNER00000000000000000"
GENERATION_ID = "01JEMBGEN10000000000000000"
MODEL_NAME = "multilingual-e5-small"
MODEL_VERSION = "1.0.0"
DIMENSION = 4
MOD_JOB = "MOD-job-service"
OWNER_NAME = "owner"
OWNER_PASSWORD = "correct horse battery staple"
WIRE_HEADERS = {
    "X-Schema-Version": CONTRACT_SCHEMA_VERSION,
    "X-Request-Id": "01J0000000000000000000000Z",
}
REPORT_ROUTES = ("/v1/reports", "/v1/reports/01JRPT10000000000000000000")
TAG_ID = "01JTAGPFD00000000000000000"
TCV1 = "01JTCV10000000000000000000"

FINGERPRINT = GenerationFingerprint(
    generation_id=GENERATION_ID,
    model_name=MODEL_NAME,
    model_version=MODEL_VERSION,
    dimension=DIMENSION,
    normalization=Normalization.L2,
)


# --- the validator ------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def validator() -> Draft202012Validator:
    schema = json.loads((CONTRACTS / "report.schema.json").read_text("utf-8"))
    target = json.loads((CONTRACTS / "target.schema.json").read_text("utf-8"))
    Draft202012Validator.check_schema(schema)
    registry = Registry().with_resource(target["$id"], Resource.from_contents(target))
    return Draft202012Validator(
        schema, registry=registry, format_checker=Draft202012Validator.FORMAT_CHECKER
    )


def assert_valid(validator: Draft202012Validator, body: Any) -> None:
    errors = sorted(validator.iter_errors(body), key=str)
    assert not errors, "\n".join(
        f"{list(error.absolute_path)}: {error.message}" for error in errors
    )


# --- (1) the fixtures --------------------------------------------------------------------------


FIXTURES_WITH_REPORT = [
    "a-tag-removed-before-publish",
    "h-already-announced-work-becomes-reference",
    "i-identity-merge-single-first-announced",
    "m-density-worked-example",
    "n-embedding-generation-switch-positive",
]


@pytest.mark.parametrize("name", FIXTURES_WITH_REPORT)
def test_every_fixture_report_validates(name: str, validator: Draft202012Validator) -> None:
    """The acceptance oracles are themselves schema-valid. Read-only: never edited to pass."""
    data = json.loads((FIXTURES / f"{name}.json").read_text("utf-8"))
    assert_valid(validator, data["expected"]["report"])


def test_the_emerging_direction_label_is_a_contract_constant() -> None:
    """REQ-D54 / B14: the block is "ứng viên để đọc sâu", never "phát hiện mới".

    Asserted against the schema's ``const`` rather than against a copy of the string, so the
    two cannot drift apart. This is a wording rule with teeth: calling the block a discovery
    would be a claim about scientific novelty that no part of this system is entitled to make.
    """
    schema = json.loads((CONTRACTS / "report.schema.json").read_text("utf-8"))
    label = schema["$defs"]["emerging_direction"]["properties"]["label"]
    assert label["const"] == EMERGING_DIRECTION_LABEL


def test_insufficient_evidence_may_not_carry_members(validator: Draft202012Validator) -> None:
    """B14 as a negative: ``insufficient_evidence`` with members must be **rejected**.

    Without this the positive tests would also pass for an implementation that labels a
    two-member cluster "insufficient" while still listing it as a direction -- the exact
    dressing-up B14 forbids.
    """
    data = json.loads((FIXTURES / "a-tag-removed-before-publish.json").read_text("utf-8"))
    body = json.loads(json.dumps(data["expected"]["report"]))
    body["emerging_directions"][0]["member_target_keys"] = ["work:01JWRKA1000000000000000000"]
    assert list(validator.iter_errors(body)), "a member list under insufficient_evidence passed"


def test_a_published_report_may_not_have_zero_items(validator: Draft202012Validator) -> None:
    """REQ-D57 / AMD-B04: an empty period has no read model at all, so ``items`` is never [].

    The empty period lives in the coverage ledger; a published report with no items would be
    exactly the "empty digest" the contract refuses to send.
    """
    data = json.loads((FIXTURES / "a-tag-removed-before-publish.json").read_text("utf-8"))
    body = json.loads(json.dumps(data["expected"]["report"]))
    body["items"] = []
    assert list(validator.iter_errors(body)), "a published report with no items passed"


# --- harness for (2) and (3) ---------------------------------------------------------------------


def _upgrade(db_path: Path) -> None:
    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(db_path)
    try:
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    db_path = tmp_path / "radar.db"
    _upgrade(db_path)
    built = create_sqlite_engine(db_path)
    with built.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana,"
                " created_at, password_hash, password_updated_at, failed_login_count,"
                " locked_until) VALUES (:id, 1, 'owner', 'Asia/Ho_Chi_Minh',"
                " '2026-09-01T00:00:00.000Z', 'x', '2026-09-01T00:00:00.000Z', 0, NULL)"
            ),
            {"id": OWNER_ID},
        )
        connection.execute(
            text(
                "INSERT INTO embedding_generation (id, owner_id, model_name, model_version,"
                " dimension, normalization, state, expected_vector_count, built_vector_count,"
                " created_at, activated_at) VALUES (:id, :owner, :name, :version, :dim, 'l2',"
                " 'active', 8, 8, '2026-09-01T02:00:00.000Z', '2026-09-01T02:30:00.000Z')"
            ),
            {
                "id": GENERATION_ID,
                "owner": OWNER_ID,
                "name": MODEL_NAME,
                "version": MODEL_VERSION,
                "dim": DIMENSION,
            },
        )
    try:
        yield built
    finally:
        built.dispose()


def _ulid() -> str:
    from server.app.report.coverage import new_ulid

    return new_ulid()


def unit(x: float, y: float) -> Vector:
    norm = (x * x + y * y) ** 0.5
    return Vector(fingerprint=FINGERPRINT, values=(x / norm, y / norm, 0.0, 0.0))


class FakeTagPort:
    """``MOD-tag-service``'s three reads. See ``tests/integration/test_publish_cas.py``."""

    def __init__(self) -> None:
        self.current = TagConfigVersion(
            id=TCV1,
            sequence=1,
            content_hash="sha256:" + "1" * 64,
            payload={
                "tags": [{"id": TAG_ID, "text": "protein folding", "similarity_threshold": None}],
                "tag_aliases": [],
                "tag_exclusions": [],
            },
            created_at="2026-09-01T02:00:00.000Z",
        )
        self.frozen: dict[str, TagConfigVersion] = {}

    def get_active_config_version(self, owner_id: str) -> TagConfigVersion:
        return self.current

    def config_version(self, *, owner_id: str, tag_config_version_id: str) -> TagConfigVersion:
        return self.current

    def freeze_config_version(
        self, *, owner_id: str, report_build_id: str, expected_tag_config_version_id: str
    ) -> TagConfigVersion:
        self.frozen.setdefault(report_build_id, self.current)
        return self.frozen[report_build_id]


def seed(engine: Engine, works: int = 2) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO tag_vector (id, owner_id, subject_type, subject_id,"
                " embedding_generation_id, vector)"
                " VALUES (:id, :owner, 'tag', :subject, :generation, :vector)"
            ),
            {
                "id": _ulid(),
                "owner": OWNER_ID,
                "subject": TAG_ID,
                "generation": GENERATION_ID,
                "vector": unit(1.0, 0.0).to_blob(),
            },
        )
        for index in range(works):
            work_id = f"01JWRK{index:02d}000000000000000000"
            analysis_id = _ulid()
            at = f"2026-09-06T01:{index:02d}:00.000Z"
            connection.execute(
                text(
                    "INSERT INTO work (id, owner_id, canonical_doi, canonical_arxiv_id, title,"
                    " paper_url, code_url, current_work_version_id, metadata_state,"
                    " identity_state, merged_into_work_id, first_discovered_at,"
                    " ingest_sequence, content_state, created_at)"
                    " VALUES (:id, :owner, NULL, NULL, 'w', NULL, NULL, NULL, 'partial',"
                    " 'active', NULL, :at, :seq, 'present', :at)"
                ),
                {"id": work_id, "owner": OWNER_ID, "at": at, "seq": index + 1},
            )
            connection.execute(
                text(
                    "INSERT INTO analysis (id, owner_id, analysis_generation_id, target_kind,"
                    " target_work_id, target_post_id, task_type, source_fingerprint,"
                    " prompt_version, schema_version, generation_number, status, payload,"
                    " payload_hash, evidence_level, provider_name, model_name,"
                    " usage_tokens_in, usage_tokens_out, analyzed_at, accepted_from_attempt_id,"
                    " moved_by_merge_id)"
                    " VALUES (:id, :owner, :gen, 'work', :work, NULL, 'summary', 'fp', '1.0.0',"
                    " '0.1.0', 1, 'valid', '{}', :hash, 'abstract', 'anthropic', 'm', NULL,"
                    " NULL, :at, 'attempt', NULL)"
                ),
                {
                    "id": analysis_id,
                    "owner": OWNER_ID,
                    "gen": _ulid(),
                    "work": work_id,
                    "hash": "sha256:" + f"{index:064d}",
                    "at": at,
                },
            )
            connection.execute(
                text(
                    "INSERT INTO work_label (id, owner_id, target_kind, target_work_id,"
                    " target_post_id, label_text, analysis_id, embedding_generation_id,"
                    " vector, created_at) VALUES (:id, :owner, 'work', :work, NULL, :label,"
                    " :analysis, :generation, :vector, :at)"
                ),
                {
                    "id": _ulid(),
                    "owner": OWNER_ID,
                    "work": work_id,
                    "label": f"protein folding {index}",
                    "analysis": analysis_id,
                    "generation": GENERATION_ID,
                    "vector": unit(1.0, 0.01 * (index + 1)).to_blob(),
                    "at": at,
                },
            )


def publish(engine: Engine) -> tuple[PublishContext, Any]:
    tag_port = FakeTagPort()
    embedding = EmbeddingService(
        engine,
        encoder=DeterministicHashEncoder(MODEL_NAME, MODEL_VERSION, DIMENSION, Normalization.L2),
    )
    context = PublishContext(engine=engine, tag_port=tag_port, embedding_port=embedding)
    snapshot = build_report(
        engine,
        owner_id=OWNER_ID,
        report_build_id=str(uuid.uuid4()),
        tag_port=tag_port,
        embedding_port=embedding,
        settings=SelectionSettings(),
    )
    record_build(context, snapshot, caller_module=MOD_JOB)
    return context, publish_report(context, snapshot)


# --- (2) what this card produces -----------------------------------------------------------------


def test_the_published_read_model_validates(
    engine: Engine, validator: Draft202012Validator
) -> None:
    """A real publish, validated against the same schema the fixtures are validated against."""
    seed(engine)
    _, result = publish(engine)
    assert result.published
    assert result.read_model is not None
    assert_valid(validator, result.read_model)


def test_the_published_read_model_pins_the_versions_it_was_built_with(engine: Engine) -> None:
    """I05's first clause: the report stores the tag version, the selection version and the
    embedding generation, so a later reader can say *which rules produced this*."""
    seed(engine)
    _, result = publish(engine)
    body = result.read_model
    assert body is not None
    assert body["selection_version"] == SELECTION_VERSION
    assert body["tag_config_version"]["tag_config_version_id"] == TCV1
    assert body["tag_config_version"]["frozen_at"] == body["published_at"]
    assert body["embedding_generation"]["embedding_generation_id"] == GENERATION_ID


def test_the_report_says_its_threshold_is_uncalibrated(engine: Engine) -> None:
    """§6 / REQ-A2: while ``threshold_calibration_state = 'uncalibrated'`` the UI must say so.

    Pinned here rather than assumed: a report that quietly claimed calibration would let the
    §1.4 quality targets be quoted off a number nobody measured, which §6 forbids by name.
    """
    seed(engine)
    _, result = publish(engine)
    body = result.read_model
    assert body is not None
    assert body["coverage_note"]["threshold_calibration_state"] == "uncalibrated"
    assert body["coverage_note"]["empty_period"] is False


def test_the_density_parameters_are_never_reported_as_calibrated(engine: Engine) -> None:
    """§8.2 / REQ-A4: the density knobs are working values behind a gate that has not run."""
    seed(engine)
    _, result = publish(engine)
    body = result.read_model
    assert body is not None
    for direction in body["emerging_directions"]:
        assert direction["parameters"]["parameters_status"] == "PROVISIONAL_BOOTSTRAP"
        assert direction["label"] == EMERGING_DIRECTION_LABEL
    assert DensityParameters().parameters_status != "CALIBRATED"


def test_a_cold_start_reports_insufficient_evidence_rather_than_a_direction(
    engine: Engine,
) -> None:
    """§8.4: the first period of a system has no baseline, so it cannot have a direction.

    This is correct behaviour, not a failure -- and the schema requires the block to exist
    anyway, which is why "no directions" is represented as one row saying why.
    """
    seed(engine)
    _, result = publish(engine)
    body = result.read_model
    assert body is not None
    assert len(body["emerging_directions"]) == 1
    assert body["emerging_directions"][0]["evidence_state"] == "insufficient_evidence"
    assert body["emerging_directions"][0]["insufficient_reason"] in {
        "below_min_sample",
        "cold_start_insufficient_history",
        "delta_below_threshold",
        "generation_reset",
    }
    assert body["emerging_directions"][0]["member_target_keys"] == []


# --- (3) the round trip, and the I05 oracle -------------------------------------------------------


def test_the_rebuilt_read_model_is_byte_identical(
    engine: Engine, validator: Draft202012Validator
) -> None:
    """``report.get`` rebuilds from rows and must produce the same object, byte for byte.

    Compared as canonical JSON rather than as dicts, because "the same object" here means "the
    same input to sha256" -- the hash is the artefact that has to be stable, and a comparison
    that ignored ordering would not test it.
    """
    seed(engine)
    context, result = publish(engine)
    with engine.connect() as connection:
        rebuilt = read_model(connection, context, owner_id=OWNER_ID, report_id=result.report_id)
    assert rebuilt is not None
    assert_valid(validator, rebuilt)
    assert canonical_json(rebuilt) == canonical_json(result.read_model)
    assert verify_content_hash(rebuilt) is True
    assert rebuilt["content_hash"] == result.content_hash


def test_the_content_hash_covers_the_object_without_covering_itself(engine: Engine) -> None:
    """``content_hash = sha256(JCS(read model with content_hash blanked))``.

    Stated as an executable definition so the two places that compute it -- the publisher and
    :func:`verify_content_hash` -- cannot drift. A hash that included its own field would be
    unverifiable, and a hash computed over a *different* subset would silently stop protecting
    whatever was left out.
    """
    seed(engine)
    _, result = publish(engine)
    body = dict(result.read_model or {})
    assert content_hash_of({**body, "content_hash": ""}) == body["content_hash"]

    tampered = json.loads(json.dumps(body))
    tampered["items"][0]["item_type"] = "prior_reference"
    assert content_hash_of({**tampered, "content_hash": ""}) != body["content_hash"]


def test_reading_the_report_twice_gives_the_same_hash(engine: Engine) -> None:
    """The read path holds no state, so repeated reads cannot diverge (I05)."""
    seed(engine)
    context, result = publish(engine)
    with engine.connect() as connection:
        first = read_model(connection, context, owner_id=OWNER_ID, report_id=result.report_id)
        second = read_model(connection, context, owner_id=OWNER_ID, report_id=result.report_id)
    assert canonical_json(first) == canonical_json(second)


# --- determinism of the numbers the schema carries ------------------------------------------------


def test_scores_are_rounded_half_up_to_four_decimals() -> None:
    """§3: half-up, four decimals -- not Python's round-half-to-even.

    The two disagree only on a tie, and a tie is exactly where two machines would otherwise
    select different sets -- one above the threshold, one below. ``0.00015`` is a value whose
    shortest representation is a tie and on which the two rules visibly part company.
    """
    assert round_half_up(0.00015) == 0.0002
    assert round(0.00015, 4) == 0.0001, "round() is half-to-even; this module must not use it"
    assert round_half_up(0.00035) == 0.0004
    assert round(0.00035, 4) == 0.0003
    assert round_half_up(0.12345) == 0.1235
    assert round_half_up(-0.12345) == -0.1235


def test_canonical_json_is_key_order_independent() -> None:
    """JCS: the hash describes the content, not the order a dict happened to be built in."""
    assert canonical_json({"b": 1, "a": 2}) == canonical_json({"a": 2, "b": 1})
    assert canonical_json({"a": [1, 2]}) != canonical_json({"a": [2, 1]})


# --- F-A3-P5-03 / CR-P0-07: what an unwired deployment answers ---------------------------------
#
# On the wire, not in a unit: the finding was found by curling a running server, so the
# assertion is made through the ASGI app the same way. It belongs in the *contract* file
# because the question is "which declared response does this operation give", which is
# `contracts/http/openapi.yaml`'s to answer, not the publish transaction's.


def declared_status_codes(operation_id: str) -> set[int]:
    """The status codes ``contracts/http/openapi.yaml`` declares for one operation.

    Read from the contract rather than restated, so a response this module invents cannot be
    blessed by a constant sitting next to it.
    """
    contract = REPO_ROOT / "contracts" / "http" / "openapi.yaml"
    document = yaml.safe_load(contract.read_text("utf-8"))
    for path in document["paths"].values():
        for operation in path.values():
            if isinstance(operation, dict) and operation.get("operationId") == operation_id:
                return {int(code) for code in operation["responses"]}
    raise AssertionError(f"{operation_id} is not in openapi.yaml")


@pytest.fixture
def authed_client(engine: Engine) -> TestClient:
    """A server with auth wired and ``report_context`` deliberately absent.

    That is the shipped process the audit curled: the owner is logged in, so 401 is out of the
    way and the *availability* question is the one being asked. A bare ``create_app()`` would
    answer 401 first and never reach it — which is itself asserted below, because the order is
    a property worth keeping.
    """
    AuthService(engine).bootstrap_owner(display_name=OWNER_NAME, password=OWNER_PASSWORD)
    app = create_app()
    app.state.auth_service = AuthService(engine)
    client = TestClient(app, base_url="https://testserver")
    response = client.post(
        "/v1/auth/login",
        json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
        headers=WIRE_HEADERS,
    )
    assert response.status_code == 200, response.text
    return client


def test_the_declared_responses_do_not_include_503_for_the_read_routes() -> None:
    """The premise of the choice made in ``router._context``, asserted against the contract.

    ``503 STORAGE_WRITE_FAILED`` exists in openapi — on 27 **mutations**. If it is ever
    declared for these two reads, this test fails and the router should be changed to use it;
    that is the point of reading it from the file instead of asserting the router's own view.
    """
    listing = declared_status_codes("report.list")
    detail = declared_status_codes("report.get")
    assert 503 not in listing and 503 not in detail
    assert listing == {200, 401, 403, 500}
    assert detail == {200, 401, 403, 404, 500}


@pytest.mark.parametrize("route", REPORT_ROUTES)
def test_an_unwired_deployment_answers_a_declared_code_and_names_the_gap(
    authed_client: TestClient, route: str
) -> None:
    """``F-A3-P5-03``: a disclosed gap must not read as a crash.

    The status stays what the contract declares — 500 ``INTERNAL``, the only code declared on
    **both** routes that does not misstate the cause (the reasoning, and why 401/403/404 are
    excluded, is in ``router._context``'s docstring). What changed is the body: it names the
    gap and ``CR-P0-07`` instead of saying "unexpected", and it carries the **route's own**
    ``operation_id`` — which was hard-coded to ``report.get``, so ``GET /v1/reports`` used to
    answer with the wrong one. That wrong id is in the audit's quoted body.
    """
    response = authed_client.get(route, headers=WIRE_HEADERS)

    expected_operation = "report.list" if route == "/v1/reports" else "report.get"
    assert response.status_code == 500
    assert response.status_code in declared_status_codes(expected_operation)

    body = response.json()
    assert body["code"] == "INTERNAL"
    assert body["message_safe"] == UNWIRED_MESSAGE_SAFE
    assert "CR-P0-07" in body["message_safe"]
    assert "không mong đợi" not in body["message_safe"], "still reads as an unexpected crash"
    assert body["details_safe"] == {"operation_id": expected_operation}
    assert body["correlation_id"]
    # errors.yaml §error_envelope: additionalProperties false, and these are its fields.
    assert set(body) == {
        "code",
        "scope",
        "retry_class",
        "message_safe",
        "correlation_id",
        "details_safe",
    }
    # forbidden_content_vi: no stack trace, no SQL, no table or column names.
    rendered = json.dumps(body, ensure_ascii=False)
    for leak in ("Traceback", "SELECT", "report_item", "coverage_window", "sqlite"):
        assert leak not in rendered


@pytest.mark.parametrize("route", REPORT_ROUTES)
def test_an_anonymous_caller_is_refused_before_availability_is_disclosed(route: str) -> None:
    """Order: headers, then identity, then availability.

    A bare ``create_app()`` has neither auth nor a report context. It must answer ``401``, not
    the unwired message — how a deployment is wired is not something to tell a caller who has
    not proved who they are.
    """
    client = TestClient(create_app(), base_url="https://testserver")
    response = client.get(route, headers=WIRE_HEADERS)
    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "UNAUTHORIZED"
    assert "CR-P0-07" not in json.dumps(body, ensure_ascii=False)


def test_a_wired_deployment_is_unchanged(engine: Engine) -> None:
    """The other half: with a context installed, the routes behave exactly as before.

    Without this, the fix above would also pass for a router that answered the unwired body
    unconditionally.
    """
    seed(engine)
    context, result = publish(engine)
    AuthService(engine).bootstrap_owner(display_name=OWNER_NAME, password=OWNER_PASSWORD)
    app = create_app()
    app.state.auth_service = AuthService(engine)
    app.state.report_context = context
    client = TestClient(app, base_url="https://testserver")
    assert (
        client.post(
            "/v1/auth/login",
            json={"username": OWNER_NAME, "password": OWNER_PASSWORD},
            headers=WIRE_HEADERS,
        ).status_code
        == 200
    )

    listing = client.get("/v1/reports", headers=WIRE_HEADERS)
    assert listing.status_code == 200
    assert [row["report_id"] for row in listing.json()["reports"]] == [result.report_id]

    detail = client.get(f"/v1/reports/{result.report_id}", headers=WIRE_HEADERS)
    assert detail.status_code == 200
    assert detail.json()["content_hash"] == result.content_hash

    missing = client.get("/v1/reports/01JRPTZZ000000000000000000", headers=WIRE_HEADERS)
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"
