"""E1/E2 — SC13: Save from the app and from Telegram at the same time, five presses.

Fixtures ``identity/d-concurrent-save-app-telegram`` and
``telegram/j-concurrent-save-app-telegram`` are the oracle. Their ``given`` rows are loaded,
their ``events`` are executed through the real service and HTTP layers, and their ``expected``
counts and ``forbidden_effects`` are asserted. Neither fixture is edited here.

What the counts prove, and why they are the right assertion
-----------------------------------------------------------
Fixture ``d`` deliberately does **not** say which channel wins: "commit order is not
deterministic; the oracle is the ROW COUNT, not the channel". So the assertions are
``saved_item__total = 1``, ``saved_item__state_active = 1``, ``saved_snapshot = 1``,
``orphan_saved_snapshot = 0`` and ``telegram_bot_responses = 5``, exactly as the fixture
states them.

``orphan_saved_snapshot = 0`` is the sharp one. It fails for an implementation that writes the
snapshot in its own transaction and the pointer in another, and it fails for one that retries
the insert after a unique violation — both of which are listed as forbidden effects. It is
the reason ``TXN-save-target`` is one ``BEGIN…COMMIT`` and the loser rolls back whole.

Two threads, not two sequential calls: a sequential pair would also pass against a
check-then-insert implementation, which the contract forbids. ``test_unique_index_is_the_arbiter``
goes further and removes the read entirely.
"""

from __future__ import annotations

import json
import os
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from rr_contracts.generated.constants import CONTRACT_SCHEMA_VERSION
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine

from server.app.auth.csrf import CSRF_COOKIE_NAME
from server.app.auth.middleware import SESSION_COOKIE_NAME, PrincipalKind, TokenRegistry
from server.app.auth.service import AuthService
from server.app.db import create_sqlite_engine
from server.app.main import create_app
from server.app.saved import service
from server.app.saved.service import SavedError, TargetRef

REPO_ROOT = Path(__file__).resolve().parents[2]

OWNER_ID = "01J0WNER100000000000000000"
WORK_ID = "01JW0RKD100000000000000000"
ANALYSIS_OLD = "01JANA1YD10000000000000000"
ANALYSIS_NEWER = "01JANA1YD20000000000000000"
REPORT_ITEM_ID = "01JR1TEMD10000000000000000"
TELEGRAM_KEY = "tg-cb-01JD000000000000000001"
TELEGRAM_SECRET = "telegram-ingress-secret-value"
OWNER_NAME = "owner"
OWNER_PASSWORD = "correct horse battery staple"
NOW = "2026-09-05T20:10:00.000Z"
LATER = "2026-09-05T20:20:00.000Z"

TARGET = TargetRef(kind="work", identifier=WORK_ID)

WIRE_HEADERS = {
    "X-Schema-Version": CONTRACT_SCHEMA_VERSION,
    "X-Request-Id": "01J0000000000000000000000Z",
}


def _analysis_payload(marker: str) -> dict[str, Any]:
    """A minimal ``analysis-result`` summary payload; ``marker`` makes revisions tell apart."""
    return {
        "schema_version": "0.1.0",
        "task_type": "summary",
        "result": {
            "content": f"Nội dung tóm tắt ({marker}).",
            "difference_from_existing": {
                "text": "Điểm khác so với cái đã có.",
                "comparator": {"kind": "unknown"},
            },
            "limitation_line": "Một dòng hạn chế.",
            "statements": [{"kind": "ai_inference", "text": "Suy luận."}],
        },
    }


# --------------------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------------------


@pytest.fixture()
def engine(tmp_path: Path) -> Iterator[Engine]:
    """A database created by the real migrations -- not by ``CREATE TABLE`` in a test."""
    database = tmp_path / "research-radar.db"
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(database)
    try:
        config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
        config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous
    built = create_sqlite_engine(database)
    _seed(built)
    yield built
    built.dispose()


