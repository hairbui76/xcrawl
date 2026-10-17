"""E1 — ``TC-tag-service``: the subscription layer against a real database and a wired app.

The oracles are the acceptance fixtures, read through ``tests/conftest.py`` (§3.2 of the root
README: no second data set):

* ``reporting/j-backfill-add-remove-readd`` — ``tag.create`` opens the D28 activation through
  the composition root; delete keeps the ledger row; re-adding the same text is a new tag id,
  activation 2, ``denied_already_consumed`` with the fixture's exact reason.
* ``reporting/a-tag-removed-before-publish`` — after a delete, the active config version is
  the one without the removed tag, and freezing it with that id succeeds.
* ``reporting/c-tag-changed-after-publish-before-send`` — a change after the freeze makes a new
  version; the frozen one is byte-identical when read back (I05).
* ``recovery/h-unauthenticated-owner-api`` / ``recovery/i-collector-token-calls-save`` —
  ``tag.delete`` without a session is 401, without CSRF ``CSRF_REJECTED``, ``tag.update`` with a
  collector token 401; nothing changes.
* ``ui/sc51-first-time-setup`` — preview with no tag returns the ``SCR-topics`` empty state.
  Its ``tag_config_version__total: 1`` after three creates is **not** what this module does;
  that disagreement is ``CR-TC-TAG-01`` and the fixture's count is recorded ``NOT_RUN``.

The encoder here is ``DeterministicHashEncoder``. It is not a model and nothing below reads a
similarity value as meaningful; it only proves vectors are written in the right generation.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text

from server.app.db import create_sqlite_engine
from server.app.embedding.generation import DeterministicHashEncoder
from server.app.embedding.service import EmbeddingService
from server.app.report import backfill
from server.app.report.builder import TagSet
from server.app.report.coverage import ReportError
from server.app.settings import Settings
from server.app.tags import service
from server.app.tags.service import TagContext, TagError
from server.app.wiring import (
    BackfillActivationAdapter,
    TagConfigVersionAdapter,
    upgrade_database,
    wire,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ADMIN = REPO_ROOT / "tools" / "rr_admin.py"
OWNER_ID = "01JW0WNER00000000000000000"
OWNER_PASSWORD = "tag-service-test-password"
COLLECTOR_TOKEN = "tag-service-collector-token-not-a-secret"
GENERATION_ID = "01JEMBGEN10000000000000000"
WIRE = {"X-Schema-Version": "0.3.0", "X-Request-Id": "01JREQ0000000000000000000A"}


# --------------------------------------------------------------------------- service level


def _seed(engine: Engine, *, backfill_days: int | None = 7) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at, password_hash, password_updated_at, failed_login_count, "
                "locked_until) VALUES (:id, 1, 'Owner', 'Asia/Ho_Chi_Minh', "
                "'2026-09-01T00:00:00.000Z', 'x', '2026-09-01T00:00:00.000Z', 0, NULL)"
            ),
            {"id": OWNER_ID},
        )
        if backfill_days is not None:
            connection.execute(
                text(
                    'INSERT INTO settings (id, owner_id, "key", value_json, updated_at) '
                    "VALUES ('01JSETBFD00000000000000000', :o, 'reporting.backfill_days', "
                    ":v, '2026-09-01T00:00:00.000Z')"
                ),
                {"o": OWNER_ID, "v": str(backfill_days)},
            )


def _active_generation(engine: Engine, encoder: DeterministicHashEncoder) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO embedding_generation (id, owner_id, model_name, model_version, "
                "dimension, normalization, state, expected_vector_count, built_vector_count, "
                "created_at, activated_at) VALUES (:id, :o, :m, :v, :d, 'l2', 'active', NULL, "
                "0, '2026-09-01T00:00:00.000Z', '2026-09-01T00:00:00.000Z')"
            ),
            {
                "id": GENERATION_ID,
                "o": OWNER_ID,
                "m": encoder.model_name,
                "v": encoder.model_version,
                "d": encoder.dimension,
            },
        )


@pytest.fixture()
def engine(tmp_path: Path) -> Iterator[Engine]:
    database = tmp_path / "radar.db"
    upgrade_database(database)
    engine = create_sqlite_engine(database)
    _seed(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture()
def encoder() -> DeterministicHashEncoder:
    return DeterministicHashEncoder(
        model_name="multilingual-e5-small", model_version="test-only", dimension=8
    )


@pytest.fixture()
def ctx(engine: Engine) -> TagContext:
    """No embedding service: the state of a deployment without RR_EMBEDDING_MODEL_PATH."""
    return TagContext(engine=engine, owner_id=OWNER_ID, activation=BackfillActivationAdapter())


def _count(engine: Engine, sql: str, **params: Any) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text(sql), params).scalar_one())


def _create(ctx: TagContext, value: str, key: str, **extra: Any) -> dict[str, Any]:
    return service.create_tag(ctx, idempotency_key=key, body={"text": value, **extra})


def test_fixture_j_create_delete_recreate_never_grants_backfill_twice(
    ctx: TagContext, engine: Engine, fixture_loader: Any
) -> None:
    """SC37: the second activation is denied, with the fixture's reason, on a new tag id."""
    fixture = fixture_loader("reporting/j-backfill-add-remove-readd")
    expected = {row["id"]: row for row in fixture.data["expected"]["rows"]["backfill_ledger"]}
    first_expected, second_expected = sorted(
        expected.values(), key=lambda row: row["activation_sequence"]
    )

    first = _create(ctx, "graph neural networks", "IDEMP-J-CREATE-0001")
    assert first["backfill"]["activation_sequence"] == 1
    assert first["backfill"]["entitlement"] == "granted"
    assert first["backfill"]["entitlement_reason"] == backfill.REASON_FIRST_ACTIVATION
    assert (
        first["backfill"]["backfill_days"]
        == fixture.data["given"]["settings"]["reporting.backfill_days"]
    )

    # Event 2 is report.publish consuming the entitlement. That write, and the `report` row its
    # FK points at, belong to the publish card (test_publish_cas.py); here it is simulated on a
    # raw autocommit connection with foreign keys off, so only the ledger column moves.
    raw = engine.raw_connection()
    try:
        driver = raw.driver_connection
        assert driver is not None
        driver.isolation_level = None
        driver.execute("PRAGMA foreign_keys = OFF")
        driver.execute(
            "UPDATE backfill_ledger SET entitlement = 'consumed', consumed_in_report_id = 'R1', "
            "consumed_at = '2026-09-09T13:00:05.000Z' WHERE id = ?",
            (first["backfill"]["backfill_ledger_id"],),
        )
        driver.execute("PRAGMA foreign_keys = ON")
    finally:
        raw.close()

    tag_v1 = first["tag"]["tag_id"]
    deleted = service.delete_tag(ctx, tag_id=tag_v1, idempotency_key="IDEMP-J-DELETE-001", body={})
    assert deleted["tag"]["state"] == "removed"
    assert _count(engine, "SELECT COUNT(*) FROM backfill_ledger") == 1, "delete keeps the ledger"

    second = _create(ctx, "graph neural networks", "IDEMP-J-CREATE-0002")
    assert second["tag"]["tag_id"] != tag_v1, "re-add is a new tag id"
    assert second["backfill"]["activation_sequence"] == second_expected["activation_sequence"]
    assert second["backfill"]["entitlement"] == second_expected["entitlement"]
    assert second["backfill"]["entitlement_reason"] == second_expected["entitlement_reason"]
    assert first_expected["activation_sequence"] == 1

    with engine.connect() as connection:
        hashes = {
            row[0]
            for row in connection.execute(
                text("SELECT DISTINCT subscription_identity_hash FROM backfill_ledger")
            )
        }
    assert len(hashes) == 1, "both activations share one subscription identity"
    assert (
        _count(
            engine, "SELECT COUNT(*) FROM backfill_ledger WHERE consumed_in_report_id IS NOT NULL"
        )
        == 1
    )


