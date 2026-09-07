"""E1 -- replay, conflict and the checkpoint-only path.

Oracles come from three fixtures and from I02 itself:

* ``acceptance/fixtures/identity/f-ingest-replay-idempotent.json`` -- same key + same
  payload returns the same receipt, ``receipt_hash`` unchanged, every count unchanged;
  same key + different payload is ``IDEMPOTENCY_CONFLICT`` with nothing overwritten.
* ``acceptance/fixtures/collection/d-duplicate-ingest-replay.json`` -- the ack-loss
  procedure: look the receipt up first, and a resubmission returns
  ``status = duplicate_replay`` with an identical ``receipt_hash``.
* ``contracts/data/invariants.md`` §I02 -- the inequality
  ``checkpoint.acked_through_ingest_sequence <= MAX(ingest_receipt.max_ingest_sequence)``
  after *any* interleaving of the two operations.

One deliberate deviation, reported as ``CR-TC-ingest-02``
--------------------------------------------------------
``f-ingest-replay-idempotent`` states its ``given`` as three ``post`` rows with
``ingest_receipt: []`` and ``checkpoint: []``. That state cannot exist: ``ENT-post`` makes
``ingest_receipt_id`` NOT NULL with a foreign key to ``ingest_receipt``, so a post without
a receipt is unrepresentable in the schema the same contract defines. Rather than weaken
the schema to admit the fixture's literal rows, the three prior posts are created here
through a real earlier ``ingest.submit_batch`` -- the only way they could have come to
exist in production. The consequence is that the absolute sequence numbers differ from the
fixture's illustrative 91..93 / 100; every *relational* oracle the fixture states (counts,
the 7+3+0=10 arithmetic, hash equality, the cursor inequality) is asserted unchanged.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import pytest
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.ingest.idempotency import compute_payload_hash
from server.app.ingest.repository import IngestRepository
from server.app.ingest.service import (
    IngestContext,
    IngestError,
    commit_checkpoint,
    get_checkpoint,
    get_receipt,
    submit_batch,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01J0WNER100000000000000000"
RUN_ID = "01JRVNF1000000000000000000"
ASSIGNMENT_ID = "01JJ0BF1000000000000000000"
LEASE_ID = "01J1EASEF10000000000000000"


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


def counts(context: IngestContext) -> dict[str, int]:
    repository = IngestRepository()
    with context.engine.connect() as connection:
        return {
            table: repository.count_rows(connection, table)
            for table in ("post", "ingest_receipt", "checkpoint")
        }


def scalar(context: IngestContext, sql: str) -> Any:
    with context.engine.connect() as connection:
        return connection.execute(text(sql)).scalar()


def assert_i02_cursor_inequality(context: IngestContext) -> None:
    """``acked_through_ingest_sequence`` never points past durable data.

    Both forms from ``invariants.md`` §I02: against the committed receipts, and the
    stronger one directly against ``post``. Asserted after every event in this module, not
    once at the end -- the invariant is about every observable moment, and checking only the
    final state would miss an implementation that overshoots and corrects itself.
    """
    acked = scalar(
        context, "SELECT COALESCE(MAX(acked_through_ingest_sequence), 0) FROM checkpoint"
    )
    max_receipt = scalar(
        context, "SELECT COALESCE(MAX(max_ingest_sequence), 0) FROM ingest_receipt"
    )
    max_post = scalar(context, "SELECT COALESCE(MAX(ingest_sequence), 0) FROM post")
    assert acked <= max_receipt
    assert acked <= max_post or max_post == 0


def rekey(batch: dict[str, Any], key: str) -> dict[str, Any]:
    """Copy a batch under a new idempotency key, recomputing nothing else.

    ``payload_hash`` is unchanged on purpose: it covers ``payload_core`` only, so a batch
    resent under a different key keeps its hash. ``TXN-ingest-batch`` calls that case
    ``different_key_same_content`` and expects it to commit normally, with row-level dedup
    doing the work.
    """
    copied = copy.deepcopy(batch)
    copied["idempotency_key"] = key
    return copied


def seed_prior_posts(context: IngestContext, batch: dict[str, Any]) -> dict[str, Any]:
    """Create the fixture's three pre-existing posts through the real ingest path."""
    seed = copy.deepcopy(batch)
    seed["items"] = seed["items"][:3]
    seed["idempotency_key"] = "ingest-2026-09-06-run-f-seed-0000"
    seed["client_checkpoint_proposal"] = dict(seed["client_checkpoint_proposal"])
    seed["client_checkpoint_proposal"]["cursor_token"] = "cursor-page-1"
    seed["payload_hash"] = compute_payload_hash(seed)
    submit_batch(context, seed, run_id=RUN_ID)
    return seed