def _seed(engine: Engine) -> None:
    """Fixture ``j``'s ``given`` rows, in the columns this schema actually has.

    Two ``analysis`` rows, both ``valid``: revision 1 is the one the report item on screen
    points at, revision 2 appeared a minute before the click. Fixture ``j`` marks the second
    "the snapshot must NOT take this one".
    """
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, created_at,"
            " failed_login_count) VALUES (?, 1, 'owner', 'Asia/Ho_Chi_Minh', ?, 0)",
            (OWNER_ID, NOW),
        )
        connection.exec_driver_sql(
            "INSERT INTO work (id, owner_id, canonical_arxiv_id, title, metadata_state,"
            " identity_state, first_discovered_at, ingest_sequence, content_state, created_at)"
            " VALUES (?, ?, '2505.05555', 'Một công trình ví dụ', 'partial', 'active', ?, 1,"
            " 'present', ?)",
            (WORK_ID, OWNER_ID, NOW, NOW),
        )
        for analysis_id, generation, marker, analyzed_at in (
            (ANALYSIS_OLD, 1, "revision đang đọc", "2026-09-05T08:30:00.000Z"),
            (ANALYSIS_NEWER, 2, "bản mới hơn", "2026-09-05T20:09:00.000Z"),
        ):
            connection.exec_driver_sql(
                "INSERT INTO analysis (id, owner_id, analysis_generation_id, target_kind,"
                " target_work_id, task_type, source_fingerprint, prompt_version, schema_version,"
                " generation_number, status, payload, payload_hash, evidence_level,"
                " provider_name, model_name, analyzed_at, accepted_from_attempt_id)"
                " VALUES (?, ?, ?, 'work', ?, 'summary', ?, 'p-1', '0.1.0', ?, 'valid', ?, ?,"
                " 'abstract', 'anthropic', 'claude-opus-5', ?, ?)",
                (
                    analysis_id,
                    OWNER_ID,
                    f"01JGEN0000000000000000000{generation}",
                    WORK_ID,
                    f"fp-{generation}",
                    generation,
                    json.dumps(_analysis_payload(marker), ensure_ascii=False),
                    "sha256:" + f"{generation}" * 64,
                    analyzed_at,
                    f"01JATT0000000000000000000{generation}",
                ),
            )


def _counts(engine: Engine) -> dict[str, int]:
    """The four count oracles fixture ``d`` names, read straight out of the database."""
    with engine.connect() as connection:
        items = int(connection.exec_driver_sql("SELECT COUNT(*) FROM saved_item").scalar_one())
        active = int(
            connection.exec_driver_sql(
                "SELECT COUNT(*) FROM saved_item WHERE state = 'active'"
            ).scalar_one()
        )
        snapshots = int(
            connection.exec_driver_sql("SELECT COUNT(*) FROM saved_snapshot").scalar_one()
        )
        orphans = int(
            connection.exec_driver_sql(
                "SELECT COUNT(*) FROM saved_snapshot AS ss WHERE NOT EXISTS"
                " (SELECT 1 FROM saved_item AS si WHERE si.saved_snapshot_id = ss.id)"
            ).scalar_one()
        )
    return {
        "saved_item__total": items,
        "saved_item__state_active": active,
        "saved_snapshot": snapshots,
        "orphan_saved_snapshot": orphans,
    }


# --------------------------------------------------------------------------------------
# SC13 — the concurrent save
# --------------------------------------------------------------------------------------


