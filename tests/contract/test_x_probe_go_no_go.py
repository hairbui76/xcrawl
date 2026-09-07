"""E1 — §7 go/no-go on synthetic run sets, both verdicts and the inconclusive cases.

The runs here are **synthetic**: numbers written by hand to put one criterion on each side
of its threshold. They are not probe results, and no probe has run. What they establish is
that the computation applies §7 verbatim -- the thresholds are read from the module and
compared against the contract text, so loosening one in code fails this file.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from probe.x_feasibility.go_no_go import (
    EXIT_CODES,
    GO,
    GO1_LIMIT_REACHED_SHARE_MIN,
    GO3_BLOCKED_MAX,
    GO4_NEW_POSTS_MEDIAN_MIN,
    GO5_PARSE_RATIO_MIN,
    GO6_PARSER_DEGRADED_MAX,
    INCONCLUSIVE,
    NO_GO,
    evaluate,
    main,
)
from probe.x_feasibility.record import ProbeRunRecord, append_record, new_ulid

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "contracts/ops/collector-probe.md"


def run(index: int, **overrides: object) -> dict:
    """One synthetic §5 record. Defaults are a clean run that satisfies every criterion."""
    base: dict = {
        "probe_run_id": new_ulid(now_ms=1_700_000_000_000 + index, randomness=bytes([index]) * 10),
        "started_at": f"2026-09-{8 + index:02d}T08:00:00.000Z",
        "ended_at": f"2026-09-{8 + index:02d}T08:30:00.000Z",
        "duration_s": 1800,
        "search_terms": ["protein folding"],
        "posts_seen": 100,
        "posts_parsed_ok": 100,
        "posts_new_vs_previous_runs": 20,
        "posts_with_paper_link": 10,
        "posts_image_only": 2,
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
        "unobservable_scope_vi": "Chỉ tab Mới nhất, trong ngân sách 30 phút.",
        "notes_vi": "",
        "protocol_version": "CT-ops-collector-probe@0.3.0",
        "probe_tool_version": "0.1.0",
        "clock_note_vi": "đồng hồ máy cá nhân",
    }
    base.update(overrides)
    return base


def clean_campaign(n: int = 5) -> list[dict]:
    return [run(i) for i in range(n)]


# --- thresholds are the contract's thresholds ----------------------------------------
def test_thresholds_match_the_contract_text() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    section = text.split("## 7. Tiêu chí go / no-go", 1)[1].split("## 8.", 1)[0]
    assert "≥ 60%" in section and GO1_LIMIT_REACHED_SHARE_MIN == 0.60
    assert "≤ 1 trên mỗi 5 đợt" in section
    assert re.search(r"GO-3.*\|\s*= 0\s*\|", section) and GO3_BLOCKED_MAX == 0
    assert "≥ 5" in section and GO4_NEW_POSTS_MEDIAN_MIN == 5
    assert "≥ 0.90" in section and GO5_PARSE_RATIO_MIN == 0.90
    assert GO6_PARSER_DEGRADED_MAX == 0


# --- GO ------------------------------------------------------------------------------
def test_clean_campaign_is_go() -> None:
    report = evaluate(clean_campaign(5))
    assert report.verdict == GO
    assert report.failed_ids == ()
    assert "không có nghĩa" in report.reason_vi, "kết luận GO phải kèm giới hạn §10"


def test_go_at_ten_runs() -> None:
    assert evaluate(clean_campaign(10)).verdict == GO


def test_go_1_at_exactly_sixty_percent() -> None:
    records = clean_campaign(5)
    for i in (3, 4):
        records[i]["stop_reason"] = "captcha"
        records[i]["limit_kind"] = None
        records[i]["challenge_count"] = 0
    # 3/5 = 0.60 exactly -> GO-1 passes at the boundary.
    report = evaluate(records)
    assert "GO-1" not in report.failed_ids


def test_go_1_below_sixty_percent_is_no_go() -> None:
    records = clean_campaign(5)
    for i in (2, 3, 4):
        records[i]["stop_reason"] = "session_expired"
        records[i]["limit_kind"] = None
    report = evaluate(records)
    assert report.verdict == NO_GO
    assert "GO-1" in report.failed_ids


# --- one criterion at a time ----------------------------------------------------------
def test_go_2_allows_one_challenge_per_five_runs() -> None:
    records = clean_campaign(5)
    records[0]["challenge_count"] = 1
    assert "GO-2" not in evaluate(records).failed_ids
    records[1]["challenge_count"] = 1
    assert "GO-2" in evaluate(records).failed_ids


def test_go_2_scales_with_n() -> None:
    records = clean_campaign(10)
    records[0]["challenge_count"] = 2
    assert "GO-2" not in evaluate(records).failed_ids
    records[1]["challenge_count"] = 1
    assert "GO-2" in evaluate(records).failed_ids


def test_go_3_any_block_is_no_go() -> None:
    records = clean_campaign(5)
    records[2]["blocked_count"] = 1
    records[2]["stop_reason"] = "source_blocked"
    records[2]["limit_kind"] = None
    report = evaluate(records)
    assert report.verdict == NO_GO
    assert "GO-3" in report.failed_ids
    assert "BLOCKED" in report.reason_vi
    assert "trả phí" in report.reason_vi, "NO-GO phải nhắc: không tự chuyển sang X API trả phí"


def test_go_4_uses_the_median_not_the_mean() -> None:
    """A single bumper run must not hide four empty ones."""
    records = clean_campaign(5)
    records[0]["posts_new_vs_previous_runs"] = 0  # first run is excluded either way
    for i in (1, 2, 3):
        records[i]["posts_new_vs_previous_runs"] = 1
    records[4]["posts_new_vs_previous_runs"] = 500
    report = evaluate(records)
    assert "GO-4" in report.failed_ids, "trung bình sẽ pass; trung vị phải fail"


def test_go_4_ignores_the_first_run() -> None:
    records = clean_campaign(5)
    records[0]["posts_new_vs_previous_runs"] = 0
    assert "GO-4" not in evaluate(records).failed_ids


def test_go_5_parse_ratio() -> None:
    records = clean_campaign(5)
    records[0]["posts_parsed_ok"] = 80  # 480/500 = 0.96
    assert "GO-5" not in evaluate(records).failed_ids
    records[1]["posts_parsed_ok"] = 30  # 410/500 = 0.82
    assert "GO-5" in evaluate(records).failed_ids


def test_go_5_zero_posts_seen_is_not_a_pass() -> None:
    records = clean_campaign(5)
    for record in records:
        record["posts_seen"] = 0
        record["posts_parsed_ok"] = 0
        record["posts_new_vs_previous_runs"] = 0
    report = evaluate(records)
    assert "GO-5" in report.failed_ids
    assert report.verdict in {NO_GO, INCONCLUSIVE}


def test_go_7_missing_unobservable_scope_fails() -> None:
    records = clean_campaign(5)
    records[3]["unobservable_scope_vi"] = ""
    report = evaluate(records)
    assert "GO-7" in report.failed_ids
    assert report.verdict == NO_GO


# --- inconclusive ---------------------------------------------------------------------
def test_fewer_than_five_runs_is_inconclusive() -> None:
    report = evaluate(clean_campaign(4))
    assert report.verdict == INCONCLUSIVE
    assert "N = 4" in report.reason_vi


def test_no_runs_at_all_is_inconclusive() -> None:
    assert evaluate([]).verdict == INCONCLUSIVE


def test_more_than_ten_runs_is_inconclusive() -> None:
    report = evaluate(clean_campaign(11))
    assert report.verdict == INCONCLUSIVE
    assert "trần" in report.reason_vi


def test_go_6_failure_is_inconclusive_not_no_go() -> None:
    """§7: GO-6 trượt ⇒ KHÔNG KẾT LUẬN. A mixed-layout campaign is not a measurement."""
    records = clean_campaign(5)
    records[1]["parser_degraded_count"] = 1
    records[1]["stop_reason"] = "source_layout_changed"
    records[1]["limit_kind"] = None
    report = evaluate(records)
    assert report.verdict == INCONCLUSIVE
    assert "GO-6" in report.failed_ids
    assert "chạy lại" in report.reason_vi


def test_go_6_failure_wins_over_other_failures() -> None:
    records = clean_campaign(5)
    records[1]["parser_degraded_count"] = 1
    records[2]["blocked_count"] = 1
    assert evaluate(records).verdict == INCONCLUSIVE


# --- rendering and CLI ------------------------------------------------------------------
def test_report_renders_every_criterion() -> None:
    rendered = evaluate(clean_campaign(5)).render_vi()
    for criterion in ("GO-1", "GO-2", "GO-3", "GO-4", "GO-5", "GO-6", "GO-7"):
        assert criterion in rendered


def test_report_dict_is_json_serialisable() -> None:
    payload = evaluate(clean_campaign(5)).to_dict()
    json.dumps(payload, ensure_ascii=False)
    assert payload["verdict"] == GO
    assert len(payload["criteria"]) == 7


def _write_campaign(path: Path, records: list[dict]) -> None:
    for data in records:
        append_record(path, ProbeRunRecord(**{k: v for k, v in data.items()}))


@pytest.mark.parametrize(
    ("mutate", "expected_verdict"),
    [
        (lambda rs: rs, GO),
        (lambda rs: [{**r, "blocked_count": 1} if i == 0 else r for i, r in enumerate(rs)], NO_GO),
        (lambda rs: rs[:3], INCONCLUSIVE),
    ],
)
def test_cli_exit_codes(tmp_path: Path, mutate, expected_verdict: str) -> None:
    target = tmp_path / "runs.jsonl"
    _write_campaign(target, mutate(clean_campaign(5)))
    assert main([str(target)]) == EXIT_CODES[expected_verdict]


def test_cli_reports_a_missing_file_without_crashing(tmp_path: Path) -> None:
    assert main([str(tmp_path / "absent.jsonl")]) == 3


def test_cli_json_output(tmp_path: Path, capsys) -> None:
    target = tmp_path / "runs.jsonl"
    _write_campaign(target, clean_campaign(5))
    main([str(target), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == GO
    assert payload["n_runs"] == 5
