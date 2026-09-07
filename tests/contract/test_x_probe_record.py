"""E1 — the §5 record: shape, the three NOT NULL rules, redaction, and JSONL round trip.

Every assertion here points at a clause of ``contracts/ops/collector-probe.md`` §5. The
field list itself is checked against the contract table, so adding a field to the record
without adding it to the contract (or the reverse) fails here rather than in a review.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from probe.x_feasibility.record import (
    LIMIT_KINDS,
    PROVENANCE_FIELDS,
    RECORD_FIELDS,
    STOP_REASONS,
    ProbeRunRecord,
    RecordValidationError,
    RunCounters,
    append_record,
    append_seen_ledger,
    hash_post_id,
    load_seen_ledger,
    new_ulid,
    read_records,
    redact,
    validate_record,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "contracts/ops/collector-probe.md"


def make_record(**overrides: object) -> ProbeRunRecord:
    base = {
        "probe_run_id": new_ulid(),
        "started_at": "2026-09-08T08:00:00.000Z",
        "ended_at": "2026-09-08T08:25:00.000Z",
        "duration_s": 1500,
        "search_terms": ["protein folding"],
        "posts_seen": 120,
        "posts_parsed_ok": 118,
        "posts_new_vs_previous_runs": 40,
        "posts_with_paper_link": 30,
        "posts_image_only": 5,
        "author_threads_opened": 0,
        "challenge_count": 0,
        "session_expired_count": 0,
        "blocked_count": 0,
        "rate_limited_count": 0,
        "rate_limited_at": None,
        "parser_degraded_count": 0,
        "stop_reason": "limit_reached",
        "limit_kind": "duration",
        "cursor_invalidated": False,
        "unobservable_scope_vi": "Chỉ quét tab Mới nhất trong 25 phút; phần sau mốc đó không quét.",
        "notes_vi": "",
    }
    base.update(overrides)
    return ProbeRunRecord(**base)  # type: ignore[arg-type]


# --- the field list is the contract's field list -------------------------------------
def test_record_fields_match_the_contract_table() -> None:
    """Every §5 row is a field, and every field is a §5 row."""
    text = CONTRACT.read_text(encoding="utf-8")
    section = text.split("## 5. Ghi nhận mỗi đợt", 1)[1].split("## 6.", 1)[0]
    in_table = set(re.findall(r"^\| `([a-z_]+)`", section, flags=re.MULTILINE))
    # §5 lists started_at and ended_at on one row.
    in_table.discard("started_at")
    in_table |= {"started_at", "ended_at"}
    assert in_table == set(RECORD_FIELDS), (
        f"lệch với bảng §5: thừa {sorted(set(RECORD_FIELDS) - in_table)}, "
        f"thiếu {sorted(in_table - set(RECORD_FIELDS))}"
    )


def test_provenance_fields_are_separate_from_contract_fields() -> None:
    assert not set(PROVENANCE_FIELDS) & set(RECORD_FIELDS)


def test_json_keys_are_emitted_in_contract_order() -> None:
    payload = make_record().to_json_dict()
    assert list(payload) == list(RECORD_FIELDS) + list(PROVENANCE_FIELDS)


def test_stop_reason_enum_matches_the_contract() -> None:
    assert STOP_REASONS == (
        "limit_reached",
        "captcha",
        "session_expired",
        "source_blocked",
        "rate_limited",
        "source_layout_changed",
        "operator_stop",
    )
    assert LIMIT_KINDS == ("posts", "duration")


# --- ULID ----------------------------------------------------------------------------
def test_ulid_is_26_crockford_characters_and_time_ordered() -> None:
    early = new_ulid(now_ms=1_000_000_000_000, randomness=b"\x00" * 10)
    late = new_ulid(now_ms=1_000_000_001_000, randomness=b"\x00" * 10)
    assert len(early) == 26
    assert re.fullmatch(r"[0-9A-HJKMNP-TV-Z]{26}", early)
    assert early < late


def test_ulid_rejects_wrong_randomness_length() -> None:
    with pytest.raises(ValueError, match="10 bytes"):
        new_ulid(randomness=b"\x00")


# --- the three NOT NULL rules of §5 ---------------------------------------------------
def test_limit_kind_required_when_limit_reached() -> None:
    with pytest.raises(RecordValidationError, match="limit_kind"):
        validate_record(make_record(limit_kind=None).to_json_dict())


def test_limit_kind_forbidden_when_not_limit_reached() -> None:
    """Both directions: a stray ``posts`` on a challenge run is an error, not a curiosity."""
    record = make_record(stop_reason="captcha", limit_kind="posts", challenge_count=1)
    with pytest.raises(RecordValidationError, match="phải NULL"):
        validate_record(record.to_json_dict())


def test_rate_limited_at_required_when_rate_limited() -> None:
    record = make_record(
        stop_reason="rate_limited", limit_kind=None, rate_limited_count=1, rate_limited_at=None
    )
    with pytest.raises(RecordValidationError, match="rate_limited_at"):
        validate_record(record.to_json_dict())


def test_rate_limited_at_accepted_with_a_count() -> None:
    record = make_record(
        stop_reason="rate_limited",
        limit_kind=None,
        rate_limited_count=1,
        rate_limited_at="2026-09-08T08:20:00.000Z",
    )
    validate_record(record.to_json_dict())


def test_rate_limited_at_without_a_count_is_rejected() -> None:
    record = make_record(rate_limited_at="2026-09-08T08:20:00.000Z", rate_limited_count=0)
    with pytest.raises(RecordValidationError, match="rate_limited_count"):
        validate_record(record.to_json_dict())


def test_unobservable_scope_must_not_be_empty() -> None:
    """AMD-B05 / GO-7: a probe that omits what it did not see gets read as 'swept everything'."""
    with pytest.raises(RecordValidationError, match="unobservable_scope_vi"):
        validate_record(make_record(unobservable_scope_vi="   ").to_json_dict())


# --- other shape rules ---------------------------------------------------------------
def test_valid_record_passes() -> None:
    validate_record(make_record().to_json_dict())


def test_missing_field_is_named() -> None:
    payload = make_record().to_json_dict()
    del payload["posts_seen"]
    with pytest.raises(RecordValidationError, match="posts_seen"):
        validate_record(payload)


def test_parsed_ok_cannot_exceed_posts_seen() -> None:
    with pytest.raises(RecordValidationError, match="posts_parsed_ok"):
        validate_record(make_record(posts_seen=5, posts_parsed_ok=6).to_json_dict())


def test_new_posts_cannot_exceed_posts_seen() -> None:
    with pytest.raises(RecordValidationError, match="posts_new_vs_previous_runs"):
        payload = make_record(
            posts_seen=5, posts_parsed_ok=5, posts_new_vs_previous_runs=6
        ).to_json_dict()
        validate_record(payload)


def test_unknown_stop_reason_is_rejected() -> None:
    with pytest.raises(RecordValidationError, match="stop_reason"):
        validate_record(make_record(stop_reason="blocked", limit_kind=None).to_json_dict())


def test_timestamps_need_millisecond_precision() -> None:
    with pytest.raises(RecordValidationError, match="started_at"):
        validate_record(make_record(started_at="2026-09-08T08:00:00Z").to_json_dict())


def test_booleans_are_not_accepted_as_counters() -> None:
    with pytest.raises(RecordValidationError, match="posts_seen"):
        validate_record(make_record(posts_seen=True).to_json_dict())


def test_search_terms_must_be_present() -> None:
    with pytest.raises(RecordValidationError, match="search_terms"):
        validate_record(make_record(search_terms=[]).to_json_dict())


# --- redaction ------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("raw", "must_not_contain"),
    [
        ("Authorization: Bearer abc.def-ghi", "abc.def-ghi"),
        ("cookie: auth_token=deadbeef; ct0=cafebabe", "deadbeef"),
        ("auth_token=deadbeef", "deadbeef"),
        ("/home/someone/rr-x-profile", "someone"),
        ("/Users/someone/rr-x-profile", "someone"),
        ("bài của @someuser rất hay", "@someuser"),
        ("api_key: sk-not-a-real-key", "sk-not-a-real-key"),
    ],
)
def test_redaction_removes_identifiers_and_credentials(raw: str, must_not_contain: str) -> None:
    assert must_not_contain not in redact(raw)


def test_redaction_is_applied_when_the_record_is_serialised() -> None:
    record = make_record(notes_vi="đợt này thấy @someuser đăng bài từ /home/someone/x")
    payload = record.to_json_dict()
    assert "@someuser" not in payload["notes_vi"]
    assert "/home/someone" not in payload["notes_vi"]
    validate_record(payload)


def test_validation_rejects_a_record_that_still_carries_a_secret() -> None:
    payload = make_record().to_json_dict()
    payload["notes_vi"] = "Authorization: Bearer leaked-token-value"
    with pytest.raises(RecordValidationError, match="che"):
        validate_record(payload)


# --- JSONL round trip -----------------------------------------------------------------
def test_append_and_read_round_trip(tmp_path: Path) -> None:
    target = tmp_path / "runs.jsonl"
    first = append_record(target, make_record())
    second = append_record(
        target, make_record(stop_reason="captcha", limit_kind=None, challenge_count=1)
    )
    records = read_records(target)
    assert [r["probe_run_id"] for r in records] == [first["probe_run_id"], second["probe_run_id"]]
    assert target.read_text(encoding="utf-8").count("\n") == 2


def test_append_refuses_an_invalid_record(tmp_path: Path) -> None:
    target = tmp_path / "runs.jsonl"
    with pytest.raises(RecordValidationError):
        append_record(target, make_record(unobservable_scope_vi=""))
    assert not target.exists() or target.read_text(encoding="utf-8") == ""


def test_read_records_names_the_bad_line(tmp_path: Path) -> None:
    target = tmp_path / "runs.jsonl"
    append_record(target, make_record())
    with target.open("a", encoding="utf-8") as handle:
        handle.write("{not json}\n")
    with pytest.raises(RecordValidationError, match=r":2"):
        read_records(target)


def test_read_records_skips_blank_lines(tmp_path: Path) -> None:
    target = tmp_path / "runs.jsonl"
    append_record(target, make_record())
    with target.open("a", encoding="utf-8") as handle:
        handle.write("\n\n")
    assert len(read_records(target)) == 1


def test_read_records_rejects_a_record_violating_section_5(tmp_path: Path) -> None:
    target = tmp_path / "runs.jsonl"
    payload = make_record().to_json_dict()
    payload["unobservable_scope_vi"] = ""
    target.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
    with pytest.raises(RecordValidationError, match="unobservable_scope_vi"):
        read_records(target)


# --- seen-id ledger --------------------------------------------------------------------
def test_ledger_stores_digests_not_post_ids(tmp_path: Path) -> None:
    """``posts_new_vs_previous_runs`` needs cross-run memory; it does not need the ids."""
    ledger = tmp_path / "seen.sha256"
    digest = hash_post_id("1900000000000000001")
    append_seen_ledger(ledger, {digest})
    body = ledger.read_text(encoding="utf-8")
    assert "1900000000000000001" not in body
    assert load_seen_ledger(ledger) == {digest}
    assert re.fullmatch(r"[0-9a-f]{64}", digest)


def test_ledger_missing_file_is_an_empty_set(tmp_path: Path) -> None:
    assert load_seen_ledger(tmp_path / "nope.sha256") == set()


# --- counters ---------------------------------------------------------------------------
def test_counters_bump_records_the_first_rate_limit_stamp() -> None:
    counters = RunCounters()
    counters.bump("rate_limited_count", at="2026-09-08T08:20:00.000Z")
    counters.bump("rate_limited_count", at="2026-09-08T08:30:00.000Z")
    assert counters.rate_limited_count == 2
    assert counters.rate_limited_at == "2026-09-08T08:20:00.000Z", "§5: mốc lần ĐẦU TIÊN"


def test_counters_bump_ignores_none() -> None:
    counters = RunCounters()
    counters.bump(None)
    assert counters.challenge_count == 0
