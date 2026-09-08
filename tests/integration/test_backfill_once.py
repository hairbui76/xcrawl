"""E1/E2 — SC37/SC38: add → remove → re-add entitles the backfill exactly once.

Oracle fixtures: ``acceptance/fixtures/reporting/j-backfill-add-remove-readd.json`` and
``acceptance/fixtures/reporting/k-builder-crash-backfill-not-consumed.json``, used as data —
``given`` seeds a database created by the **real** Alembic migrations, ``events`` run through
the **real** service layer (``server.app.report.backfill`` for the entitlement decision,
``server.app.report.builder`` / ``publisher`` for the build and the publish transaction), and
``expected.counts``, ``expected.rows``, ``expected.row_oracles`` and — the half that catches
defects — ``forbidden_effects`` are asserted.

Why the re-add is the interesting half
---------------------------------------
"Backfill is granted once" is easy to satisfy by granting it once and never testing a second
add. The defect this file exists to catch is subtler: ``ux_tag_owner_text_active`` is partial
on ``state = 'active'``, so removing a tag and adding the same words back produces a **new**
``tag.id``. An entitlement keyed on ``tag_id`` is therefore re-granted on every re-add, and
every count in a naive test still looks right — there genuinely is one row per tag. The
oracle that separates the two implementations is the one fixture ``j`` states: count the
consumed rows **grouped by subscription identity**, not by tag.

On the literal hashes in the fixture
-------------------------------------
``acceptance/fixtures/reporting/README.md`` §4 says the hex strings in these files are shape
only ("fixture khẳng định **quan hệ**, không khẳng định một chuỗi hex bịa") and they are not
recomputable from the §6.2 preimage — ``test_the_fixture_hashes_are_shape_only_by_the_readme_rule``
asserts this is still true rather than leaving it a footnote. Every hash assertion
below is therefore about the *relation*: the two activations share one identity, a different
wording does not, and the consumed count per identity is one.

What is deliberately not asserted here
---------------------------------------
The ``tag.create`` / ``tag.delete`` HTTP operations. No card in the 19 implements them —
``TC-backfill-pending-ledger`` §3 creates ``server/app/tags/rescan.py`` and no tag router — so
the tag row itself is written by :func:`create_tag` below as fixture data, in the same
transaction as the entitlement decision the service layer really does make. Recorded as
``CR-TC-BACKFILL-07``.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.db.faults import WriteFaultInjector
from server.app.embedding.generation import (
    DeterministicHashEncoder,
    GenerationFingerprint,
    Normalization,
    Vector,
)
from server.app.embedding.service import EmbeddingService
from server.app.report import backfill
from server.app.report.backfill import (
    ENTITLEMENT_CONSUMED,
    ENTITLEMENT_DENIED,
    ENTITLEMENT_GRANTED,
    REASON_ALREADY_CONSUMED,
    REASON_FIRST_ACTIVATION,
    BackfillError,
    Entitlement,
    TableSettings,
    backfill_days,
    candidate_range,
    entitlements_to_consume,
    normalize_tag_text,
    open_activation,
    plan_extension,
    subscription_identity_hash,
)
from server.app.report.builder import (
    BuildSnapshot,
    NoBackfill,
    SelectionSettings,
    ServiceBackfill,
    TagConfigVersion,
    build_report,
)
from server.app.report.coverage import new_ulid, parse_timestamp_utc_ms
from server.app.report.publisher import PublishContext, publish_report, record_build

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "acceptance" / "fixtures" / "reporting"

OWNER_ID = "01JW0WNER00000000000000000"
GENERATION_ID = "01JEMBGEN10000000000000000"
MODEL_NAME = "multilingual-e5-small"
MODEL_VERSION = "1.0.0"
DIMENSION = 4

#: Fixture ``j``'s two tag rows: same words, two ``tag.id`` values.
TAG_V1 = "01JTAGGNN00000000000000000"
TAG_V2 = "01JTAGGNN20000000000000000"
TAG_TEXT = "graph neural networks"

WORK_OLD = "01JWRKOLD10000000000000000"
WORK_NEW = "01JWRKNEW10000000000000000"

FINGERPRINT = GenerationFingerprint(
    generation_id=GENERATION_ID,
    model_name=MODEL_NAME,
    model_version=MODEL_VERSION,
    dimension=DIMENSION,
    normalization=Normalization.L2,
)

MOD_JOB = "MOD-job-service"


# --------------------------------------------------------------------------------------
# Harness
# --------------------------------------------------------------------------------------


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
    """A fresh database at ``head``, with the owner, the generation and ``settings`` seeded.

    ``reporting.backfill_days`` comes from fixture ``j``'s ``given.settings``, which is where
    card §10 ``SG-03`` says the number lives. Nothing in ``server/app`` carries the value.
    """
    db_path = tmp_path / "radar.db"
    _upgrade(db_path)
    built = create_sqlite_engine(db_path)
    fixture = json.loads((FIXTURES / "j-backfill-add-remove-readd.json").read_text("utf-8"))
    days = fixture["given"]["settings"]["reporting.backfill_days"]
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
        connection.execute(
            text(
                'INSERT INTO settings (id, owner_id, "key", value_json, updated_at)'
                " VALUES (:id, :owner, 'reporting.backfill_days', :value,"
                " '2026-09-01T00:00:00.000Z')"
            ),
            {"id": new_ulid(), "owner": OWNER_ID, "value": json.dumps(days)},
        )
    try:
        yield built
    finally:
        built.dispose()


def unit(x: float, y: float) -> Vector:
    norm = (x * x + y * y) ** 0.5
    return Vector(fingerprint=FINGERPRINT, values=(x / norm, y / norm, 0.0, 0.0))


class FakeTagPort:
    """``MOD-tag-service``'s three reads, over the **real** ``tag`` rows this card creates.

    ``tag_config_version`` still has no writer in the 19 cards, so the version object is
    assembled here from the live ``tag`` table rather than read from a table. That is the one
    remaining half of ``CR-TC-REPORT-01``; what it is *not* is a stub of the tag rows
    themselves, which now exist.
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.sequence = 0
        self.frozen: dict[str, TagConfigVersion] = {}
        self.refresh()

    def refresh(self) -> TagConfigVersion:
        with self.engine.connect() as connection:
            rows = connection.execute(
                text(
                    'SELECT id, "text", similarity_threshold FROM tag'
                    " WHERE owner_id = :owner AND state = 'active' ORDER BY id"
                ),
                {"owner": OWNER_ID},
            ).all()
        self.sequence += 1
        self.current = TagConfigVersion(
            id=f"01JTCV{self.sequence:020d}",
            sequence=self.sequence,
            content_hash="sha256:" + f"{self.sequence:064d}",
            payload={
                "tags": [
                    {"id": row[0], "text": row[1], "similarity_threshold": row[2]} for row in rows
                ],
                "tag_aliases": [],
                "tag_exclusions": [],
            },
            created_at="2026-09-01T02:00:00.000Z",
        )
        return self.current

    def get_active_config_version(self, owner_id: str) -> TagConfigVersion:
        return self.current

    def config_version(self, *, owner_id: str, tag_config_version_id: str) -> TagConfigVersion:
        return self.current

    def freeze_config_version(
        self, *, owner_id: str, report_build_id: str, expected_tag_config_version_id: str
    ) -> TagConfigVersion:
        if report_build_id in self.frozen:
            return self.frozen[report_build_id]
        self.frozen[report_build_id] = self.current
        return self.current


