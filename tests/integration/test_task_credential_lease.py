"""E1/E2 — ISO-05 run for real, the ``terms_check`` gate proved at the database, canary sealed.

``SG-ISO05`` of the card is unusually blunt about what counts:

    ISO-05 chỉ được coi là chứng minh khi ca âm **chạy thật** và bị từ chối. Một test khẳng
    định 'đường này không tồn tại' **không** phải bằng chứng cho ISO-05.

So the negative case here builds a real task, a real lease and a real credential store, and
then calls ``secret.issue_task_credential`` as a worker that does **not** hold the current
lease. The oracle is two numbers, not a narrative: the error code is ``STALE_LEASE``, and
``COUNT(task_credential)`` is unchanged across the refusal.

Three more oracles from the card's §8, in the same style:

* fixture ``recovery/f-secret-canary-injection.json`` -- the canary appears **0** times across
  every audit row, every error envelope and every column of the database;
* fixture ``ai/k-zero-api-key-all-tasks-via-cli.json`` -- a ``cli_acp`` task draws **0**
  credentials, because that path is issued nothing at all (``secrets.md`` §5.1);
* ``enabled = 1`` with ``terms_check_at IS NULL`` is refused by **SQLite**, proved by issuing
  the raw ``UPDATE`` rather than by going through the service that also checks it.

The lease itself comes from ``MOD-analysis-service``: ``analysis.enqueue_tasks`` then
``analysis.claim_task``. Writing the lease row by hand would test this file's idea of a lease
instead of the one the system actually issues.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from rr_contracts.generated.errors import ErrorCode
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError

from server.app.analysis.service import AnalysisContext, TargetRequest, claim_task, enqueue_tasks
from server.app.db import create_sqlite_engine
from server.app.secret.repository import SecretRepository
from server.app.secret.service import (
    AnalysisLeaseVerifier,
    SecretContext,
    SecretError,
    issue_task_credential,
    revoke_task_credential,
    store_provider_key,
)
from server.app.secret.store import InMemoryMaterialStore, SecretStore
from server.app.settings_service.repository import ProviderConfigRow, SettingsRepository
from server.app.settings_service.service import SettingsContext, SettingsProviderView

REPO_ROOT = Path(__file__).resolve().parents[2]
OWNER_ID = "01J0000000000000000OWNER01"
RUN_ID = "01J00000000000000000RUN001"
WORK_ID = "01J0000000000000000WORK001"
ASSIGNMENT_ID = "01J000000000000000ASSIGN01"
HOLDER = "worker-A"
INTRUDER = "worker-B"

#: The canary of ``recovery/f-secret-canary-injection.json``, verbatim.
CANARY = "CANARY-8f3a-DO-NOT-EMIT"

TEST_MASTER_KEY = b"\x22" * 32
T0 = datetime(2026, 9, 8, 9, 0, 0, tzinfo=UTC)


class FakeTaskInput:
    """One committed source, so the task has an evidence ceiling and a fingerprint."""

    def sources_for(self, *, target_key: str) -> list[Any]:
        from server.app.analysis.service import TaskSource

        return [
            TaskSource(
                source_id="01J0000000000000000SOURCE1",
                kind="work_version",
                text="Abstract nêu bộ dữ liệu là ImageNet-1k.",
                source_hash="sha256:" + "c" * 64,
                retrieved_at="2026-09-06T17:00:00.000Z",
            )
        ]


def _migrate(db_path: Path) -> None:
    from alembic import command
    from alembic.config import Config

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
    db_path = tmp_path / "rr.db"
    _migrate(db_path)
    engine = create_sqlite_engine(db_path)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                "created_at, failed_login_count) VALUES (:id, 1, 'owner', "
                "'Asia/Ho_Chi_Minh', '2026-09-01T00:00:00.000Z', 0)"
            ),
            {"id": OWNER_ID},
        )
        connection.execute(
            text(
                "INSERT INTO work (id, owner_id, metadata_state, identity_state, "
                "first_discovered_at, ingest_sequence, content_state, created_at) "
                "VALUES (:id, :owner_id, 'complete', 'active', "
                "'2026-09-05T00:00:00.000Z', 1, 'present', '2026-09-05T00:00:00.000Z')"
            ),
            {"id": WORK_ID, "owner_id": OWNER_ID},
        )
        connection.execute(
            text(
                "INSERT INTO run (id, owner_id, trigger_type, phase, status, applied_config, "
                "created_at, schedule_occurrence_ids, current_lease_epoch, attempt_count, "
                "posts_observed_total, posts_ingested_new, limit_hit, cursor_invalidated) "
                "VALUES (:id, :owner_id, 'manual', 'analyzing', 'running', '{}', "
                "'2026-09-08T08:00:00.000Z', '[]', 1, 0, 0, 0, 0, 0)"
            ),
            {"id": RUN_ID, "owner_id": OWNER_ID},
        )
        connection.execute(
            text(
                "INSERT INTO assignment (id, owner_id, run_id, kind, phase, state, "
                "required_capabilities, created_at) VALUES (:id, :owner_id, :run_id, "
                "'analyze', 'analyzing', 'claimed', '[]', '2026-09-08T08:30:00.000Z')"
            ),
            {"id": ASSIGNMENT_ID, "owner_id": OWNER_ID, "run_id": RUN_ID},
        )
    yield engine
    engine.dispose()


def _clock(start: datetime) -> Any:
    state = {"now": start}

    def now() -> datetime:
        value = state["now"]
        state["now"] = value + timedelta(milliseconds=1)
        return value

    return now


@pytest.fixture
def settings_ctx(engine: Engine) -> SettingsContext:
    return SettingsContext(engine=engine, owner_id=OWNER_ID, clock=_clock(T0))


@pytest.fixture
def secret_ctx(engine: Engine, settings_ctx: SettingsContext) -> SecretContext:
    store = SecretStore(master_key=TEST_MASTER_KEY, material=InMemoryMaterialStore())
    return SecretContext(
        engine=engine,
        owner_id=OWNER_ID,
        store=store,
        providers=SettingsProviderView(settings_ctx),
        clock=_clock(T0),
    )


@pytest.fixture
def analysis_ctx(engine: Engine, settings_ctx: SettingsContext) -> AnalysisContext:
    class ProviderChoiceView:
        """``MOD-analysis-service``'s narrower view of the same ``provider_config`` rows."""

        def provider_for(self, task_type: str) -> Any:
            from server.app.analysis.service import ProviderChoice

            binding = SettingsProviderView(settings_ctx).secret_ref_for_task(task_type)
            if binding is None:
                return None
            return ProviderChoice(
                task_type=task_type,
                auth_family=binding.auth_family,
                provider_name=binding.provider_name,
                model_name=binding.model_name,
                enabled=binding.enabled,
            )

    return AnalysisContext(
        engine=engine,
        owner_id=OWNER_ID,
        provider_config=ProviderChoiceView(),
        task_input=FakeTaskInput(),
        run_id=RUN_ID,
        clock=_clock(T0),
    )


