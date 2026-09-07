"""E1 — the shipped SQLite schema is a function of ``contracts/data/entities.yaml``.

This file is the permanent gate ruling ``F-A3R1-01`` / ``F-A3R1-02`` asked for, tightened
after ``F-A3R2-02``. It exists because the database briefly stopped being a function of the
contract: two revisions on two parallel branches each issued ``CREATE TABLE IF NOT EXISTS
owner`` with different constraint sets, so ``alembic upgrade head`` produced one schema or
the other depending on traversal order, and nothing noticed. A column set alone would not
have caught it -- the two definitions differed by a ``CHECK``.

Two things ``F-A3R2-02`` corrected in the first version of this file, both of which made a
green result mean less than it looked:

``PRAGMA table_xinfo``, not ``table_info``
    ``table_info`` **omits STORED generated columns**. Three of them ship today --
    ``analysis.target_key``, ``saved_item.target_key``, ``work_label.target_key`` -- and
    they carry the uniqueness semantics of the whole target union, so the one column class
    most worth checking was the one class invisible to the check. ``table_xinfo`` returns
    them, with ``hidden`` 2 (VIRTUAL) or 3 (STORED).

Containment in **both** directions
    Asserting only "every shipped column is declared" catches a column that ships without a
    contract, but says nothing about a contract field that never reached the database -- a
    silently missing column reads as a pass. Both directions are asserted now, per shipped
    table.

The assertions, in full:

1. every table has an entity of the same name;
2. every shipped column resolves to a field of that entity, **and** every field of that
   entity ships as a column -- equality, not containment;
3. every field's ``nullable`` matches the column, in both directions, with generated
   columns held to non-nullability *by construction* rather than excused;
4. every ``keys.primary`` is the table's primary key;
5. every ``keys.unique`` entry exists on disk under its contract name;
6. every ``CHECK`` the contract writes into a field's ``constraints`` is present in the DDL;
7. the DDL signature is identical under **four** traversal orders of the migration graph.
"""

from __future__ import annotations

import os
import re
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Bookkeeping, not contract data.
NON_ENTITY_TABLES = frozenset({"alembic_version"})

#: ``PRAGMA table_xinfo`` column positions.
_XINFO_NAME = 1
_XINFO_NOTNULL = 3
_XINFO_PK = 5
_XINFO_HIDDEN = 6

#: ``hidden`` values that mean "generated column" (2 = VIRTUAL, 3 = STORED).
_GENERATED = frozenset({2, 3})

#: The four upgrade paths the graph allows. Each is a list of targets applied in order to a
#: blank database; ``head`` last always lands on the same revision, so any difference in the
#: resulting DDL is order-dependence -- exactly the defect ``F-A3R1-01`` was.
TRAVERSAL_ORDERS: dict[str, tuple[str, ...]] = {
    "default": ("head",),
    "auth_branch_first": ("0002_tc_owner_auth_session", "head"),
    "ingest_branch_first": ("0003_tc_ingest_idempotent_ack_lost", "head"),
    "identity_branch_first": ("0003_tc_canonical_identity_merge", "head"),
}


def _upgrade(db_path: Path, *targets: str) -> None:
    """Run the real Alembic upgrades, in the order given."""
    from alembic import command
    from alembic.config import Config

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    previous = os.environ.get("RR_DATABASE_URL")
    os.environ["RR_DATABASE_URL"] = str(db_path)
    try:
        for target in targets:
            command.upgrade(config, target)
    finally:
        if previous is None:
            os.environ.pop("RR_DATABASE_URL", None)
        else:
            os.environ["RR_DATABASE_URL"] = previous


@pytest.fixture(scope="module")
def entities() -> dict[str, dict[str, Any]]:
    document = yaml.safe_load(
        (REPO_ROOT / "contracts" / "data" / "entities.yaml").read_text("utf-8")
    )
    return {entity["name"]: entity for entity in document["entities"]}


@pytest.fixture(scope="module")
def blank_upgrade(tmp_path_factory: pytest.TempPathFactory) -> Iterator[sqlite3.Connection]:
    """``alembic upgrade head`` on an empty file, the way a fresh deployment runs."""
    db_path = tmp_path_factory.mktemp("schema") / "head.db"
    _upgrade(db_path, "head")
    connection = sqlite3.connect(db_path)
    try:
        yield connection
    finally:
        connection.close()