def test_fixture_a_delete_then_freeze_the_version_the_build_read(
    ctx: TagContext, fixture_loader: Any
) -> None:
    """SC05: after the delete, the active version holds only 'protein folding', and freezing it
    with that id succeeds; freezing with the pre-delete id is TAG_VERSION_STALE."""
    fixture = fixture_loader("reporting/a-tag-removed-before-publish")
    texts = {row["text"]: row for row in fixture.data["given"]["rows"]["tag"]}
    gnn = _create(ctx, "graph neural networks", "IDEMP-A-CREATE-0001")
    pfd = _create(ctx, "protein folding", "IDEMP-A-CREATE-0002")
    assert set(texts) == {"graph neural networks", "protein folding"}
    before = pfd["tag_config_version"]["tag_config_version_id"]

    service.delete_tag(
        ctx, tag_id=gnn["tag"]["tag_id"], idempotency_key="IDEMP-A-DELETE-0001", body={}
    )
    port = TagConfigVersionAdapter(ctx)
    built = port.get_active_config_version(OWNER_ID)
    assert built.id != before
    assert [tag["text"] for tag in built.payload["tags"]] == ["protein folding"]
    # The payload is exactly what the report builder parses.
    assert [tag.text for tag in TagSet.from_payload(built.payload).tags] == ["protein folding"]

    frozen = port.freeze_config_version(
        owner_id=OWNER_ID, report_build_id="BUILD-A", expected_tag_config_version_id=built.id
    )
    assert frozen.id == built.id
    with pytest.raises(ReportError) as stale:
        port.freeze_config_version(
            owner_id=OWNER_ID, report_build_id="BUILD-A2", expected_tag_config_version_id=before
        )
    assert stale.value.code is ErrorCode.TAG_VERSION_STALE
    assert stale.value.details_safe["current_tag_config_version_id"] == built.id


