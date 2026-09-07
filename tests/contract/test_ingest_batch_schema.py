"""E1 -- the six wire fixtures of ``contracts/schemas/ingest-batch.schema.json``.

The card's §8 names one positive and five negative fixtures. Each is checked twice, because
they are two different claims:

1. **The contract accepts / rejects it.** Validated with ``jsonschema`` against the schema
   file itself -- not against the generated Pydantic model, which is downstream of it. For
   a negative fixture the failing JSON pointer must be the one the fixture predicts; a
   fixture that fails for some *other* reason would pass a weaker test than it states.
2. **The service refuses it and writes nothing.** ``VALIDATION_ERROR`` and zero rows in all
   three ingest tables. Every negative fixture lists "write any row while validation fails"
   under ``forbidden_effects``, and the only way to check a forbidden effect is to count
   rows after the call.

Fixtures are the oracle (SRC-PLAN §15): nothing here restates their content, and no
expectation is adjusted to match the implementation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.ingest.idempotency import compute_payload_hash
from server.app.ingest.repository import IngestRepository
from server.app.ingest.service import IngestContext, IngestError, submit_batch

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "ingest-batch.schema.json"
OWNER_ID = "01J0WNER100000000000000000"
RUN_ID = "01JRVNF1000000000000000000"

#: The five negative fixtures, in the order the card lists them.
NEGATIVE_FIXTURES: tuple[str, ...] = (
    "identity/neg-ingest-batch-missing-idempotency-key",
    "identity/neg-ingest-batch-bad-payload-hash",
    "identity/neg-ingest-batch-empty-items",
    "identity/neg-ingest-batch-unknown-field",
    "identity/neg-ingest-batch-timestamp-precision",
)


def build_database(path: Path) -> Engine:
    """A WAL SQLite database carrying the real schema, plus the single ``owner`` row.

    The schema comes from ``alembic upgrade head`` -- the migration chain that ships -- not
    from DDL re-declared in a test. A second source of schema truth beside
    ``server/migrations/versions/`` is exactly the drift these tests exist to catch, and
    running the real upgrade also proves the chain has a single head: with more than one,
    ``head`` is ambiguous and Alembic refuses outright.
    """
    from alembic import command
    from alembic.config import Config

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(path)
    try:
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous

    engine = create_sqlite_engine(path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at) "
                "VALUES (:id, 1, 'Owner', 'Asia/Ho_Chi_Minh', '2026-09-06T00:00:00.000Z')"
            ),
            {"id": OWNER_ID},
        )
    return engine


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    return build_database(tmp_path / "rr.db")


@pytest.fixture
def context(engine: Engine) -> IngestContext:
    return IngestContext(engine=engine, owner_id=OWNER_ID)


@pytest.fixture(scope="session")
def batch_schema() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def row_counts(context: IngestContext) -> dict[str, int]:
    repository = IngestRepository()
    with context.engine.connect() as connection:
        return {
            table: repository.count_rows(connection, table)
            for table in ("post", "ingest_receipt", "checkpoint")
        }


def test_positive_fixture_is_accepted_by_the_contract_schema(
    fixture_loader: Any, batch_schema: Draft202012Validator
) -> None:
    """``pos-ingest-batch-valid`` validates, as its ``expected_validation`` says."""
    fixture = fixture_loader("identity/pos-ingest-batch-valid")
    assert fixture.data["expected_validation"] == "accept"
    assert list(batch_schema.iter_errors(fixture.data["batch"])) == []


def test_positive_fixture_payload_hash_is_reproducible(fixture_loader: Any) -> None:
    """The fixture's ``payload_hash`` is recomputed from the contract's own definition.

    This is the independent check on the canonicaliser in ``idempotency.py``: the hash in
    the fixture was produced from ``contracts/schemas/ingest-batch.schema.json``
    §payload_hash_definition without reference to this implementation, so agreement means
    the implementation reads the definition the same way the contract author did. If the
    JCS rules were applied differently, every ack-loss replay would look like a conflict.
    """
    fixture = fixture_loader("identity/pos-ingest-batch-valid")
    batch = fixture.data["batch"]
    assert compute_payload_hash(batch) == batch["payload_hash"]


@pytest.mark.parametrize("fixture_ref", NEGATIVE_FIXTURES)
def test_negative_fixture_is_rejected_at_the_pointer_it_names(
    fixture_ref: str, fixture_loader: Any, batch_schema: Draft202012Validator
) -> None:
    """Each negative fixture fails validation, and fails *where* it says it fails."""
    fixture = fixture_loader(fixture_ref)
    assert fixture.data["expected_validation"] == "reject"
    errors = list(batch_schema.iter_errors(fixture.data["batch"]))
    assert errors, f"{fixture_ref} was expected to be rejected but validated cleanly"

    expected_pointer = fixture.data["expected_violation"]["json_pointer"]
    observed = {"/" + "/".join(str(part) for part in error.absolute_path) for error in errors}
    # A missing required property and a forbidden extra property are both reported by
    # jsonschema against the *parent* object, with the offending member named in the
    # message; the fixture names the member's own pointer. Accept either spelling.
    member = expected_pointer.rsplit("/", 1)[-1]
    parent = expected_pointer.rsplit("/", 1)[0] or "/"
    assert expected_pointer in observed or (
        parent in observed and any(member in error.message for error in errors)
    ), f"{fixture_ref}: expected a violation at {expected_pointer}, observed {sorted(observed)}"


@pytest.mark.parametrize("fixture_ref", NEGATIVE_FIXTURES)
def test_negative_fixture_writes_no_row_through_the_service(
    fixture_ref: str, fixture_loader: Any, context: IngestContext
) -> None:
    """``VALIDATION_ERROR`` and zero rows -- the ``forbidden_effects`` of all five.

    Rejection happens before any connection is opened, so "no partial write" is not a
    property of a cleanup path that could be skipped: there is nothing to clean up.
    """
    fixture = fixture_loader(fixture_ref)
    before = row_counts(context)

    with pytest.raises(IngestError) as raised:
        submit_batch(context, fixture.data["batch"], run_id=RUN_ID)

    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert raised.value.http_status == 422
    assert row_counts(context) == before == {"post": 0, "ingest_receipt": 0, "checkpoint": 0}


def test_error_envelope_carries_no_post_content(
    fixture_loader: Any, context: IngestContext
) -> None:
    """An envelope may not leak post text, a URL or a token (``contracts/errors.yaml``).

    The negative fixture with the bad timestamp carries a real post body and a real URL, so
    if anything from the request leaked into the envelope this assertion would see it.
    """
    fixture = fixture_loader("identity/neg-ingest-batch-timestamp-precision")
    item = fixture.data["batch"]["items"][0]

    with pytest.raises(IngestError) as raised:
        submit_batch(context, fixture.data["batch"], run_id=RUN_ID)

    rendered = json.dumps(raised.value.envelope("01JC0RREL10000000000000000"), ensure_ascii=False)
    assert item["text"] not in rendered
    assert item["url"] not in rendered
    assert "Bearer" not in rendered


def test_service_rejects_a_payload_hash_that_does_not_match_the_body(
    fixture_loader: Any, context: IngestContext
) -> None:
    """A declared hash that is not ``sha256(JCS(payload_core))`` is a ``VALIDATION_ERROR``.

    ``payload_hash`` is the only thing that separates a replay from a new batch. If the
    server accepted a hash it had not verified, a client could make two different batches
    share a hash and the idempotency guarantee would rest on the client's arithmetic.
    """
    fixture = fixture_loader("identity/pos-ingest-batch-valid")
    batch = dict(fixture.data["batch"])
    batch["payload_hash"] = "sha256:" + "a" * 64
    before = row_counts(context)

    with pytest.raises(IngestError) as raised:
        submit_batch(context, batch, run_id=RUN_ID)

    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert raised.value.details_safe == {"violation_kind": "payload_hash_mismatch"}
    assert row_counts(context) == before