def context_for(engine: Engine, tag_port: FakeTagPort) -> PublishContext:
    return PublishContext(
        engine=engine,
        tag_port=tag_port,
        embedding_port=EmbeddingService(
            engine,
            encoder=DeterministicHashEncoder(
                MODEL_NAME, MODEL_VERSION, DIMENSION, Normalization.L2
            ),
        ),
    )


# --------------------------------------------------------------------------------------
# The events of fixtures j and k, through the service layer
# --------------------------------------------------------------------------------------


def create_tag(engine: Engine, *, tag_id: str, text_value: str, at: str) -> Entitlement:
    """``tag.create``'s state effect: the tag row and its backfill activation, one commit.

    ``ports.yaml`` describes ``tag.create`` as opening *"một backfill activation N ngày dùng
    đúng một lần"*; the decision half is :func:`open_activation`, which is the service layer
    under test. ``days`` is read from ``settings`` and never passed as a literal.
    """
    with engine.begin() as connection:
        connection.execute(
            text(
                'INSERT INTO tag (id, owner_id, "text", similarity_threshold, state,'
                " created_at, updated_at, removed_at)"
                " VALUES (:id, :owner, :text, NULL, 'active', :at, :at, NULL)"
            ),
            {"id": tag_id, "owner": OWNER_ID, "text": text_value, "at": at},
        )
        days = backfill_days(TableSettings(owner_id=OWNER_ID, connection=connection))
        return open_activation(
            connection,
            owner_id=OWNER_ID,
            tag_id=tag_id,
            tag_text=text_value,
            days=days,
            new_id=new_ulid(),
        )


def delete_tag(engine: Engine, *, tag_id: str, at: str) -> None:
    """``tag.delete``: the row moves to ``removed``; the ledger row is untouched."""
    with engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE tag SET state = 'removed', removed_at = :at, updated_at = :at"
                " WHERE owner_id = :owner AND id = :id"
            ),
            {"owner": OWNER_ID, "id": tag_id, "at": at},
        )


def seed_work(engine: Engine, work_id: str, *, sequence: int, discovered_at: str) -> str:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO work (id, owner_id, canonical_doi, canonical_arxiv_id, title,"
                " paper_url, code_url, current_work_version_id, metadata_state,"
                " identity_state, merged_into_work_id, first_discovered_at, ingest_sequence,"
                " content_state, created_at)"
                " VALUES (:id, :owner, NULL, NULL, 'w', NULL, NULL, NULL, 'partial',"
                " 'active', NULL, :at, :seq, 'present', :at)"
            ),
            {"id": work_id, "owner": OWNER_ID, "at": discovered_at, "seq": sequence},
        )
    return f"work:{work_id}"