def _tables(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    return sorted(name for (name,) in rows if name not in NON_ENTITY_TABLES)


def _columns(connection: sqlite3.Connection, table: str) -> list[tuple[Any, ...]]:
    """Every column including generated ones. ``table_info`` would hide those."""
    return list(connection.execute(f'PRAGMA table_xinfo("{table}")'))


def _ddl(connection: sqlite3.Connection, table: str) -> str:
    """The table DDL plus every index on it, which is where UNIQUE may live."""
    table_sql = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()[0]
    index_sql = "\n".join(
        sql or ""
        for (sql,) in connection.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=?", (table,)
        )
    )
    return f"{table_sql}\n{index_sql}"


def _squash(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def _prose_checks(constraints: str) -> list[str]:
    """Every balanced ``CHECK (...)`` written into a field's ``constraints`` prose."""
    out: list[str] = []
    for match in re.finditer(r"CHECK\s*\(", constraints):
        start = constraints.index("(", match.start())
        depth = 0
        for end in range(start, len(constraints)):
            if constraints[end] == "(":
                depth += 1
            elif constraints[end] == ")":
                depth -= 1
                if depth == 0:
                    out.append(constraints[start : end + 1])
                    break
    return out


def _is_sql(expression: str) -> bool:
    """Whether a parenthesised fragment is SQL rather than a Vietnamese description.

    ``work.merged_into_work_id`` says "CHECK (`work.merged_into_work_id` khác `work.id`)" --
    a sentence, not an expression. Those fall back to the weaker assertion below rather than
    being silently skipped.
    """
    return expression.isascii() and any(op in expression for op in ("=", "<", ">", " IS ", "IN "))


def _generating_expression(ddl: str, column: str) -> str | None:
    """The ``GENERATED ALWAYS AS (...)`` body for ``column``, if it has one."""
    match = re.search(
        re.escape(column) + r"\s+\w+\s+GENERATED\s+ALWAYS\s+AS\s*\(", ddl, re.IGNORECASE
    )
    if match is None:
        return None
    start = ddl.index("(", match.end() - 1)
    depth = 0
    for end in range(start, len(ddl)):
        if ddl[end] == "(":
            depth += 1
        elif ddl[end] == ")":
            depth -= 1
            if depth == 0:
                return ddl[start + 1 : end]
    return None


# --------------------------------------------------------------------------------------


def test_every_table_has_an_entity(blank_upgrade, entities) -> None:
    tables = _tables(blank_upgrade)
    assert tables, "the migrations created no tables"
    undeclared = [table for table in tables if table not in entities]
    assert undeclared == [], undeclared


def test_columns_and_contract_fields_are_the_same_set(blank_upgrade, entities) -> None:
    """Containment in **both** directions (``F-A3R2-02``).

    ``shipped ⊆ contract`` alone hides the opposite defect: a field the contract declares
    that no migration ever created. For a shipped table the two sets must be equal.
    """
    problems: list[str] = []
    checked_columns = 0
    for table in _tables(blank_upgrade):
        declared = {field["name"] for field in entities[table]["fields"]}
        shipped = {row[_XINFO_NAME] for row in _columns(blank_upgrade, table)}
        checked_columns += len(shipped)
        for extra in sorted(shipped - declared):
            problems.append(f"{table}.{extra} ships but entities.yaml does not declare it")
        for missing in sorted(declared - shipped):
            problems.append(f"{table}.{missing} is declared but never shipped")
    assert problems == [], problems
    assert checked_columns > 0


def test_generated_columns_are_visible_to_this_check(blank_upgrade) -> None:
    """The reason ``table_info`` was wrong, asserted rather than assumed.

    If SQLite ever stops hiding generated columns from ``table_info`` this test goes quiet
    on its own; while it does hide them, this proves the stricter pragma is doing work.
    """
    generated: dict[str, set[str]] = {}
    for table in _tables(blank_upgrade):
        hidden = {
            row[_XINFO_NAME]
            for row in _columns(blank_upgrade, table)
            if row[_XINFO_HIDDEN] in _GENERATED
        }
        if hidden:
            generated[table] = hidden
    assert generated == {
        "analysis": {"target_key"},
        "saved_item": {"target_key"},
        "work_label": {"target_key"},
    }, generated
    for table, columns in generated.items():
        visible = {row[1] for row in blank_upgrade.execute(f'PRAGMA table_info("{table}")')}
        assert (
            columns & visible == set()
        ), f"{table}: table_info now returns {columns & visible}; this test's premise moved"


def test_nullability_matches_the_contract_in_both_directions(blank_upgrade, entities) -> None:
    """A column that is nullable where the contract says NOT NULL admits rows the contract
    forbids; the reverse rejects rows it permits. Both are defects.

    Generated columns are the one case SQLite will not let carry ``NOT NULL`` directly, so
    they are held to the stronger standard instead: every column their expression reads must
    itself be non-null, either by ``NOT NULL`` or by a ``CHECK`` that says so. That is what
    makes ``target_key`` non-null in fact, and it is asserted rather than excused.
    """
    violations: list[str] = []
    for table in _tables(blank_upgrade):
        fields = {field["name"]: field for field in entities[table]["fields"]}
        ddl = _ddl(blank_upgrade, table)
        for row in _columns(blank_upgrade, table):
            name = row[_XINFO_NAME]
            not_null = bool(row[_XINFO_NOTNULL])
            is_pk = bool(row[_XINFO_PK])
            is_generated = row[_XINFO_HIDDEN] in _GENERATED
            declared_nullable = fields[name]["nullable"]
            enforced_not_null = not_null or is_pk

            if declared_nullable is True and not_null:
                violations.append(f"{table}.{name} is nullable in the contract, NOT NULL on disk")
                continue
            if declared_nullable is not False or enforced_not_null:
                continue
            if not is_generated:
                violations.append(f"{table}.{name} is NOT NULL in the contract, nullable on disk")
                continue

            expression = _generating_expression(ddl, name)
            if expression is None:
                violations.append(f"{table}.{name} is generated but its expression is unreadable")
                continue
            sources = {
                token
                for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expression)
                if token in fields
            }
            assert sources, f"{table}.{name}: generating expression reads no known column"
            for source in sorted(sources):
                source_row = next(
                    r for r in _columns(blank_upgrade, table) if r[_XINFO_NAME] == source
                )
                if bool(source_row[_XINFO_NOTNULL]) or bool(source_row[_XINFO_PK]):
                    continue
                guarded = re.search(
                    r"CHECK\s*\([^;]*\b" + re.escape(source) + r"\b[^;]*IS\s+NOT\s+NULL",
                    ddl,
                    re.IGNORECASE | re.DOTALL,
                )
                if guarded is None:
                    violations.append(
                        f"{table}.{name} is NOT NULL in the contract but its source column "
                        f"{source} is nullable and unguarded by a CHECK"
                    )
    assert violations == [], violations