def test_fixture_c_change_after_freeze_leaves_the_frozen_version_byte_identical(
    ctx: TagContext, engine: Engine, fixture_loader: Any
) -> None:
    """SC19 / I05: a delete after the freeze is a new version; the frozen one reads back the
    same id and the same content_hash, and a repeat freeze of that build is idempotent."""
    fixture = fixture_loader("reporting/c-tag-changed-after-publish-before-send")
    assert "SC19" in fixture.data["scenario_refs"]
    one = _create(ctx, "graph neural networks", "IDEMP-C-CREATE-0001")
    _create(ctx, "protein folding", "IDEMP-C-CREATE-0002")
    port = TagConfigVersionAdapter(ctx)
    active = port.get_active_config_version(OWNER_ID)
    frozen = port.freeze_config_version(
        owner_id=OWNER_ID, report_build_id="BUILD-C", expected_tag_config_version_id=active.id
    )

    service.delete_tag(
        ctx, tag_id=one["tag"]["tag_id"], idempotency_key="IDEMP-C-DELETE-0001", body={}
    )
    assert port.get_active_config_version(OWNER_ID).id != frozen.id
    again = port.config_version(owner_id=OWNER_ID, tag_config_version_id=frozen.id)
    assert (again.id, again.content_hash, again.payload) == (
        frozen.id,
        frozen.content_hash,
        frozen.payload,
    )
    repeat = port.freeze_config_version(
        owner_id=OWNER_ID, report_build_id="BUILD-C", expected_tag_config_version_id=active.id
    )
    assert repeat.id == frozen.id, "freeze is idempotent per report_build_id"


def test_an_unchanged_set_reuses_its_version(ctx: TagContext, engine: Engine) -> None:
    """``ux_tag_config_version_owner_hash``: a mutation that leaves the set as it was mints no
    new sequence — a threshold set to the value it already had is the smallest such case."""
    created = _create(ctx, "protein folding", "IDEMP-R-CREATE-0001")
    tag_id = created["tag"]["tag_id"]
    same = service.update_tag(
        ctx,
        tag_id=tag_id,
        idempotency_key="IDEMP-R-UPDATE-0001",
        body={"similarity_threshold": None},
    )
    assert (
        same["tag_config_version"]["tag_config_version_id"]
        == created["tag_config_version"]["tag_config_version_id"]
    )
    assert _count(engine, "SELECT COUNT(*) FROM tag_config_version") == 1