def seed_analysis_and_label(engine: Engine, work_id: str, *, label: str, at: str) -> str:
    analysis_id = new_ulid()
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO analysis (id, owner_id, analysis_generation_id, target_kind,"
                " target_work_id, target_post_id, task_type, source_fingerprint,"
                " prompt_version, schema_version, generation_number, status, payload,"
                " payload_hash, evidence_level, provider_name, model_name, usage_tokens_in,"
                " usage_tokens_out, analyzed_at, accepted_from_attempt_id, moved_by_merge_id)"
                " VALUES (:id, :owner, :gen, 'work', :work, NULL, 'summary', 'fp', '1.0.0',"
                " '0.1.0', 1, 'valid', '{}', :hash, 'abstract', 'anthropic', 'm', NULL, NULL,"
                " :at, 'attempt', NULL)"
            ),
            {
                "id": analysis_id,
                "owner": OWNER_ID,
                "gen": new_ulid(),
                "work": work_id,
                "hash": "sha256:" + "0" * 64,
                "at": at,
            },
        )
        connection.execute(
            text(
                "INSERT INTO work_label (id, owner_id, target_kind, target_work_id,"
                " target_post_id, label_text, analysis_id, embedding_generation_id, vector,"
                " created_at) VALUES (:id, :owner, 'work', :work, NULL, :label, :analysis,"
                " :generation, :vector, :at)"
            ),
            {
                "id": new_ulid(),
                "owner": OWNER_ID,
                "work": work_id,
                "label": label,
                "analysis": analysis_id,
                "generation": GENERATION_ID,
                "vector": unit(1.0, 0.0).to_blob(),
                "at": at,
            },
        )
    return analysis_id


def seed_tag_vector(engine: Engine, tag_id: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO tag_vector (id, owner_id, subject_type, subject_id,"
                " embedding_generation_id, vector)"
                " VALUES (:id, :owner, 'tag', :subject, :generation, :vector)"
            ),
            {
                "id": new_ulid(),
                "owner": OWNER_ID,
                "subject": tag_id,
                "generation": GENERATION_ID,
                "vector": unit(1.0, 0.0).to_blob(),
            },
        )


def build_with_extension(
    engine: Engine, tag_port: FakeTagPort, *, apply_extension: bool = True
) -> tuple[BuildSnapshot, dict[str, Any]]:
    """``report.build`` with the §6.3 widening applied by the **real** builder.

    Before ``PKT-TC-REPORT-FIX1`` this helper had to compose the two halves by hand —
    ``build_report`` for the in-window snapshot, then this card's :func:`plan_extension` and
    :func:`entitlements_to_consume`, then a ``dataclasses.replace`` to graft the widened items
    onto the snapshot. That composition proved the ledger semantics but not the wiring, which
    was the whole of ``CR-TC-BACKFILL-05``: no deployment could reach the widening at all.

    ``build_report`` now takes ``backfill_port``, and :class:`ServiceBackfill` delegates to
    this card's two functions. So the path under test is the production path: the builder asks
    how far each entitled tag may reach, unions the widened rows into its own candidate set,
    scores them through its own selection, counts what the widening produced, and asks this
    card which ledger ids §6.4 conditions 2 and 3 allow. Condition 1 stays where it belongs —
    ``publisher._consume_backfill``, inside ``TXN-report-publish``.

    ``apply_extension=False`` passes no port, so the builder's default :class:`NoBackfill`
    applies. That is not a test-only shortcut: it is the behaviour every caller that has not
    opted in still gets, and period 1 below uses it deliberately.
    """
    snapshot = build_report(
        engine,
        owner_id=OWNER_ID,
        report_build_id=str(uuid.uuid4()),
        tag_port=tag_port,
        embedding_port=context_for(engine, tag_port).embedding_port,
        settings=SelectionSettings(),
        backfill_port=ServiceBackfill() if apply_extension else NoBackfill(),
    )
    return snapshot, {
        "applied": snapshot.backfill_ledger_ids_applied,
        "backfill_applied_tag_ids": snapshot.coverage_note.get("backfill_applied_tag_ids", []),
        "widened_items": [
            item.candidate.target_key
            for item in snapshot.items
            if item.candidate.selected_via_backfill
        ],
    }


def plan_for(engine: Engine, tag_port: FakeTagPort, snapshot: BuildSnapshot) -> Any:
    """This card's ``plan_extension`` alone, for the assertions that are about the *range*.

    Kept separate from :func:`build_with_extension` now that the builder owns the composition:
    the tests that ask "did the range widen at all" are about §6.3 and should not have to go
    through selection to find out.
    """
    with engine.connect() as connection:
        return plan_extension(
            connection,
            owner_id=OWNER_ID,
            coverage_from=parse_timestamp_utc_ms(snapshot.window_plan.window_from),
            coverage_to=parse_timestamp_utc_ms(snapshot.window_plan.window_to),
            tags=[str(tag["id"]) for tag in tag_port.current.payload["tags"]],
            settings=TableSettings(owner_id=OWNER_ID, connection=connection),
        )


def publish(engine: Engine, tag_port: FakeTagPort, snapshot: BuildSnapshot) -> Any:
    record_build(context_for(engine, tag_port), snapshot, caller_module=MOD_JOB)
    return publish_report(context_for(engine, tag_port), snapshot)


def count(engine: Engine, sql: str, **params: Any) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql), params).scalar() or 0)


def ledger_rows(engine: Engine) -> list[Entitlement]:
    with engine.connect() as connection:
        identity = subscription_identity_hash(OWNER_ID, TAG_TEXT)
        return backfill.rows_for_identity(connection, owner_id=OWNER_ID, identity_hash=identity)


# --------------------------------------------------------------------------------------
# §6.2 -- the identity function
# --------------------------------------------------------------------------------------


def test_normalize_tag_text_is_the_four_steps_the_contract_names() -> None:
    """NFC → trim → casefold → collapse (``time-and-tags.md`` §6.2)."""
    assert normalize_tag_text("  Graph   Neural\tNetworks  ") == TAG_TEXT
    assert normalize_tag_text("GRAPH NEURAL NETWORKS") == TAG_TEXT
    # NFC: "é" written as e + combining acute folds to the composed form before hashing.
    assert normalize_tag_text("café") == normalize_tag_text("café")
    # Idempotent -- a normalized string normalizes to itself.
    assert normalize_tag_text(normalize_tag_text(" A  B ")) == normalize_tag_text(" A  B ")