# --------------------------------------------------------------------------- replay


def test_replay_of_the_same_key_returns_the_same_receipt(
    fixture_loader: Any, context: IngestContext
) -> None:
    """FX-ID-F events 1 and 3: the ack was lost, the collector resent, nothing moved.

    The assertion set is the fixture's ``deltas_must_be_zero`` for every table this card
    owns, plus its ``hash_oracles``: ``receipt_hash`` after the replay equals ``H_RCf`` from
    the first commit, and ``received = inserted + deduplicated + rejected``.
    """
    fixture = fixture_loader("identity/f-ingest-replay-idempotent")
    batch = fixture.data["batch"]
    seed_prior_posts(context, batch)
    after_seed = counts(context)
    assert after_seed["post"] == 3

    first = submit_batch(context, batch, run_id=RUN_ID)["receipt"]
    assert first["status"] == "committed"
    assert first["receipt_kind"] == "batch_ingest"
    assert first["counts"]["received"] == 10
    assert first["counts"]["inserted"] == 7
    assert first["counts"]["deduplicated"] == 3
    assert first["counts"]["rejected"] == 0
    assert (
        first["counts"]["inserted"] + first["counts"]["deduplicated"] + first["counts"]["rejected"]
        == first["counts"]["received"]
    )
    after_commit = counts(context)
    assert after_commit["post"] == 10
    assert_i02_cursor_inequality(context)

    # Event 2 of the fixture is the network dropping the response. Nothing to execute: the
    # server has already committed and simply never learns the ACK was lost.
    replay = submit_batch(context, rekey(batch, batch["idempotency_key"]), run_id=RUN_ID)["receipt"]

    assert replay["status"] == "duplicate_replay"
    assert replay["receipt_id"] == first["receipt_id"]
    assert replay["receipt_hash"] == first["receipt_hash"]
    assert replay["counts"] == first["counts"]
    assert replay["checkpoint_ack"] == first["checkpoint_ack"]
    assert counts(context) == after_commit
    assert_i02_cursor_inequality(context)


def test_replay_leaves_discovered_at_of_duplicate_posts_untouched(
    fixture_loader: Any, context: IngestContext
) -> None:
    """A re-read must not make an old post look newly discovered (SRC-PLAN §9.1).

    ``discovered_at`` is the left edge a coverage window is measured against, so refreshing
    it on a duplicate would silently move a post from one period into another.
    """
    fixture = fixture_loader("identity/f-ingest-replay-idempotent")
    batch = fixture.data["batch"]
    seed_prior_posts(context, batch)
    with context.engine.connect() as connection:
        before = dict(
            connection.execute(text("SELECT x_post_id, discovered_at FROM post")).all()  # noqa: B905
        )

    submit_batch(context, batch, run_id=RUN_ID)

    with context.engine.connect() as connection:
        after = dict(
            connection.execute(
                text("SELECT x_post_id, discovered_at FROM post WHERE x_post_id IN (:a, :b, :c)"),
                {
                    "a": "1900000000000000101",
                    "b": "1900000000000000102",
                    "c": "1900000000000000103",
                },
            ).all()
        )
    assert after == before