def _configure_provider(
    engine: Engine,
    *,
    secret_ref_id: str | None,
    auth_family: str = "api_key",
    enabled: bool = True,
    task_type: str = "summary",
) -> None:
    """Write a ``provider_config`` row directly.

    ``terms_check_at`` is filled here because this is **test data**, not evidence: the row
    stands for an owner who has already recorded that they read the vendor's terms. Nothing in
    ``server/app/`` ever writes that field on its own -- ``SG-TERMS`` forbids it, and
    :func:`test_enabling_without_terms_check_is_refused_by_the_database` proves the gate that
    makes the omission fatal.
    """
    with engine.begin() as connection:
        SettingsRepository().upsert_provider(
            connection,
            ProviderConfigRow(
                id="01J00000000000000000PROV1",
                owner_id=OWNER_ID,
                task_type=task_type,
                auth_family=auth_family,
                provider_name="anthropic",
                model_name="claude-opus-5",
                max_concurrency=1,
                secret_ref=secret_ref_id,
                enabled=enabled,
                terms_check_at="2026-09-08T00:00:00.000Z" if enabled else None,
                terms_check_by="Owner (OD-20260908-08)" if enabled else None,
                terms_doc_ref="https://www.anthropic.com/legal/commercial-terms 2026-09-08"
                if enabled
                else None,
            ),
        )