def test_aliases_and_exclusions_round_trip_and_readding_reactivates(ctx: TagContext) -> None:
    created = _create(
        ctx,
        "graph neural networks",
        "IDEMP-X-CREATE-0001",
        aliases=["GNN"],
        exclusions=["chemistry"],
    )
    tag_id = created["tag"]["tag_id"]
    alias_id = created["tag"]["aliases"][0]["alias_id"]
    payload = service.get_active_config_version(ctx).payload
    assert [row["text"] for row in payload["tag_aliases"]] == ["GNN"]
    assert [row["tag_id"] for row in payload["tag_exclusions"]] == [tag_id]

    service.update_tag(
        ctx, tag_id=tag_id, idempotency_key="IDEMP-X-UPDATE-0001", body={"aliases": []}
    )
    assert service.get_active_config_version(ctx).payload["tag_aliases"] == []
    back = service.update_tag(
        ctx, tag_id=tag_id, idempotency_key="IDEMP-X-UPDATE-0002", body={"aliases": ["gnn"]}
    )
    assert back["tag"]["aliases"] == [
        {"alias_id": alias_id, "text": "GNN"}
    ], "same normalized text re-activates the same row (ux_tag_alias_owner_tag_text)"


def test_text_is_not_editable_and_duplicates_are_refused(ctx: TagContext) -> None:
    created = _create(ctx, "Protein  Folding", "IDEMP-V-CREATE-0001")
    with pytest.raises(TagError) as duplicate:
        _create(ctx, "protein folding", "IDEMP-V-CREATE-0002")
    assert duplicate.value.code is ErrorCode.VALIDATION_ERROR
    assert duplicate.value.details_safe["violation_kind"] == "duplicate_active_tag"
    with pytest.raises(TagError) as edit:
        service.update_tag(
            ctx,
            tag_id=created["tag"]["tag_id"],
            idempotency_key="IDEMP-V-UPDATE-0001",
            body={"text": "protein design"},
        )
    assert edit.value.details_safe["violation_kind"] == "unknown_field"


def test_idempotency_key_replays_and_refuses_a_different_payload(
    ctx: TagContext, engine: Engine
) -> None:
    first = _create(ctx, "protein folding", "IDEMP-I-CREATE-0001")
    assert _create(ctx, "protein folding", "IDEMP-I-CREATE-0001") == first
    assert _count(engine, "SELECT COUNT(*) FROM tag") == 1
    with pytest.raises(TagError) as conflict:
        _create(ctx, "graph neural networks", "IDEMP-I-CREATE-0001")
    assert conflict.value.code is ErrorCode.IDEMPOTENCY_CONFLICT


def test_delete_is_idempotent_and_deletes_nothing_else(ctx: TagContext, engine: Engine) -> None:
    created = _create(ctx, "protein folding", "IDEMP-D-CREATE-0001")
    tag_id = created["tag"]["tag_id"]
    service.delete_tag(ctx, tag_id=tag_id, idempotency_key="IDEMP-D-DELETE-0001", body={})
    again = service.delete_tag(ctx, tag_id=tag_id, idempotency_key="IDEMP-D-DELETE-0002", body={})
    assert again["already_removed"] is True
    assert _count(engine, "SELECT COUNT(*) FROM tag") == 1, "the row stays (REQ-D28 history)"
    with pytest.raises(TagError) as missing:
        service.delete_tag(
            ctx, tag_id="01JNOSUCHTAG00000000000000", idempotency_key="IDEMP-D-0003", body={}
        )
    assert missing.value.code is ErrorCode.NOT_FOUND


def test_no_backfill_setting_refuses_create_and_writes_nothing(tmp_path: Path) -> None:
    """N is never a code-side default (backfill card SG-03); the refusal names the key."""
    database = tmp_path / "bare.db"
    upgrade_database(database)
    bare = create_sqlite_engine(database)
    try:
        _seed(bare, backfill_days=None)
        context = TagContext(engine=bare, owner_id=OWNER_ID, activation=BackfillActivationAdapter())
        with pytest.raises(TagError) as refused:
            _create(context, "protein folding", "IDEMP-N-CREATE-0001")
        assert refused.value.code is ErrorCode.VALIDATION_ERROR
        assert refused.value.details_safe["field_path"] == backfill.SETTING_BACKFILL_DAYS
        assert _count(bare, "SELECT COUNT(*) FROM tag") == 0
        assert _count(bare, "SELECT COUNT(*) FROM tag_config_version") == 0
    finally:
        bare.dispose()