def test_primary_keys_match_the_contract(blank_upgrade, entities) -> None:
    for table in _tables(blank_upgrade):
        declared = sorted((entities[table].get("keys") or {}).get("primary", []))
        if not declared:
            continue
        on_disk = sorted(
            row[_XINFO_NAME] for row in _columns(blank_upgrade, table) if row[_XINFO_PK]
        )
        assert on_disk == declared, table


def test_every_declared_unique_key_exists_on_disk(blank_upgrade, entities) -> None:
    """Including the partial ones -- a partial unique index that silently became total (or
    vanished) changes which duplicates the database accepts."""
    checked = 0
    for table in _tables(blank_upgrade):
        ddl = _squash(_ddl(blank_upgrade, table))
        for key in (entities[table].get("keys") or {}).get("unique", []) or []:
            name = key.get("name")
            assert name, f"{table}: a unique key with no name cannot be checked"
            assert _squash(name) in ddl, f"{table}: unique key {name} is not on disk"
            for column in key["columns"]:
                assert _squash(column) in ddl, f"{table}.{name}: column {column} missing"
            checked += 1
    assert checked > 0


def test_every_check_the_contract_writes_is_present(blank_upgrade, entities) -> None:
    """The assertion class that ``F-A3R1-01`` turned on: the two ``owner`` definitions
    differed only by a CHECK, and no test looked at CHECKs."""
    missing: list[str] = []
    checked = 0
    for table in _tables(blank_upgrade):
        ddl = _ddl(blank_upgrade, table)
        squashed = _squash(ddl)
        for field in entities[table]["fields"]:
            for expression in _prose_checks(field.get("constraints") or ""):
                checked += 1
                if _is_sql(expression):
                    if _squash(expression) not in squashed:
                        missing.append(f"{table}.{field['name']}: {expression}")
                else:
                    # Prose CHECK: demand *a* CHECK clause naming the column.
                    pattern = re.compile(
                        r"CHECK\s*\([^)]*\b" + re.escape(field["name"]) + r"\b", re.IGNORECASE
                    )
                    if not pattern.search(ddl):
                        missing.append(f"{table}.{field['name']}: no CHECK mentions the column")
    assert missing == [], missing
    assert checked > 0