def test_the_identity_survives_remove_and_readd_and_the_tag_id_does_not() -> None:
    """The single fact fixture ``j`` is built on."""
    assert subscription_identity_hash(OWNER_ID, TAG_TEXT) == subscription_identity_hash(
        OWNER_ID, "  Graph Neural  Networks "
    )
    assert TAG_V1 != TAG_V2


def test_changing_the_words_is_a_different_subscription() -> None:
    """§6.2's deliberate consequence: the system does not guess two strings are one interest."""
    assert subscription_identity_hash(OWNER_ID, TAG_TEXT) != subscription_identity_hash(
        OWNER_ID, "graph neural nets"
    )


def test_the_identity_is_scoped_to_the_owner() -> None:
    other_owner = "01JW0WNER99999999999999999"
    assert subscription_identity_hash(OWNER_ID, TAG_TEXT) != subscription_identity_hash(
        other_owner, TAG_TEXT
    )


def test_the_hash_is_the_bare_64_hex_the_column_checks() -> None:
    """The shipped CHECK is ``length(subscription_identity_hash) = 64`` (0010), not 71."""
    value = subscription_identity_hash(OWNER_ID, TAG_TEXT)
    assert len(value) == 64
    assert value == value.lower()
    int(value, 16)


def test_the_fixture_hashes_are_shape_only_by_the_readme_rule() -> None:
    """``acceptance/fixtures/reporting/README.md`` §4, asserted instead of assumed.

    If a later change made the fixture literals recomputable, the tests below should start
    comparing against them; while they are not, comparing would fail for a reason that has
    nothing to do with the implementation. This test is the tripwire either way.
    """
    fixture = json.loads((FIXTURES / "j-backfill-add-remove-readd.json").read_text("utf-8"))
    literals = {
        event["produces"]["backfill_ledger"]["subscription_identity_hash"]
        for event in fixture["events"]
        if "produces" in event
    }
    assert len(literals) == 1, "fixture j uses one identity for both activations"
    literal = literals.pop()
    assert literal.startswith("sha256:")
    assert literal.removeprefix("sha256:") != subscription_identity_hash(OWNER_ID, TAG_TEXT)


# --------------------------------------------------------------------------------------
# SG-03 -- N comes from settings
# --------------------------------------------------------------------------------------


def test_n_is_read_from_settings(engine: Engine) -> None:
    fixture = json.loads((FIXTURES / "j-backfill-add-remove-readd.json").read_text("utf-8"))
    with engine.connect() as connection:
        assert (
            backfill_days(TableSettings(owner_id=OWNER_ID, connection=connection))
            == fixture["given"]["settings"]["reporting.backfill_days"]
        )


def test_an_unconfigured_n_is_a_validation_error_not_a_default(engine: Engine) -> None:
    """``SG-03``: read from settings, do not hard-code.

    A code-side default is the failure mode this asserts against: it would make an
    unconfigured deployment silently reach seven days back, and would put the number in the
    source where changing it is a code change.
    """
    with engine.begin() as connection:
        connection.execute(
            text('DELETE FROM settings WHERE owner_id = :owner AND "key" = :key'),
            {"owner": OWNER_ID, "key": "reporting.backfill_days"},
        )
    with engine.connect() as connection, pytest.raises(BackfillError) as raised:
        backfill_days(TableSettings(owner_id=OWNER_ID, connection=connection))
    assert raised.value.code.value == "VALIDATION_ERROR"
    assert raised.value.details_safe["violation_kind"] == "required_missing"


def test_no_module_in_this_card_hard_codes_the_working_value(engine: Engine) -> None:
    """The number 7 does not appear as a backfill constant in this card's source.

    Asserted structurally because ``SG-03``'s wording is about the *source*, not about one
    call path: a default hidden in a signature would pass every behavioural test above.
    """
    import ast

    source = (REPO_ROOT / "server" / "app" / "report" / "backfill.py").read_text("utf-8")
    tree = ast.parse(source)

    def _is_seven(node: ast.expr | None) -> bool:
        return (
            isinstance(node, ast.Constant)
            and isinstance(node.value, int)
            and not isinstance(node.value, bool)
            and node.value == 7
        )

    defaults: list[ast.expr] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            defaults.extend(node.args.defaults)
            defaults.extend(d for d in node.args.kw_defaults if d is not None)
    assert not any(_is_seven(d) for d in defaults), "N must not be a parameter default"

    assigned = [
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign | ast.AnnAssign) and node.value is not None
    ]
    assert not any(_is_seven(v) for v in assigned), "N must not be a module constant"
    # The §6.1 ceiling, by contrast, *is* a contract constant with a documented fallback: a
    # missing guard must not read as "no guard". Asserted so the two are not confused.
    assert backfill.BACKFILL_MAX_EXTENSION_DAYS == 30


# --------------------------------------------------------------------------------------
# Fixture j -- add, publish, remove, re-add
# --------------------------------------------------------------------------------------


@pytest.fixture
def tag_port(engine: Engine) -> FakeTagPort:
    return FakeTagPort(engine)


def _first_period(engine: Engine, tag_port: FakeTagPort) -> None:
    """Period 1, before any tag exists: nothing matches, so the period is empty.

    Its purpose is to leave a coverage cursor. Without a predecessor the first window starts
    at ``ingest_sequence`` 0 and the older work is *inside* it, which would make "the
    extension reached something the window did not" untestable — the widening would have
    nothing to add.
    """
    snapshot, _ = build_with_extension(engine, tag_port, apply_extension=False)
    publish(engine, tag_port, snapshot)