def test_a_refused_create_leaves_no_orphan_vector(
    tmp_path: Path, encoder: DeterministicHashEncoder
) -> None:
    """Vectors are generated before the rows, so every refusal the rows could meet must be
    checked first: an orphan vector would inflate ``built_vector_count``, which is what a
    generation's activation guard counts."""
    database = tmp_path / "orphan.db"
    upgrade_database(database)
    bare = create_sqlite_engine(database)
    try:
        _seed(bare, backfill_days=None)
        _active_generation(bare, encoder)
        context = TagContext(
            engine=bare,
            owner_id=OWNER_ID,
            embedding=EmbeddingService(bare, encoder=encoder),
            encoder=encoder,
            activation=BackfillActivationAdapter(),
        )
        with pytest.raises(TagError):
            _create(context, "protein folding", "IDEMP-O-CREATE-0001", aliases=["folding"])
        assert _count(bare, "SELECT COUNT(*) FROM tag_vector") == 0
        assert _count(bare, "SELECT built_vector_count FROM embedding_generation") == 0
    finally:
        bare.dispose()


def test_settings_service_key_is_read_when_the_contract_key_is_absent(tmp_path: Path) -> None:
    """CR-TC-TAG-08: settings.update_config writes `backfill_days`; it is honoured second."""
    database = tmp_path / "svc.db"
    upgrade_database(database)
    other = create_sqlite_engine(database)
    try:
        _seed(other, backfill_days=None)
        with other.begin() as connection:
            connection.execute(
                text(
                    'INSERT INTO settings (id, owner_id, "key", value_json, updated_at) '
                    "VALUES ('01JSETBFD20000000000000000', :o, 'backfill_days', '5', "
                    "'2026-09-01T00:00:00.000Z')"
                ),
                {"o": OWNER_ID},
            )
        context = TagContext(
            engine=other, owner_id=OWNER_ID, activation=BackfillActivationAdapter()
        )
        assert (
            _create(context, "protein folding", "IDEMP-S-CREATE-0001")["backfill"]["backfill_days"]
            == 5
        )
    finally:
        other.dispose()


def test_vectors_are_pending_without_a_model_and_generated_with_one(
    engine: Engine, encoder: DeterministicHashEncoder
) -> None:
    """No model ⇒ ``pending``, never a substitute. With an active generation ⇒ one vector per
    new subject, in that generation (I12)."""
    bare = TagContext(engine=engine, owner_id=OWNER_ID, activation=BackfillActivationAdapter())
    assert _create(bare, "protein folding", "IDEMP-E-CREATE-0001")["vectors"] == {
        "state": "pending",
        "reason": "no_local_embedding_model",
    }

    embedding = EmbeddingService(engine, encoder=encoder)
    with_model = TagContext(
        engine=engine,
        owner_id=OWNER_ID,
        embedding=embedding,
        encoder=encoder,
        activation=BackfillActivationAdapter(),
    )
    assert (
        _create(with_model, "graph neural networks", "IDEMP-E-CREATE-0002")["vectors"]["reason"]
        == "no_active_embedding_generation"
    )

    _active_generation(engine, encoder)
    made = _create(with_model, "machine learning", "IDEMP-E-CREATE-0003", aliases=["ML"])
    assert made["vectors"] == {"state": "generated", "embedding_generation_id": GENERATION_ID}
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT subject_type, embedding_generation_id FROM tag_vector "
                "ORDER BY subject_type"
            )
        ).all()
    assert [tuple(row) for row in rows] == [("tag", GENERATION_ID), ("tag_alias", GENERATION_ID)]

    preview = service.preview_matches(with_model, {"tag_id": made["tag"]["tag_id"]})
    assert preview["embedding_generation_id"] == GENERATION_ID
    assert preview["matched_labels"] == [], "no work_label exists yet"


def test_preview_with_no_tag_is_the_topics_empty_state(
    ctx: TagContext, fixture_loader: Any
) -> None:
    """SC51 (partial): never 'Không có nghiên cứu mới'."""
    fixture = fixture_loader("ui/sc51-first-time-setup")
    assert "SC51" in fixture.data["scenario_refs"]
    answer = service.preview_matches(ctx, {})
    assert answer["matched_labels"] == []
    assert answer["empty_state_vi"] == "Chưa có tag nào, báo cáo sẽ trống"
    assert "Không có nghiên cứu mới" not in str(answer)


def test_normalization_agrees_with_the_backfill_side() -> None:
    """Two copies of §6.2 (no tag → report import); they must not drift."""
    for value in ("Graph  Neural Networks ", "PROTEIN folding", "Họć máy", "x"):
        assert service.normalize_tag_text(value) == backfill.normalize_tag_text(value)