def _claim_a_task(analysis_ctx: AnalysisContext, *, worker: str = HOLDER) -> dict[str, Any]:
    enqueue_tasks(
        analysis_ctx,
        [TargetRequest(target_kind="work", target_id=WORK_ID, task_type="summary")],
        caller_module="MOD-report-service",
    )
    claimed = claim_task(
        analysis_ctx,
        worker_identity=worker,
        claim_request_id="01J0000000000000000CLAIM01",
        task_types=["summary"],
    )
    assert claimed["task"] is not None, claimed
    return dict(claimed["task"])


def _attempt_id(engine: Engine) -> str:
    with engine.connect() as connection:
        return str(connection.execute(text("SELECT id FROM analysis_attempt")).scalar_one())


def _count_credentials(engine: Engine) -> int:
    with engine.connect() as connection:
        return int(connection.execute(text("SELECT COUNT(*) FROM task_credential")).scalar_one())


# ------------------------------------------------------------------------------- ISO-05


def test_iso05_a_worker_without_the_lease_is_refused_and_no_credential_is_written(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """The negative case, executed -- ``SG-ISO05``, ``providers.yaml`` §4 ``ISO-05``.

    ``worker-A`` claims the task; ``worker-B`` asks for its credential with the same lease id
    and epoch. The refusal is ``STALE_LEASE`` and the credential table does not move.
    """
    reference = store_provider_key(secret_ctx, provider_id="anthropic", value=CANARY)
    _configure_provider(engine, secret_ref_id=reference.secret_ref_id)
    task = _claim_a_task(analysis_ctx)
    secret_ctx.leases = AnalysisLeaseVerifier(analysis_ctx)
    before = _count_credentials(engine)

    with pytest.raises(SecretError) as raised:
        issue_task_credential(
            secret_ctx,
            task_id=task["task_id"],
            attempt_id=_attempt_id(engine),
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"],
            worker_identity=INTRUDER,
            assignment_id=ASSIGNMENT_ID,
        )

    assert raised.value.code is ErrorCode.STALE_LEASE
    assert _count_credentials(engine) == before == 0
    # And the refusal carried no secret with it.
    assert CANARY not in str(raised.value.details_safe)
    assert CANARY not in raised.value.message_safe


def test_iso05_a_stale_epoch_is_refused_even_for_the_right_worker(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """The second half of ISO-05: identity alone is not the gate, the current epoch is."""
    reference = store_provider_key(secret_ctx, provider_id="anthropic", value=CANARY)
    _configure_provider(engine, secret_ref_id=reference.secret_ref_id)
    task = _claim_a_task(analysis_ctx)
    secret_ctx.leases = AnalysisLeaseVerifier(analysis_ctx)

    with pytest.raises(SecretError) as raised:
        issue_task_credential(
            secret_ctx,
            task_id=task["task_id"],
            attempt_id=_attempt_id(engine),
            lease_id=task["lease_id"],
            lease_epoch=int(task["lease_epoch"]) - 1,
            worker_identity=HOLDER,
            assignment_id=ASSIGNMENT_ID,
        )

    assert raised.value.code is ErrorCode.STALE_LEASE
    assert _count_credentials(engine) == 0


def test_the_lease_holder_receives_exactly_one_credential_and_a_replay_reuses_it(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """The positive path, so the refusals above are not vacuous.

    Then the replay rule from ``contracts/ports.yaml``: "Cùng attempt trả cùng credential còn
    hạn". Two calls, one row.
    """
    reference = store_provider_key(secret_ctx, provider_id="anthropic", value="sk-live-real-key")
    _configure_provider(engine, secret_ref_id=reference.secret_ref_id)
    task = _claim_a_task(analysis_ctx)
    secret_ctx.leases = AnalysisLeaseVerifier(analysis_ctx)
    attempt = _attempt_id(engine)

    first = issue_task_credential(
        secret_ctx,
        task_id=task["task_id"],
        attempt_id=attempt,
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        worker_identity=HOLDER,
        assignment_id=ASSIGNMENT_ID,
    )
    assert first.value.reveal() == "sk-live-real-key"
    assert first.reused is False
    assert _count_credentials(engine) == 1

    second = issue_task_credential(
        secret_ctx,
        task_id=task["task_id"],
        attempt_id=attempt,
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        worker_identity=HOLDER,
        assignment_id=ASSIGNMENT_ID,
    )
    assert second.credential_id == first.credential_id
    assert second.reused is True
    assert _count_credentials(engine) == 1


def test_the_credential_expires_with_the_lease_not_after_it(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """``secrets.md`` §5: ``task_credential_ttl`` = 900 s = ``lease_ttl_analysis``.

    A credential that outlives the right to work is the hole the number exists to close, so
    the TTL is asserted against the contract's constant rather than against itself.
    """
    from server.app.analysis.service import LEASE_TTL_ANALYSIS_SECONDS
    from server.app.secret.service import TASK_CREDENTIAL_TTL_SECONDS

    assert TASK_CREDENTIAL_TTL_SECONDS == LEASE_TTL_ANALYSIS_SECONDS

    reference = store_provider_key(secret_ctx, provider_id="anthropic", value="k")
    _configure_provider(engine, secret_ref_id=reference.secret_ref_id)
    task = _claim_a_task(analysis_ctx)
    secret_ctx.leases = AnalysisLeaseVerifier(analysis_ctx)
    issued = issue_task_credential(
        secret_ctx,
        task_id=task["task_id"],
        attempt_id=_attempt_id(engine),
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        worker_identity=HOLDER,
        assignment_id=ASSIGNMENT_ID,
    )
    with engine.connect() as connection:
        issued_at, expires_at = connection.execute(
            text("SELECT issued_at, expires_at FROM task_credential WHERE id = :id"),
            {"id": issued.credential_id},
        ).one()
    from server.app.secret.repository import parse_timestamp

    delta = parse_timestamp(expires_at) - parse_timestamp(issued_at)
    assert delta == timedelta(seconds=TASK_CREDENTIAL_TTL_SECONDS)


def test_revoking_twice_changes_nothing_the_second_time(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """``ports.yaml``: "Thu hồi lại không đổi trạng thái"."""
    reference = store_provider_key(secret_ctx, provider_id="anthropic", value="k")
    _configure_provider(engine, secret_ref_id=reference.secret_ref_id)
    task = _claim_a_task(analysis_ctx)
    secret_ctx.leases = AnalysisLeaseVerifier(analysis_ctx)
    issue_task_credential(
        secret_ctx,
        task_id=task["task_id"],
        attempt_id=_attempt_id(engine),
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        worker_identity=HOLDER,
        assignment_id=ASSIGNMENT_ID,
    )

    assert revoke_task_credential(secret_ctx, assignment_id=ASSIGNMENT_ID, reason="submitted") == 1
    assert revoke_task_credential(secret_ctx, assignment_id=ASSIGNMENT_ID, reason="submitted") == 0
    with engine.connect() as connection:
        revoked = connection.execute(
            text("SELECT COUNT(*) FROM task_credential WHERE revoked_at IS NOT NULL")
        ).scalar_one()
    assert revoked == 1


def test_a_revoked_credential_is_not_handed_out_again(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """Revocation is terminal for that slot -- and the schema is why.

    ``ux_task_credential_assignment`` is UNIQUE on ``(owner_id, assignment_id, secret_ref_id)``
    and ``ENT-task-credential`` says the same thing in prose: "Một task nhận tối đa một
    credential cho một secret". So a revoked credential cannot be replaced by a second row for
    the same pairing, and the request is refused rather than served. This test was written the
    other way round first -- expecting a fresh row -- and the database refused it; the
    expectation was wrong, not the constraint (``CR-TC-SECRET-07`` records that the contract
    never states which error code this is).
    """
    reference = store_provider_key(secret_ctx, provider_id="anthropic", value="k")
    _configure_provider(engine, secret_ref_id=reference.secret_ref_id)
    task = _claim_a_task(analysis_ctx)
    secret_ctx.leases = AnalysisLeaseVerifier(analysis_ctx)
    attempt = _attempt_id(engine)
    first = issue_task_credential(
        secret_ctx,
        task_id=task["task_id"],
        attempt_id=attempt,
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        worker_identity=HOLDER,
        assignment_id=ASSIGNMENT_ID,
    )
    revoke_task_credential(secret_ctx, assignment_id=ASSIGNMENT_ID, reason="lease_expired")

    with pytest.raises(SecretError) as raised:
        issue_task_credential(
            secret_ctx,
            task_id=task["task_id"],
            attempt_id=attempt,
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"],
            worker_identity=HOLDER,
            assignment_id=ASSIGNMENT_ID,
        )
    assert raised.value.code is ErrorCode.NOT_FOUND
    assert (raised.value.details_safe or {}).get("resource_kind") == "task_credential"
    # Still exactly the one row, still revoked: the refusal wrote nothing.
    assert _count_credentials(engine) == 1
    with engine.connect() as connection:
        revoked_at = connection.execute(
            text("SELECT revoked_at FROM task_credential WHERE id = :id"),
            {"id": first.credential_id},
        ).scalar_one()
    assert revoked_at is not None


# ------------------------------------------------------- the zero-API-key path (fixture ai/k)


def test_a_cli_acp_task_draws_no_credential(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """``ai/k-zero-api-key-all-tasks-via-cli.json``: ``COUNT(task_credential) = 0``.

    ``secrets.md`` §5.1: the CLI/ACP path receives nothing from the server, so the call is
    refused rather than served with an empty credential -- and ``REQ-D51`` stays true.
    """
    _configure_provider(engine, secret_ref_id=None, auth_family="cli_acp")
    task = _claim_a_task(analysis_ctx)
    secret_ctx.leases = AnalysisLeaseVerifier(analysis_ctx)

    with pytest.raises(SecretError) as raised:
        issue_task_credential(
            secret_ctx,
            task_id=task["task_id"],
            attempt_id=_attempt_id(engine),
            lease_id=task["lease_id"],
            lease_epoch=task["lease_epoch"],
            worker_identity=HOLDER,
            assignment_id=ASSIGNMENT_ID,
        )

    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert (raised.value.details_safe or {}).get("violation_kind") == (
        "cli_acp_receives_no_server_secret"
    )
    assert _count_credentials(engine) == 0
    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM secret_ref")).scalar_one() == 0


def test_a_disabled_adapter_is_never_handed_a_credential(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """``B13``/``ADR-0010`` §3, and the state both Anthropic adapters ship in today.

    ``contracts/ai/providers.yaml`` §2.1 has ``enabled: false`` on both entries because
    ``ISO-03``/``ISO-05`` are unverified. A disabled adapter has no claimable task at all, so
    the credential path is never even reached -- asserted here as the count that stays 0.
    """
    reference = store_provider_key(secret_ctx, provider_id="anthropic", value="k")
    _configure_provider(engine, secret_ref_id=reference.secret_ref_id, enabled=False)
    enqueue_tasks(
        analysis_ctx,
        [TargetRequest(target_kind="work", target_id=WORK_ID, task_type="summary")],
        caller_module="MOD-report-service",
    )
    claimed = claim_task(
        analysis_ctx,
        worker_identity=HOLDER,
        claim_request_id="01J0000000000000000CLAIM02",
        task_types=["summary"],
    )
    assert claimed["task"] is None
    assert claimed.get("reason") == "no_enabled_provider"
    assert _count_credentials(engine) == 0


# ------------------------------------------------------ the terms gate, proved at the database


def test_enabling_without_terms_check_is_refused_by_the_database(engine: Engine) -> None:
    """``ck_provider_config_terms_before_enable`` -- reviewer question 3 of the card's §12.

    The write is issued as raw SQL on purpose. Going through
    :func:`server.app.settings_service.service.update_config` would prove that *the service*
    checks, which is the weaker claim; ``REQ-A5`` needs the gate to hold for every path,
    including ones written later by someone who has not read this file.
    """
    _configure_provider(engine, secret_ref_id=None, enabled=False)
    with pytest.raises(IntegrityError) as raised, engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE provider_config SET enabled = 1 "
                "WHERE owner_id = :owner_id AND task_type = 'summary'"
            ),
            {"owner_id": OWNER_ID},
        )
    assert "ck_provider_config_terms_before_enable" in str(raised.value)

    with engine.connect() as connection:
        still_disabled = connection.execute(
            text("SELECT enabled FROM provider_config WHERE owner_id = :owner_id"),
            {"owner_id": OWNER_ID},
        ).scalar_one()
    assert still_disabled == 0


def test_terms_check_at_without_a_reviewer_is_refused_by_the_database(engine: Engine) -> None:
    """``ck_provider_config_terms_by``: a terms record with nobody's name is not a record."""
    _configure_provider(engine, secret_ref_id=None, enabled=False)
    with pytest.raises(IntegrityError) as raised, engine.begin() as connection:
        connection.execute(
            text(
                "UPDATE provider_config SET terms_check_at = '2026-09-08T00:00:00.000Z', "
                "terms_check_by = NULL WHERE owner_id = :owner_id"
            ),
            {"owner_id": OWNER_ID},
        )
    assert "ck_provider_config_terms_by" in str(raised.value)


def test_the_service_refuses_the_same_enable_before_the_database_has_to(
    engine: Engine, settings_ctx: SettingsContext, secret_ctx: SecretContext
) -> None:
    """The application-level check exists too -- so the owner sees a contract error, not a 500."""
    settings_ctx.secrets = secret_ctx
    from server.app.settings_service.service import update_config

    with pytest.raises(SecretError) as raised:
        update_config(
            settings_ctx,
            request_id="01J000000000000000000REQ01",
            provider={
                "task_type": "summary",
                "auth_family": "api_key",
                "provider_name": "anthropic",
                "model_name": "claude-opus-5",
                "enabled": True,
            },
        )
    assert raised.value.code is ErrorCode.VALIDATION_ERROR
    assert (raised.value.details_safe or {}).get("violation_kind") == "terms_check_missing"
    with engine.connect() as connection:
        assert connection.execute(text("SELECT COUNT(*) FROM provider_config")).scalar_one() == 0


# ------------------------------------------------------------- the canary (fixture recovery/f)


def test_the_canary_never_appears_anywhere_in_the_database_or_the_audit(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """Fixture ``recovery/f``: "grep chuỗi canary trên toàn bộ log + DB + artifact ⇒ 0 kết quả".

    Every column of every table is stringified and searched -- not just the tables this card
    owns, because a leak into someone else's table would still be a leak. The count is
    asserted to be 0 rather than "not found": a number is the oracle the fixture asks for.
    """
    reference = store_provider_key(secret_ctx, provider_id="anthropic", value=CANARY)
    _configure_provider(engine, secret_ref_id=reference.secret_ref_id)
    task = _claim_a_task(analysis_ctx)
    secret_ctx.leases = AnalysisLeaseVerifier(analysis_ctx)
    issued = issue_task_credential(
        secret_ctx,
        task_id=task["task_id"],
        attempt_id=_attempt_id(engine),
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        worker_identity=HOLDER,
        assignment_id=ASSIGNMENT_ID,
    )
    # The worker really did receive it -- otherwise the search below proves nothing.
    assert issued.value.reveal() == CANARY

    occurrences = 0
    with engine.connect() as connection:
        tables = [
            row[0]
            for row in connection.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
            ).all()
        ]
        for table in tables:
            for row in connection.execute(text(f"SELECT * FROM {table}")).mappings().all():  # noqa: S608
                occurrences += str(dict(row)).count(CANARY)
    assert occurrences == 0

    # And the redacted repr is what a log line would have captured.
    assert CANARY not in repr(issued.value)
    assert CANARY not in str(issued.value)


def test_audit_rows_record_the_issue_without_the_value(
    engine: Engine, analysis_ctx: AnalysisContext, secret_ctx: SecretContext
) -> None:
    """``secrets.md`` §8: issuing is audited; the audit never holds what was issued."""
    reference = store_provider_key(secret_ctx, provider_id="anthropic", value=CANARY)
    _configure_provider(engine, secret_ref_id=reference.secret_ref_id)
    task = _claim_a_task(analysis_ctx)
    secret_ctx.leases = AnalysisLeaseVerifier(analysis_ctx)
    issue_task_credential(
        secret_ctx,
        task_id=task["task_id"],
        attempt_id=_attempt_id(engine),
        lease_id=task["lease_id"],
        lease_epoch=task["lease_epoch"],
        worker_identity=HOLDER,
        assignment_id=ASSIGNMENT_ID,
    )
    with engine.connect() as connection:
        rows = SecretRepository().audit_rows(connection, owner_id=OWNER_ID)
    actions = [row.action for row in rows]
    assert "issued" in actions
    assert all(CANARY not in (row.outcome_detail_safe or "") for row in rows)


# --------------------------------------------------------------------------- migration graph


def test_alembic_has_exactly_one_head() -> None:
    """One head, computed from the script directory -- never asserted as a literal id."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert len(heads) == 1, heads