def test_fixture_j_the_first_activation_is_granted(engine: Engine, tag_port: FakeTagPort) -> None:
    """Event 1: ``entitlement = 'granted'``, ``entitlement_reason = 'first_activation'``."""
    entitlement = create_tag(
        engine, tag_id=TAG_V1, text_value=TAG_TEXT, at="2026-09-08T14:00:00.000Z"
    )
    assert entitlement.entitlement == ENTITLEMENT_GRANTED
    assert entitlement.entitlement_reason == REASON_FIRST_ACTIVATION
    assert entitlement.activation_sequence == 1
    assert entitlement.consumed_in_report_id is None
    fixture = json.loads((FIXTURES / "j-backfill-add-remove-readd.json").read_text("utf-8"))
    produced = fixture["events"][0]["produces"]["backfill_ledger"]
    assert entitlement.backfill_days == produced["backfill_days"]
    assert entitlement.entitlement == produced["entitlement"]
    assert entitlement.entitlement_reason == produced["entitlement_reason"]


def test_fixture_j_the_readd_is_a_new_activation_but_a_denied_entitlement(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """Events 1-5 in order, with the ledger asserted after each one.

    The re-add is *an activation* (``activation_sequence`` 2, as the fixture numbers it) and
    *not an entitlement* — the two are different questions and conflating them is what
    "exactly once" loses.
    """
    seed_work(engine, WORK_OLD, sequence=1, discovered_at="2026-09-03T02:00:00.000Z")
    seed_analysis_and_label(engine, WORK_OLD, label=TAG_TEXT, at="2026-09-03T03:00:00.000Z")
    _first_period(engine, tag_port)

    create_tag(engine, tag_id=TAG_V1, text_value=TAG_TEXT, at="2026-09-08T14:00:00.000Z")
    seed_tag_vector(engine, TAG_V1)
    tag_port.refresh()

    seed_work(engine, WORK_NEW, sequence=2, discovered_at="2026-09-09T02:00:00.000Z")
    seed_analysis_and_label(engine, WORK_NEW, label=TAG_TEXT, at="2026-09-09T03:00:00.000Z")

    snapshot, detail = build_with_extension(engine, tag_port)
    # The real builder found the earlier work through the widening, labelled it, and asked
    # this card which entitlement §6.4 lets the publish spend. None of these three come from
    # the test any more (PKT-TC-REPORT-FIX1 / CR-TC-BACKFILL-05).
    assert detail["widened_items"] == [f"work:{WORK_OLD}"]
    assert detail["applied"], "the widening should have found the earlier work"
    assert detail["backfill_applied_tag_ids"] == [TAG_V1]
    # Not consumed yet: `build` is not the commit point (§6.4 condition 1).
    with engine.connect() as connection:
        assert backfill.consumed_count(connection, owner_id=OWNER_ID) == 0

    result = publish(engine, tag_port, snapshot)
    assert result.published

    rows = ledger_rows(engine)
    assert len(rows) == 1
    assert rows[0].entitlement == ENTITLEMENT_CONSUMED
    assert rows[0].consumed_in_report_id == result.report_id
    assert rows[0].consumed_at is not None

    delete_tag(engine, tag_id=TAG_V1, at="2026-09-15T02:00:00.000Z")
    assert len(ledger_rows(engine)) == 1, "tag.delete must not delete the ledger row"

    second = create_tag(engine, tag_id=TAG_V2, text_value=TAG_TEXT, at="2026-09-20T02:00:00.000Z")
    assert second.activation_sequence == 2
    assert second.entitlement == ENTITLEMENT_DENIED
    assert second.entitlement_reason == REASON_ALREADY_CONSUMED

    fixture = json.loads((FIXTURES / "j-backfill-add-remove-readd.json").read_text("utf-8"))
    expected = fixture["expected"]["rows"]["backfill_ledger"][1]
    assert second.entitlement == expected["entitlement"]
    assert second.entitlement_reason == expected["entitlement_reason"]

    with engine.connect() as connection:
        identity = subscription_identity_hash(OWNER_ID, TAG_TEXT)
        assert backfill.consumed_count(connection, owner_id=OWNER_ID, identity_hash=identity) == 1
        assert (
            count(
                engine,
                "SELECT COUNT(*) FROM backfill_ledger WHERE owner_id = :o"
                " AND subscription_identity_hash = :h",
                o=OWNER_ID,
                h=identity,
            )
            == 2
        )


def test_fixture_j_the_period_after_the_readd_does_not_widen(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """Event 5: ``candidate_range`` = ``[coverage_from, coverage_to)`` — no widening."""
    test_fixture_j_the_readd_is_a_new_activation_but_a_denied_entitlement(engine, tag_port)
    seed_tag_vector(engine, TAG_V2)
    tag_port.refresh()
    snapshot, detail = build_with_extension(engine, tag_port)
    assert plan_for(engine, tag_port, snapshot).extended == ()
    assert detail["widened_items"] == []
    assert snapshot.backfill_ledger_ids_applied == ()
    with engine.connect() as connection:
        assert backfill.consumed_count(connection, owner_id=OWNER_ID) == 1


def test_o_6_1_no_identity_ever_has_two_consumed_rows(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """O-6.1 as the contract states it: group by identity, and no group exceeds one."""
    test_fixture_j_the_period_after_the_readd_does_not_widen(engine, tag_port)
    with engine.connect() as connection:
        assert backfill.identities_with_multiple_consumptions(connection, owner_id=OWNER_ID) == []


def test_the_database_refuses_a_second_consumption_even_if_the_code_asked(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """``ux_backfill_subscription_consumed`` is the arbiter, not this module's branch.

    The partial UNIQUE is what makes "exactly once" survive a bug in the granting logic, a
    concurrent publisher and a restart. Asserted by trying the write the branch is supposed to
    prevent and watching the database refuse it.
    """
    test_fixture_j_the_readd_is_a_new_activation_but_a_denied_entitlement(engine, tag_port)
    rows = ledger_rows(engine)
    consumed = next(row for row in rows if row.consumed_in_report_id is not None)
    denied = next(row for row in rows if row.consumed_in_report_id is None)
    with (
        pytest.raises(Exception) as raised,  # noqa: PT011 - the driver's IntegrityError
        engine.begin() as connection,
    ):
        connection.execute(
            text(
                "UPDATE backfill_ledger SET entitlement = 'consumed',"
                " consumed_in_report_id = :report, consumed_at = :at WHERE id = :id"
            ),
            {
                "report": consumed.consumed_in_report_id,
                "at": "2026-09-21T13:00:00.000Z",
                "id": denied.id,
            },
        )
    # SQLite names the *columns* of the violated index rather than the index. Both names
    # together are the partial unique key `ux_backfill_subscription_consumed` and no other
    # index on this table covers that pair, so the message identifies it unambiguously.
    message = str(raised.value)
    assert "UNIQUE constraint failed" in message
    assert "backfill_ledger.owner_id" in message
    assert "backfill_ledger.subscription_identity_hash" in message


def test_fixture_j_forbidden_effect_the_coverage_window_is_not_dragged_backwards(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """Fixture ``j``'s third forbidden effect, and §6.3's whole point.

    Backfill widens the *candidate query*; ``coverage_window.window_from`` still equals the
    predecessor's ``window_to``. If the widening moved the window, the chain would overlap and
    ``I06`` would be violated one row earlier than anybody would look.
    """
    test_fixture_j_the_readd_is_a_new_activation_but_a_denied_entitlement(engine, tag_port)
    with engine.connect() as connection:
        windows = connection.execute(
            text(
                'SELECT "sequence", window_from, window_to, predecessor_window_id'
                ' FROM coverage_window WHERE owner_id = :owner ORDER BY "sequence"'
            ),
            {"owner": OWNER_ID},
        ).all()
    assert len(windows) >= 2
    for previous, following in zip(windows, windows[1:], strict=False):
        assert following[1] == previous[2], "window_from must equal the predecessor's window_to"


def test_fixture_j_forbidden_effect_keying_on_tag_id_would_have_regranted(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """The rejected alternative, made visible.

    ``ux_backfill_tag_activation`` keys on ``tag_id``, and the two activations have different
    ``tag_id`` values — so that index alone permits both to be consumed. The reason the second
    one is not is the *other* index, on the identity. Asserting the two keys disagree is what
    makes the choice between them a tested decision rather than a comment.
    """
    test_fixture_j_the_readd_is_a_new_activation_but_a_denied_entitlement(engine, tag_port)
    rows = ledger_rows(engine)
    assert {row.tag_id for row in rows} == {TAG_V1, TAG_V2}
    assert len({row.subscription_identity_hash for row in rows}) == 1


# --------------------------------------------------------------------------------------
# §6.3 -- the candidate range
# --------------------------------------------------------------------------------------


def _entitlement(consumed: bool = False, state: str = ENTITLEMENT_GRANTED) -> Entitlement:
    return Entitlement(
        id="01JBFDJ1000000000000000000",
        owner_id=OWNER_ID,
        tag_id=TAG_V1,
        activation_sequence=1,
        subscription_identity_hash=subscription_identity_hash(OWNER_ID, TAG_TEXT),
        entitlement=state,
        entitlement_reason=None,
        backfill_days=7,
        consumed_in_report_id="01JRPT0000000000000000000" if consumed else None,
        consumed_at="2026-09-09T13:00:05.000Z" if consumed else None,
    )


def test_candidate_range_widens_the_left_edge_only() -> None:
    start = parse_timestamp_utc_ms("2026-09-08T13:00:00.000Z")
    end = parse_timestamp_utc_ms("2026-09-09T13:00:00.000Z")
    widened = candidate_range(
        tag_id=TAG_V1,
        coverage_from=start,
        coverage_to=end,
        entitlement=_entitlement(),
        days=7,
    )
    assert widened.extended
    assert widened.end == end
    assert widened.start == parse_timestamp_utc_ms("2026-09-01T13:00:00.000Z")


def test_candidate_range_is_the_plain_window_without_a_spendable_entitlement() -> None:
    start = parse_timestamp_utc_ms("2026-09-08T13:00:00.000Z")
    end = parse_timestamp_utc_ms("2026-09-09T13:00:00.000Z")
    for entitlement in (None, _entitlement(consumed=True), _entitlement(state=ENTITLEMENT_DENIED)):
        plain = candidate_range(
            tag_id=TAG_V1, coverage_from=start, coverage_to=end, entitlement=entitlement, days=7
        )
        assert not plain.extended
        assert (plain.start, plain.end) == (start, end)
        assert plain.entitlement_id is None


def test_the_ceiling_clamps_n_rather_than_extending_it() -> None:
    """§6.1's ``backfill_max_extension``: a mistyped N must not reach back forever."""
    start = parse_timestamp_utc_ms("2026-09-08T13:00:00.000Z")
    end = parse_timestamp_utc_ms("2026-09-09T13:00:00.000Z")
    clamped = candidate_range(
        tag_id=TAG_V1,
        coverage_from=start,
        coverage_to=end,
        entitlement=_entitlement(),
        days=3650,
        max_extension_days=30,
    )
    assert clamped.start == parse_timestamp_utc_ms("2026-08-09T13:00:00.000Z")


# --------------------------------------------------------------------------------------
# §6.4 -- conditions 2 and 3, and fixture k's two variants
# --------------------------------------------------------------------------------------


def test_condition_2_an_unwidened_range_is_never_consumed() -> None:
    from server.app.report.backfill import ExtensionPlan

    plan = ExtensionPlan(
        ranges=(
            candidate_range(
                tag_id=TAG_V1,
                coverage_from=parse_timestamp_utc_ms("2026-09-08T13:00:00.000Z"),
                coverage_to=parse_timestamp_utc_ms("2026-09-09T13:00:00.000Z"),
                entitlement=None,
                days=7,
            ),
        )
    )
    assert entitlements_to_consume(plan, {TAG_V1: 5}) == ()


def test_condition_3_an_empty_extension_is_never_consumed() -> None:
    """Fixture ``k``'s ``variant_empty_extension``: re-reading an empty range costs no AI."""
    from server.app.report.backfill import ExtensionPlan

    plan = ExtensionPlan(
        ranges=(
            candidate_range(
                tag_id=TAG_V1,
                coverage_from=parse_timestamp_utc_ms("2026-09-08T13:00:00.000Z"),
                coverage_to=parse_timestamp_utc_ms("2026-09-09T13:00:00.000Z"),
                entitlement=_entitlement(),
                days=7,
            ),
        )
    )
    assert entitlements_to_consume(plan, {TAG_V1: 0}) == ()
    assert entitlements_to_consume(plan, {}) == ()
    assert entitlements_to_consume(plan, {TAG_V1: 1}) == ("01JBFDJ1000000000000000000",)


def test_fixture_k_a_builder_that_never_publishes_does_not_consume(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """Fixture ``k`` events 1-2: the build runs, the process dies, nothing is consumed.

    ``after_event_2`` is asserted exactly as the fixture states it: zero published reports,
    zero report items, zero new coverage windows, and
    ``backfill_ledger[consumed_in_report_id IS NOT NULL] = 0``.
    """
    seed_work(engine, WORK_OLD, sequence=1, discovered_at="2026-09-03T02:00:00.000Z")
    seed_analysis_and_label(engine, WORK_OLD, label=TAG_TEXT, at="2026-09-03T03:00:00.000Z")
    _first_period(engine, tag_port)
    create_tag(engine, tag_id=TAG_V1, text_value=TAG_TEXT, at="2026-09-10T14:00:00.000Z")
    seed_tag_vector(engine, TAG_V1)
    tag_port.refresh()
    seed_work(engine, WORK_NEW, sequence=2, discovered_at="2026-09-11T02:00:00.000Z")
    seed_analysis_and_label(engine, WORK_NEW, label=TAG_TEXT, at="2026-09-11T03:00:00.000Z")

    windows_before = count(
        engine, "SELECT COUNT(*) FROM coverage_window WHERE owner_id = :o", o=OWNER_ID
    )
    published_before = count(
        engine,
        "SELECT COUNT(*) FROM report WHERE owner_id = :o AND status = 'published'",
        o=OWNER_ID,
    )

    snapshot, detail = build_with_extension(engine, tag_port)
    assert detail["applied"], "the build did apply the widening"
    # The builder dies here. `publish_report` is never called.

    assert count(engine, "SELECT COUNT(*) FROM report_item WHERE owner_id = :o", o=OWNER_ID) == 0
    assert (
        count(engine, "SELECT COUNT(*) FROM coverage_window WHERE owner_id = :o", o=OWNER_ID)
        == windows_before
    )
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report WHERE owner_id = :o AND status = 'published'",
            o=OWNER_ID,
        )
        == published_before
    )
    with engine.connect() as connection:
        assert backfill.consumed_count(connection, owner_id=OWNER_ID) == 0
    assert ledger_rows(engine)[0].entitlement == ENTITLEMENT_GRANTED


def test_fixture_k_a_crash_inside_the_publish_transaction_rolls_the_consumption_back(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """E2 — the harder half: the process dies **inside** ``TXN-report-publish``.

    A write fault is injected so the transaction fails after it has begun. The oracle is the
    same one, and it is what "consumption is inside the transaction" actually buys: the
    entitlement is unspent because the whole transaction rolled back, not because some code
    path chose to skip the update.
    """
    seed_work(engine, WORK_OLD, sequence=1, discovered_at="2026-09-03T02:00:00.000Z")
    seed_analysis_and_label(engine, WORK_OLD, label=TAG_TEXT, at="2026-09-03T03:00:00.000Z")
    _first_period(engine, tag_port)
    create_tag(engine, tag_id=TAG_V1, text_value=TAG_TEXT, at="2026-09-10T14:00:00.000Z")
    seed_tag_vector(engine, TAG_V1)
    tag_port.refresh()
    seed_work(engine, WORK_NEW, sequence=2, discovered_at="2026-09-11T02:00:00.000Z")
    seed_analysis_and_label(engine, WORK_NEW, label=TAG_TEXT, at="2026-09-11T03:00:00.000Z")

    snapshot, _ = build_with_extension(engine, tag_port)
    record_build(context_for(engine, tag_port), snapshot, caller_module=MOD_JOB)

    injector = WriteFaultInjector(engine)
    with injector.disk_full(), pytest.raises(Exception):  # noqa: B017,PT011
        publish_report(context_for(engine, tag_port), snapshot)

    with engine.connect() as connection:
        assert backfill.consumed_count(connection, owner_id=OWNER_ID) == 0
    assert ledger_rows(engine)[0].entitlement == ENTITLEMENT_GRANTED
    # Period 1 was an *empty* period, which REQ-D57 records as an ``aborted`` report with
    # ``abort_reason = 'empty_period'`` plus a coverage window -- not as a published digest.
    # So nothing at all is published here, and the one report row that exists is that abort.
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report WHERE owner_id = :o AND status = 'published'",
            o=OWNER_ID,
        )
        == 0
    )
    assert (
        count(
            engine,
            "SELECT COUNT(*) FROM report WHERE owner_id = :o AND abort_reason = 'empty_period'",
            o=OWNER_ID,
        )
        == 1
    )


def test_fixture_k_the_retried_build_consumes_exactly_once(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """Fixture ``k`` events 3-4: the job is requeued, the rebuild commits, one consumption."""
    test_fixture_k_a_builder_that_never_publishes_does_not_consume(engine, tag_port)
    snapshot, detail = build_with_extension(engine, tag_port)
    result = publish(engine, tag_port, snapshot)
    assert result.published
    with engine.connect() as connection:
        assert backfill.consumed_count(connection, owner_id=OWNER_ID) == 1
        assert backfill.identities_with_multiple_consumptions(connection, owner_id=OWNER_ID) == []
    rows = ledger_rows(engine)
    assert rows[0].entitlement == ENTITLEMENT_CONSUMED
    assert rows[0].consumed_in_report_id == result.report_id


def test_the_widened_item_is_marked_selected_via_backfill(
    engine: Engine, tag_port: FakeTagPort
) -> None:
    """§6.3: a row reached by the widening carries the flag and the ledger id.

    Read back out of ``report_item.selection_reason``, the JSON column §5.3 assigns these
    keys to, so the assertion is about what was persisted rather than about the object that
    was passed in.
    """
    test_fixture_k_the_retried_build_consumes_exactly_once(engine, tag_port)
    with engine.connect() as connection:
        rows = connection.execute(
            text("SELECT target_key, selection_reason FROM report_item WHERE owner_id = :o"),
            {"o": OWNER_ID},
        ).all()
    reasons = {row[0]: json.loads(row[1]) for row in rows}
    widened = reasons[f"work:{WORK_OLD}"]
    assert widened["selected_via_backfill"] is True
    assert widened["backfill_ledger_id"] == ledger_rows(engine)[0].id
    assert reasons[f"work:{WORK_NEW}"]["selected_via_backfill"] is False


# --------------------------------------------------------------------------------------
# The migration graph
# --------------------------------------------------------------------------------------


def test_the_migration_graph_has_exactly_one_head() -> None:
    """Computed, never a literal: a hard-coded revision id stops noticing a new branch."""
    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert len(heads) == 1, heads


def test_the_ledger_tables_were_created_exactly_once(tmp_path: Path) -> None:
    """``F-A3R1-01``: one ``CREATE TABLE`` per ledger across the whole graph.

    0010 created both ledgers as custodian for this card and 0013 does not recreate either.
    The count is over the *migration sources*, so a second definition is caught even if the
    two happened to agree on disk — which is precisely the case ``F-A3R1-01`` was, where two
    definitions differed only by a CHECK and the resulting schema depended on traversal order.
    """
    versions = REPO_ROOT / "server" / "migrations" / "versions"
    for table in ("pending_item_ledger", "backfill_ledger", "rescan_ledger", "tag", "settings"):
        creates = sum(
            path.read_text("utf-8").count(f"CREATE TABLE {table} (")
            for path in versions.glob("*.py")
        )
        assert creates == 1, f"{table}: {creates} CREATE TABLE statements"

    db_path = tmp_path / "graph.db"
    _upgrade(db_path)
    connection = sqlite3.connect(db_path)
    try:
        indexes = sorted(
            name
            for (name,) in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
                " AND tbl_name='backfill_ledger' AND name NOT LIKE 'sqlite_%'"
            )
        )
        assert indexes == [
            "ux_backfill_subscription_consumed",
            "ux_backfill_tag_activation",
        ], indexes
        # CR-TC-BACKFILL-10: `backfill_ledger.tag_id` is declared "FK -> tag.id" in
        # entities.yaml and still ships without the clause. `tag` now exists, so the
        # constraint is addable -- and adding it fails a passing test in another card's write
        # set, which is why it was withdrawn rather than forced. Asserted so the open state is
        # visible and so the day somebody closes it, this line says where to look.
        foreign_keys = {
            row[2] for row in connection.execute("PRAGMA foreign_key_list(backfill_ledger)")
        }
        assert "tag" not in foreign_keys, "CR-TC-BACKFILL-10 has been closed; update this test"
        rescan_keys = {
            row[2] for row in connection.execute("PRAGMA foreign_key_list(rescan_ledger)")
        }
        assert "tag" in rescan_keys, "this card's own table does carry the declared FK"
    finally:
        connection.close()


def _unused(*_: Sequence[Any]) -> None:  # pragma: no cover - import anchor
    """Keeps ``Sequence`` referenced for the type checker without exporting a helper."""