def test_the_tag_package_never_imports_the_report_package() -> None:
    """ENF-import-rule: the only edge between the two is report → tag (FE-23 guards the
    embedding package the same way, below)."""
    offenders: list[str] = []
    for package, forbidden in (
        (REPO_ROOT / "server" / "app" / "tags", "server.app.report"),
        (REPO_ROOT / "server" / "app" / "embedding", "server.app.tags"),
    ):
        for path in package.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = (
                    [node.module or ""]
                    if isinstance(node, ast.ImportFrom)
                    else [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else []
                )
                offenders += [
                    f"{path.name}: {name}" for name in names if name.startswith(forbidden)
                ]
    assert offenders == []


# --------------------------------------------------------------------------- HTTP, wired app


def _run_admin(args: list[str], tmp_path: Path, stdin: str | None = None) -> str:
    completed = subprocess.run(
        [sys.executable, str(ADMIN), *args],
        cwd=str(tmp_path),
        env={
            "PATH": "/usr/bin:/bin",
            "PYTHONDONTWRITEBYTECODE": "1",
            "RR_DATA_DIR": str(tmp_path),
            "RR_DATABASE_URL": str(tmp_path / "research-radar.db"),
        },
        input=stdin,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout


@pytest.fixture()
def client(tmp_path: Path) -> Iterator[TestClient]:
    """migrate → bootstrap → the real factory, wired, with N configured the way an Owner would."""
    from server.app.auth.service import hash_bearer_token
    from server.app.main import create_app

    _run_admin(["migrate"], tmp_path)
    owner_id = _run_admin(["bootstrap-owner"], tmp_path, stdin=OWNER_PASSWORD).strip()
    database = tmp_path / "research-radar.db"
    seeded = create_sqlite_engine(database)
    with seeded.begin() as connection:
        connection.execute(
            text(
                'INSERT INTO settings (id, owner_id, "key", value_json, updated_at) '
                "VALUES ('01JSETBFD00000000000000000', :o, 'reporting.backfill_days', '7', "
                "'2026-09-01T00:00:00.000Z')"
            ),
            {"o": owner_id},
        )
    seeded.dispose()
    settings = Settings(
        database_path=database,
        data_dir=tmp_path,
        timezone_iana="Asia/Ho_Chi_Minh",
        schedule_slots=("08:00", "20:00"),
        provider_config_path=REPO_ROOT / "contracts" / "ai" / "providers.yaml",
        telegram_webhook_secret=None,
        collector_token_sha256=hash_bearer_token(COLLECTOR_TOKEN),
        analysis_worker_token_sha256=None,
        backup_operator_token_sha256=None,
        collector_token=COLLECTOR_TOKEN,
    )
    app = create_app()
    runtime = wire(app, settings)
    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client
    runtime.engine.dispose()


def _login(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/v1/auth/login", headers=WIRE, json={"username": "Owner", "password": OWNER_PASSWORD}
    )
    assert response.status_code == 200, response.text
    return {**WIRE, "X-CSRF-Token": client.cookies["rr_csrf"]}


def _mutation(headers: dict[str, str], key: str) -> dict[str, str]:
    return {**headers, "Idempotency-Key": key}


def test_http_round_trip_and_the_report_routes_are_no_longer_500(client: TestClient) -> None:
    """CR-P0-07 closed: `/v1/reports` answers 200 on a wired app, and the six tag routes work."""
    headers = _login(client)
    assert client.get("/v1/reports", headers=headers).status_code == 200

    empty = client.get("/v1/tags", headers=headers)
    assert empty.status_code == 200
    assert empty.json()["tag_config_version"] is None

    created = client.post(
        "/v1/tags",
        headers=_mutation(headers, "IDEMP-HTTP-CREATE-01"),
        json={"text": "protein folding", "aliases": ["protein structure"]},
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["vectors"]["state"] == "pending"
    assert body["backfill"]["entitlement"] == "granted"
    tag_id = body["tag"]["tag_id"]

    patched = client.patch(
        f"/v1/tags/{tag_id}",
        headers=_mutation(headers, "IDEMP-HTTP-UPDATE-01"),
        json={"similarity_threshold": 0.75},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["tag"]["similarity_threshold"] == 0.75

    rescan = client.post(
        "/v1/tags/rescan-corpus",
        headers=_mutation(headers, "IDEMP-HTTP-RESCAN-01"),
        json={"tag_id": tag_id},
    )
    assert rescan.status_code == 202, rescan.text
    assert rescan.json()["state"] == "requested"

    preview = client.post("/v1/tags/preview-matches", headers=headers, json={"tag_id": tag_id})
    assert preview.status_code == 409, "no active generation: refused, never guessed"
    assert preview.json()["code"] == "EMBEDDING_GENERATION_MISMATCH"

    deleted = client.request(
        "DELETE",
        f"/v1/tags/{tag_id}",
        headers=_mutation(headers, "IDEMP-HTTP-DELETE-01"),
        json={"request_id": "IDEMP-HTTP-DELETE-01"},
    )
    assert deleted.status_code == 200, deleted.text
    listed = client.get("/v1/tags", headers=headers).json()
    assert listed["tags"] == []
    assert listed["empty_state_vi"] == "Chưa có tag nào, báo cáo sẽ trống"


def test_fixture_h_delete_without_session_or_csrf_changes_nothing(
    client: TestClient, fixture_loader: Any
) -> None:
    """SC40: 401 without a session; CSRF_REJECTED with a session but no CSRF token."""
    fixture = fixture_loader("recovery/h-unauthenticated-owner-api")
    operations = [event["operation"] for event in fixture.data["events"]]
    assert operations.count("tag.delete") == 2
    headers = _login(client)
    tag_id = client.post(
        "/v1/tags", headers=_mutation(headers, "IDEMP-H-CREATE-0001"), json={"text": "x"}
    ).json()["tag"]["tag_id"]
    before = client.get("/v1/tags", headers=headers).json()

    anonymous = TestClient(client.app, base_url="https://testserver")
    unauth = anonymous.request(
        "DELETE", f"/v1/tags/{tag_id}", headers=_mutation(WIRE, "IDEMP-H-DELETE-0001"), json={}
    )
    assert unauth.status_code == 401
    assert unauth.json()["code"] == "UNAUTHORIZED"

    no_csrf = {
        k: v for k, v in _mutation(headers, "IDEMP-H-DELETE-0002").items() if k != "X-CSRF-Token"
    }
    refused = client.request("DELETE", f"/v1/tags/{tag_id}", headers=no_csrf, json={})
    assert refused.status_code == 403
    assert refused.json()["code"] == "CSRF_REJECTED"
    assert client.get("/v1/tags", headers=headers).json() == before


def test_fixture_i_collector_token_cannot_update_a_tag(
    client: TestClient, fixture_loader: Any
) -> None:
    """SC41 / NC-02 / FE-11: a valid collector bearer is UNAUTHORIZED on tag.update (R5-01)."""
    fixture = fixture_loader("recovery/i-collector-token-calls-save")
    assert any(event["operation"] == "tag.update" for event in fixture.data["events"])
    headers = _login(client)
    tag_id = client.post(
        "/v1/tags", headers=_mutation(headers, "IDEMP-I-CREATE-0001"), json={"text": "y"}
    ).json()["tag"]["tag_id"]
    before = client.get("/v1/tags", headers=headers).json()

    collector = TestClient(client.app, base_url="https://testserver")
    denied = collector.patch(
        f"/v1/tags/{tag_id}",
        headers={
            **_mutation(WIRE, "IDEMP-I-UPDATE-0001"),
            "Authorization": f"Bearer {COLLECTOR_TOKEN}",
        },
        json={"similarity_threshold": 0.1},
    )
    assert denied.status_code == 401
    assert denied.json()["code"] == "UNAUTHORIZED"
    assert client.get("/v1/tags", headers=headers).json() == before


def test_wire_headers_are_required(client: TestClient) -> None:
    headers = _login(client)
    response = client.post(
        "/v1/tags",
        headers={k: v for k, v in headers.items() if k != "X-Request-Id"},
        json={"text": "z"},
    )
    assert response.status_code == 422
    assert response.json()["details_safe"]["field_path"] == "header.X-Request-Id"
    missing_key = client.post("/v1/tags", headers=headers, json={"text": "z"})
    assert missing_key.json()["details_safe"]["field_path"] == "header.Idempotency-Key"
