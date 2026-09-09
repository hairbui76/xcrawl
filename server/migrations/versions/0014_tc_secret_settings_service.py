"""The six tables ``MOD-secret-service`` and ``MOD-settings-service`` own.

Revision ID: 0014_tc_secret_settings_service
Revises: 0013_tc_backfill_pending_ledger
Create Date: 2026-09-08

One head, by chaining
---------------------
``0013_tc_backfill_pending_ledger`` is the single head at the time this revision is written,
so chaining off it keeps ``alembic heads`` at one without a merge file.
``tests/integration/test_task_credential_lease.py`` asserts that structurally --
``len(heads) == 1``, computed from the script directory, never written as a literal.

Six tables created
------------------
===========================  =============================  ==================================
table                        entity                         owner module
===========================  =============================  ==================================
``secret_ref``               ``ENT-secret-ref``             ``MOD-secret-service``
``task_credential``          ``ENT-task-credential``        ``MOD-secret-service``
``secret_audit``             ``ENT-secret-audit``           ``MOD-secret-service``
``provider_config``          ``ENT-provider-config``        ``MOD-settings-service``
``provider_test_result``     ``ENT-provider-test-result``   ``MOD-settings-service``
``source_connection``        ``ENT-source-connection``      ``MOD-settings-service``
===========================  =============================  ==================================

What this revision does **not** create
--------------------------------------
``settings``. ``0013_tc_backfill_pending_ledger`` created it *on behalf of*
``MOD-settings-service`` and said so; a second ``CREATE TABLE`` for a table another revision
already owns is the ``F-A3R1-01`` defect this repo has hit once. Every column
``ENT-settings`` declares is already on disk and correct, so there is nothing to extend
either. This card takes **ownership** of the table without touching its DDL.

Nor does it create a table for the secret **ciphertext**. ``contracts/ops/secrets.md`` §4.1
puts the ciphertext in "bảng của ``MOD-secret-service``", but ``contracts/data/entities.yaml``
declares no entity for it -- only ``secret_ref`` (a pointer), ``task_credential`` and
``secret_audit``. Shipping an undeclared table would fail
``tests/contract/test_schema_matches_entities.py`` on its first assertion, and inventing an
entity is a contract change this card is forbidden to make. The material therefore lives
behind ``server.app.secret.store.SecretMaterialStore``, injected by the composition root,
and the gap is reported as ``CR-TC-SECRET-01``.

The two CHECKs that make ``REQ-A5`` enforceable
-----------------------------------------------
``ck_provider_config_terms_before_enable`` (``enabled = 0 OR terms_check_at IS NOT NULL``)
and ``ck_provider_config_terms_by`` (``terms_check_at IS NULL OR terms_check_by IS NOT
NULL``) are written verbatim from ``ENT-provider-config.checks``. They are the reason the
card's §12 reviewer question 3 -- "is the gate at the DB or only in the application?" -- has
``DB`` for an answer: an ``UPDATE provider_config SET enabled = 1`` issued by any path at all,
including a future one nobody has written yet, is rejected by SQLite itself.

``ux_secret_ref_purpose_active`` is **partial**
------------------------------------------------
``ENT-secret-ref`` names the index ``ux_secret_ref_purpose_active`` over
``(owner_id, purpose)`` and guarantees "một mục đích có một secret hiệu lực" -- one *effective*
secret per purpose. A total unique index would say something stronger and wrong: it would make
rotation impossible, because ``secrets.md`` §3 keeps the old row (``state = 'rotated'``)
alongside the new one for ``rotation_overlap``. The predicate ``WHERE state = 'active'`` is
what the contract's own wording asks for, and it follows the shape already used by
``ux_tag_owner_text_active`` and ``ux_analysis_valid_key``.
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "0014_tc_secret_settings_service"
down_revision: str | None = "0013_tc_backfill_pending_ledger"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_D = "[0-9]"
#: The mandatory millisecond RFC 3339 UTC shape (``entities.yaml`` §timestamps), spelled as
#: every earlier revision spells it.
TIMESTAMP_UTC_MS_GLOB = f"{_D * 4}-{_D * 2}-{_D * 2}T{_D * 2}:{_D * 2}:{_D * 2}.{_D * 3}Z"

_SECRET_REF = f"""
CREATE TABLE secret_ref (
    id             TEXT NOT NULL PRIMARY KEY,
    owner_id       TEXT NOT NULL REFERENCES owner (id)
                        ON DELETE RESTRICT ON UPDATE RESTRICT,
    purpose        TEXT NOT NULL CHECK (
                        purpose IN ('ai_provider_key', 'collector_token', 'telegram_bot_token')),
    store_locator  TEXT NOT NULL CHECK (length(store_locator) BETWEEN 1 AND 200),
    created_at     TEXT NOT NULL CHECK (created_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    rotated_at     TEXT     NULL CHECK (
                        rotated_at IS NULL
                        OR rotated_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    state          TEXT NOT NULL CHECK (state IN ('active', 'rotated', 'revoked')),

    CONSTRAINT ck_secret_ref_rotated_at_pairs_with_state
        CHECK (state <> 'active' OR rotated_at IS NULL)
)
"""

_TASK_CREDENTIAL = f"""
CREATE TABLE task_credential (
    id                         TEXT NOT NULL PRIMARY KEY,
    owner_id                   TEXT NOT NULL REFERENCES owner (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
    assignment_id              TEXT NOT NULL REFERENCES assignment (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
    secret_ref_id              TEXT NOT NULL REFERENCES secret_ref (id)
                                    ON DELETE RESTRICT ON UPDATE RESTRICT,
    issued_to_worker_identity  TEXT NOT NULL CHECK (
                                    length(issued_to_worker_identity) BETWEEN 1 AND 200),
    issued_at                  TEXT NOT NULL CHECK (issued_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    expires_at                 TEXT NOT NULL CHECK (expires_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    revoked_at                 TEXT     NULL CHECK (
                                    revoked_at IS NULL
                                    OR revoked_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),

    CONSTRAINT ck_task_credential_expires_after_issue
        CHECK (expires_at > issued_at)
)
"""

_SECRET_AUDIT = f"""
CREATE TABLE secret_audit (
    id                   TEXT NOT NULL PRIMARY KEY,
    owner_id             TEXT NOT NULL REFERENCES owner (id)
                              ON DELETE RESTRICT ON UPDATE RESTRICT,
    action               TEXT NOT NULL CHECK (
                              action IN ('issued', 'read', 'rotated', 'revoked', 'denied')),
    secret_ref_id        TEXT     NULL REFERENCES secret_ref (id)
                              ON DELETE RESTRICT ON UPDATE RESTRICT,
    actor_module         TEXT NOT NULL CHECK (length(actor_module) BETWEEN 1 AND 120),
    at                   TEXT NOT NULL CHECK (at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    outcome_detail_safe  TEXT     NULL
)
"""

_PROVIDER_CONFIG = f"""
CREATE TABLE provider_config (
    id               TEXT NOT NULL PRIMARY KEY,
    owner_id         TEXT NOT NULL REFERENCES owner (id)
                          ON DELETE RESTRICT ON UPDATE RESTRICT,
    task_type        TEXT NOT NULL CHECK (
                          task_type IN ('label', 'summary', 'direction_phrasing')),
    auth_family      TEXT NOT NULL CHECK (auth_family IN ('api_key', 'cli_acp')),
    provider_name    TEXT NOT NULL CHECK (length(provider_name) BETWEEN 1 AND 120),
    model_name       TEXT NOT NULL CHECK (
                          length(model_name) BETWEEN 1 AND 120 AND model_name <> 'latest'),
    max_concurrency  INTEGER NOT NULL CHECK (max_concurrency >= 1),
    secret_ref       TEXT     NULL REFERENCES secret_ref (id)
                          ON DELETE RESTRICT ON UPDATE RESTRICT,
    enabled          INTEGER NOT NULL CHECK (enabled IN (0, 1)),
    terms_check_at   TEXT     NULL CHECK (
                          terms_check_at IS NULL
                          OR terms_check_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    terms_check_by   TEXT     NULL,
    terms_doc_ref    TEXT     NULL,

    CONSTRAINT ck_provider_config_terms_before_enable
        CHECK (enabled = 0 OR terms_check_at IS NOT NULL),
    CONSTRAINT ck_provider_config_terms_by
        CHECK (terms_check_at IS NULL OR terms_check_by IS NOT NULL),
    CONSTRAINT ck_provider_config_cli_holds_no_secret
        CHECK (auth_family <> 'cli_acp' OR secret_ref IS NULL),
    CONSTRAINT ck_provider_config_cli_concurrency_is_one
        CHECK (auth_family <> 'cli_acp' OR max_concurrency = 1)
)
"""

_PROVIDER_TEST_RESULT = f"""
CREATE TABLE provider_test_result (
    id                  TEXT NOT NULL PRIMARY KEY,
    owner_id            TEXT NOT NULL REFERENCES owner (id)
                             ON DELETE RESTRICT ON UPDATE RESTRICT,
    provider_config_id  TEXT NOT NULL REFERENCES provider_config (id)
                             ON DELETE RESTRICT ON UPDATE RESTRICT,
    tested_at           TEXT NOT NULL CHECK (tested_at GLOB '{TIMESTAMP_UTC_MS_GLOB}'),
    outcome             TEXT NOT NULL CHECK (outcome IN ('usable', 'unusable', 'unknown')),
    error_code          TEXT     NULL,
    detail_safe         TEXT     NULL,

    CONSTRAINT ck_provider_test_result_usable_has_no_error
        CHECK (outcome <> 'usable' OR error_code IS NULL)
)
"""

_SOURCE_CONNECTION = f"""
CREATE TABLE source_connection (
    id               TEXT NOT NULL PRIMARY KEY,
    owner_id         TEXT NOT NULL REFERENCES owner (id)
                          ON DELETE RESTRICT ON UPDATE RESTRICT,
    source_type      TEXT NOT NULL CHECK (
                          source_type IN ('x_web', 'arxiv_api', 'openalex_api')),
    session_state    TEXT NOT NULL CHECK (
                          session_state IN (
                              'unknown', 'ok', 'challenge_required', 'expired', 'blocked')),
    secret_ref       TEXT     NULL REFERENCES secret_ref (id)
                          ON DELETE RESTRICT ON UPDATE RESTRICT,
    last_checked_at  TEXT     NULL CHECK (
                          last_checked_at IS NULL
                          OR last_checked_at GLOB '{TIMESTAMP_UTC_MS_GLOB}')
)
"""

_STATEMENTS: tuple[str, ...] = (
    _SECRET_REF,
    "CREATE UNIQUE INDEX ux_secret_ref_purpose_active ON secret_ref (owner_id, purpose) "
    "WHERE state = 'active'",
    _TASK_CREDENTIAL,
    "CREATE UNIQUE INDEX ux_task_credential_assignment ON task_credential "
    "(owner_id, assignment_id, secret_ref_id)",
    _SECRET_AUDIT,
    "CREATE INDEX ix_secret_audit_owner_at ON secret_audit (owner_id, at)",
    _PROVIDER_CONFIG,
    "CREATE UNIQUE INDEX ux_provider_config_task ON provider_config (owner_id, task_type)",
    _PROVIDER_TEST_RESULT,
    "CREATE INDEX ix_provider_test_result_config ON provider_test_result "
    "(provider_config_id, tested_at)",
    _SOURCE_CONNECTION,
    "CREATE UNIQUE INDEX ux_source_connection_owner_type ON source_connection "
    "(owner_id, source_type)",
)

_DROPS: tuple[str, ...] = (
    "DROP TABLE IF EXISTS source_connection",
    "DROP TABLE IF EXISTS provider_test_result",
    "DROP TABLE IF EXISTS provider_config",
    "DROP TABLE IF EXISTS secret_audit",
    "DROP TABLE IF EXISTS task_credential",
    "DROP TABLE IF EXISTS secret_ref",
)


def upgrade() -> None:
    for statement in _STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in _DROPS:
        op.execute(statement)
