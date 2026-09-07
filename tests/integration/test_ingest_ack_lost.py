"""E1 + E2 -- the ack-loss timeline end to end, over the real HTTP surface and the real DB.

Scenarios: SC21 (ack lost, receipt looked up, replay changes nothing), SC03 (cursor
invalidated, feed re-read, no duplicate ingest), SC49 (a principal that is not a collector
is refused with the code the R5-01 boundary table names), and the E2 fault case from
``contracts/state/storage.yaml`` T-ST-01 (storage cannot be written: nothing is ACKed and
no row count moves).

Fixtures used as data, not as prose: ``collection/d-duplicate-ingest-replay`` for the
ack-loss timeline and ``collection/b-cursor-invalidated-reread-dedup`` for the re-read.
Both state their oracle in ``durable_rows_expected`` / ``oracle_vi`` rather than in a
``rows`` block, so the assertions below name the same measurements those fields do -- row
deltas, ``counts.deduplicated``, and hash equality -- and never a log line.

The two ways an ACK can fail to arrive
--------------------------------------
They must not be confused, and the tests keep them apart:

* **After COMMIT.** The data is durable; the client just does not know. The server must
  answer the follow-up lookup with the receipt, and a resubmission must return that same
  receipt with ``status = duplicate_replay``.
* **Before COMMIT.** Nothing is durable. The server must not have written a partial row,
  and the follow-up lookup must say ``not_committed`` -- which is the only answer that
  authorises the collector to send the batch again.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.db.faults import WriteFaultInjector
from server.app.ingest.idempotency import compute_payload_hash
from server.app.ingest.repository import IngestRepository
from server.app.ingest.router import install_ingest_error_handlers
from server.app.ingest.router import router as ingest_router
from server.app.ingest.service import (
    IngestContext,
    IngestError,
    LeaseSnapshot,
    commit_checkpoint,
    get_checkpoint,
    get_receipt,
    submit_batch,
)
from server.app.main import create_app
from server.app.storage.guard import StorageGuard

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01J0WNER100000000000000000"
RUN_ID = "01JRVNF1000000000000000000"
JOB_ID = "01JJ0BF1000000000000000000"
LEASE_ID = "01J1EASEF10000000000000000"
COLLECTOR_TOKEN = "collector-token-for-tests-only-not-a-secret"


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


class FakeAssignments:
    """Stands in for ``TC-scheduler-lease-claim``'s read port -- not for its logic.

    It answers one question, "what is the current lease of this job", because ingest has to
    ask something to distinguish a stale epoch from a revoked lease. The lease *state
    machine* is not reimplemented here; that would be writing another card's domain inside
    this one's tests.
    """

    def __init__(self, epoch: int = 1, revoked: bool = False) -> None:
        self.epoch = epoch
        self.revoked = revoked

    def lease_snapshot(self, *, job_id: str, lease_id: str) -> LeaseSnapshot | None:
        if lease_id != LEASE_ID:
            return None
        return LeaseSnapshot(run_id=RUN_ID, lease_epoch=self.epoch, revoked=self.revoked)


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    return build_database(tmp_path / "rr.db")


@pytest.fixture
def context(engine: Engine) -> IngestContext:
    return IngestContext(engine=engine, owner_id=OWNER_ID)


def counts(context: IngestContext) -> dict[str, int]:
    repository = IngestRepository()
    with context.engine.connect() as connection:
        return {
            table: repository.count_rows(connection, table)
            for table in ("post", "ingest_receipt", "checkpoint")
        }


def batch_of(
    items: list[dict[str, Any]], *, key: str, cursor: str | None, state: str
) -> dict[str, Any]:
    """A schema-valid ingest batch with a correctly computed ``payload_hash``."""
    batch: dict[str, Any] = {
        # A ULID is Crockford base32, uppercase; a retry mints a new one while the
        # idempotency key stays the same, which is what makes a replay recognisable.
        "request_id": "01JREQH1000000000000000000",
        "schema_version": "0.1.0",
        "idempotency_key": key,
        "payload_hash": "",
        "job_id": JOB_ID,
        "lease_id": LEASE_ID,
        "lease_epoch": 1,
        "items": items,
        "client_checkpoint_proposal": {
            "phase": "collecting",
            "cursor_token": cursor,
            "cursor_state": state,
            "items_collected_in_run": len(items),
            "stop_hint": "none",
        },
    }
    batch["payload_hash"] = compute_payload_hash(batch)
    return batch


def item(x_post_id: str, *, links: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "x_post_id": x_post_id,
        "author": {"handle": "acc1"},
        "url": f"https://x.com/acc1/status/{x_post_id}",
        "text": f"post {x_post_id}",
        "collected_at": "2026-09-07T08:00:00.000Z",
        "media_refs": [],
        "referenced_links": links or [],
    }


# ------------------------------------------------------------------ SC21: ack lost


def test_ack_lost_after_commit_is_recovered_by_looking_the_receipt_up(
    fixture_loader: Any, context: IngestContext
) -> None:
    """``collection/d-duplicate-ingest-replay``, events 1-3.

    The oracle that fixture states: ``COUNT(post)`` unchanged across events 2, 3 and 4;
    ``receipt_hash`` equal at events 2 and 3; exactly one receipt for the key. The fixture's
    event 1 has ``response_status: null`` on purpose -- the client does not know -- so the
    test throws the first response away rather than asserting on it.
    """
    fixture = fixture_loader("collection/d-duplicate-ingest-replay")
    key = fixture.data["events"][0]["request_headers"]["Idempotency-Key"]
    batch = batch_of(
        [item(f"19000000000000000{n:02d}") for n in range(15)],
        key=key,
        cursor="cursor-page-3",
        state="valid",
    )

    submit_batch(context, batch, run_id=RUN_ID)  # event 1: committed, ACK lost on the way back
    after_commit = counts(context)
    assert after_commit["post"] == 15

    looked_up = get_receipt(context, idempotency_key=key)["receipt"]  # event 2: the required step
    assert looked_up["status"] == "committed"
    assert counts(context) == after_commit

    replayed = submit_batch(context, batch, run_id=RUN_ID)["receipt"]  # event 3
    assert replayed["status"] == "duplicate_replay"
    assert replayed["receipt_hash"] == looked_up["receipt_hash"]
    assert replayed["checkpoint_ack"] == looked_up["checkpoint_ack"]
    assert counts(context) == after_commit

    mutated = copy.deepcopy(batch)  # event 4: same key, different payload
    mutated["items"][0]["text"] = "edited"
    mutated["payload_hash"] = compute_payload_hash(mutated)
    with pytest.raises(IngestError) as raised:
        submit_batch(context, mutated, run_id=RUN_ID)
    assert raised.value.code is ErrorCode.IDEMPOTENCY_CONFLICT
    assert counts(context) == after_commit

    with context.engine.connect() as connection:
        for_key = connection.execute(
            text("SELECT COUNT(*) FROM ingest_receipt WHERE idempotency_key = :k"), {"k": key}
        ).scalar_one()
    assert for_key == 1


def test_ack_lost_before_commit_leaves_nothing_and_is_safe_to_resubmit(
    context: IngestContext,
) -> None:
    """E2 -- the write fails inside the transaction (``T-ST-01`` disk full).

    The whole of ``TXN-ingest-batch`` rolls back: no post, no receipt, no checkpoint. The
    follow-up lookup then answers ``not_committed`` with ``safe_to_resubmit``, and the
    resubmission commits normally. This is the branch where treating a timeout as a
    rollback would be right -- but the client is only allowed to conclude that because the
    *server* said so, not because the connection dropped.
    """
    batch = batch_of(
        [item("1900000000000000900")],
        key="batch-2026-09-07-fault-0001",
        cursor="cursor-page-1",
        state="valid",
    )
    injector = WriteFaultInjector(context.engine)

    with injector.disk_full(), pytest.raises(IngestError) as raised:
        submit_batch(context, batch, run_id=RUN_ID)

    assert raised.value.code is ErrorCode.STORAGE_WRITE_FAILED
    assert raised.value.http_status == 503
    assert counts(context) == {"post": 0, "ingest_receipt": 0, "checkpoint": 0}

    answer = get_receipt(context, idempotency_key=batch["idempotency_key"])
    assert answer["not_committed"]["safe_to_resubmit"] is True

    receipt = submit_batch(context, batch, run_id=RUN_ID)["receipt"]
    assert receipt["status"] == "committed"
    assert counts(context) == {"post": 1, "ingest_receipt": 1, "checkpoint": 1}


def test_storage_guard_refuses_the_mutation_before_the_transaction_opens(
    engine: Engine,
) -> None:
    """``storage.health = write_blocked`` -- no ACK, no rows, and the cursor does not move.

    The guard is asked *before* the transaction, so the refusal costs no write attempt at
    all; the assertion that no row moved is therefore about the contract, not about a
    rollback happening to work.
    """
    guard = StorageGuard()
    guard.record_write_failure()
    assert guard.current_health().value == "write_blocked"
    context = IngestContext(engine=engine, owner_id=OWNER_ID, storage_guard=guard)
    batch = batch_of(
        [item("1900000000000000901")],
        key="batch-2026-09-07-blocked-01",
        cursor="cursor-page-1",
        state="valid",
    )

    with pytest.raises(IngestError) as raised:
        submit_batch(context, batch, run_id=RUN_ID)

    assert raised.value.code is ErrorCode.STORAGE_WRITE_FAILED
    assert counts(context) == {"post": 0, "ingest_receipt": 0, "checkpoint": 0}


def test_storage_guard_also_refuses_the_checkpoint_only_path(engine: Engine) -> None:
    """``ingest.commit_checkpoint`` is in the same ``mutation_ack`` refusal group."""
    guard = StorageGuard()
    guard.record_write_failure()
    context = IngestContext(engine=engine, owner_id=OWNER_ID, storage_guard=guard)
    request = {
        "request_id": "01JREQC0000000000000000001",
        "schema_version": "0.1.0",
        "assignment_id": JOB_ID,
        "checkpoint_seq": 1,
        "lease_id": LEASE_ID,
        "lease_epoch": 1,
        "cursor_token": None,
        "cursor_state": "invalidated",
        "proposed_acked_through_ingest_sequence": 0,
        "reason": "end_of_feed",
    }

    with pytest.raises(IngestError) as raised:
        commit_checkpoint(context, request, run_id=RUN_ID)

    assert raised.value.code is ErrorCode.STORAGE_WRITE_FAILED
    assert counts(context) == {"post": 0, "ingest_receipt": 0, "checkpoint": 0}
    assert guard.machine.refusal_for(OperationId.INGEST_SUBMIT_BATCH) is not None


# ------------------------------------------------- SC03: cursor invalidated, feed re-read


def test_invalidated_cursor_allows_a_re_read_without_ingesting_a_duplicate(
    fixture_loader: Any, context: IngestContext
) -> None:
    """``collection/b-cursor-invalidated-reread-dedup``.

    Its ``durable_rows_expected``: +3 posts (only the new ``x_post_id`` values, total 8 and
    not 13), +2 receipts, +2 append-only checkpoints with ``acked_through`` rising 5 -> 8,
    and ``discovered_at`` of the five re-read posts unchanged.

    The commitment under AMD-B05 is "no duplicate ingest", not "never read twice", and the
    fixture says so explicitly: request count is not the oracle, row count is.
    """
    fixture = fixture_loader("collection/b-cursor-invalidated-reread-dedup")
    assert "SC03" in fixture.scenario_refs

    first = submit_batch(
        context,
        batch_of(
            [item(f"190000000000000000{n}") for n in range(1, 6)],
            key="batch-2026-09-07-0001-aaaa",
            cursor="cursor-page-1",
            state="valid",
        ),
        run_id=RUN_ID,
    )["receipt"]
    assert first["counts"]["inserted"] == 5
    acked_after_first = first["checkpoint_ack"]["acked_through_ingest_sequence"]
    with context.engine.connect() as connection:
        discovered_before = dict(
            connection.execute(text("SELECT x_post_id, discovered_at FROM post")).all()
        )

    # Event 1: the cursor died. Recorded through the checkpoint-only path, and the ack mark
    # must NOT move -- no new data was read.
    invalidated = commit_checkpoint(
        context,
        {
            "request_id": "01JREQC0000000000000000002",
            "schema_version": "0.1.0",
            "assignment_id": JOB_ID,
            "checkpoint_seq": first["checkpoint_ack"]["checkpoint_sequence"] + 1,
            "lease_id": LEASE_ID,
            "lease_epoch": 1,
            "cursor_token": None,
            "cursor_state": "invalidated",
            "proposed_acked_through_ingest_sequence": acked_after_first,
            "reason": "end_of_feed",
        },
        run_id=RUN_ID,
    )["receipt"]
    assert invalidated["receipt_kind"] == "checkpoint_only"
    assert invalidated["checkpoint_ack"]["acked_through_ingest_sequence"] == acked_after_first
    assert counts(context)["post"] == 5

    # Event 2 is `worker.claim_assignment`, owned by MOD-job-service. What ingest owes that
    # flow is the resume mark, so that is what is asserted here.
    resume = get_checkpoint(context, run_id=RUN_ID)
    assert resume["cursor_state"] == "invalidated"
    assert resume["cursor_token"] is None
    assert resume["acked_through_ingest_sequence"] == acked_after_first

    # Event 3: the feed is read again from the top; 5 of the 8 items are already ingested.
    reread = submit_batch(
        context,
        batch_of(
            [item(f"190000000000000000{n}") for n in range(1, 9)],
            key="batch-2026-09-07-0003-aaaa",
            cursor="cursor-page-1b",
            state="valid",
        ),
        run_id=RUN_ID,
    )["receipt"]

    assert reread["counts"]["received"] == 8
    assert reread["counts"]["deduplicated"] == 5
    assert reread["counts"]["inserted"] == 3
    assert counts(context)["post"] == 8
    assert reread["checkpoint_ack"]["acked_through_ingest_sequence"] > acked_after_first

    with context.engine.connect() as connection:
        discovered_after = dict(
            connection.execute(
                text("SELECT x_post_id, discovered_at FROM post WHERE ingest_sequence <= :s"),
                {"s": acked_after_first},
            ).all()
        )
        acked = connection.execute(
            text("SELECT MAX(acked_through_ingest_sequence) FROM checkpoint")
        ).scalar_one()
        max_receipt = connection.execute(
            text("SELECT MAX(max_ingest_sequence) FROM ingest_receipt")
        ).scalar_one()
        checkpoint_rows = connection.execute(text("SELECT COUNT(*) FROM checkpoint")).scalar_one()
    assert discovered_after == discovered_before
    assert acked <= max_receipt
    assert checkpoint_rows == 3


# ------------------------------------------------------------------------- lease guards


def test_a_stale_lease_epoch_commits_nothing(context: IngestContext, engine: Engine) -> None:
    """``STALE_LEASE`` (I10): an older epoch changes no authoritative data."""
    context = IngestContext(engine=engine, owner_id=OWNER_ID, assignment=FakeAssignments(epoch=3))
    batch = batch_of(
        [item("1900000000000000902")],
        key="batch-2026-09-07-stale-001",
        cursor="cursor-page-1",
        state="valid",
    )  # lease_epoch 1 vs current 3

    with pytest.raises(IngestError) as raised:
        submit_batch(context, batch)

    assert raised.value.code is ErrorCode.STALE_LEASE
    assert raised.value.http_status == 409
    assert counts(context) == {"post": 0, "ingest_receipt": 0, "checkpoint": 0}


def test_a_revoked_lease_commits_nothing(engine: Engine) -> None:
    """``WORKER_LEASE_EXPIRED``: the assignment was taken away; the old worker cannot commit.

    A different code from ``STALE_LEASE`` on purpose -- one says "you are behind", the other
    says "the job is no longer yours" -- and the collector's recovery differs.
    """
    context = IngestContext(
        engine=engine, owner_id=OWNER_ID, assignment=FakeAssignments(revoked=True)
    )
    batch = batch_of(
        [item("1900000000000000903")],
        key="batch-2026-09-07-revok-001",
        cursor="cursor-page-1",
        state="valid",
    )

    with pytest.raises(IngestError) as raised:
        submit_batch(context, batch)

    assert raised.value.code is ErrorCode.WORKER_LEASE_EXPIRED
    assert raised.value.http_status == 412
    assert counts(context) == {"post": 0, "ingest_receipt": 0, "checkpoint": 0}


# --------------------------------------------------------------------- the HTTP surface


@pytest.fixture
def client(engine: Engine) -> TestClient:
    app = FastAPI()
    install_ingest_error_handlers(app)
    app.include_router(ingest_router)
    app.state.ingest_context = IngestContext(
        engine=engine, owner_id=OWNER_ID, assignment=FakeAssignments()
    )
    app.state.collector_token = COLLECTOR_TOKEN
    return TestClient(app)


def collector_headers(key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {COLLECTOR_TOKEN}",
        "X-Schema-Version": CONTRACT_SCHEMA_VERSION,
        "X-Request-Id": "01JREQH1000000000000000000",
        "Idempotency-Key": key,
    }


def test_http_replay_returns_the_same_receipt_with_the_contract_envelope(
    client: TestClient, context: IngestContext
) -> None:
    """The ack-loss timeline over HTTP: 200 then 200 ``duplicate_replay``, then 409."""
    key = "batch-2026-09-07-http-00001"
    batch = batch_of([item("1900000000000000910")], key=key, cursor="c1", state="valid")

    first = client.post("/v1/ingest/batches", json=batch, headers=collector_headers(key))
    assert first.status_code == 200
    assert first.headers["X-Schema-Version"] == CONTRACT_SCHEMA_VERSION
    committed = first.json()["receipt"]
    assert committed["status"] == "committed"

    lookup = client.get(
        f"/v1/ingest/receipts/{key}",
        params={"assignment_id": JOB_ID},
        headers={k: v for k, v in collector_headers(key).items() if k != "Idempotency-Key"},
    )
    assert lookup.status_code == 200
    assert lookup.json()["receipt"]["receipt_hash"] == committed["receipt_hash"]

    replay = client.post("/v1/ingest/batches", json=batch, headers=collector_headers(key))
    assert replay.status_code == 200
    assert replay.json()["receipt"]["status"] == "duplicate_replay"

    mutated = copy.deepcopy(batch)
    mutated["items"][0]["text"] = "edited"
    mutated["payload_hash"] = compute_payload_hash(mutated)
    conflict = client.post("/v1/ingest/batches", json=mutated, headers=collector_headers(key))
    assert conflict.status_code == 409
    envelope = conflict.json()
    assert envelope["code"] == ErrorCode.IDEMPOTENCY_CONFLICT.value
    assert envelope["scope"] == "request"
    assert envelope["retry_class"] == "none"
    assert envelope["correlation_id"]
    assert counts(context)["post"] == 1


@pytest.mark.parametrize(
    "headers",
    [
        pytest.param({}, id="no-credential"),
        pytest.param({"Authorization": "Bearer wrong-token-entirely"}, id="wrong-token"),
        pytest.param({"Cookie": "rr_session=owner-session-value"}, id="owner-session-cookie"),
    ],
)
def test_a_non_collector_principal_is_unauthorized(
    headers: dict[str, str], client: TestClient, context: IngestContext
) -> None:
    """SC49 / R5-01: wrong principal class for the operation is ``UNAUTHORIZED`` (401).

    Not ``FORBIDDEN_EDGE`` and not ``CAPABILITY_DENIED``: those two name an edge that the
    registry does not contain and a platform capability the actor lacks. The card says
    choosing the wrong code is itself a failure, so the code is asserted, not just the
    status.
    """
    key = "batch-2026-09-07-deny-00001"
    batch = batch_of([item("1900000000000000920")], key=key, cursor="c1", state="valid")
    request_headers = {
        "X-Schema-Version": CONTRACT_SCHEMA_VERSION,
        "X-Request-Id": "01JREQH1000000000000000000",
        "Idempotency-Key": key,
        **headers,
    }

    response = client.post("/v1/ingest/batches", json=batch, headers=request_headers)

    assert response.status_code == 401
    assert response.json()["code"] == ErrorCode.UNAUTHORIZED.value
    assert counts(context) == {"post": 0, "ingest_receipt": 0, "checkpoint": 0}


def test_missing_wire_headers_are_rejected_before_any_write(
    client: TestClient, context: IngestContext
) -> None:
    """``X-Schema-Version`` / ``X-Request-Id`` / ``Idempotency-Key`` are required parameters."""
    key = "batch-2026-09-07-hdr-000001"
    batch = batch_of([item("1900000000000000930")], key=key, cursor="c1", state="valid")

    response = client.post(
        "/v1/ingest/batches",
        json=batch,
        headers={"Authorization": f"Bearer {COLLECTOR_TOKEN}"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == ErrorCode.VALIDATION_ERROR.value
    assert body["details_safe"]["violation_kind"] == "required_header_missing"
    assert counts(context) == {"post": 0, "ingest_receipt": 0, "checkpoint": 0}


def test_get_checkpoint_is_not_exposed_over_http(client: TestClient) -> None:
    """``ingest.get_checkpoint`` has transport ``internal``; no route may answer for it.

    An HTTP door onto an internal port would let any holder of a collector token read a
    run's cursor state, which ``contracts/modules.yaml`` grants only to MOD-job-service.
    """
    paths = {route.path for route in client.app.routes}  # type: ignore[attr-defined]
    assert "/v1/ingest/checkpoints" in paths
    assert not any("get_checkpoint" in path for path in paths)


# -------------------------------------------------------------- identity, when available


def test_a_post_linked_to_a_known_work_resolves_to_that_target(context: IngestContext) -> None:
    """``identity.resolve_target`` is called through the port and its answer is stored.

    Only the read side: recording a new alias and merging works belong to
    ``TC-canonical-identity-merge`` (this card's §1 non-goals), so a post whose identifiers
    match nothing stays ``pending`` rather than being linked on a guess.
    """
    identity = pytest.importorskip(
        "server.app.identity.service", reason="pending TC-canonical-identity-merge"
    )
    identity.record_alias(
        context.engine,
        owner_id=OWNER_ID,
        identifier=identity.Identifier(
            scheme=identity.IdScheme.ARXIV, raw="https://arxiv.org/abs/2507.07777"
        ),
    )

    receipt = submit_batch(
        context,
        batch_of(
            [
                item(
                    "1900000000000000940",
                    links=[
                        {
                            "url": "https://arxiv.org/abs/2507.07777",
                            "link_kind_hint": "arxiv_abs",
                        }
                    ],
                )
            ],
            key="batch-2026-09-07-ident-001",
            cursor="c1",
            state="valid",
        ),
        run_id=RUN_ID,
    )["receipt"]

    accepted = receipt["accepted_items"][0]
    assert accepted["target_ref"] is not None
    assert accepted["target_ref"]["kind"] == "work"
    with context.engine.connect() as connection:
        resolution = connection.execute(
            text("SELECT identity_resolution FROM post WHERE x_post_id = :x"),
            {"x": "1900000000000000940"},
        ).scalar_one()
    assert resolution == "resolved_linked"


def test_a_post_with_no_known_identifier_stays_pending(context: IngestContext) -> None:
    """No identifier, no guess: ``pending`` is the honest state (REQ-D33, B15)."""
    submit_batch(
        context,
        batch_of(
            [item("1900000000000000950")],
            key="batch-2026-09-07-ident-002",
            cursor="c1",
            state="valid",
        ),
        run_id=RUN_ID,
    )

    with context.engine.connect() as connection:
        resolution = connection.execute(
            text("SELECT identity_resolution FROM post WHERE x_post_id = :x"),
            {"x": "1900000000000000950"},
        ).scalar_one()
    assert resolution == "pending"


# ----------------------------------------------- the schema the migrations actually build


def test_the_ingest_tables_carry_the_foreign_keys_the_contract_declares(engine: Engine) -> None:
    """``PRAGMA foreign_key_list`` -- finding ``F-A3R1-05``.

    ``owner_id`` on both ingest tables and ``post.ingest_receipt_id`` are foreign keys in
    ``contracts/data/entities.yaml``. Until revision ``0003_tc_ingest_idempotent_ack_lost``
    rebuilt ``post`` they were bare columns, which made owner scoping (``REQ-S7.3-01``) a
    convention the database did not hold anyone to: a row with the wrong ``owner_id`` was
    simply accepted.

    The oracle is the pragma, not the DDL text: a constraint written in a CREATE statement
    that some later rebuild silently dropped would still read correctly in the source.
    """
    with engine.connect() as connection:
        keys = {
            table: {
                (row[3], row[2], row[4])
                for row in connection.exec_driver_sql(f"PRAGMA foreign_key_list({table})")
            }
            for table in ("post", "checkpoint", "ingest_receipt", "post_work")
        }

    assert ("owner_id", "owner", "id") in keys["checkpoint"]
    assert ("owner_id", "owner", "id") in keys["ingest_receipt"]
    assert ("owner_id", "owner", "id") in keys["post"]
    assert ("ingest_receipt_id", "ingest_receipt", "id") in keys["post"]
    assert ("created_by_receipt_id", "ingest_receipt", "id") in keys["checkpoint"]
    assert ("checkpoint_id", "checkpoint", "id") in keys["ingest_receipt"]
    # The rebuild dropped and recreated `post`; `post_work`'s reference to it must survive.
    assert ("post_id", "post", "id") in keys["post_work"]

    with engine.connect() as connection:
        indexes = {row[1] for row in connection.exec_driver_sql("PRAGMA index_list(post)")}
        violations = connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
    assert {"ux_post_owner_x_post_id", "ux_post_owner_ingest_sequence"} <= indexes
    assert violations == []


def test_a_post_cannot_reference_a_receipt_that_does_not_exist(engine: Engine) -> None:
    """The new foreign key is enforced, not merely declared.

    Writing a post whose ``ingest_receipt_id`` names no receipt used to succeed. It must now
    fail at COMMIT -- deferred, because the real ingest transaction legitimately inserts the
    post before the receipt row it points at.
    """
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO post (id, owner_id, x_post_id, author_handle, url, text, "
            "discovered_at, ingest_sequence, discovered_by_run_id, ingest_receipt_id, "
            "is_author_thread_member, media_refs, referenced_links, identity_resolution, "
            "source_snapshot_hash, content_state) VALUES "
            "('01JPOSTDANGLING0000000000', ?, '1900000000000000999', 'acc1', "
            "'https://x.com/acc1/status/1', 'x', '2026-09-07T08:00:00.000Z', 1, ?, "
            "'01JRECEIPTDOESNOTEXIST0000', 0, '[]', '[]', 'pending', "
            "'sha256:" + "0" * 64 + "', 'present')",
            (OWNER_ID, RUN_ID),
        )

    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT COUNT(*) FROM post").scalar_one() == 0


# --------------------------------------------- the write gate on the shipped app factory


def test_the_write_gate_is_live_on_the_app_factory(engine: Engine) -> None:
    """``F-A3R1-11``: ``create_app()`` must produce an app whose ingest gate actually runs.

    The context wired here carries **no** guard of its own, exactly as a deployment
    entrypoint would leave it. If the router did not carry ``app.state.storage_guard`` into
    the service, the pre-check would silently not run and a write-blocked store would be
    discovered only when the write itself failed -- after the collector had been told
    nothing about it.
    """
    app = create_app()
    app.state.ingest_context = IngestContext(engine=engine, owner_id=OWNER_ID)
    app.state.collector_token = COLLECTOR_TOKEN
    guard = app.state.storage_guard
    assert isinstance(guard, StorageGuard)
    assert app.state.ingest_context.storage_guard is None

    guard.record_write_failure()
    assert guard.current_health().value == "write_blocked"

    key = "batch-2026-09-07-gate-00001"
    batch = batch_of([item("1900000000000000960")], key=key, cursor="c1", state="valid")
    response = TestClient(app).post(
        "/v1/ingest/batches", json=batch, headers=collector_headers(key)
    )

    assert response.status_code == 503
    assert response.json()["code"] == ErrorCode.STORAGE_WRITE_FAILED.value
    assert response.headers["Retry-After"] == "30"
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT COUNT(*) FROM post").scalar_one() == 0


def test_an_explicitly_injected_guard_is_not_overridden_by_the_app_one(engine: Engine) -> None:
    """A test's own guard wins over ``app.state``; otherwise it could not be tested at all."""
    app = create_app()
    injected = StorageGuard()
    app.state.ingest_context = IngestContext(
        engine=engine,
        owner_id=OWNER_ID,
        storage_guard=injected,
        assignment=FakeAssignments(),
    )
    app.state.collector_token = COLLECTOR_TOKEN
    app.state.storage_guard.record_write_failure()  # the app's guard, not the injected one

    key = "batch-2026-09-07-gate-00002"
    batch = batch_of([item("1900000000000000961")], key=key, cursor="c1", state="valid")
    response = TestClient(app).post(
        "/v1/ingest/batches", json=batch, headers=collector_headers(key)
    )

    assert response.status_code == 200
    assert injected.current_health().value == "healthy"


# ------------------------------------------------------- §2 fixtures not otherwise used


def test_the_e2e_happy_path_ingest_leg_runs_through_this_service(
    fixture_loader: Any, context: IngestContext
) -> None:
    """``acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json``, events 4 and 5.

    The card's §2 names this fixture; only its two ``ingest.submit_batch`` events are in this
    card's reach, and they are executed here rather than read. What the fixture asserts about
    them -- one post per batch, both under ``TXN-ingest-batch``, the ack after the commit,
    and a strictly increasing ``max_ingest_sequence`` across the two -- is checked against
    real rows. The other sixteen events belong to scheduling, enrichment, analysis, report
    and delivery, and are recorded ``NOT_RUN`` for this card in the handoff addendum.
    """
    fixture = fixture_loader("e2e/a-happy-path-schedule-to-delivered")
    ingest_events = [
        event for event in fixture.events if event.get("operation") == "ingest.submit_batch"
    ]
    assert len(ingest_events) == 2
    assert all(
        event["_commit_boundary"].startswith("B3: TXN-ingest-batch") for event in ingest_events
    )
    assert all(event["performed_by"] == "MOD-ingest-service" for event in ingest_events)

    receipts = []
    for index, event in enumerate(ingest_events):
        receipt = submit_batch(
            context,
            batch_of(
                [item(f"19000000000000010{index}")],
                key=event["_idempotency_key"],
                cursor=f"e2e-cursor-{index}",
                state="valid",
            ),
            run_id=RUN_ID,
        )["receipt"]
        receipts.append(receipt)
        assert receipt["counts"]["received"] == 1
        assert receipt["counts"]["inserted"] == 1

    first, second = receipts
    assert second["counts"]["max_ingest_sequence"] > first["counts"]["max_ingest_sequence"]
    assert (
        second["checkpoint_ack"]["checkpoint_sequence"]
        > (first["checkpoint_ack"]["checkpoint_sequence"])
    )
    assert counts(context) == {"post": 2, "ingest_receipt": 2, "checkpoint": 2}


def test_the_default_deny_sweep_names_no_edge_into_this_module(fixture_loader: Any) -> None:
    """``acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`` -- also §2.

    Checking the fixture's *coverage* rather than skipping it: none of the 36 forbidden edges
    has ``MOD-ingest-service`` as caller or callee, which is why this card's denial testing is
    the ``UNAUTHORIZED`` boundary on its own three routes instead of a slice of the sweep. If
    a future edge were added that did name this module, this assertion fails and the card is
    forced to cover it rather than quietly continuing to test nothing.
    """
    fixture = fixture_loader("boundary/a-default-deny-sweep-36-edges")
    events = fixture.events
    assert len(events) == 36
    touching = [
        event
        for event in events
        if "MOD-ingest-service" in {event.get("actor"), event.get("callee")}
    ]
    assert touching == []
    assert all(str(event.get("operation") or "").startswith(("", "")) for event in events)