def test_same_key_with_a_different_payload_is_a_conflict(
    fixture_loader: Any, context: IngestContext
) -> None:
    """FX-ID-F event 4: same key, edited first item, so a different ``payload_hash``.

    The fixture names a specific hex value for the mutated payload; that value belongs to
    its author's exact edit, so the edit itself is reproduced here ("text of the first item
    was changed") and the hash recomputed. What is asserted is the fixture's rule, not its
    hex: ``IDEMPOTENCY_CONFLICT`` and no overwrite.
    """
    fixture = fixture_loader("identity/f-ingest-replay-idempotent")
    batch = fixture.data["batch"]
    seed_prior_posts(context, batch)
    committed = submit_batch(context, batch, run_id=RUN_ID)["receipt"]
    before = counts(context)

    mutated = copy.deepcopy(batch)
    mutated["items"][0]["text"] = "Bài đã có 1 (đã sửa)"
    mutated["payload_hash"] = compute_payload_hash(mutated)
    assert mutated["payload_hash"] != batch["payload_hash"]

    with pytest.raises(IngestError) as raised:
        submit_batch(context, mutated, run_id=RUN_ID)

    assert raised.value.code is ErrorCode.IDEMPOTENCY_CONFLICT
    assert raised.value.http_status == 409
    details = raised.value.details_safe or {}
    assert details["payload_hash_stored"] == batch["payload_hash"]
    assert details["payload_hash_seen"] == mutated["payload_hash"]
    assert counts(context) == before

    stored = get_receipt(context, idempotency_key=batch["idempotency_key"])["receipt"]
    assert stored["receipt_hash"] == committed["receipt_hash"]
    assert_i02_cursor_inequality(context)


def test_a_different_key_with_the_same_content_commits_and_dedups_by_row(
    fixture_loader: Any, context: IngestContext
) -> None:
    """``TXN-ingest-batch.idempotency.different_key_same_content`` -- correct, not an error.

    A new key means a new receipt; ``ux_post_owner_x_post_id`` means no new post. The
    commitment is "no duplicate ingest", not "no repeated request".
    """
    fixture = fixture_loader("identity/f-ingest-replay-idempotent")
    batch = fixture.data["batch"]
    seed_prior_posts(context, batch)
    submit_batch(context, batch, run_id=RUN_ID)
    before = counts(context)

    again = submit_batch(context, rekey(batch, "ingest-2026-09-06-run-f-batch-0002"), run_id=RUN_ID)
    receipt = again["receipt"]

    assert receipt["status"] == "committed"
    assert receipt["counts"]["inserted"] == 0
    assert receipt["counts"]["deduplicated"] == 10
    assert counts(context)["post"] == before["post"]
    assert counts(context)["ingest_receipt"] == before["ingest_receipt"] + 1
    assert_i02_cursor_inequality(context)


def test_get_receipt_answers_not_committed_for_an_unknown_key(context: IngestContext) -> None:
    """``not_committed`` is a definite answer, unlike a client-side timeout.

    ``safe_to_resubmit`` is the single point in the contract that authorises a resend, so
    it may only appear on this branch.
    """
    answer = get_receipt(context, idempotency_key="ingest-2026-09-06-never-committed")
    assert answer["not_committed"]["status"] == "not_committed"
    assert answer["not_committed"]["safe_to_resubmit"] is True
    assert "receipt" not in answer


# ------------------------------------------------------------------- checkpoint-only


def checkpoint_only_request(
    *, seq: int, acked: int, cursor: str | None, state: str, reason: str = "end_of_feed"
) -> dict[str, Any]:
    return {
        "request_id": "01JREQC" + str(seq).rjust(19, "0"),
        "schema_version": "0.1.0",
        "assignment_id": ASSIGNMENT_ID,
        "checkpoint_seq": seq,
        "lease_id": LEASE_ID,
        "lease_epoch": 1,
        "cursor_token": cursor,
        "cursor_state": state,
        "proposed_acked_through_ingest_sequence": acked,
        "reason": reason,
    }