def test_the_owner_constraint_set_is_complete(blank_upgrade) -> None:
    """``ENT-owner`` explicitly, because it is the table the two revisions disagreed about.

    Named separately from the generic sweep so a regression reads as "the owner constraint
    set regressed" rather than as one line in a list.
    """
    ddl = _squash(_ddl(blank_upgrade, "owner"))
    assert "check(singleton_guard=1)" in ddl
    assert "ux_owner_singleton" in ddl
    assert "check(length(display_name)between1and120)" in ddl
    assert "created_atglob" in ddl
    columns = {row[_XINFO_NAME] for row in _columns(blank_upgrade, "owner")}
    assert {
        "id",
        "singleton_guard",
        "display_name",
        "timezone_iana",
        "created_at",
        "password_hash",
        "password_updated_at",
        "failed_login_count",
        "locked_until",
    } == columns


def _schema_signature(db_path: Path) -> dict[str, str]:
    """Normalised DDL of every object, plus the full column list read through ``xinfo``.

    The column list is part of the signature because a generated column is invisible to
    ``table_info`` and could otherwise differ between two databases whose ``sqlite_master``
    text happened to match after normalisation.
    """
    connection = sqlite3.connect(db_path)
    try:
        signature = {
            f"sql:{name}": _squash(sql or "")
            for name, sql in connection.execute(
                "SELECT name, sql FROM sqlite_master "
                "WHERE name NOT LIKE 'sqlite_%' AND name <> 'alembic_version'"
            )
        }
        for table in _tables(connection):
            signature[f"cols:{table}"] = ",".join(
                f"{row[_XINFO_NAME]}:{row[_XINFO_NOTNULL]}:{row[_XINFO_PK]}:{row[_XINFO_HIDDEN]}"
                for row in _columns(connection, table)
            )
        return signature
    finally:
        connection.close()


def test_the_schema_is_identical_under_all_four_traversal_orders(tmp_path) -> None:
    """``F-A3R1-01`` directly: force each branch to run first and demand one schema.

    Three branches descend from ``0002_base_entities``, so there are four upgrade paths a
    real deployment can take. If any of them produced a different schema the database would
    be a function of the walk rather than of ``contracts/data/entities.yaml`` -- which is
    what happened, and what went unnoticed because nothing compared the orders.
    """
    signatures: dict[str, dict[str, str]] = {}
    for label, targets in TRAVERSAL_ORDERS.items():
        db_path = tmp_path / f"{label}.db"
        _upgrade(db_path, *targets)
        signatures[label] = _schema_signature(db_path)

    assert len(signatures) == 4
    baseline_label = "default"
    baseline = signatures[baseline_label]
    for label, signature in signatures.items():
        if label == baseline_label:
            continue
        assert set(signature) == set(baseline), (
            label,
            set(signature).symmetric_difference(baseline),
        )
        differing = [key for key in baseline if baseline[key] != signature[key]]
        assert differing == [], (label, differing)


def test_alembic_has_exactly_one_head() -> None:
    """An ambiguous head makes ``alembic upgrade head`` fail on a fresh deployment."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    config = Config(str(REPO_ROOT / "server" / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "server" / "migrations"))
    heads = ScriptDirectory.from_config(config).get_heads()
    assert len(heads) == 1, heads