def test_app_and_telegram_save_concurrently_produce_one_saved(
    engine: Engine, fixture_loader: Any
) -> None:
    """Fixture ``identity/d`` events 1 and 2, run in two threads against one database."""
    fixture = fixture_loader("identity/d-concurrent-save-app-telegram")
    expected = fixture.data["expected"]["counts"]

    barrier = threading.Barrier(2)
    results: dict[str, Any] = {}
    errors: dict[str, BaseException] = {}

    def save(channel: str, caller: str, idempotency_key: str | None) -> None:
        try:
            barrier.wait(timeout=10)
            results[channel] = service.create_save(
                engine,
                owner_id=OWNER_ID,
                target=TARGET,
                save_channel=channel,
                analysis_id=ANALYSIS_OLD,
                source_report_item_id=REPORT_ITEM_ID,
                idempotency_key=idempotency_key,
                caller_module=caller,
            )
        except BaseException as failure:  # recorded, then re-raised by the assertion below
            errors[channel] = failure

    threads = [
        threading.Thread(target=save, args=("app", "MOD-web-ui", None)),
        threading.Thread(target=save, args=("telegram", "MOD-telegram-adapter", TELEGRAM_KEY)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert not errors, errors
    counts = _counts(engine)
    assert counts["saved_item__total"] == expected["saved_item__total"]
    assert counts["saved_item__state_active"] == expected["saved_item__state_active"]
    assert counts["saved_snapshot"] == expected["saved_snapshot"]
    assert counts["orphan_saved_snapshot"] == expected["orphan_saved_snapshot"]

    statuses = sorted(result.status for result in results.values())
    assert statuses == ["already_saved", "created"], statuses
    # Both channels answer, and both name the SAME row -- the fixture's "cả hai đường nhận
    # phản hồi nhất quán".
    assert len({result.saved_item_id for result in results.values()}) == 1


def test_five_telegram_presses_make_one_row_and_five_answers(
    engine: Engine, fixture_loader: Any
) -> None:
    """Fixture ``d`` event 3: four more presses on the same key. ``5 presses = 1 row``.

    ``telegram_bot_responses = 5`` is asserted as five returned results, not as five log
    lines: the contract's point (REQ-D38) is that the owner is never left without an answer,
    and a silent 2nd..5th press is listed as a forbidden effect.
    """
    fixture = fixture_loader("identity/d-concurrent-save-app-telegram")
    expected = fixture.data["expected"]["counts"]

    answers = [
        service.create_save(
            engine,
            owner_id=OWNER_ID,
            target=TARGET,
            save_channel="telegram",
            analysis_id=ANALYSIS_OLD,
            source_report_item_id=REPORT_ITEM_ID,
            idempotency_key=TELEGRAM_KEY,
            caller_module="MOD-telegram-adapter",
        )
        for _ in range(5)
    ]

    assert len(answers) == expected["telegram_bot_responses"]
    assert [answer.status for answer in answers] == ["created"] + ["already_saved"] * 4
    assert len({answer.saved_item_id for answer in answers}) == 1
    counts = _counts(engine)
    assert counts["saved_item__total"] == 1
    assert counts["saved_snapshot"] == 1
    assert counts["orphan_saved_snapshot"] == 0


def test_unique_index_is_the_arbiter_not_a_pre_read(
    engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With every "is it already saved?" read blinded, still exactly one row.

    ``entities.yaml`` lists "check-then-insert without a lock" as a forbidden implementation.
    This test makes the lookups answer ``None`` forever — the state an implementation that
    trusted a pre-read would see when it loses the race — and asserts the second call still
    cannot create a second row, because the partial UNIQUE index refused the INSERT.
    """
    first = service.create_save(
        engine,
        owner_id=OWNER_ID,
        target=TARGET,
        save_channel="app",
        analysis_id=ANALYSIS_OLD,
    )
    assert first.status == "created"

    monkeypatch.setattr(service.SavedRepository, "active_item", lambda *a, **k: None)
    monkeypatch.setattr(service.SavedRepository, "item_by_idempotency_key", lambda *a, **k: None)

    with pytest.raises(SavedError) as refused:
        service.create_save(
            engine,
            owner_id=OWNER_ID,
            target=TARGET,
            save_channel="telegram",
            analysis_id=ANALYSIS_OLD,
            caller_module="MOD-telegram-adapter",
        )
    # The row exists but the blinded read cannot find it: CONFLICT is the registered code for
    # this collision class (ports.yaml error_note_vi), and it is raised rather than a second
    # row being written.
    assert refused.value.code is ErrorCode.CONFLICT
    assert _counts(engine) == {
        "saved_item__total": 1,
        "saved_item__state_active": 1,
        "saved_snapshot": 1,
        "orphan_saved_snapshot": 0,
    }


def test_snapshot_takes_the_revision_being_read_not_the_newer_one(engine: Engine) -> None:
    """Fixture ``j``: analysis 2 exists and is newer; the snapshot must still cite analysis 1.

    ``TXN-save-target.snapshot_source_rule`` calls taking the newer revision a forbidden
    effect: between reading and clicking, a fresher analysis may appear, and saving it would
    snapshot something the owner never saw.
    """
    result = service.create_save(
        engine,
        owner_id=OWNER_ID,
        target=TARGET,
        save_channel="app",
        analysis_id=ANALYSIS_OLD,
        source_report_item_id=REPORT_ITEM_ID,
    )
    assert result.status == "created"

    wire = service.read_saved(engine, owner_id=OWNER_ID, target=TARGET)
    assert wire is not None
    assert wire["snapshot"]["analysis_id_at_save"] == ANALYSIS_OLD
    assert wire["snapshot"]["content"]["analysis_ref"]["analysis_id"] == ANALYSIS_OLD
    assert "revision đang đọc" in wire["snapshot"]["content"]["summary"]["content_vi"]


def test_work_detail_branch_takes_the_newest_valid_revision(engine: Engine) -> None:
    """No ``source_report_item_id`` ⇒ the newest ``valid`` analysis at transaction start.

    The other half of ``snapshot_source_rule``: saving from Work detail is outside any report,
    so there is no "revision being read" and the rule names the newest one instead.
    """
    result = service.create_save(engine, owner_id=OWNER_ID, target=TARGET, save_channel="app")
    assert result.status == "created"
    wire = service.read_saved(engine, owner_id=OWNER_ID, target=TARGET)
    assert wire is not None
    assert wire["snapshot"]["analysis_id_at_save"] == ANALYSIS_NEWER


# --------------------------------------------------------------------------------------
# SC49 / NC-01, NC-20, NC-36 — who may not call save.create
# --------------------------------------------------------------------------------------


@pytest.fixture()
def client(engine: Engine) -> Iterator[TestClient]:
    """The real app: this card's routes, the real ``AuthService``, a Telegram ingress secret.

    The session provider is the one ``TC-owner-auth-session`` ships, not a stand-in. A fake
    would prove only that the fake admits the right callers; the codes asserted below
    (401 vs 403, ``UNAUTHORIZED`` vs ``CSRF_REJECTED``) come out of that card's middleware
    and are exactly what this card must not get wrong.
    """
    app = create_app()
    app.state.engine = engine
    app.state.telegram_ingress_secret = TELEGRAM_SECRET
    app.state.token_registry = TokenRegistry(
        {
            "collector-token-value": PrincipalKind.COLLECTOR,
            "worker-token-value": PrincipalKind.ANALYSIS_WORKER,
        }
    )
    auth_service = AuthService(engine)
    auth_service.bootstrap_owner(display_name=OWNER_NAME, password=OWNER_PASSWORD)
    app.state.auth_service = auth_service
    with TestClient(app) as test_client:
        yield test_client


def _login(client: TestClient) -> str:
    """Log in through the real service and return the CSRF token for the double submit."""
    service_obj = client.app.state.auth_service
    result = service_obj.login(OWNER_NAME, OWNER_PASSWORD)
    client.cookies.set(SESSION_COOKIE_NAME, result.session_token)
    client.cookies.set(CSRF_COOKIE_NAME, result.csrf_token)
    return result.csrf_token


@pytest.mark.parametrize(
    ("case", "headers"),
    [
        ("NC-01", {"Authorization": "Bearer collector-token-value"}),
        ("NC-20", {"Authorization": "Bearer worker-token-value"}),
        ("NC-36", {}),
    ],
)
def test_denied_principals_cannot_save(
    client: TestClient, engine: Engine, case: str, headers: dict[str, str]
) -> None:
    """NC-01 / NC-20 / NC-36: ``UNAUTHORIZED`` (401) and **no row changes at all**.

    ``UNAUTHORIZED``, not ``FORBIDDEN_EDGE``: three upstream files agree on the code for a
    valid credential of a class the operation does not admit — ``modules.yaml`` denied cases,
    the ``UNAUTHORIZED`` oracle in ``errors.yaml``, and the ``collectorToken`` description in
    ``openapi.yaml`` (401). Fixture ``recovery/i-collector-token-calls-save`` pins it and
    records the packet text that once said otherwise (``CR-PC08-04``).
    """
    before = _counts(engine)
    response = client.post(
        "/v1/saved",
        json={"target": TARGET.key},
        headers={**WIRE_HEADERS, "Idempotency-Key": "nc-case-key-0001", **headers},
    )
    assert response.status_code == 401, response.text
    assert response.json()["code"] == ErrorCode.UNAUTHORIZED.value
    assert _counts(engine) == before


def test_telegram_ingress_from_an_unlinked_chat_is_refused(
    client: TestClient, engine: Engine
) -> None:
    """A valid ingress secret from a chat that is not linked ⇒ ``UNAUTHORIZED_COMMAND``.

    Card §7: "Save từ chat chưa liên kết ⇒ im lặng, không đổi state". The transport is
    trusted; the sender is not authorised. No resolver is installed here, and that answers the
    same way an unlinked chat does — "linking has not shipped" is not a reason to write rows
    on behalf of whoever asked.
    """
    before = _counts(engine)
    response = client.post(
        "/v1/saved",
        json={"target": TARGET.key, "chat_id": "999"},
        headers={
            **WIRE_HEADERS,
            "Idempotency-Key": "tg-unlinked-key-01",
            "X-Telegram-Bot-Api-Secret-Token": TELEGRAM_SECRET,
        },
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == ErrorCode.UNAUTHORIZED_COMMAND.value
    assert _counts(engine) == before


def test_forbidden_caller_module_is_forbidden_edge_not_unauthorized(engine: Engine) -> None:
    """The in-process half of R5-01: an unregistered caller module ⇒ ``FORBIDDEN_EDGE``.

    Deliberately a different code from the HTTP cases above. ``save.create`` has exactly two
    registered callers; anything else calling the service function directly is row 2 of the
    boundary table, and card §10 ``SG-DENY`` makes returning the wrong one of the two a FAIL.
    """
    before = _counts(engine)
    with pytest.raises(SavedError) as refused:
        service.create_save(
            engine,
            owner_id=OWNER_ID,
            target=TARGET,
            save_channel="app",
            caller_module="MOD-analysis-worker",
        )
    assert refused.value.code is ErrorCode.FORBIDDEN_EDGE
    assert refused.value.details_safe["forbidden_edge_ref"] == "FE-14"
    assert _counts(engine) == before


# --------------------------------------------------------------------------------------
# The save-from-chat path (TC-telegram-linking-auth)
# --------------------------------------------------------------------------------------


def test_cmd_save_goes_through_this_service(engine: Engine) -> None:
    """``CMD-save`` (plain text) reaches ``save.create``: five presses, one row, five replies.

    Integrates with the sibling card for real rather than against a stub. If
    ``server.app.telegram`` is not there yet this xfails — the integration is the thing being
    asserted, and a stubbed adapter would assert only that the stub works.
    """
    commands = pytest.importorskip(
        "server.app.telegram.commands", reason="pending TC-telegram-linking-auth"
    )
    adapter = service.TelegramSaveAdapter(engine)
    ports = commands.CommandPorts(save_create=adapter)

    replies = []
    for index in range(5):
        parsed = commands.parse_command(f"/save {TARGET.key}")
        assert parsed is not None
        result = commands.execute_command(
            parsed, owner_id=OWNER_ID, request_id=f"01JREQ00000000000000000{index:03d}", ports=ports
        )
        replies.extend(result.replies)

    assert len(replies) == 5
    # Plain text only: no parse mode, no inline keyboard, no callback_data (OD-20260908-09).
    assert all(isinstance(reply, str) and reply for reply in replies)
    counts = _counts(engine)
    assert counts["saved_item__total"] == 1
    assert counts["saved_item__state_active"] == 1
    assert counts["saved_snapshot"] == 1
    assert counts["orphan_saved_snapshot"] == 0


def test_telegram_save_result_shape_matches_the_adapter_port(engine: Engine) -> None:
    """The duck-typed result really is the shape ``CommandPorts.save_create`` expects."""
    commands = pytest.importorskip(
        "server.app.telegram.commands", reason="pending TC-telegram-linking-auth"
    )
    mine = {field for field in service.TelegramSaveResult.__dataclass_fields__}
    theirs = {field for field in commands.SaveResult.__dataclass_fields__}
    assert mine == theirs, (mine, theirs)


# --------------------------------------------------------------------------------------
# save.remove and the HTTP surface
# --------------------------------------------------------------------------------------


def test_remove_keeps_the_snapshot_and_is_idempotent(engine: Engine) -> None:
    """``save.remove`` un-saves. The snapshot's bytes and its hash do not move."""
    created = service.create_save(
        engine, owner_id=OWNER_ID, target=TARGET, save_channel="app", analysis_id=ANALYSIS_OLD
    )
    before = _counts(engine)

    first = service.remove_save(engine, owner_id=OWNER_ID, target=TARGET, now=LATER)
    assert first.removed is True
    assert first.state == "unsaved"
    assert first.unsaved_at == LATER

    second = service.remove_save(engine, owner_id=OWNER_ID, target=TARGET, now=LATER)
    assert second.removed is False
    assert second.saved_item_id == first.saved_item_id

    after = _counts(engine)
    assert after["saved_snapshot"] == before["saved_snapshot"]
    assert after["saved_item__total"] == before["saved_item__total"]
    assert after["saved_item__state_active"] == 0

    still_readable = service.read_saved(engine, owner_id=OWNER_ID, target=TARGET)
    assert still_readable is not None
    assert still_readable["snapshot"]["content_hash"] == created.content_hash


def test_resave_after_unsave_makes_a_new_snapshot(engine: Engine) -> None:
    """Re-saving takes a fresh snapshot; the old row stays as history.

    ``unsave_resave_semantics`` in the schema: reusing the old snapshot would lie about when
    it was taken, because a new analysis generation may have landed in between.
    """
    first = service.create_save(
        engine, owner_id=OWNER_ID, target=TARGET, save_channel="app", analysis_id=ANALYSIS_OLD
    )
    service.remove_save(engine, owner_id=OWNER_ID, target=TARGET, now=LATER)
    second = service.create_save(
        engine, owner_id=OWNER_ID, target=TARGET, save_channel="app", analysis_id=ANALYSIS_NEWER
    )
    assert second.status == "created"
    assert second.saved_snapshot_id != first.saved_snapshot_id

    counts = _counts(engine)
    assert counts["saved_item__total"] == 2
    assert counts["saved_item__state_active"] == 1
    assert counts["saved_snapshot"] == 2
    assert counts["orphan_saved_snapshot"] == 0


def test_http_save_and_list_round_trip(client: TestClient, engine: Engine) -> None:
    """The owner-session branch end to end: 201 created, then the item appears in the list."""
    csrf_token = _login(client)

    created = client.post(
        "/v1/saved",
        json={"target": TARGET.key, "analysis_id": ANALYSIS_OLD},
        headers={
            **WIRE_HEADERS,
            "Idempotency-Key": "app-save-key-0001",
            "X-CSRF-Token": csrf_token,
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["status"] == "created"

    listed = client.get("/v1/saved", headers=WIRE_HEADERS)
    assert listed.status_code == 200, listed.text
    body = listed.json()
    assert body["count"] == 1
    assert body["items"][0]["saved_item"]["target_key"] == TARGET.key
    assert body["items"][0]["snapshot"]["content_hash"] == created.json()["content_hash"]

    removed = client.request(
        "DELETE",
        f"/v1/saved/{TARGET.key}",
        headers={
            **WIRE_HEADERS,
            "Idempotency-Key": "app-remove-key-0001",
            "X-CSRF-Token": csrf_token,
        },
    )
    assert removed.status_code == 200, removed.text
    assert removed.json()["removed"] is True
    # Un-saving removes it from the Saved screen; it does not remove the snapshot row.
    assert client.get("/v1/saved", headers=WIRE_HEADERS).json()["count"] == 0
    with engine.connect() as connection:
        assert (
            int(connection.exec_driver_sql("SELECT COUNT(*) FROM saved_snapshot").scalar_one()) == 1
        )


def test_missing_csrf_on_a_mutation_is_csrf_rejected(client: TestClient, engine: Engine) -> None:
    """A valid session without the double-submit token ⇒ 403 ``CSRF_REJECTED``, session intact.

    The order matters and is the one openapi puts the two schemes in: no credential at all is
    ``UNAUTHORIZED``; a good session with a missing proof of intent is ``CSRF_REJECTED``, and
    it does not end the session (ruling R5-01 row 4).
    """
    _login(client)
    before = _counts(engine)
    response = client.post(
        "/v1/saved",
        json={"target": TARGET.key},
        headers={**WIRE_HEADERS, "Idempotency-Key": "app-save-key-0002"},
    )
    assert response.status_code == 403, response.text
    assert response.json()["code"] == ErrorCode.CSRF_REJECTED.value
    assert _counts(engine) == before
    # The session still works afterwards.
    assert client.get("/v1/saved", headers=WIRE_HEADERS).status_code == 200


def test_save_export_is_not_routed(client: TestClient) -> None:
    """``SG-01``: export is deferred (``F-PC00-02``), so no route answers it."""
    routes = {getattr(route, "operation_id", None) for route in client.app.routes}
    assert "save.export" not in routes