def test_checkpoint_only_advances_the_cursor_without_acknowledging_new_data(
    fixture_loader: Any, context: IngestContext
) -> None:
    """``TXN-checkpoint-only`` -- one checkpoint, one receipt, zero posts.

    Every ``forbidden_effect`` of that transaction is asserted: no post row, no rise in
    ``acked_through_ingest_sequence``, every count zero on the receipt, and the previous
    checkpoint row untouched (append-only).
    """
    fixture = fixture_loader("identity/f-ingest-replay-idempotent")
    batch = fixture.data["batch"]
    seed_prior_posts(context, batch)
    first = submit_batch(context, batch, run_id=RUN_ID)["receipt"]
    acked = first["checkpoint_ack"]["acked_through_ingest_sequence"]
    sequence = first["checkpoint_ack"]["checkpoint_sequence"]
    before = counts(context)
    with context.engine.connect() as connection:
        rows_before = connection.execute(
            text('SELECT id, "sequence", acked_through_ingest_sequence FROM checkpoint')
        ).all()

    receipt = commit_checkpoint(
        context,
        checkpoint_only_request(seq=sequence + 1, acked=acked, cursor=None, state="invalidated"),
        run_id=RUN_ID,
    )["receipt"]

    assert receipt["receipt_kind"] == "checkpoint_only"
    assert receipt["counts"] == {
        "received": 0,
        "inserted": 0,
        "deduplicated": 0,
        "quarantined": 0,
        "rejected": 0,
        "works_linked": 0,
        "max_ingest_sequence": acked,
    }
    assert receipt["checkpoint_ack"]["acked_through_ingest_sequence"] == acked
    assert receipt["checkpoint_ack"]["cursor_state"] == "invalidated"
    assert receipt["checkpoint_ack"]["cursor_token"] is None

    after = counts(context)
    assert after["post"] == before["post"]
    assert after["checkpoint"] == before["checkpoint"] + 1
    assert after["ingest_receipt"] == before["ingest_receipt"] + 1
    with context.engine.connect() as connection:
        rows_after = connection.execute(
            text('SELECT id, "sequence", acked_through_ingest_sequence FROM checkpoint')
        ).all()
    assert rows_after[: len(rows_before)] == rows_before
    assert_i02_cursor_inequality(context)


def test_checkpoint_only_refuses_a_cursor_past_the_acked_mark(
    fixture_loader: Any, context: IngestContext
) -> None:
    """The R-01 guard: counterexample 2 of I02, turned into a refusal that leaves no trace.

    A checkpoint pointing at data the server has not committed is exactly how a collector
    ends up skipping a range for ever, so the proposal is rejected and nothing partial is
    written.
    """
    fixture = fixture_loader("identity/f-ingest-replay-idempotent")
    batch = fixture.data["batch"]
    seed_prior_posts(context, batch)
    first = submit_batch(context, batch, run_id=RUN_ID)["receipt"]
    acked = first["checkpoint_ack"]["acked_through_ingest_sequence"]
    sequence = first["checkpoint_ack"]["checkpoint_sequence"]
    before = counts(context)

    with pytest.raises(IngestError) as raised:
        commit_checkpoint(
            context,
            checkpoint_only_request(
                seq=sequence + 1, acked=acked + 1, cursor="cursor-page-9", state="valid"
            ),
            run_id=RUN_ID,
        )

    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert (raised.value.details_safe or {})["violation_kind"] == "acked_through_exceeds_committed"
    assert counts(context) == before
    assert_i02_cursor_inequality(context)


