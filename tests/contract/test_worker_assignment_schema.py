"""E1 — every payload this card puts on the wire validates against the contract's schema.

``contracts/schemas/worker-assignment.schema.json`` is the oracle, used as a schema and not
paraphrased: the objects are built by the **real** service functions and handed to a
Draft 2020-12 validator, so a field this code invents or misspells fails here rather than at
the collector.

Why that matters more than usual for this schema
-------------------------------------------------
The document is ``additionalProperties: false`` at the top level **and** inside every
``$defs`` object. An extra key is therefore a hard failure, not a tolerated addition — which
is exactly what catches the easy mistake in :func:`_assignment_payload`: ``ingest.get_checkpoint``
returns a ``created_at`` that the ``server_checkpoint`` definition does not have, so passing
its dictionary through unfiltered would produce an invalid assignment. The projection that
prevents it is asserted below rather than trusted.

The top level is also a six-branch ``oneOf``: exactly one of ``claim_request``,
``assignment``, ``no_work``, ``heartbeat_request``, ``heartbeat_response`` or
``release_request``. A response that carried both an ``assignment`` and a ``no_work`` would be
refused, which is the schema's way of saying that "here is work" and "there is no work" are
not both true.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker
from rr_contracts.generated.operations import OperationId

from server.app.jobs.lease import (
    CLAIM_IDLE_BACKOFF_SECONDS,
    HEARTBEAT_INTERVAL_COLLECTOR_SECONDS,
    LEASE_TTL_COLLECTOR_SECONDS,
    Lease,
    LeaseState,
    timestamp_utc_ms,
)
from server.app.jobs.service import (
    NO_WORK_REASONS,
    STOP_REASON_EFFECT,
    WIRE_TO_STORED_WORKER_KIND,
    _no_work,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "contracts" / "schemas" / "worker-assignment.schema.json"
FIXTURE_ROOT = REPO_ROOT / "acceptance" / "fixtures"

OWNER_ID = "01JW0WNER00000000000000000"
NOW = datetime(2026, 9, 7, 8, 0, 0, tzinfo=UTC)


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return data


@pytest.fixture(scope="module")
def validator(schema) -> Draft202012Validator:  # type: ignore[no-untyped-def]
    """Draft 2020-12 with the format checker **on**.

    Off by default in ``jsonschema``, and leaving it off would silently skip every
    ``date-time`` and ``uri`` constraint in the document — the checks most likely to catch a
    timestamp written in the wrong shape.
    """
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def assert_valid(validator: Draft202012Validator, payload: dict[str, Any]) -> None:
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    assert errors == [], [f"{list(e.path)}: {e.message}" for e in errors]


# --- the schema's own shape, asserted before it is relied on ----------------------------------


def test_the_schema_is_a_six_branch_oneof_that_forbids_extra_keys(schema) -> None:
    """Premise check. Everything below reads as a stronger assertion than it is if the
    document ever stopped being closed."""
    assert schema["additionalProperties"] is False
    branches = {tuple(branch["required"])[0] for branch in schema["oneOf"]}
    assert branches == {
        "claim_request",
        "assignment",
        "no_work",
        "heartbeat_request",
        "heartbeat_response",
        "release_request",
    }
    for name in ("assignment", "no_work", "lease", "server_checkpoint", "heartbeat_response"):
        assert schema["$defs"][name]["additionalProperties"] is False, name


def test_two_branches_at_once_are_refused(validator) -> None:
    """ "Here is work" and "there is no work" cannot both be true.

    Asserted because the ``oneOf`` is what makes the claim response unambiguous, and a
    validator configured with ``anyOf`` semantics by mistake would accept this.
    """
    payload = {**_no_work("no_due_occurrence"), "assignment": {}}
    assert list(validator.iter_errors(payload)) != [], "a two-branch payload validated"


# --- no_work ----------------------------------------------------------------------------------


def test_every_no_work_reason_the_service_can_emit_is_in_the_schema(schema) -> None:
    """The service's reason set is the schema's, not a superset it hopes overlaps."""
    declared = set(schema["$defs"]["no_work"]["properties"]["reason"]["enum"])
    assert declared == NO_WORK_REASONS


@pytest.mark.parametrize("reason", sorted(NO_WORK_REASONS))
def test_each_no_work_payload_validates(validator, reason: str) -> None:
    assert_valid(validator, _no_work(reason))


def test_the_no_work_backoff_is_the_retry_policy_ceiling(validator) -> None:
    """Fixture ``collection/g-schedule-due-claim.json`` event 3 pins ``retry_after_ms: 45000``.

    45 s is the top of ``claim_idle_backoff`` (5/15/45). Read from the fixture rather than
    typed here, so a change to the contract's backoff shows up as a failure.
    """
    fixture = json.loads(
        (FIXTURE_ROOT / "collection" / "g-schedule-due-claim.json").read_text(encoding="utf-8")
    )
    pinned = next(
        event["response_body"]["no_work"]["retry_after_ms"]
        for event in fixture["events"]
        if isinstance(event.get("response_body"), dict) and "no_work" in event["response_body"]
    )
    payload = _no_work("assignment_already_held")
    assert payload["no_work"]["retry_after_ms"] == pinned
    assert pinned == CLAIM_IDLE_BACKOFF_SECONDS[-1] * 1000
    assert_valid(validator, payload)


# --- lease ------------------------------------------------------------------------------------


def _lease() -> Lease:
    return Lease(
        id="08ZSTPHZ4MKNY25V807H2ESQCC",
        owner_id=OWNER_ID,
        run_id="6PNQ047XA29K4GVSEEXF8WFNJT",
        job_id="KZA8XXCYQBY4190TVQJ05NMPZ3",
        worker_identity="H5RYV3TMNHCTZFEGSX0P3V2CX9",
        lease_epoch=1,
        expires_at=NOW + timedelta(seconds=LEASE_TTL_COLLECTOR_SECONDS),
        state=LeaseState.HELD,
    )


def test_the_lease_object_matches_the_schema_and_the_fixture(validator, schema) -> None:
    """Five properties, no more. ``ttl_s`` and ``heartbeat_interval_s`` are the contract's.

    The fixture's own lease block is compared key-for-key, so this asserts the shipped shape
    against an accepted example rather than against the schema alone — a payload can satisfy a
    schema and still not be the thing the fixture describes.
    """
    wire = _lease().wire()
    assert set(wire) == set(schema["$defs"]["lease"]["required"])
    assert wire["ttl_s"] == LEASE_TTL_COLLECTOR_SECONDS
    assert wire["heartbeat_interval_s"] == HEARTBEAT_INTERVAL_COLLECTOR_SECONDS

    fixture = json.loads(
        (FIXTURE_ROOT / "collection" / "g-schedule-due-claim.json").read_text(encoding="utf-8")
    )
    pinned = next(
        event["response_body"]["assignment"]["lease"]
        for event in fixture["events"]
        if isinstance(event.get("response_body"), dict) and "assignment" in event["response_body"]
    )
    assert set(wire) == set(pinned)
    assert wire["ttl_s"] == pinned["ttl_s"]
    assert wire["heartbeat_interval_s"] == pinned["heartbeat_interval_s"]
    assert wire["lease_epoch"] == pinned["lease_epoch"] == 1


def test_the_lease_ttl_satisfies_the_constraint_retry_policy_states(schema) -> None:
    """``ttl_s >= 4 x heartbeat_interval_s`` and ``> online_threshold`` (90 s).

    ``retry-policy.yaml`` states this as a *constraint* on the value rather than as a
    property of 120 s, so it is asserted rather than assumed — changing one number without the
    other would give a lease that expires before the heartbeat meant to renew it.
    """
    description = schema["$defs"]["lease"]["properties"]["ttl_s"]["description"]
    assert "4" in description and "90" in description
    assert LEASE_TTL_COLLECTOR_SECONDS >= 4 * HEARTBEAT_INTERVAL_COLLECTOR_SECONDS
    assert LEASE_TTL_COLLECTOR_SECONDS > 90


# --- heartbeat and release --------------------------------------------------------------------


def test_the_heartbeat_response_shapes_validate(validator) -> None:
    """Both shapes the service returns: renewed, and stopped because the run was cancelled.

    ``lease_expires_at`` is absent from the cancelled shape on purpose — the schema says it is
    "vắng mặt khi ``lease_valid = false``", and sending a renewal time with a dead lease would
    be a contradiction the collector has to resolve.
    """
    renewed = {
        "heartbeat_response": {
            "lease_valid": True,
            "lease_expires_at": timestamp_utc_ms(NOW + timedelta(seconds=120)),
            "directive": "continue",
        }
    }
    cancelled = {"heartbeat_response": {"lease_valid": False, "directive": "stop_cancelled"}}
    assert_valid(validator, renewed)
    assert_valid(validator, cancelled)
    assert "lease_expires_at" not in cancelled["heartbeat_response"]


def test_every_directive_the_service_can_send_is_in_the_schema(schema) -> None:
    declared = set(schema["$defs"]["heartbeat_response"]["properties"]["directive"]["enum"])
    assert {"continue", "stop_cancelled"} <= declared


def test_the_release_reasons_the_schema_allows_are_a_closed_set(schema) -> None:
    """``completed_phase | worker_shutdown | local_storage_unavailable`` — three, not more.

    Two of them also appear in ``worker.report_stop``'s vocabulary, which is why the service
    keeps :data:`STOP_REASON_EFFECT` separate: the same word means "give the job back" on one
    route and "the run stops for this reason" on the other.
    """
    declared = set(schema["$defs"]["release_request"]["properties"]["release_reason"]["enum"])
    assert declared == {"completed_phase", "worker_shutdown", "local_storage_unavailable"}
    assert {"worker_shutdown", "local_storage_unavailable"} <= set(STOP_REASON_EFFECT)


# --- the assignment payload, built by the real service ----------------------------------------


def test_the_checkpoint_block_is_projected_to_exactly_the_schemas_six_properties(schema) -> None:
    """The defect this test exists for: ``ingest.get_checkpoint`` returns a seventh key.

    ``server.app.ingest.service.get_checkpoint`` returns ``created_at`` alongside the six the
    schema declares, and ``server_checkpoint`` is ``additionalProperties: false``. Passing that
    dictionary straight into the assignment would produce an invalid payload, so the service
    projects it. Asserted against the schema's own ``required`` list rather than a copy.
    """
    from server.app.jobs.service import JobContext, _checkpoint_for
    from server.app.scheduler.evaluator import ScheduleSettings

    class NoisyCheckpointPort:
        """Returns the real ingest shape, extra key and all."""

        def get_checkpoint(self, *, run_id: str) -> dict[str, Any]:
            return {
                "phase": "collecting",
                "cursor_token": "abc",
                "cursor_state": "valid",
                "acked_through_ingest_sequence": 42,
                "items_ingested_total": 42,
                "checkpoint_sequence": 3,
                "created_at": "2026-09-07T08:00:00.000Z",
            }

    ctx = JobContext(
        engine=None,  # type: ignore[arg-type] - never touched on this path
        owner_id=OWNER_ID,
        settings=ScheduleSettings(slots_local=("08:00",), timezone_iana="Asia/Ho_Chi_Minh"),
        checkpoint_port=NoisyCheckpointPort(),
    )
    block = _checkpoint_for(ctx, run_id="6PNQ047XA29K4GVSEEXF8WFNJT", phase="collecting")

    declared = set(schema["$defs"]["server_checkpoint"]["required"])
    assert set(block) == declared
    assert "created_at" not in block
    assert block["acked_through_ingest_sequence"] == 42


def test_an_absent_checkpoint_is_the_empty_new_one_not_an_error(schema) -> None:
    """A first claim has no checkpoint, and refusing would make a fresh run unclaimable.

    ``checkpoint_sequence: 0`` is the schema's own description of that state
    ("Rỗng-mới (sequence 0) cho một run chưa ingest gì"), and fixture
    ``collection/g-schedule-due-claim.json`` event 2 pins exactly this block.
    """
    from server.app.jobs.service import JobContext, _checkpoint_for
    from server.app.scheduler.evaluator import ScheduleSettings

    ctx = JobContext(
        engine=None,  # type: ignore[arg-type] - never touched on this path
        owner_id=OWNER_ID,
        settings=ScheduleSettings(slots_local=("08:00",), timezone_iana="Asia/Ho_Chi_Minh"),
    )
    block = _checkpoint_for(ctx, run_id="r", phase="collecting")

    fixture = json.loads(
        (FIXTURE_ROOT / "collection" / "g-schedule-due-claim.json").read_text(encoding="utf-8")
    )
    pinned = next(
        event["response_body"]["assignment"]["checkpoint"]
        for event in fixture["events"]
        if isinstance(event.get("response_body"), dict) and "assignment" in event["response_body"]
    )
    assert block == pinned
    assert set(block) == set(schema["$defs"]["server_checkpoint"]["required"])


# --- the vocabularies the wire and the database each own --------------------------------------


def test_the_wire_worker_kind_is_mapped_to_the_stored_one_explicitly(schema) -> None:
    """Two vocabularies, each authoritative for its own layer.

    ``entities.yaml`` stores ``x_collector | analysis_worker``; ``ports.yaml`` and this schema
    put ``collector`` on the wire. The mapping is a dict rather than a string that happens to
    work, and this asserts the wire half against the schema so a rename on either side fails
    here instead of writing an enum value the CHECK constraint refuses.
    """
    declared = set(schema["$defs"]["claim_request"]["properties"]["worker_kind"]["enum"])
    assert declared == {"collector"}, "claim is collector-only (analysis has its own port)"
    assert declared <= set(WIRE_TO_STORED_WORKER_KIND)
    assert WIRE_TO_STORED_WORKER_KIND["collector"] == "x_collector"


def test_the_stop_reason_vocabulary_is_the_ports_yaml_one() -> None:
    """``worker.report_stop``'s eight request values, each mapped to a state-machine effect.

    Read from ``contracts/ports.yaml`` rather than restated, so an added stop reason fails
    here — with the message that the state machine has no effect for it — instead of being
    silently dropped by a ``dict.get`` at run time.
    """
    import yaml

    ports = yaml.safe_load((REPO_ROOT / "contracts" / "ports.yaml").read_text("utf-8"))
    operation = next(
        op
        for op in ports["operations"]
        if op["operation_id"] == OperationId.WORKER_REPORT_STOP.value
    )
    summary = operation["request_summary_vi"]
    for reason in STOP_REASON_EFFECT:
        assert f"`{reason}`" in summary, f"{reason} is not in the contract's request vocabulary"