def test_checkpoint_only_refuses_a_sequence_that_does_not_move_forward(
    fixture_loader: Any, context: IngestContext
) -> None:
    """``checkpoint.sequence`` is monotonic within a run; a repeat or a regression is rejected."""
    fixture = fixture_loader("identity/f-ingest-replay-idempotent")
    batch = fixture.data["batch"]
    seed_prior_posts(context, batch)
    first = submit_batch(context, batch, run_id=RUN_ID)["receipt"]
    acked = first["checkpoint_ack"]["acked_through_ingest_sequence"]
    sequence = first["checkpoint_ack"]["checkpoint_sequence"]
    before = counts(context)

    with pytest.raises(IngestError) as raised:
        commit_checkpoint(
            context,
            checkpoint_only_request(seq=sequence, acked=acked, cursor=None, state="valid"),
            run_id=RUN_ID,
        )

    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert (raised.value.details_safe or {})["violation_kind"] == "checkpoint_seq_regression"
    assert counts(context) == before


def test_checkpoint_only_rejects_a_body_carrying_items(context: IngestContext) -> None:
    """Card §7: ``item_count != 0`` on this path is a ``VALIDATION_ERROR``.

    ``ingest-receipt.schema.json#/$defs/checkpoint_only_request`` sets
    ``additionalProperties: false`` and declares no ``item_count`` member at all -- while
    ``contracts/ports.yaml`` describes the field as mandatory and zero. The wire schema
    wins, so any body carrying it is refused as an unknown field, which satisfies the §7
    obligation for every value. Reported as ``CR-TC-ingest-03``.
    """
    request = checkpoint_only_request(seq=1, acked=0, cursor=None, state="valid")
    request["item_count"] = 3

    with pytest.raises(IngestError) as raised:
        commit_checkpoint(context, request, run_id=RUN_ID)

    assert raised.value.code is ErrorCode.VALIDATION_ERROR


def test_checkpoint_only_replay_returns_the_stored_receipt(
    fixture_loader: Any, context: IngestContext
) -> None:
    """Same ``assignment_id + checkpoint_seq``: the stored receipt, no second checkpoint."""
    fixture = fixture_loader("identity/f-ingest-replay-idempotent")
    batch = fixture.data["batch"]
    seed_prior_posts(context, batch)
    first = submit_batch(context, batch, run_id=RUN_ID)["receipt"]
    request = checkpoint_only_request(
        seq=first["checkpoint_ack"]["checkpoint_sequence"] + 1,
        acked=first["checkpoint_ack"]["acked_through_ingest_sequence"],
        cursor=None,
        state="invalidated",
    )
    committed = commit_checkpoint(context, request, run_id=RUN_ID)["receipt"]
    before = counts(context)

    replay = commit_checkpoint(context, request, run_id=RUN_ID)["receipt"]

    assert replay["status"] == "duplicate_replay"
    assert replay["receipt_id"] == committed["receipt_id"]
    assert replay["receipt_hash"] == committed["receipt_hash"]
    assert counts(context) == before
    assert_i02_cursor_inequality(context)


def test_get_checkpoint_reports_the_latest_mark(
    fixture_loader: Any, context: IngestContext
) -> None:
    """``ingest.get_checkpoint`` -- the internal read ``MOD-job-service`` resumes from."""
    fixture = fixture_loader("identity/f-ingest-replay-idempotent")
    batch = fixture.data["batch"]
    seed_prior_posts(context, batch)
    receipt = submit_batch(context, batch, run_id=RUN_ID)["receipt"]

    state = get_checkpoint(context, run_id=RUN_ID)

    assert (
        state["acked_through_ingest_sequence"]
        == (receipt["checkpoint_ack"]["acked_through_ingest_sequence"])
    )
    assert state["checkpoint_sequence"] == receipt["checkpoint_ack"]["checkpoint_sequence"]
    assert state["cursor_token"] == receipt["checkpoint_ack"]["cursor_token"]


def test_get_checkpoint_is_not_found_for_a_run_without_one(context: IngestContext) -> None:
    """A run with no checkpoint is ``NOT_FOUND``, not an invented zero cursor."""
    with pytest.raises(IngestError) as raised:
        get_checkpoint(context, run_id="01JRVNZZ000000000000000000")
    assert raised.value.code is ErrorCode.NOT_FOUND
